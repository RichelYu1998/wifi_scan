# WiFi扫描与硬件检测工具

跨平台WiFi信道扫描与硬件信息检测工具，支持Windows、macOS、Linux系统。

## 🚀 快速启动

### Web界面（推荐）

使用启动脚本直接启动Web界面：

**Linux/macOS**:
```bash
cd scripts
./start.sh --web
```

**Windows**:
```cmd
cd scripts
start.bat --web
```

Web界面访问地址：http://localhost:5001

### 命令行模式

**Linux/macOS**:
```bash
python3 wifi_scan.py
```

**Windows**:
```cmd
python wifi_scan.py
```

## 📋 功能说明

### 1. WiFi网络扫描
- 扫描周围WiFi网络（支持Windows/macOS/Linux）
- 显示网络详细信息（SSID、信道、信号强度、BSSID）
- 信号质量评估
- 信道优化建议
- CSV导出功能

### 2. 硬件信息检测
- **CPU信息**：型号、核心数、频率、架构
- **GPU信息**：品牌、型号、显存
- **内存信息**：容量、使用率
- **系统信息**：操作系统、版本、架构
- **主板信息**：品牌、型号、芯片组
- **磁盘信息**：容量、类型

### 3. Web界面
- 现代化Web界面（基于Flask）
- 实时显示WiFi扫描结果
- 硬件信息可视化
- 地理位置与运营商信息
- 历史信道分析
- 推荐信道智能推荐

### 4. JSON文件管理
- JSON文件统计信息
- 文件重新组织
- 日期格式修复

## 🎯 命令行参数

```bash
# WiFi网络扫描
python wifi_scan.py

# 硬件信息检测
python wifi_scan.py --hardware

# 完整系统测试
python wifi_scan.py --all-in-one

# 导出CSV
python wifi_scan.py --export ./report.csv

# 显示调试信息
python wifi_scan.py --debug

# 启动Web界面
python wifi_scan.py --web

# JSON文件管理
python wifi_scan.py --json-stats          # 显示统计信息
python wifi_scan.py --organize-json       # 重新组织文件
python wifi_scan.py --fix-date-format     # 修复日期格式

# 数据库更新
python wifi_scan.py --update-mapping      # 更新映射配置
python wifi_scan.py --update-hardware-db  # 更新硬件数据库

# 显示帮助
python wifi_scan.py --help
```

## 🔧 系统要求

- Python 3.7+
- Windows 10/11 / Linux / macOS
- 网络连接（用于地理位置获取）
- 无线网卡（用于WiFi扫描）

## 📦 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 安装依赖
pip install psutil requests geopy flask flask-cors
```

## 📁 项目结构

```
wifi_scan/
├── wifi_scan.py          # 主程序
├── index.html            # Web界面
├── json/                 # 数据文件夹
│   ├── config/          # 配置文件
│   ├── hardware/        # 硬件数据
│   ├── logs/            # 日志文件
│   └── network/         # 网络数据
├── scripts/              # 启动脚本
│   ├── start.bat        # Windows启动脚本
│   └── start.sh         # Linux/macOS启动脚本
└── README.md            # 项目说明
```

## 🐛 故障排除

### WiFi扫描失败
- Windows：确保以管理员权限运行
- Linux：确保有网络管理权限
- macOS：确保有WiFi访问权限

### Flask未安装
```bash
pip install flask flask-cors
```

### 中文显示乱码
确保终端使用UTF-8编码

## 📝 版本信息

### v3.5.0 (2026-05-09)

- Linux WiFi扫描支持（nmcli/iwlist/iw）
- 启动脚本添加`--web`参数
- 跨平台全面支持（Windows/macOS/Linux）