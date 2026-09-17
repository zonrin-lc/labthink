#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投标响应文件审阅复核 —— 可移植版核心脚本（零依赖，仅用 Python 标准库）

为什么可移植：
  .docx 本质是一个 zip 包，正文是里面的 word/document.xml（OOXML）。
  本脚本用标准库 zipfile + xml.etree.ElementTree 直接解析，
  不依赖 python-docx / openpyxl，也不需联网 pip install。
  只要有 Python 3.8+ 即可在任意机器运行。

v1.1.0 变更（相对 v1.0.0）：
  * 修订感知增强：收集文本时跳过 w:del 子树，已删除内容不再混入正式文本
  * 新增页眉/页脚解析：盖章、声明等关键词可命中页眉页脚
  * 新增检查项：域错误残留（“错误！未找到引用源”等）、批注残留、
    外部链接/引用、图片引用完整性
  * 表格列宽改为实测（tblGrid vs 页面可用宽度），无表格时不再恒 warn
  * 页码占位检测改进（只命中“第 页”等空页码残留，不再误伤“第 5 页”引用）
  * HTML 转义补引号；Windows stdout 编码兜底；import 不再依赖当前目录
  * 支持 --score-low/--score-mid/--score-high/--score-note 三档得分
  * 报告输出文件大小、修改时间、SHA-256，便于证明核查版本
  * --patterns/--compliance/--stamp 支持 --xxx-add 追加模式
  * 样式优先从 references/report_template.html 读取（单源维护），缺失时回退内嵌

用法：
  python docx_review.py <标书.docx> [--eval 评标办法.xlsx]
                         [--out report.html] [--name "报告标题"]
                         [--patterns "待补充;TODO;XXX"] [--compliance "完全满足"]
                         [--stamp "盖章;声明;签章"]
                         [--patterns-add ...] [--compliance-add ...] [--stamp-add ...]
                         [--score-low 80] [--score-mid 85] [--score-high 90]
                         [--score-note "评分口径说明"]

退出码：0=正常，2=文件无法解析。
"""
import argparse
import datetime
import hashlib
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PKG = "{http://schemas.openxmlformats.org/package/2006/relationships}"
DC = "{http://purl.org/dc/elements/1.1/}"
CP = "{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}"
EP = "{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}"

# Word 域未更新 / 交叉引用失效时的残留文本（投标文件高频硬伤）
FIELD_ERRORS = (
    "错误！未找到引用源",
    "错误！未定义书签",
    "错误！链接无效",
    "Error! Bookmark not defined",
    "Error! Reference source not found",
)

DEFAULTS = {
    "patterns": ["待补充", "TODO", "【待", "XXX", "待填", "未填", "占位"],
    "compliance": ["完全满足", "满足", "响应"],
    "stamp": ["盖章", "声明", "签章", "鲜章", "法定代表人"],
}

# ---------------------------------------------------------------------------
# 抽取层：从 .docx 读出正文、表格、页眉页脚、修订痕迹、目录域、媒体引用
# ---------------------------------------------------------------------------

def _collect_text(elem):
    """收集 elem 子树里所有 w:t 的文本（保持文档顺序），跳过 w:del 删除子树。

    用显式栈遍历以便剪枝：已删除内容（w:del 内的 w:t / w:delText）
    一律不进入正式文本，避免占位符、应答、页码等扫描被旧版本内容污染。
    """
    parts = []
    stack = [elem]
    while stack:
        node = stack.pop()
        if node.tag == W + "del":
            continue
        if node.tag == W + "t" and node.text:
            parts.append(node.text)
        stack.extend(reversed(list(node)))
    return "".join(parts)


def _collect_part_texts(z, names, pattern):
    """收集 zip 中匹配 pattern 的部件（如 header/footer）的文本，并拼接。"""
    out = []
    for n in names:
        if re.match(pattern, n):
            try:
                out.append(_collect_text(ET.fromstring(z.read(n))))
            except ET.ParseError:
                pass
    return "".join(out)


def _read_rels(z, names, doc_name):
    """读取 document.xml 的关系表：rId -> {Type, Target, TargetMode}。"""
    rels = {}
    rel_path = "word/_rels/%s.rels" % os.path.basename(doc_name)
    if rel_path not in names:
        rel_path = "word/_rels/document.xml.rels"
    if rel_path in names:
        try:
            rroot = ET.fromstring(z.read(rel_path))
            for rel in rroot:
                rels[rel.get("Id")] = {
                    "Type": rel.get("Type") or "",
                    "Target": rel.get("Target") or "",
                    "TargetMode": rel.get("TargetMode") or "",
                }
        except ET.ParseError:
            pass
    return rels


def _check_embeds(root, rels, names):
    """校验文档内图片引用（r:embed）在包内是否存在对应媒体文件。

    返回缺失的 rId 列表。外部链接（TargetMode=External）不算缺失。
    """
    missing = []
    for blip in root.iter(R + "embed"):
        rid = blip.text
        if not rid:
            continue
        t = rels.get(rid)
        if t is None:
            missing.append(rid)
            continue
        if t.get("TargetMode") == "External":
            continue
        target = t.get("Target", "")
        if target.startswith("/"):
            full = target.lstrip("/")
        else:
            full = os.path.normpath(os.path.join("word", target)).replace("\\", "/")
        if full not in names:
            missing.append(rid)
    return missing


def _count_comments(z, names):
    if "word/comments.xml" not in names:
        return 0
    try:
        croot = ET.fromstring(z.read("word/comments.xml"))
        return sum(1 for _ in croot.iter(W + "comment"))
    except ET.ParseError:
        return 0


def _comment_authors(z, names):
    """批注作者集合（串标痕迹：批注人可能露出其他编制方）。"""
    if "word/comments.xml" not in names:
        return set()
    try:
        croot = ET.fromstring(z.read("word/comments.xml"))
        return {c.get(W + "author") or "" for c in croot.iter(W + "comment")} - {""}
    except ET.ParseError:
        return set()


def _doc_props(z, names):
    """读取 docProps/core.xml 与 app.xml 的作者/公司/经理字段（串标痕迹）。"""
    creator = last_modified_by = company = manager = ""
    if "docProps/core.xml" in names:
        try:
            croot = ET.fromstring(z.read("docProps/core.xml"))
            e1 = croot.find(DC + "creator")
            e2 = croot.find(CP + "lastModifiedBy")
            creator = e1.text.strip() if e1 is not None and e1.text else ""
            last_modified_by = e2.text.strip() if e2 is not None and e2.text else ""
        except ET.ParseError:
            pass
    if "docProps/app.xml" in names:
        try:
            aroot = ET.fromstring(z.read("docProps/app.xml"))
            e3 = aroot.find(EP + "Company")
            e4 = aroot.find(EP + "Manager")
            company = e3.text.strip() if e3 is not None and e3.text else ""
            manager = e4.text.strip() if e4 is not None and e4.text else ""
        except ET.ParseError:
            pass
    return creator, last_modified_by, company, manager


def _hidden_text(root):
    """收集隐藏文字（w:vanish）：可能是残留的内部备注/其他编制方信息。"""
    samples = []
    for r in root.iter(W + "r"):
        rpr = r.find(W + "rPr")
        if rpr is not None and rpr.find(W + "vanish") is not None:
            txt = _collect_text(r)
            if txt.strip():
                samples.append(txt.strip())
    return samples


def _table_width(root):
    """实测表格列宽合计 vs 页面可用宽度（twips）。

    返回 (over, n_tbl)：
      n_tbl  = 表格总数（含嵌套）
      over   = 超出页面可用宽度的最大 twips 值；None 表示无法实测
    """
    sect = root.find(".//" + W + "sectPr")
    avail = None
    if sect is not None:
        pg = sect.find(W + "pgSz")
        mar = sect.find(W + "pgMar")
        if pg is not None and pg.get(W + "w"):
            pw = int(pg.get(W + "w"))
            ml = int(mar.get(W + "left")) if (mar is not None and mar.get(W + "left")) else 0
            mr = int(mar.get(W + "right")) if (mar is not None and mar.get(W + "right")) else 0
            avail = pw - ml - mr
    tbls = list(root.iter(W + "tbl"))
    if not tbls:
        return None, 0
    over = 0
    measured = False
    for tbl in tbls:
        grid = tbl.find(W + "tblGrid")
        if grid is None:
            continue
        total = 0
        has_w = True
        for gc in grid.findall(W + "gridCol"):
            wv = gc.get(W + "w")
            if wv is None:
                has_w = False
                break
            total += int(wv)
        if has_w:
            measured = True
            if avail is not None and total > avail:
                over = max(over, total - avail)
    if not measured:
        return None, len(tbls)
    return over, len(tbls)


def extract_docx(path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        doc_name = "word/document.xml" if "word/document.xml" in names else None
        if doc_name is None:
            doc_name = next((n for n in names if n.endswith("document.xml")), None)
        if doc_name is None:
            raise ValueError(
                "未找到 document.xml，可能不是有效的 .docx 文件"
                "（.doc 老格式、.wps 等不支持，请先另存为 .docx）"
            )
        doc_xml = z.read(doc_name)
        root = ET.fromstring(doc_xml)
        body = root.find(W + "body")

        full_text = _collect_text(root)
        header_footer_text = _collect_part_texts(z, names, r"word/(header|footer)\d*\.xml$")

        # 修订痕迹（修订感知：删除子树已不进入 full_text，这里仅统计数量供提示）
        ins_count = sum(1 for _ in root.iter(W + "ins"))
        del_count = sum(1 for _ in root.iter(W + "del"))

        # 目录域 TOC
        has_toc = False
        for instr in root.iter(W + "instrText"):
            if instr.text and "TOC" in instr.text.upper():
                has_toc = True
                break
        if not has_toc:
            for fs in root.iter(W + "fldSimple"):
                val = fs.get(W + "instr") or ""
                if "TOC" in val.upper():
                    has_toc = True
                    break

        # 表格（每行只取直接子级单元格，嵌套表格不再并入外层行）
        tables = []
        for tbl in body.iter(W + "tbl"):
            rows = []
            for tr in tbl.iter(W + "tr"):
                cells = [_collect_text(tc) for tc in tr.findall(W + "tc")]
                rows.append(cells)
            tables.append(rows)

        # 段落块（含表格）按文档顺序，便于定位
        blocks = []
        for child in list(body):
            if child.tag == W + "p":
                blocks.append(("para", _collect_text(child)))
            elif child.tag == W + "tbl":
                cells = []
                for tr in child.findall(W + "tr"):
                    for tc in tr.findall(W + "tc"):
                        cells.append(_collect_text(tc))
                blocks.append(("table", " | ".join(cells)))

        # 媒体 / 外部引用 / 批注 / 域错误
        media = [n for n in names if n.startswith("word/media/")]
        rels = _read_rels(z, names, doc_name)
        embed_missing = _check_embeds(root, rels, names)
        ext_refs = [t for t in rels.values() if t.get("TargetMode") == "External"]
        comments = _count_comments(z, names)
        field_errors = [e for e in FIELD_ERRORS if e in full_text]

        # 串标痕迹：文档属性 / 修订与批注作者 / 隐藏文本
        doc_creator, doc_last_modified_by, doc_company, doc_manager = _doc_props(z, names)
        rev_authors = set()
        for el in list(root.iter(W + "ins")) + list(root.iter(W + "del")):
            a = el.get(W + "author")
            if a:
                rev_authors.add(a)
        comment_authors = _comment_authors(z, names)
        hidden_samples = _hidden_text(root)

        # 表格宽度实测
        width_over, table_count = _table_width(root)

        # 文件元信息（供报告证明核查的是哪一版文件）
        st = os.stat(path)
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)

    return {
        "full_text": full_text,
        "header_footer_text": header_footer_text,
        "blocks": blocks,
        "tables": tables,
        "ins_count": ins_count,
        "del_count": del_count,
        "has_toc": has_toc,
        "media": media,
        "embed_missing": embed_missing,
        "ext_refs": ext_refs,
        "comments": comments,
        "field_errors": field_errors,
        "doc_creator": doc_creator,
        "doc_last_modified_by": doc_last_modified_by,
        "doc_company": doc_company,
        "doc_manager": doc_manager,
        "rev_authors": rev_authors,
        "comment_authors": comment_authors,
        "hidden_samples": hidden_samples,
        "table_width_over": width_over,
        "table_count": table_count,
        "file_size": st.st_size,
        "file_mtime": datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"),
        "file_sha256": sha256.hexdigest(),
    }


# ---------------------------------------------------------------------------
# 检查层：逐项脚本验证（不做目测）
# ---------------------------------------------------------------------------

def run_checks(data, patterns, compliance_kw, stamp_kw, company=None):
    full = data["full_text"]
    hf = data["header_footer_text"]
    checks = []

    # 1) 占位符扫描（疑似未填内容，报告命中总数与样例）
    hits, total_hits = [], 0
    for p in patterns:
        n = full.count(p)
        total_hits += n
        if n:
            m = full.find(p)
            s = max(0, m - 12)
            e = min(len(full), m + len(p) + 12)
            hits.append("…%s…" % full[s:e].replace("\n", " "))
    if hits:
        checks.append({
            "name": "占位符/未填内容扫描",
            "status": "error",
            "evidence": "检出疑似占位符 %d 处（如：%s）" %
                        (total_hits, "；".join(hits[:3])),
        })
    else:
        checks.append({"name": "占位符/未填内容扫描", "status": "ok",
                        "evidence": "未发现 %s 等占位残留" % "、".join(patterns[:4])})

    # 2) 修订残留
    total_rev = data["ins_count"] + data["del_count"]
    if total_rev > 0:
        checks.append({
            "name": "修订残留（w:ins / w:del）",
            "status": "warn",
            "evidence": "检出插入 %d 处、删除 %d 处，定稿前建议“接受所有修订”"
                       "（已删除内容不计入正文统计）" %
                       (data["ins_count"], data["del_count"]),
        })
    else:
        checks.append({"name": "修订残留（w:ins / w:del）", "status": "ok",
                        "evidence": "未发现修订痕迹"})

    # 3) 目录域 TOC
    if data["has_toc"]:
        checks.append({"name": "目录域（TOC）", "status": "ok",
                       "evidence": "存在 TOC 域；请人工确认页码缓存已刷新"})
    else:
        checks.append({"name": "目录域（TOC）", "status": "warn",
                       "evidence": "未检出 TOC 域，若需目录请补充并刷新"})

    # 4) 符合性应答
    c = sum(full.count(k) for k in compliance_kw)
    if c == 0:
        checks.append({"name": "符合性应答", "status": "error",
                       "evidence": "未检出 %s 等应答措辞，请确认已逐项作答" %
                                  "、".join(compliance_kw)})
    else:
        checks.append({"name": "符合性应答", "status": "ok",
                       "evidence": "检出应答措辞 %d 处（关键词：%s）" %
                                  (c, "、".join(compliance_kw))})

    # 5) 盖章/声明（正文 + 页眉页脚——盖章声明常出现在页眉）
    sc = sum(full.count(k) for k in stamp_kw) + sum(hf.count(k) for k in stamp_kw)
    if sc == 0:
        checks.append({"name": "盖章/声明出现", "status": "warn",
                       "evidence": "正文与页眉页脚均未检出 %s 等关键词，"
                                   "请确认各节已附声明/盖章" % "、".join(stamp_kw)})
    else:
        where = []
        if any(full.count(k) for k in stamp_kw):
            where.append("正文")
        if any(hf.count(k) for k in stamp_kw):
            where.append("页眉页脚")
        checks.append({"name": "盖章/声明出现", "status": "ok",
                       "evidence": "检出 %s 等关键词 %d 处（命中：%s）" %
                                  ("、".join(stamp_kw), sc, "/".join(where))})

    # 6) 页码占位残留（“第 页”这类空页码；“第 5 页”正常引用不误伤）
    pg_hits = re.findall(r"Pg\s*\d{0,3}", full) + re.findall(r"第\s*页", full)
    if pg_hits:
        checks.append({"name": "页码占位残留", "status": "warn",
                       "evidence": "检出页码占位残留 %d 处，请刷新域/补全页码" % len(pg_hits)})
    else:
        checks.append({"name": "页码占位残留", "status": "ok",
                       "evidence": "未发现 Pg / 第 页 之类占位残留"})

    # 7) 表格列宽（实测 tblGrid vs 页面可用宽度）
    n_tbl = data["table_count"]
    over = data["table_width_over"]
    if n_tbl == 0:
        checks.append({"name": "表格列宽合计", "status": "ok",
                       "evidence": "未检出表格"})
    elif over is None:
        checks.append({"name": "表格列宽合计", "status": "warn",
                       "evidence": "共 %d 个表格；未能自动测量列宽（缺 tblGrid 或页面宽度定义），"
                                   "请人工目检" % n_tbl})
    elif over > 0:
        checks.append({"name": "表格列宽合计", "status": "warn",
                       "evidence": "共 %d 个表格；检测到列宽合计超出正文可用宽度约 %d twips，"
                                   "建议人工确认换行/缩放" % (n_tbl, over)})
    else:
        checks.append({"name": "表格列宽合计", "status": "ok",
                       "evidence": "共 %d 个表格；列宽合计在页面可用宽度内" % n_tbl})

    # 8) 域错误残留（Word 交叉引用/域未刷新）
    if data["field_errors"]:
        checks.append({"name": "域错误残留", "status": "error",
                       "evidence": "检出域错误文本：%s。请打开 Word 更新域/修复交叉引用"
                                   % "；".join(data["field_errors"])})
    else:
        checks.append({"name": "域错误残留", "status": "ok",
                       "evidence": "未检出“错误！未找到引用源”等域错误残留"})

    # 9) 批注残留
    if data["comments"]:
        checks.append({"name": "批注残留", "status": "warn",
                       "evidence": "检出 %d 条批注，定稿前请清除" % data["comments"]})
    else:
        checks.append({"name": "批注残留", "status": "ok",
                       "evidence": "未检出批注"})

    # 10) 外部链接/引用（离线评标环境可能失效）
    if data["ext_refs"]:
        checks.append({"name": "外部链接/引用", "status": "warn",
                       "evidence": "检出 %d 处外部引用（TargetMode=External），"
                                   "离线评标环境可能失效，请确认是否需内嵌/移除"
                                   % len(data["ext_refs"])})
    else:
        checks.append({"name": "外部链接/引用", "status": "ok",
                       "evidence": "未检出外部引用"})

    # 11) 图片引用完整性（r:embed 指向的媒体文件是否在包内存在）
    if data["embed_missing"]:
        checks.append({"name": "图片引用完整性", "status": "error",
                       "evidence": "%d 处图片引用在包内找不到对应文件（rId：%s），"
                                   "打开会显示红叉，请重新插入图片"
                                   % (len(data["embed_missing"]),
                                      "、".join(data["embed_missing"][:5]))})
    else:
        checks.append({"name": "图片引用完整性", "status": "ok",
                       "evidence": "图片引用完整（包内 %d 个媒体文件）" % len(data["media"])})

    # 12) 文档属性（作者/公司）——串标痕迹：露出其他编制方
    meta_parts = []
    if data["doc_creator"]:
        meta_parts.append("创建者：%s" % data["doc_creator"])
    if data["doc_last_modified_by"]:
        meta_parts.append("最后修改者：%s" % data["doc_last_modified_by"])
    if data["doc_company"]:
        meta_parts.append("公司：%s" % data["doc_company"])
    if data["doc_manager"]:
        meta_parts.append("经理：%s" % data["doc_manager"])
    if not meta_parts:
        meta_parts = ["未检出 docProps 元数据（文档可能经第三方工具处理）"]
    if company:
        # 仅对“公司”字段做一致性判定；创建者/最后修改者通常是人名或系统名，
        # 只展示不判定（无法据此判断是否串标）。
        if data["doc_company"] and company not in data["doc_company"]:
            checks.append({"name": "文档属性（作者/公司）", "status": "warn",
                           "evidence": "文档属性中公司为“%s”，与本公司（%s）不一致，请核查"
                                       % (data["doc_company"], company)})
        else:
            checks.append({"name": "文档属性（作者/公司）", "status": "ok",
                           "evidence": "文档属性与本公司一致；元数据：%s"
                                       % "；".join(meta_parts)})
    else:
        checks.append({"name": "文档属性（作者/公司）", "status": "ok",
                       "evidence": "文档元数据（供核对是否含其他投标人痕迹）：%s"
                                   % "；".join(meta_parts)})

    # 13) 修订/批注作者——串标痕迹：同一人/同一公司修改多家标书
    authors = sorted(set(data["rev_authors"]) | set(data["comment_authors"]))
    if authors:
        if company:
            others = [a for a in authors if company not in a]
            if others:
                checks.append({"name": "修订/批注作者", "status": "warn",
                               "evidence": "修订/批注作者：%s；检出非本公司作者（%s），请核查"
                                           % ("、".join(authors), "、".join(others))})
            else:
                checks.append({"name": "修订/批注作者", "status": "ok",
                               "evidence": "修订/批注作者均为本公司人员：%s"
                                           % "、".join(authors)})
        else:
            checks.append({"name": "修订/批注作者", "status": "ok",
                           "evidence": "修订/批注作者：%s（请人工核对是否含其他投标人/编制方）"
                                       % "、".join(authors)})
    else:
        checks.append({"name": "修订/批注作者", "status": "ok",
                       "evidence": "无修订/批注作者记录"})

    # 14) 隐藏文本——串标痕迹：残留的内部备注/其他编制方信息
    if data["hidden_samples"]:
        checks.append({"name": "隐藏文本", "status": "warn",
                       "evidence": "检出 %d 段隐藏文字（如：%s），定稿前请确认是否需保留"
                                   % (len(data["hidden_samples"]),
                                      "；".join(data["hidden_samples"][:3]))})
    else:
        checks.append({"name": "隐藏文本", "status": "ok",
                       "evidence": "未检出隐藏文字"})

    return checks


# ---------------------------------------------------------------------------
# 评分层（依据评标办法重估，给出三档区间与假设）
# ---------------------------------------------------------------------------

def build_score_worksheet(eval_sheets):
    """从评标办法结构化行中抽取疑似评分条目。

    eval_sheets: [{"sheet": 名, "rows": [{"row": 行号, "cells": [...]}]}]
    返回: [{"sheet", "row", "line"}]，供报告渲染成表格。
    """
    if not eval_sheets:
        return None
    # 用组合词避免单个“分”字大量误命中（“部分”“分明”等）
    kw = re.compile(r"权重|评分|分值|得分|满分|评审|%|业绩|资质|价格|技术|商务|档")
    picked = []
    for sh in eval_sheets:
        for r in sh["rows"]:
            line = " ".join(str(c) for c in r["cells"] if str(c) != "")
            if line.strip() and kw.search(line):
                picked.append({"sheet": sh["sheet"], "row": r["row"], "line": line[:300]})
            if len(picked) >= 60:
                break
        if len(picked) >= 60:
            break
    return picked


# ---------------------------------------------------------------------------
# 报告层：生成自包含 HTML（样式优先读 references/report_template.html）
# ---------------------------------------------------------------------------

CSS_FALLBACK = """    :root {
      --c-primary: #0f62fe;
      --c-on-primary: #ffffff;
      --c-ink: #161616;
      --c-ink-muted: #525252;
      --c-ink-subtle: #8c8c8c;
      --c-canvas: #ffffff;
      --c-surface-1: #f4f4f4;
      --c-hairline: #e0e0e0;
      --c-success: #24a148;
      --c-warning: #f1c21b;
      --c-error: #da1e28;
      --font: 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif;
      --ls-body: 0.16px;
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: var(--font); background: var(--c-canvas); color: var(--c-ink); line-height: 1.5; letter-spacing: var(--ls-body); -webkit-font-smoothing: antialiased; }
    .page { max-width: 960px; margin: 0 auto; padding: 32px 24px 64px; }
    h1 { font-size: 32px; font-weight: 300; line-height: 1.25; margin: 0 0 8px; }
    .subtitle { font-size: 16px; color: var(--c-ink-muted); margin-bottom: 8px; }
    .meta { font-size: 12px; color: var(--c-ink-subtle); margin-bottom: 24px; word-break: break-all; }
    h2 { font-size: 20px; font-weight: 400; line-height: 1.4; margin: 32px 0 12px; padding-bottom: 8px; border-bottom: 1px solid var(--c-hairline); }
    h3 { font-size: 16px; font-weight: 600; margin: 20px 0 8px; }
    .card { background: var(--c-canvas); border: 1px solid var(--c-hairline); padding: 16px 20px; margin-bottom: 12px; }
    .band { background: var(--c-surface-1); border: 1px solid var(--c-hairline); padding: 16px 20px; margin-bottom: 12px; }
    .kpis { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 8px; }
    .kpi { flex: 1 1 160px; background: var(--c-canvas); border: 1px solid var(--c-hairline); padding: 12px 16px; }
    .kpi .label { font-size: 12px; color: var(--c-ink-subtle); letter-spacing: 0.32px; }
    .kpi .value { font-size: 24px; font-weight: 300; margin-top: 4px; }
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--c-hairline); vertical-align: top; }
    th { font-weight: 600; color: var(--c-ink); background: var(--c-surface-1); }
    tbody tr:nth-child(even) { background: var(--c-surface-1); }
    .pill { display: inline-block; font-size: 12px; padding: 2px 8px; border-radius: 9999px; letter-spacing: 0.32px; }
    .pill.ok    { color: var(--c-success); border: 1px solid var(--c-success); }
    .pill.warn  { color: #8a6d00; border: 1px solid var(--c-warning); }
    .pill.error { color: var(--c-error); border: 1px solid var(--c-error); }
    .score-band { display: flex; gap: 12px; flex-wrap: wrap; }
    .score-case { flex: 1 1 180px; border: 1px solid var(--c-hairline); padding: 12px 16px; }
    .score-case .name { font-size: 12px; color: var(--c-ink-subtle); }
    .score-case .score { font-size: 24px; font-weight: 300; color: var(--c-primary); margin-top: 4px; }
    .score-case .assume { font-size: 13px; color: var(--c-ink-muted); margin-top: 4px; }
    .risk { border-left: 3px solid var(--c-error); padding: 8px 12px; margin: 8px 0; background: var(--c-surface-1); }
    .risk .risk-title { font-weight: 600; color: var(--c-error); }
    .risk .risk-detail { font-size: 14px; color: var(--c-ink-muted); margin-top: 2px; }
    .muted { color: var(--c-ink-muted); font-size: 13px; }
    .note { font-size: 12px; color: var(--c-ink-subtle); margin-top: 16px; }
    pre { white-space: pre-wrap; font-size: 13px; color: var(--c-ink-muted); }"""


def load_css():
    """优先读 references/report_template.html 的 <style>，保证样式单源维护。"""
    here = os.path.dirname(os.path.abspath(__file__))
    tmpl = os.path.join(here, "..", "references", "report_template.html")
    try:
        with open(tmpl, encoding="utf-8") as f:
            m = re.search(r"<style>(.*?)</style>", f.read(), re.S)
        if m and m.group(1).strip():
            return m.group(1)
    except (OSError, IOError):
        pass
    return CSS_FALLBACK


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))


def pill(status):
    label = {"ok": "已通过", "warn": "待处理", "error": "风险"}.get(status, status)
    return '<span class="pill %s">%s</span>' % (status, label)


def _fmt_size(n):
    if n >= 1024 * 1024:
        return "%.1f MB" % (n / 1024.0 / 1024.0)
    if n >= 1024:
        return "%.1f KB" % (n / 1024.0)
    return "%d B" % n


def build_report(title, filename, data, checks, eval_rows, score=None, score_note=None):
    css = load_css()
    total = len(checks)
    ok = sum(1 for c in checks if c["status"] == "ok")
    warn = sum(1 for c in checks if c["status"] == "warn")
    error = sum(1 for c in checks if c["status"] == "error")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # 二、调整项逐条核验表（全部检查项）
    adj_rows = "".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (esc(c["name"]), pill(c["status"]), esc(c["evidence"]))
        for c in checks
    )

    # 三、评分风险块（error / warn 视为需拍板项）
    risk_rows = ""
    for c in checks:
        if c["status"] in ("error", "warn"):
            risk_rows += ('<div class="risk"><div class="risk-title">%s</div>'
                          '<div class="risk-detail">%s</div></div>') % (esc(c["name"]), esc(c["evidence"]))
    if not risk_rows:
        risk_rows = '<div class="risk"><div class="risk-title">未发现显著风险</div>' \
                    '<div class="risk-detail">各项核验均通过。</div></div>'

    # 四、评分工作表（来自评标办法，结构化表格）
    score_block = ""
    picked = build_score_worksheet(eval_rows)
    if picked:
        rows_html = "".join(
            "<tr><td>%d</td><td>%s</td><td>%d</td><td>%s</td></tr>"
            % (i + 1, esc(p["sheet"]), p["row"], esc(p["line"]))
            for i, p in enumerate(picked)
        )
        score_block = (
            '<div class="card"><h3>评标办法抽取（供核定权重/档位）</h3>'
            '<table><thead><tr><th>#</th><th>工作表</th><th>行</th>'
            '<th>疑似评分条目</th></tr></thead><tbody>%s</tbody></table>'
            '<p class="muted">以上为从评标办法中自动抽取的疑似评分条目，'
            "请据此核定商务/技术/价格权重、业绩有效性判定与评分档位，"
            "并自行填入下方三档得分。</p></div>"
        ) % rows_html
    else:
        score_block = '<div class="card"><h3>评标办法</h3><p class="muted">未提供评标办法 .xlsx 或未抽取到评分条目，' \
                      "请手动依据招标文件核定评分权重后填入下方三档得分。</p></div>"

    # 三档得分（参数未提供则显示 —）
    score = score or {}
    low = score.get("low")
    mid = score.get("mid")
    high = score.get("high")
    score_range = "待核定"
    if low is not None and high is not None:
        score_range = "%s–%s" % (low, high)
    elif low is not None:
        score_range = "≥%s" % low

    def _case(name, val, assume):
        v = "—" if val is None else esc(val)
        return ('<div class="score-case"><div class="name">%s</div>'
                '<div class="score">%s</div><div class="assume">%s</div></div>') % (
                    name, v, assume)

    cases = (
        _case("保守情形", low, "按“仅确认项计分”假设")
        + _case("基准情形", mid, "按“应得项计分”假设")
        + _case("乐观情形", high, "按“争取项计分”假设")
    )
    note_txt = score_note or "评分口径：权重、业绩有效性判定、评分档位等以评标办法原文为准。"

    # 五、待处理检查项（仅 warn/error，避免与第二节重复）
    pending = [c for c in checks if c["status"] != "ok"]
    if pending:
        pend_rows = "".join(
            "<tr><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (esc(c["name"]), pill(c["status"]), esc(c["evidence"]))
            for c in pending
        )
    else:
        pend_rows = "<tr><td colspan='3'>无待处理项</td></tr>"

    # 文件元信息
    meta_line = (
        "文件：%s　|　大小 %s　|　最后修改 %s<br>SHA-256：%s"
        % (esc(filename), _fmt_size(data["file_size"]), esc(data["file_mtime"]),
           esc(data["file_sha256"]))
    )

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>%s</title>
  <style>%s</style>
</head>
<body>
  <div class="page">
    <header>
      <h1>%s</h1>
      <p class="subtitle">%s · 核查时间 %s</p>
      <p class="meta">%s</p>
    </header>

    <h2>一、核查概要</h2>
    <div class="kpis">
      <div class="kpi"><div class="label">检查项总数</div><div class="value">%d</div></div>
      <div class="kpi"><div class="label">通过 / 待处理 / 风险</div><div class="value">%d / %d / %d</div></div>
      <div class="kpi"><div class="label">重估得分区间</div><div class="value">%s</div></div>
    </div>
    <div class="band"><p>本报告由可移植版脚本（零依赖，仅标准库）只读生成，未修改原标书文件；
    涉及得分与合规的事项须由投标人最终拍板。</p></div>

    <h2>二、调整项逐条核验结果</h2>
    <table>
      <thead><tr><th>调整项</th><th>核验结果</th><th>证据 / 定位</th></tr></thead>
      <tbody>%s</tbody>
    </table>

    <h2>三、评分风险与修改建议</h2>
    %s
    <div class="card"><h3>修改建议</h3><p>风险/待处理项已逐条列示，请据此修订后重新运行本脚本核验。</p></div>

    <h2>四、重估得分</h2>
    <div class="score-band">%s</div>
    %s
    <p class="muted">%s</p>

    <h2>五、待处理检查项</h2>
    <table>
      <thead><tr><th>检查项</th><th>状态</th><th>证据 / 处理建议</th></tr></thead>
      <tbody>%s</tbody>
    </table>

    <p class="note">本报告为只读核查结果，未修改原标书文件；涉及得分与合规的事项须由投标人最终拍板。</p>
  </div>
</body>
</html>
""" % (esc(title), css, esc(title), esc(filename), now, meta_line,
       total, ok, warn, error, esc(score_range),
       adj_rows, risk_rows, cases, score_block, esc(note_txt), pend_rows)

    return html


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

def _resolve_kw(args, key):
    """--key 提供则替换默认，--key-add 在其后追加（去重）。"""
    base = _split_kw(getattr(args, key)) if getattr(args, key) else list(DEFAULTS[key])
    add = _split_kw(getattr(args, key + "_add") or "")
    for x in add:
        if x not in base:
            base.append(x)
    return base


def _split_kw(s):
    return [p for p in s.split(";") if p]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    # 确保同目录模块可导入（不依赖当前工作目录）
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    ap = argparse.ArgumentParser(description="投标响应文件审阅复核（可移植版，零依赖）")
    ap.add_argument("docx", help="标书 .docx 路径")
    ap.add_argument("--eval", help="评标办法 .xlsx 路径（可选）", default=None)
    ap.add_argument("--out", help="输出 HTML 报告路径", default="bid_review_report.html")
    ap.add_argument("--name", help="报告标题", default="投标响应文件核查报告")
    ap.add_argument("--patterns", help="占位符模式，分号分隔（替换默认）", default=None)
    ap.add_argument("--patterns-add", help="追加占位符模式，分号分隔", default=None)
    ap.add_argument("--compliance", help="符合性应答关键词，分号分隔（替换默认）", default=None)
    ap.add_argument("--compliance-add", help="追加符合性应答关键词", default=None)
    ap.add_argument("--stamp", help="盖章/声明关键词，分号分隔（替换默认）", default=None)
    ap.add_argument("--stamp-add", help="追加盖章/声明关键词", default=None)
    ap.add_argument("--score-low", type=int, default=None, help="保守情形得分")
    ap.add_argument("--score-mid", type=int, default=None, help="基准情形得分")
    ap.add_argument("--score-high", type=int, default=None, help="乐观情形得分")
    ap.add_argument("--score-note", default=None, help="评分口径说明，覆盖默认文案")
    ap.add_argument("--company", default=None,
                    help="本公司名称（用于串标痕迹核验：文档属性/修订批注作者与本公司一致性）")
    args = ap.parse_args()

    if not os.path.exists(args.docx):
        print("错误：找不到标书文件 %s" % args.docx, file=sys.stderr)
        return 2

    try:
        data = extract_docx(args.docx)
    except Exception as e:
        print("解析标书失败：%s" % e, file=sys.stderr)
        return 2

    patterns = _resolve_kw(args, "patterns")
    compliance_kw = _resolve_kw(args, "compliance")
    stamp_kw = _resolve_kw(args, "stamp")

    checks = run_checks(data, patterns, compliance_kw, stamp_kw, company=args.company)

    eval_rows = []
    if args.eval:
        if os.path.exists(args.eval):
            try:
                from xlsx_eval import extract_xlsx
                eval_rows = extract_xlsx(args.eval)
            except Exception as e:
                print("解析评标办法失败（跳过评分工作表）：%s" % e, file=sys.stderr)
        else:
            print("警告：找不到评标办法文件 %s（跳过评分工作表）" % args.eval, file=sys.stderr)

    score = {}
    for k in ("low", "mid", "high"):
        v = getattr(args, "score_" + k)
        if v is not None:
            score[k] = v

    html = build_report(args.name, os.path.basename(args.docx), data, checks,
                        eval_rows, score=score or None, score_note=args.score_note)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)

    ok = sum(1 for c in checks if c["status"] == "ok")
    warn = sum(1 for c in checks if c["status"] == "warn")
    error = sum(1 for c in checks if c["status"] == "error")
    print("核查完成：检查项 %d，通过 %d / 待处理 %d / 风险 %d" % (len(checks), ok, warn, error))
    print("报告已生成：%s" % os.path.abspath(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
