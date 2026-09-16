# Logo资产说明

本目录包含示例logo资产（假logo占位，非真实企业），用于演示和测试。

## 文件说明

| 文件 | 说明 |
|---|---|
| `template.pptx` | 客户墙模板PPT（16:9，标题+49单元格，7x7布局） |
| `logos/` | 49个示例占位logo（灰色圆角矩形+"Logo 01"文字） |
| `order.txt` | 示例排序文件（49个示例企业） |

## 使用方法

实际使用时，用真实企业logo替换 `logos/` 目录下的图片，文件名保持 `01_企业名.png` 格式，并更新 `order.txt` 为真实企业名称。

**一键重建示例客户墙：**
```bash
python scripts/normalize_logos.py assets/logos --outdir logos_fit --maxw 1200 --maxh 400
python scripts/refill_template.py assets/template.pptx logos_fit assets/order.txt 客户Logo墙.pptx
```

## 注意事项

- 示例logo为占位图，不代表任何真实企业
- 真实企业logo涉及商标权，仅限内部使用
- 严格按用户名单顺序排列，不重排
- 必须做视觉QA后再交付
