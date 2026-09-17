@echo off
chcp 65001 >nul
echo ========================================
echo 安装 labthink-gravimetric-ppt Skill
echo ========================================
echo.

set USER_SKILLS_DIR=%LOCALAPPDATA%\Doubao\User Data\Default\.doubao\agent_mode\workspace\.user_skills
set SKILL_DIR=%~dp0skills\labthink-gravimetric-ppt

echo 目标目录: %USER_SKILLS_DIR%
echo.

if not exist "%USER_SKILLS_DIR%" (
    echo 创建用户技能目录...
    mkdir "%USER_SKILLS_DIR%"
)

echo 安装 labthink-gravimetric-ppt...
xcopy /E /I /Y "%SKILL_DIR%" "%USER_SKILLS_DIR%\labthink-gravimetric-ppt" >nul
if %errorlevel% equ 0 (
    echo   ✓ labthink-gravimetric-ppt 安装成功
) else (
    echo   ✗ labthink-gravimetric-ppt 安装失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo Skill名称: labthink-gravimetric-ppt
echo 功能: 济南兰光重量分析产品（C840/C860/C870）行业解决方案PPT制作
echo.
echo 使用方法:
echo   1. 重启豆包
echo   2. 输入"做一份XX行业的重量分析解决方案PPT"
echo   3. 选择版式（A=深蓝金默认 / B=墨绿金 / C=米白深蓝金 / D=蓝青金）
echo.
echo 内置能力:
echo   - 12个行业知识文件（医药/食品/化工/冶金/环保/建材/橡胶/塑料/烟草/饲料/造纸/能源）
echo   - 4套已验证版式
echo   - 49家医药客户Logo资产
echo   - 跨行业术语对照表
echo   - 飞书知识库标准检索
echo.
echo 依赖:
echo   - 飞书连接器授权（读取行业标准表、检测报告库）
echo   - Python 3.x + lxml库
echo.
echo 详细说明: 见 skills\labthink-gravimetric-ppt\README.md
echo.

pause
