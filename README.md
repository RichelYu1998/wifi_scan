# WiFi扫描与投影仪推荐系统

## 🚀 快速启动

### Windows用户

**推荐方式**（自动检测虚拟环境）：
```bash
start.bat
```

**PowerShell方式**（需要绕过执行策略）：
```bash
start_pwsh.bat
```

**直接运行Python**：
```bash
python run.py
```

### Linux/macOS用户

```bash
./start.sh
```

**或者直接运行**：
```bash
python3 run.py
```

## 📋 功能说明

### 1. WiFi扫描工具
- 扫描周围WiFi网络
- 显示网络详细信息（信号强度、加密方式、频道等）

### 2. 硬件信息检测
- 检测CPU、GPU、内存、硬盘等硬件信息
- 显示BIOS版本和主板信息
- 计算硬件性能评分

### 3. 投影仪推荐器（交互式）
- 根据预算推荐性价比最高的投影仪
- 支持国补价格对比
- 输入示例：`3000`（预算）或 `爱普生`（品牌）

### 4. 投影仪图表生成器
- 生成价格对比图表
- 生成分价比对比图表
- 自动生成包含购买链接的HTML报告

### 5. 价格数据更新
- 从网络更新最新的投影仪价格数据
- 支持国补价格计算

### 6. 运行所有测试
- 运行全面测试，确保所有功能正常
- 验证中文显示无乱码

### 7. 视频分辨率推荐
- 根据屏幕尺寸和观看距离推荐最佳分辨率

### 8. 网络速度测试
- 测试网络上传和下载速度

## 🔧 系统要求

- Python 3.7+
- Windows 10/11 或 Linux/macOS
- 虚拟环境（可选但推荐）

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
pip install -r requirements.txt
```

## 🎯 启动脚本说明

### start.bat（Windows推荐）
- 自动检测虚拟环境（`.venv` → `venv` → `env`）
- 优先使用虚拟环境中的Python
- 设置UTF-8编码确保中文正常显示
- 错误处理和暂停显示

### start.ps1（PowerShell）
- PowerShell原生脚本
- 彩色输出支持
- 更好的错误处理
- 需要绕过执行策略（通过start_pwsh.bat调用）

### start_pwsh.bat（PowerShell包装器）
- 解决PowerShell执行策略限制
- 自动调用start.ps1
- 绕过ExecutionPolicy限制

### run.py（Python启动器）
- 跨平台支持
- 自动检测虚拟环境
- 统一的启动接口

## 📊 项目结构

```
wifi_scan/
├── common_imports.py          # 统一跨平台导入
├── config_manager.py          # 配置管理器
├── data_updater.py           # 数据更新器
├── data_manager.py           # 数据管理基类
├── run.py                  # Python启动器
├── start.bat               # Windows启动脚本
├── start.ps1              # PowerShell启动脚本
├── start_pwsh.bat         # PowerShell包装器
├── wifi_scan.py           # WiFi扫描工具
├── hardware_info.py       # 硬件信息检测
├── projector_recommender.py  # 投影仪推荐器
├── projector_price_updater.py  # 价格更新器
├── projector_chart_generator.py  # 图表生成器
├── test_all.py           # 全面测试脚本
└── ...其他功能模块
```

## 🐛 故障排除

### PowerShell执行策略错误
**问题**：无法运行PowerShell脚本
**解决**：使用`start_pwsh.bat`或直接使用`start.bat`

### 中文显示乱码
**问题**：中文显示为乱码
**解决**：确保使用`start.bat`或`start_pwsh.bat`，它们会设置UTF-8编码

### 虚拟环境未检测到
**问题**：未使用虚拟环境中的Python
**解决**：确保虚拟环境目录名为`.venv`、`venv`或`env`

### 依赖缺失
**问题**：ImportError或ModuleNotFoundError
**解决**：运行`pip install -r requirements.txt`安装依赖

## ✅ 测试

运行全面测试：
```bash
python test_all.py
```

或者在启动器中选择"运行所有测试"选项。

## 📝 版本信息

- 版本：v2.3.0
- 更新日期：2026-03-28
- 支持平台：Windows、Linux、macOS

## 💡 使用提示

1. **推荐使用虚拟环境**：避免依赖冲突，保持环境干净
2. **使用start.bat启动**：自动检测虚拟环境，设置正确的编码
3. **定期更新数据**：使用"价格数据更新"功能获取最新价格
4. **运行测试**：遇到问题时先运行测试检查系统状态

## 📞 技术支持

如遇问题，请：
1. 运行`test_all.py`检查系统状态
2. 查看错误信息
3. 确认Python版本和依赖安装情况

---

**享受使用WiFi扫描与投影仪推荐系统！** 🎉