#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_sheet.py — Tile a folder of images into labeled contact sheets for visual QA.
ALWAYS inspect the sheet before shipping: catch white-on-transparent logos, wrong
companies, clipped or blurred artwork.

Usage:  python make_sheet.py <folder> <out.png> [--cols 5] [--per 25]
        (writes <out.png>, plus <out>_2.png etc. when more than --per images)
"""
import os, sys, glob, argparse
from PIL import Image, ImageDraw, ImageFont


def load_font(size):
    for cand in ("C:/Windows/Fonts/msyh.ttc",          # Windows CJK
                 "/System/Library/Fonts/PingFang.ttc", # macOS CJK
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(cand, size)
        except Exception:
            continue
    return ImageFont.load_default()


def sheet(files, out, cols, cell, label_h):
    rows = (len(files) + cols - 1) // cols
    W, H = cols * cell[0], rows * (cell[1] + label_h)
    canvas = Image.new("RGB", (W, H), (245, 246, 248))
    d = ImageDraw.Draw(canvas)
    font = load_font(18)
    for i, f in enumerate(files):
        r, c = divmod(i, cols)
        x0, y0 = c * cell[0], r * (cell[1] + label_h)
        d.rectangle([x0, y0, x0 + cell[0] - 2, y0 + cell[1] + label_h - 2],
                    fill="white", outline=(210, 210, 210))
        try:
            im = Image.open(f).convert("RGBA")
            bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
            im = Image.alpha_composite(bg, im).convert("RGB")
            im.thumbnail((cell[0] - 24, cell[1] - 24))
            canvas.paste(im, (x0 + (cell[0] - im.width) // 2,
                              y0 + (cell[1] - im.height) // 2))
        except Exception:
            d.text((x0 + 8, y0 + 40), "[unreadable]", fill="red", font=font)
        d.text((x0 + 8, y0 + cell[1] + 4), os.path.basename(f)[:46],
               fill="black", font=font)
    canvas.save(out)
    print("saved", out, len(files), "imgs")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("out")
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--per", type=int, default=25)
    args = ap.parse_args()
    files = sorted(f for f in
                   glob.glob(os.path.join(args.folder, "*.png")) +
                   glob.glob(os.path.join(args.folder, "*.jpg")) +
                   glob.glob(os.path.join(args.folder, "*.jpeg")) +
                   glob.glob(os.path.join(args.folder, "*.webp"))
                   if "_sheet" not in f and "_verify" not in f)
    for page in range(0, max(1, (len(files) + args.per - 1) // args.per)):
        chunk = files[page * args.per:(page + 1) * args.per]
        if not chunk: break
        out = args.out if page == 0 else args.out.replace(".png", f"_{page+1}.png")
        sheet(chunk, out, args.cols, (420, 170), 30)


if __name__ == "__main__":
    main()
