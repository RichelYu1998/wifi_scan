#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投影仪图表生成器 - 生成价格对比图表
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
import json
from html_generator import HTMLGenerator


class ProjectorChartGenerator:
    """投影仪图表生成器"""
    
    def __init__(self, output_dir=None):
        self.output_dir = output_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            'charts'
        )
        
        self.config = {
            'fonts': ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans'],
            'dpi': 300,
            'colors': {
                'original_price': '#2196F3',
                'subsidy_price': '#4CAF50',
                'discount': '#FF9800',
                'value_score': '#FF9800',
                'total_score': '#9C27B0',
                'no_data': '#9E9E9E'
            },
            'bar_width': 0.35,
            'marker_size': 6,
            'line_width': 2,
            'grid_alpha': 0.3,
            'bar_alpha': 0.8
        }
        
        self.html_generator = HTMLGenerator()
        self._setup_charts()
    
    def _setup_charts(self):
        """设置图表配置"""
        os.makedirs(self.output_dir, exist_ok=True)
        plt.rcParams['font.sans-serif'] = self.config['fonts']
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['font.family'] = ['sans-serif']
    
    def _get_output_file(self, filename):
        """获取输出文件路径"""
        return os.path.join(self.output_dir, filename)
    
    def _add_bar_labels(self, ax, bars, labels=None, format_func=None):
        """添加柱状图标签"""
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                text = labels.pop(0) if labels else f'{int(height)}'
                if format_func:
                    text = format_func(height)
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       text, ha='center', va='bottom', 
                       fontsize=10, fontweight='bold')
    
    def _add_purchase_links(self, projectors):
        """添加购买链接信息"""
        purchase_info = "购买链接:\n"
        for i, projector in enumerate(projectors):
            purchase_links = projector.get('purchase_links', {})
            if purchase_links:
                main_link = list(purchase_links.values())[0]
                short_name = f"{projector.get('brand', '')} {projector.get('model', '')}"
                purchase_info += f"{i+1}. {short_name}: {main_link}\n"
        return purchase_info
    
    def _add_purchase_links_text(self, purchase_info):
        """添加购买链接文本框"""
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.figtext(0.5, 0.02, purchase_info, ha='center', fontsize=9, 
                   bbox=props, family='monospace')
        plt.subplots_adjust(bottom=0.25)
    
    def _setup_chart_style(self, ax, title, xlabel, ylabel, grid_axis='y'):
        """设置图表样式"""
        ax.set_title(title, fontsize=18, fontweight='bold', pad=25)
        ax.set_xlabel(xlabel, fontsize=13)
        ax.set_ylabel(ylabel, fontsize=13)
        ax.grid(True, alpha=self.config['grid_alpha'], axis=grid_axis, linestyle='--')
    
    def _save_chart(self, fig, output_file):
        """保存图表"""
        plt.savefig(output_file, dpi=self.config['dpi'], bbox_inches='tight')
        plt.close()
        return output_file
    
    def generate_price_history_chart(self, projector_id, projector_name, price_history, output_file=None):
        """生成价格历史图表"""
        if not price_history:
            return None
        
        output_file = output_file or self._get_output_file(f'projector_{projector_id}_price_history.png')
        
        timestamps = [datetime.fromisoformat(r['timestamp']) for r in price_history]
        original_prices = [r['original_price'] for r in price_history]
        subsidy_prices = [r['subsidy_price'] for r in price_history]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(timestamps, original_prices, marker='o', linewidth=self.config['line_width'], 
                label='原价', color=self.config['colors']['original_price'], 
                markersize=self.config['marker_size'])
        
        ax.plot(timestamps, subsidy_prices, marker='s', linewidth=self.config['line_width'], 
                label='国补价', color=self.config['colors']['subsidy_price'], 
                markersize=self.config['marker_size'])
        
        ax.fill_between(timestamps, subsidy_prices, original_prices, 
                     alpha=0.3, color=self.config['colors']['discount'], label='优惠金额')
        
        self._setup_chart_style(ax, f'{projector_name} - 价格历史趋势', '时间', '价格（元）')
        ax.legend(loc='upper right', fontsize=10)
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(timestamps)//10)))
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._save_chart(fig, output_file)
    
    def generate_price_comparison_chart(self, projectors, use_subsidy=True, output_file=None, add_links=False):
        """生成价格对比图表"""
        if not projectors:
            return None
        
        output_file = output_file or self._get_output_file('price_comparison.png')
        names = [f"{p['brand']} {p['model']}" for p in projectors]
        
        original_prices = [p['price_info']['original_price'] for p in projectors]
        subsidy_prices = [p['price'] for p in projectors] if use_subsidy else None
        
        fig, ax = plt.subplots(figsize=(16, 10))
        x = range(len(names))
        width = self.config['bar_width']
        
        bars1 = ax.bar([i - width/2 for i in x], original_prices, width, 
                        label='原价', color=self.config['colors']['original_price'], 
                        alpha=self.config['bar_alpha'])
        
        self._add_bar_labels(ax, bars1)
        
        if use_subsidy and subsidy_prices:
            bars2 = ax.bar([i + width/2 for i in x], subsidy_prices, width, 
                            label='国补价', color=self.config['colors']['subsidy_price'], 
                            alpha=self.config['bar_alpha'])
            self._add_bar_labels(ax, bars2)
        
        self._setup_chart_style(ax, '投影仪价格对比', '投影仪型号', '价格（元）')
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha='right', fontsize=11)
        ax.legend(loc='upper right', fontsize=12)
        
        if add_links:
            self._add_purchase_links_text(self._add_purchase_links(projectors))
        
        return self._save_chart(fig, output_file)
    
    def generate_value_score_chart(self, projectors, output_file=None, add_links=False):
        """生成分价比对比图表"""
        if not projectors:
            return None
        
        output_file = output_file or self._get_output_file('value_score_comparison.png')
        names = [f"{p['brand']} {p['model']}" for p in projectors]
        value_scores = [p['value_score'] for p in projectors]
        total_scores = [p['total_score'] for p in projectors]
        
        fig, ax = plt.subplots(figsize=(16, 10))
        x = range(len(names))
        width = self.config['bar_width']
        
        bars1 = ax.bar([i - width/2 for i in x], value_scores, width, 
                        label='性价比评分', color=self.config['colors']['value_score'], 
                        alpha=self.config['bar_alpha'])
        
        bars2 = ax.bar([i + width/2 for i in x], total_scores, width, 
                        label='综合评分', color=self.config['colors']['total_score'], 
                        alpha=self.config['bar_alpha'])
        
        self._add_bar_labels(ax, bars1, format_func=lambda h: f'{h:.1f}')
        self._add_bar_labels(ax, bars2, format_func=lambda h: f'{h:.1f}')
        
        self._setup_chart_style(ax, '投影仪性价比对比', '投影仪型号', '评分')
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha='right', fontsize=11)
        ax.legend(loc='upper right', fontsize=12)
        
        if add_links:
            self._add_purchase_links_text(self._add_purchase_links(projectors))
        
        return self._save_chart(fig, output_file)
    
    def generate_budget_comparison_chart(self, budget_ranges, recommendations, output_file=None):
        """生成预算对比图表"""
        if not budget_ranges or not recommendations:
            return None
        
        output_file = output_file or self._get_output_file('budget_comparison.png')
        
        range_labels = [
            f"{r['min']}-{r['max']}" if r['max'] >= 10000 
            else f"{r['min']//1000}k-{r['max']//1000}k"
            for r in budget_ranges
        ]
        
        best_prices = [rec['price'] if rec else 0 for rec in recommendations]
        best_value_scores = [rec['value_score'] if rec else 0 for rec in recommendations]
        projector_names = [f"{rec['brand']} {rec['model']}" if rec else "无推荐" for rec in recommendations]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
        
        colors1 = [self.config['colors']['subsidy_price'] if price > 0 
                   else self.config['colors']['no_data'] for price in best_prices]
        bars1 = ax1.bar(range_labels, best_prices, color=colors1, alpha=self.config['bar_alpha'])
        
        for bar, price, name in zip(bars1, best_prices, projector_names):
            if price > 0:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                       f'¥{int(price)}\n{name}', ha='center', va='bottom', 
                       fontsize=9, fontweight='bold')
        
        self._setup_chart_style(ax1, '不同预算的最佳推荐价格', '', '价格（元）')
        
        colors2 = [self.config['colors']['value_score'] if score > 0 
                   else self.config['colors']['no_data'] for score in best_value_scores]
        bars2 = ax2.bar(range_labels, best_value_scores, color=colors2, alpha=self.config['bar_alpha'])
        
        for bar, score, name in zip(bars2, best_value_scores, projector_names):
            if score > 0:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                       f'{score:.1f}\n{name}', ha='center', va='bottom', 
                       fontsize=9, fontweight='bold')
        
        self._setup_chart_style(ax2, '不同预算的最佳性价比', '预算范围（元）', '性价比评分')
        
        purchase_info = "购买链接:\n"
        for rec, range_info in zip(recommendations, budget_ranges):
            if rec:
                purchase_links = rec.get('purchase_links', {})
                if purchase_links:
                    main_link = list(purchase_links.values())[0]
                    short_name = f"{rec['brand']} {rec['model']}"
                    budget_range = f"{range_info['min']}-{range_info['max']}"
                    purchase_info += f"{budget_range}元: {short_name} - {main_link}\n"
        
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.figtext(0.5, 0.02, purchase_info, ha='center', fontsize=8, 
                   bbox=props, family='monospace')
        plt.subplots_adjust(bottom=0.20, hspace=0.3)
        
        return self._save_chart(fig, output_file)
    
    def generate_radar_chart(self, projector, output_file=None):
        """生成投影仪性能雷达图"""
        if not projector:
            return None
        
        output_file = output_file or self._get_output_file(f'projector_{projector["id"]}_radar.png')
        
        breakdown = projector.get('score_breakdown', {})
        categories = ['分辨率', '亮度', '对比度', '寿命', '功能', '品牌']
        values = [
            breakdown.get('resolution', 0),
            breakdown.get('brightness', 0),
            breakdown.get('contrast', 0),
            breakdown.get('lifespan', 0),
            breakdown.get('features', 0),
            breakdown.get('brand', 0)
        ]
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        angles = [n / len(categories) * 2 * 3.14159 for n in range(len(categories))]
        angles += angles[:1]
        values += values[:1]
        
        ax.plot(angles, values, 'o-', linewidth=self.config['line_width'], 
                color=self.config['colors']['original_price'])
        ax.fill(angles, values, alpha=0.25, color=self.config['colors']['original_price'])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=12)
        ax.set_title(f'{projector["brand"]} {projector["model"]} - 性能分析', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=self.config['grid_alpha'])
        ax.set_ylim(0, 100)
        
        return self._save_chart(fig, output_file)


def main():
    """主函数 - 从真实数据源获取数据"""
    print("=== 投影仪图表生成器 ===")
    print()
    
    from projector_recommender import ProjectorRecommender
    
    generator = ProjectorChartGenerator()
    recommender = ProjectorRecommender()
    
    print("🔄 正在从网络获取投影仪数据...")
    print()
    
    # 更新价格数据
    recommender.update_price_data(force_update=False)
    
    # 获取所有投影仪数据
    projectors = recommender.projectors
    
    if not projectors:
        print("❌ 错误：没有找到投影仪数据")
        print("   请确保 projector_data.json 文件存在且包含有效数据")
        return
    
    print(f"✅ 成功加载 {len(projectors)} 款投影仪数据")
    print()
    
    # 选择前5款投影仪进行对比
    selected_projectors = projectors[:5]
    
    # 为每个投影仪计算评分
    for projector in selected_projectors:
        value_data = recommender.calculate_value_score(projector, use_subsidy=True)
        projector['value_score'] = value_data['value_score']
        projector['total_score'] = value_data['total_score']
        projector['price'] = value_data['price']
        projector['price_info'] = value_data['price_info']
        projector['score_breakdown'] = value_data['breakdown']
    
    # 收集所有生成的图表
    chart_files = []
    
    print("📊 生成价格对比图表...")
    price_chart = generator.generate_price_comparison_chart(selected_projectors, add_links=False)
    if price_chart:
        print(f"✅ 价格对比图表已生成: {price_chart}")
        chart_files.append(price_chart)
    
    print("📊 生成分价比对比图表...")
    value_chart = generator.generate_value_score_chart(selected_projectors, add_links=False)
    if value_chart:
        print(f"✅ 性价比对比图表已生成: {value_chart}")
        chart_files.append(value_chart)
    
    # 生成HTML页面
    if chart_files:
        print()
        print("📄 生成HTML页面...")
        html_file = os.path.join(generator.output_dir, 'projector_comparison.html')
        html_content = generator.html_generator.generate_html_page(
            '投影仪对比报告',
            chart_files=chart_files,
            items=selected_projectors,
            link_key='purchase_links'
        )
        if generator.html_generator.save_html(html_content, html_file):
            print(f"✅ HTML页面已生成: {html_file}")
        else:
            print("❌ HTML页面生成失败")
    
    print()
    print("✅ 图表生成完成！")
    print()
    print("💡 提示:")
    print("  - 所有数据都是从网络实时获取的真实数据")
    print("  - 图表已保存到 charts 目录")
    print("  - 打开 projector_comparison.html 查看完整报告")
    print("  - HTML页面中的购买链接可以直接点击")


if __name__ == '__main__':
    main()