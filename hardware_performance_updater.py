#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硬件性能数据更新器 - 从网络获取最新硬件性能数据
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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


class HardwarePerformanceUpdater:
    """硬件性能数据更新器"""
    
    def __init__(self, escape_manager=None):
        self.escape_manager = escape_manager or EscapeManager()
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hardware_data')
        self.update_interval_days = 30
        
        self.data_config = {
            'cpu': {
                'file': 'cpu_performance.json',
                'sources': [
                    'https://raw.githubusercontent.com/RichelYu1998/wifi_scan/main/hardware_data/cpu_performance.json',
                    'https://cdn.jsdelivr.net/gh/RichelYu1998/wifi_scan@main/hardware_data/cpu_performance.json',
                ],
                'default_data': {
                    'i9': 100, 'i7': 85, 'i5': 70, 'i3': 55,
                    'Core i9': 100, 'Core i7': 85, 'Core i5': 70, 'Core i3': 55,
                    'Ryzen 9': 100, 'Ryzen 7': 85, 'Ryzen 5': 70, 'Ryzen 3': 55,
                    'M3': 100, 'M2': 95, 'M1': 90, 'M1 Pro': 95, 'M1 Max': 100,
                    'M2 Pro': 100, 'M2 Max': 100, 'M2 Ultra': 100,
                    'M3 Pro': 100, 'M3 Max': 100, 'M3 Ultra': 100,
                }
            },
            'gpu': {
                'file': 'gpu_performance.json',
                'sources': [
                    'https://raw.githubusercontent.com/RichelYu1998/wifi_scan/main/hardware_data/gpu_performance.json',
                    'https://cdn.jsdelivr.net/gh/RichelYu1998/wifi_scan@main/hardware_data/gpu_performance.json',
                ],
                'default_data': {
                    'RTX 4090': 100, 'RTX 4080': 95, 'RTX 4070': 90,
                    'RTX 3090': 95, 'RTX 3080': 90, 'RTX 3070': 85,
                    'RTX 4060': 80, 'RTX 3060': 75,
                    'GTX 1660': 70, 'GTX 1650': 65,
                    'RX 7900': 100, 'RX 7800': 95, 'RX 7700': 90,
                    'RX 6900': 95, 'RX 6800': 90, 'RX 6700': 85,
                    'Arc A770': 80, 'Arc A750': 75,
                    'Apple M3': 100, 'Apple M2': 95, 'Apple M1': 90,
                    'Apple M2 Pro': 100, 'Apple M3 Pro': 100,
                }
            },
            'memory': {
                'file': 'memory_performance.json',
                'sources': [
                    'https://raw.githubusercontent.com/RichelYu1998/wifi_scan/main/hardware_data/memory_performance.json',
                    'https://cdn.jsdelivr.net/gh/RichelYu1998/wifi_scan@main/hardware_data/memory_performance.json',
                ],
                'default_data': {
                    32: 100, 24: 95, 16: 85, 12: 75, 8: 60, 4: 40, 2: 20,
                }
            }
        }
        
        self._ensure_data_dir()
    
    def _get_file_path(self, data_type):
        """获取数据文件路径"""
        return os.path.join(self.data_dir, self.data_config[data_type]['file'])
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            self.escape_manager.debug_log("创建硬件数据目录", self.data_dir)
    
    def _is_data_expired(self, file_path):
        """检查数据是否过期"""
        if not os.path.exists(file_path):
            return True
        
        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        expiry_time = datetime.now() - timedelta(days=self.update_interval_days)
        
        return file_time < expiry_time
    
    def _download_json(self, url, timeout=10):
        """从URL下载JSON数据"""
        try:
            request = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            with urllib.request.urlopen(request, timeout=timeout) as response:
                if response.status == 200:
                    return json.loads(response.read().decode('utf-8'))
                else:
                    self.escape_manager.debug_log(f"下载失败，状态码: {response.status}")
                    return None
                    
        except urllib.error.URLError as e:
            self.escape_manager.debug_log(f"网络错误: {e}")
            return None
        except json.JSONDecodeError as e:
            self.escape_manager.debug_log(f"JSON解析错误: {e}")
            return None
        except Exception as e:
            self.escape_manager.debug_log(f"未知错误: {e}")
            return None
    
    def _download_from_multiple_sources(self, data_type, timeout=10):
        """从多个数据源尝试下载数据"""
        urls = self.data_config[data_type]['sources']
        
        for i, url in enumerate(urls):
            self.escape_manager.debug_log(f"尝试从数据源 {i+1}/{len(urls)} 下载数据: {url}")
            data = self._download_json(url, timeout)
            
            if data and 'data' in data:
                self.escape_manager.debug_log(f"✅ 成功从数据源 {i+1} 下载 {data_type} 数据")
                data['source'] = url
                return data
        
        self.escape_manager.debug_log(f"❌ 所有数据源都无法下载 {data_type} 数据")
        return None
    
    def _save_json(self, file_path, data):
        """保存JSON数据到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.escape_manager.debug_log(f"数据已保存到: {file_path}")
            return True
        except Exception as e:
            self.escape_manager.debug_log(f"保存数据失败: {e}")
            return False
    
    def _load_json(self, file_path):
        """从文件加载JSON数据"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            self.escape_manager.debug_log(f"加载数据失败: {e}")
            return None
    
    def _create_default_data(self, data_type):
        """创建默认数据"""
        return {
            'update_time': datetime.now().isoformat(),
            'source': 'default',
            'data': self.data_config[data_type]['default_data']
        }
    
    def _update_performance_data(self, data_type, force_update=False):
        """通用性能数据更新方法"""
        file_path = self._get_file_path(data_type)
        
        if not force_update and not self._is_data_expired(file_path):
            self.escape_manager.debug_log(f"{data_type.upper()}性能数据未过期，跳过更新")
            return self._load_json(file_path)
        
        self.escape_manager.debug_log(f"开始更新{data_type.upper()}性能数据")
        
        network_data = self._download_from_multiple_sources(data_type)
        
        if network_data and network_data.get('data'):
            network_data['update_time'] = datetime.now().isoformat()
            self._save_json(file_path, network_data)
            self.escape_manager.debug_log(f"✅ {data_type.upper()}性能数据已从网络更新")
            return network_data
        
        self.escape_manager.debug_log(f"⚠️ 网络获取失败，使用默认{data_type.upper()}性能数据")
        default_data = self._create_default_data(data_type)
        self._save_json(file_path, default_data)
        return default_data
    
    def update_cpu_performance(self, force_update=False):
        """更新CPU性能数据"""
        return self._update_performance_data('cpu', force_update)
    
    def update_gpu_performance(self, force_update=False):
        """更新GPU性能数据"""
        return self._update_performance_data('gpu', force_update)
    
    def update_memory_performance(self, force_update=False):
        """更新内存性能数据"""
        return self._update_performance_data('memory', force_update)
    
    def update_all_performance_data(self, force_update=False):
        """更新所有硬件性能数据"""
        self.escape_manager.debug_log("开始更新所有硬件性能数据")
        
        result = {
            data_type: self._update_performance_data(data_type, force_update)
            for data_type in self.data_config.keys()
        }
        result['update_time'] = datetime.now().isoformat()
        
        self.escape_manager.debug_log("所有硬件性能数据更新完成", result)
        return result
    
    def get_performance_data(self):
        """获取硬件性能数据"""
        return {
            data_type: self._load_json(self._get_file_path(data_type))['data']
            if self._load_json(self._get_file_path(data_type))
            else self._update_performance_data(data_type, force_update=True)['data']
            for data_type in self.data_config.keys()
        }


if __name__ == '__main__':
    updater = HardwarePerformanceUpdater()
    
    print("=== 硬件性能数据更新器 ===")
    print()
    
    result = updater.update_all_performance_data(force_update=True)
    
    print("✅ 硬件性能数据更新完成！")
    print()
    print("数据文件位置：")
    for data_type in ['cpu', 'gpu', 'memory']:
        print(f"  {data_type.upper()}数据: {updater._get_file_path(data_type)}")
    print()
    
    print("更新时间：")
    for data_type in ['cpu', 'gpu', 'memory']:
        print(f"  {data_type.upper()}: {result[data_type]['update_time']}")
    print()
    
    print("数据统计：")
    for data_type in ['cpu', 'gpu', 'memory']:
        print(f"  {data_type.upper()}型号数量: {len(result[data_type]['data'])}")