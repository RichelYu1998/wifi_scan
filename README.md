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

### Windows用户

**直接运行Python**：
```bash
python wifi_scan.py
```

### Linux/macOS用户

```bash
python3 wifi_scan.py
```

### 使用启动脚本（推荐）

项目提供了跨平台的启动脚本，会自动检测虚拟环境并运行程序：

**Linux/macOS**:
```bash
cd scripts
./start.sh
```

**Windows**:
```cmd
cd scripts
start.bat
```

启动脚本功能：
- 自动检测虚拟环境（.venv/venv/env）
- 自动检查并安装依赖库
- 交互式菜单选择功能
- 支持自定义参数运行
- **支持直接启动Web界面（`--web`参数）**

## 📋 功能说明

### 1. WiFi网络扫描
- 扫描周围WiFi网络（支持Windows/macOS/Linux）
- 显示网络详细信息（SSID、信道、信号强度、BSSID）
- 信号质量评估（优秀/良好/一般/差）
- 信道优化建议
- CSV导出功能
- 历史信道分析
- 推荐信道智能推荐

### 2. 硬件信息检测
- **CPU信息**：型号、核心数、频率、架构
- **GPU信息**：品牌、型号、显存
- **内存信息**：容量、使用率
- **系统信息**：操作系统、版本、架构
- **主板信息**：品牌、型号、芯片组
- **磁盘信息**：容量、类型
- **BIOS信息**：版本、制造商、日期

### 3. Web界面
- 现代化Web界面（基于Flask）
- 实时显示WiFi扫描结果
- 硬件信息可视化
- 地理位置与运营商信息
- 历史信道分析
- 推荐信道智能推荐
- 响应式设计，浅色渐变背景

### 4. JSON文件管理
- JSON文件统计信息
- 文件重新组织
- 日期格式修复

## 🔧 系统要求

- Python 3.7+
- Windows 10/11 / Linux / macOS
- 网络连接（用于地理位置获取）
- 无线网卡（用于WiFi扫描）

## 📦 安装依赖

### 创建虚拟环境（推荐）
```bash
python -m venv .venv
```

### 激活虚拟环境
**Windows**:
```bash
.venv\Scripts\activate
```

**Linux/macOS**:
```bash
source .venv/bin/activate
```

### 安装依赖
```bash
pip install psutil requests geopy flask flask-cors
```

## 🎯 命令行参数

### WiFi网络扫描
```bash
python wifi_scan.py
```

### 硬件信息检测
```bash
python wifi_scan.py --hardware
```

### 完整系统测试
```bash
python wifi_scan.py --all-in-one
```

### 导出CSV
```bash
python wifi_scan.py --export ./report.csv
```

### 显示调试信息
```bash
python wifi_scan.py --debug
```

### 启动Web界面
```bash
python wifi_scan.py --web
```

### JSON文件管理
```bash
python wifi_scan.py --json-stats          # 显示统计信息
python wifi_scan.py --organize-json       # 重新组织文件
python wifi_scan.py --fix-date-format     # 修复日期格式
```

### 数据库更新
```bash
python wifi_scan.py --update-mapping      # 更新映射配置
python wifi_scan.py --update-hardware-db  # 更新硬件数据库
python wifi_scan.py --update-all          # 更新所有数据库
```

### 显示帮助
```bash
python wifi_scan.py --help
```

## 📊 项目结构

```
wifi_scan/
├── wifi_scan.py              # 核心集成系统（主程序）
├── index.html                 # Web界面
├── json/                     # 数据文件夹
│   ├── config/               # 配置文件
│   ├── hardware/              # 硬件数据
│   │   ├── cpu_performance.json
│   │   ├── gpu_performance.json
│   │   └── memory_performance.json
│   ├── logs/                  # 日志文件
│   └── network/               # 网络数据
├── scripts/                   # 脚本文件
│   ├── start.sh              # Linux/macOS启动脚本
│   └── start.bat             # Windows启动脚本
└── README.md                 # 项目说明文档
```

## 🐛 故障排除

### 依赖缺失
**问题**：ImportError或ModuleNotFoundError
**解决**：运行`pip install psutil requests geopy flask flask-cors`安装依赖

### Python版本不兼容
**问题**：显示"Python版本过低"错误
**解决**：升级到Python 3.7+

### 中文显示乱码
**问题**：中文显示为乱码
**解决**：确保终端使用UTF-8编码

### WiFi扫描失败
**问题**：无法扫描WiFi网络
**解决**：
- 确保以管理员权限运行（Windows）
- 确保WiFi适配器正常工作
- Linux用户：确保有网络管理权限
- macOS用户：确保有WiFi访问权限
- 检查是否有其他WiFi管理程序冲突

### Flask未安装
**问题**：Web界面无法启动
**解决**：
```bash
pip install flask flask-cors
```

## 📝 版本信息

### v3.5.0 (2026-05-09) - Linux支持与Web启动优化

#### ✨ 新增功能
1. **Linux WiFi扫描支持**
   - 添加完整的Linux WiFi扫描实现
   - 支持多种扫描方式：nmcli、iwlist、iw命令
   - 自动检测无线网卡接口
   - 频率自动转换为信道

2. **启动脚本Web模式**
   - 添加`--web`参数支持，直接启动Web界面
   - Windows脚本支持：`start.bat --web`
   - Linux/macOS脚本支持：`./start.sh --web`
   - 自动检测并安装Flask依赖

3. **Flask安装优化**
   - 升级pip后再安装Flask
   - 备用安装方案（指定版本flask==2.3.0）
   - 自动验证Flask安装

#### 🔧 代码优化
1. **跨平台兼容性增强**
   - Windows、macOS、Linux三大平台全面支持
   - 统一的WiFi扫描接口

2. **启动脚本改进**
   - 命令行参数解析
   - Web模式快速初始化
   - 菜单模式保持不变

#### ✅ 测试通过
- ✅ Windows Web界面启动正常
- ✅ Flask依赖自动安装
- ✅ 跨平台脚本正常工作

### v3.4.0 (2026-04-28) - 代码精简与模块移除

#### 🔧 代码优化
1. **移除投影仪模块**
   - 删除 `ProjectorRecommender` 类（约560行代码）
   - 移除前端投影仪相关代码
   - 简化命令行参数
   - 更新README文档

2. **前端修复**
   - 修复JavaScript语法错误（乱码问题）
   - 移除未定义的 `filters` 变量引用

#### ✅ 测试通过
- ✅ WiFi扫描API正常
- ✅ 硬件信息API正常
- ✅ 前端页面加载正常

### v3.3.0 (2026-04-28) - Web界面与API服务

#### ✨ 新增功能
1. **Flask Web服务**
   - 新增 `app.py` 提供RESTful API服务
   - 支持跨域请求（CORS）
   - 端口5001提供Web服务

2. **前端Web界面**
   - 新增 `index.html` 现代化Web界面
   - 基于Vue 3 + Element Plus UI
   - 响应式设计，浅色渐变背景

3. **WiFi扫描页面**
   - 地理位置、运营商、IP地址卡片展示
   - 历史使用信道展示
   - 推荐信道智能推荐

4. **硬件信息页面**
   - CPU/显卡/内存/系统卡片式布局
   - 无线网卡信息展示（名称、WiFi标准、最大速度、频段）
   - 支持WiFi类型和可选网卡品牌展示

5. **完整报告页面**
   - 各大模块统计卡片
   - 快速导航按钮

#### 🔧 代码优化
1. **运营商名称本地化**
   - Chinanet → 中国电信
   - ChinaUnicom → 中国联通
   - ChinaMobile → 中国移动

2. **JSON数据处理**
   - 修正键名（操作系统、版本等中文键名）
   - 历史信道智能分析
   - 推荐信道算法优化

#### 🐛 Bug修复
- 修复硬件数据键名错误
- 修复网卡信息获取逻辑
- 修复端口冲突问题

#### ✅ 测试通过
- ✅ WiFi扫描API正常
- ✅ 硬件信息API正常
- ✅ 前端页面加载正常

### v3.2.0 (2026-04-15) - 跨平台路径管理系统

#### ✨ 新增功能
1. **跨平台路径管理系统**
   - 引入 `pathlib.Path` 替代 `os.path.join`
   - 统一使用 `Path` 对象进行路径操作
   - 消除了硬编码的路径分隔符问题

2. **统一路径管理方法**
   - `get_config_path()` - 配置文件路径
   - `get_hardware_path()` - 硬件文件路径  
   - `get_network_path()` - 网络文件路径
   - `get_log_path()` - 日志文件路径

3. **统一目录创建**
   - 添加 `ensure_dir_exists()` 方法统一处理目录创建
   - 自动处理父目录创建

4. **统一文件名清理**
   - 添加 `sanitize_filename()` 方法统一处理文件名清理
   - 移除了重复的 `clean_filename()` 方法
   - 统一处理跨平台非法字符

#### 🔧 代码优化
1. **代码精简**
   - 优化了 **19处** `os.makedirs()` 调用
   - 替换了 **10处** 硬编码路径
   - 统一了 **7处** 文件名清理逻辑
   - 添加了 **6个** 统一路径管理方法

2. **跨平台兼容性**
   - 统一使用 `pathlib.Path`，支持 Windows/Linux/macOS
   - 自动处理不同操作系统的路径分隔符
   - 统一的错误处理和目录创建逻辑

3. **代码复用**
   - 消除重复代码，提高可维护性
   - 所有路径操作集中在 `UnifiedUtils` 类中
   - 统一的目录创建和错误处理机制

### v3.1.6 (2026-04-10) - 环境检测系统完善

#### ✨ 新增功能
1. **环境检测系统**
   - 完善系统环境检测功能
   - 支持多平台环境适配

2. **网络更新策略优化**
   - 默认禁用网络更新，快速启动
   - 手动触发更新机制
   - CDN加速支持

#### 🔧 代码优化
1. **网络请求优化**
   - 添加超时处理
   - 异常捕获机制
   - 跳过网络更新选项

### v3.0.1 (2026-04-05) - 稳定性回退版本

#### 🐛 Bug修复
- 修复文件名中显示unknown的问题
- 修复WiFiChannelScanner类缺少get_location_info方法的问题
- 修复地理位置映射大小写敏感问题

#### 🔧 代码优化
1. **网络更新优化**
   - 添加跳过网络更新选项
   - 优化网络请求速度
   - CDN加速支持

### v3.0.0 (2026-04-01) - 初始版本

#### ✨ 主要功能
1. **WiFi信道扫描**
   - Windows WiFi扫描支持
   - 网络信息获取

2. **硬件信息检测**
   - CPU信息检测
   - GPU信息检测
   - 内存信息检测

3. **JSON数据管理**
   - 配置文件管理
   - 硬件数据库
   - 网络数据存储