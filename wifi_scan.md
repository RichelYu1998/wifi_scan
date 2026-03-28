# WiFi扫描工具 (WiFiScanner)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

扫描周围WiFi网络并显示详细信息

[快速开始](#-快速开始) • [功能介绍](#-功能介绍) • [API文档](#-api文档)

</div>

---

## 📋 目录

- [项目简介](#-项目简介)
- [功能介绍](#-功能介绍)
- [快速开始](#-快速开始)
- [API文档](#-api文档)
- [使用示例](#-使用示例)
- [版本历史](#-版本历史)
- [许可证](#-许可证)

## 🎯 项目简介

WiFi扫描工具是一个功能强大的WiFi网络扫描器，可以扫描周围WiFi网络并显示详细信息。

### 特点

- ✅ **WiFi扫描** - 扫描周围WiFi网络
- ✅ **详细信息** - 显示网络详细信息
- ✅ **网卡检测** - 检测网络卡信息
- ✅ **中文支持** - 中文显示无乱码

## ✨ 功能介绍

### 1. WiFi扫描
- 扫描周围WiFi网络
- 显示信号强度
- 显示加密方式
- 显示网络频道

### 2. 网络信息
- SSID（网络名称）
- BSSID（MAC地址）
- 信号强度
- 加密方式
- 网络频道
- 网络类型

### 3. 网卡检测
- 网卡型号
- 网卡带宽
- 网卡驱动
- 网卡状态

## 🚀 快速开始

### 基本使用

```python
from wifi_scan import WiFiScanner

# 创建扫描器实例
scanner = WiFiScanner()

# 扫描WiFi网络
networks = scanner.scan_networks()

# 显示扫描结果
for network in networks:
    print(f"SSID: {network['ssid']}")
    print(f"信号强度: {network['signal']}")
    print(f"加密方式: {network['encryption']}")
    print()
```

### 命令行使用

```bash
python wifi_scan.py
```

## 🔧 API文档

### WiFiScanner类

#### `__init__()`
初始化WiFi扫描器。

**参数**: 无

**返回**: 无

**示例**:
```python
scanner = WiFiScanner()
```

#### `scan_networks()`
扫描WiFi网络。

**参数**: 无

**返回**: list - WiFi网络列表

**示例**:
```python
networks = scanner.scan_networks()
```

#### `get_network_info(ssid)`
获取指定网络的信息。

**参数**:
- `ssid` (str): 网络SSID

**返回**: dict - 网络信息

**示例**:
```python
info = scanner.get_network_info('WiFi-Name')
```

#### `get_network_card_info()`
获取网络卡信息。

**参数**: 无

**返回**: dict - 网络卡信息

**示例**:
```python
card_info = scanner.get_network_card_info()
```

## 💡 使用示例

### 示例1：基本扫描

```python
from wifi_scan import WiFiScanner

scanner = WiFiScanner()
networks = scanner.scan_networks()

for network in networks:
    print(f"SSID: {network['ssid']}")
    print(f"信号强度: {network['signal']}")
    print(f"加密方式: {network['encryption']}")
    print(f"频道: {network['channel']}")
    print()
```

### 示例2：获取网络卡信息

```python
from wifi_scan import WiFiScanner

scanner = WiFiScanner()
card_info = scanner.get_network_card_info()

print(f"网卡型号: {card_info['model']}")
print(f"网卡带宽: {card_info['bandwidth']}")
print(f"网卡驱动: {card_info['driver']}")
```

## 📝 版本历史

### v2.2.0 (2026-03-28)
- 🎉 初始版本
- ✨ 扫描WiFi网络
- ✨ 显示网络详细信息
- ✨ 检测网络卡信息
- ✨ 中文显示无乱码

### v2.1.0 (2026-03-28)
- 🎉 项目基础版本
- ✨ WiFi扫描功能
- ✨ 网络信息检测
- ✨ 网卡检测功能

## 📄 许可证

MIT License

---

<div align="center">

**项目状态**: ✅ 完成
**当前版本**: v2.2.0
**中文支持**: ✅ 完全支持，无乱码

如果这个项目对您有帮助，请给我们一个 ⭐️

</div>