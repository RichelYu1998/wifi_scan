根系# 投影仪推荐器 (ProjectorRecommender)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

根据预算智能推荐投影仪

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

投影仪推荐器是一个智能推荐系统，根据用户的预算推荐性价比最高的投影仪。支持国补价格对比、性价比评分和综合评分。

### 特点

- ✅ **智能推荐** - 根据预算推荐最佳投影仪
- ✅ **国补对比** - 支持国补价格对比
- ✅ **性价比评分** - 计算性价比评分
- ✅ **综合评分** - 综合多个指标评分
- ✅ **购买链接** - 提供多个购买平台的链接

## ✨ 功能介绍

### 1. 智能推荐
- 根据预算筛选投影仪
- 计算性价比评分
- 计算综合评分
- 排序推荐结果

### 2. 价格对比
- 原价显示
- 国补价显示
- 价格差异计算
- 平台价格对比

### 3. 评分系统
- 性价比评分
- 综合评分
- 多维度评估
- 排序和筛选

### 4. 购买链接
- 京东购买链接
- 天猫购买链接
- 淘宝购买链接
- 拼多多购买链接
- 官方商城链接

## 🚀 快速开始

### 基本使用

```python
from projector_recommender import ProjectorRecommender

# 创建推荐器实例
recommender = ProjectorRecommender()

# 根据预算推荐
recommendations = recommender.recommend_by_budget(budget=3000)

# 查看推荐结果
for item in recommendations:
    print(f"{item['brand']} {item['model']}")
    print(f"价格: {item['price']}元")
    print(f"性价比: {item['value_score']}")
    print(f"综合评分: {item['total_score']}")
```

### 高级使用

```python
# 使用国补价格
recommendations = recommender.recommend_by_budget(
    budget=3000,
    use_subsidy=True
)

# 获取最佳推荐
best = recommender.get_best_recommendation(budget=3000)

# 获取推荐列表
top_5 = recommender.get_top_recommendations(budget=3000, top_n=5)
```

## 🔧 API文档

### ProjectorRecommender类

#### `__init__()`
初始化推荐器。

**参数**: 无

**返回**: 无

**示例**:
```python
recommender = ProjectorRecommender()
```

#### `load_data()`
加载投影仪数据。

**参数**: 无

**返回**: bool - 是否加载成功

**示例**:
```python
success = recommender.load_data()
```

#### `recommend_by_budget(budget, use_subsidy=False)`
根据预算推荐投影仪。

**参数**:
- `budget` (int): 预算金额
- `use_subsidy` (bool, optional): 是否使用国补价格

**返回**: list - 推荐列表

**示例**:
```python
recommendations = recommender.recommend_by_budget(
    budget=3000,
    use_subsidy=True
)
```

#### `get_best_recommendation(budget, use_subsidy=False)`
获取最佳推荐。

**参数**:
- `budget` (int): 预算金额
- `use_subsidy` (bool, optional): 是否使用国补价格

**返回**: dict - 最佳推荐

**示例**:
```python
best = recommender.get_best_recommendation(budget=3000)
```

#### `get_top_recommendations(budget, top_n=5, use_subsidy=False)`
获取前N个推荐。

**参数**:
- `budget` (int): 预算金额
- `top_n` (int, optional): 推荐数量
- `use_subsidy` (bool, optional): 是否使用国补价格

**返回**: list - 推荐列表

**示例**:
```python
top_5 = recommender.get_top_recommendations(budget=3000, top_n=5)
```

#### `calculate_value_score(projector)`
计算性价比评分。

**参数**:
- `projector` (dict): 投影仪信息

**返回**: float - 性价比评分

**示例**:
```python
score = recommender.calculate_value_score(projector)
```

#### `calculate_total_score(projector)`
计算综合评分。

**参数**:
- `projector` (dict): 投影仪信息

**返回**: float - 综合评分

**示例**:
```python
score = recommender.calculate_total_score(projector)
```

## 💡 使用示例

### 示例1：基本推荐

```python
from projector_recommender import ProjectorRecommender

recommender = ProjectorRecommender()
recommendations = recommender.recommend_by_budget(budget=3000)

for item in recommendations:
    print(f"{item['brand']} {item['model']}")
    print(f"价格: {item['price']}元")
    print(f"性价比: {item['value_score']:.2f}")
    print(f"综合评分: {item['total_score']:.2f}")
    print()
```

### 示例2：使用国补价格

```python
from projector_recommender import ProjectorRecommender

recommender = ProjectorRecommender()
recommendations = recommender.recommend_by_budget(
    budget=3000,
    use_subsidy=True
)

for item in recommendations:
    print(f"{item['brand']} {item['model']}")
    print(f"原价: {item['price_info']['original_price']}元")
    print(f"国补价: {item['price']}元")
    print(f"节省: {item['price_info']['original_price'] - item['price']}元")
    print()
```

### 示例3：获取最佳推荐

```python
from projector_recommender import ProjectorRecommender

recommender = ProjectorRecommender()
best = recommender.get_best_recommendation(budget=3000)

print("最佳推荐:")
print(f"品牌: {best['brand']}")
print(f"型号: {best['model']}")
print(f"价格: {best['price']}元")
print(f"性价比: {best['value_score']:.2f}")
print(f"综合评分: {best['total_score']:.2f}")
```

## 📝 版本历史

### v2.2.0 (2026-03-28)
- 🎉 初始版本
- ✨ 根据预算推荐投影仪
- ✨ 国补价格对比
- ✨ 性价比评分
- ✨ 综合评分
- ✨ 购买链接

### v2.1.0 (2026-03-28)
- 🎉 项目基础版本
- ✨ 投影仪推荐功能
- ✨ 价格对比功能
- ✨ 评分系统

## 📄 许可证

MIT License

---

<div align="center">

**项目状态**: ✅ 完成
**当前版本**: v2.2.0
**中文支持**: ✅ 完全支持，无乱码

如果这个项目对您有帮助，请给我们一个 ⭐️

</div>