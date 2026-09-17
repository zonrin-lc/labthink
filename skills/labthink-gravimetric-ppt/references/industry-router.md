# 行业自适应路由 + 飞书知识库检索手册

## 1. 行业 → 产品线映射

无论哪个行业，兰光重量分析产品恒为三系列，按检测项目选系列：

| 检测项目（行业术语可能不同） | 产品线 | 典型场景 |
|---|---|---|
| 干燥失重 / 水分 / 干燥减量 / 烘干法 | C870 集成式干燥失重检测系统 | 原料药/辅料/食品水分/煤炭全水分 |
| 炽灼残渣 / 灰分 / 粗灰分 / 烧失量 / 灼烧残渣 | C860 集成式灼烧残渣检测系统 | 药炽灼残渣、食品/饲料粗灰分、煤灰分、橡胶灰分 |
| 蒸发残渣 / 不挥发物 / 总迁移量 | C840 集成式蒸发残渣检测系统 | 药包材、制药用水、食品接触材料、浸泡液残渣 |

恒重判定统一：连续两次称量差 ≤ 0.3mg；C840/C870 室温~130℃，C860 室温~800℃（外置液冷常温称重）。

## 2. 行业自适应要产出的内容

每换一个行业，必须为内容稿补齐四组内容（医药已有现成素材，其他行业按下法检索）：

1. **行业术语**：从 `references/industry/<行业>-knowledge.md` + `terms-crosswalk.md` 取标准用词。
2. **行业标准**：见第 3 节飞书知识库，列出本行业适用的标准号/名称/版本/关键条款，并标注对应 C840/C860/C870。
3. **行业困境**：传统重量分析在本行业的四维困境（效率/误差/风险/合规），尽量带本行业数字（如"单样2小时以上、全程值守""灰分800℃马弗炉人手取放"）。
4. **政策驱动**：本行业相关法规/新规/监管/数智化政策，**每条标注发文部门与日期**（如医药：2025版药典2025-10-01施行；七部门《医药工业数智化转型实施方案（2025—2030年）》）。

## 3. 飞书知识库检索操作（行业标准 + 案例）

**知识库根**：`重分产品-各行业标准`
- URL：`https://ucn0ovkrddzj.feishu.cn/wiki/ZiY7wZN3RiXKZ1kIvMIc25uHnVh`
- space_id：`7684206381922028732`

### 3.1 列行业分类
```
lark-cli wiki +node-list --space-id 7684206381922028732 \
  --parent-node-token "ZiY7wZN3RiXKZ1kIvMIc25uHnVh" --as user --format json --page-all
```
得到 10 个行业分类节点：
- 一、医药・药典・药包材・医疗器械 → `Y48nwUEMzi8e5ikGzaYcul5cnRh`
- 二、食品・食品接触材料・包装 → `Ehxowl7CbitbickBnVUc9EgTnfc`
- 三、环境监测・水质・大气・土壤・固废・海洋 → `IqfzwLwd8i2Ha6knRNOcy0ZRn7d`
- 四、化工・化学试剂・有机无机化工 → `UN52wOmcxiuM5dkLVRxcVxClnGu`
- 五、涂料・胶粘剂・塑料・橡胶・日化 → `JShPwAdDYi9JsXkZo1CcusOwnKb`
- 六、冶金・钢铁・有色金属・矿石・耐火材料 → `UJMkwkkZ1iRUGrkN70CcFfUPncI`
- 七、煤炭・焦炭・固体燃料 → `GLdvwLIb4itWN8kR92KcX95anUh`
- 八、建材・水泥・陶瓷・玻璃・铸造 → `O45QwmO0kioMQRk65d6cncOtnWh`
- 九、造纸・纸浆・纺织・皮革・木材 → `HAKewlpYaid2yEkTmtJce0Omntf`
- 十、饲料・肥料・农药 → `E8vxwSxIHinrOVkPV92cKXOgnwL`
- 其他参考 → `NVkKwquLRipyqsk0lOEc9wBdnag`

### 3.2 列某行业下的标准文件
```
lark-cli wiki +node-list --space-id 7684206381922028732 \
  --parent-node-token "<行业node_token>" --as user --format json --page-all
```
子节点为 PDF（obj_type=file）或 docx（药典通则）。docx 用下面 3.4 读全文；PDF 用 `lark-cli drive +download --wiki-token <node_token>` 下载后按 pdf skill 解析。

### 3.3 读标准索引表（一张表看全行业标准）
主文档嵌入一张索引 sheet：token `BrQTsOZekh971htc7uJcvYDGnad`，sheet-id `FusY4c`。列：行业领域 / 标准号 / 标准名称 / 版本·状态 / C840 / C860 / C870（●○标记）/ 文件链接 / 关键条款·备注。
```
lark-cli sheets +cells-get --url "https://ucn0ovkrddzj.feishu.cn/sheets/BrQTsOZekh971htc7uJcvYDGnad" \
  --range "FusY4c!A1:J200" --as user
```
按"行业领域"筛目标行业，取 ● 标记对应本行业产品的标准，"关键条款/备注"直接写进内容稿。

### 3.4 读药典通则 docx 全文
```
lark-cli docs +fetch --doc "<wiki链接或obj_token>" --as user --doc-format markdown
```
医药行业关键通则 node：0831 干燥失重、0832 水分、0841 炽灼残渣、4204 药包材溶出物、0261 制药用水。

### 3.5 标准现行性核对
- 标准号以官方题录为准：https://openstd.samr.gov.cn/bzgk/gb/
- 药典用现行版（2025年版，2025-10-01 施行）；注意换版（如 GB/T 4498.1-2025、GB/T 2793-2026）。商业网站标注的"新版号"不可靠。

## 4. 实证案例规则（来源：检测报告知识库）

实证案例**不是**凭空写，而是从"检测报告知识库索引表"里按行业/产品挑真实报告，客户名已脱敏。

### 4.1 案例库位置
- Wiki 节点：`https://ucn0ovkrddzj.feishu.cn/wiki/FGNlwh8jKiHa0gknHorc8RbwnXc`（标题"检测报告知识库索引表"，与行业标准库同一 space `7684206381922028732`）
- 电子表格 token：`PTHdszLd6hHZfwtsWorclYzDn4t`
- 7 个页签（用 `--sheet-id` 选，**不要**把 tab id 写进 range）：

| 页签 | sheet-id | 内容 |
|---|---|---|
| 说明 | `0GeRes` | 字段口径与维护规则（开工必读） |
| 索引表 | `1KTXDp` | **26 份报告 × 29 列全字段总表**（选案例用这张） |
| 结果明细 | `2NnnRl` | 样品/杯组级实测值、均值、平行差 |
| 客户代号 | `3NHnhV` | 脱敏客户名→代号映射（真实名单另存，PPT 只用代号化称谓） |
| 蒸发残渣 | `4SKEOx` | C840 类报告（3 份） |
| 炽灼残渣 | `5ssAjq` | C860 类报告（16 份） |
| 干燥失重 | `6QDeqE` | C870 类报告（8 份） |

### 4.2 索引表 29 列（选案例时按列取值）
报告编号 / 检测日期 / 报告版本 / 客户代号 / 样品名称 / 检测项目 / 测试标准·依据 / 仪器型号 / 空杯温度·首次·循环·模式 / 试样炭化·灰化·灼烧温度 / 试样时长·模式 / 取样量 / 介质·前处理 / 蒸发·水浴程序 / 限值要求 / 判定结果 / 设备组合·功能附件 / **结果摘要** / 报告文件路径 / 数据文件路径 / 照片路径 / 备注。

读取命令（jq 只取 value 矩阵）：
```
python -c "import subprocess,json; q='.data.ranges[0].cells | map(map(.value // \"\"))'; \
out=subprocess.run(['lark-cli','sheets','+cells-get','--url',\
'https://ucn0ovkrddzj.feishu.cn/sheets/PTHdszLd6hHZfwtsWorclYzDn4t',\
'--sheet-id','1KTXDp','--range','A1:AC60','--jq',q],capture_output=True,text=True,encoding='utf-8').stdout; \
print(json.loads(out))"
```
> 注意：`+cells-get` **不接受 `--as`**；range 不带 sheet 前缀，用 `--sheet-id` 选页。要更细的实测数据再读 `2NnnRl`（结果明细）对应行。

### 4.3 选案例规则
1. **按本次行业/产品挑 2 个真实报告**：优先选"备注"列已标注用于 PPT 场景的报告，判定结果为"符合"或有代表性实测值、标准条款明确的。
2. **已标注的 V1.4 三个场景数据源**（医药行业可直接复用）：
   - 场景一·蒸发残渣/不挥发物：A001 华东某制药 PVC 固体药用硬片总迁移量（C840H）；A011 四川某药业 PVC/PVDC 复合硬片蒸发残渣仪器验证（C840M）。
   - 场景二·炽灼残渣/灰分：A003 某阿胶 胶类/药材粉末灰分（药典2302灰分法，C860M）。
   - 场景三·干燥失重：A011 四川某药业 C840M/C870H/手工三机对比（麦芽糊精 4.37%/4.47% 等，药典0831）。
3. **某行业/产品在库里没有对应报告**时：用上述最接近的医药案例改写行业称谓，或按 V1.4 模板补 1 个通用模糊案例，并在内容稿标注"通用示例，待客户真实报告替换"。
4. **数据纪律**：数值一律取报告原文（索引表"结果摘要"+"结果明细"表），不推算、不估算；报告未给限值/判定的留空，不得编造"符合"。
5. 案例页结构：客户（用索引表里的脱敏称谓/客户代号化，如"华东某制药""某阿胶股份"）+ 设备组合（仪器型号列）+ 检测数据表（平行样、均值、判定）+ 客户价值。
6. 发货前试机/验机、未恒重、负值异常等报告**不选作对外案例**（备注已标）。
