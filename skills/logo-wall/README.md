# Logo Wall Skill — 企业 Logo 搜集与 PPT 客户墙排版

**这是什么**：一个跨平台可用的 Skill 包，把"给一批公司名单 → 搜集官方 Logo → 排版成整齐的 PPT 客户墙"全流程固化成了方法论 + 脚本 + 现成素材。在任何支持读取文件的 AI 平台（Kimi、Claude、ChatGPT、Copilot 等）上，把本包解压后交给 AI，让它先读 `SKILL.md` 即可开工。

## 包结构

```
logo-wall/
├── SKILL.md                  ← 入口：完整工作流（Phase 0-6）与五条金律，AI 先读这个
├── scripts/                  ← 7 个平台无关的 Python 脚本
│   ├── fetch_logos.py        ← 批量从官网抓 Logo（无需浏览器）
│   ├── browser_fetch.py      ← 无头 Chromium 补抓（JS 渲染/防爬站点）
│   ├── svg_to_png.py         ← SVG 渲染成 PNG（无需 cairo）
│   ├── make_sheet.py         ← 拼目检联系表（视觉 QA 必做）
│   ├── normalize_logos.py    ← 裁白边/重着色/统一外接框
│   ├── build_logo_wall.py    ← 从零生成 16:9 Logo 墙 PPT
│   └── refill_template.py    ← 在用户自己的 PPT 模板里原位换 Logo（优先用）
├── references/
│   ├── design-principles.md  ← 排版协调的 8 条设计要点
│   └── troubleshooting.md    ← 实战踩坑与对症处理表
└── assets/                   ← 医药行业 49 家完整参考案例（已 QA 通过）
    ├── template.pptx         ← 16:9 模板：标题 + 49 个 1.36″×0.52″ 统一格子
    ├── logos/01–49           ← 49 个白底/透明底彩色 Logo，按名单顺序编号
    ├── order.txt             ← 排列顺序文件（与名单一一对应）
    └── logo-index.xlsx       ← 企业名 → 文件 → 来源 → 备注 索引
```

## 五条金律（不可跳过）

1. **顺序绝不重排**——严格按用户给的名单顺序。
2. **统一的是格子，不是 Logo**——fit-inside 约束外接框，保持纵横比，格内居中。
3. **白底/透明底彩色版**——"深色底+白标"一律不用；白色图稿按品牌色重着色。
4. **数量=名单数**——49 家就放 49 个，不凑整、不增减。
5. **必须视觉 QA**——交付前拼联系表逐个人眼核对。

## 快速开始

**场景 A：直接用现成案例重建这页 PPT**

```bash
pip install pillow python-pptx
python scripts/normalize_logos.py assets/logos --outdir logos_fit --maxw 1200 --maxh 400
python scripts/refill_template.py assets/template.pptx logos_fit assets/order.txt 客户Logo墙.pptx
```

**场景 B：换一批新公司（全流程）**

1. 准备 `companies.csv`（每行：公司名,官网1,官网2…）；
2. 依次运行 `fetch_logos.py` →（失败者）`browser_fetch.py` → `svg_to_png.py`；
3. `make_sheet.py` 拼图，逐个人眼检查，按 `references/troubleshooting.md` 修；
4. `normalize_logos.py` 归一化；
5. 有模板用 `refill_template.py`，没有模板用 `build_logo_wall.py`；
6. 交付前再过一次目检。

## 依赖

`requests beautifulsoup4 lxml pillow python-pptx`；仅抓取困难站点时需要 `playwright` + Chromium。脚本全部为平台无关 Python（Windows / macOS / Linux 均可），示例路径均为当前工作目录相对路径。
