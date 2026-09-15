# Logo资产说明

本目录用于存放客户墙logo资产。由于涉及商标权，仓库中不包含实际logo文件。

## 获取医药行业49家logo资产包

向管理员获取`logo-wall-assets.zip`，解压到本目录，结构如下：

```
assets/
├── logos/              # 49家医药企业logo（PNG，白底/透明底彩色版）
├── template.pptx       # 客户墙模板PPT（49单元格）
├── order.txt           # 企业排序文件（严格按用户名单顺序）
└── logo-index.xlsx     # logo索引表（企业名→文件名→来源→备注）
```

## 其他行业客户墙

做非医药行业方案时，需按SKILL.md的6阶段流程自行抓取和制作：
1. 准备客户名单（CSV格式：name,official_url）
2. 批量抓取logo（`scripts/fetch_logos.py`）
3. 浏览器抓取补充（`scripts/browser_fetch.py`）
4. SVG转PNG（`scripts/svg_to_png.py`）
5. 视觉QA（`scripts/make_sheet.py`生成拼图逐张检查）
6. 标准化（`scripts/normalize_logos.py`）
7. 生成PPT客户墙（`scripts/build_logo_wall.py`或`scripts/refill_template.py`）

## 注意事项

- 企业logo涉及商标权，仅限内部使用，禁止公开分发
- 严格按名单顺序排列，不按颜色/大小/重要性重排
- 必须做视觉QA，自动化抓取经常返回错公司、不可见白标、裁切不全
- "深色底块+白标"一律不用，改为重着色为品牌色
