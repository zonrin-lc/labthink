# labthink-industry-solution-ppt

行业解决方案PPT制作Skill（通用版）。基于企业提供的参考材料（公司介绍、产品手册、检测报告、行业标准、资质荣誉等）制作面向特定行业的解决方案PPT及其内容稿。

## 功能特性

- **模板复用模式**：基于已定稿的医药行业PPT（V1.6，32页）扩展到其他行业，仅重写行业专属页（约25%）
- **内容稿先行**：先产出内容稿，用户确认后再制作幻灯片
- **事实审查**：对照材料逐条事实审查，确保数据可追溯
- **行业知识路由**：支持医药/食品/化工/环境/冶金/建材/橡胶/塑料/烟草/饲料/造纸/能源等12个行业
- **客户墙子流程**：内置49家医药企业logo资产，支持按客户名单抓取新logo

## 适用场景

- "做一份XX行业解决方案PPT"
- "写方案内容稿"
- "先出内容稿再出PPT"
- "按材料做一个行业方案"
- "把这份材料做成对外讲稿/方案"

## 安装方式

### 方式一：豆包自动安装（推荐）

复制这句话发给豆包：
```
帮我安装labthink-industry-solution-ppt skill，仓库地址：https://github.com/zonrin-lc/labthink.git
```

### 方式二：单独安装

双击运行仓库根目录的 `install-labthink-industry-solution-ppt.bat`

### 方式三：一键安装全部

双击运行仓库根目录的 `install-all.bat`，选择安装全部或指定Skill

## 使用方法

1. 重启豆包
2. 输入"帮我做一份XX行业解决方案PPT"
3. 提供企业材料（公司介绍、产品手册、检测报告、行业标准等）
4. 按流程产出内容稿 → 事实审查 → 修订定稿 → 制作幻灯片

## 依赖环境

- 豆包专业版
- 飞书连接器授权（读取行业标准表、检测报告库）
- Python 3.x + lxml库

## 目录结构

```
labthink-industry-solution-ppt/
├── SKILL.md                          # 主流程文档
├── assets/
│   ├── templates/
│   │   └── pharma-template-v1.6.pptx # 制药行业基础模板（32页）
│   └── logo-wall/                    # 客户墙资产（49家医药企业logo）
├── references/
│   ├── deck-structure.md             # PPT五幕结构模板
│   ├── brand-language.md             # 品牌设计语言
│   ├── fact-check.md                 # 事实审查清单
│   ├── copywriting.md                # 文案措辞规范
│   ├── logo-wall-design.md           # 客户墙设计原则
│   ├── logo-wall-troubleshooting.md  # logo抓取排错指南
│   └── industry/                     # 12个行业知识文件
└── scripts/
    ├── scan_keywords.py              # 关键词扫描脚本
    └── logo-wall/                    # 客户墙工具脚本（7个）
```

## 版本历史

- **V1.6**（当前）：C860/C870场景页各补充第二个真实客户案例
- **V1.5**：元素解组优化布局，修复组合元素导致的布局问题
- **V1.4**：初始定稿版
