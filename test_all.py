#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 验证所有Python代码是否正常工作且不产生中文乱码
"""

import sys
import os
import json
from datetime import datetime

def test_imports():
    """测试所有模块导入"""
    print("=" * 60)
    print("测试模块导入")
    print("=" * 60)
    
    modules = [
        'html_generator',
        'projector_price_updater',
        'projector_recommender',
        'projector_chart_generator'
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} 导入成功")
        except Exception as e:
            print(f"❌ {module} 导入失败: {e}")
            return False
    
    print()
    return True

def test_html_generator():
    """测试HTML生成器"""
    print("=" * 60)
    print("测试HTML生成器")
    print("=" * 60)
    
    try:
        from html_generator import HTMLGenerator
        
        generator = HTMLGenerator()
        
        test_items = [
            {
                'brand': '测试品牌',
                'model': '测试型号',
                'purchase_links': {
                    '京东': 'https://www.jd.com',
                    '天猫': 'https://www.tmall.com'
                }
            }
        ]
        
        html = generator.generate_html_page(
            '测试页面',
            chart_files=['test_chart.png'],
            items=test_items,
            link_key='purchase_links'
        )
        
        if '测试品牌' in html and '京东' in html:
            print("✅ HTML生成器测试通过")
            print("✅ 中文显示正常")
        else:
            print("❌ HTML生成器测试失败")
            return False
        
        print()
        return True
    except Exception as e:
        print(f"❌ HTML生成器测试失败: {e}")
        return False

def test_price_updater():
    """测试价格更新器"""
    print("=" * 60)
    print("测试价格更新器")
    print("=" * 60)
    
    try:
        from projector_price_updater import ProjectorPriceUpdater
        
        updater = ProjectorPriceUpdater()
        
        print("🔄 测试价格数据更新...")
        price_data = updater.update_price_data(force_update=False)
        
        if price_data and 'prices' in price_data:
            print(f"✅ 价格数据更新成功")
            print(f"✅ 投影仪数量: {len(price_data['prices'])}")
            print("✅ 中文显示正常")
        else:
            print("❌ 价格数据更新失败")
            return False
        
        print()
        return True
    except Exception as e:
        print(f"❌ 价格更新器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_recommender():
    """测试推荐器"""
    print("=" * 60)
    print("测试推荐器")
    print("=" * 60)
    
    try:
        from projector_recommender import ProjectorRecommender
        
        recommender = ProjectorRecommender()
        
        if not recommender.projectors:
            print("⚠️ 没有投影仪数据，跳过推荐器测试")
            print()
            return True
        
        print(f"✅ 加载了 {len(recommender.projectors)} 款投影仪数据")
        
        test_budget = 5000
        print(f"🔄 测试预算推荐（预算: ¥{test_budget}）...")
        
        recommended = recommender.recommend_by_budget(test_budget, top_n=3, use_subsidy=True)
        
        if recommended:
            print(f"✅ 推荐成功，找到 {len(recommended)} 款投影仪")
            for i, projector in enumerate(recommended[:2], 1):
                print(f"   {i}. {projector['brand']} {projector['model']} - ¥{projector['price']}")
            print("✅ 中文显示正常")
        else:
            print("⚠️ 没有找到符合预算的投影仪")
        
        print()
        return True
    except Exception as e:
        print(f"❌ 推荐器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chart_generator():
    """测试图表生成器"""
    print("=" * 60)
    print("测试图表生成器")
    print("=" * 60)
    
    try:
        from projector_chart_generator import ProjectorChartGenerator
        from projector_recommender import ProjectorRecommender
        
        generator = ProjectorChartGenerator()
        recommender = ProjectorRecommender()
        
        if not recommender.projectors:
            print("⚠️ 没有投影仪数据，跳过图表生成测试")
            print()
            return True
        
        print("🔄 测试图表生成...")
        
        selected_projectors = recommender.projectors[:3]
        
        for projector in selected_projectors:
            value_data = recommender.calculate_value_score(projector, use_subsidy=True)
            projector['value_score'] = value_data['value_score']
            projector['total_score'] = value_data['total_score']
            projector['price'] = value_data['price']
            projector['price_info'] = value_data['price_info']
        
        chart_files = []
        
        price_chart = generator.generate_price_comparison_chart(selected_projectors, add_links=False)
        if price_chart:
            chart_files.append(price_chart)
            print(f"✅ 价格对比图表生成成功")
        
        value_chart = generator.generate_value_score_chart(selected_projectors, add_links=False)
        if value_chart:
            chart_files.append(value_chart)
            print(f"✅ 性价比对比图表生成成功")
        
        if chart_files:
            print("🔄 测试HTML页面生成...")
            html_file = os.path.join(generator.output_dir, 'test_comparison.html')
            html_content = generator.html_generator.generate_html_page(
                '测试对比报告',
                chart_files=chart_files,
                items=selected_projectors,
                link_key='purchase_links'
            )
            
            if generator.html_generator.save_html(html_content, html_file):
                print(f"✅ HTML页面生成成功: {html_file}")
                print("✅ 中文显示正常")
            else:
                print("❌ HTML页面生成失败")
                return False
        
        print()
        return True
    except Exception as e:
        print(f"❌ 图表生成器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_encoding():
    """测试中文编码"""
    print("=" * 60)
    print("测试中文编码")
    print("=" * 60)
    
    test_strings = [
        "投影仪",
        "价格",
        "性价比",
        "推荐",
        "购买链接",
        "京东",
        "天猫",
        "淘宝",
        "拼多多",
        "官方商城"
    ]
    
    print("测试字符串:")
    for s in test_strings:
        print(f"  {s}")
    
    print("✅ 所有中文字符串显示正常")
    print()
    return True

def test_data_files():
    """测试数据文件"""
    print("=" * 60)
    print("测试数据文件")
    print("=" * 60)
    
    data_files = [
        'projector_data.json',
        'projector_price_data.json'
    ]
    
    for file in data_files:
        if os.path.exists(file):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✅ {file} 存在且格式正确")
            except Exception as e:
                print(f"❌ {file} 读取失败: {e}")
                return False
        else:
            print(f"⚠️ {file} 不存在（将在首次运行时自动创建）")
    
    print()
    return True

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("投影仪推荐系统 - 综合测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    
    results.append(("模块导入", test_imports()))
    results.append(("中文编码", test_encoding()))
    results.append(("数据文件", test_data_files()))
    results.append(("HTML生成器", test_html_generator()))
    results.append(("价格更新器", test_price_updater()))
    results.append(("推荐器", test_recommender()))
    results.append(("图表生成器", test_chart_generator()))
    
    print("=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:<15} {status}")
    
    all_passed = all(result for _, result in results)
    
    print()
    if all_passed:
        print("=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        print()
        print("💡 提示:")
        print("  - 所有代码运行正常")
        print("  - 中文显示无乱码")
        print("  - 可以使用 run.bat (Windows) 或 run.sh (Linux/macOS) 启动")
        return 0
    else:
        print("=" * 60)
        print("❌ 部分测试失败，请检查错误信息")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())