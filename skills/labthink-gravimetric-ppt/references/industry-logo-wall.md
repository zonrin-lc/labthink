# 49 家合作客户 Logo 墙（已融合 logo-wall 流程）

客户墙页是 PPT 第二幕固定页：标题"XX行业服务客户——1000+制药企业的共同选择"（其他行业把"制药"换成对应行业，如"食品企业"）。**数量必须 49 家**，严格按名单顺序。

## 0. 医药行业（默认，直接出图，无需重新抓取）

本 skill 已内置一套 QA 通过的 49 家医药客户资产：

```
assets/logo-wall/
├── logos/01_国药集团.png … 49_贵州百灵.png   # 49 张白底/透明底彩色 Logo
├── order.txt        # 49 家名单顺序（一行一个文件名前缀）
├── logo-index.xlsx  # 名称→文件→来源→备注
└── template.pptx    # 用户版式模板（标题"医药行业服务客户——1000+制药企业的共同选择"，49 个 1.36"×0.52" 圆角格）
```

一键重建客户墙页：
```bash
cd <项目目录>
python <skill>/scripts/logo-wall/normalize_logos.py \
    "<skill>/assets/logo-wall/logos" --outdir logos_fit --maxw 1200 --maxh 400
python <skill>/scripts/logo-wall/refill_template.py \
    "<skill>/assets/logo-wall/template.pptx" logos_fit \
    "<skill>/assets/logo-wall/order.txt" 客户Logo墙.pptx
# 然后渲染/打开 客户Logo墙.pptx 逐格目检
```

> 把 `<skill>` 替换为本 skill 根目录绝对路径。`refill_template.py` 只换图片、保留模板标题与格子样式；格数 ≠ Logo 数会自动中止。

## 1. 换行业/换名单时（非默认 49 家医药）

需要新客户名单时，按 logo-wall 全流程重跑（脚本都在 `scripts/logo-wall/`）：

1. **备名单**：一行一家 `名称,官网1,官网2,...`。先核对法定名称与域名（常见坑：仲景皖西→仲景宛西、科伦制药→科伦药业；chinahuadong.com 是神州数码不是中美华东）。
2. **批量抓取**：`python scripts/logo-wall/fetch_logos.py companies.csv --outdir logos_raw`（约成功 50–70%）。
3. **浏览器补抓**：`pip install playwright && python -m playwright install chromium`，再 `python scripts/logo-wall/browser_fetch.py remaining.csv --outdir logos_raw`（`--click 全拒绝` 关 Cookie 弹层；`--fetch-img images/logo.png` 绕防盗链）。
4. **SVG→PNG**：`python scripts/logo-wall/svg_to_png.py logos_raw`。
5. **视觉 QA**：`python scripts/logo-wall/make_sheet.py logos_raw sheet.png`，打开整表逐张核对（不可见白标/错公司/深色块白标/裁切/模糊/标语杂线）。
6. **归一化**：`python scripts/logo-wall/normalize_logos.py logos_raw --outdir logos_fit --maxw 1200 --maxh 400 [--adjust adjust.csv]`（裁白边、重着色、fit-inside）。
7. **建页**：有模板走 `refill_template.py`（首选，保标题与格子不变）；无模板走 `build_logo_wall.py logos_fit order.txt out.pptx --title "..." --cols 7`。

## 2. 五条金规则（不可破）

1. **不改顺序**：墙上顺序严格等于用户名单顺序，不按颜色/大小/重要性重排。
2. **统一格子不统一 Logo 尺寸**：每个 Logo 保持原始纵横比、fit-inside 统一格框、格内居中；绝不拉伸成同宽同高。
3. **白底/透明底彩色版**：首选透明底彩色 PNG；"深色块+白标"是最大视觉噪声，禁止——把白稿重着色为品牌色导透明 PNG。白格配白底彩色版亦可。
4. **数量=名单数，不凑整**：名单 49 家就出 49 个，宁可格子不方正，不发明/删公司凑整数。
5. **必做视觉 QA**：建 contact sheet 逐张看，再交付。

## 3. 设计参数

- 格子 1.36"×0.52"，内边距约 0.06"；Logo 实际宽 ≤1.25"、高 ≤0.42"，双阈值先碰先缩。
- 方形/圆形实心标再缩 10–15%；细线条/长英文标可放大 5–10%。
- 行距≈列距，且明显大于 Logo 与格边距；整墙页边距对称。
- 同物理高度、≥250dpi；优先 SVG 或 2x/3x。
- 完整设计原则见 `references/logo-wall/design-principles.md`；逐症状排障见 `references/logo-wall/troubleshooting.md`。

## 4. 已踩过的实体映射（医药 49 家）

- 科伦 = 科伦药业 KELUN，不是科伦集团。
- 中美华东用母品牌 华东医药 Huadong Medicine。
- 仲景宛西（不是"皖西"）。
- 第 49 席原为海思科制药，用户已移除，名单保持 49 家。
