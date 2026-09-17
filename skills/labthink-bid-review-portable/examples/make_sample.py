#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成一个用于自测的极小 .docx（不依赖任何第三方库），供 docx_review.py 验证零依赖解析。

运行：python make_sample.py
产物：同目录 sample_bid.docx

样本覆盖（供 run_sample_test.py 断言）：
  * 符合性应答（正文）
  * 页眉盖章声明（验证页眉解析：正文不含盖章关键词）
  * 一处标准修订残留（w:del + w:delText，验证删除文本不入正式文本）
  * TOC 域
  * 域错误残留（“错误！未找到引用源”）
  * 一处占位符（表格内“待补充XXX”）
"""
import zipfile

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rIdH1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>
<Relationship Id="rIdImg1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image1.png"/>
</Relationships>"""

# 1x1 透明 PNG（用于图片引用完整性 + 围标对比的图片指纹测试）
PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d49444154789c636001000000ffff03000006000557bfabd40000000049454e44ae426082"
)

HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:p><w:r><w:t>投标文件页眉声明：本响应文件已加盖公章。</w:t></w:r></w:p>
</w:hdr>"""

CORE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                   xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:dcterms="http://purl.org/dc/terms/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dc:creator>测试编制人</dc:creator>
<cp:lastModifiedBy>测试编制人</cp:lastModifiedBy>
<dcterms:created xsi:type="dcterms:W3CDTF">2026-09-01T08:00:00Z</dcterms:created>
<dcterms:modified xsi:type="dcterms:W3CDTF">2026-09-10T08:00:00Z</dcterms:modified>
</cp:coreProperties>"""

APP = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
            xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
<Company>示例工程有限公司</Company>
<Manager>张三</Manager>
</Properties>"""

# 注意：修订删除使用标准结构 w:del > w:r > w:delText；
# docx_review.py 会跳过 w:del 子树，因此“旧版本待删除内容”不得进入正式文本统计。
# 修订作者 = 本公司编制组，用于串标痕迹核验（--company 匹配）。
DOCUMENT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<w:body>
<w:p><w:r><w:t>投标响应文件自查样本</w:t></w:r></w:p>
<w:p><w:r><w:t>本项目承诺完全满足招标文件全部要求。</w:t></w:r></w:p>
<w:p><w:r><w:t>详见错误！未找到引用源。</w:t></w:r></w:p>
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
<w:p><w:del w:id="1" w:author="示例工程有限公司 编制组" w:date="2026-01-01T00:00:00Z">
  <w:r><w:delText xml:space="preserve">旧版本待删除内容</w:delText></w:r>
</w:del></w:p>
<w:p><w:r><w:rPr><w:vanish/></w:rPr><w:t>内部备注：此段隐藏文字不应出现在定稿中。</w:t></w:r></w:p>
<w:p><w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve">TOC \\o "1-3" \\h \\z \\u</w:instrText></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>
<w:tbl><w:tblGrid><w:gridCol w:w="4000"/><w:gridCol w:w="4000"/></w:tblGrid><w:tr><w:tc><w:p><w:r><w:t>序号</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>内容</w:t></w:r></w:p></w:tc></w:tr>
<w:tr><w:tc><w:p><w:r><w:t>1</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>实施方案待补充XXX</w:t></w:r></w:p></w:tc></w:tr></w:tbl>
<w:sectPr>
  <w:headerReference w:type="default" r:id="rIdH1"/>
  <w:pgSz w:w="11906" w:h="16838"/>
  <w:pgMar w:top="1440" w:right="1800" w:bottom="1440" w:left="1800"/>
</w:sectPr>
</w:body>
</w:document>"""


def main():
    out = "sample_bid.docx"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/header1.xml", HEADER)
        z.writestr("word/media/image1.png", PNG_BYTES)
        z.writestr("docProps/core.xml", CORE)
        z.writestr("docProps/app.xml", APP)
        z.writestr("word/document.xml", DOCUMENT)
    print("已生成自测样本：%s" % out)


if __name__ == "__main__":
    main()
