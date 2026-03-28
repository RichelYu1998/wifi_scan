# 网络速度测试 (NetworkSpeedTester)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

测试网络上传和下载速度

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

网络速度测试是一个功能强大的网络测试工具，可以测试网络上传和下载速度。

### 特点

- ✅ **速度测试** - 测试网络上传和下载速度
- ✅ **详细报告** - 提供详细的测试报告
- ✅ **多服务器** - 支持多个测试服务器
- ✅ **中文支持** - 中文显示无乱码

## ✨ 功能介绍

### 1. 下载速度测试
- 测试下载速度
- 显示实时进度
- 计算平均速度

### 2. 上传速度测试
- 测试上传速度
- 显示实时进度
- 计算平均速度

### 3. 详细报告
- 下载速度
- 上传速度
- 延迟
- 抖动

## 🚀 快速开始

### 基本使用

```python
from network_speed_tester import NetworkSpeedTester

# 创建测试器实例
tester = NetworkSpeedTester()

# 测试网络速度
result = tester.test_speed()

# 显示测试结果
print(f"下载速度: {result['download_speed']} Mbps")
print(f"上传速度: {result['upload_speed']} Mbps")
```

### 命令行使用

```bash
python network_speed_tester.py
```

## 🔧 API文档

### NetworkSpeedTester类

#### `__init__()`
初始化网络速度测试器。

**参数**: 无

**返回**: 无

**示例**:
```python
tester = NetworkSpeedTester()
```

#### `test_speed()`
测试网络速度。

**参数**: 无

**返回**: dict - 测试结果

**示例**:
```python
result = tester.test_speed()
```

#### `test_download_speed()`
测试下载速度。

**参数**: 无

**返回**: float - 下载速度（Mbps）

**示例**:
```python
speed = tester.test_download_speed()
```

#### `test_upload_speed()`
测试上传速度。

**参数**: 无

**返回**: float - 上传速度（Mbps）

**示例**:
```python
speed = tester.test_upload_speed()
```

## 💡 使用示例

### 示例1：基本测试

```python
from network_speed_tester import NetworkSpeedTester

tester = NetworkSpeedTester()
result = tester.test_speed()

print("网络速度测试结果:")
print(f"下载速度: {result['download_speed']:.2f} Mbps")
print(f"上传速度: {result['upload_speed']:.2f} Mbps")
print(f"延迟: {result['latency']:.2f} ms")
print(f"抖动: {result['jitter']:.2f} ms")
```

### 示例2：单独测试

```python
from network_speed_tester import NetworkSpeedTester

tester = NetworkSpeedTester()

# 只测试下载速度
download_speed = tester.test_download_speed()
print(f"下载速度: {download_speed:.2f} Mbps")

# 只测试上传速度
upload_speed = tester.test_upload_speed()
print(f"上传速度: {upload_speed:.2f} Mbps")
```

## 📝 版本历史

### v2.2.0 (2026-03-28)
- 🎉 初始版本
- ✨ 测试网络上传和下载速度
- ✨ 提供详细报告
- ✨ 支持多个测试服务器

### v2.1.0 (2026-03-28)
- 🎉 项目基础版本
- ✨ 网络速度测试功能
- ✨ 上传速度测试
- ✨ 下载速度测试

## 📄 许可证

MIT License

---

<div align="center">

**项目状态**: ✅ 完成
**当前版本**: v2.2.0
**中文支持**: ✅ 完全支持，无乱码

如果这个项目对您有帮助，请给我们一个 ⭐️

</div>