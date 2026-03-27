# 视频分辨率推荐器 (VideoResolutionRecommender)

## 功能概述

视频分辨率推荐器是一个智能的Python模块，根据当前网络速度和硬件性能，为不同视频平台推荐最优的视频分辨率，确保流畅的观看体验。

## 主要功能

### 1. 多平台支持
- **短视频平台**: 抖音、快手等
- **游戏直播平台**: 虎牙、斗鱼等
- **长视频平台**: 优酷、腾讯视频、爱奇艺等
- **综合视频平台**: 哔哩哔哩等

### 2. 智能推荐算法
- **网络速度适配**: 根据下载速度推荐合适的分辨率
- **硬件性能考虑**: 结合硬件性能调整推荐策略
- **安全带宽预留**: 保留20%带宽应对网络波动

### 3. 分辨率级别
- **4K超清**: 3840x2160 (15-25 Mbps)
- **1080P高清**: 1920x1080 (5-8 Mbps)
- **720P标清**: 1280x720 (2.5-4 Mbps)
- **480P流畅**: 854x480 (1-2 Mbps)
- **360P省流**: 640x360 (0.5-1 Mbps)

## 使用方法

### 基本使用
```python
from video_resolution_recommender import VideoResolutionRecommender

# 创建视频分辨率推荐器实例
recommender = VideoResolutionRecommender()

# 根据网速推荐所有平台的分辨率
recommendations = recommender.recommend_resolution(download_speed_mbps=50)

# 输出推荐结果
for platform, info in recommendations.items():
    print(f"{info['平台']}: {info['推荐分辨率']} ({info['分辨率描述']})")
    print(f"  所需带宽: {info['所需带宽']} Mbps, 当前带宽: {info['当前带宽']} Mbps")
```

### 指定平台推荐
```python
# 只推荐抖音平台的分辨率
recommendations = recommender.recommend_resolution(
    download_speed_mbps=20, 
    platform_name='抖音'
)
```

### 考虑硬件性能
```python
# 结合硬件性能进行推荐
recommendations = recommender.recommend_resolution(
    download_speed_mbps=30,
    hardware_performance_score=85
)
```

### 集成到其他模块
```python
from video_resolution_recommender import VideoResolutionRecommender

# 在网络速度测试后自动推荐分辨率
tester = NetworkSpeedTester()
speed_info = tester.test_network_speed()
download_speed = speed_info['下载速度_Mbps']

recommender = VideoResolutionRecommender()
recommendations = recommender.recommend_resolution(download_speed)
```

## 输出格式

```json
{
  "抖音": {
    "平台": "抖音",
    "类型": "短视频",
    "推荐分辨率": "1080P",
    "分辨率描述": "1080P高清 (1920x1080)",
    "所需带宽": 8.0,
    "当前带宽": 50.0,
    "可用带宽": 40.0,
    "硬件性能影响": "未考虑"
  },
  "虎牙": {
    "平台": "虎牙",
    "类型": "游戏直播",
    "推荐分辨率": "4K",
    "分辨率描述": "4K超清 (3840x2160)",
    "所需带宽": 20.0,
    "当前带宽": 50.0,
    "可用带宽": 40.0,
    "硬件性能影响": "未考虑"
  }
}
```

## 平台配置

### 抖音配置
```python
'抖音': {
    'name': '抖音',
    'type': '短视频',
    'resolutions': {
        '4K': {'bitrate': 25, 'description': '4K超清 (3840x2160)'},
        '1080P': {'bitrate': 8, 'description': '1080P高清 (1920x1080)'},
        '720P': {'bitrate': 4, 'description': '720P标清 (1280x720)'},
        '480P': {'bitrate': 2, 'description': '480P流畅 (854x480)'},
        '360P': {'bitrate': 1, 'description': '360P省流 (640x360)'}
    }
}
```

### 虎牙配置
```python
'虎牙': {
    'name': '虎牙',
    'type': '游戏直播',
    'resolutions': {
        '4K': {'bitrate': 20, 'description': '4K超清 (3840x2160)'},
        '1080P': {'bitrate': 6, 'description': '1080P高清 (1920x1080)'},
        '720P': {'bitrate': 3, 'description': '720P标清 (1280x720)'},
        '480P': {'bitrate': 1.5, 'description': '480P流畅 (854x480)'},
        '360P': {'bitrate': 0.8, 'description': '360P省流 (640x360)'}
    }
}
```

## 推荐算法

### 带宽计算
```python
# 基础可用带宽
available_bandwidth = download_speed

# 硬件性能调整
if hardware_performance_score is not None:
    hardware_factor = hardware_performance_score / 100
    available_bandwidth *= (0.7 + 0.3 * hardware_factor)

# 安全带宽预留（20%）
safe_bandwidth = available_bandwidth * 0.8
```

### 分辨率选择
```python
# 找到最适合的分辨率
best_resolution = None
best_bitrate = 0

for res_name, res_info in platform['resolutions'].items():
    if res_info['bitrate'] <= safe_bandwidth and res_info['bitrate'] > best_bitrate:
        best_resolution = res_name
        best_bitrate = res_info['bitrate']

# 如果没有合适的分辨率，使用最低分辨率
if best_resolution is None:
    lowest_res = list(platform['resolutions'].keys())[-1]
    best_resolution = lowest_res
    best_bitrate = platform['resolutions'][lowest_res]['bitrate']
```

## 硬件性能影响

### 性能等级划分
| 性能评分 | 带宽调整系数 | 说明 |
|----------|--------------|------|
| 0-40 | 50% | 低性能硬件，大幅降低带宽要求 |
| 40-60 | 70% | 中等性能硬件，适度降低带宽要求 |
| 60-80 | 85% | 良好性能硬件，轻微降低带宽要求 |
| 80-100 | 100% | 高性能硬件，不降低带宽要求 |

### 实际应用
```python
# 高性能硬件可以更好地处理高分辨率视频
# 低性能硬件需要降低分辨率要求以确保流畅播放
```

## 测试场景

### 不同网速下的推荐
```python
# 测试不同网速下的推荐结果
test_speeds = [1, 5, 10, 20, 50, 100]

for speed in test_speeds:
    recommendations = recommender.recommend_resolution(speed)
    print(f"\n=== 网速 {speed} Mbps 推荐 ===")
    for platform, info in recommendations.items():
        print(f"{info['平台']}: {info['推荐分辨率']}")
```

### 硬件性能对比
```python
# 测试不同硬件性能下的推荐差异
speed = 20
performance_scores = [30, 60, 90]

for score in performance_scores:
    recommendations = recommender.recommend_resolution(speed, hardware_performance_score=score)
    print(f"\n=== 硬件性能 {score} 分推荐 ===")
    for platform, info in recommendations.items():
        print(f"{info['平台']}: {info['推荐分辨率']}")
```

## 平台特性考虑

### 短视频平台（抖音）
- **特点**: 短内容，快速加载
- **推荐策略**: 优先保证流畅性，适当提高分辨率

### 游戏直播平台（虎牙）
- **特点**: 实时性要求高，画面复杂
- **推荐策略**: 平衡画质和流畅性，考虑硬件解码能力

### 长视频平台（优酷等）
- **特点**: 内容较长，可以缓冲
- **推荐策略**: 可以适当提高分辨率要求

## 错误处理

### 参数类型处理
```python
# 支持直接传入速度值或包含速度的字典
if isinstance(download_speed_mbps, dict):
    download_speed = download_speed_mbps.get('下载速度_Mbps', 0)
else:
    download_speed = float(download_speed_mbps)
```

### 平台不存在处理
```python
platforms_to_check = [platform_name] if platform_name else self.video_platforms.keys()

for platform_key in platforms_to_check:
    if platform_key in self.video_platforms:
        # 处理存在的平台
        pass
```

## 依赖项

- 无外部依赖，纯Python实现
- 使用标准库进行数据处理

## 版本历史

- **v1.0** (2026-03-28): 初始版本，支持基本分辨率推荐
- **v1.1** (2026-03-28): 增加硬件性能考虑，优化推荐算法

## 扩展性

### 添加新平台
```python
# 在 self.video_platforms 中添加新平台配置
'新平台': {
    'name': '平台名称',
    'type': '平台类型',
    'resolutions': {
        # 分辨率配置
    }
}
```

### 自定义分辨率
```python
# 修改现有平台的分辨率配置
self.video_platforms['抖音']['resolutions']['4K']['bitrate'] = 30
```

## 作者

WiFi信道扫描工具开发团队