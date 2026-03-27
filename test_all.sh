#!/bin/bash

# WiFi信道扫描工具 - 跨平台测试脚本

echo "========================================"
echo "     WiFi信道扫描工具 - 跨平台测试"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3，请先安装Python 3.6+"
    echo "Ubuntu/Debian: sudo apt install python3"
    echo "CentOS/RHEL: sudo yum install python3"
    echo "macOS: brew install python3"
    exit 1
fi

echo "✅ Python环境检测通过"
echo ""

# 运行跨平台测试
python3 test_cross_platform.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 跨平台测试通过！"
else
    echo ""
    echo "❌ 跨平台测试失败"
fi

echo ""
echo "📋 测试完成"
echo ""