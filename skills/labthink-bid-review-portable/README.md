# labthink-bid-review-portable

兰光投标响应文件审阅复核（可移植版）。对 `.docx` 投标响应文件做只读检查与复核打分，输出结构化 HTML 核查报告。

## 功能特性

- **零依赖**：仅用 Python 标准库（`zipfile` + `xml.etree`）直接解析 OOXML，无需联网、无需 pip install、不污染环境
- **只读检查**：不修改原文件，输出独立 HTML 报告
- **围标/串标检测**：
  - 单文件自查：文档属性、修订/批注作者、隐藏文本
  - 多文件横向对比：`bid_collusion.py` 脚本
- **评标办法重估**：按评标办法抽取结构化数据并复核得分
- **修订感知**：跳过 `w:del` 子树，已删除内容不混入统计
- **页眉/页脚解析**：盖章、声明等关键词可命中页眉页脚
- **完整性检查**：域错误残留、批注残留、外部链接、图片引用完整性

## 适用场景

- "帮我审阅这份投标响应文件"
- "检查投标文件有没有问题"
- "复核投标文件得分"
- "检测围标串标痕迹"
- "投标文件合规性检查"

## 安装方式

### 方式一：单独安装（推荐）

双击运行仓库根目录的 `install-bid-review.bat`

### 方式二：豆包自动安装

复制这句话发给豆包：
```
帮我安装labthink-bid-review-portable skill：
1. 用git克隆仓库 https://github.com/zonrin-lc/labthink.git 到 D:\labthink
2. 运行 install-bid-review.bat 安装
3. 告诉我安装结果
```

## 使用方法

1. 重启豆包
2. 输入"帮我审阅这份投标响应文件"
3. 上传 `.docx` 投标文件
4. 豆包自动运行检查并输出 HTML 核查报告

### 命令行直接运行（可选）

```bash
python scripts/bid_review.py 投标文件.docx --output 核查报告.html
```

## 依赖环境

- Python 3.8+（**仅标准库**，无需安装任何第三方包）
- 豆包专业版（通过豆包调用时）

## 目录结构

```
labthink-bid-review-portable/
├── SKILL.md                    # 主流程文档
├── examples/                   # 示例文件
├── references/
│   └── report_template.html    # HTML报告模板
└── scripts/
    ├── bid_review.py           # 主检查脚本
    └── bid_collusion.py        # 围标串标多文件对比脚本
```

## 版本历史

- **v1.1.0**（当前）：
  - 修订感知增强（跳过 w:del）
  - 新增页眉/页脚解析
  - 新增围标/串标检测
  - 表格列宽改为实测
  - 评标办法抽取结构化
  - 报告增强（文件哈希、三档得分）
- **v1.0.0**：初始可移植版，零依赖解析 OOXML

## 与原版的区别

| 维度 | 原版 | 本可移植版 |
|---|---|---|
| 解析依赖 | python-docx + openpyxl | 仅标准库 zipfile + xml.etree |
| 运行前提 | 需联网安装第三方库 | 任何 Python 3.8+ 即可 |
| 环境安全 | 可能污染全局 site-packages | 零副作用 |
| 携带方式 | 依赖外部库存在 | 目录整体拷贝即迁移 |
