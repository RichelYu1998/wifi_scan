# 快速启动脚本 (QuickStart)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

一键执行完整流程

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

快速启动脚本是一个一键执行完整流程的工具，自动更新数据、生成图表和生成HTML报告。

### 特点

- ✅ **一键执行** - 自动执行完整流程
- ✅ **数据更新** - 自动更新投影仪价格数据
- ✅ **图表生成** - 自动生成价格对比图表
- ✅ **报告生成** - 自动生成HTML报告
- ✅ **跨平台** - 支持Windows/Linux/macOS

## ✨ 功能介绍

### 1. 自动数据更新
- 从网络更新最新的投影仪价格数据
- 支持国补价格计算
- 自动保存更新后的数据

### 2. 自动图表生成
- 生成价格对比图表
- 生成性价比对比图表
- 生成预算对比图表

### 3. 自动报告生成
- 生成包含图表的HTML报告
- 包含购买链接
- 支持多个购买平台

### 4. 简洁输出
- 清晰的进度提示
- 友好的完成提示
- 详细的文件列表

## 🚀 快速开始

### 运行脚本

```bash
python quick_start.py
```

### 输出示例

```
🔄 开始快速启动流程...

🔄 步骤1: 更新价格数据...
✅ 价格数据更新完成

🔄 步骤2: 生成图表...
✅ 图表生成完成

🔄 步骤3: 生成HTML报告...
✅ HTML报告生成完成

🎉 快速启动流程完成！

生成的文件:
- charts/price_comparison.png
- charts/value_score_comparison.png
- charts/budget_comparison.png
- charts/projector_comparison.html
```

## 🔧 API文档

### QuickStart类

#### `__init__()`
初始化快速启动脚本。

**参数**: 无

**返回**: 无

**示例**:
```python
quick_start = QuickStart()
```

#### `update_price_data()`
更新价格数据。

**参数**: 无

**返回**: bool - 是否更新成功

**示例**:
```python
success = quick_start.update_price_data()
```

#### `generate_charts()`
生成图表。

**参数**: 无

**返回**: bool - 是否生成成功

**示例**:
```python
success = quick_start.generate_charts()
```

#### `generate_html_report()`
生成HTML报告。

**参数**: 无

**返回**: bool - 是否生成成功

**示例**:
```python
success = quick_start.generate_html_report()
```

#### `run()`
运行完整流程。

**参数**: 无

**返回**: int - 退出码

**示例**:
```python
exit_code = quick_start.run()
```

## 💡 使用示例

### 示例1：基本使用

```python
from quick_start import QuickStart

quick_start = QuickStart()
exit_code = quick_start.run()

if exit_code == 0:
    print("快速启动成功！")
else:
    print("快速启动失败！")
```

### 示例2：单独执行步骤

```python
from quick_start import QuickStart

quick_start = QuickStart()

# 只更新价格数据
quick_start.update_price_data()

# 只生成图表
quick_start.generate_charts()

# 只生成HTML报告
quick_start.generate_html_report()
```

## 📝 版本历史

### v2.2.0 (2026-03-28)
- 🎉 初始版本
- ✨ 一键执行完整流程
- ✨ 自动更新数据
- ✨ 自动生成图表
- ✨ 自动生成HTML报告

### v2.1.0 (2026-03-28)
- 🎉 项目基础版本
- ✨ 快速启动功能
- ✨ 自动化流程

## 📄 许可证

MIT License

---

<div align="center">

**项目状态**: ✅ 完成
**当前版本**: v2.2.0
**中文支持**: ✅ 完全支持，无乱码

如果这个项目对您有帮助，请给我们一个 ⭐️

</div>