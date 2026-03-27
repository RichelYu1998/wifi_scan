#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版投影仪推荐器 - 支持实时预算、历史价格对比、图表生成和购买链接
"""

import json
import os
import sys
from datetime import datetime

from projector_recommender import ProjectorRecommender
from projector_price_history import ProjectorPriceHistory
from projector_chart_generator import ProjectorChartGenerator
from projector_price_updater import ProjectorPriceUpdater


class EnhancedProjectorRecommender:
    """增强版投影仪推荐器"""
    
    def __init__(self):
        self.recommender = ProjectorRecommender()
        self.price_history = ProjectorPriceHistory()
        self.chart_generator = ProjectorChartGenerator()
        self.price_updater = ProjectorPriceUpdater()
        
        # 预设预算范围
        self.budget_ranges = [
            {'name': '入门级', 'min': 0, 'max': 2000, 'description': '适合预算有限的用户'},
            {'name': '经济型', 'min': 2000, 'max': 3000, 'description': '性价比之选'},
            {'name': '主流型', 'min': 3000, 'max': 5000, 'description': '家庭娱乐首选'},
            {'name': '高端型', 'min': 5000, 'max': 7000, 'description': '追求更好画质'},
            {'name': '旗舰型', 'min': 7000, 'max': 10000, 'description': '顶级体验'}
        ]
    
    def get_user_budget(self):
        """获取用户预算"""
        print("="*80)
        print("💰 投影仪预算选择")
        print("="*80)
        print()
        
        # 显示预设预算范围
        print("📋 预设预算范围:")
        for i, range_info in enumerate(self.budget_ranges, 1):
            print(f"  {i}. {range_info['name']} (¥{range_info['min']:,} - ¥{range_info['max']:,}) - {range_info['description']}")
        
        print(f"  {len(self.budget_ranges) + 1}. 自定义预算")
        print()
        
        while True:
            try:
                choice = input("请选择预算范围 (输入数字): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(self.budget_ranges):
                    selected_range = self.budget_ranges[choice_num - 1]
                    print(f"✅ 已选择: {selected_range['name']} (¥{selected_range['min']:,} - ¥{selected_range['max']:,})")
                    return selected_range['max']
                elif choice_num == len(self.budget_ranges) + 1:
                    while True:
                        try:
                            custom_budget = float(input("请输入自定义预算 (元): ").strip())
                            if custom_budget > 0:
                                print(f"✅ 已设置自定义预算: ¥{custom_budget:,.0f}")
                                return custom_budget
                            else:
                                print("❌ 预算必须大于0，请重新输入")
                        except ValueError:
                            print("❌ 请输入有效的数字")
                else:
                    print(f"❌ 请输入1-{len(self.budget_ranges) + 1}之间的数字")
            except ValueError:
                print("❌ 请输入有效的数字")
    
    def get_subsidy_preference(self):
        """获取国补偏好"""
        print()
        print("="*80)
        print("🎁 国家补贴政策")
        print("="*80)
        print()
        print("国家补贴可为您节省20%的投影仪费用！")
        print("例如: 原价¥5000的投影仪，国补后仅需¥4000")
        print()
        
        while True:
            choice = input("是否使用国家补贴价格进行推荐？ (y/n): ").strip().lower()
            if choice in ['y', 'yes', '是', '1']:
                print("✅ 将使用国家补贴价格进行推荐")
                return True
            elif choice in ['n', 'no', '否', '0']:
                print("✅ 将使用原价进行推荐")
                return False
            else:
                print("❌ 请输入 y/n 或 是/否")
    
    def recommend_by_budget_range(self, budget, use_subsidy=False, top_n=3):
        """根据预算范围推荐投影仪"""
        print()
        print("="*80)
        print(f"🔍 预算范围推荐 (¥{budget:,.0f})")
        print("="*80)
        print()
        
        # 获取推荐
        recommended = self.recommender.recommend_by_budget(budget, top_n, use_subsidy)
        
        if not recommended:
            print("❌ 在当前预算范围内没有找到合适的投影仪")
            return []
        
        # 显示推荐结果
        print(f"✅ 找到 {len(recommended)} 款符合预算的投影仪")
        print()
        
        for i, projector in enumerate(recommended, 1):
            print(f"{i}. {projector['brand']} {projector['model']}")
            print(f"   💰 价格: ¥{projector['price']:,.0f}")
            print(f"   🎯 性价比: {projector['value_score']:.2f}")
            print(f"   ⭐ 综合评分: {projector['total_score']:.2f}")
            print(f"   📺 分辨率: {projector['resolution']}")
            print(f"   💡 亮度: {projector['brightness']} 流明")
            print(f"   🎭 对比度: {projector['contrast']:,}:1")
            print(f"   ⏰ 寿命: {projector['lifespan']:,} 小时")
            print(f"   ✨ 功能: {', '.join(projector['features'][:5])}")
            print()
        
        return recommended
    
    def show_price_history(self, projector_id, days=30):
        """显示价格历史"""
        print()
        print("="*80)
        print("📊 价格历史分析")
        print("="*80)
        print()
        
        # 获取价格历史
        history = self.price_history.get_price_history(projector_id, days)
        
        if not history:
            print("⚠️ 暂无价格历史数据")
            return
        
        # 获取价格趋势
        trend = self.price_history.get_price_trend(projector_id, days)
        
        if trend:
            print(f"📈 价格趋势 (过去{days}天):")
            print(f"   原价变化: ¥{trend['original_price_change']:+,} ({trend['original_price_change_rate']:+.1f}%)")
            print(f"   国补价变化: ¥{trend['subsidy_price_change']:+,} ({trend['subsidy_price_change_rate']:+.1f}%)")
            print(f"   记录数量: {trend['record_count']}")
            print()
        
        # 获取最低价格
        lowest = self.price_history.get_lowest_price(projector_id, days)
        if lowest:
            print(f"🏆 最低价格:")
            print(f"   原价: ¥{lowest['original_price']:,}")
            print(f"   国补价: ¥{lowest['subsidy_price']:,}")
            print(f"   记录时间: {lowest['timestamp'][:19]}")
            print()
        
        # 获取最高价格
        highest = self.price_history.get_highest_price(projector_id, days)
        if highest:
            print(f"📊 最高价格:")
            print(f"   原价: ¥{highest['original_price']:,}")
            print(f"   国补价: ¥{highest['subsidy_price']:,}")
            print(f"   记录时间: {highest['timestamp'][:19]}")
            print()
        
        # 获取平均价格
        average = self.price_history.get_average_price(projector_id, days)
        if average:
            print(f"📈 平均价格:")
            print(f"   平均原价: ¥{average['average_original_price']:,.2f}")
            print(f"   平均国补价: ¥{average['average_subsidy_price']:,.2f}")
            print()
    
    def show_purchase_links(self, projector):
        """显示购买链接"""
        print()
        print("="*80)
        print("🛒 购买渠道")
        print("="*80)
        print()
        
        purchase_links = projector.get('purchase_links', {})
        
        if not purchase_links:
            print("⚠️ 暂无购买链接信息")
            return
        
        print(f"📺 {projector['brand']} {projector['model']} - 购买链接:")
        print()
        
        for platform, link in purchase_links.items():
            print(f"  🔗 {platform}: {link}")
        
        print()
        print("💡 提示: 点击链接可跳转到对应电商平台查看详情和购买")
        print()
    
    def generate_comparison_charts(self, projectors, use_subsidy=True):
        """生成对比图表"""
        print()
        print("="*80)
        print("📊 生成对比图表")
        print("="*80)
        print()
        
        if not projectors:
            print("❌ 没有投影仪数据，无法生成图表")
            return
        
        # 生成价格对比图表
        print("📈 生成价格对比图表...")
        price_chart = self.chart_generator.generate_price_comparison_chart(
            projectors, use_subsidy
        )
        if price_chart:
            print(f"✅ 价格对比图表已生成: {price_chart}")
        
        # 生成分价比对比图表
        print("📈 生成分价比对比图表...")
        value_chart = self.chart_generator.generate_value_score_chart(projectors)
        if value_chart:
            print(f"✅ 性价比对比图表已生成: {value_chart}")
        
        # 生成雷达图（仅第一个投影仪）
        if projectors:
            print("📈 生成性能雷达图...")
            radar_chart = self.chart_generator.generate_radar_chart(projectors[0])
            if radar_chart:
                print(f"✅ 性能雷达图已生成: {radar_chart}")
        
        print()
    
    def generate_budget_comparison_charts(self):
        """生成预算对比图表"""
        print()
        print("="*80)
        print("📊 生成预算对比图表")
        print("="*80)
        print()
        
        recommendations = []
        
        for range_info in self.budget_ranges:
            # 获取该预算范围的推荐
            recommended = self.recommender.recommend_by_budget(
                range_info['max'], 1, use_subsidy=True
            )
            if recommended:
                recommendations.append(recommended[0])
            else:
                recommendations.append(None)
        
        # 生成预算对比图表
        budget_chart = self.chart_generator.generate_budget_comparison_chart(
            self.budget_ranges, recommendations
        )
        if budget_chart:
            print(f"✅ 预算对比图表已生成: {budget_chart}")
        
        print()
        
        return recommendations
    
    def interactive_recommendation(self):
        """交互式推荐"""
        print()
        print("🎬 投影仪智能推荐系统")
        print("="*80)
        print()
        print("欢迎使用投影仪智能推荐系统！")
        print("本系统将根据您的预算和需求，为您推荐最适合的投影仪")
        print()
        
        # 获取用户预算
        budget = self.get_user_budget()
        
        # 获取国补偏好
        use_subsidy = self.get_subsidy_preference()
        
        # 根据预算推荐
        recommended = self.recommend_by_budget_range(budget, use_subsidy, top_n=3)
        
        if not recommended:
            return
        
        # 显示最佳推荐
        best_projector = recommended[0]
        print()
        print("="*80)
        print("🏆 最佳推荐")
        print("="*80)
        print()
        print(f"📺 型号: {best_projector['brand']} {best_projector['model']}")
        print(f"💰 价格: ¥{best_projector['price']:,.0f}")
        print(f"🎯 性价比: {best_projector['value_score']:.2f}")
        print(f"⭐ 综合评分: {best_projector['total_score']:.2f}")
        print(f"✨ 适合场景: {best_projector['usage_scenario']}")
        print()
        
        # 显示购买链接
        self.show_purchase_links(best_projector)
        
        # 显示价格历史
        self.show_price_history(best_projector['id'])
        
        # 生成对比图表
        self.generate_comparison_charts(recommended, use_subsidy)
        
        # 询问是否查看其他预算范围的推荐
        print()
        print("="*80)
        print("📊 其他预算范围推荐")
        print("="*80)
        print()
        
        choice = input("是否查看其他预算范围的推荐？ (y/n): ").strip().lower()
        if choice in ['y', 'yes', '是', '1']:
            recommendations = self.generate_budget_comparison_charts()
            
            print("📋 各预算范围最佳推荐:")
            print()
            
            for i, (range_info, rec) in enumerate(zip(self.budget_ranges, recommendations)):
                if rec:
                    print(f"{range_info['name']} (¥{range_info['min']:,} - ¥{range_info['max']:,}):")
                    print(f"  📺 {rec['brand']} {rec['model']}")
                    print(f"  💰 ¥{rec['price']:,.0f} | 🎯 性价比: {rec['value_score']:.2f}")
                    print()
                else:
                    print(f"{range_info['name']} (¥{range_info['min']:,} - ¥{range_info['max']:,}):")
                    print(f"  ⚠️ 暂无推荐")
                    print()
        
        print()
        print("="*80)
        print("✅ 推荐完成！")
        print("="*80)
        print()
        print("💡 提示:")
        print("  - 图表已保存到 charts 目录")
        print("  - 您可以随时更新价格数据以获取最新推荐")
        print("  - 建议在购买前查看价格历史和购买链接")
        print()


def main():
    """主函数"""
    recommender = EnhancedProjectorRecommender()
    recommender.interactive_recommendation()


if __name__ == '__main__':
    main()