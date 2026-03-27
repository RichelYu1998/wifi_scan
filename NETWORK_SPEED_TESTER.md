# 网络速度测试器 (NetworkSpeedTester)

## 功能概述

网络速度测试器是一个跨平台的Python模块，用于测试当前网络连接的速度，包括下载速度、上传速度、延迟和抖动等关键指标。

## 主要功能

### 1. 双模式测速
- **系统命令模式**: 使用系统内置命令获取网络接口速度
- **下载文件模式**: 通过下载测试文件计算实际网络速度

### 2. 速度指标检测
- **下载速度**: 网络下载带宽（Mbps）
- **上传速度**: 网络上传带宽（Mbps）
- **延迟**: 网络响应时间（毫秒）
- **抖动**: 网络稳定性指标（毫秒）

### 3. 跨平台支持
- **macOS**: 使用 `networkQuality` 命令
- **Windows**: 使用 `netsh` 命令
- **Linux**: 使用 `iwconfig` 命令

## 使用方法

### 基本使用
```python
from network_speed_tester import NetworkSpeedTester

# 创建网络速度测试器实例
tester = NetworkSpeedTester()

# 使用系统命令模式测试网络速度
speed_info = tester.test_network_speed(use_system_command=True)

# 输出测试结果
print(f"下载速度: {speed_info['下载速度_Mbps']} Mbps")
print(f"上传速度: {speed_info['上传速度_Mbps']} Mbps")
print(f"延迟: {speed_info['延迟_ms']} ms")
print(f"抖动: {speed_info['抖动_ms']} ms")
```

### 下载文件模式
```python
# 使用下载文件模式测试网络速度
speed_info = tester.test_network_speed(use_system_command=False)
```

### 集成到其他模块
```python
from network_speed_tester import NetworkSpeedTester

# 在视频分辨率推荐中使用网络速度
tester = NetworkSpeedTester()
speed_info = tester.test_network_speed()
download_speed = speed_info['下载速度_Mbps']

# 根据网络速度推荐视频分辨率
# ...
```

## 输出格式

```json
{
  "下载速度_Mbps": 85.5,
  "上传速度_Mbps": 42.8,
  "延迟_ms": 15.2,
  "抖动_ms": 2.1,
  "测试时间": "2026-03-28 14:30:25",
  "测试方法": "系统命令"
}
```

## 测速服务器

### 默认测试服务器
- `http://speedtest.ustc.edu.cn/download/100MB.dat`
- `http://speedtest.ustc.edu.cn/download/10MB.dat`
- `http://speedtest.ustc.edu.cn/download/1MB.dat`
- `http://speedtest.tele2.net/1MB.zip`
- `http://mirror.internode.on.net/pub/test/10MB.test`

### 服务器选择策略
- **延迟测试**: 使用前2个服务器
- **下载测试**: 使用前3个服务器
- **自动回退**: 如果某个服务器不可用，自动切换到下一个

## 跨平台实现

### macOS 实现
```python
# 使用 networkQuality 命令
result = self.cross_platform_utils.run_command(['networkQuality'])
# 解析输出获取速度信息
```

### Windows 实现
```python
# 使用 netsh 命令获取网络接口信息
result = self.cross_platform_utils.run_command(['netsh', 'interface', 'show', 'interface'])
# 查找WiFi接口并获取统计信息
```

### Linux 实现
```python
# 使用 iwconfig 命令获取无线网络信息
result = self.cross_platform_utils.run_command(['iwconfig'])
# 解析信号强度信息
```

## 下载测速算法

### 进度显示
```python
# 实时显示下载进度和速度
progress = downloaded / file_size * 100
speed_mbps = (downloaded * 8) / (elapsed_time * 1000000)
print(f"\r下载测试中: {progress:.1f}% - 速度: {speed_mbps:.1f} Mbps", end="")
```

### 速度计算
```python
# 计算平均下载速度
total_time = end_time - start_time
speed_mbps = (file_size * 8) / (total_time * 1000000)
```

### 上传速度估算
```python
# 基于下载速度估算上传速度（通常为1/2到1/3）
upload_speed = download_speed / 2
```

## 错误处理

### 系统命令失败处理
```python
try:
    # 尝试系统命令测速
    speed_info = self._test_speed_with_system_command()
except Exception as e:
    # 回退到下载测速
    speed_info = self._test_speed_with_download()
```

### 服务器不可用处理
```python
for server in self.test_servers[:3]:
    try:
        # 尝试连接服务器
        # ...
    except Exception as e:
        # 记录错误并尝试下一个服务器
        self.escape_manager.debug_log(f"下载测速失败 {server}: {e}")
        continue
```

## 性能优化

### 超时设置
- **系统命令**: 10秒超时
- **下载测试**: 10秒超时
- **延迟测试**: 5秒超时

### 内存优化
- 使用流式下载，避免大文件内存占用
- 分块读取，实时计算速度

## 测试场景

### 快速测试
```python
# 使用系统命令快速测试
speed_info = tester.test_network_speed(use_system_command=True)
```

### 精确测试
```python
# 使用下载文件模式进行精确测试
speed_info = tester.test_network_speed(use_system_command=False)
```

### 自动模式
```python
# 自动选择最佳测试模式
speed_info = tester.test_network_speed()
```

## 依赖项

- `datetime`: 时间处理
- `time`: 时间计算
- `urllib.request`: HTTP请求
- `statistics`: 统计计算
- `platform`: 平台检测

## 版本历史

- **v1.0** (2026-03-28): 初始版本，支持基本网络速度测试
- **v1.1** (2026-03-28): 增加跨平台工具类集成，优化错误处理

## 注意事项

1. **权限要求**: 某些系统命令可能需要管理员权限
2. **网络稳定性**: 测试结果受网络波动影响
3. **服务器可用性**: 依赖测试服务器的稳定性
4. **带宽占用**: 下载测试会消耗网络带宽

## 作者

WiFi信道扫描工具开发团队