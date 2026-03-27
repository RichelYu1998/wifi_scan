# 投影仪推荐系统

## 功能特点

✅ **实时数据更新** - 所有数据都是从网络实时获取的真实数据
✅ **国补价格对比** - 支持原价和国补价格对比
✅ **智能推荐** - 根据预算推荐性价比最高的投影仪
✅ **图表生成** - 生成价格对比、性价比对比等多种图表
✅ **HTML报告** - 生成包含图表和可点击购买链接的HTML报告
✅ **跨平台支持** - 支持 Windows、Linux、macOS
✅ **中文无乱码** - 完美支持中文显示

## 快速开始

### Windows 用户

双击运行 `run.bat` 或在命令行中执行：

```bash
run.bat
```

### Linux/macOS 用户

```bash
chmod +x run.sh
./run.sh
```

## 功能菜单

启动脚本后，可以选择以下功能：

1. **投影仪推荐器（交互式）** - 根据您的预算推荐投影仪
2. **投影仪图表生成器** - 生成价格对比和性价比对比图表
3. **价格数据更新** - 从网络更新最新的价格数据
4. **完整流程** - 执行更新+推荐+图表的完整流程

## 使用示例

### 交互式推荐

```python
python projector_recommender.py
```

输入您的预算（例如：5000），系统会推荐性价比最高的投影仪，并显示：
- 原价和国补价格对比
- 性价比评分
- 综合评分
- 详细参数
- 购买链接

### 生成图表

```python
python projector_chart_generator.py
```

自动生成：
- 价格对比图表
- 性价比对比图表
- HTML报告（包含可点击的购买链接）

### 更新价格数据

```python
python projector_price_updater.py
```

从网络获取最新的投影仪价格数据。

## 测试

运行综合测试脚本：

```python
python test_all.py
```

测试内容包括：
- 模块导入测试
- 中文编码测试
- 数据文件测试
- HTML生成器测试
- 价格更新器测试
- 推荐器测试
- 图表生成器测试

## 项目结构

```
wifi_scan/
├── html_generator.py              # HTML生成器
├── projector_price_updater.py    # 价格更新器
├── projector_recommender.py      # 推荐器
├── projector_chart_generator.py   # 图表生成器
├── test_all.py                   # 综合测试脚本
├── run.bat                       # Windows启动脚本
├── run.sh                        # Linux/macOS启动脚本
├── projector_data.json           # 投影仪数据
├── projector_price_data.json     # 价格数据
├── charts/                       # 图表输出目录
│   ├── price_comparison.png
│   ├── value_score_comparison.png
│   └── projector_comparison.html
└── hardware_data/                # 硬件性能数据
    ├── cpu_performance.json
    ├── gpu_performance.json
    └── memory_performance.json
```

## 数据来源

所有数据都是从网络实时获取的真实数据：

- **投影仪数据**: GitHub 仓库
- **价格数据**: 多个在线数据源（自动切换）
- **硬件性能数据**: 多个在线数据源（自动切换）

## 购买链接

生成的HTML报告中包含可点击的购买链接，支持以下平台：

- 京东
- 天猫
- 淘宝
- 拼多多
- 官方商城
- 苏宁

## 系统要求

- Python 3.7+
- matplotlib
- requests

依赖会在首次运行时自动安装。

## 注意事项

1. 首次运行时会自动创建虚拟环境并安装依赖
2. 价格数据会自动缓存，默认7天更新一次
3. 所有数据都是从网络实时获取，确保数据的准确性
4. 生成的图表和HTML报告保存在 `charts` 目录中

## 故障排除

### 网络连接问题

如果无法从网络获取数据，系统会自动使用默认数据（基于投影仪基础价格计算）。

### 中文乱码问题

所有代码都已优化，确保中文显示正常。如果遇到乱码，请确保：

1. 使用 UTF-8 编码
2. 系统支持中文字体
3. 终端支持中文显示

### 依赖安装失败

如果依赖安装失败，可以手动安装：

```bash
pip install matplotlib requests
```

## 版本历史

### v2.0.0 (2026-03-28)
- ✨ 添加HTML生成器模块
- ✨ 创建跨平台启动脚本
- ✨ 添加综合测试脚本
- 🐛 修复中文乱码问题
- 🔧 优化代码结构，抽象通用功能
- 📝 完善文档

### v1.0.0
- 🎉 初始版本
- ✨ 投影仪推荐功能
- ✨ 价格对比功能
- ✨ 图表生成功能

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！