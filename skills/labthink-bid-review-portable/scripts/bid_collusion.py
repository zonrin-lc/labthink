#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
围标/串标痕迹对比 —— 多投标文件横向比对（零依赖，仅用 Python 标准库）

用途：
  招标人 / 代理机构：对比多家投标文件，识别“不同投标人却出自同一制作链”的信号；
  投标人自查：把自己的标书与其他渠道拿到的关联文件对比。

对比维度（逐对文件）：
  * 文档属性（创建者 / 最后修改者 / 公司 / 经理）是否相同      -> 高
  * 修订作者（w:ins / w:del 的 author）是否有交集             -> 高
  * 批注作者（comments.xml 的 author）是否有交集              -> 高
  * 正文相似度（去空白后 4-gram Jaccard）                     -> 高 / 中
  * 图片指纹（word/media/* 内容 SHA-256）是否相同              -> 中
  * 文档属性指纹（docProps/core.xml、app.xml 内容一致）        -> 高

重要说明：
  每个信号仅是“线索”而非“结论”。例如创建者同为“Administrator”、
  或两家都引用了招标文件截图（图片指纹相同）都可能是巧合。
  请结合招标文件、开标记录等证据综合判断，必要时移交监管/法务。

用法：
  python bid_collusion.py 标书A.docx 标书B.docx [标书C.docx ...]
                         [--out report.html] [--name "报告标题"]

退出码：0=正常，2=参数或解析错误。
"""
import argparse
import datetime
import hashlib
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_review import extract_docx, load_css, esc


def _sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def _normalize(text):
    return re.sub(r"[\s\u3000]+", "", text or "")


def _shingles(s, k=4):
    if len(s) < k:
        return {s} if s else set()
    return {s[i:i + k] for i in range(len(s) - k + 1)}


def _jaccard(a, b):
    sa, sb = _shingles(a), _shingles(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def extract_meta(path):
    """抽取单个 docx 的串标相关指纹。"""
    data = extract_docx(path)
    meta = {
        "name": os.path.basename(path),
        "creator": data["doc_creator"],
        "last_modified_by": data["doc_last_modified_by"],
        "company": data["doc_company"],
        "manager": data["doc_manager"],
        "rev_authors": data["rev_authors"],
        "comment_authors": data["comment_authors"],
        "norm_text": _normalize(data["full_text"]),
    }
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        meta["media_hashes"] = {
            n: _sha256_bytes(z.read(n)) for n in names if n.startswith("word/media/")
        }
        meta["docprops_hashes"] = {
            n: _sha256_bytes(z.read(n))
            for n in ("docProps/core.xml", "docProps/app.xml") if n in names
        }
    return meta


def compare_pairs(metas):
    """逐对对比，返回带风险等级的信号列表。"""
    pairs = []
    for i in range(len(metas)):
        for j in range(i + 1, len(metas)):
            a, b = metas[i], metas[j]
            signals = []

            for field, label in (("creator", "创建者"), ("last_modified_by", "最后修改者"),
                                 ("company", "公司"), ("manager", "经理")):
                if a[field] and a[field] == b[field]:
                    signals.append({"label": label, "value": a[field], "level": "high"})

            ov = sorted(a["rev_authors"] & b["rev_authors"])
            if ov:
                signals.append({"label": "修订作者交集", "value": "、".join(ov), "level": "high"})
            ov2 = sorted(a["comment_authors"] & b["comment_authors"])
            if ov2:
                signals.append({"label": "批注作者交集", "value": "、".join(ov2), "level": "high"})

            sim = _jaccard(a["norm_text"], b["norm_text"])
            if sim >= 0.9:
                signals.append({"label": "正文相似度",
                                "value": "%.1f%%（极高，疑似同一底稿套用）" % (sim * 100),
                                "level": "high"})
            elif sim >= 0.75:
                signals.append({"label": "正文相似度",
                                "value": "%.1f%%（高，疑似同模板/同编制链）" % (sim * 100),
                                "level": "medium"})
            elif sim >= 0.6:
                signals.append({"label": "正文相似度",
                                "value": "%.1f%%（中，存在相似段落，建议人工比对）" % (sim * 100),
                                "level": "medium"})

            same_media = set(a["media_hashes"].values()) & set(b["media_hashes"].values())
            if same_media:
                fnames = sorted(n for n, h in a["media_hashes"].items() if h in same_media)
                signals.append({"label": "相同图片指纹",
                                "value": "%d 个相同文件（如：%s）"
                                         % (len(same_media), "、".join(fnames[:3])),
                                "level": "medium"})

            same_docprops = set(a["docprops_hashes"].values()) & set(b["docprops_hashes"].values())
            if same_docprops:
                signals.append({"label": "文档属性指纹相同",
                                "value": "core.xml/app.xml 内容一致（疑似同一制作链）",
                                "level": "high"})

            if any(s["level"] == "high" for s in signals):
                level = "high"
            elif any(s["level"] == "medium" for s in signals):
                level = "medium"
            else:
                level = "low"

            pairs.append({"a": a["name"], "b": b["name"], "signals": signals,
                          "level": level, "sim": sim})
    return pairs


def _pill(level):
    label = {"high": "高风险", "medium": "中风险", "low": "低风险"}[level]
    return '<span class="pill %s">%s</span>' % ({"high": "error", "medium": "warn", "low": "ok"}[level], label)


def build_html(title, names, pairs, now):
    css = load_css()
    file_list = "".join("<li>%s</li>" % esc(n) for n in names)
    if not pairs:
        return ("<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"UTF-8\">"
                "<title>%s</title></head><body><div class=\"page\"><h1>%s</h1>"
                "<p>文件不足 2 个，无法对比。</p></div></body></html>") % (esc(title), esc(title))

    cards = []
    for p in pairs:
        if p["signals"]:
            rows = "".join(
                "<tr><td>%s</td><td>%s</td><td>%s</td></tr>"
                % (esc(s["label"]), esc(s["value"]),
                   _pill("high" if s["level"] == "high" else "medium"))
                for s in p["signals"]
            )
        else:
            rows = "<tr><td colspan='3'>未检出明显串标信号</td></tr>"
        cards.append(
            '<div class="card"><h3>%s  vs  %s　%s</h3>'
            "<table><thead><tr><th>信号</th><th>值</th><th>等级</th></tr></thead>"
            "<tbody>%s</tbody></table></div>"
            % (esc(p["a"]), esc(p["b"]), _pill(p["level"]), rows)
        )

    high_n = sum(1 for p in pairs if p["level"] == "high")
    medium_n = sum(1 for p in pairs if p["level"] == "medium")

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
      <p class="subtitle">参与对比 %d 份投标文件 · 核查时间 %s</p>
    </header>

    <h2>一、对比文件</h2>
    <ul>%s</ul>

    <h2>二、逐对对比结果</h2>
    %s

    <h2>三、结论与使用注意</h2>
    <div class="band">
      <p>共 %d 对文件：高风险 %d 对、中风险 %d 对。</p>
      <p class="muted">本报告由脚本只读生成。所有信号均为<b>线索而非结论</b>：
      创建者同为系统默认名、共用招标文件截图等都可能造成巧合命中；
      请结合招标文件要求、开标记录、保证金来源等证据综合判断，
      涉及围标串标认定须移交监管或法务部门依法处理。</p>
    </div>

    <p class="note">本报告未修改任何投标文件。</p>
  </div>
</body>
</html>
""" % (esc(title), css, esc(title), len(names), now, file_list,
       "".join(cards), len(pairs), high_n, medium_n)
    return html


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(description="围标/串标痕迹对比（可移植版，零依赖）")
    ap.add_argument("docx", nargs="+", help="投标文件 .docx 路径（至少 2 个）")
    ap.add_argument("--out", help="输出 HTML 报告路径", default=None)
    ap.add_argument("--name", help="报告标题", default="围标/串标痕迹对比报告")
    args = ap.parse_args()

    if len(args.docx) < 2:
        print("错误：至少需要 2 个投标文件才能对比", file=sys.stderr)
        return 2

    metas = []
    for p in args.docx:
        if not os.path.exists(p):
            print("错误：找不到文件 %s" % p, file=sys.stderr)
            return 2
        try:
            metas.append(extract_meta(p))
        except Exception as e:
            print("解析失败 %s：%s" % (p, e), file=sys.stderr)
            return 2

    pairs = compare_pairs(metas)

    # 控制台输出
    print("== 参与对比 ==")
    for i, m in enumerate(metas, 1):
        print("%d. %s" % (i, m["name"]))
    print()
    for p in pairs:
        level_txt = {"high": "高风险", "medium": "中风险", "low": "低风险"}[p["level"]]
        print("[%s] %s vs %s" % (level_txt, p["a"], p["b"]))
        if p["signals"]:
            for s in p["signals"]:
                print("  - %s：%s" % (s["label"], s["value"]))
        else:
            print("  - 未检出明显串标信号")
        print()

    if args.out:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(build_html(args.name, [m["name"] for m in metas], pairs, now))
        print("报告已生成：%s" % os.path.abspath(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
