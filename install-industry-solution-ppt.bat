@echo off
chcp 65001 >nul
echo ========================================
echo 安装 industry-solution-ppt Skill
echo ========================================
echo.

set USER_SKILLS_DIR=%LOCALAPPDATA%\Doubao\User Data\Default\.doubao\agent_mode\workspace\.user_skills
set SKILL_DIR=%~dp0skills\industry-solution-ppt

echo 目标目录: %USER_SKILLS_DIR%
echo.

if not exist "%USER_SKILLS_DIR%" (
    echo 创建用户技能目录...
    mkdir "%USER_SKILLS_DIR%"
)

echo 安装 industry-solution-ppt...
xcopy /E /I /Y "%SKILL_DIR%" "%USER_SKILLS_DIR%\industry-solution-ppt" >nul
if %errorlevel% equ 0 (
    echo   ✓ industry-solution-ppt 安装成功
) else (
    echo   ✗ industry-solution-ppt 安装失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo Skill名称: industry-solution-ppt
echo 功能: 基于企业参考材料制作面向特定行业的解决方案PPT
echo.
echo 使用方法:
echo   1. 重启豆包
echo   2. 输入"帮我做一份XX行业解决方案PPT"
echo   3. 提供企业材料（公司介绍、产品手册、检测报告、行业标准等）
echo.
echo 依赖:
echo   - 飞书连接器授权（读取行业标准表、检测报告库）
echo   - Python 3.x + lxml库
echo.
echo 详细说明: 见 skills\industry-solution-ppt\README.md
echo.

pause
