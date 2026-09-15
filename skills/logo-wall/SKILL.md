---
name: logo-wall
description: Collect official company logos (horizontal, white/transparent background) from the web and lay them out as a uniform client/partner logo wall in PowerPoint. Use when the user provides a list of company names (typically ~49) and asks to (1) gather/download/搜集 their logos for a PPT, website, or poster, (2) build a 客户墙/Logo 墙/client logo slide with consistent size and alignment, or (3) normalize an existing folder of logos that look inconsistent. Covers homepage scraping, headless-browser capture, SVG rendering, white-logo recoloring to brand colors, whitespace trimming, fit-inside scaling, grid PPT generation, and refilling the user's own PPT template. Ships with a QA-passed 49-company 医药行业 reference set (template + curated logos + order file).
---

# Logo Wall — 企业 Logo 搜集与 PPT 客户墙排版

End-to-end workflow: company name list → official logos → uniform grid slide.

**Golden rules (never skip):**

1. **Never reorder.** Logo order in the final deck must exactly match the user's list, first to last. Do not sort by color, size, or importance unless the user explicitly asks.
2. **Uniform cells, not uniform logos.** Constrain each logo's bounding box (fit-inside), preserve its aspect ratio. Never stretch logos to identical width/height.
3. **White or transparent background, colored artwork.** Prefer the white/transparent-background color version of every logo. The "dark block + white mark" style (navy/gray/red block with a white logo) is the biggest source of visual noise on the wall — never ship it: recolor the white artwork to the brand color on a transparent background instead. White background is acceptable when the slide cells are white; transparent PNG is always best.
4. **Count = the list, no padding.** Ship exactly as many logos as the user's list contains (e.g. 49), even if the grid is not a perfect rectangle. Never invent or drop companies to reach a round number.
5. **Always do visual QA.** Build a contact sheet and LOOK at it before delivering. Automated fetches regularly return white-on-transparent (invisible) logos, wrong companies, clipped marks, or decorative lines.

## Workflow

### Phase 0 — Prepare the company list

- One row per company: `name,official_url1,official_url2,...` (CSV, e.g. `companies.csv`).
- Verify official domains with web search when unsure. Two classic traps:
  - **Wrong-name trap**: user lists may contain typos/variants (e.g. 仲景皖西 → correct is 仲景宛西; 科伦制药 → 科伦药业). Map every name to the exact legal entity before fetching.
  - **Wrong-domain trap**: similar domains may belong to a different company entirely (e.g. chinahuadong.com is 神州数码, NOT 中美华东). After fetching, confirm the logo actually shows the requested company.
- Some companies have no independent site (subsidiaries); use the parent group's brand logo and note it (e.g. 杭州中美华东 → 华东医药).

### Phase 1 — Bulk fetch (no browser)

```bash
python scripts/fetch_logos.py companies.csv --outdir logos_raw
```

Typically succeeds for ~50–70% of companies. Failures are usually JS-rendered sites, WAF blocks, or wrong domains — fix domains first, then Phase 2.

### Phase 2 — Browser capture (headless Chromium)

```bash
pip install playwright && python -m playwright install chromium
python scripts/browser_fetch.py remaining.csv --outdir logos_raw
# options: --click 全拒绝   (dismiss cookie overlay)
#          --fetch-img images/logo.png   (in-page fetch, bypasses hot-link WAF)
```

Element screenshots produce transparent PNGs at 3x. Companies that only yield a `*_strip.png` (top-of-page strip) need a manual crop — read the strip, crop to the logo with PIL, and discard parent-group marks when the user asked for the subsidiary (e.g. crop 华鲁集团 out of 新华制药's header).

If the official site is down, fall back to a high-res logo image from an encyclopedia page (Baidu Baike etc.) and note the substitution.

### Phase 3 — SVG → PNG

```bash
python scripts/svg_to_png.py logos_raw
```

### Phase 4 — Visual QA + fixes

```bash
python scripts/make_sheet.py logos_raw sheet.png
```

Open the sheet and check EVERY logo against this list:

- **Invisible (white on transparent)** → recolor to brand color (see `recolor` in Phase 5, or rewrite `fill="#FFFFFF"` in the SVG before rendering). Common victims: footer/header white versions.
- **Wrong company** → wrong domain; refetch (Phase 0 trap).
- **Dark/colored background block with white artwork** → this is the style to avoid. Get the color-on-white version instead (check the site's footer, press kit, or an existing deck from the user); otherwise recolor the white artwork to the brand color and export a transparent PNG. A plain *white* background block is fine when the slide cells are white.
- **Clipped mark** → re-crop with a wider strip.
- **Tiny/blurry** → re-capture at device_scale_factor=3, or fetch the `@2x` asset.
- **Slogan/badge clutter** (CCTV badges, 股票代码, phone numbers) → crop them off.
- Square/vertical official marks (rare) → keep as-is; fit-inside handles them.

### Phase 5 — Normalize

```bash
python scripts/normalize_logos.py logos_raw --outdir logos_fit --maxw 1200 --maxh 400 \
    --adjust adjust.csv        # optional: filename,recolor,"213,25,0" / weight,0.85
```

Trims whitespace, applies recolors, scales every logo into the same max box.
Apply `weight` tweaks for visual balance: square/solid marks 0.85–0.9, thin/light or long-English marks 1.0 (they are already capped by the box).

### Phase 6 — Build the slide

Two modes; prefer **Mode A** whenever the user provides their own template deck.

**Mode A — Refill the user's template (preferred).** Keeps the user's title, cell shapes and decorations pixel-identical; only the logo pictures are swapped in:

```bash
python scripts/refill_template.py template.pptx logos_fit order.txt out.pptx \
    --cellw 1.36 --cellh 0.52 --pad 0.06
```

It deletes every existing picture (including inside groups), locates the uniform cell AUTO_SHAPEs by size, sorts them row-major, and inserts logos fit-inside and centered. It saves to a NEW file — never overwrite the user's template. It aborts if cell count ≠ logo count.

**Mode B — Build from scratch** (no template given):

```bash
python scripts/build_logo_wall.py logos_fit order.txt out.pptx \
    --title "..." --cols 7 --cellw 1.36 --cellh 0.52
```

`order.txt` = user's company order, one filename prefix per line. Then render/inspect the deck (or rebuild the contact sheet from `logos_fit`) before delivering.

Deliver: `logos_fit/` (white/transparent PNGs, numbered), an index file (name → file → source → notes), the .pptx, and a QA contact sheet.

## Bundled assets (医药行业案例 · 49 家)

The `assets/` folder ships a complete, QA-passed reference case:

- `assets/template.pptx` — the user's styled 16:9 template (title "医药行业服务客户——1000+制药企业的共同选择", 49 uniform 1.36″×0.52″ snip-corner cells).
- `assets/logos/01_…png … 49_…png` — the 49 curated white/transparent-background logos, numbered in the user's list order.
- `assets/order.txt` — the exact order file matching those 49 names.
- `assets/logo-index.xlsx` — name → file → source → notes index.

One-command rebuild of the whole case (after `normalize_logos.py` into `logos_fit`):

```bash
python scripts/normalize_logos.py assets/logos --outdir logos_fit --maxw 1200 --maxh 400
python scripts/refill_template.py assets/template.pptx logos_fit assets/order.txt 客户Logo墙.pptx
```

Entity-mapping notes learned the hard way for this list: 科伦 is 科伦药业 (KELUN), not 科伦集团; 中美华东 uses the parent brand 华东医药 (Huadong Medicine); 仲景宛西 (not 皖西); the 49th slot originally held 海思科制药, which the user removed — the list stays at 49.

## Design principles & troubleshooting

- Read `references/design-principles.md` for the full logo-wall design rules (share with the user when they ask "怎么排版才协调").
- Read `references/troubleshooting.md` for per-symptom fixes collected from real runs (cookie overlays, WAF 403s, mask-based SVGs rendering blank, etc.).

## Dependencies

`requests beautifulsoup4 lxml pillow python-pptx` (+ `playwright` with Chromium for Phases 2–3). Install only what the current phase needs. All scripts are platform-agnostic Python; paths in examples use the current working directory.
