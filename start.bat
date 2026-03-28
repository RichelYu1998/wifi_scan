@echo off
REM WiFi扫描与投影仪推荐系统 - Windows启动脚本
REM 集成版 - 支持虚拟环境检测

REM 设置代码页为UTF-8
chcp 65001 >nul 2>&1

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 设置环境变量确保中文正确显示
set PYTHONIOENCODING=utf-8

REM 检测虚拟环境
set VENV_DETECTED=false
set PYTHON_EXE=python

if exist ".venv\Scripts\python.exe" (
    set PYTHON_EXE=.venv\Scripts\python.exe
    set VENV_DETECTED=true
    echo [信息] 检测到虚拟环境: .venv
) else if exist "venv\Scripts\python.exe" (
    set PYTHON_EXE=venv\Scripts\python.exe
    set VENV_DETECTED=true
    echo [信息] 检测到虚拟环境: venv
) else if exist "env\Scripts\python.exe" (
    set PYTHON_EXE=env\Scripts\python.exe
    set VENV_DETECTED=true
    echo [信息] 检测到虚拟环境: env
) else (
    echo [信息] 未检测到虚拟环境
    set PYTHON_EXE=python
)

echo.

REM 检查Python是否可用
%PYTHON_EXE% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Python不可用，请先安装Python 3.7+
    echo [信息] 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM 显示Python版本信息
echo [信息] 当前Python环境:
%PYTHON_EXE% --version
echo.

REM 运行集成系统
%PYTHON_EXE% integrated_system.py

REM 检查执行结果
if %errorlevel% neq 0 (
    echo.
    echo [错误] 程序执行失败，错误代码: %errorlevel%
    echo.
    echo [信息] 故障排除建议:
    echo   1. 检查Python版本是否为3.7+
    echo   2. 运行: pip install psutil requests 安装依赖
    echo   3. 查看README.md获取详细帮助
    echo.
    pause
    exit /b %errorlevel%
)

REM 暂停以查看输出
pause