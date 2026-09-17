#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
svg_to_png.py — Render every .svg in a directory to a transparent PNG (3x) via headless
Chromium. Avoids the libcairo dependency that breaks cairosvg on Windows.

Requires:  pip install playwright && python -m playwright install chromium

Usage:  python svg_to_png.py logos_raw [--scale 3]
"""
import os, sys, glob, argparse

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("pip install playwright && python -m playwright install chromium")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("indir")
    ap.add_argument("--scale", type=int, default=3)
    args = ap.parse_args()

    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1600, "height": 1000},
                            device_scale_factor=args.scale)
        for svg in glob.glob(os.path.join(args.indir, "*.svg")):
            name = os.path.splitext(os.path.basename(svg))[0]
            out = os.path.join(args.indir, name + ".png")
            pg = ctx.new_page()
            try:
                pg.goto("file:///" + os.path.abspath(svg).replace("\\", "/"),
                        timeout=15000)
                pg.wait_for_timeout(800)
                pg.locator("svg").first.screenshot(path=out, omit_background=True)
                print(f"OK   {name} ({os.path.getsize(out)}B)", flush=True)
            except Exception as e:
                print(f"FAIL {name}: {type(e).__name__}", flush=True)
            finally:
                pg.close()
        b.close()


if __name__ == "__main__":
    main()
