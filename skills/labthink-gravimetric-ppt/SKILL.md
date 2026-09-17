---
name: labthink-gravimetric-ppt
description: 济南兰光（Labthink）重量分析产品（C840蒸发残渣/C860灼烧残渣·灰分/C870干燥失重·水分）行业解决方案PPT制作技能。面向"给定行业 → 产出一份对外解决方案PPT"的完整流程：先定行业（自动匹配色调风格/行业术语/行业标准/行业困境与政策）→ 行业知识与飞书知识库标准检索 → 内容稿 → 事实审查 → 49家合作客户Logo墙（内置49家医药客户Logo资产与排版脚本）→ 幻灯片制作 → 终检交付。内置四套已验证版式（A=用户定稿V1.4深蓝金为主，B=豆包墨绿金，C=Kimi米白深蓝金，D=WorkBuddy蓝青金），无论选哪套版式，"关于Labthink公司介绍页、资质与荣誉页、产品体系架构页"三页一律复用用户V1.4原版（仅允许改色调）。当用户说"做一份XX行业的重量分析/水分/灰分/灼烧残渣/蒸发残渣解决方案PPT""按行业出方案""兰光行业方案PPT"时使用。
---

# 兰光重量分析产品 · 行业解决方案 PPT 制作

面向"**选定行业 → 兰光重量分析产品行业解决方案 PPT**"的端到端工作流。产品恒为三系列：**C870 干燥失重/水分、C860 灼烧残渣·炽灼残渣/灰分、C840 蒸发残渣/不挥发物**；变化的是**行业**——行业决定色调、术语、标准、困境、政策、案例。

## 0. 开工前置：先定行业与版式（不可跳过）

### 0.1 确定目标行业
开工第一件事是确认本次面向哪个行业。行业决定一切下游内容：
- 从 `references/industry/` 加载对应行业知识文件（术语、标准映射、政策来源、客户类型）：
  `pharma`（医药/药包材/制药用水/医疗器械）、`food`（食品+食品接触材料）、`environment`（水质/大气/土壤/固废/海洋）、`metallurgy`（冶金/钢铁/有色/矿石/耐材）、`construction`（建材/水泥/陶瓷/玻璃/铸造）、`rubber`（橡胶）、`plastics`（塑料及高分子）、`chemical`（化学试剂/化工/涂料/胶黏剂/油墨）、`tobacco`（烟草）、`feed`（饲料/肥料/农药）、`paper`（造纸/纸浆/纺织/皮革/木材）、`energy`（煤炭/石油/润滑油）。
- 同时打开 `references/industry/terms-crosswalk.md` 跨行业术语对照表，确认本行业标准用词（最高频出错点：医药"炽灼残渣"不可写"灼烧残渣"、食品接触材料"总迁移量"不可写"蒸发残渣"、饲料"粗灰分"不可省"粗"）。
- 无对应知识文件时：用 `scripts/scan_keywords.py` 从材料提取标准号/术语/客户类型，现场建知识清单；无法核实的标"待核验"，沉淀为新行业文件。

### 0.2 按行业取色调风格
色调不是自选，由行业路由决定。见 `references/design-systems.md` 的"行业→主色映射表"：医药=深蓝金（默认A版式）、食品=暖橙/绿、化工=蓝灰、冶金=钢青、环保=青绿……**主版式结构不变，只换行业主色与强调色**。用户另有指定时以用户为准。

### 0.3 选版式（默认A，须与用户确认）
四套版式均已由真实成稿验证，见 `references/design-systems.md`：
- **版式 A（默认主，用户定稿 V1.4）**：深蓝黑 `#040505` 章节页 + 金 `#F5B700/#FCC800` + 白底浅灰卡片，32页五幕。**未经用户明确要求，默认用 A。**
- 版式 B（豆包）：墨绿 `#0F3D3E` + 金 `#C9A961`，带英文副标题、精致卡片。
- 版式 C（Kimi）：深蓝 `#131B36` + 金 `#F5B700` + 米白 `#EDEAE0/#D9D4C7`，每页页眉导航条。
- 版式 D（WorkBuddy）：深蓝 `#0F233C` + 青 `#00A0B0` + 金 `#F5B700` + 浅蓝白 `#F5F8FC`，37页六章、含市场趋势与对比页。
- **四套版式元素不可混用**；选定后全篇一致。

### 0.4 三条不可破的硬约束
1. **三个固定页永远复用用户 V1.4 原版**，无论选哪套版式、换什么色调：
   - 第二章"关于 Labthink 公司介绍页"（始于1989/37年/110+国家/70%市占 + 自主创新/科研平台/标准话语权/知识产权四栏）
   - "资质与荣誉页"（官方资质/行业身份与话语权/科技奖项三段式）
   - 第三章"产品体系架构页"（数据层/执行层/控制层三层 + 六模块）
   - 详见 `references/locked-pages.md`。**只允许改这三页的主色/强调色以适配行业，文字、数据、结构、图标关系一律不得改动。**
2. **客户墙页必须 49 家**，使用内置 49 家合作客户 Logo 资产与排版脚本（见 `references/industry-logo-wall.md`），不得自行编造客户、不得凑整增减。
3. **行业标准与实证案例必须来自飞书知识库**（见 `references/industry-router.md`）：按行业检索标准号与关键条款；实证案例若知识库/材料中有对应行业案例选 **2 个**，没有对应行业案例则**自动补 1 个通用模糊化案例**，并在内容稿标注"通用示例，待客户真实案例替换"。

## 工作流

### 1. 读全参考材料
- 材料可能是 docx/pptx/pdf/xlsx/png；docx 遍历 paragraphs/tables/inline_shapes 及 word/media；pdf 用 get_text+get_images+find_tables。
- 公司介绍 PPT 是数据权威来源（成立年份/客户数/资质/研发投入），优先完整读取。
- 用 `scripts/scan_keywords.py` 按关键词定位关键事实；所有数字/名称/结论可追溯到文件与页码，禁止凭印象补数据；同系列型号参数不可类推。

### 2. 行业标准与案例检索（飞书知识库）
- 按 `references/industry-router.md` 的步骤，用 `lark-cli` 检索**两个**飞书知识库：
  - **行业标准库**：根 wiki `https://ucn0ovkrddzj.feishu.cn/wiki/ZiY7wZN3RiXKZ1kIvMIc25uHnVh`（space_id `7684206381922028732`），10 个行业分类 + 索引 sheet；按目标行业取"标准号/标准名称/版本/对应 C840·C860·C870/关键条款"。
  - **检测报告案例库**：wiki `https://ucn0ovkrddzj.feishu.cn/wiki/FGNlwh8jKiHa0gknHorc8RbwnXc`（spreadsheet `PTHdszLd6hHZfwtsWorclYzDn4t`），26 份脱敏报告 × 29 字段，按 C840/C860/C870 分页。
  - 标准号以现行有效版本为准；公开标准全文可在 https://openstd.samr.gov.cn/bzgk/gb/ 核对。
- 据此生成本行业的：**行业困境（效率/误差/风险/合规四维）+ 政策驱动（每条标注发文部门/日期）+ 引用标准清单**。
- **实证案例**：从检测报告案例库按行业/产品挑 **2 个真实报告**（客户已脱敏、数值取报告原文，试机/未恒重/异常报告不选）；无对应行业报告才补 1 个通用案例并标注待客户真实报告替换。详见 industry-router.md 第 4 节。

### 3. 内容稿先行
- 默认先产出内容稿（docx/md），用户确认后再做幻灯片；用户只要文字就只交文字稿。
- 结构按 `references/deck-structure.md` 五幕（困境与政策 / 关于公司[含3固定页] / 产品体系[含1固定页] / 应用场景与实证 / 服务支持），每页标注数据出处。
- 文字稿是后续 PPT 的唯一内容基线。

### 4. 事实审查
- 按 `references/fact-check.md` 四维清单（虚构/事实错误/前后矛盾/缺依据）+ 行业术语独立复检。
- 每条问题 = 位置 + 问题 + 材料原文依据 + 修改建议；找不到出处的单独标注；汇总/换算/比例用计算工具复核，禁止心算。

### 5. 制作 49 家客户 Logo 墙页
- 按 `references/industry-logo-wall.md` 执行（已融合 logo-wall 全流程）：
  - 直接用 `assets/logo-wall/logos/01_…49_…png`、`order.txt`、`template.pptx`（医药行业 49 家已 QA 客户墙）。
  - 非医药行业需更换客户名单时，按该文件流程用 `scripts/logo-wall/` 重新抓取/归一化；**未重新抓取前不得改名单**。
  - 金规则：严格按名单顺序、统一格子不拉伸、白底/透明底彩色版、数量严格=名单数、必做视觉 QA。

### 6. 制作幻灯片
- 读取并遵循 ppt skill 的 SKILL.md 及新建/改稿分支，不可凭记忆操作。
- 按选定版式（默认 A）执行；三个固定页从用户 V1.4 源文件对应页抽取 XML/版式复用，仅替换主色。
- 逐页闭环：落稿 → 三查（结论式标题/溢出重叠对比度/数据与基线一致）→ 渲染确认 → 每页 note 写 3–5 句可照读讲稿。
- 产品页用实拍图；流程页用流程图；共性特点按"精准/高效/合规/安全"四维；连续两页避免相同骨架。
- 跨轮编辑后必须用 present_files 交付最新版本。

### 7. 终检与交付
- 合并自检：内容项（3 固定页文字零改动、49 客户数对、标准号现行、术语正确、政策有出处、案例数量达标）+ 工程项（页数对、无溢出、配色统一、note 齐全）。
- 交付：可查看的 PPTX + 可编辑源文件 + 简短说明（总页数/结构/关键取舍/待客户真实案例替换项）。

## 资源
- `references/design-systems.md` — 四套版式规范 + 行业→色调映射（替换旧版 design-languages）
- `references/locked-pages.md` — 三个固定复用页的文字/数据/结构清单（只允许改色）
- `references/industry-router.md` — 行业自适应路由 + 飞书知识库检索操作手册
- `references/industry-logo-wall.md` — 49 家客户 Logo 墙融合工作流
- `references/deck-structure.md` — 五幕结构模板
- `references/fact-check.md` — 事实审查清单
- `references/copywriting.md` — 文案/客户模糊化/属地规范
- `references/industry/`（13 文件）— 分行业知识 + terms-crosswalk 跨行业术语对照
- `references/logo-wall/` — Logo 墙设计原则与排障
- `assets/logo-wall/` — 49 家客户 Logo、order.txt、logo-index.xlsx、template.pptx
- `scripts/scan_keywords.py` — docx/pptx/pdf/xlsx 关键词扫描
- `scripts/logo-wall/` — Logo 抓取/归一化/建墙脚本集（fetch_logos/browser_fetch/normalize_logos/build_logo_wall/refill_template/make_sheet 等）
