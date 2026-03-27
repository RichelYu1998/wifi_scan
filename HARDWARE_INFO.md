# 硬件信息检测器 (HardwareInfo)

## 功能概述

硬件信息检测器是一个跨平台的Python模块，用于自动检测和收集系统的硬件信息，包括CPU、显卡、内存等关键组件，并提供性能评分。

## 主要功能

### 1. CPU信息检测
- **跨平台支持**: Windows、macOS、Linux
- **检测内容**: 
  - CPU型号名称
  - 核心数量
  - 运行频率
  - 架构信息
- **系统命令**:
  - macOS: `sysctl` 命令
  - Windows: `wmic` 命令
  - Linux: `/proc/cpuinfo` 文件

### 2. 显卡信息检测
- **跨平台支持**: Windows、macOS、Linux
- **检测内容**:
  - 显卡型号名称
  - 显存容量
- **系统命令**:
  - macOS: `system_profiler SPDisplaysDataType`
  - Windows: `wmic path win32_VideoController get name`
  - Linux: `lspci` 命令

### 3. 内存信息检测
- **跨平台支持**: 使用 `psutil` 库统一检测
- **检测内容**:
  - 总内存容量
  - 可用内存
  - 内存使用率

### 4. 系统信息检测
- **检测内容**:
  - 操作系统类型
  - 系统版本
  - 系统架构
  - Python版本

### 5. 性能评分系统
- **评分维度**:
  - CPU性能 (40%权重)
  - 显卡性能 (40%权重)
  - 内存容量 (20%权重)
- **评分算法**:
  - 基于硬件型号的性能映射表
  - 硬件规格的量化评估
  - 加权综合评分

## 使用方法

### 基本使用
```python
from hardware_info import HardwareInfo

# 创建硬件信息检测器实例
hw = HardwareInfo()

# 获取完整的硬件信息
hardware_info = hw.get_hardware_info()

# 输出硬件信息
print(f"CPU: {hardware_info['cpu']['名称']}")
print(f"显卡: {hardware_info['gpu']['名称']}")
print(f"内存: {hardware_info['memory']['总容量_GB']}GB")
print(f"性能评分: {hardware_info['performance_score']}")
```

### 集成到其他模块
```python
from hardware_info import HardwareInfo

# 在视频分辨率推荐中使用硬件信息
hw = HardwareInfo()
hardware_info = hw.get_hardware_info()
performance_score = hardware_info['performance_score']

# 根据硬件性能调整视频分辨率推荐
# ...
```

## 输出格式

```json
{
  "cpu": {
    "名称": "Apple M2 Pro",
    "架构": "arm64",
    "核心数": 10,
    "频率_MHz": 3200
  },
  "gpu": {
    "名称": "Apple M2 Pro",
    "显存_MB": 8192
  },
  "memory": {
    "总容量_GB": 16.0,
    "可用_GB": 8.5,
    "使用率_%": 46.9
  },
  "system": {
    "操作系统": "Darwin",
    "版本": "22.4.0",
    "架构": "arm64",
    "Python版本": "3.13.5"
  },
  "performance_score": 85.5
}
```

## 跨平台兼容性

### macOS 支持
- ✅ Apple Silicon (M1/M2/M3系列)
- ✅ Intel Mac
- ✅ 系统命令: `sysctl`, `system_profiler`

### Windows 支持
- ✅ Windows 10/11
- ✅ 系统命令: `wmic`
- ✅ 备用方案: `psutil`

### Linux 支持
- ✅ Ubuntu/Debian/CentOS等主流发行版
- ✅ 系统文件: `/proc/cpuinfo`
- ✅ 系统命令: `lspci`

## 性能评分标准

### CPU性能评分
| 型号 | 评分 | 说明 |
|------|------|------|
| Apple M3/M2/M1 | 90-100 | 高性能ARM处理器 |
| Intel i9/Ryzen 9 | 85-100 | 高端桌面处理器 |
| Intel i7/Ryzen 7 | 75-85 | 中高端处理器 |
| Intel i5/Ryzen 5 | 60-75 | 主流处理器 |
| Intel i3/Ryzen 3 | 50-60 | 入门级处理器 |

### 显卡性能评分
| 型号 | 评分 | 说明 |
|------|------|------|
| RTX 4090/4080 | 95-100 | 旗舰级显卡 |
| RTX 4070/4060 | 85-95 | 高端显卡 |
| RTX 3060/3070 | 75-85 | 中端显卡 |
| GTX 1660/1650 | 60-75 | 入门级显卡 |

### 内存容量评分
| 容量 | 评分 | 说明 |
|------|------|------|
| 32GB+ | 100 | 超大内存 |
| 24GB | 95 | 大内存 |
| 16GB | 85 | 标准内存 |
| 8GB | 60 | 基础内存 |
| 4GB | 40 | 小内存 |

## 错误处理

- **优雅降级**: 如果系统命令失败，使用`psutil`作为备用方案
- **异常捕获**: 所有系统调用都有异常处理
- **调试日志**: 支持调试模式输出详细信息

## 依赖项

- `platform`: Python标准库
- `psutil`: 第三方库，用于内存和CPU信息检测
- `re`: 正则表达式处理

## 版本历史

- **v1.0** (2026-03-28): 初始版本，支持基本硬件信息检测
- **v1.1** (2026-03-28): 增加跨平台工具类集成，优化错误处理

## 作者

WiFi信道扫描工具开发团队