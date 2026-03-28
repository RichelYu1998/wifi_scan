# 硬件信息检测 (HardwareInfo)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

检测CPU、GPU、内存、硬盘等硬件信息

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

硬件信息检测是一个功能强大的硬件检测工具，可以检测CPU、GPU、内存、硬盘等硬件信息。

### 特点

- ✅ **CPU检测** - 检测CPU型号、核心数、频率等
- ✅ **GPU检测** - 检测GPU型号、显存等
- ✅ **内存检测** - 检测内存容量、频率等
- ✅ **硬盘检测** - 检测硬盘容量、类型等
- ✅ **网卡检测** - 检测网卡型号、带宽等

## ✨ 功能介绍

### 1. CPU信息
- CPU型号
- 核心数
- 线程数
- 频率
- 架构

### 2. GPU信息
- GPU型号
- 显存大小
- 显卡驱动
- 显卡厂商

### 3. 内存信息
- 内存容量
- 内存频率
- 内存类型
- 内存插槽

### 4. 硬盘信息
- 硬盘容量
- 硬盘类型
- 硬盘转速
- 硬盘接口

### 5. 网卡信息
- 网卡型号
- 网卡带宽
- 网卡驱动
- 网卡状态

## 🚀 快速开始

### 基本使用

```python
from hardware_info import HardwareInfo

# 创建检测器实例
detector = HardwareInfo()

# 检测所有硬件信息
info = detector.get_all_info()

# 显示硬件信息
print(f"CPU: {info['cpu']['model']}")
print(f"GPU: {info['gpu']['model']}")
print(f"内存: {info['memory']['capacity']}")
print(f"硬盘: {info['disk']['capacity']}")
```

### 命令行使用

```bash
python hardware_info.py
```

## 🔧 API文档

### HardwareInfo类

#### `__init__()`
初始化硬件信息检测器。

**参数**: 无

**返回**: 无

**示例**:
```python
detector = HardwareInfo()
```

#### `get_cpu_info()`
获取CPU信息。

**参数**: 无

**返回**: dict - CPU信息

**示例**:
```python
cpu_info = detector.get_cpu_info()
```

#### `get_gpu_info()`
获取GPU信息。

**参数**: 无

**返回**: dict - GPU信息

**示例**:
```python
gpu_info = detector.get_gpu_info()
```

#### `get_memory_info()`
获取内存信息。

**参数**: 无

**返回**: dict - 内存信息

**示例**:
```python
memory_info = detector.get_memory_info()
```

#### `get_disk_info()`
获取硬盘信息。

**参数**: 无

**返回**: dict - 硬盘信息

**示例**:
```python
disk_info = detector.get_disk_info()
```

#### `get_network_info()`
获取网卡信息。

**参数**: 无

**返回**: dict - 网卡信息

**示例**:
```python
network_info = detector.get_network_info()
```

#### `get_all_info()`
获取所有硬件信息。

**参数**: 无

**返回**: dict - 所有硬件信息

**示例**:
```python
all_info = detector.get_all_info()
```

## 💡 使用示例

### 示例1：检测所有硬件

```python
from hardware_info import HardwareInfo

detector = HardwareInfo()
info = detector.get_all_info()

print("硬件信息:")
print(f"CPU: {info['cpu']['model']}")
print(f"  核心数: {info['cpu']['cores']}")
print(f"  频率: {info['cpu']['frequency']}GHz")
print()
print(f"GPU: {info['gpu']['model']}")
print(f"  显存: {info['gpu']['memory']}GB")
print()
print(f"内存: {info['memory']['capacity']}GB")
print(f"  频率: {info['memory']['frequency']}MHz")
print()
print(f"硬盘: {info['disk']['capacity']}GB")
print(f"  类型: {info['disk']['type']}")
```

### 示例2：单独检测CPU

```python
from hardware_info import HardwareInfo

detector = HardwareInfo()
cpu_info = detector.get_cpu_info()

print("CPU信息:")
print(f"型号: {cpu_info['model']}")
print(f"核心数: {cpu_info['cores']}")
print(f"线程数: {cpu_info['threads']}")
print(f"频率: {cpu_info['frequency']}GHz")
print(f"架构: {cpu_info['architecture']}")
```

## 📝 版本历史

### v2.2.0 (2026-03-28)
- 🎉 初始版本
- ✨ CPU信息检测
- ✨ GPU信息检测
- ✨ 内存信息检测
- ✨ 硬盘信息检测
- ✨ 网卡信息检测

### v2.1.0 (2026-03-28)
- 🎉 项目基础版本
- ✨ 硬件信息检测功能
- ✨ CPU检测
- ✨ GPU检测
- ✨ 内存检测
- ✨ 硬盘检测

## 📄 许可证

MIT License

---

<div align="center">

**项目状态**: ✅ 完成
**当前版本**: v2.2.0
**中文支持**: ✅ 完全支持，无乱码

如果这个项目对您有帮助，请给我们一个 ⭐️

</div>