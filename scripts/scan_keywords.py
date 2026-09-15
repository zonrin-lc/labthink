# -*- coding: utf-8 -*-
"""多格式关键词扫描：docx / pptx / pdf / xlsx。
用法：python3 scan_keywords.py --keys "关键词1,关键词2" --files <文件1> <文件2> ...
输出：每个文件的命中文本（含页码/工作表），用于从企业材料中快速定位事实。
命中后必须回到原文逐条核对，禁止仅凭扫描片段下结论。
"""
import sys, os, re, argparse

def iter_docx_text(path, out):
    import docx
    d = docx.Document(path)
    for i, p in enumerate(d.paragraphs):
        t = p.text.strip()
        if t:
            out.append(("P%d" % i, t))
    for ti, tb in enumerate(d.tables):
        for row in tb.rows:
            line = " | ".join(c.text.strip().replace("\n", " ") for c in row.cells)
            if line.strip():
                out.append(("T%d" % ti, line))

def iter_pptx_text(path, out):
    from pptx import Presentation
    prs = Presentation(path)
    def walk(shape, acc):
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                t = "".join(r.text for r in para.runs).strip()
                if t:
                    acc.append(t)
        if shape.shape_type == 6:
            for sub in shape.shapes:
                walk(sub, acc)
        if getattr(shape, "has_table", False) and shape.has_table:
            for row in shape.table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        acc.append("[T] " + cell.text.strip())
        if getattr(shape, "has_chart", False) and shape.has_chart:
            try:
                ch = shape.chart
                cats = list(ch.plots[0].categories)
                for s in ch.plots[0].series:
                    acc.append("[CHART] cats=%s series=%s" % (cats, list(s.values)))
            except Exception:
                pass
    for idx, slide in enumerate(prs.slides, 1):
        acc = []
        for shape in slide.shapes:
            walk(shape, acc)
        for t in acc:
            out.append(("P%d" % idx, t))

def iter_pdf_text(path, out):
    import fitz
    doc = fitz.open(path)
    for i, pg in enumerate(doc):
        for ln in pg.get_text().splitlines():
            if ln.strip():
                out.append(("P%d" % (i + 1), ln.strip()))
        for img in pg.get_images():
            out.append(("P%d" % (i + 1), "[IMAGE] xref=%s" % img[0]))
        for tab in pg.find_tables():
            for row in tab.extract():
                line = " | ".join(str(c) for c in row if c is not None)
                if line.strip():
                    out.append(("P%d" % (i + 1), line))

def iter_xlsx_text(path, out):
    from openpyxl import load_workbook
    wb = load_workbook(path, read_only=True, data_only=True)
    for ws in wb.worksheets:
        for row in ws.iter_rows(values_only=True):
            line = " | ".join(str(c) for c in row if c is not None)
            if line.strip():
                out.append(("[%s]" % ws.title, line[:300]))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keys", required=True, help="逗号分隔的关键词/正则片段")
    ap.add_argument("--files", nargs="+", required=True, help="待扫描文件路径")
    ap.add_argument("--regex", action="store_true", help="将 keys 视为正则表达式")
    args = ap.parse_args()
    if args.regex:
        pat = re.compile("|".join(args.keys.split(",")))
    else:
        pat = re.compile("|".join(re.escape(k) for k in args.keys.split(",")))
    for f in args.files:
        print("===== %s =====" % os.path.basename(f))
        ext = os.path.splitext(f)[1].lower()
        out = []
        try:
            if ext == ".docx":
                iter_docx_text(f, out)
            elif ext == ".pptx":
                iter_pptx_text(f, out)
            elif ext == ".pdf":
                iter_pdf_text(f, out)
            elif ext in (".xlsx", ".xlsm"):
                iter_xlsx_text(f, out)
            else:
                print("(unsupported type: %s)" % ext)
                continue
        except Exception as e:
            print("ERR: %s" % e)
            continue
        seen, hits = set(), 0
        for loc, text in out:
            if pat.search(text) and text not in seen:
                seen.add(text)
                print("[%s] %s" % (loc, text))
                hits += 1
        if not hits:
            print("(no hits)")

if __name__ == "__main__":
    main()
