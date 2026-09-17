# Labthink 豆包Skill集合

济南兰光机电技术有限公司内部使用的豆包Skill集合，用于提升工作效率。

## 📦 Skill列表

| Skill | 说明 |
|---|---|
| [labthink-industry-solution-ppt](skills/labthink-industry-solution-ppt/) | 行业解决方案PPT制作（通用版，基于V1.6模板扩展） |
| [labthink-logo-wall](skills/labthink-logo-wall/) | 企业Logo搜集与PPT客户墙排版（49家客户logo墙自动生成） |
| [labthink-bid-review-portable](skills/labthink-bid-review-portable/) | 投标响应文件只读审阅与复核打分（14项检查+围标串标+评标办法，零依赖） |

## 🚀 安装方式（推荐：豆包一句话自动安装）

**同事只需要复制下面对应的一句话，发给豆包，豆包会自动完成全部安装。不需要手动下载任何东西，也不需要懂技术。**

### 安装全部Skill

```
帮我安装labthink的豆包skill集合，仓库地址：https://github.com/zonrin-lc/labthink.git
```

### 单独安装 labthink-industry-solution-ppt（行业方案PPT）

```
帮我安装labthink-industry-solution-ppt skill，仓库地址：https://github.com/zonrin-lc/labthink.git
```

### 单独安装 labthink-logo-wall（客户Logo墙）

```
帮我安装labthink-logo-wall skill，仓库地址：https://github.com/zonrin-lc/labthink.git
```

### 单独安装 labthink-bid-review-portable（投标文件审阅）

```
帮我安装labthink-bid-review-portable skill，仓库地址：https://github.com/zonrin-lc/labthink.git
```

豆包会自动完成：检查环境 → 下载代码 → 安装skill → 报告结果。**同事全程只需要复制一句话，其他都由豆包自动处理。**

### 安装后验证

安装完成后，在豆包里输入：
```
你有哪些skill？列出已安装的skill
```

看到对应的skill就说明安装成功。

### 更新Skill

复制这句话发给豆包：
```
帮我更新labthink的豆包skill
```

---

## 🔧 备选：手动安装（不推荐）

如果豆包自动安装失败，可手动操作：

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
install-labthink-industry-solution-ppt.bat   # 或其他单独安装脚本
# 或
install-all.bat                                # 全部安装（可选择）
```

**第4步：重启豆包**
完全关闭豆包（包括右下角托盘图标），然后重新打开。

---

## 📖 Skill详细说明

### labthink-industry-solution-ppt — 行业解决方案PPT制作（通用版）

**功能**：基于已定稿的医药行业PPT（V1.6，32页，C840/C860/C870场景页各含2个真实案例）扩展到食品、化工、环境、建材等其他行业。

**核心特性**：
- 模板复用模式：仅重写约25%行业专属页，75%通用模块直接复用
- 智能术语替换：自动加载对应行业知识文件，确保检测项目术语准确
- 实战避坑指南：autoFit设置、医药术语残留检查、各页面替换清单
- 客户墙集成：内置logo-wall子流程

**使用方法**：
```
基于医药行业方案，帮我做一份食品行业的解决方案PPT
```

### labthink-logo-wall — 企业Logo搜集与客户墙排版

**功能**：从官网批量抓取企业logo，标准化处理后生成统一规格的PPT客户墙。

**核心特性**：
- 支持无浏览器和Playwright浏览器两种抓取模式
- SVG自动转PNG
- 自动裁白边、fit-inside统一尺寸、品牌色重着色
- 视觉QA拼图生成
- 支持向用户PPT模板填充logo或从零构建
- **必须先提供49家企业名称**，不存储之前的企业

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

## 📁 目录结构

```
labthink/
├── README.md                                    # 本文件
├── install-all.bat                              # 全部安装（可选择）
├── install-all.sh                               # Mac/Linux全部安装
├── install-labthink-industry-solution-ppt.bat   # 单独安装 行业方案PPT
├── install-labthink-logo-wall.bat               # 单独安装 客户Logo墙
├── install-bid-review.bat                       # 单独安装 投标文件审阅
├── config.example.yaml                          # 配置模板
├── .gitignore
└── skills/
    ├── labthink-industry-solution-ppt/
    │   ├── README.md                            # 单独说明
    │   ├── SKILL.md                             # 主流程
    │   ├── references/                          # 12个行业知识文件 + 结构模板
    │   ├── scripts/                             # 关键词扫描 + logo工具链
    │   └── assets/
    │       ├── templates/                       # 制药行业V1.6模板
    │       └── logo-wall/                       # 客户墙资产
    ├── labthink-logo-wall/
    │   ├── README.md                            # 单独说明
    │   ├── SKILL.md                             # 主流程（要求先提供49家企业名称）
    │   ├── references/                          # 设计原则 + 排错指南
    │   ├── scripts/                             # 7个logo工具脚本
    │   └── assets/                              # 示例logo + 模板
    └── labthink-bid-review-portable/
        ├── README.md                            # 单独说明
        ├── SKILL.md                             # 主流程
        ├── references/                          # HTML报告模板
        ├── scripts/                             # docx_review + bid_collusion + xlsx_eval
        └── examples/                            # 自测样本
```

## 🔧 依赖环境

- 豆包专业版
- 飞书连接器授权（labthink-industry-solution-ppt需要，由管理员统一开通）
- Python 3.x（labthink-industry-solution-ppt需 lxml；投标审阅技能零依赖）
- Git（豆包自动安装时会自动检查/安装）

## 🤝 贡献指南

1. 在`skills/`下新建skill目录，名称以`labthink-`开头
2. 包含`SKILL.md`（必须有name和description字段，name也以`labthink-`开头）
3. 创建对应的`install-<skill-name>.bat`单独安装脚本
4. 在本README的Skill列表中添加条目
5. 提交PR或直接推送

## 🏷️ 仓库维护

### 设置仓库描述和主题标签

在GitHub仓库页面（https://github.com/zonrin-lc/labthink）点击右上角齿轮图标设置：

- **Description（描述）**：济南兰光机电技术有限公司内部豆包Skill集合，包含行业解决方案PPT制作、企业Logo墙生成、投标文件审阅等工具
- **Topics（主题标签）**：`doubao` `skill` `ppt` `labthink` `automation` `python` `feishu` `lark` `bid-review`

## 📄 许可证

内部使用，禁止公开分发。企业logo和客户名单涉及商标权和商业机密，仅限授权人员使用。
