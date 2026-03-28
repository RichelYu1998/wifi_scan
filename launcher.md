 # 统一启动器 (CrossPlatformLauncher)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-success)

跨平台统一启动器，支持Windows/Linux/macOS

[快速开始](#-快速开始) • [功能介绍](#-功能介绍) • [使用文档](#-使用文档)

</div>

---

## 📋 目录

- [项目简介](#-项目简介)
- [功能介绍](#-功能介绍)
- [快速开始](#-快速开始)
- [安装指南](#-安装指南)
- [使用文档](#-使用文档)
- [API文档](#-api文档)
- [故障排除](#-故障排除)
- [版本历史](#-版本历史)
- [许可证](#-许可证)

## 🎯 项目简介

统一启动器是一个功能强大的跨平台工具，用于管理整个WiFi扫描与投影仪推荐系统的所有功能。它提供了统一的接口来运行各种Python脚本，并自动处理跨平台兼容性问题。

### 特点

- ✅ **跨平台支持** - 支持 Windows、Linux、macOS
- ✅ **自动环境管理** - 自动创建虚拟环境和安装依赖
- ✅ **统一接口** - 提供统一的脚本执行接口
- ✅ **友好界面** - 直观的菜单界面，详细的功能说明
- ✅ **错误处理** - 完善的错误处理和日志记录

## ✨ 功能介绍

### 1. 跨平台支持
- 自动检测操作系统（Windows/Linux/macOS）
- 自动选择合适的Python解释器
- 自动处理路径分隔符
- 自动处理编码问题

### 2. 环境管理
- 自动创建虚拟环境
- 自动安装项目依赖
- 自动检查依赖更新

### 3. 功能菜单
提供9个主要功能选项：
1. WiFi扫描工具
2. 硬件信息检测
3. 投影仪推荐器（交互式）
4. 投影仪图表生成器
5. 价格数据更新
6. 快速启动（完整流程）
7. 运行所有测试
8. 视频分辨率推荐
9. 网络速度测试

### 4. 脚本执行
- 统一的脚本执行接口
- 错误处理和日志记录
- 用户中断处理

## 🚀 快速开始

### Windows 用户

#### 方式1：双击启动（推荐）
```
双击 start.bat
```

#### 方式2：命令行启动
```bash
start.bat
```

#### 方式3：直接运行Python
```bash
python launcher.py
```

### Linux/macOS 用户

#### 方式1：命令行启动（推荐）
```bash
chmod +x start.sh
./start.sh
```

#### 方式2：直接运行Python
```bash
python3 launcher.py
```

### 首次运行

首次运行时，系统会自动：
1. 创建虚拟环境
2. 安装项目依赖
3. 初始化配置文件

## 📦 安装指南

### 系统要求

#### 最低要求
- Python 3.7+
- Windows 10+ / Linux / macOS 10.15+
- 网络连接（用于更新数据）

#### 推荐配置
- Python 3.8+
- 4GB+ 内存
- 稳定的网络连接

### 手动安装

如果自动安装失败，可以手动安装：

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 📖 使用文档

### 功能菜单

启动后可以选择以下功能：

| 选项 | 功能 | 说明 |
|------|------|------|
| 1 | WiFi扫描工具 | 扫描WiFi网络 |
| 2 | 硬件信息检测 | 检测硬件信息 |
| 3 | 投影仪推荐器（交互式） | 根据预算推荐投影仪 |
| 4 | 投影仪图表生成器 | 生成价格对比图表 |
| 5 | 价格数据更新 | 更新投影仪价格数据 |
| 6 | 快速启动（完整流程） | 一键执行完整流程 |
| 7 | 运行所有测试 | 运行全面测试 |
| 8 | 视频分辨率推荐 | 推荐视频分辨率 |
| 9 | 网络速度测试 | 测试网络速度 |
| 0 | 退出 | 退出程序 |

### 使用示例

#### WiFi扫描
1. 运行启动脚本
2. 选择"1" - WiFi扫描工具
3. 查看扫描结果

#### 投影仪推荐
1. 运行启动脚本
2. 选择"3" - 投影仪推荐器（交互式）
3. 输入您的预算
4. 选择是否使用国补价格
5. 查看推荐结果

#### 生成图表
1. 运行启动脚本
2. 选择"4" - 投影仪图表生成器
3. 等待图表生成完成
4. 打开 `charts/projector_comparison.html` 查看结果

## 🔧 API文档

### CrossPlatformLauncher类

#### `__init__()`
初始化启动器。

**参数**: 无

**返回**: 无

**示例**:
```python
launcher = CrossPlatformLauncher()
```

#### `_get_python_exe()`
获取Python可执行文件路径。

**参数**: 无

**返回**: str - Python可执行文件路径

**示例**:
```python
python_exe = launcher._get_python_exe()
```

#### `_setup_environment()`
设置运行环境。

**参数**: 无

**返回**: 无

**功能**:
- 创建虚拟环境（如果不存在）
- 安装项目依赖

**示例**:
```python
launcher._setup_environment()
```

#### `_run_script(script_name, args=None)`
运行指定的Python脚本。

**参数**:
- `script_name` (str): 脚本文件名
- `args` (list, optional): 脚本参数

**返回**: bool - 是否运行成功

**示例**:
```python
success = launcher._run_script('wifi_scan.py')
```

#### `_test_all_scripts()`
测试所有脚本。

**参数**: 无

**返回**: bool - 所有测试是否通过

**功能**:
- 运行所有测试脚本
- 显示测试结果汇总

**示例**:
```python
all_passed = launcher._test_all_scripts()
```

#### `_show_menu()`
显示功能菜单。

**参数**: 无

**返回**: 无

**功能**:
- 显示系统信息
- 显示所有功能选项

**示例**:
```python
launcher._show_menu()
```

#### `run()`
运行启动器主循环。

**参数**: 无

**返回**: int - 退出码

**功能**:
- 初始化环境
- 显示菜单
- 处理用户输入

**示例**:
```python
exit_code = launcher.run()
```

## 🔍 故障排除

### Windows用户

#### 编码问题
如果遇到中文乱码：
1. 确保使用UTF-8编码的终端
2. 运行 `chcp 65001` 设置编码
3. 使用 `start.bat` 启动

#### 依赖问题
如果依赖安装失败：
```bash
pip install -r requirements.txt
```

### Linux/macOS用户

#### 权限问题
如果遇到权限问题：
```bash
chmod +x start.sh
```

#### 依赖问题
如果依赖安装失败：
```bash
pip3 install -r requirements.txt
```

### 通用问题

#### 网络连接问题
如果无法从网络获取数据，系统会自动使用默认数据。

#### 虚拟环境问题
如果虚拟环境创建失败，可以手动创建：
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

## 📝 版本历史

### v2.2.0 (2026-03-28)
- 🎉 初始版本
- ✨ 跨平台支持（Windows/Linux/macOS）
- ✨ 自动环境管理
- ✨ 9个功能选项，每个都有详细说明
- ✨ 统一的脚本执行接口
- ✨ 完善的错误处理

### v2.1.0 (2026-03-28)
- 🎉 项目基础版本
- ✨ WiFi扫描功能
- ✨ 硬件信息检测功能
- ✨ 投影仪推荐功能
- ✨ 价格对比功能
- ✨ 图表生成功能
- ✨ 视频分辨率推荐功能
- ✨ 网络速度测试功能

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