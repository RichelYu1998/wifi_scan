# 投影仪图表生成器 (ProjectorChartGenerator)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

生成投影仪价格对比、性价比对比等图表

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

投影仪图表生成器是一个功能强大的图表生成工具，可以生成投影仪价格对比、性价比对比等图表。

### 特点

- ✅ **价格对比** - 生成价格对比图表
- ✅ **性价比对比** - 生成性价比对比图表
- ✅ **预算对比** - 生成预算对比图表
- ✅ **HTML报告** - 自动生成包含购买链接的HTML报告
- ✅ **中文支持** - 中文显示无乱码

## ✨ 功能介绍

### 1. 价格对比图表
- 原价对比
- 国补价对比
- 价格差异显示
- 多品牌对比

### 2. 性价比对比图表
- 性价比评分对比
- 综合评分对比
- 排序显示
- 最佳推荐标记

### 3. 预算对比图表
- 预算范围对比
- 价格分布显示
- 推荐范围标记
- 动态预算测试

### 4. HTML报告
- 包含所有图表
- 包含购买链接
- 响应式设计
- 美观的UI

## 🚀 快速开始

### 基本使用

```python
from projector_chart_generator import ProjectorChartGenerator

# 创建图表生成器实例
generator = ProjectorChartGenerator()

# 生成价格对比图表
generator.generate_price_comparison_chart(projectors)

# 生成性价比对比图表
generator.generate_value_score_chart(projectors)

# 生成HTML报告
generator.generate_html_report(projectors)
```

### 命令行使用

```bash
python projector_chart_generator.py
```

## 🔧 API文档

### ProjectorChartGenerator类

#### `__init__()`
初始化图表生成器。

**参数**: 无

**返回**: 无

**示例**:
```python
generator = ProjectorChartGenerator()
```

#### `generate_price_comparison_chart(projectors, use_subsidy=True, output_file=None)`
生成价格对比图表。

**参数**:
- `projectors` (list): 投影仪列表
- `use_subsidy` (bool, optional): 是否使用国补价格
- `output_file` (str, optional): 输出文件路径

**返回**: str - 图表文件路径

**示例**:
```python
chart_file = generator.generate_price_comparison_chart(
    projectors,
    use_subsidy=True
)
```

#### `generate_value_score_chart(projectors, output_file=None)`
生成性价比对比图表。

**参数**:
- `projectors` (list): 投影仪列表
- `output_file` (str, optional): 输出文件路径

**返回**: str - 图表文件路径

**示例**:
```python
chart_file = generator.generate_value_score_chart(projectors)
```

#### `generate_budget_comparison_chart(projectors, budget, output_file=None)`
生成预算对比图表。

**参数**:
- `projectors` (list): 投影仪列表
- `budget` (int): 预算金额
- `output_file` (str, optional): 输出文件路径

**返回**: str - 图表文件路径

**示例**:
```python
chart_file = generator.generate_budget_comparison_chart(
    projectors,
    budget=3000
)
```

#### `generate_html_report(projectors, output_file=None)`
生成HTML报告。

**参数**:
- `projectors` (list): 投影仪列表
- `output_file` (str, optional): 输出文件路径

**返回**: str - HTML文件路径

**示例**:
```python
html_file = generator.generate_html_report(projectors)
```

## 💡 使用示例

### 示例1：生成所有图表

```python
from projector_chart_generator import ProjectorChartGenerator

generator = ProjectorChartGenerator()

# 生成价格对比图表
price_chart = generator.generate_price_comparison_chart(projectors)

# 生成性价比对比图表
value_chart = generator.generate_value_score_chart(projectors)

# 生成预算对比图表
budget_chart = generator.generate_budget_comparison_chart(projectors, budget=3000)

# 生成HTML报告
html_report = generator.generate_html_report(projectors)
```

### 示例2：自定义输出路径

```python
from projector_chart_generator import ProjectorChartGenerator

generator = ProjectorChartGenerator()

# 自定义输出路径
generator.generate_price_comparison_chart(
    projectors,
    output_file='custom_price_chart.png'
)
```

## 📝 版本历史

### v2.2.0 (2026-03-28)
- 🎉 初始版本
- ✨ 生成价格对比图表
- ✨ 生成性价比对比图表
- ✨ 生成预算对比图表
- ✨ 自动生成HTML报告

### v2.1.0 (2026-03-28)
- 🎉 项目基础版本
- ✨ 图表生成功能
- ✨ 价格对比图表
- ✨ 性价比对比图表

## 📄 许可证

MIT License

---

<div align="center">

**项目状态**: ✅ 完成
**当前版本**: v2.2.0
**中文支持**: ✅ 完全支持，无乱码

如果这个项目对您有帮助，请给我们一个 ⭐️

</div>