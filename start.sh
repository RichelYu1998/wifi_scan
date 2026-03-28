#!/bin/bash
# WiFi扫描与投影仪推荐系统 - Linux/macOS启动脚本
# 集成版 - 支持虚拟环境检测

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 设置环境变量确保中文正确显示
export PYTHONIOENCODING=utf-8
export LANG=zh_CN.UTF-8

# 检测操作系统
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS_NAME="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS_NAME="Linux"
else
    OS_NAME="Unknown"
fi

echo "[信息] 检测到操作系统: $OS_NAME"

# 检测虚拟环境
VENV_DETECTED=false
PYTHON_EXE="python3"

if [ -f ".venv/bin/python3" ]; then
    PYTHON_EXE=".venv/bin/python3"
    VENV_DETECTED=true
    echo "[信息] 检测到虚拟环境: .venv"
elif [ -f "venv/bin/python3" ]; then
    PYTHON_EXE="venv/bin/python3"
    VENV_DETECTED=true
    echo "[信息] 检测到虚拟环境: venv"
elif [ -f "env/bin/python3" ]; then
    PYTHON_EXE="env/bin/python3"
    VENV_DETECTED=true
    echo "[信息] 检测到虚拟环境: env"
else
    echo "[信息] 未检测到虚拟环境"
    if command -v python3 &> /dev/null; then
        PYTHON_EXE="python3"
    elif command -v python &> /dev/null; then
        PYTHON_EXE="python"
    fi
fi

echo

# 检查Python是否可用
if ! $PYTHON_EXE --version &> /dev/null; then
    echo "[错误] Python不可用，请先安装Python 3.7+"
    echo
    echo "[信息] 推荐安装方式:"
    if [[ "$OS_NAME" == "macOS" ]]; then
        echo "  使用Homebrew安装: brew install python3"
    elif [[ "$OS_NAME" == "Linux" ]]; then
        echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-venv"
    fi
    echo "  从官网下载: https://www.python.org/downloads/"
    echo
    exit 1
fi

# 显示Python版本信息
echo "[信息] 当前Python环境:"
$PYTHON_EXE --version
echo

# 运行集成系统
$PYTHON_EXE integrated_system.py

# 检查执行结果
if [ $? -ne 0 ]; then
    echo
    echo "[错误] 程序执行失败，错误代码: $?"
    echo
    echo "[信息] 故障排除建议:"
    echo "  1. 检查Python版本是否为3.7+"
    echo "  2. 运行: pip install psutil requests 安装依赖"
    echo "  3. 查看README.md获取详细帮助"
    echo
    read -p "按回车键退出..."
    exit 1
fi

echo
echo "[成功] 程序正常退出"