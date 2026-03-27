#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动脚本 - 一键执行完整流程
"""

import sys
import os

def main():
    print("=" * 60)
    print("投影仪推荐系统 - 快速启动")
    print("=" * 60)
    print()
    
    print("🔄 [1/3] 更新价格数据...")
    print()
    
    from projector_price_updater import ProjectorPriceUpdater
    updater = ProjectorPriceUpdater()
    updater.update_price_data(force_update=False)
    
    print()
    print("🔄 [2/3] 生成推荐图表...")
    print()
    
    from projector_chart_generator import ProjectorChartGenerator
    from projector_recommender import ProjectorRecommender
    
    generator = ProjectorChartGenerator()
    recommender = ProjectorRecommender()
    
    projectors = recommender.projectors
    if not projectors:
        print("❌ 没有找到投影仪数据")
        return 1
    
    selected_projectors = projectors[:5]
    
    for projector in selected_projectors:
        value_data = recommender.calculate_value_score(projector, use_subsidy=True)
        projector['value_score'] = value_data['value_score']
        projector['total_score'] = value_data['total_score']
        projector['price'] = value_data['price']
        projector['price_info'] = value_data['price_info']
        projector['score_breakdown'] = value_data['breakdown']
    
    chart_files = []
    
    price_chart = generator.generate_price_comparison_chart(selected_projectors, add_links=False)
    if price_chart:
        print(f"✅ 价格对比图表: {price_chart}")
        chart_files.append(price_chart)
    
    value_chart = generator.generate_value_score_chart(selected_projectors, add_links=False)
    if value_chart:
        print(f"✅ 性价比对比图表: {value_chart}")
        chart_files.append(value_chart)
    
    if chart_files:
        print()
        print("🔄 [3/3] 生成HTML报告...")
        html_file = os.path.join(generator.output_dir, 'projector_comparison.html')
        html_content = generator.html_generator.generate_html_page(
            '投影仪对比报告',
            chart_files=chart_files,
            items=selected_projectors,
            link_key='purchase_links'
        )
        if generator.html_generator.save_html(html_content, html_file):
            print(f"✅ HTML报告: {html_file}")
        else:
            print("❌ HTML报告生成失败")
    
    print()
    print("=" * 60)
    print("✅ 完成！")
    print("=" * 60)
    print()
    print("📊 生成的文件:")
    for chart_file in chart_files:
        print(f"  - {chart_file}")
    print(f"  - {html_file}")
    print()
    print("💡 提示:")
    print("  - 所有数据都是从网络实时获取的真实数据")
    print("  - 打开 HTML 文件查看完整的对比报告和购买链接")
    print()
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)