# WiFi扫描与投影仪推荐系统

## 🎯 项目简介

这是一个功能强大的跨平台工具集，包含WiFi扫描、硬件信息检测、投影仪推荐等功能。所有代码都经过全面测试，确保中文显示正常，无乱码问题。

## ✨ 主要功能

### 1. WiFi扫描工具
- 扫描周围WiFi网络
- 显示网络详细信息
- 检测网络卡信息
- 中文显示无乱码

### 2. 硬件信息检测
- CPU信息检测
- GPU信息检测
- 内存信息检测
- 硬盘信息检测
- 网卡信息检测

### 3. 投影仪推荐系统
- 根据预算推荐投影仪
- 国补价格对比
- 性价比评分
- 综合评分
- 购买链接

### 4. 图表生成
- 价格对比图表
- 性价比对比图表
- 预算对比图表
- HTML报告生成
- 可点击购买链接

### 5. 其他功能
- 视频分辨率推荐
- 网络速度测试
- 价格历史追踪
- 硬件性能数据更新

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

## 📋 功能菜单

启动后可以选择以下功能：

1. **WiFi扫描工具** - 扫描WiFi网络
2. **硬件信息检测** - 检测硬件信息
3. **投影仪推荐器（交互式）** - 根据预算推荐投影仪
4. **投影仪图表生成器** - 生成价格对比图表
5. **价格数据更新** - 更新投影仪价格数据
6. **快速启动（完整流程）** - 一键执行完整流程
7. **运行所有测试** - 运行全面测试
8. **视频分辨率推荐** - 推荐视频分辨率
9. **网络速度测试** - 测试网络速度
0. **退出** - 退出程序

## 📊 测试结果

### 全面测试结果

```
======================================================================
  测试结果汇总
======================================================================
  编码测试                 ✅ 通过
  模块导入                 ✅ 通过
  数据文件                 ✅ 通过
  HTML生成器              ✅ 通过
  价格更新器                ✅ 通过
  推荐器                  ✅ 通过
  图表生成器                ✅ 通过
  WiFi扫描               ✅ 通过
  硬件信息                 ✅ 通过
  跨平台兼容性               ✅ 通过

======================================================================
  测试结论
======================================================================
  ✅ 所有测试通过！
  ✅ 代码运行正常
  ✅ 中文显示无乱码
  ✅ 跨平台兼容
```

### 中文编码测试

所有中文字符串都正常显示：

- ✅ 投影仪、价格、性价比、推荐
- ✅ 购买链接、京东、天猫、淘宝
- ✅ 拼多多、官方商城
- ✅ WiFi扫描、硬件信息、网络速度
- ✅ 视频分辨率、更新时间、数据来源

## 📁 项目结构

```
wifi_scan/
├── 启动脚本
│   ├── launcher.py                    # 统一启动器
│   ├── start.bat                      # Windows启动脚本
│   └── start.sh                       # Linux/macOS启动脚本
│
├── 核心模块
│   ├── html_generator.py              # HTML生成器
│   ├── projector_price_updater.py     # 价格更新器
│   ├── projector_recommender.py       # 推荐器
│   ├── projector_chart_generator.py    # 图表生成器
│   ├── wifi_scan.py                  # WiFi扫描
│   ├── hardware_info.py              # 硬件信息
│   ├── network_speed_tester.py       # 网络速度测试
│   ├── video_resolution_recommender.py # 视频分辨率推荐
│   ├── hardware_performance_updater.py # 硬件性能更新
│   ├── enhanced_projector_recommender.py # 增强推荐器
│   ├── projector_price_history.py    # 价格历史
│   └── cross_platform_utils.py      # 跨平台工具
│
├── 工具脚本
│   ├── quick_start.py                # 快速启动脚本
│   ├── test_all.py                   # 基础测试脚本
│   └── test_comprehensive.py         # 全面测试脚本
│
├── 配置文件
│   ├── requirements.txt               # Python依赖
│   ├── projector_data.json           # 投影仪数据
│   ├── projector_price_data.json     # 价格数据
│   └── hardware_data/                # 硬件性能数据
│       ├── cpu_performance.json
│       ├── gpu_performance.json
│       └── memory_performance.json
│
├── 输出目录
│   └── charts/                       # 图表输出目录
│       ├── price_comparison.png
│       ├── value_score_comparison.png
│       ├── projector_comparison.html
│       └── test_comprehensive.html
│
└── 文档
    ├── README.md                      # 本文档
    ├── PROJECTOR_README.md            # 投影仪系统文档
    ├── OPTIMIZATION_SUMMARY.md        # 优化总结
    ├── PROJECT_COMPLETION_SUMMARY.md  # 项目完成总结
    └── CROSS_PLATFORM_SUMMARY.md     # 跨平台脚本总结
```

## 🔧 系统要求

### 最低要求
- Python 3.7+
- Windows 10+ / Linux / macOS 10.15+
- 网络连接（用于更新数据）

### 推荐配置
- Python 3.8+
- 4GB+ 内存
- 稳定的网络连接

## 📦 依赖管理

### requirements.txt
```
matplotlib>=3.5.0
requests>=2.28.0
```

所有依赖都会在首次运行时自动安装。

## 🌐 跨平台支持

### 支持的系统
- ✅ Windows 10/11
- ✅ Linux (Ubuntu, Debian, CentOS, Fedora, etc.)
- ✅ macOS 10.15+

### 跨平台特性
- 自动检测操作系统
- 自动选择Python解释器
- 自动处理路径分隔符
- 自动处理编码问题

## 🧪 测试

### 运行测试

#### 全面测试
```bash
python test_comprehensive.py
```

#### 基础测试
```bash
python test_all.py
```

### 测试覆盖
- ✅ 编码测试
- ✅ 模块导入测试
- ✅ 数据文件测试
- ✅ HTML生成器测试
- ✅ 价格更新器测试
- ✅ 推荐器测试
- ✅ 图表生成器测试
- ✅ WiFi扫描测试
- ✅ 硬件信息测试
- ✅ 跨平台兼容性测试

## 💡 使用技巧

### 投影仪推荐
1. 运行启动脚本
2. 选择"投影仪推荐器（交互式）"
3. 输入您的预算
4. 选择是否使用国补价格
5. 查看推荐结果

### 生成图表
1. 运行启动脚本
2. 选择"投影仪图表生成器"
3. 等待图表生成完成
4. 打开 `charts/projector_comparison.html` 查看结果

### WiFi扫描
1. 运行启动脚本
2. 选择"WiFi扫描工具"
3. 查看扫描结果

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

## 📚 详细文档

- `PROJECTOR_README.md` - 投影仪推荐系统详细文档
- `OPTIMIZATION_SUMMARY.md` - 代码优化总结
- `PROJECT_COMPLETION_SUMMARY.md` - 项目完成总结
- `CROSS_PLATFORM_SUMMARY.md` - 跨平台脚本总结

## 🎉 特点

### 核心特点
- ✅ 跨平台支持（Windows/Linux/macOS）
- ✅ 中文完全支持，无乱码
- ✅ 实时数据更新
- ✅ 自动化测试
- ✅ 简单易用的界面
- ✅ 完整的文档

### 技术特点
- ✅ 模块化设计
- ✅ 代码复用
- ✅ 错误处理
- ✅ 日志记录
- ✅ 配置管理

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如果遇到问题，请：
1. 查看文档
2. 运行测试脚本
3. 提交 Issue

---

**项目状态**: ✅ 完成
**测试状态**: ✅ 所有测试通过
**跨平台**: ✅ 支持 Windows/Linux/macOS
**中文支持**: ✅ 完全支持，无乱码