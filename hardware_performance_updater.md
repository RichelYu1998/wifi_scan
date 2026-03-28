
# 硬件性能数据更新器 (HardwarePerformanceUpdater)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

从网络更新硬件性能数据

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

硬件性能数据更新器是一个功能强大的数据更新工具，可以从网络获取最新的硬件性能数据。

### 特点

- ✅ **网络更新** - 从网络获取最新数据
- ✅ **多数据源** - 支持多个数据源
- ✅ **数据缓存** - 本地缓存性能数据
- ✅ **自动更新** - 支持自动更新
- ✨ **中文支持** - 中文显示无乱码

## ✨ 功能介绍

### 1. 数据更新
- 从网络获取最新性能数据
- 更新本地性能数据
- 支持多个数据源

### 2. 硬件类型
- CPU性能数据
- GPU性能数据
- 内存性能数据
- 硬盘性能数据

### 3. 数据源
- 官方数据库
- 第三方评测网站
- 社区贡献数据

### 4. 数据缓存
- 本地缓存性能数据
- 减少网络请求
- 提高响应速度

## 🚀 快速开始

### 基本使用

```python
from hardware_performance_updater import HardwarePerformanceUpdater

# 创建更新器实例
updater = HardwarePerformanceUpdater()

# 更新性能数据
success = updater.update_all()

# 显示更新结果
if success:
    print("性能数据更新成功！")
else:
    print("性能数据更新失败！")
```

### 命令行使用

```bash
python hardware_performance_updater.py
```

## 🔧 API文档

### HardwarePerformanceUpdater类

#### `__init__()`
初始化性能数据更新器。

**参数**: 无

**返回**: 无

**示例**:
```python
updater = HardwarePerformanceUpdater()
```

#### `update_all()`
更新所有性能数据。

**参数**: 无

**返回**: bool - 是否更新成功

**示例**:
```python
success = updater.update_all()
```

#### `update_cpu_data()`
更新CPU性能数据。

**参数**: 无

**返回**: bool - 是否更新成功

**示例**:
```python
success = updater.update_cpu_data()
```

#### `update_gpu_data()`
更新GPU性能数据。

**参数**: 无

**返回**: bool - 是否更新成功

**示例**:
```python
success = updater.update_gpu_data()
```

#### `update_memory_data()`
更新内存性能数据。

**参数**: 无

**返回**: bool - 是否更新成功

**示例**:
```python
success = updater.update_memory_data()
```

#### `get_performance_score(hardware_type, model)`
获取性能评分。

**参数**:
- `hardware_type` (str): 硬件类型
- `model` (str): 硬件型号

**返回**: float - 性能评分

**示例**:
```python
score = updater.get_performance_score('cpu', 'Intel Core i7-12700K')
```

## 💡 使用示例

### 示例1：更新所有数据

```python
from hardware_performance_updater import HardwarePerformanceUpdater

updater = HardwarePerformanceUpdater()
success = updater.update_all()

if success:
    print("性能数据更新成功！")
    print(f"更新时间: {updater.get_update_time()}")
else:
    print("性能数据更新失败！")
```

### 示例2：更新特定类型数据

```python
from hardware_performance_updater import HardwarePerformanceUpdater

updater = HardwarePerformanceUpdater()

# 只更新CPU数据
success = updater.update_cpu_data()

if success:
    print("CPU性能数据更新成功！")
```

### 示例3：获取性能评分

```python
from hardware_performance_updater import HardwarePerformanceUpdater

updater = HardwarePerformanceUpdater()

# 获取CPU性能评分
cpu_score = updater.get_performance_score('cpu', 'Intel Core i7-12700K')
print(f"CPU性能评分: {cpu_score}")

# 获取GPU性能评分
gpu_score = updater.get_performance_score('gpu', 'NVIDIA RTX 3080')
print(f"GPU性能评分: {gpu_score}")
```

## 📝 版本历史

### v2.2.0 (2026-03-28)
- 🎉 初始版本
- ✨ 从网络获取最新数据
- ✨ 支持多个数据源
- ✨ 本地缓存性能数据
- ✨ 支持自动更新

### v2.1.0 (2026-03-28)
- 🎉 项目基础版本
- ✨ 性能数据更新功能
- ✨ 多数据源支持
- ✨ 自动更新

## 📄 许可证

MIT License

---

<div align="center">

**项目状态**: ✅ 完成
**当前版本**: v2.2.0
**中文支持**: ✅ 完全支持，无乱码

如果这个项目对您有帮助，请给我们一个 ⭐️

</div>