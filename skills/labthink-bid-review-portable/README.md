# labthink-bid-review-portable

兰光投标响应文件审阅复核（可移植版）。对 `.docx` 投标响应文件做只读检查与复核打分，输出结构化 HTML 核查报告。

## 功能特性

- **零依赖**：仅用 Python 标准库（`zipfile` + `xml.etree`）直接解析 OOXML，无需联网、无需 pip install、不污染环境
- **只读检查**：不修改原文件，输出独立 HTML 报告
- **围标/串标检测**：
  - 单文件自查（报告“二、围标/串标风险自查（重点关注）”重点区块）：12 个风险子项（文档属性创建者/最后修改者/公司/经理、模板、时间戳、修订/批注作者、隐藏文本、嵌入对象、外部文件链接、共享文档标记），内置《招标投标法实施条例》第四十条依据说明与逐项清零提示
  - 多文件横向对比：`bid_collusion.py` 脚本
- **评标办法重估**：按评标办法抽取结构化数据并复核得分
- **修订感知**：跳过 `w:del` 子树，已删除内容不混入统计
- **页眉/页脚解析**：盖章、声明等关键词可命中页眉页脚
- **完整性检查**：域错误残留、批注残留、外部链接、图片引用完整性、模板残留、嵌入对象、外部文件链接、共享文档标记（共 18 项检查）

## 适用场景

- "帮我审阅这份投标响应文件"
- "检查投标文件有没有问题"
- "复核投标文件得分"
- "检测围标串标痕迹"
- "投标文件合规性检查"
- "检查投标文件有没有围标串标风险"

## 使用方法

在豆包中直接说"帮我审阅这份投标响应文件"并上传 `.docx` 投标文件，或命令行运行：

```bash
# 基本用法
python scripts/docx_review.py 标书.docx --out report.html

# 带本公司名称（围标/串标自查一致性判定）与评标办法
python scripts/docx_review.py 标书.docx --eval 评标办法.xlsx \
  --company "本公司名称" --score-low 80 --score-mid 85 --score-high 90 \
  --out report.html

# 围标/串标多文件横向对比（至少 2 个投标文件）
python scripts/bid_collusion.py 标书A.docx 标书B.docx --out collusion_report.html

# 自测（65 项断言，回归用）
python examples/run_sample_test.py
```

## 依赖环境

- Python 3.8+（**仅标准库**，无需安装任何第三方包）

## 目录结构

```
labthink-bid-review-portable/
├── SKILL.md                    # 主流程文档
├── scripts/
│   ├── docx_review.py          # 核心：抽取 + 检查（18 项）+ 围标自查区块 + 生成 HTML 报告
│   ├── bid_collusion.py        # 围标/串标多文件横向对比
│   └── xlsx_eval.py            # 评标办法 .xlsx 抽取
├── references/
│   └── report_template.html    # HTML 报告样式（唯一来源）
└── examples/
    ├── make_sample.py          # 自测样本生成器
    ├── run_sample_test.py      # 65 项自测断言
    ├── sample_bid.docx         # 自测样本（投标人一）
    ├── collusion_b.docx        # 自测样本（投标人二）
    ├── sample_report.html      # 样本单文件核查报告
    └── collusion_report.html   # 样本围标/串标对比报告
```

## 版本历史

- **v1.2.0**（当前）：单文件围标/串标自查升级为报告重点区块（12 风险子项 + 法条依据 + 逐项清零提示）；新增 4 项检查（模板残留/嵌入对象/外部文件链接/共享文档标记，14 → 18 项）；自测断言 39 → 65 项
- **v1.1.0**：修订感知增强、页眉/页脚解析、围标/串标检测（3 项单文件 + 多文件对比）、表格列宽实测、评标办法抽取结构化、报告增强（文件哈希、三档得分）
- **v1.0.0**：初始可移植版，零依赖解析 OOXML

## 与原版的区别

| 维度 | 原版 | 本可移植版 |
|---|---|---|
| 解析依赖 | python-docx + openpyxl | 仅标准库 zipfile + xml.etree |
| 运行前提 | 需联网安装第三方库 | 任何 Python 3.8+ 即可 |
| 环境安全 | 可能污染全局 site-packages | 零副作用 |
| 携带方式 | 依赖外部库存在 | 目录整体拷贝即迁移 |
