@echo off
chcp 65001 >nul
title WiFi信道扫描工具 - 跨平台测试

REM 设置UTF-8编码环境
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo ========================================
echo     WiFi信道扫描工具 - 跨平台测试
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

echo ✅ Python环境检测通过
echo.

REM 运行跨平台测试
python test_cross_platform.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ 跨平台测试通过！
) else (
    echo.
    echo ❌ 跨平台测试失败
)

echo.
echo 📋 测试完成
echo.
pause