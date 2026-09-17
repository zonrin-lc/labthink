---
name: labthink-logo-wall
description: 企业Logo搜集与PPT客户墙排版工具。用户提供49家企业名称后，自动从官网抓取logo、标准化处理、生成统一规格的PPT客户墙。适用于"帮我做一份XX行业49家企业的logo墙"、"这是客户名单，帮我抓取logo并排版成客户墙"等场景。
---

# Logo Wall — 企业 Logo 搜集与 PPT 客户墙排版

## ⚠️ 开工前必须确认

**用户必须先提供49家企业名称**，否则不开始制作。

向用户索要：
```
请提供49家企业的完整名单（企业全称），我会按顺序抓取logo并生成客户墙PPT。
格式示例：
1. 雀巢（Nestlé）
2. 百事公司（PepsiCo）
...
49. 思念食品
```

收到名单后，整理成CSV格式：`企业名称,官网URL`（官网URL可后续补充或自动搜索）。

## 黄金法则（不可违反）

1. **严格按用户名单顺序排列**，不按颜色、大小、重要性重排。
2. **统一单元格，不统一logo尺寸**：每个logo放入相同大小的单元格（fit-inside），保持原始宽高比，禁止拉伸。
3. **白底或透明底，彩色logo**：优先使用白底/透明底的彩色版本。"深色底块+白标"一律不用，改为重着色为品牌色。
4. **数量=名单数量**：用户给49家就输出49个，不凑整、不删减。
5. **必须做视觉QA**：生成拼图逐张检查，自动化抓取经常返回错公司、不可见白标、裁切不全。

## 工作流程

### 第1步：准备企业名单

- 用户提供49家企业名称
- 搜索并补充每家企业的官网URL
- 保存为 `companies.csv`：`name,official_url`
- 核实企业名称准确性（避免错别字、简称混用）

### 第2步：批量抓取logo（无浏览器模式）

```bash
python scripts/fetch_logos.py companies.csv --outdir logos_raw
```

通常成功率50-70%，失败的进入第3步。

### 第3步：浏览器抓取补充（Playwright）

```bash
pip install playwright && python -m playwright install chromium
python scripts/browser_fetch.py remaining.csv --outdir logos_raw
```

### 第4步：SVG转PNG

```bash
python scripts/svg_to_png.py logos_raw
```

### 第5步：视觉QA

```bash
python scripts/make_sheet.py logos_raw sheet.png
```

打开拼图逐张检查：
- 不可见（白底白标）→ 重着色为品牌色
- 错公司 → 重新抓取
- 深色底块+白标 → 获取彩色版本或重着色
- 裁切不全 → 重新裁切
- 模糊 → 重新抓取高清版

### 第6步：标准化

```bash
python scripts/normalize_logos.py logos_raw --outdir logos_fit --maxw 1200 --maxh 400
```

裁白边、统一尺寸、居中。

### 第7步：生成客户墙PPT

**方式A：使用内置模板（推荐）**

```bash
python scripts/refill_template.py assets/template.pptx logos_fit assets/order.txt 客户Logo墙.pptx \
    --cellw 1.6 --cellh 0.65 --pad 0.1
```

**方式B：从零构建**

```bash
python scripts/build_logo_wall.py logos_fit order.txt 客户Logo墙.pptx \
    --title "合作客户——49家行业领先企业的共同选择" --cols 7 --cellw 1.6 --cellh 0.65
```

### 第8步：交付

交付物：
- `客户Logo墙.pptx`（最终PPT）
- `logos_fit/`（标准化后的logo图片）
- `sheet.png`（QA拼图，供用户核对）
- `logo-index.csv`（企业名→文件名→来源→备注）

## 内置示例资产

`assets/` 目录包含完整示例（使用假logo占位，非真实企业）：

- `assets/template.pptx` — 16:9客户墙模板（标题+49单元格，7x7布局）
- `assets/logos/01_示例企业1.png … 49_示例企业49.png` — 49个示例占位logo
- `assets/order.txt` — 示例排序文件

**一键重建示例：**
```bash
python scripts/normalize_logos.py assets/logos --outdir logos_fit --maxw 1200 --maxh 400
python scripts/refill_template.py assets/template.pptx logos_fit assets/order.txt 示例客户墙.pptx
```

> 注意：示例logo为灰色占位图，实际使用时替换为真实企业logo。

## 设计原则与排错

- 设计原则：`references/design-principles.md`
- 常见问题排错：`references/troubleshooting.md`

## 依赖

```
requests beautifulsoup4 lxml pillow python-pptx
```

浏览器抓取额外需要：`playwright` + Chromium。
