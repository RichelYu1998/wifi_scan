@echo off
chcp 65001 >nul
title WiFi信道扫描工具

echo ========================================
echo      WiFi信道扫描工具 - Windows版本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到Python，请先安装Python 3.6+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
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

python wifi_scan.py

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