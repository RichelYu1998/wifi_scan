#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硬件信息检测器 - 检测CPU、显卡、内存等硬件信息
"""

import platform
import psutil
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

try:
    from hardware_performance_updater import HardwarePerformanceUpdater
except ImportError:
    class HardwarePerformanceUpdater:
        def __init__(self, escape_manager=None):
            pass
        
        def get_performance_data(self):
            return {
                'cpu': {},
                'gpu': {},
                'memory': {}
            }
        
        def update_all_performance_data(self, force_update=False):
            return {
                'cpu': {'update_time': '', 'data': {}},
                'gpu': {'update_time': '', 'data': {}},
                'memory': {'update_time': '', 'data': {}},
                'update_time': ''
            }


class HardwareInfo:
    """硬件信息检测器 - 检测CPU、显卡、内存等硬件信息"""
    
    def __init__(self, escape_manager=None, cross_platform_utils=None):
        if escape_manager is None:
            escape_manager = EscapeManager()
        if cross_platform_utils is None:
            cross_platform_utils = get_cross_platform_utils()
            
        self.escape_manager = escape_manager
        self.cross_platform_utils = cross_platform_utils
        
        # 使用硬件性能数据更新器获取最新数据
        self.performance_updater = HardwarePerformanceUpdater(escape_manager)
        performance_data = self.performance_updater.get_performance_data()
        
        self.cpu_performance_map = performance_data['cpu'] if performance_data['cpu'] else {
            'i9': 100, 'i7': 85, 'i5': 70, 'i3': 55,
            'Core i9': 100, 'Core i7': 85, 'Core i5': 70, 'Core i3': 55,
            'Ryzen 9': 100, 'Ryzen 7': 85, 'Ryzen 5': 70, 'Ryzen 3': 55,
            'M3': 100, 'M2': 95, 'M1': 90, 'M1 Pro': 95, 'M1 Max': 100,
            'M2 Pro': 100, 'M2 Max': 100, 'M2 Ultra': 100,
            'M3 Pro': 100, 'M3 Max': 100, 'M3 Ultra': 100,
        }
        
        self.gpu_performance_map = performance_data['gpu'] if performance_data['gpu'] else {
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
        
        self.memory_capacity_map = performance_data['memory'] if performance_data['memory'] else {
            32: 100, 24: 95, 16: 85, 12: 75, 8: 60, 4: 40, 2: 20,
        }
    
    def get_hardware_info(self):
        """获取硬件信息（统一接口）"""
        hardware_info = {
            'cpu': self._get_cpu_info(),
            'gpu': self._get_gpu_info(),
            'memory': self._get_memory_info(),
            'system': self._get_system_info()
        }
        hardware_info['performance_score'] = self._calculate_performance_score(hardware_info)
        self.escape_manager.debug_log("硬件信息检测完成", hardware_info)
        return hardware_info
    
    def _get_cpu_info(self):
        """获取CPU信息"""
        cpu_info = {'名称': '未知', '架构': platform.machine(), '核心数': 1, '频率_MHz': 0}
        try:
            system = platform.system()
            if system == 'Darwin':
                result = self.cross_platform_utils.run_command(['sysctl', '-n', 'machdep.cpu.brand_string'])
                if result and result.strip():
                    cpu_info['名称'] = result.strip()
                else:
                    result = self.cross_platform_utils.run_command(['sysctl', '-n', 'hw.model'])
                    if result and result.strip():
                        cpu_info['名称'] = f"Apple {result.strip()}"
                
                result = self.cross_platform_utils.run_command(['sysctl', '-n', 'hw.ncpu'])
                if result and result.strip():
                    cpu_info['核心数'] = int(result.strip())
                
                result = self.cross_platform_utils.run_command(['sysctl', '-n', 'hw.cpufrequency'])
                if result and result.strip():
                    cpu_info['频率_MHz'] = int(result.strip()) // 1000000
                else:
                    # Apple Silicon默认频率
                    cpu_info['频率_MHz'] = 3200
                    
            elif system == 'Windows':
                # Windows系统使用WMIC获取CPU信息
                result = self.cross_platform_utils.run_command(['wmic', 'cpu', 'get', 'name'])
                if result:
                    lines = result.strip().split('\n')
                    if len(lines) > 1:
                        cpu_info['名称'] = lines[1].strip()
                
                cpu_info['核心数'] = psutil.cpu_count(logical=False)
                cpu_info['频率_MHz'] = int(psutil.cpu_freq().current) if psutil.cpu_freq() else 0
                
            else:  # Linux
                with open('/proc/cpuinfo', 'r') as f:
                    cpuinfo = f.read()
                    model_match = re.search(r'model name\s+:\s+(.+)', cpuinfo)
                    if model_match:
                        cpu_info['名称'] = model_match.group(1).strip()
                
                cpu_info['核心数'] = psutil.cpu_count(logical=False)
                cpu_info['频率_MHz'] = int(psutil.cpu_freq().current) if psutil.cpu_freq() else 0
                
        except Exception as e:
            self.escape_manager.debug_log(f"获取CPU信息失败: {e}")
            # 使用psutil作为备选方案
            cpu_info['核心数'] = psutil.cpu_count(logical=False) or 1
            cpu_info['频率_MHz'] = int(psutil.cpu_freq().current) if psutil.cpu_freq() else 0
        
        return cpu_info
    
    def _get_gpu_info(self):
        """获取显卡信息"""
        gpu_info = {'名称': '未知', '显存_MB': 0}
        try:
            system = platform.system()
            if system == 'Darwin':
                # macOS使用system_profiler获取显卡信息
                result = self.cross_platform_utils.run_command(['system_profiler', 'SPDisplaysDataType'])
                if result:
                    # 解析显卡信息
                    chip_match = re.search(r'Chipset Model:\s+(.+)', result)
                    if chip_match:
                        gpu_info['名称'] = chip_match.group(1).strip()
                    
                    # 解析显存
                    vram_match = re.search(r'VRAM.*?(\d+)\s*MB', result)
                    if vram_match:
                        gpu_info['显存_MB'] = int(vram_match.group(1))
                    else:
                        # Apple Silicon使用统一内存，根据总内存估算
                        mem_info = psutil.virtual_memory()
                        total_gb = mem_info.total // (1024**3)
                        gpu_info['显存_MB'] = min(total_gb * 512, 8192)  # 估算显存
                        
            elif system == 'Windows':
                # Windows使用WMIC获取显卡信息
                result = self.cross_platform_utils.run_command(['wmic', 'path', 'win32_VideoController', 'get', 'name'])
                if result:
                    lines = result.strip().split('\n')
                    if len(lines) > 1:
                        gpu_info['名称'] = lines[1].strip()
                
            else:  # Linux
                # Linux使用lspci获取显卡信息
                result = self.cross_platform_utils.run_command(['lspci'])
                if result:
                    gpu_lines = [line for line in result.split('\n') if 'VGA' in line or '3D' in line]
                    if gpu_lines:
                        gpu_info['名称'] = gpu_lines[0].split(':')[2].strip()
                        
        except Exception as e:
            self.escape_manager.debug_log(f"获取显卡信息失败: {e}")
        
        return gpu_info
    
    def _get_memory_info(self):
        """获取内存信息"""
        memory_info = {'总容量_GB': 0, '可用_GB': 0, '使用率_%': 0}
        try:
            mem = psutil.virtual_memory()
            memory_info['总容量_GB'] = round(mem.total / (1024**3), 1)
            memory_info['可用_GB'] = round(mem.available / (1024**3), 1)
            memory_info['使用率_%'] = round(mem.percent, 1)
        except Exception as e:
            self.escape_manager.debug_log(f"获取内存信息失败: {e}")
        
        return memory_info
    
    def _get_system_info(self):
        """获取系统信息"""
        system_info = {
            '操作系统': platform.system(),
            '版本': platform.release(),
            '架构': platform.machine(),
            'Python版本': platform.python_version()
        }
        return system_info
    
    def _calculate_performance_score(self, hardware_info):
        """计算硬件性能评分"""
        cpu_score = self._calculate_cpu_score(hardware_info['cpu'])
        gpu_score = self._calculate_gpu_score(hardware_info['gpu'])
        memory_score = self._calculate_memory_score(hardware_info['memory'])
        
        # 加权计算总分（CPU 40%, GPU 40%, 内存 20%）
        total_score = cpu_score * 0.4 + gpu_score * 0.4 + memory_score * 0.2
        return round(total_score, 1)
    
    def _calculate_cpu_score(self, cpu_info):
        """计算CPU性能评分"""
        cpu_name = cpu_info['名称'].lower()
        
        # 根据CPU型号名称匹配性能评分
        for model, score in self.cpu_performance_map.items():
            if model.lower() in cpu_name:
                return score
        
        # 根据核心数和频率估算评分
        base_score = min(cpu_info['核心数'] * 10, 60)  # 核心数贡献最多60分
        freq_score = min(cpu_info['频率_MHz'] / 100, 40)  # 频率贡献最多40分
        return min(base_score + freq_score, 100)
    
    def _calculate_gpu_score(self, gpu_info):
        """计算显卡性能评分"""
        gpu_name = gpu_info['名称'].lower()
        
        # 根据GPU型号名称匹配性能评分
        for model, score in self.gpu_performance_map.items():
            if model.lower() in gpu_name:
                return score
        
        # 根据显存估算评分
        vram_score = min(gpu_info['显存_MB'] / 100, 60)  # 显存贡献最多60分
        return min(vram_score + 40, 100)  # 基础分40分
    
    def _calculate_memory_score(self, memory_info):
        """计算内存性能评分"""
        total_gb = memory_info['总容量_GB']
        
        # 根据内存容量匹配性能评分
        for capacity, score in self.memory_capacity_map.items():
            if total_gb >= float(capacity):
                return score
        
        return 20  # 默认评分
    
    def update_performance_data(self, force_update=False):
        """手动更新硬件性能数据"""
        self.escape_manager.debug_log("开始手动更新硬件性能数据")
        
        # 重新获取性能数据
        performance_data = self.performance_updater.update_all_performance_data(force_update)
        
        # 更新性能映射
        if performance_data['cpu'] and performance_data['cpu']['data']:
            self.cpu_performance_map = performance_data['cpu']['data']
            self.escape_manager.debug_log(f"CPU性能数据已更新，包含 {len(self.cpu_performance_map)} 个型号")
        
        if performance_data['gpu'] and performance_data['gpu']['data']:
            self.gpu_performance_map = performance_data['gpu']['data']
            self.escape_manager.debug_log(f"GPU性能数据已更新，包含 {len(self.gpu_performance_map)} 个型号")
        
        if performance_data['memory'] and performance_data['memory']['data']:
            self.memory_capacity_map = performance_data['memory']['data']
            self.escape_manager.debug_log(f"内存性能数据已更新，包含 {len(self.memory_capacity_map)} 个规格")
        
        return performance_data


if __name__ == '__main__':
    hw = HardwareInfo()
    info = hw.get_hardware_info()
    print("硬件信息检测结果:")
    print(f"CPU: {info['cpu']['名称']}")
    print(f"显卡: {info['gpu']['名称']}")
    print(f"内存: {info['memory']['总容量_GB']}GB")
    print(f"性能评分: {info['performance_score']}")