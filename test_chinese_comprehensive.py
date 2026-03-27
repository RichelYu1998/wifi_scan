#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面中文乱码测试脚本
测试WiFi扫描工具的所有中文显示和文件处理功能
"""

import sys
import os
import json
import datetime
import re

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from wifi_scan import WiFiChannelScanner, EscapeManager

def test_control_panel_comparison():
    """测试控制面板网卡信息与代码获取信息的一致性"""
    print("=" * 70)
    print("控制面板网卡信息对比测试")
    print("=" * 70)
    
    # 控制面板中显示的网卡信息
    control_panel_info = {
        "名称": "WLAN",
        "接口描述": "Realtek 8811CU Wireless LAN 802.11ac USB NIC",
        "状态": "Up",
        "链接速度": "433.3 Mbps"
    }
    
    print("控制面板中的网卡信息:")
    for key, value in control_panel_info.items():
        print(f"  {key}: {value}")
    
    # 测试代码获取的网卡信息
    scanner = WiFiChannelScanner()
    wifi_info = scanner.get_current_wifi_info()
    
    if wifi_info:
        print("\n代码获取的网卡信息:")
        for key, value in wifi_info.items():
            print(f"  {key}: {repr(value)}")
        
        # 检查网卡描述信息
        description_fields = ['说明', 'Description', '描述', '网卡描述', '网卡完整描述']
        code_description = None
        for field in description_fields:
            if field in wifi_info:
                code_description = wifi_info[field]
                print(f"\n找到网卡描述字段 '{field}': {repr(code_description)}")
                break
        
        # 对比控制面板和代码获取的信息
        if code_description:
            control_description = control_panel_info["接口描述"]
            if code_description == control_description:
                print("✅ 网卡描述信息与控制面板一致")
            else:
                print(f"❌ 网卡描述信息不一致:")
                print(f"   控制面板: {repr(control_description)}")
                print(f"   代码获取: {repr(code_description)}")
        else:
            print("❌ 代码无法获取网卡描述信息")
    else:
        print("❌ 无法获取WiFi信息")

def test_chinese_output_comprehensive():
    """全面测试中文输出功能"""
    print("\n" + "=" * 70)
    print("全面中文输出测试")
    print("=" * 70)
    
    # 测试各种中文字符串
    test_strings = [
        "WiFi信道扫描工具",
        "安徽省合肥市庐阳区逍遥津街道",
        "中国移动5G网络",
        "Realtek 8811CU Wireless LAN 802.11ac USB NIC",
        "小旭二手手机",
        "基于周围WiFi信道优化推荐",
        "测试中文乱码修复功能",
        "灏忔棴浜屾墜鎵嬫満"  # 这是乱码SSID
    ]
    
    print("中文字符串输出测试:")
    for i, text in enumerate(test_strings, 1):
        try:
            print(f"  {i:2d}. {text}")
        except UnicodeEncodeError as e:
            print(f"  {i:2d}. ❌ 编码错误: {e}")
    
    print("\n输出测试完成!")

def test_json_file_chinese():
    """测试JSON文件中的中文处理"""
    print("\n" + "=" * 70)
    print("JSON文件中文处理测试")
    print("=" * 70)
    
    # 检查最新的JSON文件
    log_dir = "wifi_logs"
    if os.path.exists(log_dir):
        json_files = [f for f in os.listdir(log_dir) if f.endswith('.json')]
        if json_files:
            latest_file = max(json_files, key=lambda f: os.path.getmtime(os.path.join(log_dir, f)))
            file_path = os.path.join(log_dir, latest_file)
            
            print(f"检查最新JSON文件: {latest_file}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 检查文件中的中文内容
                issues_found = []
                
                # 检查网卡信息
                if isinstance(data, list) and len(data) > 0:
                    latest_scan = data[-1]
                    
                    # 检查网卡信息
                    if 'network_card' in latest_scan:
                        network_card = latest_scan['network_card']
                        print("\n网卡信息检查:")
                        for key, value in network_card.items():
                            if isinstance(value, str):
                                # 检查是否包含乱码字符
                                if '�' in value or '\ufffd' in value:
                                    issues_found.append(f"网卡信息字段 '{key}' 包含乱码: {repr(value)}")
                                    print(f"  ❌ {key}: {repr(value)} (包含乱码)")
                                else:
                                    print(f"  ✅ {key}: {repr(value)}")
                    
                    # 检查地理位置信息
                    if 'location' in latest_scan:
                        location = latest_scan['location']
                        print("\n地理位置信息检查:")
                        for key, value in location.items():
                            if isinstance(value, str):
                                if '�' in value or '\ufffd' in value:
                                    issues_found.append(f"地理位置字段 '{key}' 包含乱码: {repr(value)}")
                                    print(f"  ❌ {key}: {repr(value)} (包含乱码)")
                                else:
                                    print(f"  ✅ {key}: {repr(value)}")
                    
                    # 检查当前WiFi信息
                    if 'current_wifi' in latest_scan:
                        current_wifi = latest_scan['current_wifi']
                        print("\n当前WiFi信息检查:")
                        for key, value in current_wifi.items():
                            if isinstance(value, str):
                                if '�' in value or '\ufffd' in value:
                                    issues_found.append(f"WiFi信息字段 '{key}' 包含乱码: {repr(value)}")
                                    print(f"  ❌ {key}: {repr(value)} (包含乱码)")
                                else:
                                    print(f"  ✅ {key}: {repr(value)}")
                
                if not issues_found:
                    print("\n✅ JSON文件中没有发现中文乱码问题")
                else:
                    print(f"\n❌ 发现 {len(issues_found)} 个中文乱码问题:")
                    for issue in issues_found:
                        print(f"  - {issue}")
                        
            except Exception as e:
                print(f"❌ 读取JSON文件失败: {e}")
        else:
            print("❌ 没有找到JSON文件")
    else:
        print("❌ wifi_logs目录不存在")

def test_escape_manager_comprehensive():
    """全面测试转义管理器功能"""
    print("\n" + "=" * 70)
    print("转义管理器全面测试")
    print("=" * 70)
    
    escape_manager = EscapeManager()
    
    # 测试乱码检测
    test_cases = [
        ("正常中文", "中国移动", False),
        ("乱码字符", "中国�移动", True),
        ("长中文", "安徽省合肥市庐阳区逍遥津街道县桥社区", False),
        ("控制字符", "WiFi\x00网络", True),
        ("品牌名称", "TP-LINK_5G", False),
        ("网卡型号", "Realtek 8811CU Wireless LAN 802.11ac USB NIC", False),
        ("乱码SSID", "灏忔棴浜屾墜鎵嬫満", True)
    ]
    
    print("乱码检测测试:")
    all_passed = True
    for name, text, expected in test_cases:
        result = escape_manager.is_garbled_ssid(text)
        status = "✓" if result == expected else "✗"
        if result != expected:
            all_passed = False
        print(f"  {status} {name}: '{text}' -> 乱码: {result} (期望: {expected})")
    
    if all_passed:
        print("✅ 所有乱码检测测试通过")
    else:
        print("❌ 部分乱码检测测试失败")

def main():
    """主测试函数"""
    print("开始全面中文乱码测试...\n")
    
    # 设置UTF-8编码环境
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # 运行各项测试
    test_control_panel_comparison()
    test_chinese_output_comprehensive()
    test_json_file_chinese()
    test_escape_manager_comprehensive()
    
    print("\n" + "=" * 70)
    print("全面中文乱码测试完成!")
    print("=" * 70)

if __name__ == "__main__":
    main()