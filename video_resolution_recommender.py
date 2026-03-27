
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频分辨率推荐器 - 根据网速推荐视频平台最优分辨率
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from cross_platform_utils import CrossPlatformUtils, get_cross_platform_utils
except ImportError:
    # 如果cross_platform_utils不可用，创建简化版本
    class CrossPlatformUtils:
        def __init__(self, debug_mode=False):
            self.debug_mode = debug_mode
            import platform
            self.platform = platform.system()
        
        def run_command(self, command, timeout=10):
            import subprocess
            try:
                result = subprocess.run(
                    command, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True, 
                    encoding='utf-8',
                    errors='replace',
                    timeout=timeout
                )
                return result.stdout if result.returncode == 0 else ""
            except:
                return ""

try:
    from escape_manager import EscapeManager
except ImportError:
    class EscapeManager:
        def __init__(self):
            self.debug_mode = False
        
        def debug_log(self, message, data=None, debug=None):
            if debug is None:
                debug = self.debug_mode
            if debug and data:
                print(f"调试：{message} {data}")
            elif debug:
                print(f"调试：{message}")


class VideoResolutionRecommender:
    """视频分辨率推荐器 - 根据网速推荐视频平台最优分辨率"""
    
    def __init__(self, escape_manager=None, cross_platform_utils=None):
        if escape_manager is None:
            escape_manager = EscapeManager()
        if cross_platform_utils is None:
            cross_platform_utils = get_cross_platform_utils()
            
        self.escape_manager = escape_manager
        self.cross_platform_utils = cross_platform_utils
        
        self.video_platforms = {
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
            },
            '虎牙': {
                'name': '虎牙',
                'type': '直播平台',
                'resolutions': {
                    '4K': {'bitrate': 30, 'description': '4K超清直播 (3840x2160)'},
                    '1080P': {'bitrate': 10, 'description': '1080P高清直播 (1920x1080)'},
                    '720P': {'bitrate': 5, 'description': '720P标清直播 (1280x720)'},
                    '480P': {'bitrate': 2.5, 'description': '480P流畅直播 (854x480)'},
                    '360P': {'bitrate': 1.2, 'description': '360P省流直播 (640x360)'}
                }
            },
            '优酷': {
                'name': '优酷',
                'type': '长视频',
                'resolutions': {
                    '4K': {'bitrate': 40, 'description': '4K HDR (3840x2160)'},
                    '1080P': {'bitrate': 15, 'description': '1080P高清 (1920x1080)'},
                    '720P': {'bitrate': 6, 'description': '720P标清 (1280x720)'},
                    '480P': {'bitrate': 3, 'description': '480P流畅 (854x480)'},
                    '360P': {'bitrate': 1.5, 'description': '360P省流 (640x360)'}
                }
            },
            '腾讯视频': {
                'name': '腾讯视频',
                'type': '长视频',
                'resolutions': {
                    '4K': {'bitrate': 35, 'description': '4K超清 (3840x2160)'},
                    '1080P': {'bitrate': 12, 'description': '1080P高清 (1920x1080)'},
                    '720P': {'bitrate': 5, 'description': '720P标清 (1280x720)'},
                    '480P': {'bitrate': 2.5, 'description': '480P流畅 (854x480)'},
                    '360P': {'bitrate': 1.5, 'description': '360P省流 (640x360)'}
                }
            },
            '爱奇艺': {
                'name': '爱奇艺',
                'type': '长视频',
                'resolutions': {
                    '4K': {'bitrate': 35, 'description': '4K超清 (3840x2160)'},
                    '1080P': {'bitrate': 12, 'description': '1080P高清 (1920x1080)'},
                    '720P': {'bitrate': 5, 'description': '720P标清 (1280x720)'},
                    '480P': {'bitrate': 2.5, 'description': '480P流畅 (854x480)'},
                    '360P': {'bitrate': 1.5, 'description': '360P省流 (640x360)'}
                }
            }
        }
    
    def recommend_resolution(self, speed_info, platform_name=None, hardware_performance_score=None):
        """根据网速推荐视频分辨率
        
        Args:
            speed_info: 下载速度（Mbps）或包含下载速度的字典
            platform_name: 平台名称，如果为None则推荐所有平台
            hardware_performance_score: 硬件性能评分（0-100），用于调整推荐
            
        Returns:
            推荐的分辨率信息
        """
        recommendations = {}
        
        # 处理参数类型：支持直接传入速度值或包含速度的字典
        if isinstance(speed_info, dict):
            # 如果传入的是字典，提取下载速度
            download_speed = speed_info.get('下载速度_Mbps', 0)
        else:
            # 如果传入的是数字，直接使用
            download_speed = float(speed_info)
        
        # 根据硬件性能调整可用带宽
        available_bandwidth = download_speed
        if hardware_performance_score is not None:
            # 硬件性能影响：高性能硬件可以更好地处理高分辨率视频
            hardware_factor = hardware_performance_score / 100
            available_bandwidth *= (0.7 + 0.3 * hardware_factor)  # 基础70% + 硬件影响30%
        
        # 安全系数：保留20%带宽用于网络波动
        safe_bandwidth = available_bandwidth * 0.8
        
        platforms_to_check = [platform_name] if platform_name else self.video_platforms.keys()
        
        for platform_key in platforms_to_check:
            if platform_key in self.video_platforms:
                platform = self.video_platforms[platform_key]
                best_resolution = None
                best_bitrate = 0
                
                # 找到最适合的分辨率
                for res_name, res_info in platform['resolutions'].items():
                    if res_info['bitrate'] <= safe_bandwidth and res_info['bitrate'] > best_bitrate:
                        best_resolution = res_name
                        best_bitrate = res_info['bitrate']
                
                # 如果没有找到合适的分辨率，使用最低分辨率
                if best_resolution is None:
                    lowest_res = list(platform['resolutions'].keys())[-1]
                    best_resolution = lowest_res
                    best_bitrate = platform['resolutions'][lowest_res]['bitrate']
                
                recommendations[platform_key] = {
                    '平台': platform['name'],
                    '类型': platform['type'],
                    '推荐分辨率': best_resolution,
                    '分辨率描述': platform['resolutions'][best_resolution]['description'],
                    '所需带宽': platform['resolutions'][best_resolution]['bitrate'],
                    '当前带宽': download_speed,
                    '可用带宽': round(safe_bandwidth, 1),
                    '硬件性能影响': hardware_performance_score if hardware_performance_score else '未考虑'
                }
        
        return recommendations
    
    def _recommend_for_platform(self, platform_name, platform_config, download_speed):
        """为单个平台推荐分辨率"""
        if download_speed <= 0:
            return {
                'platform': platform_name,
                'type': platform_config['type'],
                'recommended': '360P',
                'bitrate': platform_config['resolutions']['360P']['bitrate'],
                'description': platform_config['resolutions']['360P']['description']
            }
        
        resolution_order = ['4K', '1080P', '720P', '480P', '360P']
        
        for resolution in resolution_order:
            required_bitrate = platform_config['resolutions'][resolution]['bitrate']
            if download_speed >= required_bitrate:
                return {
                    'platform': platform_name,
                    'type': platform_config['type'],
                    'recommended': resolution,
                    'bitrate': required_bitrate,
                    'description': platform_config['resolutions'][resolution]['description']
                }
        
        return {
            'platform': platform_name,
            'type': platform_config['type'],
            'recommended': '360P',
            'bitrate': platform_config['resolutions']['360P']['bitrate'],
            'description': platform_config['resolutions']['360P']['description']
        }
    
    def recommend_resolution_with_hardware(self, speed_info, hardware_info):
        """根据网速和硬件信息综合推荐各平台最优分辨率"""
        if not speed_info or '下载速度_Mbps' not in speed_info:
            return self.recommend_resolution(speed_info)
        
        if not hardware_info or 'performance_score' not in hardware_info:
            return self.recommend_resolution(speed_info)
        
        download_speed = speed_info.get('下载速度_Mbps', 0)
        performance_score = hardware_info.get('performance_score', 50)
        
        adjusted_speed = download_speed
        
        if performance_score < 40:
            adjusted_speed = download_speed * 0.5
        elif performance_score < 60:
            adjusted_speed = download_speed * 0.7
        elif performance_score < 80:
            adjusted_speed = download_speed * 0.85
        
        adjusted_speed_info = speed_info.copy()
        adjusted_speed_info['下载速度_Mbps'] = adjusted_speed
        
        recommendations = self.recommend_resolution(adjusted_speed_info)
        
        for platform_name in recommendations:
            recommendations[platform_name]['performance_score'] = performance_score
            recommendations[platform_name]['adjusted_speed'] = round(adjusted_speed, 2)
            recommendations[platform_name]['original_speed'] = download_speed
        
        return recommendations


if __name__ == '__main__':
    recommender = VideoResolutionRecommender()
    
    speed_info = {
        '下载速度_Mbps': 50,
        '上传速度_Mbps': 10,
        '延迟_ms': 20,
        '测试模式': '系统命令'
    }
    
    recommendations = recommender.recommend_resolution(speed_info)
    print("视频分辨率推荐结果:")
    for platform_name, rec in recommendations.items():
        if '推荐分辨率' in rec:
            print(f"{platform_name}: {rec['推荐分辨率']} - {rec['分辨率描述']}")
        else:
            print(f"{platform_name}: {rec['recommended']} - {rec['description']}")