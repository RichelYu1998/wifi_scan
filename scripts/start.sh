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

# Logging functions
log_section() {
    echo ""
    echo "============================================================"
    echo "$1"
    echo "============================================================"
}

log_info() {
    echo "[INFO] $1"
}

log_warn() {
    echo "[WARNING] $1"
}

log_error() {
    echo "[ERROR] $1"
}

# Detect Python environment
detect_python() {
    log_section "🔍 环境检测与配置"
    
    echo "[1/6] 检测Python环境..."
    PYTHON_CMD=""
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        log_info "Python版本：$(python3 --version 2>&1 | awk '{print $2}') (命令: python3)"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        log_info "Python版本：$(python --version 2>&1 | awk '{print $2}') (命令: python)"
    else
        log_error "Python环境检测失败"
        echo ""
        echo "请先安装Python 3.10或更高版本："
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip"
            echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
            echo "  Arch Linux: sudo pacman -S python python-pip"
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            echo "  macOS: brew install python3"
        fi
        return 1
    fi
    
    return 0
}

# Detect virtual environment
detect_venv() {
    echo "[2/6] 检测虚拟环境..."
    
    if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
        log_info "检测到虚拟环境：venv"
        VENV_EXISTS=1
        VENV_PATH="venv"
    elif [ -d ".venv" ] && [ -f ".venv/bin/activate" ]; then
        log_info "检测到虚拟环境：.venv"
        VENV_EXISTS=1
        VENV_PATH=".venv"
    elif [ -d "env" ] && [ -f "env/bin/activate" ]; then
        log_info "检测到虚拟环境：env"
        VENV_EXISTS=1
        VENV_PATH="env"
    else
        log_warn "未检测到虚拟环境"
        echo ""
        log_info "正在自动创建虚拟环境..."
        
        if $PYTHON_CMD -m venv venv; then
            log_info "虚拟环境创建成功：venv"
            VENV_EXISTS=1
            VENV_PATH="venv"
            echo ""
        else
            log_error "虚拟环境创建失败"
            VENV_EXISTS=0
            VENV_PATH=""
            echo ""
        fi
    fi
    
    return 0
}

# Check dependencies
check_dependencies() {
    echo "[3/6] 检测依赖包..."
    
    if [ -n "$VENV_PATH" ]; then
        source "$VENV_PATH/bin/activate"
        
        if $PYTHON_CMD -c "import geopy" &> /dev/null; then
            log_info "geopy依赖正常"
        else
            log_warn "geopy未安装"
        fi
        
        if $PYTHON_CMD -c "import psutil" &> /dev/null; then
            log_info "psutil依赖正常"
        else
            log_warn "psutil未安装"
        fi
        
        if $PYTHON_CMD -c "import requests" &> /dev/null; then
            log_info "requests依赖正常"
        else
            log_warn "requests未安装"
        fi
        
        deactivate
    else
        if $PYTHON_CMD -c "import geopy" &> /dev/null; then
            log_info "geopy依赖正常"
        else
            log_warn "geopy未安装"
        fi
        
        if $PYTHON_CMD -c "import psutil" &> /dev/null; then
            log_info "psutil依赖正常"
        else
            log_warn "psutil未安装"
        fi
        
        if $PYTHON_CMD -c "import requests" &> /dev/null; then
            log_info "requests依赖正常"
        else
            log_warn "requests未安装"
        fi
    fi
    
    return 0
}

# Detect operating system
detect_os() {
    echo "[4/6] 检测操作系统..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS_NAME="macOS"
        log_info "操作系统: macOS"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS_NAME="Linux"
        log_info "操作系统: Linux"
    else
        OS_NAME="Unknown"
        log_warn "操作系统: 未知"
    fi
    
    return 0
}

# Set Python executable
set_python_executable() {
    echo "[5/6] 配置Python环境..."
    
    if [ -n "$VENV_PATH" ]; then
        PYTHON_EXE="$VENV_PATH/bin/python3"
        log_info "使用虚拟环境Python: $PYTHON_EXE"
    else
        PYTHON_EXE="$PYTHON_CMD"
        log_info "使用系统Python: $PYTHON_EXE"
    fi
    
    return 0
}

# Install missing dependencies
install_dependencies() {
    echo "[6/6] 安装缺失的依赖..."
    
    # 使用阿里云镜像加速
    PIP_MIRROR="-i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com"
    
    if [ -n "$VENV_PATH" ]; then
        source "$VENV_PATH/bin/activate"
        
        if ! $PYTHON_CMD -c "import geopy" &> /dev/null; then
            log_info "正在安装geopy（使用阿里云镜像加速）..."
            $PYTHON_CMD -m pip install geopy $PIP_MIRROR
        fi
        
        if ! $PYTHON_CMD -c "import psutil" &> /dev/null; then
            log_info "正在安装psutil（使用阿里云镜像加速）..."
            $PYTHON_CMD -m pip install psutil $PIP_MIRROR
        fi
        
        if ! $PYTHON_CMD -c "import requests" &> /dev/null; then
            log_info "正在安装requests（使用阿里云镜像加速）..."
            $PYTHON_CMD -m pip install requests $PIP_MIRROR
        fi
        
        deactivate
    else
        if ! $PYTHON_CMD -c "import geopy" &> /dev/null; then
            log_info "正在安装geopy（使用阿里云镜像加速）..."
            $PYTHON_CMD -m pip install geopy $PIP_MIRROR
        fi
        
        if ! $PYTHON_CMD -c "import psutil" &> /dev/null; then
            log_info "正在安装psutil（使用阿里云镜像加速）..."
            $PYTHON_CMD -m pip install psutil $PIP_MIRROR
        fi
        
        if ! $PYTHON_CMD -c "import requests" &> /dev/null; then
            log_info "正在安装requests（使用阿里云镜像加速）..."
            $PYTHON_CMD -m pip install requests $PIP_MIRROR
        fi
    fi
    
    log_info "依赖安装完成"
    return 0
}

echo "============================================================"
echo "WiFi扫描与优化工具 - Linux/macOS启动脚本"
echo "============================================================"
echo

# Run environment detection
if ! detect_python; then
    exit 1
fi

detect_venv
check_dependencies
detect_os
set_python_executable
install_dependencies

echo ""
echo "============================================================"
echo "✅ 环境检测完成"
echo "============================================================"
echo ""
echo "当前配置："
echo "  Python命令: $PYTHON_CMD"
echo "  Python可执行文件: $PYTHON_EXE"
echo "  虚拟环境: $([ -n "$VENV_PATH" ] && echo "$VENV_PATH" || echo "未使用")"
echo "  操作系统: $OS_NAME"
echo ""
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