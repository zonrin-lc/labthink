---
name: labthink-bid-review-portable
version: 1.1.0
description: 对 .docx 投标响应文件做只读检查与复核打分；零依赖（仅 Python 标准库），可直接拷贝到任意装有 Python 3 的机器运行。可移植版。
display_name: "兰光投标响应文件审阅复核（可移植版）"
display_name_en: "Labthink Bid Response Document Review (Portable)"
agent_created: true
visibility: "public"
portable: true
---

# 兰光投标响应文件审阅与复核（可移植版）

对一份 `.docx` 投标响应文件执行**只读检查**与**按评标办法重估得分**，输出结构化 HTML 核查报告。
本版本是「投标响应文件审阅复核」的**可移植改造版**：把原版对 `python-docx` / `openpyxl` 的强依赖，替换为**纯 Python 标准库**（`zipfile` + `xml.etree`）直接解析 OOXML，因此**无需联网、无需 pip install、不污染环境**，可直接拷贝到任意装有 Python 3.8+ 的机器运行。

## 与原版的关键差异（为什么可移植）

| 维度 | 原版 | 本可移植版 |
|---|---|---|
| 解析依赖 | `python-docx` + `openpyxl`（`pip install`） | 仅标准库 `zipfile` + `xml.etree` |
| 运行前提 | 需联网安装第三方库 | 任何 Python 3.8+ 即可 |
| 环境安全 | 可能污染全局 site-packages | 零副作用 |
| 携带方式 | 依赖外部库存在 | 目录整体拷贝即迁移 |

`.docx` / `.xlsx` 本质都是 zip 包（OOXML）。正文在 `word/document.xml`，页眉页脚在 `word/header*.xml` / `footer*.xml`，共享字符串在 `xl/sharedStrings.xml`，工作表在 `xl/worksheets/sheetN.xml`。本 skill 的脚本直接读这些 XML，做到零依赖。

## v1.1.0 更新要点

- **修订感知增强**：收集文本时跳过 `w:del` 子树，已删除内容不再混入正文统计（避免“待补充”等占位符被旧版本内容误报）；
- **新增页眉/页脚解析**：盖章、声明等关键词可命中页眉页脚（该处是盖章声明的常见位置）；
- **新增检查项**：域错误残留（“错误！未找到引用源”等）、批注残留、外部链接/引用、图片引用完整性（r:embed 指向的媒体文件是否缺失）；
- **新增围标/串标检测**（详见下方专节）：单文件自查 3 项（文档属性、修订/批注作者、隐藏文本）+ 多文件横向对比脚本 `bid_collusion.py`；
- **表格列宽改为实测**（tblGrid vs 页面可用宽度），无表格时不再恒报“待处理”；
- **评标办法抽取结构化**：按 workbook.xml 真实工作表顺序、跳过隐藏表、保留列位、铺开合并单元格，报告以表格呈现（含工作表名与行号）；
- **报告增强**：输出文件大小/最后修改时间/SHA-256（证明核查的是哪一版文件）；三档得分支持 `--score-low/mid/high` 填入；“待处理检查项”区仅列 warn/error，不再与第二节重复；
- **健壮性**：HTML 转义补引号、Windows stdout 编码兜底、import 不依赖当前目录、样式优先读 `references/report_template.html`（单源维护）。

## 围标/串标痕迹检测

**单文件自查（docx_review.py，14 项检查中的 3 项）**：
- **文档属性（作者/公司）**：读取 `docProps/core.xml`、`app.xml` 的创建者/最后修改者/公司/经理，暴露是否残留其他编制方信息；提供 `--company "本公司名"` 后，公司字段与本公司不一致会标 warn；
- **修订/批注作者**：汇总 `w:ins`/`w:del` 修订作者与批注作者；`--company` 下检出非本公司作者会标 warn（多人轮转修改同一家标书是串标常见形态）；
- **隐藏文本**：检测 `w:vanish` 隐藏文字（残留的内部备注/其他编制方信息）。

**多文件横向对比（bid_collusion.py）**：逐对对比多家投标文件：
| 信号 | 说明 | 等级 |
|---|---|---|
| 文档属性相同 | 创建者 / 最后修改者 / 公司 / 经理一致 | 高 |
| 修订作者交集 | 同一人/同一编制组修改多家标书 | 高 |
| 批注作者交集 | 批注人交叉 | 高 |
| 文档属性指纹相同 | core.xml / app.xml 内容一致（同一制作链） | 高 |
| 正文相似度 | 去空白 4-gram Jaccard：≥90% 极高（疑似同一底稿）/ ≥75% 高 | 高/中 |
| 相同图片指纹 | word/media/* 内容 SHA-256 相同 | 中 |

> **使用注意**：所有信号均为**线索而非结论**。创建者同为系统默认名、共用招标文件截图等都可能造成巧合命中；请结合招标文件要求、开标记录、保证金来源等证据综合判断，涉及围标串标认定须移交监管或法务部门依法处理。对比报告在结论区内置此说明。

## 适用情形

- 提交标书前自查：完整性、遗漏项、评分隐患、合规问题；
- 依据评标办法重估得分（保守 / 基准 / 乐观三档工作表）；
- 用户给出一组调整项，要求逐条确认是否已处理到位。

## 目录结构

```
labthink-bid-review-portable/
├── SKILL.md
├── scripts/
│   ├── docx_review.py     # 核心：抽取 + 检查（14 项）+ 生成 HTML 报告
│   ├── bid_collusion.py   # 围标/串标痕迹多文件对比
│   └── xlsx_eval.py       # 评标办法 .xlsx 抽取（供评分工作表）
├── references/
│   └── report_template.html  # 报告版式（IBM Carbon 风格，样式唯一来源）
└── examples/
    ├── make_sample.py     # 生成自测样本 docx（含页眉/修订/域错误/图片/串标痕迹）
    ├── run_sample_test.py # 自测断言（39 项，防止重构破坏行为）
    ├── sample_bid.docx    # 自测样本（投标人一）
    ├── collusion_b.docx   # 自测样本（投标人二，与样本一存在串标信号）
    ├── sample_report.html     # 样本单文件核查报告
    └── collusion_report.html  # 样本围标/串标对比报告
```

## 执行步骤

**阶段一：确认输入** —— 找出响应文件本体及配套材料（招标文件、评标办法、模板等）。脚本会记录文件体积、最后修改时间与 SHA-256 到报告，确保核查版本可追溯。

**阶段二：全量抽取正文** —— `docx_review.py` 递归收集段落、表格、文本框、页眉页脚文本，并做**修订感知**（跳过 `w:del` 删除子树）。

**阶段三：完整性排查（14 项，逐项脚本验证）**：
1. 占位符/未填内容扫描（`待补充`/`TODO`/`XXX` 等，可 `--patterns` / `--patterns-add` 自定义）；
2. 修订残留（`w:ins`/`w:del` 计数）；
3. 目录域 TOC 是否存在；
4. 符合性应答是否出现（`完全满足` 等，可 `--compliance` / `--compliance-add` 自定义）；
5. 盖章/声明关键词出现次数（正文 + 页眉页脚，可 `--stamp` / `--stamp-add` 自定义）；
6. 页码占位残留（`Pg` / `第 页`，不误伤“第 5 页”正常引用）；
7. 表格列宽（实测 tblGrid vs 页面可用宽度，超宽自动提示）；
8. 域错误残留（`错误！未找到引用源` 等，Word 域未刷新的高频硬伤）；
9. 批注残留；
10. 外部链接/引用（离线评标环境可能失效）；
11. 图片引用完整性（r:embed 指向的媒体文件是否缺失）；
12. 文档属性（作者/公司，串标痕迹，`--company` 可判定一致性）；
13. 修订/批注作者（串标痕迹，`--company` 可判定是否含非本公司作者）；
14. 隐藏文本（`w:vanish`，残留内部备注等）。

**阶段四：核定评分口径** —— 若提供 `--eval 评标办法.xlsx`，`xlsx_eval.py` 按工作表真实顺序抽取疑似评分条目（保留行号、列位、合并单元格），在报告中以表格呈现，供用户核定权重/档位。

**阶段五：重估得分** —— 报告提供「保守 / 基准 / 乐观」三档框架；可用 `--score-low/--score-mid/--score-high` 直接填入，也可由投标人依据评标办法原文核定后填写（避免脚本臆断）。

**阶段六：输出核查报告** —— 自包含 HTML（样式读自模板），含六大区块：文件信息 / 核查概要 / 调整项核验 / 评分风险与建议 / 重估得分 / 待处理检查项。

## 约束与提醒

- **只读铁律**：全程不修改原标书，改动只给建议/待办清单。
- **独立核验、不采信缓存**：若用户质疑读错文件，重新定位最新文件并重抽。
- **结论逐条有据**：每条结论由脚本扫描结果支撑。
- **评分风险显式提示**：影响得分、需拍板的事项单独列出并附建议。

## 运行方式

```bash
# 基本用法（仅需标书）
python scripts/docx_review.py 标书.docx --out report.html

# 带评标办法与三档得分
python scripts/docx_review.py 标书.docx --eval 评标办法.xlsx \
  --score-low 80 --score-mid 85 --score-high 90 --out report.html

# 自定义扫描关键词（--xxx 替换默认；--xxx-add 在默认后追加）
python scripts/docx_review.py 标书.docx \
  --patterns "待补充;TODO;XXX" \
  --compliance "完全满足;满足" \
  --stamp "盖章;声明;签章" \
  --stamp-add "电子签章;骑缝章" \
  --company "本公司名称" \
  --score-note "评分口径：以评标办法原文为准，业绩仅计已验收项目。"

# 围标/串标痕迹多文件对比（至少 2 个投标文件）
python scripts/bid_collusion.py 标书A.docx 标书B.docx 标书C.docx \
  --out collusion_report.html

# 自测（39 项断言，回归用）
python examples/run_sample_test.py
```

> 注：脚本内部已显式将自身目录加入 `sys.path`，任意目录下运行均可正确引用 `xlsx_eval` 模块，无需先 cd 到 `scripts/`。

## 前置依赖

- **仅需 Python 3.8+**（标准库 `zipfile`、`xml.etree.ElementTree`、`argparse`、`re`、`datetime`、`hashlib`、`os`）。无第三方库、无需联网。

## 已知限制

- 仅支持 `.docx`（OOXML）；`.doc` 老格式、`.wps` 等不支持，请先在 Word/WPS 中另存为 `.docx`。
- 评标办法 `.xlsx` 中**日期格式单元格**显示为 Excel 内部序列号（零依赖版不做日期格式换算）；评分办法通常无日期，影响有限。
- `docx_review.py` 一次只核查一个标书文件；批量核查可对多个文件循环调用，多投标人横向比对用 `bid_collusion.py`。
- 加密/损坏的 docx、xlsx 会报解析失败（退出码 2）。
- 围标/串标信号仅为线索，最终认定须由招标人/监管部门依法结合证据作出。
