#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自测断言：生成样本 → 运行核心抽取与检查 → 断言关键行为。
防止后续改动悄悄破坏“修订感知 / 页眉解析 / 域错误检测 / 占位符扫描”等核心行为。

运行：python run_sample_test.py
退出码：0=全部通过，1=存在失败。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, HERE)

FAILED = []
PASSED = 0


def check(name, cond):
    global PASSED
    print(("  PASS  " if cond else "  FAIL  ") + name)
    if cond:
        PASSED += 1
    else:
        FAILED.append(name)


def main():
    # 1) 生成样本
    print("== 生成样本 ==")
    r = subprocess.run([sys.executable, os.path.join(HERE, "make_sample.py")],
                       cwd=HERE, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr

    from docx_review import extract_docx, run_checks, DEFAULTS, FIELD_ERRORS
    from xlsx_eval import extract_xlsx

    print("== 抽取层 ==")
    data = extract_docx(os.path.join(HERE, "sample_bid.docx"))

    check("修订删除文本不入正式文本",
          "旧版本待删除内容" not in data["full_text"])
    check("页眉文本被收集（盖章声明在页眉）",
          "已加盖公章" in data["header_footer_text"])
    check("修订计数检出删除 1 处",
          data["del_count"] == 1)
    check("TOC 域被检出", data["has_toc"] is True)
    check("域错误被检出",
          any(e in data["full_text"] for e in FIELD_ERRORS))
    check("文件元信息齐全",
          data["file_size"] > 0 and len(data["file_sha256"]) == 64)
    check("表格按列抽取（2 行 x 2 列）",
          len(data["tables"]) == 1 and len(data["tables"][0]) == 2
          and len(data["tables"][0][0]) == 2)

    print("== 检查层 ==")
    checks = run_checks(data, DEFAULTS["patterns"], DEFAULTS["compliance"], DEFAULTS["stamp"])
    status = {c["name"]: c["status"] for c in checks}
    check("占位符/未填内容扫描 = error",
          status.get("占位符/未填内容扫描") == "error")
    check("修订残留 = warn",
          status.get("修订残留（w:ins / w:del）") == "warn")
    check("目录域（TOC）= ok", status.get("目录域（TOC）") == "ok")
    check("符合性应答 = ok", status.get("符合性应答") == "ok")
    check("盖章/声明出现 = ok（页眉命中）",
          status.get("盖章/声明出现") == "ok")
    check("页码占位残留 = ok", status.get("页码占位残留") == "ok")
    check("域错误残留 = error", status.get("域错误残留") == "error")
    check("批注残留 = ok", status.get("批注残留") == "ok")
    check("外部链接/引用 = ok", status.get("外部链接/引用") == "ok")
    check("图片引用完整性 = ok", status.get("图片引用完整性") == "ok")
    check("表格列宽合计 = ok（可实测）", status.get("表格列宽合计") == "ok")

    print("== 表格列宽实测（超宽路径）==")
    import xml.etree.ElementTree as ET
    from docx_review import _table_width
    over_xml = (
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body><w:tbl><w:tblGrid><w:gridCol w:w=\"6000\"/><w:gridCol w:w=\"6000\"/>"
        "</w:tblGrid><w:tr><w:tc/></w:tr></w:tbl>"
        '<w:sectPr><w:pgSz w:w="11906"/>'
        '<w:pgMar w:left="1800" w:right="1800"/></w:sectPr></w:body></w:document>'
    )
    over, n = _table_width(ET.fromstring(over_xml))
    check("超宽表格被检出（over>0）", over is not None and over > 0 and n == 1)

    print("== 串标痕迹检查（单文件）==")
    check("文档属性（作者/公司）= ok（展示元数据）",
          status.get("文档属性（作者/公司）") == "ok"
          and "示例工程有限公司" in [c["evidence"] for c in checks
                                     if c["name"] == "文档属性（作者/公司）"][0])
    check("修订/批注作者 = ok（本公司人员）", status.get("修订/批注作者") == "ok")
    check("隐藏文本 = warn（检出隐藏备注）", status.get("隐藏文本") == "warn")

    checks_c = run_checks(data, DEFAULTS["patterns"], DEFAULTS["compliance"],
                          DEFAULTS["stamp"], company="示例工程有限公司")
    status_c = {c["name"]: c["status"] for c in checks_c}
    check("--company 匹配：文档属性 = ok", status_c.get("文档属性（作者/公司）") == "ok")
    check("--company 匹配：修订/批注作者 = ok", status_c.get("修订/批注作者") == "ok")

    checks_o = run_checks(data, DEFAULTS["patterns"], DEFAULTS["compliance"],
                          DEFAULTS["stamp"], company="其他工程有限公司")
    status_o = {c["name"]: c["status"] for c in checks_o}
    check("--company 不匹配：文档属性 = warn", status_o.get("文档属性（作者/公司）") == "warn")

    print("== 围标/串标对比（多文件）==")
    coll = os.path.join(HERE, "collusion_b.docx")
    _make_collusion_docx(coll)
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "bid_collusion.py"),
         os.path.join(HERE, "sample_bid.docx"), coll,
         "--out", os.path.join(HERE, "collusion_report.html")],
        cwd=ROOT, capture_output=True, text=True)
    check("bid_collusion 运行成功", r.returncode == 0)
    check("检出创建者相同信号", "创建者" in r.stdout)
    check("检出修订作者交集", "修订作者交集" in r.stdout)
    check("控制台标记高风险", "高风险" in r.stdout)
    chtml = ""
    if os.path.exists(os.path.join(HERE, "collusion_report.html")):
        with open(os.path.join(HERE, "collusion_report.html"), encoding="utf-8") as f:
            chtml = f.read()
    check("对比报告 HTML 含信号表", "相同图片指纹" in chtml or "修订作者交集" in chtml)
    check("对比报告含使用注意说明", "线索而非结论" in chtml)

    print("== 报告层 ==")
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "docx_review.py"),
         os.path.join(HERE, "sample_bid.docx"),
         "--out", os.path.join(HERE, "sample_report.html"),
         "--score-low", "80", "--score-mid", "85", "--score-high", "90"],
        cwd=ROOT, capture_output=True, text=True)
    check("docx_review 命令行运行成功", r.returncode == 0 and r.stderr == "")
    if r.stderr:
        print("    stderr: %s" % r.stderr.strip())
    html = ""
    if os.path.exists(os.path.join(HERE, "sample_report.html")):
        with open(os.path.join(HERE, "sample_report.html"), encoding="utf-8") as f:
            html = f.read()
    check("报告含 SHA-256", "SHA-256" in html)
    check("报告含三档得分 80/85/90", "80" in html and "85" in html and "90" in html)
    check("第五节只列待办（无‘已通过’pill）",
          "<span class=\"pill ok\">已通过</span>" not in html.split("五、待处理检查项")[1]
          if "五、待处理检查项" in html else False)

    print("== 评标办法抽取 ==")
    # 构造一个最小 xlsx 做零依赖验证（共享字符串 + 两个 sheet + 隐藏表）
    if _make_mini_xlsx():
        sheets = extract_xlsx(os.path.join(HERE, "mini_eval.xlsx"))
        names = [s["sheet"] for s in sheets]
        check("sheet 顺序按 workbook.xml（非字符串排序）", names == ["评分办法", "细则"])
        check("隐藏工作表被跳过", "隐藏表" not in names)
        # 空单元格不导致列错位：A1=评分项, C1=分值
        r0 = sheets[0]["rows"][0]["cells"]
        check("列位保持（第3列=分值）", len(r0) >= 3 and r0[2] == "分值")
        check("合并单元格值铺开", any(c == "技术标" for s in sheets for r in s["rows"] for c in r["cells"]))

    print("== 结果 ==")
    if FAILED:
        print("失败 %d 项：%s" % (len(FAILED), "；".join(FAILED)))
        sys.exit(1)
    print("全部通过（%d 项断言）。" % PASSED)
    sys.exit(0)


def _make_mini_xlsx():
    """生成一个极简 .xlsx：两个可见表 + 一个隐藏表，含共享字符串、空列、合并单元格。"""
    import zipfile

    CT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
<Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
<Override PartName="/xl/worksheets/sheet3.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
<Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>
</Types>"""
    RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""
    WB_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet3.xml"/>
</Relationships>"""
    WB = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets>
<sheet name="评分办法" sheetId="1" r:id="rId1"/>
<sheet name="细则" sheetId="2" r:id="rId2"/>
<sheet name="隐藏表" sheetId="3" state="hidden" r:id="rId3"/>
</sheets>
</workbook>"""
    SS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="4" uniqueCount="4">
<si><t>评分项</t></si><si><t>分值</t></si><si><t>技术标</t></si><si><t>权重30%</t></si>
</sst>"""
    # sheet1：A1=评分项，C1=分值（B 列为空，验证列位）；A2:A3 合并且值为“技术标”
    S1 = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<mergeCells count="1"><mergeCell ref="A2:A3"/></mergeCells>
<sheetData>
<row r="1"><c r="A1" t="s"><v>0</v></c><c r="C1" t="s"><v>1</v></c></row>
<row r="2"><c r="A2" t="s"><v>2</v></c><c r="B2"><v>5</v></c></row>
<row r="3"><c r="C3" t="s"><v>3</v></c></row>
</sheetData>
</worksheet>"""
    # sheet2：一行评分项（验证第二张表）
    S2 = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<sheetData><row r="1"><c r="A1"><v>1</v></c></row></sheetData>
</worksheet>"""
    S3 = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<sheetData><row r="1"><c r="A1"><v>9</v></c></row></sheetData>
</worksheet>"""
    out = os.path.join(HERE, "mini_eval.xlsx")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CT)
        z.writestr("_rels/.rels", RELS)
        z.writestr("xl/_rels/workbook.xml.rels", WB_RELS)
        z.writestr("xl/workbook.xml", WB)
        z.writestr("xl/sharedStrings.xml", SS)
        z.writestr("xl/worksheets/sheet1.xml", S1)
        z.writestr("xl/worksheets/sheet2.xml", S2)
        z.writestr("xl/worksheets/sheet3.xml", S3)
    return True


def _make_collusion_docx(path):
    """构造“疑似串标”第二投标人文件：与 sample_bid.docx 同创建者、
    修订作者交集、共用同一图片，但正文与公司不同。"""
    import zipfile

    PNG_BYTES = bytes.fromhex(
        "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
        "0000000d49444154789c636001000000ffff03000006000557bfabd40000000049454e44ae426082"
    )
    CT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""
    RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
    DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rIdImg1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image1.png"/>
</Relationships>"""
    CORE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                   xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:dcterms="http://purl.org/dc/terms/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dc:creator>测试编制人</dc:creator>
<cp:lastModifiedBy>乙公司编制人</cp:lastModifiedBy>
<dcterms:created xsi:type="dcterms:W3CDTF">2026-09-02T09:00:00Z</dcterms:created>
<dcterms:modified xsi:type="dcterms:W3CDTF">2026-09-11T09:00:00Z</dcterms:modified>
</cp:coreProperties>"""
    APP = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
            xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
<Company>乙建设工程有限公司</Company>
<Manager>李四</Manager>
</Properties>"""
    # 修订插入作者与 sample_bid.docx 的删除作者相同 -> 修订作者交集信号
    DOCUMENT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<w:body>
<w:p><w:r><w:t>乙公司投标文件</w:t></w:r></w:p>
<w:p><w:r><w:t>本响应文件由我司独立编制，技术方案详见附件。</w:t></w:r></w:p>
<w:p><w:ins w:id="2" w:author="示例工程有限公司 编制组" w:date="2026-09-05T00:00:00Z">
<w:r><w:t>补充业绩证明文件。</w:t></w:r></w:ins></w:p>
<w:p><w:r><w:drawing>
<wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" distT="0" distB="0" distL="0" distR="0">
<wp:extent cx="100000" cy="100000"/>
<wp:docPr id="1" name="图片1"/>
<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
<pic:nvPicPr><pic:cNvPr id="1" name="图片1"/><pic:cNvPicPr/></pic:nvPicPr>
<pic:blipFill><a:blip r:embed="rIdImg1"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="100000" cy="100000"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>
</pic:pic>
</a:graphicData>
</a:graphic>
</wp:inline>
</w:drawing></w:r></w:p>
</w:body>
</w:document>"""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CT)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/media/image1.png", PNG_BYTES)
        z.writestr("docProps/core.xml", CORE)
        z.writestr("docProps/app.xml", APP)
        z.writestr("word/document.xml", DOCUMENT)
    return True


if __name__ == "__main__":
    main()
