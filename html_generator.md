# HTML生成器 (HTMLGenerator)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

通用的HTML页面生成功能，支持图表和购买链接

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

HTML生成器是一个通用的HTML页面生成工具，用于生成包含图表和购买链接的HTML报告。它提供了组件化的设计，便于自定义和扩展。

### 特点

- ✅ **通用HTML生成** - 支持生成完整的HTML页面
- ✅ **组件化设计** - 分离头部、尾部、图表、链接
- ✅ **动态样式** - 集中管理CSS样式，支持动态平台颜色
- ✅ **购买链接** - 支持多个购买平台的彩色按钮
- ✅ **响应式设计** - 自动适应屏幕尺寸

## ✨ 功能介绍

### 1. HTML页面生成
- 生成完整的HTML页面
- 支持自定义标题
- 支持嵌入多个图表
- 支持添加购买链接

### 2. 样式管理
- 集中管理CSS样式
- 支持动态平台颜色
- 响应式设计
- 美观的UI界面

### 3. 购买链接支持
- 支持多个购买平台
- 彩色按钮设计
- 悬停效果
- 新标签页打开

### 4. 支持的购买平台
- 京东（红色 #e4393c）
- 天猫（粉色 #ff0036）
- 淘宝（橙色 #ff5000）
- 拼多多（深红色 #e02e24）
- 官方商城（蓝色 #2196F3）
- 苏宁（黄色 #F90）
- 其他（灰色 #9E9E9E）

## 🚀 快速开始

### 基本使用

```python
from html_generator import HTMLGenerator

# 创建生成器实例
generator = HTMLGenerator()

# 生成HTML页面
html = generator.generate_html_page(
    title='页面标题',
    chart_files=['chart1.png', 'chart2.png'],
    items=[{'brand': '品牌', 'model': '型号', 'purchase_links': {...}}],
    link_key='purchase_links'
)

# 保存HTML文件
generator.save_html(html, 'output.html')
```

### 高级使用

```python
# 自定义名称格式
html = generator.generate_html_page(
    title='页面标题',
    chart_files=chart_files,
    items=items,
    link_key='purchase_links',
    name_format=lambda item: f"{item['brand']} {item['model']}"
)

# 添加额外信息
html = generator.generate_html_page(
    title='页面标题',
    chart_files=chart_files,
    items=items,
    link_key='purchase_links',
    extra_info='额外的页面信息'
)
```

## 🔧 API文档

### HTMLGenerator类

#### `__init__()`
初始化HTML生成器。

**参数**: 无

**返回**: 无

**示例**:
```python
generator = HTMLGenerator()
```

#### `generate_html_page(title, chart_files, items, link_key, name_format, extra_info)`
生成完整的HTML页面。

**参数**:
- `title` (str): 页面标题
- `chart_files` (list): 图表文件列表
- `items` (list): 项目列表
- `link_key` (str): 链接键名
- `name_format` (function, optional): 名称格式化函数
- `extra_info` (str, optional): 额外信息

**返回**: HTML字符串

**示例**:
```python
html = generator.generate_html_page(
    title='投影仪推荐',
    chart_files=['chart.png'],
    items=items,
    link_key='purchase_links'
)
```

#### `save_html(html, output_file)`
保存HTML文件。

**参数**:
- `html` (str): HTML内容
- `output_file` (str): 输出文件路径

**返回**: bool - 是否保存成功

**示例**:
```python
success = generator.save_html(html, 'output.html')
```

#### `generate_html_header(title)`
生成HTML头部。

**参数**:
- `title` (str): 页面标题

**返回**: HTML头部字符串

**示例**:
```python
header = generator.generate_html_header('页面标题')
```

#### `generate_html_footer(extra_info)`
生成HTML尾部。

**参数**:
- `extra_info` (str, optional): 额外信息

**返回**: HTML尾部字符串

**示例**:
```python
footer = generator.generate_html_footer('额外信息')
```

#### `generate_chart_section(chart_files)`
生成图表部分。

**参数**:
- `chart_files` (list): 图表文件列表

**返回**: 图表部分HTML字符串

**示例**:
```python
section = generator.generate_chart_section(['chart1.png', 'chart2.png'])
```

#### `generate_purchase_links_section(items, link_key, name_format)`
生成购买链接部分。

**参数**:
- `items` (list): 项目列表
- `link_key` (str): 链接键名
- `name_format` (function, optional): 名称格式化函数

**返回**: 购买链接部分HTML字符串

**示例**:
```python
section = generator.generate_purchase_links_section(
    items=[{'brand': '爱普生', 'model': 'CH-TW6250'}],
    link_key='purchase_links'
)
```

## 💡 使用示例

### 示例1：生成简单的HTML页面

```python
from html_generator import HTMLGenerator

generator = HTMLGenerator()

html = generator.generate_html_page(
    title='测试页面',
    chart_files=['test.png'],
    items=[],
    link_key='purchase_links'
)

generator.save_html(html, 'test.html')
```

### 示例2：生成包含购买链接的HTML页面

```python
from html_generator import HTMLGenerator

generator = HTMLGenerator()

items = [
    {
        'brand': '爱普生',
        'model': 'CH-TW6250',
        'purchase_links': {
            '京东': 'https://www.jd.com',
            '天猫': 'https://www.tmall.com'
        }
    }
]

html = generator.generate_html_page(
    title='投影仪推荐',
    chart_files=['price_comparison.png'],
    items=items,
    link_key='purchase_links'
)

generator.save_html(html, 'projector.html')
```

### 示例3：自定义名称格式

```python
from html_generator import HTMLGenerator

generator = HTMLGenerator()

html = generator.generate_html_page(
    title='投影仪推荐',
    chart_files=['price_comparison.png'],
    items=items,
    link_key='purchase_links',
    name_format=lambda item: f"{item['brand']} {item['model']} ({item['price']}元)"
)

generator.save_html(html, 'projector.html')
```

## 📝 版本历史

### v2.2.0 (2026-03-28)
- 🎉 初始版本
- ✨ 通用HTML页面生成
- ✨ 组件化设计
- ✨ 动态样式管理
- ✨ 购买链接支持

### v2.1.0 (2026-03-28)
- 🎉 项目基础版本
- ✨ HTML页面生成功能
- ✨ 图表嵌入功能
- ✨ 购买链接功能

## 📄 许可证

MIT License

---

<div align="center">

**项目状态**: ✅ 完成
**当前版本**: v2.2.0
**中文支持**: ✅ 完全支持，无乱码

如果这个项目对您有帮助，请给我们一个 ⭐️

</div>