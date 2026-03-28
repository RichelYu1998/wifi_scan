# 投影仪价格更新器 (ProjectorPriceUpdater)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

从网络更新最新的投影仪价格数据

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

投影仪价格更新器是一个功能强大的价格更新工具，可以从网络获取最新的投影仪价格数据。

### 特点

- ✅ **网络更新** - 从网络获取最新价格
- ✅ **多平台支持** - 支持多个购买平台
- ✅ **国补计算** - 自动计算国补价格
- ✅ **数据缓存** - 本地缓存价格数据
- ✅ **中文支持** - 中文显示无乱码

## ✨ 功能介绍

### 1. 价格更新
- 从网络获取最新价格
- 更新本地价格数据
- 支持多个数据源

### 2. 平台支持
- 京东价格
- 天猫价格
- 淘宝价格
- 拼多多价格
- 官方商城价格

### 3. 国补计算
- 自动计算国补价格
- 显示原价和国补价对比
- 支持自定义国补比例

### 4. 数据缓存
- 本地缓存价格数据
- 减少网络请求
- 提高响应速度

## 🚀 快速开始

### 基本使用

```python
from projector_price_updater import ProjectorPriceUpdater

# 创建更新器实例
updater = ProjectorPriceUpdater()

# 更新价格数据
success = updater.update_prices()

# 显示更新结果
if success:
    print("价格数据更新成功！")
else:
    print("价格数据更新失败！")
```

### 命令行使用

```bash
python projector_price_updater.py
```

## 🔧 API文档

### ProjectorPriceUpdater类

#### `__init__()`
初始化价格更新器。

**参数**: 无

**返回**: 无

**示例**:
```python
updater = ProjectorPriceUpdater()
```

#### `update_prices()`
更新价格数据。

**参数**: 无

**返回**: bool - 是否更新成功

**示例**:
```python
success = updater.update_prices()
```

#### `get_price(projector_id, platform='京东')`
获取指定投影仪的价格。

**参数**:
- `projector_id` (str): 投影仪ID
- `platform` (str, optional): 购买平台

**返回**: float - 价格

**示例**:
```python
price = updater.get_price('projector_001', '京东')
```

#### `get_all_prices(projector_id)`
获取指定投影仪的所有平台价格。

**参数**:
- `projector_id` (str): 投影仪ID

**返回**: dict - 所有平台价格

**示例**:
```python
prices = updater.get_all_prices('projector_001')
```

#### `calculate_subsidy_price(original_price, subsidy_rate=0.15)`
计算国补价格。

**参数**:
- `original_price` (float): 原价
- `subsidy_rate` (float, optional): 国补比例

**返回**: float - 国补价格

**示例**:
```python
subsidy_price = updater.calculate_subsidy_price(3000, 0.15)
```

## 💡 使用示例

### 示例1：更新价格数据

```python
from projector_price_updater import ProjectorPriceUpdater

updater = ProjectorPriceUpdater()
success = updater.update_prices()

if success:
    print("价格数据更新成功！")
    print(f"更新时间: {updater.get_update_time()}")
else:
    print("价格数据更新失败！")
```

### 示例2：获取价格

```python
from projector_price_updater import ProjectorPriceUpdater

updater = ProjectorPriceUpdater()

# 获取单个平台价格
jd_price = updater.get_price('projector_001', '京东')
print(f"京东价格: {jd_price}元")

# 获取所有平台价格
all_prices = updater.get_all_prices('projector_001')
print("所有平台价格:")
for platform, price in all_prices.items():
    print(f"  {platform}: {price}元")
```

### 示例3：计算国补价格

```python
from projector_price_updater import ProjectorPriceUpdater

updater = ProjectorPriceUpdater()

original_price = 3000
subsidy_price = updater.calculate_subsidy_price(original_price, 0.15)

print(f"原价: {original_price}元")
print(f"国补价: {subsidy_price}元")
print(f"节省: {original_price - subsidy_price}元")
```

## 📝 版本历史

### v2.2.0 (2026-03-28)
- 🎉 初始版本
- ✨ 从网络获取最新价格
- ✨ 支持多个购买平台
- ✨ 自动计算国补价格
- ✨ 本地缓存价格数据

### v2.1.0 (2026-03-28)
- 🎉 项目基础版本
- ✨ 价格更新功能
- ✨ 多平台支持
- ✨ 国补计算

## 📄 许可证

MIT License

---

<div align="center">

**项目状态**: ✅ 完成
**当前版本**: v2.2.0
**中文支持**: ✅ 完全支持，无乱码

如果这个项目对您有帮助，请给我们一个 ⭐️

</div>