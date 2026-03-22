# WiFi信道扫描工具

一个用于扫描和分析WiFi信道使用情况的Python工具，支持Windows和macOS系统。

## 功能特性

- 🔍 **WiFi网络扫描**：自动扫描周围的WiFi网络
- 📊 **信道分析**：分析各信道的使用情况和干扰程度
- 💡 **智能推荐**：推荐最优的信道选择
- 📈 **数据导出**：支持CSV格式报告导出
- 📝 **日志记录**：自动保存扫描结果和优化建议
- 🌐 **跨平台支持**：支持Windows和macOS系统

## 快速开始

### Windows系统
双击运行 `wifi_scan.bat` 文件，或使用命令行：
```cmd
python Channel.py
```

### macOS系统
运行 `wifi_scan_macos.sh` 文件，或使用命令行：
```bash
python3 Channel.py
```

### 导出CSV报告
```bash
python Channel.py --export wifi_report.csv
```

## 文件说明

- `Channel.py` - 主程序文件
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
`WiFi名称1&WiFi名称2_YYYYMMDDwifi优化建议.json`

例如：`HomeNet&Office_20260322wifi优化建议.json`

## 系统要求

### Windows系统
- Windows 10/11
- Python 3.6+
- 管理员权限（用于WiFi扫描）

### macOS系统
- macOS 10.12+
- Python 3.6+
- 需要启用WiFi扫描权限

## 注意事项

### Windows系统
1. 需要管理员权限才能进行WiFi扫描
2. 程序会自动创建 `wifi_logs` 目录保存日志
3. 如果扫描失败，会使用演示数据进行展示

### macOS系统
1. 需要启用WiFi扫描权限（系统偏好设置 > 安全性与隐私 > 隐私 > 定位服务）
2. airport命令可能需要手动启用：`sudo ln -s /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport /usr/local/bin/airport`
3. 程序会自动创建 `wifi_logs` 目录保存日志
4. 如果扫描失败，会使用演示数据进行展示