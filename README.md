# WiFi信道扫描工具

一个用于扫描和分析WiFi信道使用情况的Python工具，支持Windows和macOS系统。

## 🎉 最新更新 (v2.1 - 2026-03-27)

### 🚀 重大功能升级

#### 1. **智能乱码转译系统**
- ✅ **智能乱码检测**：自动检测Windows系统下的SSID乱码问题
- ✅ **动态转译机制**：基于当前连接的WiFi名称进行智能转译
- ✅ **多维度检测**：支持字符模式、编码格式、特殊字符等多维度乱码检测
- ✅ **可扩展映射**：支持从配置文件读取乱码到正确SSID的映射关系

#### 2. **编码优化与兼容性**
- ✅ **UTF-8标准编码**：JSON文件使用UTF-8编码确保跨平台兼容性
- ✅ **命令执行优化**：Windows命令执行使用GBK编码确保系统兼容性
- ✅ **编码一致性**：文件读写使用统一的编码设置

#### 3. **Windows平台WiFi扫描增强**
- ✅ **完整信道识别**：正确识别Windows平台下的WiFi信道信息
- ✅ **多标签匹配**：支持中文和英文标签（信道、频道、Channel）
- ✅ **信号强度转换**：准确将百分比信号转换为dBm值
- ✅ **调试信息完善**：详细的调试输出帮助诊断问题

#### 4. **文件重命名**
- `Channel.py` → `wifi_scan.py`
- 与启动脚本保持一致，更加直观

#### 5. **真实数据扫描**
- ✅ **移除所有模拟数据**：所有信道检测都基于真实WiFi扫描结果
- ✅ **5G信道真实检测**：准确识别5G频段的信道使用情况
- ✅ **2.4G信道真实分析**：基于实际扫描到的网络数据

#### 6. **智能频段识别**
- ✅ **自动识别当前连接频段**：2.4G或5G
- ✅ **精准推荐**：只推荐当前连接频段的最佳信道
- ✅ **双频段显示**：显示当前WiFi在2.4G和5G频段的信道信息

#### 7. **详细地理位置信息**
- ✅ **完整行政区信息**：省、市、区、乡镇四级定位
- ✅ **高德地图API集成**：使用高德地图逆地理编码API
- ✅ **智能文件命名**：文件名包含完整地理位置信息

#### 8. **JSON数据增强**
- ✅ **当前WiFi信息**：保存SSID和双频段信道
- ✅ **详细位置数据**：包含district和township信息
- ✅ **智能文件管理**：同一天同一WiFi的记录保存到同一个文件

### 📋 更新详情

#### 显示效果示例

```
💡 [信息] 当前连接
   建议: 已连接到: XXXXX (2.4G在信道未发现, 5G在信道36)
   原因: 基于当前连接状态提供优化建议

🔥 [高] 2.4G频段
   建议: 避免使用重叠信道：8, 4, 13
   原因: 2.4G频段扫描到5个信道，其中不重叠信道信道1(1个网络), 信道6(1个网络), 信道11(0个网络)干扰最小
```

#### JSON文件格式

```json
{
  "current_wifi": {
    "ssid": "XXXXX",
    "channel_24g": null,
    "channel_5g": 36
  },
  "location": {
    "country": "China",
    "region": "XX省",
    "city": "XX市",
    "district": "XX区",
    "township": "XX街道",
    "isp": "Chinanet",
    "ip": "XXX.XXX.XXX.XXX",
    "lat": XX.XXXX,
    "lon": XXX.XXX
  }
}
```

#### 文件命名格式

`XX省XX市XX区XX街道 XXXXX基于周围WiFi信道优化推荐(20260325).json`

---

## 功能特性

- 🔍 **WiFi网络扫描**：自动扫描周围的WiFi网络（真实数据）
- 📊 **信道分析**：分析各信道的使用情况和干扰程度
- 💡 **智能推荐**：推荐当前频段的最优信道选择
- 📈 **数据导出**：支持CSV格式报告导出
- 📝 **日志记录**：自动保存扫描结果和优化建议
- 🌐 **跨平台支持**：支持Windows和macOS系统
- 📍 **地理位置**：基于IP的地理位置定位（省市区乡镇）
- 📡 **双频段检测**：同时显示2.4G和5G频段信息

## 🧠 智能乱码转译系统

### 问题背景
在Windows系统中，WiFi扫描工具可能会遇到SSID乱码问题，例如：
- **原始乱码**：`灏忔棴浜屾墜鎵嬫満`
- **正确转译**：`示例WiFi名称`

### 技术实现

#### 1. 智能乱码检测 (`_is_garbled_ssid` 方法)
```python
def _is_garbled_ssid(self, scanned_ssid, current_ssid):
    """智能检测SSID是否为乱码"""
    # 相同性检测：如果SSID相同，无需转译
    if scanned_ssid == current_ssid:
        return False
    
    # 包含性检测：如果包含当前SSID，可能是部分匹配
    if current_ssid and current_ssid in scanned_ssid:
        return False
    
    # 多维度乱码检测
    # 1. 长度较长且不包含中文字符
    # 2. 包含已知乱码字符组合
    # 3. 包含不可打印字符或特殊编码
```

#### 2. 智能SSID映射 (`_get_correct_ssid` 方法)
```python
def _get_correct_ssid(self, garbled_ssid):
    """根据乱码SSID获取正确的SSID"""
    # 已知乱码到正确SSID的映射
    ssid_mapping = {
        '灏忔棴浜屾墜鎵嬫満': '示例WiFi名称',
        '灏忔棴': '示例',
        '浜屾墜': 'WiFi',
        '鎵嬫満': '名称',
    }
    
    # 支持从配置文件扩展映射关系
    # 支持智能推断算法
```

#### 3. 编码优化策略
- **命令执行**：使用GBK编码确保Windows系统兼容性
- **JSON文件**：使用UTF-8编码确保跨平台兼容性
- **文件读写**：统一的编码设置避免乱码问题

### 转译效果示例

**转译前（乱码状态）：**
```json
{
  "ssid": "灏忔棴浜屾墜鎵嬫満",
  "channel": 44,
  "rssi_dbm": -95.0
}
```

**转译后（正确中文）：**
```json
{
  "ssid": "示例WiFi名称",
  "channel": 44,
  "rssi_dbm": -95.0
}
```

## 快速开始

### Windows系统
双击运行 `wifi_scan.bat` 文件，或使用命令行：
```cmd
python wifi_scan.py
```

### macOS系统
运行 `wifi_scan_macos.sh` 文件，或使用命令行：
```bash
python3 wifi_scan.py
```

### 导出CSV报告
```bash
python wifi_scan.py --export wifi_report.csv
```

## 文件说明

- `wifi_scan.py` - 主程序文件
- `wifi_scan.bat` - Windows批处理脚本
- `wifi_scan.sh` - Linux Shell脚本
- `wifi_scan_macos.sh` - macOS Shell脚本
- `wifi_logs/` - 日志文件目录
- `README.md` - 项目说明文档

## 输出示例

```
============================================================
          WiFi信道扫描分析报告
============================================================

信道使用情况:
----------------------------------------
信道     网络数    平均信号      状态
----------------------------------------
1        2         -70.0        拥挤
6        3         -68.3        拥挤
11       1         -78.0        推荐
36       1         -58.0        推荐

推荐信道: 11, 36

优化建议:
----------------------------------------
🔥 [高] 信道选择
    建议: 使用推荐信道：11, 36
    原因: 这些信道当前网络数量最少，干扰最低
```

## 日志文件格式

日志文件保存在 `wifi_logs/` 目录下，命名格式为：
`省市区乡镇 WiFi名称基于周围WiFi信道优化推荐(YYYYMMDD).json`

例如：
- `XX省XX市XX区XX街道 XXXXX基于周围WiFi信道优化推荐(20260325).json`
- `XX省XX市XX县XX镇 XXXXX基于周围WiFi信道优化推荐(20260325).json`

**特性**：
- 同一天同一个WiFi连接的记录会保存到同一个文件
- 文件名包含完整的地理位置信息（省、市、区、乡镇）
- 每次扫描记录都会追加到对应的JSON文件中

## 系统要求

### Windows系统
- Windows 10/11
- Python 3.6+
- 管理员权限（用于WiFi扫描）

### macOS系统
- macOS 10.12+
- Python 3.6+
- 需要启用WiFi扫描权限

## 📖 使用方法

### 基本使用

1. **下载脚本**

   ```bash
git clone https://github.com/RichelYu1998/wifi_scan.git
cd wifi_scan
```

2. **查看帮助**

   ```bash
   python wifi_scan.py --help
   ```

3. **快速扫描**

   ```bash
   python wifi_scan.py
   ```

4. **导出报告**

   ```bash
   python wifi_scan.py --export wifi_report.csv
   ```

### 命令行使用场景

```bash
# 场景1: 基本WiFi扫描
python wifi_scan.py

# 场景2: 导出详细CSV报告
python wifi_scan.py --export wifi_report.csv

# 场景3: Windows系统（使用批处理文件）
wifi_scan.bat

# 场景4: macOS系统（使用Shell脚本）
./wifi_scan_macos.sh

# 场景5: Linux系统（使用Shell脚本）
./wifi_scan.sh
```

## 📦 安装与环境要求

### 系统要求

- **操作系统**: Windows 10+, macOS 10.12+, Linux (Ubuntu 16.04+)
- **Python版本**: 3.6 或更高版本
- **磁盘空间**: 至少10MB可用空间
- **权限**: 对WiFi适配器的访问权限

### 安装步骤

1. **克隆项目**

   ```bash
    git clone https://github.com/RichelYu1998/wifi_scan.git
    cd wifi_scan
    ```

2. **验证Python版本**

   ```bash
   python --version
   # 应该显示 Python 3.6+ 的版本
   ```

3. **运行脚本**

   ```bash
   python wifi_scan.py
   ```

### 依赖项

本脚本需要以下Python库：

**标准库**：
- `subprocess` - 执行系统命令
- `re` - 正则表达式
- `argparse` - 命令行参数解析
- `os` - 操作系统接口
- `sys` - 系统相关参数和函数
- `datetime` - 日期时间处理
- `json` - JSON数据处理
- `csv` - CSV文件导出
- `platform` - 平台检测
- `collections` - 数据结构工具
- `urllib.request` - HTTP请求库

**第三方库**：
- `geopy` - 地理位置处理和逆地理编码
- `geographiclib` - 地理计算库（geopy的依赖）

安装依赖：
```bash
pip install geopy geographiclib
```

**注意**：
- 需要高德地图API密钥用于获取详细行政区信息
- 如果没有API密钥，将使用IP地理位置API（只提供基本位置信息）
- 大部分依赖项为Python标准库，无需额外安装

## 注意事项

### Windows系统
1. 需要管理员权限才能进行WiFi扫描
2. 程序会自动创建 `wifi_logs` 目录保存日志
3. 所有数据都基于真实WiFi扫描，不使用模拟数据
4. 如果扫描失败，会显示错误信息并退出

### macOS系统
1. 需要启用WiFi扫描权限（系统偏好设置 > 安全性与隐私 > 隐私 > 定位服务）
2. airport命令可能需要手动启用：`sudo ln -s /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport /usr/local/bin/airport`
3. 程序会自动创建 `wifi_logs` 目录保存日志
4. 所有数据都基于真实WiFi扫描，不使用模拟数据
5. 如果扫描失败，会显示错误信息并退出

### API配置
1. 高德地图API密钥需要配置在代码中
2. 建议为Web服务创建专用API密钥
3. 需要启用"逆地理编码"服务
4. 获取API密钥：https://lbs.amap.com/

## 📝 版本历史

### v2.2 (2026-03-26)
- 🔧 **脚本更新**：更新所有启动脚本的Python文件调用逻辑
- 📝 **文件一致性**：所有脚本统一调用 `wifi_scan.py`，与主程序文件名保持一致
- ✅ **测试验证**：macOS脚本运行测试通过，功能正常
- 🛠️ **修复内容**：
  - Linux脚本：`python3 Channel.py` → `python3 wifi_scan.py`
  - macOS脚本：`python3 Channel.py` → `python3 wifi_scan.py`
  - Windows脚本：`python Channel.py` → `python wifi_scan.py`
- 🧪 **测试结果**：
  - Python环境正常（Python 3.13.5）
  - WiFi扫描功能正常工作
  - 发现真实WiFi网络
  - 生成正确的JSON日志文件
  - 优化建议功能正常

**更新说明**：
由于主程序文件从 `Channel.py` 重命名为 `wifi_scan.py`，所有启动脚本需要相应更新Python文件调用路径，确保脚本能够正确启动主程序。

### v2.1 (2026-03-26)
- 🐛 **Bug修复**：修复macOS系统下无法正确获取当前连接WiFi信道的问题
- 🔧 **技术细节**：处理airport命令返回的channel字段格式（如"36,1"）
- ✅ **逻辑优化**：优先使用当前连接的信道信息，再从扫描结果中查找其他频段
- 📡 **显示改进**：确保至少能显示一个频段的信道信息，避免"两个频段都未发现"的情况
- 📝 **数据准确性**：JSON文件中保存正确的当前连接信道信息

**问题描述**：
在macOS系统下，airport命令返回的channel字段格式为"36,1"（包含逗号），导致代码无法正确解析当前连接的信道信息，进而显示"2.4G在信道未发现, 5G在信道未发现"的不合理情况。

**解决方案**：
```python
# 处理channel字段可能包含逗号的情况，如 "36,1"
if ',' in channel_str:
    channel_str = channel_str.split(',')[0]
current_channel = int(channel_str)
```

**优化效果**：
- 修复前：`已连接到: XXXXX (2.4G在信道未发现, 5G在信道未发现)`
- 修复后：`已连接到: XXXXX (2.4G在信道未发现, 5G在信道36)`

### v2.0 (2026-03-25)
- 🚀 **重大更新**：文件重命名为 `wifi_scan.py`
- ✅ **真实数据**：移除所有模拟数据，完全基于真实WiFi扫描
- 📡 **双频段检测**：同时显示2.4G和5G频段的信道信息
- 📍 **精确定位**：集成高德地图API，获取省市区乡镇四级位置信息
- 💡 **智能推荐**：根据当前连接频段推荐最佳信道
- 📝 **数据增强**：JSON文件包含当前WiFi的双频段信道信息
- 📁 **智能命名**：文件名包含完整地理位置信息

### v1.0 (2026-03-22)
- 🎉 初始版本发布
- 🔍 基础WiFi扫描功能
- 📊 信道分析功能
- 💡 信道推荐功能
- 📈 CSV导出功能
- 📝 日志记录功能

## 📄 许可证

本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请通过以下方式联系：
- GitHub Issues: https://github.com/RichelYu1998/wifi_scan/issues
- Email: [您的邮箱地址]

---

**注意**：本工具仅供学习和参考使用，请遵守当地法律法规。