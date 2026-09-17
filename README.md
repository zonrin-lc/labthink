# Labthink 豆包Skill集合

济南兰光机电技术有限公司内部使用的豆包Skill集合，用于提升工作效率。

## 📦 Skill列表

| Skill | 说明 | 单独安装脚本 |
|---|---|---|
| [industry-solution-ppt](skills/industry-solution-ppt/) | 行业解决方案PPT制作（通用版，基于V1.6模板扩展） | `install-industry-solution-ppt.bat` |
| [logo-wall](skills/logo-wall/) | 企业Logo搜集与PPT客户墙排版（49家客户logo墙自动生成） | `install-logo-wall.bat` |
| [labthink-gravimetric-ppt](skills/labthink-gravimetric-ppt/) | 兰光重量分析产品行业方案PPT（专业版，四套版式可选） | `install-labthink-gravimetric-ppt.bat` |

## 🚀 安装方式

### 方式一：单独安装（推荐）

根据需要选择安装对应的Skill，双击运行对应的安装脚本：

| 需求 | 运行脚本 |
|---|---|
| 只做行业解决方案PPT | `install-industry-solution-ppt.bat` |
| 只做客户Logo墙 | `install-logo-wall.bat` |
| 兰光重量分析产品专用方案 | `install-labthink-gravimetric-ppt.bat` |
| 全部安装 | `install-all.bat`（可选择安装哪些） |

### 方式二：豆包自动安装（复制这句话发给豆包）

**安装单个Skill（以industry-solution-ppt为例）：**
```
帮我安装industry-solution-ppt skill：
1. 用git克隆仓库 https://github.com/zonrin-lc/labthink.git 到 D:\labthink
2. 运行 install-industry-solution-ppt.bat 安装
3. 告诉我安装结果
```

**安装全部Skill：**
```
帮我安装labthink豆包skill集合：
1. 用git克隆仓库 https://github.com/zonrin-lc/labthink.git 到 D:\labthink
2. 运行 install-all.bat 安装所有skill
3. 告诉我安装了哪些skill
```

### 方式三：手动安装

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
install-industry-solution-ppt.bat   # 或其他单独安装脚本
# 或
install-all.bat                      # 全部安装（可选择）
```

**第4步：重启豆包**
完全关闭豆包（包括右下角托盘图标），然后重新打开。

### 安装验证

在豆包里输入：
```
你有哪些skill？列出已安装的skill
```

看到对应的skill就说明安装成功。

### 更新Skill

```bash
cd D:\labthink
git pull
install-industry-solution-ppt.bat   # 重新运行对应安装脚本
```

然后重启豆包。

> 详细说明见 [同事使用指南](USAGE.md) | [快速安装卡片](QUICKSTART.md)

## 📖 Skill详细说明

### industry-solution-ppt — 行业解决方案PPT制作（通用版）

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

### logo-wall — 企业Logo搜集与客户墙排版

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

### labthink-gravimetric-ppt — 兰光重量分析产品行业方案PPT（专业版）

**功能**：济南兰光重量分析产品（C840蒸发残渣/C860灼烧残渣/C870干燥失重）行业解决方案PPT制作，内置四套已验证版式。

**核心特性**：
- 四套版式可选：A深蓝金（默认）/ B墨绿金 / C米白深蓝金 / D蓝青金
- 12个行业知识文件：医药/食品/化工/环境/冶金/建材/橡胶/塑料/烟草/饲料/造纸/能源
- 49家医药客户Logo资产内置
- 跨行业术语对照表，避免术语混用
- 飞书知识库标准检索

**使用方法**：
```
做一份食品行业的重量分析解决方案PPT，用版式A
```

## 📁 目录结构

```
labthink/
├── README.md                              # 本文件
├── install-all.bat                        # 全部安装（可选择）
├── install-all.sh                         # Mac/Linux全部安装
├── install-industry-solution-ppt.bat      # 单独安装 industry-solution-ppt
├── install-logo-wall.bat                  # 单独安装 logo-wall
├── install-labthink-gravimetric-ppt.bat   # 单独安装 labthink-gravimetric-ppt
├── config.example.yaml                    # 配置模板
├── .gitignore
└── skills/
    ├── industry-solution-ppt/
    │   ├── README.md                      # 单独说明
    │   ├── SKILL.md                       # 主流程
    │   ├── references/                    # 12个行业知识文件 + 结构模板
    │   ├── scripts/                       # 关键词扫描 + logo工具链
    │   └── assets/
    │       ├── templates/                 # 制药行业V1.6模板
    │       └── logo-wall/                 # 客户墙资产
    ├── logo-wall/
    │   ├── README.md                      # 单独说明
    │   ├── SKILL.md                       # 主流程（要求先提供49家企业名称）
    │   ├── references/                    # 设计原则 + 排错指南
    │   ├── scripts/                       # 7个logo工具脚本
    │   └── assets/                        # 示例logo + 模板
    └── labthink-gravimetric-ppt/
        ├── README.md                      # 单独说明
        ├── SKILL.md                       # 主流程
        ├── references/                    # 行业知识 + 版式设计 + 术语对照
        ├── scripts/                       # 工具脚本
        └── assets/                        # 模板 + logo资产
```

## 🔧 依赖环境

- 豆包专业版
- 飞书连接器授权（lark-cli）
- Python 3.x + lxml库
- Git（用于更新skill）

## 🤝 贡献指南

1. 在`skills/`下新建skill目录
2. 包含`SKILL.md`（必须有name和description字段）
3. 创建对应的`install-<skill-name>.bat`单独安装脚本
4. 在本README的Skill列表中添加条目
5. 提交PR或直接推送

## 🏷️ 仓库维护

### 设置仓库描述和主题标签

在GitHub仓库页面（https://github.com/zonrin-lc/labthink）点击右上角齿轮图标设置：

- **Description（描述）**：济南兰光机电技术有限公司内部豆包Skill集合，包含行业解决方案PPT制作、企业Logo墙生成等工具
- **Topics（主题标签）**：`doubao` `skill` `ppt` `labthink` `automation` `python` `feishu` `lark`

## 📄 许可证

内部使用，禁止公开分发。企业logo和客户名单涉及商标权和商业机密，仅限授权人员使用。
