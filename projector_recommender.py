#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投影仪性价比推荐器 - 根据预算推荐性价比最高的投影仪（支持国补对比）
"""

import json
import os
import sys
from datetime import datetime

from projector_price_updater import ProjectorPriceUpdater


class ProjectorRecommender:
    """投影仪推荐器（支持国补对比）"""
    
    def __init__(self, data_file=None, price_updater=None):
        self.data_file = data_file or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            'projector_data.json'
        )
        self.projectors = self._load_projector_data()
        self.price_updater = price_updater or ProjectorPriceUpdater()
        self.current_use_subsidy = False
        
        self.score_config = {
            'weights': {
                'resolution': 0.25,
                'brightness': 0.20,
                'contrast': 0.15,
                'lifespan': 0.10,
                'features': 0.20,
                'brand': 0.10
            },
            'resolution': {
                '4K': 100, '3840x2160': 100,
                '2K': 85, '2560x1440': 85,
                '1080P': 70, '1920x1080': 70,
                '720P': 50, '1280x720': 50,
                '480P': 30, '854x480': 30
            },
            'brand': {
                '爱普生': 95, '索尼': 100, '明基': 85, '优派': 80,
                '极米': 90, '坚果': 85, '当贝': 88, '峰米': 85,
                '米家': 90, '小米': 88, '宏碁': 82, '奥图码': 80,
                '松下': 92, 'NEC': 85, '理光': 83
            },
            'features': {
                '4K支持': 15, 'HDR支持': 10, '3D功能': 8,
                '自动梯形校正': 8, '侧投功能': 6, '无线投屏': 10,
                '蓝牙音响': 6, '智能系统': 12, '游戏模式': 8,
                '低延迟': 10, '高刷新率': 8, '短焦投影': 10,
                '激光光源': 15, 'LED光源': 12
            },
            'brightness_ranges': [
                (0, 1000, 40, 20),
                (1000, 2000, 60, 20),
                (2000, 3000, 80, 15),
                (3000, float('inf'), 95, 5)
            ],
            'contrast_ranges': [
                (0, 5000, 40, 20),
                (5000, 10000, 60, 20),
                (10000, 20000, 80, 15),
                (20000, float('inf'), 95, 5)
            ],
            'lifespan_ranges': [
                (0, 10000, 40, 20),
                (10000, 20000, 60, 20),
                (20000, 30000, 80, 15),
                (30000, float('inf'), 95, 5)
            ]
        }
    
    def _load_projector_data(self):
        """加载投影仪数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('projectors', [])
            return []
        except Exception as e:
            print(f"加载投影仪数据失败: {e}")
            return []
    
    def _get_projector_price(self, projector_id, use_subsidy=False):
        """获取投影仪价格（支持国补）"""
        price_info = self.price_updater.get_projector_price(projector_id, use_subsidy)
        
        if price_info:
            return price_info['price']
        
        projector = next((p for p in self.projectors if p.get('id') == projector_id), None)
        if projector:
            base_price = projector.get('price', 0)
            return self.price_updater._calculate_subsidy_price(base_price) if use_subsidy else base_price
        return 0
    
    def _calculate_range_score(self, value, ranges):
        """根据范围计算评分"""
        if value <= 0:
            return 30
        
        for min_val, max_val, base_score, max_add in ranges:
            if min_val < value <= max_val:
                if max_val == float('inf'):
                    return base_score + min(max_add, (value - min_val) / 1000)
                return base_score + ((value - min_val) / (max_val - min_val)) * max_add
        return 30
    
    def _get_score(self, score_type, value):
        """通用评分获取方法"""
        if score_type == 'resolution':
            return self.score_config['resolution'].get(value, 50)
        elif score_type == 'brand':
            return self.score_config['brand'].get(value, 75)
        elif score_type == 'brightness':
            return self._calculate_range_score(value, self.score_config['brightness_ranges'])
        elif score_type == 'contrast':
            return self._calculate_range_score(value, self.score_config['contrast_ranges'])
        elif score_type == 'lifespan':
            return self._calculate_range_score(value, self.score_config['lifespan_ranges'])
        elif score_type == 'features':
            return min(100, sum(self.score_config['features'].get(f, 0) for f in value))
        return 50
    
    def _calculate_total_score(self, projector):
        """计算综合评分"""
        scores = {
            'resolution': self._get_score('resolution', projector.get('resolution', '')),
            'brightness': self._get_score('brightness', projector.get('brightness', 0)),
            'contrast': self._get_score('contrast', projector.get('contrast', 0)),
            'lifespan': self._get_score('lifespan', projector.get('lifespan', 0)),
            'features': self._get_score('features', projector.get('features', [])),
            'brand': self._get_score('brand', projector.get('brand', ''))
        }
        
        weights = self.score_config['weights']
        total_score = sum(scores[key] * weights[key] for key in scores.keys())
        
        return round(total_score, 2), scores
    
    def _enrich_projector_data(self, projector, use_subsidy=False):
        """丰富投影仪数据（添加评分和价格信息）"""
        projector_id = projector.get('id')
        price = self._get_projector_price(projector_id, use_subsidy)
        price_info = self.price_updater.get_projector_price(projector_id, use_subsidy)
        
        total_score, scores = self._calculate_total_score(projector)
        value_score = (total_score * 1000) / price if price > 0 else 0
        
        projector['value_score'] = round(value_score, 2)
        projector['total_score'] = total_score
        projector['price'] = price
        projector['price_info'] = price_info
        projector['score_breakdown'] = {k: round(v, 2) for k, v in scores.items()}
        
        return projector
    
    def calculate_value_score(self, projector, use_subsidy=False):
        """计算性价比评分（支持国补价格）"""
        projector_copy = projector.copy()
        self._enrich_projector_data(projector_copy, use_subsidy)
        
        return {
            'total_score': projector_copy['total_score'],
            'value_score': projector_copy['value_score'],
            'price': projector_copy['price'],
            'price_info': projector_copy['price_info'],
            'breakdown': projector_copy['score_breakdown']
        }
    
    def recommend_by_budget(self, budget, top_n=5, use_subsidy=False):
        """根据预算推荐投影仪（支持国补）"""
        self.current_use_subsidy = use_subsidy
        
        affordable_projectors = [
            p.copy() for p in self.projectors
            if self._get_projector_price(p.get('id'), use_subsidy) <= budget
        ]
        
        if not affordable_projectors:
            return []
        
        for projector in affordable_projectors:
            self._enrich_projector_data(projector, use_subsidy)
        
        return sorted(affordable_projectors, key=lambda x: x['value_score'], reverse=True)[:top_n]
    
    def compare_projectors(self, projector_ids, use_subsidy=False):
        """对比多个投影仪（支持国补）"""
        projectors_to_compare = [
            p.copy() for p in self.projectors if p.get('id') in projector_ids
        ]
        
        if not projectors_to_compare:
            return []
        
        for projector in projectors_to_compare:
            self._enrich_projector_data(projector, use_subsidy)
        
        return projectors_to_compare
    
    def get_best_value_projector(self, budget=None, use_subsidy=False):
        """获取性价比最高的投影仪（支持国补）"""
        if budget:
            projectors_to_check = [
                p.copy() for p in self.projectors
                if self._get_projector_price(p.get('id'), use_subsidy) <= budget
            ]
        else:
            projectors_to_check = [p.copy() for p in self.projectors]
        
        if not projectors_to_check:
            return None
        
        for projector in projectors_to_check:
            self._enrich_projector_data(projector, use_subsidy)
        
        return max(projectors_to_check, key=lambda x: x['value_score'])
    
    def compare_subsidy_prices(self, projector_id):
        """对比原价和国补价格"""
        return self.price_updater.compare_prices(projector_id)
    
    def update_price_data(self, force_update=False):
        """更新价格数据"""
        return self.price_updater.update_price_data(force_update)


def format_price(price):
    """格式化价格显示"""
    return f"¥{price:,.0f}"


def print_projector_info(projector, show_details=False, show_price_comparison=False):
    """打印投影仪信息（支持国补价格对比）"""
    print(f"📺 {projector.get('brand', '')} {projector.get('model', '')}")
    
    price = projector.get('price', 0)
    price_info = projector.get('price_info', {})
    
    if show_price_comparison and price_info:
        original_price = price_info.get('original_price', price)
        subsidy_price = price_info.get('subsidy_price', price)
        subsidy_amount = price_info.get('subsidy_amount', 0)
        subsidy_rate = price_info.get('subsidy_rate', 0)
        
        print(f"   💰 原价: {format_price(original_price)}")
        print(f"   🎁 国补价: {format_price(subsidy_price)}")
        print(f"   💸 优惠: ¥{subsidy_amount} ({subsidy_rate*100:.0f}%)")
        print(f"   🎯 性价比评分: {projector.get('value_score', 0):.2f}")
        print(f"   ⭐ 综合评分: {projector.get('total_score', 0):.2f}")
    else:
        print(f"   💰 价格: {format_price(price)}")
        print(f"   🎯 性价比评分: {projector.get('value_score', 0):.2f}")
        print(f"   ⭐ 综合评分: {projector.get('total_score', 0):.2f}")
    
    if show_details:
        print(f"   📊 详细参数:")
        print(f"      分辨率: {projector.get('resolution', 'N/A')}")
        print(f"      亮度: {projector.get('brightness', 0)} ANSI流明")
        print(f"      对比度: {projector.get('contrast', 0):,}")
        print(f"      灯泡寿命: {projector.get('lifespan', 0)} 小时")
        print(f"      投影尺寸: {projector.get('screen_size', 'N/A')}")
        print(f"      投影距离: {projector.get('throw_distance', 'N/A')}")
        
        features = projector.get('features', [])
        if features:
            print(f"      特色功能: {', '.join(features)}")
        
        breakdown = projector.get('score_breakdown', {})
        if breakdown:
            print(f"   📈 评分明细:")
            print(f"      分辨率: {breakdown.get('resolution', 0):.1f}")
            print(f"      亮度: {breakdown.get('brightness', 0):.1f}")
            print(f"      对比度: {breakdown.get('contrast', 0):.1f}")
            print(f"      寿命: {breakdown.get('lifespan', 0):.1f}")
            print(f"      功能: {breakdown.get('features', 0):.1f}")
            print(f"      品牌: {breakdown.get('brand', 0):.1f}")


def print_comparison_table(projectors, show_price_comparison=False):
    """打印对比表格（支持国补价格对比）"""
    if not projectors:
        print("❌ 没有可对比的投影仪")
        return
    
    print("\n" + "="*120)
    print("📊 投影仪对比表")
    print("="*120)
    
    header = f"{'品牌型号':<20} {'原价':<12} {'国补价':<12} {'优惠':<10} {'分辨率':<12} {'亮度':<10} {'性价比':<10} {'综合评分':<10}" if show_price_comparison else f"{'品牌型号':<20} {'价格':<12} {'分辨率':<12} {'亮度':<10} {'性价比':<10} {'综合评分':<10}"
    
    print(header)
    print("-"*120)
    
    for i, projector in enumerate(projectors, 1):
        price_info = projector.get('price_info', {})
        
        if show_price_comparison and price_info:
            original_price = price_info.get('original_price', projector.get('price', 0))
            subsidy_price = price_info.get('subsidy_price', projector.get('price', 0))
            subsidy_amount = price_info.get('subsidy_amount', 0)
            
            row = f"{i}. {projector.get('brand', '')} {projector.get('model', ''):<15} " \
                   f"{format_price(original_price):<10} " \
                   f"{format_price(subsidy_price):<10} " \
                   f"¥{subsidy_amount:<8} " \
                   f"{projector.get('resolution', 'N/A'):<10} " \
                   f"{projector.get('brightness', 0):<8} " \
                   f"{projector.get('value_score', 0):<8.1f} " \
                   f"{projector.get('total_score', 0):<8.1f}"
        else:
            row = f"{i}. {projector.get('brand', '')} {projector.get('model', ''):<15} " \
                   f"{format_price(projector.get('price', 0)):<10} " \
                   f"{projector.get('resolution', 'N/A'):<10} " \
                   f"{projector.get('brightness', 0):<8} " \
                   f"{projector.get('value_score', 0):<8.1f} " \
                   f"{projector.get('total_score', 0):<8.1f}"
        
        print(row)
    
    print("="*120)


def print_price_comparison(projector_id, recommender):
    """打印价格对比"""
    comparison = recommender.compare_subsidy_prices(projector_id)
    
    if not comparison:
        print("❌ 无法获取价格对比信息")
        return
    
    print("\n" + "="*80)
    print("💰 价格对比")
    print("="*80)
    print(f"原价: {format_price(comparison['original_price'])}")
    print(f"国补价: {format_price(comparison['subsidy_price'])}")
    print(f"优惠金额: ¥{comparison['subsidy_amount']}")
    print(f"优惠比例: {comparison['savings_rate']:.1f}%")
    print(f"国补比例: {comparison['subsidy_rate']*100:.0f}%")
    print(f"是否享受国补: {'是' if comparison['has_subsidy'] else '否'}")
    print(f"数据来源: {comparison['platform']}")
    print(f"更新时间: {comparison['update_time']}")
    print("="*80)


def main():
    """主函数"""
    print("🎬 投影仪性价比推荐器（支持国补对比）")
    print("="*50)
    
    recommender = ProjectorRecommender()
    
    if not recommender.projectors:
        print("❌ 错误：没有找到投影仪数据")
        print("   请确保 projector_data.json 文件存在且包含有效数据")
        return
    
    print(f"✅ 成功加载 {len(recommender.projectors)} 款投影仪数据")
    
    print("🔄 检查价格数据...")
    price_data = recommender.update_price_data(force_update=False)
    print()
    
    try:
        budget_input = input("请输入您的预算（元）: ").strip()
        budget = float(budget_input)
        
        if budget <= 0:
            print("❌ 预算必须大于0")
            return
            
    except ValueError:
        print("❌ 无效的预算输入，请输入数字")
        return
    except KeyboardInterrupt:
        print("\n👋 用户取消操作")
        return
    
    print(f"\n💰 您的预算: {format_price(budget)}")
    print()
    
    try:
        use_subsidy_input = input("是否使用国补价格？(y/n): ").strip().lower()
        use_subsidy = use_subsidy_input in ['y', 'yes', '是']
    except KeyboardInterrupt:
        print("\n👋 用户取消操作")
        return
    
    print(f"\n{'🎁 使用国补价格' if use_subsidy else '💰 使用原价'}")
    print()
    
    print("🔍 正在分析投影仪性价比...")
    print()
    
    recommended = recommender.recommend_by_budget(budget, top_n=5, use_subsidy=use_subsidy)
    
    if not recommended:
        print(f"❌ 没有找到预算在 {format_price(budget)} 以内的投影仪")
        print("💡 建议：增加预算或查看其他价位的投影仪")
        return
    
    print(f"✅ 找到 {len(recommended)} 款符合预算的投影仪")
    print()
    
    print("🏆 推荐结果（按性价比排序）")
    print("="*120)
    
    for i, projector in enumerate(recommended, 1):
        print(f"\n🥇 第{i}名推荐")
        print_projector_info(projector, show_details=True, show_price_comparison=True)
        print()
    
    print_comparison_table(recommended, show_price_comparison=True)
    
    best_projector = recommended[0]
    print("\n" + "="*120)
    print("🎯 最佳推荐")
    print("="*120)
    print_projector_info(best_projector, show_details=True, show_price_comparison=True)
    
    if best_projector.get('price_info'):
        print_price_comparison(best_projector['id'], recommender)
    
    print("\n💡 购买建议:")
    print(f"   📺 型号: {best_projector.get('brand', '')} {best_projector.get('model', '')}")
    
    price_info = best_projector.get('price_info', {})
    if price_info and price_info.get('has_subsidy'):
        print(f"   💰 原价: {format_price(price_info.get('original_price', 0))}")
        print(f"   🎁 国补价: {format_price(price_info.get('subsidy_price', 0))}")
        print(f"   💸 优惠: ¥{price_info.get('subsidy_amount', 0)} ({price_info.get('subsidy_rate', 0)*100:.0f}%)")
    else:
        print(f"   💰 价格: {format_price(best_projector.get('price', 0))}")
    
    print(f"   🎯 性价比: {best_projector.get('value_score', 0):.2f}")
    print(f"   ✨ 适合场景: {best_projector.get('usage_scenario', '家庭娱乐')}")
    print()
    print("="*120)


if __name__ == '__main__':
    main()