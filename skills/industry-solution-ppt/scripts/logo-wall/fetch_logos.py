#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_logos.py — Pass 1: bulk-fetch company logos from official homepages (no browser).

Input:  a CSV file with columns:  name,url1,url2,url3   (extra url columns optional)
        Example row:  国药集团,https://www.sinopharm.com,http://www.sinopharm.com
Output: <outdir>/<name>.<ext>  +  <outdir>/_results.json

Usage:  python fetch_logos.py companies.csv --outdir logos_raw
"""
import os, re, sys, csv, json, argparse, warnings
from urllib.parse import urljoin, urlparse

warnings.filterwarnings("ignore")
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("pip install requests beautifulsoup4 lxml")

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


def score_candidate(tag, src):
    """Heuristic score: higher = more likely the real header logo."""
    s = 0
    text = " ".join([src or "", tag.get("alt") or "",
                     " ".join(tag.get("class") or []), tag.get("id") or "",
                     tag.get("title") or ""]).lower()
    if "logo" in text: s += 10
    if "header" in text or "head" in text: s += 2
    if "footer" in text: s -= 5
    if "icon" in text: s -= 3
    if re.search(r"\.(png|svg)(\?|$)", src or "", re.I): s += 2
    if any(w in text for w in ("banner", "slide", "qrcode", "wx", "ewm")): s -= 8
    p = tag.parent
    for _ in range(4):
        if p is None: break
        cls = (" ".join(p.get("class") or []) + " " + (p.get("id") or "")).lower()
        if "footer" in cls: s -= 5
        if any(w in cls for w in ("header", "top", "nav")): s += 2
        p = p.parent
    return s


def fetch_company(name, urls, outdir):
    for base in urls:
        base = base.strip()
        if not base: continue
        try:
            r = requests.get(base, headers=UA, timeout=15, verify=False)
            if r.status_code != 200: continue
            r.encoding = r.apparent_encoding or "utf-8"
            soup = BeautifulSoup(r.text, "lxml")
        except Exception:
            continue
        cands = []
        for img in soup.find_all("img"):
            src = (img.get("src") or img.get("data-src") or
                   img.get("data-original") or img.get("lay-src"))
            if not src: continue
            full = urljoin(r.url, src)
            cands.append((score_candidate(img, full), full))
        cands.sort(key=lambda x: -x[0])
        for sc, full in cands[:6]:
            if sc < 5 and len(cands) > 1: continue
            try:
                rr = requests.get(full, headers={**UA, "Referer": r.url},
                                  timeout=15, verify=False)
                ct = rr.headers.get("Content-Type", "")
                ok_type = ("image" in ct or full.lower().endswith(
                    (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")))
                if rr.status_code == 200 and len(rr.content) > 300 and ok_type:
                    ext = ".svg" if ("svg" in ct or full.lower().endswith(".svg")) \
                          else os.path.splitext(urlparse(full).path)[1] or ".png"
                    if ext.lower() not in (".png", ".jpg", ".jpeg", ".gif",
                                           ".svg", ".webp", ".bmp"):
                        ext = ".png"
                    fn = os.path.join(outdir, name + ext.lower())
                    with open(fn, "wb") as f:
                        f.write(rr.content)
                    return {"name": name, "file": fn, "src": full, "site": r.url}
            except Exception:
                continue
    return {"name": name, "file": None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--outdir", default="logos_raw")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    results = []
    with open(args.csv, encoding="utf-8-sig") as f:
        for row in csv.reader(f):
            if not row or not row[0].strip(): continue
            name, urls = row[0].strip(), row[1:]
            res = fetch_company(name, urls, args.outdir)
            results.append(res)
            print(("OK   " if res["file"] else "FAIL ") + name +
                  (" -> " + res.get("src", "") if res["file"] else ""), flush=True)

    with open(os.path.join(args.outdir, "_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    ok = sum(1 for r in results if r["file"])
    print(f"\npass1: {ok}/{len(results)} succeeded. Run browser_fetch.py for the rest.")


if __name__ == "__main__":
    main()
