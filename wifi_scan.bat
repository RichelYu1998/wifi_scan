@echo off
chcp 65001 >nul
title WiFi信道扫描工具

REM 设置UTF-8编码环境
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo ========================================
echo      WiFi信道扫描工具 - Windows版本
echo ========================================
echo.

REM 检查虚拟环境是否存在
if exist ".venv\Scripts\python.exe" (
    echo ✅ 检测到虚拟环境，使用虚拟环境中的Python
    set PYTHON_PATH=.venv\Scripts\python.exe
) else (
    echo ⚠️  未找到虚拟环境，尝试使用系统Python
    REM 检查Python是否安装
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ 错误：未找到Python，请先安装Python 3.6+
        echo 下载地址：https://www.python.org/downloads/
        echo.
        echo 或者运行以下命令创建虚拟环境：
        echo python -m venv .venv
        echo .venv\Scripts\activate
        echo pip install -r requirements.txt
        pause
        exit /b 1
    )
    set PYTHON_PATH=python
)

REM 检查是否以管理员权限运行
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  警告：建议以管理员权限运行以获得最佳扫描效果
    echo 右键点击 -> 以管理员身份运行
    echo.
)

REM 运行WiFi扫描程序
echo 🚀 开始WiFi信道扫描...
echo.

REM 设置UTF-8编码环境并运行Python程序
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

REM 检查是否传递了--debug参数
if "%1"=="--debug" (
    %PYTHON_PATH% wifi_scan.py --debug
) else (
    %PYTHON_PATH% wifi_scan.py
)

if %errorlevel% equ 0 (
    echo.
    echo ✅ 扫描完成！
) else (
    echo.
    echo ❌ 扫描过程中出现错误
)

echo.
echo 📁 日志文件保存在：wifi_logs 目录
echo.
pause