# Labthink 豆包Skill集合

济南兰光机电技术有限公司内部使用的豆包Skill集合，用于提升工作效率。

## 🚀 安装方式

### 方式一：一键安装（推荐，复制这句话发给豆包）

```
帮我安装labthink豆包skill集合：
1. 用git克隆仓库 https://github.com/zonrin-lc/labthink.git 到 D:\labthink
2. 进入目录运行 install-all.bat 安装所有skill
3. 告诉我安装了哪些skill
```

豆包会自动完成：安装Git → 克隆仓库 → 运行安装脚本 → 报告结果。

### 方式二：手动安装

**第1步：安装Git**（如果没有）
- 下载：https://git-scm.com/download/win
- 安装时全部默认选项

**第2步：克隆仓库**
```bash
git clone https://github.com/zonrin-lc/labthink.git D:\labthink
```

**第3步：运行安装脚本**
```bash
cd D:\labthink
install-all.bat
```

**第4步：重启豆包**
完全关闭豆包（包括右下角托盘图标），然后重新打开。

### 安装验证

在豆包里输入：
```
你有哪些skill？列出industry-solution-ppt、logo-wall和labthink-bid-review-portable
```

看到这三个skill就说明安装成功。

### 更新Skill

```bash
cd D:\labthink
git pull
install-all.bat
```

然后重启豆包。

> 详细说明见 [同事使用指南](USAGE.md) | [快速安装卡片](QUICKSTART.md)

## Skill列表

| Skill | 说明 | 状态 |
|---|---|---|
| [industry-solution-ppt](skills/industry-solution-ppt/) | 基于医药行业方案模板，快速生成其他行业（食品/化工/环境等）解决方案PPT | ✅ 可用 |
| [logo-wall](skills/logo-wall/) | 企业Logo搜集与PPT客户墙排版工具（支持49家客户logo墙自动生成） | ✅ 可用 |
| [labthink-bid-review-portable](skills/labthink-bid-review-portable/) | 投标响应文件只读审阅与复核打分（14项检查+围标串标对比+评标办法得分，零依赖可移植） | ✅ 可用 |

## 使用示例

```
基于医药行业方案，帮我做一份食品行业的解决方案PPT
```

```
帮我做一份食品行业49家企业的logo墙PPT
```

```
帮我审阅这份投标响应文件，输出核查报告
```

```
对比这几家投标文件，查围标串标痕迹
```

## Skill详细说明

### industry-solution-ppt — 行业解决方案PPT制作

**功能**：基于已定稿的医药行业PPT（V1.5，32页）扩展到食品、化工、环境、建材等其他行业。

**核心特性**：
- 模板复用模式：仅重写约25%行业专属页，75%通用模块直接复用
- 智能术语替换：自动加载对应行业知识文件，确保检测项目术语准确
- 实战避坑指南：autoFit设置、医药术语残留检查、各页面替换清单
- 客户墙集成：内置logo-wall子流程

**使用方法**：
```
基于医药行业方案，帮我做一份食品行业的解决方案PPT
```

### logo-wall — 企业Logo搜集与客户墙排版

**功能**：从官网批量抓取企业logo，标准化处理后生成统一规格的PPT客户墙。

**核心特性**：
- 支持无浏览器和Playwright浏览器两种抓取模式
- SVG自动转PNG
- 自动裁白边、fit-inside统一尺寸、品牌色重着色
- 视觉QA拼图生成
- 支持向用户PPT模板填充logo或从零构建

**使用方法**：
```
帮我做一份食品行业49家企业的logo墙PPT
```

### labthink-bid-review-portable — 投标响应文件审阅复核

**功能**：对 .docx 投标响应文件做只读检查与按评标办法重估得分，输出结构化 HTML 核查报告。

**核心特性**：
- 14 项只读检查：占位符、修订残留、TOC、符合性应答、盖章、页码、列宽实测、域错误、批注、外链、图片完整性、文档属性、修订/批注作者、隐藏文本
- 围标/串标检测：多文件横向对比（文档属性、作者交集、正文相似度、图片指纹）
- 评标办法抽取：从 .xlsx 里规则化抽取并给出保守/基准/乐观三档分数
- 零依赖：纯 Python 标准库（zipfile + xml.etree），无需 pip install，可直接拷贝运行

**使用方法**：
```
帮我审阅这份投标响应文件，输出核查报告
```

```
对比这几家投标文件，查围标串标痕迹
```

## 目录结构

```
labthink/
├── README.md                    # 本文件
├── install-all.bat              # Windows一键安装全部skill
├── install-all.sh               # Mac/Linux一键安装全部skill
├── config.example.yaml          # 配置模板
├── .gitignore
└── skills/
    ├── industry-solution-ppt/
    │   ├── SKILL.md             # 主流程
    │   ├── references/          # 12个行业知识文件 + 结构模板
    │   ├── scripts/             # 关键词扫描 + logo工具链
    │   └── assets/              # 资产说明
    └── logo-wall/
        ├── SKILL.md             # 主流程（要求先提供49家企业名称）
        ├── references/          # 设计原则 + 排错指南
        ├── scripts/             # 7个logo工具脚本
        └── assets/              # 示例logo + 模板（49个占位图+template.pptx）
    └── labthink-bid-review-portable/
        ├── SKILL.md             # 主流程（14项检查+围标串标+评标办法）
        ├── scripts/             # docx_review + bid_collusion + xlsx_eval
        ├── references/          # HTML报告模板
        └── examples/            # 自测样本与39项断言
```

## 依赖环境

- 豆包专业版
- 飞书连接器授权（lark-cli）
- Python 3.x（行业方案PPT需 lxml；投标审阅技能零依赖）
- Git（用于更新skill）

## 贡献指南

1. 在`skills/`下新建skill目录
2. 包含`SKILL.md`（必须有name和description字段）
3. 提交PR或直接推送
4. 更新本README的Skill列表

## 仓库维护

### 设置仓库描述和主题标签

在GitHub仓库页面（https://github.com/zonrin-lc/labthink）点击右上角齿轮图标设置：

- **Description（描述）**：济南兰光机电技术有限公司内部豆包Skill集合，包含行业解决方案PPT制作、企业Logo墙生成等工具
- **Website**：可留空或填写公司官网
- **Topics（主题标签）**：`doubao` `skill` `ppt` `labthink` `automation` `python` `feishu` `lark`

### 发布Release

当Skill有重大更新时，创建Release：

1. 进入仓库 → Releases → Create a new release
2. Tag版本号：`v1.0.0`（语义化版本）
3. 标题：`v1.0.0 - 初始版本`
4. 描述：更新内容摘要
5. 勾选 "Set as the latest release"

## 许可证

内部使用，禁止公开分发。企业logo和客户名单涉及商标权和商业机密，仅限授权人员使用。
