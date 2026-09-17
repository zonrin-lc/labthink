@echo off
chcp 65001 >nul
echo ========================================
echo 安装 logo-wall Skill
echo ========================================
echo.

set USER_SKILLS_DIR=%LOCALAPPDATA%\Doubao\User Data\Default\.doubao\agent_mode\workspace\.user_skills
set SKILL_DIR=%~dp0skills\logo-wall

echo 目标目录: %USER_SKILLS_DIR%
echo.

if not exist "%USER_SKILLS_DIR%" (
    echo 创建用户技能目录...
    mkdir "%USER_SKILLS_DIR%"
)

echo 安装 logo-wall...
xcopy /E /I /Y "%SKILL_DIR%" "%USER_SKILLS_DIR%\logo-wall" >nul
if %errorlevel% equ 0 (
    echo   ✓ logo-wall 安装成功
) else (
    echo   ✗ logo-wall 安装失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo Skill名称: logo-wall
echo 功能: 企业Logo搜集与客户墙PPT排版
echo.
echo 使用方法:
echo   1. 重启豆包
echo   2. 输入"帮我做客户墙/Logo墙"
echo   3. 提供49家企业名称（必须先提供名单）
echo.
echo 依赖:
echo   - Python 3.x + requests/beautifulsoup4/lxml/pillow/python-pptx
echo   - Playwright + Chromium（用于浏览器抓取Logo）
echo.
echo 注意:
echo   - 内置49个示例Logo占位图，实际使用需替换为真实企业Logo
echo   - 必须先提供49家企业名称，skill不会自行编造客户名单
echo.
echo 详细说明: 见 skills\logo-wall\README.md
echo.

pause
