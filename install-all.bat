@echo off
chcp 65001 >nul
echo ========================================
echo Labthink 豆包Skill集合 - 一键安装
echo ========================================
echo.

set USER_SKILLS_DIR=%LOCALAPPDATA%\Doubao\User Data\Default\.doubao\agent_mode\workspace\.user_skills
set SKILLS_DIR=%~dp0skills

echo 目标目录: %USER_SKILLS_DIR%
echo.

if not exist "%USER_SKILLS_DIR%" (
    echo 创建用户技能目录...
    mkdir "%USER_SKILLS_DIR%"
)

echo 安装 industry-solution-ppt...
xcopy /E /I /Y "%SKILLS_DIR%\industry-solution-ppt" "%USER_SKILLS_DIR%\industry-solution-ppt" >nul
if %errorlevel% equ 0 (echo   ✓ industry-solution-ppt 安装成功) else (echo   ✗ industry-solution-ppt 安装失败)

echo 安装 logo-wall...
xcopy /E /I /Y "%SKILLS_DIR%\logo-wall" "%USER_SKILLS_DIR%\logo-wall" >nul
if %errorlevel% equ 0 (echo   ✓ logo-wall 安装成功) else (echo   ✗ logo-wall 安装失败)

echo 安装 labthink-bid-review-portable...
xcopy /E /I /Y "%SKILLS_DIR%\labthink-bid-review-portable" "%USER_SKILLS_DIR%\labthink-bid-review-portable" >nul
if %errorlevel% equ 0 (echo   ✓ labthink-bid-review-portable 安装成功) else (echo   ✗ labthink-bid-review-portable 安装失败)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 请重启豆包后使用。
echo.
echo 已安装的Skill:
echo   1. industry-solution-ppt - 行业解决方案PPT制作
echo   2. logo-wall - 企业Logo搜集与客户墙排版
echo   3. labthink-bid-review-portable - 投标响应文件审阅复核
echo.
echo 注意事项:
echo   1. 请确保已配置飞书连接器授权
echo   2. 请复制config.example.yaml为config.yaml并填写配置
echo   3. logo资产需向管理员获取后放入skills/logo-wall/assets目录
echo.

pause
