#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
normalize_logos.py — Make heterogeneous logos visually uniform:

  1. trim    — cut away transparent / near-white margins
  2. recolor — optional: recolor (near-)white artwork to a brand color
               (for white-on-transparent logos that are invisible on white slides)
  3. fit     — scale into a max box (fit-inside, keep aspect ratio)
  4. weight  — optional visual-weight adjustment per file
               (square/solid marks smaller, thin/light marks larger)

Input:  directory of .png files (logos), plus an optional adjustment CSV:
            filename,action,value
            拜耳.png,weight,0.85          # shrink to 85%
            强生.png,recolor,"213,25,0"   # J&J red
Usage:  python normalize_logos.py logos_raw --outdir logos_fit \
            --maxw 1200 --maxh 400 [--adjust adjust.csv]
Output PNGs keep transparency and original aspect ratio.
"""
import os, sys, csv, glob, argparse
from PIL import Image

WHITE_T = 235   # near-white threshold for trimming / recoloring


def trim(im, bg_white=True):
    """Crop to non-transparent (and optionally non-white) bounding box."""
    rgba = im.convert("RGBA")
    px = rgba.load()
    xs, ys = [], []
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = px[x, y]
            if a <= 8: continue
            if bg_white and r > WHITE_T and g > WHITE_T and b > WHITE_T: continue
            xs.append(x); ys.append(y)
    if not xs: return rgba
    return rgba.crop((min(xs), min(ys), max(xs) + 1, max(ys) + 1))


def recolor_white(im, color):
    rgba = im.convert("RGBA")
    px = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = px[x, y]
            if a > 0 and r > 200 and g > 200 and b > 200:
                px[x, y] = (color[0], color[1], color[2], a)
    return rgba


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("indir")
    ap.add_argument("--outdir", default="logos_fit")
    ap.add_argument("--maxw", type=int, default=1200, help="max width px")
    ap.add_argument("--maxh", type=int, default=400, help="max height px")
    ap.add_argument("--keep-white", action="store_true",
                    help="trim transparency only, keep white margins")
    ap.add_argument("--adjust", default=None, help="CSV: filename,action,value")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    adj = {}
    if args.adjust:
        with open(args.adjust, encoding="utf-8-sig") as f:
            for row in csv.reader(f):
                if len(row) >= 3:
                    adj.setdefault(row[0].strip(), []).append((row[1].strip(),
                                                               row[2].strip()))

    for f in sorted(glob.glob(os.path.join(args.indir, "*.png"))):
        base = os.path.basename(f)
        im = Image.open(f).convert("RGBA")
        for action, value in adj.get(base, []):
            if action == "recolor":
                im = recolor_white(im, tuple(int(v) for v in value.split(",")))
        im = trim(im, bg_white=not args.keep_white)
        scale = min(args.maxw / im.width, args.maxh / im.height, 1.0)
        for action, value in adj.get(base, []):
            if action == "weight":
                scale *= float(value)
        if scale < 1.0:
            im = im.resize((max(1, round(im.width * scale)),
                            max(1, round(im.height * scale))), Image.LANCZOS)
        im.save(os.path.join(args.outdir, base))
        print(f"{base}: {im.width}x{im.height}", flush=True)


if __name__ == "__main__":
    main()
