#!/bin/bash

# WiFi信道扫描工具 - Linux版本

echo "========================================"
echo "     WiFi信道扫描工具 - Linux版本"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3，请先安装Python 3.6+"
    echo "Ubuntu/Debian: sudo apt install python3"
    echo "CentOS/RHEL: sudo yum install python3"
    exit 1
fi

# 检查是否以root权限运行（Linux下需要root权限扫描WiFi）
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  警告：建议以root权限运行以获得最佳扫描效果"
    echo "请使用：sudo ./wifi_scan.sh"
    echo ""
fi

# 运行WiFi扫描程序
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