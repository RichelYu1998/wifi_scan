#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一启动脚本 - 跨平台支持（Windows/Linux/macOS）
"""

import sys
import os
import subprocess
import platform
from pathlib import Path


class CrossPlatformLauncher:
    """跨平台启动器"""
    
    def __init__(self):
        self.system = platform.system()
        self.project_dir = Path(__file__).parent.absolute()
        self.python_exe = self._get_python_exe()
        
    def _get_python_exe(self):
        """获取Python可执行文件路径"""
        if self.system == 'Windows':
            venv_python = self.project_dir / '.venv' / 'Scripts' / 'python.exe'
        else:
            venv_python = self.project_dir / '.venv' / 'bin' / 'python'
        
        if venv_python.exists():
            return str(venv_python)
        else:
            return sys.executable
    
    def _setup_environment(self):
        """设置环境"""
        venv_dir = self.project_dir / '.venv'
        
        if not venv_dir.exists():
            print("🔄 创建虚拟环境...")
            subprocess.run([sys.executable, '-m', 'venv', str(venv_dir)], 
                        check=True, capture_output=True)
            print("✅ 虚拟环境创建成功")
        
        print("🔄 安装依赖...")
        requirements_file = self.project_dir / 'requirements.txt'
        if requirements_file.exists():
            subprocess.run([self.python_exe, '-m', 'pip', 'install', '-q', '-r', str(requirements_file)],
                        check=True, capture_output=True)
            print("✅ 依赖安装完成")
        else:
            print("⚠️ requirements.txt 不存在，跳过依赖安装")
    
    def _run_script(self, script_name, args=None):
        """运行脚本"""
        script_path = self.project_dir / script_name
        
        if not script_path.exists():
            print(f"❌ 脚本不存在: {script_name}")
            return False
        
        print(f"\n{'='*60}")
        print(f"运行: {script_name}")
        print(f"{'='*60}\n")
        
        cmd = [self.python_exe, str(script_path)]
        if args:
            cmd.extend(args)
        
        try:
            result = subprocess.run(cmd, cwd=str(self.project_dir), check=True)
            print(f"\n✅ {script_name} 运行成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"\n❌ {script_name} 运行失败: {e}")
            return False
        except KeyboardInterrupt:
            print(f"\n⚠️ {script_name} 被用户中断")
            return False
    
    def _test_all_scripts(self):
        """测试所有脚本"""
        print("\n" + "="*60)
        print("测试所有Python脚本")
        print("="*60 + "\n")
        
        scripts = [
            'test_all.py',
            'wifi_scan.py',
            'hardware_info.py',
            'projector_recommender.py',
            'projector_price_updater.py',
            'projector_chart_generator.py',
            'quick_start.py'
        ]
        
        results = {}
        for script in scripts:
            print(f"\n测试: {script}")
            print("-"*60)
            result = self._run_script(script)
            results[script] = result
        
        print("\n" + "="*60)
        print("测试结果汇总")
        print("="*60)
        for script, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{script:<35} {status}")
        
        all_passed = all(results.values())
        print("\n" + "="*60)
        if all_passed:
            print("✅ 所有测试通过！")
        else:
            print("❌ 部分测试失败")
        print("="*60)
        
        return all_passed
    
    def _show_menu(self):
        """显示菜单"""
        print("\n" + "="*60)
        print("投影仪推荐系统 - 统一启动器")
        print("="*60)
        print(f"系统: {self.system}")
        print(f"Python: {self.python_exe}")
        print("="*60)
        print("选择功能:")
        print("="*60)
        print("1. WiFi扫描工具")
        print("   扫描周围WiFi网络，显示网络详细信息")
        print()
        print("2. 硬件信息检测")
        print("   检测CPU、GPU、内存、硬盘等硬件信息")
        print()
        print("3. 投影仪推荐器（交互式）")
        print("   根据预算推荐性价比最高的投影仪")
        print("   支持国补价格对比和购买链接")
        print()
        print("4. 投影仪图表生成器")
        print("   生成价格对比、性价比对比等图表")
        print("   自动生成包含购买链接的HTML报告")
        print()
        print("5. 价格数据更新")
        print("   从网络更新最新的投影仪价格数据")
        print("   支持国补价格计算")
        print()
        print("6. 快速启动（完整流程）")
        print("   一键执行：更新数据+生成图表+生成报告")
        print()
        print("7. 运行所有测试")
        print("   运行全面测试，确保所有功能正常")
        print("   验证中文显示无乱码")
        print()
        print("8. 视频分辨率推荐")
        print("   根据屏幕尺寸和观看距离推荐最佳分辨率")
        print()
        print("9. 网络速度测试")
        print("   测试网络上传和下载速度")
        print()
        print("0. 退出")
        print("   退出程序")
        print("="*60)
    
    def run(self):
        """运行启动器"""
        print("\n🔄 初始化环境...")
        self._setup_environment()
        
        while True:
            self._show_menu()
            
            try:
                choice = input("\n请选择功能 (0-9): ").strip()
                
                if choice == '0':
                    print("\n👋 再见！")
                    break
                elif choice == '1':
                    self._run_script('wifi_scan.py')
                elif choice == '2':
                    self._run_script('hardware_info.py')
                elif choice == '3':
                    self._run_script('projector_recommender.py')
                elif choice == '4':
                    self._run_script('projector_chart_generator.py')
                elif choice == '5':
                    self._run_script('projector_price_updater.py')
                elif choice == '6':
                    self._run_script('quick_start.py')
                elif choice == '7':
                    self._test_all_scripts()
                elif choice == '8':
                    self._run_script('video_resolution_recommender.py')
                elif choice == '9':
                    self._run_script('network_speed_tester.py')
                else:
                    print("\n❌ 无效选择，请重新输入")
                
                input("\n按回车键继续...")
                
            except KeyboardInterrupt:
                print("\n\n👋 用户中断操作")
                break
            except Exception as e:
                print(f"\n❌ 错误: {e}")
                input("\n按回车键继续...")


def main():
    """主函数"""
    try:
        launcher = CrossPlatformLauncher()
        launcher.run()
    except Exception as e:
        print(f"❌ 启动器错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())