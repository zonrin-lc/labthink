@echo off
chcp 65001 >nul
echo ========================================
echo Labthink 豆包Skill集合 - 安装程序
echo ========================================
echo.
echo 可用Skill:
echo   1. industry-solution-ppt    - 行业解决方案PPT制作（通用版）
echo   2. logo-wall                 - 企业Logo搜集与客户墙排版
echo   3. labthink-gravimetric-ppt - 兰光重量分析产品行业方案PPT（专业版）
echo.
echo 请选择安装方式:
echo   A. 安装全部Skill
echo   B. 仅安装 industry-solution-ppt
echo   C. 仅安装 logo-wall
echo   D. 仅安装 labthink-gravimetric-ppt
echo   Q. 退出
echo.
set /p choice=请输入选项 (A/B/C/D/Q):

if /i "%choice%"=="A" goto install_all
if /i "%choice%"=="B" goto install_industry
if /i "%choice%"=="C" goto install_logo
if /i "%choice%"=="D" goto install_gravimetric
if /i "%choice%"=="Q" goto end

echo 无效选项，请重新运行
pause
exit /b 1

:install_all
echo.
echo 开始安装全部Skill...
call :install_skill industry-solution-ppt
call :install_skill logo-wall
call :install_skill labthink-gravimetric-ppt
goto finish

:install_industry
call :install_skill industry-solution-ppt
goto finish

:install_logo
call :install_skill logo-wall
goto finish

:install_gravimetric
call :install_skill labthink-gravimetric-ppt
goto finish

:install_skill
set SKILL_NAME=%~1
set USER_SKILLS_DIR=%LOCALAPPDATA%\Doubao\User Data\Default\.doubao\agent_mode\workspace\.user_skills
set SKILL_DIR=%~dp0skills\%SKILL_NAME%

if not exist "%USER_SKILLS_DIR%" (
    mkdir "%USER_SKILLS_DIR%"
)

echo 安装 %SKILL_NAME%...
xcopy /E /I /Y "%SKILL_DIR%" "%USER_SKILLS_DIR%\%SKILL_NAME%" >nul
if %errorlevel% equ 0 (
    echo   ✓ %SKILL_NAME% 安装成功
) else (
    echo   ✗ %SKILL_NAME% 安装失败
)
exit /b 0

:finish
echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 请重启豆包后使用。
echo.
echo 各Skill详细说明:
echo   - skills\industry-solution-ppt\README.md
echo   - skills\logo-wall\README.md
echo   - skills\labthink-gravimetric-ppt\README.md
echo.
echo 注意事项:
echo   1. 请确保已配置飞书连接器授权
echo   2. logo-wall内置示例Logo，实际使用需替换为真实企业Logo
echo   3. labthink-gravimetric-ppt内置49家医药客户Logo资产
echo.

pause
:end
