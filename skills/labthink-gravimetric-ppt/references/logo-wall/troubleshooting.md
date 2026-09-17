# Troubleshooting — Logo 搜集实战踩坑

按症状索引。

## 抓取阶段

| 症状 | 原因 | 处理 |
|---|---|---|
| `requests` 返回 200 但找不到 logo img | JS 渲染站点 | 用 `browser_fetch.py`（Playwright） |
| 直接下载 logo URL 返回 HTML "Request Rejected" | WAF 拦热链 | `browser_fetch.py --fetch-img <src子串>`，在页面上下文里 fetch |
| 截图全是 cookie 弹窗 | GDPR/国内 cookie 横幅 | `--click 全拒绝`（或页面上的实际按钮文本） |
| 官网连接重置 / 空响应 | 站点故障 | 改用百科（百度百科等）高清词条首图，并在交付备注中说明 |
| 抓到的是"神州数码"等陌生公司 | 域名张冠李戴 | 重新搜索确认官网；抓取后必须目检核对公司名 |
| 抓到装饰线/小图标 | 选择器太宽 | 浏览器模式会 dump `candidates/*_strip.png`，人工裁剪正确区域 |
| 页眉同时有母公司和子公司标志 | 集团站 | 裁掉母公司部分，只留用户点名的主体 |

## 图像阶段

| 症状 | 原因 | 处理 |
|---|---|---|
| PNG 打开全空白 | 白色版 logo（用于深色页眉） | `normalize_logos.py` 的 `recolor` 动作重着色为品牌色；SVG 则先把 `fill="#FFFFFF"` 改成品牌色再渲染 |
| SVG 在 Windows 上无法转 PNG（cairosvg 报 libcairo） | 缺 cairo 动态库 | 用 `svg_to_png.py`（Playwright 渲染，无需 cairo） |
| 截图带灰/蓝色底块 | 页眉底色被一起截入 | 优先找透明版资源；或用元素级 `omit_background` 截图；最后用 PIL 把接近底色的像素置透明 |
| 含"CCTV 民族匠心品牌"、股票代码、电话等杂项 | 抓的是组合横幅 | 裁掉，只留标志本体（可保留官方 slogan 如"健康世界"） |
| 标志模糊 | 源图太小 | 用 `device_scale_factor=3` 重截，或找 `@2x` 资源；AI 超分仅作最后手段 |
| 透明底 PNG 转 RGB 后变黑底 | alpha 通道被直接丢弃 | 先合成到白色背景再处理：`bg.alpha_composite(im)`，然后再裁边/保存 |
| 深色底+白标，找不到彩色版 | 官网只发布反白版 | 取白色图稿的亮度作 alpha，按品牌色（官网 CSS 出现次数最多的主题色）重着色 |
| 拼图上少了几张图 | 文件是 `.jpeg`，glob 只匹配了 `.jpg/.png` | `make_sheet.py` 已修复；自己写 glob 时记得 `*.jpeg` |
| 官网 SVG 链接 404 | 猜的 URL 路径不对 | 抓首页 HTML，从 `src/href` 里找真实资源地址（常在 OSS 域名下） |

## 排版阶段

| 症状 | 原因 | 处理 |
|---|---|---|
| 格子统一但仍显乱 | 白边未裁 | 先 `normalize_logos.py` 裁边 |
| 方形标明显"大一圈" | 视觉重量差异 | `adjust.csv` 加 `weight,0.85` |
| 个别标带深色底块破坏整墙 | 违反底色统一规则 | 换白底/透明底彩色版；白色图稿按品牌色重着色，不要用 PS 橡皮敷衍 |
| 用户已有排好版的 PPT，只需换图 | — | 用 `refill_template.py`：删除全部图片形状→按尺寸定位单元格→行主序匹配名单→fit-inside 插入；另存新文件 |
| 需要最高质量的"官方认可"版本 | 用户自己的旧 PPT 就是最佳来源 | 解压旧 pptx，`ppt/media/` 里就是用户已接受的版本，按白底合成+裁边后可直接复用 |
| 单元格识别不到或数量对不上 | 模板格子尺寸/容差不符 | 调 `--cellw/--cellh/--tol`；脚本在 格子数 ≠ Logo 数 时会中止并报出两个数字 |
