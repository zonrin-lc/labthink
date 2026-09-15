# Labthink 豆包Skill集合

济南兰光机电技术有限公司内部使用的豆包Skill集合，用于提升工作效率。

## 🚀 快速安装（复制这句话发给豆包）

```
帮我安装labthink豆包skill集合：
1. 用git克隆仓库 https://github.com/zonrin-lc/labthink.git 到 D:\labthink
2. 进入目录运行 install-all.bat 安装所有skill
3. 告诉我安装了哪些skill
```

安装完成后**重启豆包**即可使用。

> 详细说明见 [同事使用指南](USAGE.md) | [快速安装卡片](QUICKSTART.md)

## Skill列表

| Skill | 说明 | 状态 |
|---|---|---|
| [industry-solution-ppt](skills/industry-solution-ppt/) | 基于医药行业方案模板，快速生成其他行业（食品/化工/环境等）解决方案PPT | ✅ 可用 |
| [logo-wall](skills/logo-wall/) | 企业Logo搜集与PPT客户墙排版工具（支持49家客户logo墙自动生成） | ✅ 可用 |

## 使用示例

```
基于医药行业方案，帮我做一份食品行业的解决方案PPT
```

```
帮我做一份食品行业49家企业的logo墙PPT
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
        ├── SKILL.md             # 主流程
        ├── references/          # 设计原则 + 排错指南
        ├── scripts/             # 7个logo工具脚本
        └── assets/              # logo资产（需自行获取）
```

## 依赖环境

- 豆包专业版
- 飞书连接器授权（lark-cli）
- Python 3.x + lxml库
- Git（用于更新skill）

## 更新Skill

```bash
cd labthink
git pull
install-all.bat  # 重新安装
```

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
