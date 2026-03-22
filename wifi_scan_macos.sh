#!/bin/bash

# WiFi信道扫描工具 - macOS版本

echo "========================================"
echo "     WiFi信道扫描工具 - macOS版本"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3，请先安装Python 3.6+"
    echo "推荐使用Homebrew安装：brew install python3"
    echo "或从官网下载：https://www.python.org/downloads/"
    exit 1
fi

# 检查airport命令是否可用
airport_paths=(
    "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
    "/usr/local/bin/airport"
)

airport_cmd=""
for path in "${airport_paths[@]}"; do
    if [ -f "$path" ]; then
        airport_cmd="$path"
        break
    fi
done

if [ -z "$airport_cmd" ]; then
    echo "⚠️  提示：未找到airport命令，尝试创建符号链接..."
    sudo ln -s /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport /usr/local/bin/airport 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ airport命令已启用"
        airport_cmd="/usr/local/bin/airport"
    else
        echo "⚠️  无法创建符号链接，请手动启用WiFi扫描权限"
        echo "系统偏好设置 > 安全性与隐私 > 隐私 > 定位服务"
    fi
fi

# 检查WiFi扫描权限
echo ""
echo "🔍 检查WiFi扫描权限..."
if [ -n "$airport_cmd" ]; then
    $airport_cmd -s >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "⚠️  警告：WiFi扫描权限可能受限"
        echo "请确保已启用定位服务权限"
        echo "系统偏好设置 > 安全性与隐私 > 隐私 > 定位服务"
    fi
fi

# 运行WiFi扫描程序
echo ""
echo "🚀 开始WiFi信道扫描..."
echo ""

python3 Channel.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 扫描完成！"
else
    echo ""
    echo "❌ 扫描过程中出现错误"
fi

echo ""
echo "📁 日志文件保存在：wifi_logs 目录"
echo ""
echo "💡 提示：如果扫描结果不准确，请检查WiFi权限设置"
echo ""

# 等待用户按键（macOS不需要pause）
read -p "按回车键退出..."