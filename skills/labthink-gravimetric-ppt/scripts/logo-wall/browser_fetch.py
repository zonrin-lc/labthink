#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
browser_fetch.py — Pass 2: headless-browser logo capture for sites that resist plain HTTP
(JS-rendered pages, cookie overlays, CSS-background logos, WAF blocks).

Requires:  pip install playwright && python -m playwright install chromium

Input:  same CSV as fetch_logos.py (name,url1,url2,...).
Modes per company, tried in order:
  1. element   — screenshot the best logo element (transparent PNG, omit_background)
  2. strip     — screenshot the full top strip (<outdir>/candidates/<name>_strip.png)
                 so a human/agent can crop precisely afterwards.
Options:
  --click "全拒绝"     click a cookie-consent button (by visible text) before capture
  --fetch-img logo.png download an <img> whose src contains this substring, via in-page
                       fetch (bypasses hot-link WAF that blocks plain requests)

Usage:  python browser_fetch.py remaining.csv --outdir logos_raw [--click 全拒绝]
"""
import os, sys, csv, argparse, base64

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("pip install playwright && python -m playwright install chromium")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "Chrome/124.0 Safari/537.36")

FIND_JS = """
() => {
  const out = [];
  const push = (el, kind, url) => {
    const r = el.getBoundingClientRect();
    if (r.width < 50 || r.height < 12 || r.width > 1200 || r.height > 300) return;
    if (r.top > 500 || r.bottom < 0) return;
    const meta = ((url||'') + ' ' + (el.alt||'') + ' ' +
        (typeof el.className==='string'?el.className:'') + ' ' + (el.id||'')).toLowerCase();
    let s = 0;
    if (meta.includes('logo')) s += 10;
    if (meta.match(/banner|qrcode|\\bwx\\b|search|ewm/)) s -= 9;
    if (meta.match(/menu|nav|arrow|icon/)) s -= 4;
    if (el.tagName === 'SVG') s += 2;
    if (r.width > r.height * 1.4) s += 3;   // horizontal preference
    if (r.top < 250) s += 2;
    out.push({s, x:r.x, y:r.y, w:r.width, h:r.height, kind, url:(url||'').slice(0,180)});
  };
  document.querySelectorAll('img').forEach(el => push(el, 'img', el.currentSrc || el.src));
  document.querySelectorAll('svg').forEach(el => push(el, 'svg', ''));
  document.querySelectorAll('*').forEach(el => {
    const bg = getComputedStyle(el).backgroundImage;
    if (bg && bg !== 'none') {
      const m = bg.match(/url\\(["']?(.*?)["']?\\)/);
      if (m) push(el, 'bg', m[1]);
    }
  });
  out.sort((a,b) => b.s - a.s || (a.w*a.h) - (b.w*b.h));
  return out.slice(0, 8);
}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--outdir", default="logos_raw")
    ap.add_argument("--click", default=None, help="cookie-consent button text")
    ap.add_argument("--fetch-img", default=None,
                    help="substring of an <img> src to download via in-page fetch")
    args = ap.parse_args()
    cand = os.path.join(args.outdir, "candidates")
    os.makedirs(cand, exist_ok=True)

    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1600, "height": 1000},
                            device_scale_factor=3, ignore_https_errors=True,
                            user_agent=UA)
        with open(args.csv, encoding="utf-8-sig") as f:
            for row in csv.reader(f):
                if not row or not row[0].strip(): continue
                name, urls = row[0].strip(), [u.strip() for u in row[1:] if u.strip()]
                done = False
                for url in urls:
                    if done: break
                    pg = ctx.new_page()
                    try:
                        pg.goto(url, timeout=40000, wait_until="domcontentloaded")
                        pg.wait_for_timeout(4000)
                        if args.click:
                            try:
                                pg.click(f"text={args.click}", timeout=5000)
                                pg.wait_for_timeout(1500)
                            except Exception:
                                pass
                        if args.fetch_img:
                            data = pg.evaluate("""
                              async (sub) => {
                                const el = Array.from(document.querySelectorAll('img'))
                                  .find(i => (i.src||'').includes(sub));
                                if (!el) return null;
                                const r = await fetch(el.src, {credentials:'include'});
                                const bytes = new Uint8Array(await r.arrayBuffer());
                                let s=''; for (let i=0;i<bytes.length;i++) s+=String.fromCharCode(bytes[i]);
                                return btoa(s);
                              }""", args.fetch_img)
                            if data:
                                fn = os.path.join(args.outdir, name + ".png")
                                open(fn, "wb").write(base64.b64decode(data))
                                print(f"OK   {name} (fetch-img {args.fetch_img})", flush=True)
                                done = True
                                continue
                        cands = pg.evaluate(FIND_JS)
                        for c in cands:
                            if c["s"] < 10 and len(cands) > 1: continue
                            clip = {"x": max(c["x"]-6, 0), "y": max(c["y"]-6, 0),
                                    "width": min(c["w"]+12, 1600), "height": c["h"]+12}
                            fn = os.path.join(args.outdir, name + ".png")
                            pg.screenshot(path=fn, clip=clip, omit_background=True)
                            if os.path.getsize(fn) > 800:
                                print(f"OK   {name} <- {url} "
                                      f"({c['w']:.0f}x{c['h']:.0f})", flush=True)
                                done = True
                                break
                        if not done:
                            fn = os.path.join(cand, f"{name}_strip.png")
                            pg.screenshot(path=fn, omit_background=True,
                                          clip={"x": 0, "y": 0,
                                                "width": 1400, "height": 170})
                            print(f"STRIP {name} (crop manually: {fn})", flush=True)
                            done = True
                    except Exception as e:
                        print(f"ERR  {name} {url}: {type(e).__name__}", flush=True)
                    finally:
                        pg.close()
                if not done:
                    print(f"FAIL {name}", flush=True)
        b.close()


if __name__ == "__main__":
    main()
