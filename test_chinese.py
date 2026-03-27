#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文乱码测试脚本
测试WiFi扫描工具的中文显示和文件处理功能
"""

import sys
import os
import json
import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from wifi_scan import WiFiChannelScanner, EscapeManager

def test_chinese_output():
    """测试中文输出功能"""
    print("=" * 60)
    print("中文乱码测试 - 输出显示测试")
    print("=" * 60)
    
    # 测试各种中文字符串
    test_strings = [
        "WiFi信道扫描工具",
        "安徽省合肥市庐阳区",
        "中国移动5G网络",
        "TP-LINK_5G_高速路由器",
        "测试中文乱码修复功能"
    ]
    
    for i, text in enumerate(test_strings, 1):
        try:
            print(f"测试 {i}: {text}")
        except UnicodeEncodeError as e:
            print(f"测试 {i} 编码错误: {e}")
    
    print("\n输出测试完成!")

def test_escape_manager():
    """测试转义管理器功能"""
    print("\n" + "=" * 60)
    print("中文乱码测试 - 转义管理器测试")
    print("=" * 60)
    
    escape_manager = EscapeManager()
    
    # 测试乱码检测
    test_cases = [
        ("正常中文", "中国移动", False),
        ("乱码字符", "中国�移动", True),
        ("长乱码", "安徽省合肥市庐阳区逍遥津街道县桥社区", False),
        ("控制字符", "WiFi\x00网络", True),
        ("品牌名称", "TP-LINK_5G", False)
    ]
    
    for name, text, expected in test_cases:
        result = escape_manager.is_garbled_ssid(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} {name}: '{text}' -> 乱码: {result} (期望: {expected})")
    
    # 测试中文翻译
    print("\n中文翻译测试:")
    translations = [
        ("China", "中国"),
        ("Beijing", "北京"),
        ("China Mobile", "中国移动"),
        ("Anhui", "安徽")
    ]
    
    for en, expected_cn in translations:
        result = escape_manager.translate_country(en) if en in ["China", "Beijing"] else \
                 escape_manager.translate_isp(en) if "Mobile" in en else \
                 escape_manager.translate_region(en)
        status = "✓" if result == expected_cn else "✗"
        print(f"{status} {en} -> {result} (期望: {expected_cn})")

def test_file_operations():
    """测试文件操作中的中文处理"""
    print("\n" + "=" * 60)
    print("中文乱码测试 - 文件操作测试")
    print("=" * 60)
    
    # 创建测试数据
    test_data = {
        "scan_time": datetime.datetime.now().isoformat(),
        "location": {
            "country": "中国",
            "region": "安徽省",
            "city": "合肥市",
            "district": "庐阳区"
        },
        "current_wifi": {
            "ssid": "TP-LINK_5G_高速路由器"
        },
        "network_details": [
            {"ssid": "中国移动5G", "channel": 36, "rssi_dbm": -65},
            {"ssid": "TP-LINK_2.4G", "channel": 6, "rssi_dbm": -72}
        ]
    }
    
    # 测试JSON文件写入
    test_filename = "测试中文文件名.json"
    try:
        with open(test_filename, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        print(f"✓ JSON文件写入成功: {test_filename}")
        
        # 测试JSON文件读取
        with open(test_filename, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        print(f"✓ JSON文件读取成功")
        
        # 清理测试文件
        os.remove(test_filename)
        print("✓ 测试文件清理完成")
        
    except Exception as e:
        print(f"✗ 文件操作失败: {e}")

def test_scanner_initialization():
    """测试扫描器初始化"""
    print("\n" + "=" * 60)
    print("中文乱码测试 - 扫描器初始化测试")
    print("=" * 60)
    
    try:
        scanner = WiFiChannelScanner()
        print("✓ WiFiChannelScanner初始化成功")
        
        # 测试平台信息获取
        platform_info = scanner.get_platform_info()
        print(f"✓ 平台信息: {platform_info}")
        
        # 测试转义管理器
        escape_manager = scanner.escape_manager
        print("✓ 转义管理器访问成功")
        
        return scanner
    except Exception as e:
        print(f"✗ 扫描器初始化失败: {e}")
        return None

def main():
    """主测试函数"""
    print("开始中文乱码测试...\n")
    
    # 设置UTF-8编码环境
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # 运行各项测试
    test_chinese_output()
    test_escape_manager()
    test_file_operations()
    scanner = test_scanner_initialization()
    
    print("\n" + "=" * 60)
    print("中文乱码测试完成!")
    print("=" * 60)
    
    if scanner:
        print("\n提示: 可以运行以下命令进行完整测试:")
        print("python wifi_scan.py --debug")
        print("wifi_scan.bat --debug")

if __name__ == "__main__":
    main()