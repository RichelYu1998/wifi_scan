# 跨平台工具 (CrossPlatformUtils)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

跨平台工具类，提供跨平台兼容性支持

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

跨平台工具类是一个功能强大的工具类，提供跨平台兼容性支持，确保代码在Windows、Linux和macOS上都能正常运行。

### 特点

- ✅ **跨平台支持** - 支持Windows/Linux/macOS
- ✅ **路径处理** - 统一的路径处理
- ✅ **编码处理** - 统一的编码处理
- ✅ **命令执行** - 统一的命令执行
- ✅ **中文支持** - 中文显示无乱码

## ✨ 功能介绍

### 1. 系统检测
- 检测操作系统
- 检测Python版本
- 检测系统架构

### 2. 路径处理
- 统一路径分隔符
- 路径转换
- 路径拼接

### 3. 编码处理
- 智能编码检测
- 编码转换
- UTF-8编码支持

### 4. 命令执行
- 跨平台命令执行
- 命令输出捕获
- 错误处理

## 🚀 快速开始

### 基本使用

```python
from cross_platform_utils import CrossPlatformUtils

# 创建工具实例
utils = CrossPlatformUtils()

# 检测操作系统
system = utils.get_system()
print(f"操作系统: {system}")

# 处理路径
path = utils.normalize_path('path/to/file')
print(f"路径: {path}")

# 执行命令
result = utils.run_command('echo Hello')
print(f"输出: {result['output']}")
```

### 命令行使用

```bash
python cross_platform_utils.py
```

## 🔧 API文档

### CrossPlatformUtils类

#### `__init__()`
初始化跨平台工具。

**参数**: 无

**返回**: 无

**示例**:
```python
utils = CrossPlatformUtils()
```

#### `get_system()`
获取操作系统。

**参数**: 无

**返回**: str - 操作系统名称

**示例**:
```python
system = utils.get_system()
```

#### `is_windows()`
判断是否为Windows系统。

**参数**: 无

**返回**: bool - 是否为Windows

**示例**:
```python
if utils.is_windows():
    print("Windows系统")
```

#### `is_linux()`
判断是否为Linux系统。

**参数**: 无

**返回**: bool - 是否为Linux

**示例**:
```python
if utils.is_linux():
    print("Linux系统")
```

#### `is_macos()`
判断是否为macOS系统。

**参数**: 无

**返回**: bool - 是否为macOS

**示例**:
```python
if utils.is_macos():
    print("macOS系统")
```

#### `normalize_path(path)`
规范化路径。

**参数**:
- `path` (str): 路径

**返回**: str - 规范化后的路径

**示例**:
```python
path = utils.normalize_path('path/to/file')
```

#### `join_path(*paths)`
拼接路径。

**参数**:
- `*paths` (str): 路径片段

**返回**: str - 拼接后的路径

**示例**:
```python
path = utils.join_path('dir', 'subdir', 'file.txt')
```

#### `run_command(command, capture_output=True)`
执行命令。

**参数**:
- `command` (str): 命令
- `capture_output` (bool, optional): 是否捕获输出

**返回**: dict - 执行结果

**示例**:
```python
result = utils.run_command('echo Hello')
```

#### `get_encoding()`
获取系统编码。

**参数**: 无

**返回**: str - 系统编码

**示例**:
```python
encoding = utils.get_encoding()
```

## 💡 使用示例

### 示例1：系统检测

```python
from cross_platform_utils import CrossPlatformUtils

utils = CrossPlatformUtils()

# 检测操作系统
system = utils.get_system()
print(f"操作系统: {system}")

# 判断系统类型
if utils.is_windows():
    print("Windows系统")
elif utils.is_linux():
    print("Linux系统")
elif utils.is_macos():
    print("macOS系统")
```

### 示例2：路径处理

```python
from cross_platform_utils import CrossPlatformUtils

utils = CrossPlatformUtils()

# 规范化路径
path = utils.normalize_path('path/to/file')
print(f"路径: {path}")

# 拼接路径
path = utils.join_path('dir', 'subdir', 'file.txt')
print(f"路径: {path}")
```

### 示例3：命令执行

```python
from cross_platform_utils import CrossPlatformUtils

utils = CrossPlatformUtils()

# 执行命令
result = utils.run_command('echo Hello')
print(f"输出: {result['output']}")
print(f"错误: {result['error']}")
print(f"返回码: {result['returncode']}")
```

### 示例4：编码处理

```python
from cross_platform_utils import CrossPlatformUtils

utils = CrossPlatformUtils()

# 获取系统编码
encoding = utils.get_encoding()
print(f"系统编码: {encoding}")
```

## 📝 版本历史

### v2.2.0 (2026-03-28)
- 🎉 初始版本
- ✨ 跨平台支持
- ✨ 路径处理
- ✨ 编码处理
- ✨ 命令执行

### v2.1.0 (2026-03-28)
- 🎉 项目基础版本
- ✨ 跨平台工具功能
- ✨ 路径处理
- ✨ 编码处理

## 📄 许可证

MIT License

---

<div align="center">

**项目状态**: ✅ 完成
**当前版本**: v2.2.0
**跨平台**: ✅ 支持 Windows/Linux/macOS
**中文支持**: ✅ 完全支持，无乱码

如果这个项目对您有帮助，请给我们一个 ⭐️

</div>