#!/bin/bash

echo "===================================="
echo "投影仪推荐系统 - Linux/macOS启动脚本"
echo "===================================="
echo ""

python3 -m venv .venv 2>/dev/null || echo "虚拟环境已存在或创建失败，继续..."

source .venv/bin/activate

echo ""
echo "正在安装依赖..."
pip install -q -r requirements.txt

echo ""
echo "===================================="
echo "选择功能:"
echo "===================================="
echo "1. 投影仪推荐器（交互式）"
echo "2. 投影仪图表生成器"
echo "3. 价格数据更新"
echo "4. 完整流程（更新+推荐+图表）"
echo "5. 运行测试"
echo "6. 退出"
echo "===================================="
echo ""

read -p "请选择功能 (1-6): " choice

case $choice in
    1)
        echo ""
        echo "启动投影仪推荐器..."
        python projector_recommender.py
        ;;
    2)
        echo ""
        echo "启动图表生成器..."
        python projector_chart_generator.py
        ;;
    3)
        echo ""
        echo "更新价格数据..."
        python projector_price_updater.py
        ;;
    4)
        echo ""
        echo "执行完整流程..."
        echo ""
        echo "[1/3] 更新价格数据..."
        python projector_price_updater.py
        echo ""
        echo "[2/3] 生成推荐图表..."
        python projector_chart_generator.py
        echo ""
        echo "[3/3] 完成！"
        ;;
    5)
        echo ""
        echo "运行测试..."
        python test_all.py
        ;;
    6)
        echo ""
        echo "退出..."
        exit 0
        ;;
    *)
        echo ""
        echo "无效选择，退出..."
        exit 1
        ;;
esac

echo ""
echo "===================================="
echo "执行完成！"
echo "===================================="
echo ""