@echo off
chcp 65001 >nul
echo ========================================
echo 行业解决方案PPT Skill 安装脚本
echo ========================================
echo.

set SKILL_NAME=industry-solution-ppt
set USER_SKILLS_DIR=%LOCALAPPDATA%\Doubao\User Data\Default\.doubao\agent_mode\workspace\.user_skills
set TARGET_DIR=%USER_SKILLS_DIR%\%SKILL_NAME%

echo 目标目录: %TARGET_DIR%
echo.

if not exist "%USER_SKILLS_DIR%" (
    echo 创建用户技能目录...
    mkdir "%USER_SKILLS_DIR%"
)

echo 复制Skill文件...
xcopy /E /I /Y "%~dp0*" "%TARGET_DIR%\" >nul

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 安装成功！
    echo ========================================
    echo.
    echo 请重启豆包后使用。
    echo.
    echo 使用方法：在豆包中输入"基于医药行业方案，做一份XX行业的解决方案PPT"
    echo.
    echo 注意事项：
    echo 1. 请确保已配置飞书连接器授权
    echo 2. 请复制config.example.yaml为config.yaml并填写配置
    echo 3. logo资产需向管理员获取后放入assets/logo-wall目录
    echo.
) else (
    echo.
    echo 安装失败，请检查权限后重试。
    echo.
)

pause
