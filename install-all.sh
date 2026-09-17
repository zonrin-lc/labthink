#!/bin/bash
echo "========================================"
echo "Labthink 豆包Skill集合 - 一键安装"
echo "========================================"
echo ""

USER_SKILLS_DIR="$HOME/.doubao/agent_mode/workspace/.user_skills"
SKILLS_DIR="$(dirname "$0")/skills"

echo "目标目录: $USER_SKILLS_DIR"
echo ""

if [ ! -d "$USER_SKILLS_DIR" ]; then
    echo "创建用户技能目录..."
    mkdir -p "$USER_SKILLS_DIR"
fi

echo "安装 labthink-industry-solution-ppt..."
cp -R "$SKILLS_DIR/labthink-industry-solution-ppt" "$USER_SKILLS_DIR/"
if [ $? -eq 0 ]; then echo "  ✓ labthink-industry-solution-ppt 安装成功"; else echo "  ✗ labthink-industry-solution-ppt 安装失败"; fi

echo "安装 labthink-logo-wall..."
cp -R "$SKILLS_DIR/labthink-logo-wall" "$USER_SKILLS_DIR/"
if [ $? -eq 0 ]; then echo "  ✓ labthink-logo-wall 安装成功"; else echo "  ✗ labthink-logo-wall 安装失败"; fi

echo "安装 labthink-bid-review-portable..."
cp -R "$SKILLS_DIR/labthink-bid-review-portable" "$USER_SKILLS_DIR/"
if [ $? -eq 0 ]; then echo "  ✓ labthink-bid-review-portable 安装成功"; else echo "  ✗ labthink-bid-review-portable 安装失败"; fi

echo ""
echo "========================================"
echo "安装完成！"
echo "========================================"
echo ""
echo "请重启豆包后使用。"
echo ""
echo "已安装的Skill:"
echo "  1. labthink-industry-solution-ppt - 行业解决方案PPT制作"
echo "  2. labthink-logo-wall - 企业Logo搜集与客户墙排版"
echo "  3. labthink-bid-review-portable - 投标响应文件审阅复核"
echo ""
echo "注意事项:"
echo "  1. 请确保已配置飞书连接器授权"
echo "  2. 请复制config.example.yaml为config.yaml并填写配置"
echo "  3. logo资产需向管理员获取后放入skills/labthink-logo-wall/assets目录"
echo ""
