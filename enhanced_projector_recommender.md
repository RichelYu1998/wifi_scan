# 增强投影仪推荐器 (EnhancedProjectorRecommender)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

增强版投影仪推荐器，提供更多推荐功能

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

增强投影仪推荐器是投影仪推荐器的增强版本，提供更多推荐功能和更详细的推荐结果。

### 特点

- ✅ **智能推荐** - 根据预算推荐最佳投影仪
- ✅ **多维度评分** - 综合多个指标评分
- ✅ **个性化推荐** - 根据用户偏好推荐
- ✅ **详细分析** - 提供详细的推荐分析
- ✅ **中文支持** - 中文显示无乱码

## ✨ 功能介绍

### 1. 智能推荐
- 根据预算推荐
- 根据使用场景推荐
- 根据用户偏好推荐
- 多条件筛选推荐

### 2. 多维度评分
- 性价比评分
- 综合评分
- 用户评分
- 专家评分

### 3. 个性化推荐
- 用户偏好设置
- 使用场景选择
- 预算范围设置
- 品牌偏好设置

### 4. 详细分析
- 推荐理由说明
- 优缺点分析
- 适用场景说明
- 购买建议

## 🚀 快速开始

### 基本使用

```python
from enhanced_projector_recommender import EnhancedProjectorRecommender

# 创建推荐器实例
recommender = EnhancedProjectorRecommender()

# 根据预算推荐
recommendations = recommender.recommend_by_budget(budget=3000)

# 查看推荐结果
for item in recommendations:
    print(f"{item['brand']} {item['model']}")
    print(f"价格: {item['price']}元")
    print(f"性价比: {item['value_score']}")
    print(f"推荐理由: {item['recommendation_reason']}")
```

### 命令行使用

```bash
python enhanced_projector_recommender.py
```

## 🔧 API文档

### EnhancedProjectorRecommender类

#### `__init__()`
初始化增强推荐器。

**参数**: 无

**返回**: 无

**示例**:
```python
recommender = EnhancedProjectorRecommender()
```

#### `recommend_by_budget(budget, use_subsidy=False, preferences=None)`
根据预算推荐投影仪。

**参数**:
- `budget` (int): 预算金额
- `use_subsidy` (bool, optional): 是否使用国补价格
- `preferences` (dict, optional): 用户偏好

**返回**: list - 推荐列表

**示例**:
```python
recommendations = recommender.recommend_by_budget(
    budget=3000,
    use_subsidy=True,
    preferences={'brand': '爱普生', 'scene': '电影'}
)
```

#### `recommend_by_scene(scene, budget=None)`
根据使用场景推荐投影仪。

**参数**:
- `scene` (str): 使用场景
- `budget` (int, optional): 预算金额

**返回**: list - 推荐列表

**示例**:
```python
recommendations = recommender.recommend_by_scene('电影', budget=3000)
```

#### `get_detailed_analysis(projector)`
获取投影仪的详细分析。

**参数**:
- `projector` (dict): 投影仪信息

**返回**: dict - 详细分析

**示例**:
```python
analysis = recommender.get_detailed_analysis(projector)
```

#### `set_user_preferences(preferences)`
设置用户偏好。

**参数**:
- `preferences` (dict): 用户偏好

**返回**: 无

**示例**:
```python
recommender.set_user_preferences({
    'brand': '爱普生',
    'scene': '电影',
    'resolution': '1080P'
})
```

## 💡 使用示例

### 示例1：基本推荐

```python
from enhanced_projector_recommender import EnhancedProjectorRecommender

recommender = EnhancedProjectorRecommender()
recommendations = recommender.recommend_by_budget(budget=3000)

for item in recommendations:
    print(f"{item['brand']} {item['model']}")
    print(f"价格: {item['price']}元")
    print(f"性价比: {item['value_score']:.2f}")
    print(f"推荐理由: {item['recommendation_reason']}")
    print()
```

### 示例2：个性化推荐

```python
from enhanced_projector_recommender import EnhancedProjectorRecommender

recommender = EnhancedProjectorRecommender()

# 设置用户偏好
recommender.set_user_preferences({
    'brand': '爱普生',
    'scene': '电影',
    'resolution': '1080P'
})

# 根据偏好推荐
recommendations = recommender.recommend_by_budget(budget=3000)

for item in recommendations:
    print(f"{item['brand']} {item['model']}")
    print(f"推荐理由: {item['recommendation_reason']}")
```

### 示例3：根据场景推荐

```python
from enhanced_projector_recommender import EnhancedProjectorRecommender

recommender = EnhancedProjectorRecommender()

# 根据场景推荐
recommendations = recommender.recommend_by_scene('电影', budget=3000)

for item in recommendations:
    print(f"{item['brand']} {item['model']}")
    print(f"适用场景: {item['scene']}")
    print(f"推荐理由: {item['recommendation_reason']}")
```

## 📝 版本历史

### v2.2.0 (2026-03-28)
- 🎉 初始版本
- ✨ 智能推荐功能
- ✨ 多维度评分
- ✨ 个性化推荐
- ✨ 详细分析

### v2.1.0 (2026-03-28)
- 🎉 项目基础版本
- ✨ 增强推荐功能
- ✨ 多维度评分
- ✨ 个性化设置

## 📄 许可证

MIT License

---

<div align="center">

**项目状态**: ✅ 完成
**当前版本**: v2.2.0
**中文支持**: ✅ 完全支持，无乱码

如果这个项目对您有帮助，请给我们一个 ⭐️

</div>