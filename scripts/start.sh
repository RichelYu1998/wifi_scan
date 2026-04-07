#!/bin/bash
# WiFi Scanner and Optimization Tool - Linux/macOS Startup Script
# Version: v2.0.0
# Update Date: 2026-03-29

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Change to project root directory (parent of scripts)
cd "$SCRIPT_DIR/.."

# Set environment variables for proper encoding
export PYTHONIOENCODING=utf-8
export LANG=en_US.UTF-8

echo "============================================================"
echo "WiFi扫描与优化工具 - Linux/macOS启动脚本"
echo "============================================================"
echo

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
    echo "[信息] 未检测到虚拟环境，使用系统Python"
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
        echo "  CentOS/RHEL: sudo yum install python3"
        echo "  Arch Linux: sudo pacman -S python"
    fi
    echo "  从官网下载: https://www.python.org/downloads/"
    echo
    exit 1
fi

# 显示Python版本信息
echo "[信息] 当前Python环境:"
$PYTHON_EXE --version
echo

# 检查依赖库是否安装
echo "[信息] 检查依赖库..."

# 检查geopy
if ! $PYTHON_EXE -c "import geopy" &> /dev/null; then
    echo "[警告] geopy未安装，正在安装..."
    $PYTHON_EXE -m pip install geopy
fi

# 检查psutil
if ! $PYTHON_EXE -c "import psutil" &> /dev/null; then
    echo "[警告] psutil未安装，正在安装..."
    $PYTHON_EXE -m pip install psutil
fi

# 检查requests
if ! $PYTHON_EXE -c "import requests" &> /dev/null; then
    echo "[警告] requests未安装，正在安装..."
    $PYTHON_EXE -m pip install requests
fi

echo
echo "============================================================"
echo "正在启动WiFi扫描与优化工具..."
echo "============================================================"
echo

# Display function menu
menu() {
    echo "============================================================"
    echo "请选择功能:"
    echo "============================================================"
    echo "1. WiFi网络扫描"
    echo "2. 硬件信息检测"
    echo "3. 投影仪推荐"
    echo "4. 交互式投影仪推荐"
    echo "5. 完整系统测试"
    echo "6. 更新投影仪数据库"
    echo "7. 更新硬件数据库"
    echo "8. 更新硬件数据（网卡、GPU、投影仪）"
    echo "9. JSON文件管理"
    echo "10. 自定义参数运行"
    echo "0. 退出程序"
    echo "============================================================"
    read -p "请选择功能 (0-10): " choice
    echo
}

# Main loop
while true; do
    menu
    
    # Execute corresponding function based on user selection
    case $choice in
        1)
            echo "[信息] 启动WiFi网络扫描..."
            $PYTHON_EXE wifi_scan.py
            ;;
        2)
            echo "[信息] 启动硬件信息检测..."
            $PYTHON_EXE wifi_scan.py --hardware
            ;;
        3)
            echo "[信息] 启动投影仪推荐..."
            $PYTHON_EXE wifi_scan.py --projector
            ;;
        4)
            echo "[信息] 启动交互式投影仪推荐..."
            $PYTHON_EXE wifi_scan.py --interactive
            ;;
        5)
            echo "[信息] 启动完整系统测试..."
            $PYTHON_EXE wifi_scan.py --all-in-one
            ;;
        6)
            echo "[信息] 更新投影仪数据库..."
            $PYTHON_EXE wifi_scan.py --projector --update-projector-db
            ;;
        7)
            echo "[信息] 更新硬件性能数据库..."
            $PYTHON_EXE wifi_scan.py --hardware --update-hardware-db
            ;;
        8)
            echo "[信息] 更新硬件数据（网卡、GPU、投影仪）..."
            $PYTHON_EXE wifi_scan.py --update-mapping
            ;;
        9)
            echo "[信息] JSON文件管理..."
            echo
            echo "请选择JSON管理功能:"
            echo "1. 显示JSON文件统计"
            echo "2. 重新组织JSON文件"
            echo "3. 显示分类规则"
            read -p "请选择 (1-3): " json_choice
            
            case $json_choice in
                1)
                    $PYTHON_EXE wifi_scan.py --json-stats
                    ;;
                2)
                    $PYTHON_EXE wifi_scan.py --organize-json
                    ;;
                3)
                    $PYTHON_EXE wifi_scan.py --show-json-rules
                    ;;
                *)
                    echo "[错误] 无效的选择"
                    ;;
            esac
            ;;
        10)
            echo "[信息] 使用自定义参数运行"
            echo
            echo "可用参数:"
            echo "   --export PATH       导出CSV文件 (例如: ./wifi_report.csv)"
            echo "   --debug             显示调试信息"
            echo "   --hardware           硬件检测"
            echo "   --projector          投影仪推荐"
            echo "   --update-projector-db 更新投影仪数据库"
            echo "   --update-hardware-db 更新硬件数据库"
            echo "   --budget RANGE       投影仪预算范围 (例如: 3000-8000)"
            echo "   --brand BRAND        投影仪品牌偏好 (例如: 极米,坚果,当贝)"
            echo "   --resolution RES      投影仪分辨率偏好 (例如: 4K,1080P)"
            echo "   --all-in-one        运行完整系统测试"
            echo "   --json-stats        显示JSON文件统计"
            echo "   --organize-json     重新组织JSON文件"
            echo "   --show-json-rules   显示JSON分类规则"
            echo
            read -p "请输入参数 (例如: --hardware --debug): " custom_params
            if [ -z "$custom_params" ]; then
                echo "[错误] 未输入参数"
            else
                $PYTHON_EXE wifi_scan.py $custom_params
            fi
            ;;
        0)
            echo "[信息] 退出程序"
            exit 0
            ;;
        *)
            echo "[错误] 无效的选择"
            ;;
    esac
    
    echo
    echo "============================================================"
    echo "[成功] 程序执行完成"
    echo "============================================================"
    echo
    read -p "按回车键继续..."
    echo
done