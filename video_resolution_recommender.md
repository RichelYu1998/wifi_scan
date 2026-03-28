# 视频分辨率推荐 (VideoResolutionRecommender)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

根据屏幕尺寸和观看距离推荐最佳分辨率

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

视频分辨率推荐是一个智能推荐系统，根据屏幕尺寸和观看距离推荐最佳分辨率。

### 特点

- ✅ **智能推荐** - 根据屏幕尺寸和观看距离推荐
- ✅ **多种场景** - 支持多种观看场景
- ✅ **详细说明** - 提供详细的推荐说明
- ✅ **中文支持** - 中文显示无乱码

## ✨ 功能介绍

### 1. 分辨率推荐
- 根据屏幕尺寸推荐
- 根据观看距离推荐
- 综合推荐最佳分辨率

### 2. 观看场景
- 电影观看
- 游戏娱乐
- 办公工作
- 日常使用

### 3. 详细说明
- 推荐分辨率
- 推荐理由
- 适用场景
- 注意事项

## 🚀 快速开始

### 基本使用

```python
from video_resolution_recommender import VideoResolutionRecommender

# 创建推荐器实例
recommender = VideoResolutionRecommender()

# 根据屏幕尺寸和观看距离推荐
resolution = recommender.recommend(
    screen_size=65,
    viewing_distance=3
)

# 显示推荐结果
print(f"推荐分辨率: {resolution['resolution']}")
print(f"推荐理由: {resolution['reason']}")
```

### 命令行使用

```bash
python video_resolution_recommender.py
```

## 🔧 API文档

### VideoResolutionRecommender类

#### `__init__()`
初始化视频分辨率推荐器。

**参数**: 无

**返回**: 无

**示例**:
```python
recommender = VideoResolutionRecommender()
```

#### `recommend(screen_size, viewing_distance, scenario='movie')`
根据屏幕尺寸和观看距离推荐分辨率。

**参数**:
- `screen_size` (float): 屏幕尺寸（英寸）
- `viewing_distance` (float): 观看距离（米）
- `scenario` (str, optional): 观看场景

**返回**: dict - 推荐结果

**示例**:
```python
resolution = recommender.recommend(
    screen_size=65,
    viewing_distance=3,
    scenario='movie'
)
```

#### `get_all_resolutions()`
获取所有支持的分辨率。

**参数**: 无

**返回**: list - 分辨率列表

**示例**:
```python
resolutions = recommender.get_all_resolutions()
```

## 💡 使用示例

### 示例1：电影观看

```python
from video_resolution_recommender import VideoResolutionRecommender

recommender = VideoResolutionRecommender()
resolution = recommender.recommend(
    screen_size=65,
    viewing_distance=3,
    scenario='movie'
)

print("电影观看推荐:")
print(f"推荐分辨率: {resolution['resolution']}")
print(f"推荐理由: {resolution['reason']}")
print(f"适用场景: {resolution['scenario']}")
```

### 示例2：游戏娱乐

```python
from video_resolution_recommender import VideoResolutionRecommender

recommender = VideoResolutionRecommender()
resolution = recommender.recommend(
    screen_size=55,
    viewing_distance=2.5,
    scenario='game'
)

print("游戏娱乐推荐:")
print(f"推荐分辨率: {resolution['resolution']}")
print(f"推荐理由: {resolution['reason']}")
print(f"适用场景: {resolution['scenario']}")
```

## 📝 版本历史

### v2.2.0 (2026-03-28)
- 🎉 初始版本
- ✨ 根据屏幕尺寸和观看距离推荐
- ✨ 支持多种观看场景
- ✨ 提供详细推荐说明

### v2.1.0 (2026-03-28)
- 🎉 项目基础版本
- ✨ 视频分辨率推荐功能
- ✨ 场景支持
- ✨ 详细说明

## 📄 许可证

MIT License

---

<div align="center">

**项目状态**: ✅ 完成
**当前版本**: v2.2.0
**中文支持**: ✅ 完全支持，无乱码

如果这个项目对您有帮助，请给我们一个 ⭐️

</div>