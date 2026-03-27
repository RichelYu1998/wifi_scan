#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨平台功能测试脚本 - 测试所有模块的跨平台兼容性
"""

import sys
import os
import platform

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cross_platform_utils():
    """测试跨平台工具类"""
    print("=== 测试跨平台工具类 ===")
    
    try:
        from cross_platform_utils import CrossPlatformUtils, get_cross_platform_utils
        utils = CrossPlatformUtils(debug_mode=True)
        
        print(f"✅ 跨平台工具类导入成功")
        print(f"   平台信息: {utils.get_platform_info()}")
        print(f"   系统编码: {utils.encoding}")
        
        # 测试命令执行
        if utils.is_windows():
            result = utils.run_command(["ipconfig"])
            print(f"   ipconfig测试: {'成功' if result else '失败'}")
        elif utils.is_macos():
            result = utils.run_command(["ifconfig"])
            print(f"   ifconfig测试: {'成功' if result else '失败'}")
        else:
            result = utils.run_command(["ifconfig"])
            print(f"   ifconfig测试: {'成功' if result else '失败'}")
            
        return True
    except Exception as e:
        print(f"❌ 跨平台工具类测试失败: {e}")
        return False

def test_hardware_info():
    """测试硬件信息检测器"""
    print("\n=== 测试硬件信息检测器 ===")
    
    try:
        from hardware_info import HardwareInfo
        hw = HardwareInfo()
        info = hw.get_hardware_info()
        
        print(f"✅ 硬件信息检测器导入成功")
        print(f"   CPU: {info['cpu']['名称']}")
        print(f"   显卡: {info['gpu']['名称']}")
        print(f"   内存: {info['memory']['总容量_GB']}GB")
        print(f"   性能评分: {info['performance_score']}")
        
        return True
    except Exception as e:
        print(f"❌ 硬件信息检测器测试失败: {e}")
        return False

def test_network_speed_tester():
    """测试网络速度测试器"""
    print("\n=== 测试网络速度测试器 ===")
    
    try:
        from network_speed_tester import NetworkSpeedTester
        tester = NetworkSpeedTester()
        info = tester.test_network_speed(use_system_command=False)  # 使用下载测速避免权限问题
        
        print(f"✅ 网络速度测试器导入成功")
        print(f"   下载速度: {info['下载速度_Mbps']} Mbps")
        print(f"   上传速度: {info['上传速度_Mbps']} Mbps")
        print(f"   延迟: {info['延迟_ms']} ms")
        
        return True
    except Exception as e:
        print(f"❌ 网络速度测试器测试失败: {e}")
        return False

def test_video_resolution_recommender():
    """测试视频分辨率推荐器"""
    print("\n=== 测试视频分辨率推荐器 ===")
    
    try:
        from video_resolution_recommender import VideoResolutionRecommender
        recommender = VideoResolutionRecommender()
        
        print(f"✅ 视频分辨率推荐器导入成功")
        
        # 测试不同网速下的推荐
        test_speeds = [5, 10, 50]
        for speed in test_speeds:
            recommendations = recommender.recommend_resolution(speed)
            print(f"   {speed}Mbps推荐: {list(recommendations.keys())}")
        
        return True
    except Exception as e:
        print(f"❌ 视频分辨率推荐器测试失败: {e}")
        return False

def test_wifi_scan():
    """测试WiFi扫描器"""
    print("\n=== 测试WiFi扫描器 ===")
    
    try:
        from wifi_scan import WiFiChannelScanner
        scanner = WiFiChannelScanner()
        
        print(f"✅ WiFi扫描器导入成功")
        print(f"   平台: {scanner.platform}")
        print(f"   日志目录: {scanner.log_dir}")
        
        # 测试当前WiFi信息获取
        wifi_info = scanner.get_current_wifi_info()
        print(f"   当前WiFi: {wifi_info.get('ssid', '未连接')}")
        
        return True
    except Exception as e:
        print(f"❌ WiFi扫描器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始跨平台功能测试")
    print(f"当前系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {platform.python_version()}")
    print("=" * 50)
    
    # 运行所有测试
    tests = [
        test_cross_platform_utils,
        test_hardware_info,
        test_network_speed_tester,
        test_video_resolution_recommender,
        test_wifi_scan
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试函数 {test_func.__name__} 执行异常: {e}")
            results.append(False)
    
    # 统计测试结果
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有模块跨平台兼容性测试通过！")
    else:
        print("⚠️  部分模块测试失败，请检查错误信息")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)