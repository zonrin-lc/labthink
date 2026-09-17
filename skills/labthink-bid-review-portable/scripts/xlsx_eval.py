#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评标办法 .xlsx 抽取（零依赖，仅标准库）

.xlsx 也是 zip 包：共享字符串在 xl/sharedStrings.xml，工作表在 xl/worksheets/sheetN.xml。
本模块按“工作表（按 workbook.xml 真实顺序）→ 行 → 单元格（按列引用定位）”抽取，
供 docx_review.py 生成“评分工作表”。

v1.1.0 变更（相对 v1.0.0）：
  * 按 xl/workbook.xml 的 <sheet> 顺序输出，不再按 sheetN.xml 字符串排序
    （旧版会把 sheet10 排到 sheet2 前面）
  * 跳过隐藏工作表（hidden / veryHidden）
  * 解析单元格列引用（r="C5"），空单元格不再导致列错位
  * 处理合并单元格：把左上角的值铺到合并区域内的空格
  * 输出结构化：{"sheet": 名, "rows": [{"row": 行号, "cells": [...]}]}

已知限制：日期格式单元格显示为 Excel 内部序列号（零依赖版不做日期格式换算）。
"""
import os
import re
import zipfile
import xml.etree.ElementTree as ET

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def _col_index(ref):
    """"C5" / "C" -> 2（0 基列号）。只取字母部分，兼容纯列号与“列+行”。"""
    m = re.match(r"([A-Z]+)", ref or "")
    if not m:
        return None
    s = m.group(1)
    n = 0
    for ch in s:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def _cell_value(c, shared):
    """取单元格值：共享字符串 / 内联字符串 / 布尔 / 数字。"""
    t = c.get("t")
    v = c.find(NS + "v")
    val = ""
    if v is not None and v.text is not None:
        if t == "s":
            try:
                val = shared[int(v.text)]
            except (ValueError, IndexError):
                val = v.text
        elif t == "b":
            val = "TRUE" if v.text == "1" else "FALSE"
        else:
            val = v.text
    is_el = c.find(NS + "is")
    if is_el is not None:
        val = "".join(tt.text or "" for tt in is_el.iter(NS + "t"))
    return val


def _read_shared_strings(z, names):
    if "xl/sharedStrings.xml" not in names:
        return []
    try:
        sroot = ET.fromstring(z.read("xl/sharedStrings.xml"))
    except ET.ParseError:
        return []
    return ["".join(t.text or "" for t in si.iter(NS + "t"))
            for si in sroot.iter(NS + "si")]


def _sheet_order(z, names):
    """按 workbook.xml 返回 [(名称, 部件路径, 是否隐藏)]；无法解析时回退数值排序。"""
    if "xl/workbook.xml" not in names:
        files = [n for n in names if re.match(r"xl/worksheets/sheet\d+\.xml$", n)]
        files.sort(key=lambda n: int(re.search(r"(\d+)", n).group(1)))
        return [(os.path.basename(f), f, False) for f in files]

    rels = {}
    if "xl/_rels/workbook.xml.rels" in names:
        try:
            rroot = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
            for rel in rroot:
                rels[rel.get("Id")] = rel.get("Target") or ""
        except ET.ParseError:
            pass

    order = []
    try:
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        sheets_el = wb.find(NS + "sheets")
        if sheets_el is None:
            return []
        for sh in sheets_el:
            rid = sh.get(R + "id")
            target = rels.get(rid, "")
            path = ("xl/" + target.lstrip("/")) if target else ""
            order.append((sh.get("name") or "", path,
                          (sh.get("state") or "visible") in ("hidden", "veryHidden")))
    except ET.ParseError:
        return []
    return order


def _read_sheet(z, path, shared):
    """读取单个工作表：行号 + 按列引用定位的单元格，处理合并单元格。"""
    sroot = ET.fromstring(z.read(path))

    # 合并区域列表：(c1, r1, c2, r2)，0 基列、1 基行
    merges = []
    for mc in sroot.iter(NS + "mergeCell"):
        ref = mc.get("ref") or ""
        m = re.match(r"([A-Z]+)(\d+):([A-Z]+)(\d+)", ref)
        if m:
            merges.append((_col_index(m.group(1)), int(m.group(2)),
                           _col_index(m.group(3)), int(m.group(4))))

    out = []
    rno = 0
    for row in sroot.iter(NS + "row"):
        rno = int(row.get("r") or (rno + 1))
        cells = {}
        max_col = -1
        for c in row.iter(NS + "c"):
            col = _col_index(c.get("r"))
            if col is None:
                col = len(cells)
            cells[col] = _cell_value(c, shared)
            max_col = max(max_col, col)

        rowcells = []
        for ci in range(max_col + 1):
            val = cells.get(ci, "")
            if val == "":
                for (c1, r1, c2, r2) in merges:
                    if r1 <= rno <= r2 and c1 <= ci <= c2:
                        val = cells.get(c1, "")
                        break
            rowcells.append(val)
        out.append({"row": rno, "cells": rowcells})
    return out


def extract_xlsx(path):
    """返回 [{"sheet": 名, "rows": [{"row": 行号, "cells": [...]}]}]。"""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        shared = _read_shared_strings(z, names)
        sheets = []
        for name, spath, hidden in _sheet_order(z, names):
            if hidden or not spath or spath not in names:
                continue
            try:
                sheets.append({"sheet": name, "rows": _read_sheet(z, spath, shared)})
            except (ET.ParseError, KeyError):
                continue
    return sheets


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法：python xlsx_eval.py <评标办法.xlsx>")
        raise SystemExit(1)
    for sh in extract_xlsx(sys.argv[1]):
        print("== 工作表：%s ==" % sh["sheet"])
        for r in sh["rows"]:
            print("第%d行 | " % r["row"] + " | ".join(str(c) for c in r["cells"] if str(c) != ""))
