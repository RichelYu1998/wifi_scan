# WiFi扫描工具

## 📋 概述

`wifi_scan.py` 提供WiFi网络扫描功能，用于检测和分析周围的无线网络。

## 🎯 主要功能

### 1. 网络扫描
- 扫描周围所有可用的WiFi网络
- 显示网络基本信息（SSID、信号强度、加密方式）

### 2. 网络详细信息
- 显示网络SSID名称
- 显示信号强度（dBm格式）
- 显示加密方式（WPA2、WPA、WEP、Open）
- 显示网络频道
- 显示BSSID（MAC地址）

### 3. 网络质量评估
- 信号强度等级评估（优秀、良好、一般、差）
- 加密安全性评估
- 频道干扰分析

## 🔧 技术实现

### 平台支持
- **Windows**: 使用`netsh`命令扫描网络
- **Linux**: 使用`iwlist`工具扫描网络
- **macOS**: 使用`airport`命令扫描网络

### 扫描方法
```python
def scan_wifi():
    """扫描WiFi网络"""
    if platform.system() == 'Windows':
        return _scan_windows()
    elif platform.system() == 'Linux':
        return _scan_linux()
    elif platform.system() == 'Darwin':
        return _scan_macos()
```

### 数据结构
```python
{
    'ssid': '网络名称',
    'bssid': 'MAC地址',
    'signal': '信号强度',
    'channel': '频道',
    'encryption': '加密方式',
    'quality': '信号质量'
}
```

## 📊 输出格式

### 网络列表显示
```
=== WiFi网络扫描结果 ===

1. WiFi名称
   SSID: MyWiFi
   信号强度: -45dBm (优秀)
   加密方式: WPA2-PSK
   频道: 6
   BSSID: 00:11:22:33:44:55:66

2. WiFi名称
   SSID: GuestWiFi
   信号强度: -65dBm (一般)
   加密方式: WPA-PSK
   频道: 11
   BSSID: 00:11:22:33:44:55:77
```

### 信号质量评估
- **优秀**: > -50dBm
- **良好**: -50dBm 到 -70dBm
- **一般**: -70dBm 到 -85dBm
- **差**: < -85dBm

## 🔧 系统要求

### Python依赖
```python
# Windows
import subprocess
import re

# Linux
import subprocess
import re

# macOS
import subprocess
import re
```

### 系统要求
- Python 3.7+
- Windows 10/11 或 Linux/macOS
- 管理员权限（用于网络扫描）

## 📝 使用示例

### 基本扫描
```python
from wifi_scan import scan_wifi

networks = scan_wifi()
for network in networks:
    print(f"SSID: {network['ssid']}")
    print(f"信号: {network['signal']}dBm")
```

### 集成调用
```python
from integrated_system import WiFiRecommender

recommender = WiFiRecommender()
recommender.scan_networks()
```

## 🐛 故障排除

### 常见问题

#### 1. 无法扫描网络
**问题**: 扫描结果为空
**解决**: 
- 检查WiFi适配器是否正常工作
- 确认有管理员权限
- 检查WiFi服务是否启动

#### 2. 信号强度显示异常
**问题**: 信号强度数值不合理
**解决**: 
- 重新扫描网络
- 检查WiFi驱动是否正常

#### 3. 编码方式显示错误
**问题**: 加密方式显示不正确
**解决**: 
- 更新WiFi扫描算法
- 检查网络适配器兼容性

## 📞 版本信息

- **版本**: v1.0.0
- **更新日期**: 2026-03-28
- **支持平台**: Windows、Linux、macOS

## 🎉 特色功能

1. **跨平台支持**: 支持三大操作系统
2. **详细网络信息**: 提供完整的网络参数
3. **信号质量评估**: 智能评估网络质量
4. **加密安全分析**: 分析网络安全级别
5. **频道干扰检测**: 分析频道使用情况

---

**享受使用WiFi扫描工具！** 📶