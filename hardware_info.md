# 硬件信息检测工具

## 📋 概述

`hardware_info.py` 提供全面的硬件信息检测功能，用于获取计算机的详细硬件配置。

## 🎯 主要功能

### 1. CPU信息检测
- CPU型号和制造商
- 核心数和线程数
- 频率（MHz）
- 架构信息

### 2. GPU信息检测
- GPU品牌和型号
- 显存大小（MB和GB）
- 制造商（如NVIDIA、AMD）
- 物理GPU识别（过滤虚拟显卡）

### 3. 内存信息检测
- 内存总容量（GB）
- 内存频率（MHz）
- DDR类型（DDR3、DDR4等）
- 插槽数量和使用情况

### 4. 硬盘信息检测
- 硬盘型号
- 硬盘容量（GB）
- 读写速度（MB/s）
- 分区信息

### 5. BIOS信息检测
- BIOS版本号
- BIOS制造商
- BIOS日期
- 最新版本对比

### 6. 主板信息检测
- 主板品牌
- 主板型号
- 芯片组信息

## 🔧 技术实现

### 平台支持
- **Windows**: 使用WMIC命令获取硬件信息
- **Linux**: 使用`/proc`和`lshw`命令获取硬件信息
- **macOS**: 使用`system_profiler`命令获取硬件信息

### 检测方法
```python
class HardwareInfoCollector:
    """硬件信息收集器"""
    def get_cpu_info(self)
    def get_gpu_info(self)
    def get_memory_info(self)
    def get_disk_info(self)
    def get_bios_info(self)
    def get_motherboard_info(self)
```

### 数据结构
```python
{
    'cpu': {
        'brand': 'Intel',
        'model': 'Core i7-12700K',
        'cores': 12,
        'frequency': '3500MHz'
    },
    'gpu': {
        'brand': 'ASUSTeK',
        'model': 'RTX 3060',
        'memory': '12GB'
    },
    'memory': {
        'total': '32GB',
        'frequency': '3200MHz',
        'type': 'DDR4'
    },
    'disk': {
        'model': 'Samsung 980 PRO',
        'capacity': '1TB',
        'read_speed': '500MB/s',
        'write_speed': '450MB/s'
    }
}
```

## 📊 输出格式

### 硬件信息汇总
```
=== 硬件信息检测结果 ===

CPU信息:
  品牌: Intel
  型号: Core i7-12700K
  核心数: 12核
  频率: 3500MHz

GPU信息:
  品牌: ASUSTeK
  型号: RTX 3060
  显存: 12GB
  制造商: NVIDIA

内存信息:
  总容量: 32GB
  频率: 3200MHz
  DDR类型: DDR4

硬盘信息:
  型号: Samsung 980 PRO
  容量: 1TB
  读取速度: 500MB/s
  写入速度: 450MB/s

BIOS信息:
  版本: 3202
  制造商: American Megatrends
  日期: 2023-05-15
  是否最新: 否 (最新版本: 3205)

主板信息:
  品牌: ASUSTeK
  型号: PRIME Z690-P
  芯片组: Intel Z690
```

## 🔧 系统要求

### Python依赖
```python
psutil >= 5.8.0
```

### 系统要求
- Python 3.7+
- Windows 10/11 或 Linux/macOS
- 管理员权限（用于获取硬件信息）

## 📝 使用示例

### 基本检测
```python
from hardware_info import HardwareInfoCollector

collector = HardwareInfoCollector()
hardware_info = collector.get_all_hardware_info()
print(hardware_info)
```

### 集成调用
```python
from integrated_system import HardwareDetector

detector = HardwareDetector()
detector.detect_and_display()
```

## 🐛 故障排除

### 常见问题

#### 1. 无法获取GPU信息
**问题**: GPU信息显示为"未知"
**解决**: 
- 检查显卡驱动是否正常安装
- 确认使用物理GPU而非虚拟GPU

#### 2. 内存频率显示为0
**问题**: 内存频率显示为0MHz
**解决**: 
- 更新WMIC命令参数
- 检查内存模块是否正常工作

#### 3. BIOS版本对比失败
**问题**: BIOS是否最新显示"未知"
**解决**: 
- 更新BIOS版本数据库
- 检查网络连接是否正常

#### 4. 硬盘速度异常
**问题**: 读写速度显示异常高值
**解决**: 
- 修正速度计算方法
- 检查硬盘健康状态

## 📞 版本信息

- **版本**: v1.2.0
- **更新日期**: 2026-03-28
- **支持平台**: Windows、Linux、macOS

## 🎉 特色功能

1. **全面硬件检测**: 覆盖CPU、GPU、内存、硬盘、BIOS、主板
2. **智能GPU识别**: 自动过滤虚拟GPU，识别物理显卡
3. **BIOS版本对比**: 自动检查BIOS是否为最新版本
4. **跨平台支持**: 支持Windows、Linux、macOS三大平台
5. **详细参数显示**: 提供频率、容量、速度等详细技术参数

---

**享受使用硬件信息检测工具！** 💻