# 投影仪价格历史 (ProjectorPriceHistory)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

跟踪和记录投影仪价格历史

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

投影仪价格历史是一个功能强大的价格跟踪工具，可以记录和跟踪投影仪价格的历史变化。

### 特点

- ✅ **价格跟踪** - 跟踪价格历史变化
- ✅ **趋势分析** - 分析价格趋势
- ✅ **数据存储** - 本地存储价格数据
- ✅ **图表生成** - 生成价格趋势图
- ✅ **中文支持** - 中文显示无乱码

## ✨ 功能介绍

### 1. 价格记录
- 记录价格历史
- 记录时间戳
- 记录平台信息

### 2. 趋势分析
- 分析价格趋势
- 计算价格变化
- 预测价格走势

### 3. 数据存储
- 本地存储价格数据
- JSON格式存储
- 支持数据导入导出

### 4. 图表生成
- 生成价格趋势图
- 生成价格对比图
- 支持自定义图表

## 🚀 快速开始

### 基本使用

```python
from projector_price_history import ProjectorPriceHistory

# 创建价格历史实例
history = ProjectorPriceHistory()

# 记录价格
history.record_price('projector_001', 3000, '京东')

# 获取价格历史
price_history = history.get_price_history('projector_001')

# 分析价格趋势
trend = history.analyze_trend('projector_001')
```

### 命令行使用

```bash
python projector_price_history.py
```

## 🔧 API文档

### ProjectorPriceHistory类

#### `__init__()`
初始化价格历史记录器。

**参数**: 无

**返回**: 无

**示例**:
```python
history = ProjectorPriceHistory()
```

#### `record_price(projector_id, price, platform)`
记录价格。

**参数**:
- `projector_id` (str): 投影仪ID
- `price` (float): 价格
- `platform` (str): 购买平台

**返回**: bool - 是否记录成功

**示例**:
```python
success = history.record_price('projector_001', 3000, '京东')
```

#### `get_price_history(projector_id)`
获取价格历史。

**参数**:
- `projector_id` (str): 投影仪ID

**返回**: list - 价格历史列表

**示例**:
```python
price_history = history.get_price_history('projector_001')
```

#### `analyze_trend(projector_id)`
分析价格趋势。

**参数**:
- `projector_id` (str): 投影仪ID

**返回**: dict - 趋势分析结果

**示例**:
```python
trend = history.analyze_trend('projector_001')
```

#### `generate_trend_chart(projector_id, output_file=None)`
生成价格趋势图。

**参数**:
- `projector_id` (str): 投影仪ID
- `output_file` (str, optional): 输出文件路径

**返回**: str - 图表文件路径

**示例**:
```python
chart_file = history.generate_trend_chart('projector_001')
```

## 💡 使用示例

### 示例1：记录价格

```python
from projector_price_history import ProjectorPriceHistory

history = ProjectorPriceHistory()

# 记录价格
history.record_price('projector_001', 3000, '京东')
history.record_price('projector_001', 2900, '天猫')
history.record_price('projector_001', 2850, '淘宝')

# 获取价格历史
price_history = history.get_price_history('projector_001')

print("价格历史:")
for record in price_history:
    print(f"  {record['date']}: {record['price']}元 ({record['platform']})")
```

### 示例2：分析趋势

```python
from projector_price_history import ProjectorPriceHistory

history = ProjectorPriceHistory()

# 分析价格趋势
trend = history.analyze_trend('projector_001')

print("价格趋势分析:")
print(f"  最高价格: {trend['max_price']}元")
print(f"  最低价格: {trend['min_price']}元")
print(f"  平均价格: {trend['avg_price']}元")
print(f"  价格趋势: {trend['trend']}")
```

### 示例3：生成趋势图

```python
from projector_price_history import ProjectorPriceHistory

history = ProjectorPriceHistory()

# 生成价格趋势图
chart_file = history.generate_trend_chart('projector_001')

print(f"价格趋势图已生成: {chart_file}")
```

## 📝 版本历史

### v2.2.0 (2026-03-28)
- 🎉 初始版本
- ✨ 跟踪价格历史变化
- ✨ 分析价格趋势
- ✨ 本地存储价格数据
- ✨ 生成价格趋势图

### v2.1.0 (2026-03-28)
- 🎉 项目基础版本
- ✨ 价格历史跟踪功能
- ✨ 趋势分析
- ✨ 数据存储

## 📄 许可证

MIT License

---

<div align="center">

**项目状态**: ✅ 完成
**当前版本**: v2.2.0
**中文支持**: ✅ 完全支持，无乱码

如果这个项目对您有帮助，请给我们一个 ⭐️

</div>