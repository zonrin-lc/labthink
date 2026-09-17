@echo off
chcp 65001 >nul
echo ========================================
echo 安装 labthink-bid-review-portable Skill
echo ========================================
echo.

set USER_SKILLS_DIR=%LOCALAPPDATA%\Doubao\User Data\Default\.doubao\agent_mode\workspace\.user_skills
set SKILL_DIR=%~dp0skills\labthink-bid-review-portable

echo 目标目录: %USER_SKILLS_DIR%
echo.

if not exist "%USER_SKILLS_DIR%" (
    echo 创建用户技能目录...
    mkdir "%USER_SKILLS_DIR%"
)

echo 安装 labthink-bid-review-portable...
xcopy /E /I /Y "%SKILL_DIR%" "%USER_SKILLS_DIR%\labthink-bid-review-portable" >nul
if %errorlevel% equ 0 (
    echo   ✓ labthink-bid-review-portable 安装成功
) else (
    echo   ✗ labthink-bid-review-portable 安装失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo Skill名称: labthink-bid-review-portable
echo 功能: 投标响应文件审阅复核（可移植版，零依赖）
echo.
echo 使用方法:
echo   1. 重启豆包
echo   2. 输入"帮我审阅这份投标响应文件"
echo   3. 上传.docx投标文件
echo.
echo 特点:
echo   - 零依赖：仅用Python标准库，无需pip install
echo   - 只读检查：不修改原文件，输出HTML核查报告
echo   - 围标/串标检测：单文件自查 + 多文件横向对比
echo   - 评标办法重估：按评标办法抽取结构化数据并复核得分
echo.
echo 依赖:
echo   - Python 3.8+（仅标准库，无需安装第三方包）
echo.
echo 详细说明: 见 skills\labthink-bid-review-portable\README.md
echo.

pause
