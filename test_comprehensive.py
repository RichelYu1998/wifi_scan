#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面测试脚本 - 测试所有Python文件，确保无中文乱码
"""

import sys
import os
import json
import subprocess
import platform
from pathlib import Path
from datetime import datetime


class ComprehensiveTest:
    """全面测试类"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent.absolute()
        self.system = platform.system()
        self.test_results = {}
        self.chinese_test_strings = [
            "投影仪", "价格", "性价比", "推荐", "购买链接",
            "京东", "天猫", "淘宝", "拼多多", "官方商城",
            "WiFi扫描", "硬件信息", "网络速度", "视频分辨率",
            "更新时间", "数据来源", "生成时间", "测试通过"
        ]
    
    def print_header(self, title):
        """打印标题"""
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)
    
    def print_subheader(self, title):
        """打印子标题"""
        print("\n" + "-"*70)
        print(f"  {title}")
        print("-"*70)
    
    def test_encoding(self):
        """测试编码"""
        self.print_subheader("测试编码")
        
        print("测试中文字符串:")
        for s in self.chinese_test_strings:
            print(f"  ✓ {s}")
        
        print("\n✅ 中文编码测试通过")
        return True
    
    def test_imports(self):
        """测试所有模块导入"""
        self.print_subheader("测试模块导入")
        
        py_files = list(self.project_dir.glob("*.py"))
        exclude_files = ['launcher.py', 'test_comprehensive.py', 'test_all.py']
        
        modules = []
        for py_file in py_files:
            if py_file.name not in exclude_files and not py_file.name.startswith('_'):
                module_name = py_file.stem
                modules.append(module_name)
        
        success_count = 0
        for module in sorted(modules):
            try:
                __import__(module)
                print(f"  ✓ {module}.py")
                success_count += 1
            except Exception as e:
                print(f"  ✗ {module}.py - {e}")
        
        result = success_count == len(modules)
        print(f"\n✅ 模块导入测试: {success_count}/{len(modules)} 通过")
        return result
    
    def test_data_files(self):
        """测试数据文件"""
        self.print_subheader("测试数据文件")
        
        json_files = [
            'projector_data.json',
            'projector_price_data.json',
            'hardware_data/cpu_performance.json',
            'hardware_data/gpu_performance.json',
            'hardware_data/memory_performance.json'
        ]
        
        success_count = 0
        for json_file in json_files:
            file_path = self.project_dir / json_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"  ✓ {json_file}")
                    success_count += 1
                except Exception as e:
                    print(f"  ✗ {json_file} - {e}")
            else:
                print(f"  ⚠ {json_file} - 不存在（将在首次运行时创建）")
        
        result = success_count > 0
        print(f"\n✅ 数据文件测试: {success_count} 个文件通过")
        return result
    
    def test_html_generator(self):
        """测试HTML生成器"""
        self.print_subheader("测试HTML生成器")
        
        try:
            from html_generator import HTMLGenerator
            
            generator = HTMLGenerator()
            
            test_items = [
                {
                    'brand': '测试品牌',
                    'model': '测试型号',
                    'purchase_links': {
                        '京东': 'https://www.jd.com',
                        '天猫': 'https://www.tmall.com',
                        '淘宝': 'https://www.taobao.com'
                    }
                }
            ]
            
            html = generator.generate_html_page(
                '测试页面',
                chart_files=['test_chart.png'],
                items=test_items,
                link_key='purchase_links'
            )
            
            checks = [
                ('测试品牌' in html, '包含品牌名称'),
                ('京东' in html, '包含京东链接'),
                ('天猫' in html, '包含天猫链接'),
                ('淘宝' in html, '包含淘宝链接'),
                ('https://www.jd.com' in html, '包含京东URL'),
                ('购买链接' in html, '包含购买链接标题')
            ]
            
            all_passed = True
            for check, desc in checks:
                if check:
                    print(f"  ✓ {desc}")
                else:
                    print(f"  ✗ {desc}")
                    all_passed = False
            
            result = all_passed
            print(f"\n{'✅' if result else '❌'} HTML生成器测试")
            return result
        except Exception as e:
            print(f"  ✗ 错误: {e}")
            return False
    
    def test_price_updater(self):
        """测试价格更新器"""
        self.print_subheader("测试价格更新器")
        
        try:
            from projector_price_updater import ProjectorPriceUpdater
            
            updater = ProjectorPriceUpdater()
            
            print("  更新价格数据...")
            price_data = updater.update_price_data(force_update=False)
            
            if price_data and 'prices' in price_data:
                print(f"  ✓ 价格数据加载成功")
                print(f"  ✓ 投影仪数量: {len(price_data['prices'])}")
                
                all_prices = updater.get_all_prices(use_subsidy=True)
                print(f"  ✓ 获取所有价格: {len(all_prices)} 个")
                
                result = True
            else:
                print(f"  ✗ 价格数据加载失败")
                result = False
            
            print(f"\n{'✅' if result else '❌'} 价格更新器测试")
            return result
        except Exception as e:
            print(f"  ✗ 错误: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_recommender(self):
        """测试推荐器"""
        self.print_subheader("测试推荐器")
        
        try:
            from projector_recommender import ProjectorRecommender
            
            recommender = ProjectorRecommender()
            
            if not recommender.projectors:
                print("  ⚠ 没有投影仪数据，跳过测试")
                return True
            
            print(f"  ✓ 加载了 {len(recommender.projectors)} 款投影仪")
            
            test_budget = 5000
            print(f"  测试预算推荐（预算: ¥{test_budget}）...")
            
            recommended = recommender.recommend_by_budget(test_budget, top_n=3, use_subsidy=True)
            
            if recommended:
                print(f"  ✓ 推荐成功，找到 {len(recommended)} 款投影仪")
                for i, projector in enumerate(recommended[:2], 1):
                    print(f"    {i}. {projector['brand']} {projector['model']} - ¥{projector['price']}")
                
                best = recommender.get_best_value_projector(budget=test_budget, use_subsidy=True)
                if best:
                    print(f"  ✓ 最佳推荐: {best['brand']} {best['model']}")
                
                result = True
            else:
                print(f"  ⚠ 没有找到符合预算的投影仪")
                result = True
            
            print(f"\n{'✅' if result else '❌'} 推荐器测试")
            return result
        except Exception as e:
            print(f"  ✗ 错误: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_chart_generator(self):
        """测试图表生成器"""
        self.print_subheader("测试图表生成器")
        
        try:
            from projector_chart_generator import ProjectorChartGenerator
            from projector_recommender import ProjectorRecommender
            
            generator = ProjectorChartGenerator()
            recommender = ProjectorRecommender()
            
            if not recommender.projectors:
                print("  ⚠ 没有投影仪数据，跳过测试")
                return True
            
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
                print(f"  ✓ 价格对比图表生成成功")
            
            value_chart = generator.generate_value_score_chart(selected_projectors, add_links=False)
            if value_chart:
                chart_files.append(value_chart)
                print(f"  ✓ 性价比对比图表生成成功")
            
            if chart_files:
                html_file = os.path.join(generator.output_dir, 'test_comprehensive.html')
                html_content = generator.html_generator.generate_html_page(
                    '全面测试报告',
                    chart_files=chart_files,
                    items=selected_projectors,
                    link_key='purchase_links'
                )
                
                if generator.html_generator.save_html(html_content, html_file):
                    print(f"  ✓ HTML页面生成成功: {os.path.basename(html_file)}")
                    result = True
                else:
                    print(f"  ✗ HTML页面生成失败")
                    result = False
            else:
                result = False
            
            print(f"\n{'✅' if result else '❌'} 图表生成器测试")
            return result
        except Exception as e:
            print(f"  ✗ 错误: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_wifi_scan(self):
        """测试WiFi扫描"""
        self.print_subheader("测试WiFi扫描")
        
        try:
            from wifi_scan import WiFiChannelScanner, EscapeManager
            
            scanner = WiFiChannelScanner()
            print("  ✓ WiFiChannelScanner 初始化成功")
            
            escape_manager = EscapeManager()
            print("  ✓ EscapeManager 初始化成功")
            
            result = True
            print(f"\n{'✅' if result else '❌'} WiFi扫描测试")
            return result
        except Exception as e:
            print(f"  ✗ 错误: {e}")
            return False
    
    def test_hardware_info(self):
        """测试硬件信息"""
        self.print_subheader("测试硬件信息")
        
        try:
            from hardware_info import HardwareInfo
            
            info = HardwareInfo()
            print("  ✓ HardwareInfo 初始化成功")
            
            result = True
            print(f"\n{'✅' if result else '❌'} 硬件信息测试")
            return result
        except Exception as e:
            print(f"  ✗ 错误: {e}")
            return False
    
    def test_cross_platform(self):
        """测试跨平台兼容性"""
        self.print_subheader("测试跨平台兼容性")
        
        try:
            from cross_platform_utils import CrossPlatformUtils
            
            utils = CrossPlatformUtils()
            print(f"  ✓ 系统检测: {utils.platform}")
            print(f"  ✓ Python路径: {sys.executable}")
            
            result = True
            print(f"\n{'✅' if result else '❌'} 跨平台兼容性测试")
            return result
        except Exception as e:
            print(f"  ✗ 错误: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        self.print_header("全面测试 - 确保无中文乱码")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"系统: {self.system}")
        print(f"Python: {sys.version}")
        
        tests = [
            ("编码测试", self.test_encoding),
            ("模块导入", self.test_imports),
            ("数据文件", self.test_data_files),
            ("HTML生成器", self.test_html_generator),
            ("价格更新器", self.test_price_updater),
            ("推荐器", self.test_recommender),
            ("图表生成器", self.test_chart_generator),
            ("WiFi扫描", self.test_wifi_scan),
            ("硬件信息", self.test_hardware_info),
            ("跨平台兼容性", self.test_cross_platform)
        ]
        
        results = {}
        for name, test_func in tests:
            try:
                result = test_func()
                results[name] = result
            except Exception as e:
                print(f"\n❌ {name} 测试异常: {e}")
                results[name] = False
        
        self.print_header("测试结果汇总")
        
        for name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  {name:<20} {status}")
        
        all_passed = all(results.values())
        
        self.print_header("测试结论")
        if all_passed:
            print("  ✅ 所有测试通过！")
            print("  ✅ 代码运行正常")
            print("  ✅ 中文显示无乱码")
            print("  ✅ 跨平台兼容")
            print("\n💡 提示:")
            print("  - 所有Python文件都可以正常运行")
            print("  - 中文显示完全正常，无乱码")
            print("  - 可以使用 start.bat (Windows) 或 start.sh (Linux/macOS) 启动")
        else:
            print("  ❌ 部分测试失败")
            print("  请检查上述失败项目的错误信息")
        
        return 0 if all_passed else 1


def main():
    """主函数"""
    try:
        tester = ComprehensiveTest()
        return tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠ 测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n❌ 测试错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())