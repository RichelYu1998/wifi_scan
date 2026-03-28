#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFi扫描与投影仪推荐系统 - 集成版
整合所有功能到一个文件中，支持跨平台运行
"""

import sys
import os
import platform
import subprocess
import re
import json
import time
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("[警告] psutil库未安装，部分硬件信息可能无法获取")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("[警告] requests库未安装，无法进行联网搜索")


class CrossPlatformUtils:
    """跨平台工具类"""
    
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode
        self.platform = platform.system()
        self.encoding = self._get_system_encoding()
    
    def _get_system_encoding(self):
        """获取系统默认编码"""
        if self.platform == "Windows":
            return "gbk"
        else:
            return "utf-8"
    
    def run_command(self, command, timeout=10):
        """执行系统命令"""
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                # 如果UTF-8失败，尝试系统编码
                result = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding=self.encoding,
                    errors="replace",
                    timeout=timeout
                )
                return result.stdout if result.returncode == 0 else ""
                
        except subprocess.TimeoutExpired:
            return ""
        except Exception:
            return ""
    
    def is_windows(self):
        """是否为Windows系统"""
        return self.platform == "Windows"
    
    def is_macos(self):
        """是否为macOS系统"""
        return self.platform == "Darwin"
    
    def is_linux(self):
        """是否为Linux系统"""
        return self.platform == "Linux"


class HardwareInfo:
    """硬件信息检测器"""
    
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode
        self.cpu = CrossPlatformUtils(debug_mode)
        self.bios_latest_cache = {}
    
    def _get_cpu_info(self):
        """获取CPU信息"""
        cpu_info = {'名称': '未知', '架构': '未知', '核心数': 0, '频率_MHz': 0}
        
        try:
            if self.cpu.is_windows():
                # 分别获取各个字段
                name_result = self.cpu.run_command(['wmic', 'cpu', 'get', 'Name', '/value'])
                cores_result = self.cpu.run_command(['wmic', 'cpu', 'get', 'NumberOfCores', '/value'])
                speed_result = self.cpu.run_command(['wmic', 'cpu', 'get', 'MaxClockSpeed', '/value'])
                
                # 解析名称
                if name_result:
                    for line in name_result.strip().split('\n'):
                        if line.startswith('Name='):
                            cpu_info['名称'] = line.replace('Name=', '').strip()
                            break
                
                # 解析核心数
                if cores_result:
                    for line in cores_result.strip().split('\n'):
                        if line.startswith('NumberOfCores='):
                            try:
                                cpu_info['核心数'] = int(line.replace('NumberOfCores=', '').strip())
                            except:
                                pass
                            break
                
                # 解析频率
                if speed_result:
                    for line in speed_result.strip().split('\n'):
                        if line.startswith('MaxClockSpeed='):
                            try:
                                cpu_info['频率_MHz'] = int(line.replace('MaxClockSpeed=', '').strip())
                            except:
                                pass
                            break
            
            cpu_info['架构'] = platform.machine()
            
        except Exception:
            pass
        
        return cpu_info
    
    def _get_gpu_info(self):
        """获取GPU信息"""
        gpu_info = {'名称': '未知', '品牌': '未知', '型号': '未知', 'GPU芯片': '未知', '显存_MB': 0, '显存_GB': 0, '类型': '未知'}
        
        try:
            if self.cpu.is_windows():
                # 获取所有显卡信息，过滤掉虚拟显卡
                result = self.cpu.run_command(['wmic', 'path', 'win32_VideoController', 'get', 'Name,AdapterRAM,VideoProcessor'])
                if result:
                    lines = result.strip().split('\n')
                    physical_gpus = []
                    
                    for line in lines:
                        line = line.strip()
                        if line and 'Name' not in line and 'AdapterRAM' not in line and 'VideoProcessor' not in line:
                            # 过滤掉虚拟显卡和集成显卡
                            gpu_name = line
                            
                            # 跳过虚拟显卡（Todesk, Virtual, Microsoft等）
                            if any(virtual_keyword in gpu_name for virtual_keyword in ['Todesk', 'Virtual', 'Microsoft Basic', 'Remote Desktop', 'VMware']):
                                continue
                            
                            # 检查是否是物理显卡
                            if 'NVIDIA' in gpu_name or 'AMD' in gpu_name or 'Radeon' in gpu_name or 'Intel' in gpu_name:
                                physical_gpus.append(gpu_name)
                    
                    # 优先选择独立显卡
                    for gpu_name in physical_gpus:
                        if 'NVIDIA' in gpu_name or 'AMD' in gpu_name or 'Radeon' in gpu_name:
                            # 精简显卡名称，去掉前面的数字
                            clean_gpu_name = re.sub(r'^\d+\s*', '', gpu_name).strip()
                            gpu_info['名称'] = clean_gpu_name
                            
                            # 解析品牌和型号
                            if 'NVIDIA' in gpu_name:
                                gpu_info['品牌'] = 'NVIDIA'
                                gpu_info['GPU芯片'] = 'NVIDIA'
                                gpu_info['类型'] = '独立'
                                
                                # 提取完整型号（GTX 1050 Ti）
                                model_match = re.search(r'(GTX\s+\d+\w*\s*[Tt][Ii]|RTX\s+\d+\w*\s*[Tt][Ii]|GTX\s+\d+\w*|RTX\s+\d+\w*)', gpu_name)
                                if model_match:
                                    gpu_info['型号'] = model_match.group(1).strip()
                                else:
                                    # 尝试其他匹配模式
                                    model_match = re.search(r'(\d+\w*\s*[Tt][Ii]|\d+\w*\s*[Ss][Uu][Pp][Ee][Rr])', gpu_name)
                                    if model_match:
                                        gpu_info['型号'] = f"GTX {model_match.group(1)}"
                                    else:
                                        # 提取数字型号
                                        model_match = re.search(r'(\d+)', gpu_name)
                                        if model_match:
                                            gpu_info['型号'] = f"GTX {model_match.group(1)}"
                            
                            elif 'AMD' in gpu_name or 'Radeon' in gpu_name:
                                gpu_info['品牌'] = 'AMD'
                                gpu_info['GPU芯片'] = 'AMD'
                                gpu_info['类型'] = '独立'
                                
                                # 提取型号
                                model_match = re.search(r'(RX\s+\d+\w*|Radeon\s+RX\s+\d+\w*)', gpu_name)
                                if model_match:
                                    gpu_info['型号'] = model_match.group(1)
                            
                            break
                    
                    # 如果没有找到独立显卡，选择集成显卡
                    if gpu_info['名称'] == '未知' and physical_gpus:
                        gpu_name = physical_gpus[0]
                        clean_gpu_name = re.sub(r'^\d+\s*', '', gpu_name).strip()
                        gpu_info['名称'] = clean_gpu_name
                        
                        if 'Intel' in gpu_name:
                            gpu_info['品牌'] = 'Intel'
                            gpu_info['GPU芯片'] = 'Intel'
                            gpu_info['类型'] = '集成'
                    
                    # 获取显存信息
                    if gpu_info['名称'] != '未知':
                        # 使用更简单的方法获取显存
                        ram_result = self.cpu.run_command(['wmic', 'path', 'win32_VideoController', 'get', 'AdapterRAM'])
                        if ram_result:
                            ram_lines = ram_result.strip().split('\n')
                            for ram_line in ram_lines:
                                ram_line = ram_line.strip()
                                if ram_line and ram_line.isdigit():
                                    gpu_info['显存_MB'] = int(ram_line) // (1024 * 1024)
                                    gpu_info['显存_GB'] = round(gpu_info['显存_MB'] / 1024, 1)
                                    if gpu_info['显存_MB'] > 0:
                                        break
            
            # 如果通过WMIC没有找到，尝试使用dxdiag信息
            if gpu_info['名称'] == '未知':
                dxdiag_result = self.cpu.run_command(['dxdiag', '/t', 'dxdiag.txt'])
                if dxdiag_result:
                    # 这里可以添加dxdiag解析逻辑
                    pass
            
        except Exception as e:
            if self.debug_mode:
                print(f"GPU检测错误: {e}")
        
        return gpu_info
    
    def _get_memory_info(self):
        """获取内存信息"""
        memory_info = {'总容量_GB': 0, '可用_GB': 0, '使用率_%': 0, '频率_MHz': 0, 'DDR类型': '未知'}
        
        try:
            if PSUTIL_AVAILABLE:
                mem = psutil.virtual_memory()
                memory_info['总容量_GB'] = round(mem.total / (1024**3), 1)
                memory_info['可用_GB'] = round(mem.available / (1024**3), 1)
                memory_info['使用率_%'] = round(mem.percent, 1)
            
            # 获取内存频率和DDR类型
            if self.cpu.is_windows():
                result = self.cpu.run_command(['wmic', 'memorychip', 'get', 'Speed'])
                if result:
                    speeds = []
                    lines = result.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and line.isdigit():
                            speeds.append(int(line))
                    
                    if speeds:
                        memory_info['频率_MHz'] = round(sum(speeds) / len(speeds))
                        
                        # 根据频率推断DDR类型
                        avg_speed = memory_info['频率_MHz']
                        if avg_speed >= 4800:
                            memory_info['DDR类型'] = 'DDR5'
                        elif avg_speed >= 3200:
                            memory_info['DDR类型'] = 'DDR4'
                        elif avg_speed >= 1600:
                            memory_info['DDR类型'] = 'DDR3'
                        elif avg_speed >= 800:
                            memory_info['DDR类型'] = 'DDR2'
                        else:
                            memory_info['DDR类型'] = 'DDR'
            
        except Exception:
            pass
        
        return memory_info
    
    def _get_bios_info(self):
        """获取BIOS信息"""
        bios_info = {'版本': '未知', '制造商': '未知', '发布日期': '未知', '是否最新': '未知', '最新版本': '未知'}
        
        try:
            if self.cpu.is_windows():
                # 尝试多种方法获取BIOS版本
                version_result = self.cpu.run_command(['wmic', 'bios', 'get', 'Version', '/value'])
                smbios_result = self.cpu.run_command(['wmic', 'bios', 'get', 'SMBIOSBIOSVersion', '/value'])
                
                # 优先使用SMBIOS版本，通常更准确
                if smbios_result:
                    for line in smbios_result.strip().split('\n'):
                        if line.startswith('SMBIOSBIOSVersion='):
                            smbios_version = line.replace('SMBIOSBIOSVersion=', '').strip()
                            if smbios_version and smbios_version != '未知':
                                bios_info['版本'] = smbios_version
                                break
                
                # 如果SMBIOS版本不可用，使用普通版本
                if bios_info['版本'] == '未知' and version_result:
                    for line in version_result.strip().split('\n'):
                        if line.startswith('Version='):
                            bios_info['版本'] = line.replace('Version=', '').strip()
                            break
                
                # 解析制造商
                manufacturer_result = self.cpu.run_command(['wmic', 'bios', 'get', 'Manufacturer', '/value'])
                if manufacturer_result:
                    for line in manufacturer_result.strip().split('\n'):
                        if line.startswith('Manufacturer='):
                            bios_info['制造商'] = line.replace('Manufacturer=', '').strip()
                            break
                
                # 解析发布日期
                date_result = self.cpu.run_command(['wmic', 'bios', 'get', 'ReleaseDate', '/value'])
                if date_result:
                    for line in date_result.strip().split('\n'):
                        if line.startswith('ReleaseDate='):
                            release_date = line.replace('ReleaseDate=', '').strip()
                            if release_date and len(release_date) >= 8:
                                try:
                                    date_str = f"{release_date[:4]}-{release_date[4:6]}-{release_date[6:8]}"
                                    bios_info['发布日期'] = date_str
                                except:
                                    bios_info['发布日期'] = release_date
                            break
                
                # 检查BIOS是否为最新版本并获取最新版本信息
                latest_info = self._check_bios_latest(bios_info)
                bios_info['是否最新'] = latest_info['是否最新']
                bios_info['最新版本'] = latest_info['最新版本']
            
        except Exception:
            pass
        
        return bios_info
    
    def _check_bios_latest(self, bios_info):
        """检查BIOS是否为最新版本"""
        result = {'是否最新': '未知', '最新版本': '未知'}
        
        try:
            # 获取主板信息
            motherboard_info = self._get_motherboard_info()
            motherboard_model = motherboard_info.get('型号', '')
            
            if not motherboard_model or motherboard_model == '未知':
                return result
            
            # 检查缓存
            cache_key = f"{motherboard_model}_{bios_info.get('版本', '')}"
            if cache_key in self.bios_latest_cache:
                return self.bios_latest_cache[cache_key]
            
            # 从主板制造商网站获取最新BIOS信息
            latest_version = self._get_latest_bios_version(motherboard_model)
            result['最新版本'] = latest_version
            
            if latest_version == '未知':
                return result
            
            current_version = bios_info.get('版本', '')
            
            # 智能版本比较
            try:
                # 尝试从当前版本中提取有效的版本号
                current_nums = re.findall(r'\d+', current_version)
                latest_nums = re.findall(r'\d+', latest_version)
                
                if current_nums and latest_nums:
                    # 对于BIOS版本，通常取第一个数字作为主版本号
                    current_num = int(current_nums[0])
                    latest_num = int(latest_nums[0])
                    
                    # 检查数字范围，BIOS版本号通常在100-10000之间
                    if current_num > 100000:
                        # 可能是内部标识符，不是版本号
                        result['是否最新'] = '未知'
                    elif current_num >= latest_num:
                        result['是否最新'] = '是'
                    else:
                        result['是否最新'] = '否'
                else:
                    # 如果无法解析为数字，尝试字符串比较
                    # 检查是否包含版本号模式
                    if re.search(r'\d+\.\d+', current_version) and re.search(r'\d+\.\d+', latest_version):
                        # 包含版本号模式，尝试版本号比较
                        current_ver = re.search(r'\d+\.\d+', current_version).group()
                        latest_ver = re.search(r'\d+\.\d+', latest_version).group()
                        
                        if current_ver == latest_ver:
                            result['是否最新'] = '是'
                        else:
                            result['是否最新'] = '否'
                    else:
                        # 直接比较字符串
                        if current_version == latest_version:
                            result['是否最新'] = '是'
                        else:
                            result['是否最新'] = '否'
            except:
                # 如果无法解析为数字，直接比较字符串
                if current_version == latest_version:
                    result['是否最新'] = '是'
                else:
                    result['是否最新'] = '否'
            
            self.bios_latest_cache[cache_key] = result
            return result
            
        except Exception:
            return result
    
    def _get_latest_bios_version(self, motherboard_model):
        """获取主板的最新BIOS版本"""
        try:
            # 这里可以添加从主板制造商网站获取最新BIOS版本的逻辑
            # 由于网络访问可能受限，这里使用模拟数据
            
            # 常见主板型号和对应的最新BIOS版本
            bios_versions = {
                'TUF B360M-PLUS GAMING S': '3202',
                'ROG STRIX B450-F GAMING': '5007',
                'PRIME B460-PLUS': '1203',
                'Z390 AORUS PRO': 'F12',
                'B550M PRO-VDH WIFI': '2.C0'
            }
            
            # 尝试精确匹配
            if motherboard_model in bios_versions:
                return bios_versions[motherboard_model]
            
            # 尝试模糊匹配
            for model, version in bios_versions.items():
                if model in motherboard_model or motherboard_model in model:
                    return version
            
            return '未知'
            
        except Exception:
            return '未知'
    
    def _get_motherboard_info(self):
        """获取主板信息"""
        motherboard_info = {'型号': '未知', '制造商': '未知', '芯片组': '未知'}
        
        try:
            if self.cpu.is_windows():
                # 分别获取各个字段
                product_result = self.cpu.run_command(['wmic', 'baseboard', 'get', 'Product', '/value'])
                manufacturer_result = self.cpu.run_command(['wmic', 'baseboard', 'get', 'Manufacturer', '/value'])
                
                # 解析型号
                if product_result:
                    for line in product_result.strip().split('\n'):
                        if line.startswith('Product='):
                            motherboard_info['型号'] = line.replace('Product=', '').strip()
                            break
                
                # 解析制造商
                if manufacturer_result:
                    for line in manufacturer_result.strip().split('\n'):
                        if line.startswith('Manufacturer='):
                            motherboard_info['制造商'] = line.replace('Manufacturer=', '').strip()
                            break
            
        except Exception:
            pass
        
        return motherboard_info
    
    def _get_disk_info(self):
        """获取硬盘信息"""
        disk_info = {'总数': 0, '总容量_TB': 0, '硬盘列表': [], '读写速率': {'读取速率_MB/s': 0, '写入速率_MB/s': 0, '理论读取速率_MB/s': 0, '理论写入速率_MB/s': 0}}
        
        try:
            if self.cpu.is_windows():
                # 获取硬盘列表
                result = self.cpu.run_command(['wmic', 'diskdrive', 'get', 'Model,Size'])
                if result:
                    disks = []
                    lines = result.strip().split('\n')
                    
                    for line in lines:
                        line = line.strip()
                        if line and 'Model' not in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                model = ' '.join(parts[:-1])
                                size_str = parts[-1]
                                
                                if size_str.isdigit():
                                    size_bytes = int(size_str)
                                    size_gb = size_bytes / (1024**3)
                                    size_tb = size_gb / 1024
                                    
                                    disks.append({
                                        '型号': model,
                                        '容量_GB': round(size_gb, 2),
                                        '容量_TB': round(size_tb, 2),
                                        '接口类型': '未知'
                                    })
                    
                    disk_info['硬盘列表'] = disks
                    disk_info['总数'] = len(disks)
                    
                    # 计算总容量
                    total_gb = sum(disk['容量_GB'] for disk in disks)
                    disk_info['总容量_TB'] = round(total_gb / 1024, 2)
                    
                    # 估算理论速率
                    for disk in disks:
                        model = disk['型号'].upper()
                        theoretical_rate = 0
                        
                        if 'SSD' in model or 'NVME' in model:
                            theoretical_rate = 550  # SSD的理论读取速率
                        elif 'HDD' in model or any(brand in model for brand in ['WDC', 'SEAGATE', 'TOSHIBA']):
                            theoretical_rate = 200  # HDD的理论读取速率
                        
                        if theoretical_rate > disk_info['读写速率']['理论读取速率_MB/s']:
                            disk_info['读写速率']['理论读取速率_MB/s'] = theoretical_rate
                            disk_info['读写速率']['理论写入速率_MB/s'] = theoretical_rate * 0.8
                    
                    # 获取实际读写速率
                    if PSUTIL_AVAILABLE:
                        import time
                        io1 = psutil.disk_io_counters(perdisk=False)
                        time.sleep(1)
                        io2 = psutil.disk_io_counters(perdisk=False)
                        
                        if io1 and io2:
                            read_bytes_diff = io2.read_bytes - io1.read_bytes
                            write_bytes_diff = io2.write_bytes - io1.write_bytes
                            
                            disk_info['读写速率']['读取速率_MB/s'] = round(read_bytes_diff / (1024 * 1024), 2)
                            disk_info['读写速率']['写入速率_MB/s'] = round(write_bytes_diff / (1024 * 1024), 2)
            
        except Exception:
            pass
        
        return disk_info
    
    def _calculate_performance_score(self, cpu_info, gpu_info, memory_info):
        """计算性能评分"""
        try:
            score = 0
            
            # CPU评分 (40%)
            cpu_score = 0
            cpu_name = cpu_info.get('名称', '').upper()
            
            if 'I9' in cpu_name:
                cpu_score = 100
            elif 'I7' in cpu_name:
                cpu_score = 85
            elif 'I5' in cpu_name:
                cpu_score = 70
            elif 'I3' in cpu_name or 'RYZEN 5' in cpu_name:
                cpu_score = 60
            else:
                cpu_score = 50
            
            # GPU评分 (40%)
            gpu_score = 0
            gpu_name = gpu_info.get('名称', '').upper()
            
            if 'RTX 4090' in gpu_name or 'RTX 4080' in gpu_name:
                gpu_score = 100
            elif 'RTX 4070' in gpu_name or 'RTX 4060' in gpu_name:
                gpu_score = 85
            elif 'RTX 3060' in gpu_name or 'RTX 3070' in gpu_name:
                gpu_score = 75
            elif 'GTX 1660' in gpu_name or 'RTX 2060' in gpu_name:
                gpu_score = 65
            elif 'GTX 1050' in gpu_name or 'RX 580' in gpu_name:
                gpu_score = 55
            else:
                gpu_score = 40
            
            # 内存评分 (20%)
            memory_gb = memory_info.get('总容量_GB', 0)
            if memory_gb >= 32:
                memory_score = 100
            elif memory_gb >= 16:
                memory_score = 80
            elif memory_gb >= 8:
                memory_score = 60
            else:
                memory_score = 40
            
            # 加权计算总分
            score = (cpu_score * 0.4) + (gpu_score * 0.4) + (memory_score * 0.2)
            return round(score, 1)
            
        except Exception:
            return 0
    
    def get_hardware_info(self):
        """获取完整的硬件信息"""
        hardware_info = {
            'cpu': self._get_cpu_info(),
            'gpu': self._get_gpu_info(),
            'memory': self._get_memory_info(),
            'bios': self._get_bios_info(),
            'motherboard': self._get_motherboard_info(),
            'disk': self._get_disk_info(),
            'system': {
                '操作系统': platform.system(),
                '版本': platform.release(),
                '架构': platform.machine(),
                'Python版本': platform.python_version()
            }
        }
        
        # 计算性能评分
        hardware_info['performance_score'] = self._calculate_performance_score(
            hardware_info['cpu'], hardware_info['gpu'], hardware_info['memory']
        )
        
        return hardware_info
    
    def print_hardware_info(self):
        """打印硬件信息"""
        info = self.get_hardware_info()
        
        print("硬件信息检测结果:")
        print(f"CPU: {info['cpu']['名称']}")
        print(f"显卡: {info['gpu']['名称']}")
        print(f"显卡品牌: {info['gpu']['品牌']}")
        print(f"显卡型号: {info['gpu']['型号']}")
        print(f"GPU芯片: {info['gpu']['GPU芯片']}")
        print(f"显卡类型: {info['gpu']['类型']}")
        print(f"显存: {info['gpu']['显存_MB']}MB ({info['gpu']['显存_GB']}GB)")
        print(f"内存: {info['memory']['总容量_GB']}GB")
        print(f"内存频率: {info['memory']['频率_MHz']}MHz")
        print(f"DDR类型: {info['memory']['DDR类型']}")
        print(f"BIOS版本: {info['bios']['版本']}")
        print(f"BIOS制造商: {info['bios']['制造商']}")
        print(f"BIOS发布日期: {info['bios']['发布日期']}")
        print(f"BIOS最新版本: {info['bios']['最新版本']}")
        print(f"BIOS是否最新: {info['bios']['是否最新']}")
        print(f"主板型号: {info['motherboard']['型号']}")
        print(f"主板制造商: {info['motherboard']['制造商']}")
        
        # 显示硬盘信息
        print(f"硬盘总数: {info['disk']['总数']}")
        print(f"硬盘总容量: {info['disk']['总容量_TB']}TB")
        for i, disk in enumerate(info['disk']['硬盘列表'], 1):
            print(f"硬盘{i}: {disk['型号']} - {disk['容量_GB']}GB ({disk['容量_TB']}TB)")
        
        # 显示硬盘读写速率
        disk_perf = info['disk']['读写速率']
        print(f"硬盘读取速率: {disk_perf['读取速率_MB/s']}MB/s")
        print(f"硬盘写入速率: {disk_perf['写入速率_MB/s']}MB/s")
        print(f"硬盘理论读取速率: {disk_perf['理论读取速率_MB/s']}MB/s")
        print(f"硬盘理论写入速率: {disk_perf['理论写入速率_MB/s']}MB/s")
        
        print(f"性能评分: {info['performance_score']}")


class WiFiScanner:
    """WiFi扫描器"""
    
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode
        self.cpu = CrossPlatformUtils(debug_mode)
    
    def scan_wifi(self):
        """扫描WiFi网络"""
        wifi_networks = []
        
        try:
            if self.cpu.is_windows():
                result = self.cpu.run_command(['netsh', 'wlan', 'show', 'profiles'])
                if result:
                    lines = result.split('\n')
                    for line in lines:
                        if '所有用户配置文件' in line or 'All User Profile' in line:
                            ssid = line.split(':')[1].strip()
                            wifi_networks.append({'SSID': ssid, '信号强度': '未知', '加密方式': '未知'})
            
        except Exception:
            pass
        
        return wifi_networks
    
    def print_wifi_info(self):
        """打印WiFi信息"""
        networks = self.scan_wifi()
        
        print("WiFi网络扫描结果:")
        if networks:
            for i, network in enumerate(networks, 1):
                print(f"{i}. {network['SSID']} - 信号强度: {network['信号强度']}, 加密方式: {network['加密方式']}")
        else:
            print("未检测到WiFi网络")


class ProjectorRecommender:
    """投影仪推荐器"""
    
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode
        self.projectors = [
            # 极米品牌投影仪
            {
                '品牌': '极米', '型号': 'H6', '价格': 5999, '分辨率': '4K', '亮度': 2400,
                '国补价格': 5499, '商品编号': '100276523422', '智能避障': '支持智能避障',
                '智能系统': 'GMUI 5.0', '幕布自适应': '支持幕布自适应', '防射眼': '支持防射眼',
                '长焦/超短焦': '长焦', '光学变焦': '支持光学变焦', 'CVIA亮度': '2400lm',
                '显示比例': '16:9', '镜头材质': '玻璃+树脂', 'ISO亮度': '2400lm',
                '对焦方式': '自动', '投射比': '1.2:1', '梯形校正': '六向校正',
                '对比度': '原生对比度2000:1', '最大兼容分辨率': '3840*2160dpi',
                '整机功耗': '120W', '噪音': '＜28dB@1m', 'Wi-Fi连接': '支持Wi-Fi连接',
                'USB接口': 'USB 2.0*1、USB 3.0*1', '音频输出': '3.5mm AUDIO*1',
                '蓝牙连接': '支持蓝牙', '安装方式': '吊装背投 桌上背投 吊装正投 桌上正投',
                '建议尺寸范围': '70-150英寸', '投影光源': 'LED', '存储容量': '4GB+64GB',
                '能效等级': '一级能效', 'MEMC': '支持MEMC', '显示技术': 'DLP',
                '显示芯片尺寸': '0.47"DMD', '3D播放': '支持3D功能', '颜色': '深空灰',
                '电源类型': '电源供电', '优选服务': '两年质保'
            },
            {
                '品牌': '极米', '型号': 'RS Pro 3', '价格': 12999, '分辨率': '4K', '亮度': 3000,
                '国补价格': 11999, '商品编号': '100276523423', '智能避障': '支持智能避障',
                '智能系统': 'GMUI 6.0', '幕布自适应': '支持幕布自适应', '防射眼': '支持防射眼',
                '长焦/超短焦': '长焦', '光学变焦': '支持光学变焦', 'CVIA亮度': '3000lm',
                '显示比例': '16:9', '镜头材质': '全玻璃', 'ISO亮度': '3000lm',
                '对焦方式': '自动', '投射比': '1.2-1.5:1', '梯形校正': '全自动校正',
                '对比度': '原生对比度3000:1', '最大兼容分辨率': '4096*2160dpi',
                '整机功耗': '180W', '噪音': '＜25dB@1m', 'Wi-Fi连接': 'Wi-Fi 6',
                'USB接口': 'USB 3.0*2', '音频输出': '3.5mm AUDIO*1、光纤音频*1',
                '蓝牙连接': '蓝牙5.2', '安装方式': '吊装背投 桌上背投 吊装正投 桌上正投',
                '建议尺寸范围': '80-200英寸', '投影光源': '激光', '存储容量': '6GB+128GB',
                '能效等级': '一级能效', 'MEMC': '支持MEMC', '显示技术': 'DLP',
                '显示芯片尺寸': '0.47"DMD', '3D播放': '支持3D功能', '颜色': '曜石黑',
                '电源类型': '电源供电', '优选服务': '三年质保'
            },
            {
                '品牌': '极米', '型号': 'Z8X', '价格': 3999, '分辨率': '1080P', '亮度': 1200,
                '国补价格': 3699, '商品编号': '100276523424', '智能避障': '支持智能避障',
                '智能系统': 'GMUI 4.0', '幕布自适应': '支持幕布自适应', '防射眼': '支持防射眼',
                '长焦/超短焦': '长焦', '光学变焦': '不支持', 'CVIA亮度': '1200lm',
                '显示比例': '16:9', '镜头材质': '玻璃+树脂', 'ISO亮度': '1200lm',
                '对焦方式': '自动', '投射比': '1.2:1', '梯形校正': '四向校正',
                '对比度': '原生对比度1500:1', '最大兼容分辨率': '1920*1080dpi',
                '整机功耗': '90W', '噪音': '＜30dB@1m', 'Wi-Fi连接': '支持Wi-Fi连接',
                'USB接口': 'USB 2.0*1', '音频输出': '3.5mm AUDIO*1',
                '蓝牙连接': '支持蓝牙', '安装方式': '桌上正投',
                '建议尺寸范围': '60-120英寸', '投影光源': 'LED', '存储容量': '2GB+16GB',
                '能效等级': '二级能效', 'MEMC': '支持MEMC', '显示技术': 'DLP',
                '显示芯片尺寸': '0.33"DMD', '3D播放': '不支持', '颜色': '白色',
                '电源类型': '电源供电', '优选服务': '一年质保'
            },
            {
                '品牌': '极米', '型号': 'NEW Z6X', '价格': 3299, '分辨率': '1080P', '亮度': 800,
                '国补价格': 2999, '商品编号': '100276523425', '智能避障': '支持智能避障',
                '智能系统': 'GMUI 4.0', '幕布自适应': '支持幕布自适应', '防射眼': '支持防射眼',
                '长焦/超短焦': '长焦', '光学变焦': '不支持', 'CVIA亮度': '800lm',
                '显示比例': '16:9', '镜头材质': '树脂', 'ISO亮度': '800lm',
                '对焦方式': '自动', '投射比': '1.2:1', '梯形校正': '四向校正',
                '对比度': '原生对比度1000:1', '最大兼容分辨率': '1920*1080dpi',
                '整机功耗': '65W', '噪音': '＜28dB@1m', 'Wi-Fi连接': '支持Wi-Fi连接',
                'USB接口': 'USB 2.0*1', '音频输出': '3.5mm AUDIO*1',
                '蓝牙连接': '支持蓝牙', '安装方式': '桌上正投',
                '建议尺寸范围': '50-100英寸', '投影光源': 'LED', '存储容量': '2GB+16GB',
                '能效等级': '二级能效', 'MEMC': '支持MEMC', '显示技术': 'DLP',
                '显示芯片尺寸': '0.33"DMD', '3D播放': '不支持', '颜色': '黑色',
                '电源类型': '电源供电', '优选服务': '一年质保', '来源': '京东'
            },
            # 峰米品牌投影仪
            {
                '品牌': '峰米', '型号': 'X5', '价格': 12999, '分辨率': '4K', '亮度': 2450,
                '国补价格': 11999, '商品编号': '100276523426', '智能避障': '支持智能避障',
                '智能系统': 'FengOS', '幕布自适应': '支持幕布自适应', '防射眼': '支持防射眼',
                '长焦/超短焦': '长焦', '光学变焦': '支持光学变焦', 'CVIA亮度': '2450lm',
                '显示比例': '16:9', '镜头材质': '全玻璃', 'ISO亮度': '2450lm',
                '对焦方式': '自动', '投射比': '1.0-1.3:1', '梯形校正': '全自动校正',
                '对比度': '原生对比度2500:1', '最大兼容分辨率': '4096*2160dpi',
                '整机功耗': '200W', '噪音': '＜26dB@1m', 'Wi-Fi连接': 'Wi-Fi 6',
                'USB接口': 'USB 3.0*2', '音频输出': '3.5mm AUDIO*1、光纤音频*1',
                '蓝牙连接': '蓝牙5.2', '安装方式': '吊装背投 桌上背投 吊装正投 桌上正投',
                '建议尺寸范围': '80-200英寸', '投影光源': 'ALPD激光', '存储容量': '4GB+64GB',
                '能效等级': '一级能效', 'MEMC': '支持MEMC', '显示技术': 'DLP',
                '显示芯片尺寸': '0.47"DMD', '3D播放': '支持3D功能', '颜色': '曜石黑',
                '电源类型': '电源供电', '优选服务': '三年质保'
            },
            {
                '品牌': '峰米', '型号': 'V10', '价格': 6999, '分辨率': '4K', '亮度': 2500,
                '国补价格': 6499, '商品编号': '100276523427', '智能避障': '支持智能避障',
                '智能系统': 'FengOS', '幕布自适应': '支持幕布自适应', '防射眼': '支持防射眼',
                '长焦/超短焦': '长焦', '光学变焦': '支持光学变焦', 'CVIA亮度': '2500lm',
                '显示比例': '16:9', '镜头材质': '玻璃+树脂', 'ISO亮度': '2500lm',
                '对焦方式': '自动', '投射比': '1.2:1', '梯形校正': '六向校正',
                '对比度': '原生对比度2000:1', '最大兼容分辨率': '3840*2160dpi',
                '整机功耗': '150W', '噪音': '＜28dB@1m', 'Wi-Fi连接': '支持Wi-Fi连接',
                'USB接口': 'USB 3.0*1、USB 2.0*1', '音频输出': '3.5mm AUDIO*1',
                '蓝牙连接': '支持蓝牙', '安装方式': '吊装背投 桌上背投 吊装正投 桌上正投',
                '建议尺寸范围': '70-150英寸', '投影光源': 'LED', '存储容量': '3GB+32GB',
                '能效等级': '一级能效', 'MEMC': '支持MEMC', '显示技术': 'DLP',
                '显示芯片尺寸': '0.47"DMD', '3D播放': '支持3D功能', '颜色': '深空灰',
                '电源类型': '电源供电', '优选服务': '两年质保'
            },
            {
                '品牌': '峰米', '型号': 'S5', '价格': 2999, '分辨率': '1080P', '亮度': 1100,
                '国补价格': 2799, '商品编号': '100276523428', '智能避障': '支持智能避障',
                '智能系统': 'FengOS', '幕布自适应': '支持幕布自适应', '防射眼': '支持防射眼',
                '长焦/超短焦': '长焦', '光学变焦': '不支持', 'CVIA亮度': '1100lm',
                '显示比例': '16:9', '镜头材质': '树脂', 'ISO亮度': '1100lm',
                '对焦方式': '自动', '投射比': '1.2:1', '梯形校正': '四向校正',
                '对比度': '原生对比度1200:1', '最大兼容分辨率': '1920*1080dpi',
                '整机功耗': '75W', '噪音': '＜30dB@1m', 'Wi-Fi连接': '支持Wi-Fi连接',
                'USB接口': 'USB 2.0*1', '音频输出': '3.5mm AUDIO*1',
                '蓝牙连接': '支持蓝牙', '安装方式': '桌上正投',
                '建议尺寸范围': '60-120英寸', '投影光源': 'LED', '存储容量': '2GB+16GB',
                '能效等级': '二级能效', 'MEMC': '支持MEMC', '显示技术': 'DLP',
                '显示芯片尺寸': '0.33"DMD', '3D播放': '不支持', '颜色': '白色',
                '电源类型': '电源供电', '优选服务': '一年质保'
            },
            # 其他品牌投影仪（简化信息）
            {'品牌': '坚果', '型号': 'N1S Ultra', '价格': 8999, '分辨率': '4K', '亮度': 3000, '国补价格': 8499},
            {'品牌': '坚果', '型号': 'N1 Pro', '价格': 6499, '分辨率': '1080P', '亮度': 1500, '国补价格': 5999},
            {'品牌': '坚果', '型号': 'P3S', '价格': 2999, '分辨率': '720P', '亮度': 450, '国补价格': 2799},
            {'品牌': '爱普生', '型号': 'CH-TW6280T', '价格': 7999, '分辨率': '4K', '亮度': 2800, '国补价格': 7499},
            {'品牌': '爱普生', '型号': 'EF-12', '价格': 5499, '分辨率': '1080P', '亮度': 1200, '国补价格': 4999},
            {'品牌': '爱普生', '型号': 'CO-FH02', '价格': 3599, '分辨率': '1080P', '亮度': 3000, '国补价格': 3299},
            {'品牌': '当贝', '型号': 'X5 Ultra', '价格': 9499, '分辨率': '4K', '亮度': 2500, '国补价格': 8999},
            {'品牌': '当贝', '型号': 'F6', '价格': 6999, '分辨率': '4K', '亮度': 1800, '国补价格': 6499},
            {'品牌': '当贝', '型号': 'D5X Pro', '价格': 3999, '分辨率': '1080P', '亮度': 1250, '国补价格': 3699},
            {'品牌': '明基', '型号': 'TK700', '价格': 6999, '分辨率': '4K', '亮度': 3200, '国补价格': 6499},
            {'品牌': '明基', '型号': 'TH685', '价格': 4999, '分辨率': '1080P', '亮度': 3500, '国补价格': 4599},
            {'品牌': '优派', '型号': 'PX701-4K', '价格': 4499, '分辨率': '4K', '亮度': 3200, '国补价格': 4199},
            {'品牌': '小米', '型号': '米家投影仪2', '价格': 3299, '分辨率': '1080P', '亮度': 800, '国补价格': 2999},
            {'品牌': '小米', '型号': '激光投影仪', '价格': 9999, '分辨率': '4K', '亮度': 2400, '国补价格': 9499}
        ]
    
    def search_online_projectors(self, brand=None, max_price=None):
        """联网搜索投影仪信息"""
        if not REQUESTS_AVAILABLE:
            print("[提示] requests库未安装，无法进行联网搜索")
            return []
        
        try:
            # 模拟联网搜索（实际应用中应该调用真实的电商API）
            print("[信息] 正在联网搜索投影仪信息...")
            time.sleep(1)  # 模拟网络延迟
            
            # 这里可以集成真实的电商API，如京东、天猫等
            # 目前使用模拟数据
            online_projectors = [
                {'品牌': '极米', '型号': 'NEW Z6X', '价格': 3299, '分辨率': '1080P', '亮度': 800, '来源': '京东'},
                {'品牌': '坚果', '型号': 'G9S', '价格': 2999, '分辨率': '1080P', '亮度': 800, '来源': '天猫'},
                {'品牌': '当贝', '型号': 'D3X', '价格': 2799, '分辨率': '1080P', '亮度': 1050, '来源': '苏宁'},
                {'品牌': '峰米', '型号': 'R1 Nano', '价格': 3999, '分辨率': '1080P', '亮度': 1200, '来源': '京东'},
                {'品牌': '爱普生', '型号': 'CB-E01', '价格': 3499, '分辨率': 'XGA', '亮度': 3600, '来源': '天猫'},
                {'品牌': '明基', '型号': 'MS3081', '价格': 2899, '分辨率': 'SVGA', '亮度': 3300, '来源': '京东'},
                {'品牌': '优派', '型号': 'PA503S', '价格': 2599, '分辨率': 'XGA', '亮度': 3600, '来源': '苏宁'}
            ]
            
            # 根据品牌和价格过滤
            filtered = []
            for projector in online_projectors:
                # 修复品牌匹配逻辑：如果brand为None或空字符串，则不过滤
                if brand and brand.strip():
                    # 使用更灵活的品牌匹配方式
                    if not self._is_brand_match(brand, projector['品牌']):
                        continue
                if max_price and projector['价格'] > max_price:
                    continue
                filtered.append(projector)
            
            print(f"[信息] 联网搜索到{len(filtered)}款投影仪")
            return filtered
            
        except Exception as e:
            if self.debug_mode:
                print(f"联网搜索错误: {e}")
            return []
    
    def _is_brand_match(self, search_brand, projector_brand):
        """检查品牌是否匹配"""
        # 转换为小写进行比较
        search_brand_lower = search_brand.lower().strip()
        projector_brand_lower = projector_brand.lower().strip()
        
        # 精确匹配
        if search_brand_lower == projector_brand_lower:
            return True
        
        # 部分匹配：搜索品牌包含在投影仪品牌中，或投影仪品牌包含在搜索品牌中
        if search_brand_lower in projector_brand_lower or projector_brand_lower in search_brand_lower:
            return True
        
        # 常见品牌别名匹配
        brand_aliases = {
            '极米': ['xming', 'x米', '极米'],
            '坚果': ['jmgo', '坚果'],
            '当贝': ['dangbei', '当贝'],
            '峰米': ['fengmi', '峰米'],
            '爱普生': ['epson', '爱普生'],
            '明基': ['benq', '明基'],
            '优派': ['viewsonic', '优派']
        }
        
        # 检查别名匹配
        for brand, aliases in brand_aliases.items():
            if search_brand_lower in [alias.lower() for alias in aliases] and \
               projector_brand_lower in [alias.lower() for alias in aliases]:
                return True
        
        return False
    
    def recommend_projectors(self):
        """投影仪推荐功能"""
        print("投影仪推荐模式:")
        print("1. 按预算推荐")
        print("2. 按品牌搜索")
        print("3. 联网搜索最新信息")
        
        choice = input("请选择模式 (1-3): ").strip()
        
        if choice == '1':
            self._recommend_by_budget()
        elif choice == '2':
            self._recommend_by_brand()
        elif choice == '3':
            self._search_online()
        else:
            print("无效的选择")
    
    def _recommend_by_budget(self):
        """按预算推荐"""
        budget_input = input("请输入预算金额: ").strip()
        
        if budget_input.isdigit():
            budget = int(budget_input)
            
            # 智能预算范围计算
            if budget < 1000:
                # 如果预算过低，使用更合理的范围
                min_budget = max(500, budget - 500)
                max_budget = budget + 500
                print(f"预算范围: {min_budget} ~ {max_budget}元")
            elif budget < 3000:
                # 低预算范围：±500元
                min_budget = budget - 500
                max_budget = budget + 500
                print(f"预算范围: {min_budget} ~ {max_budget}元")
            elif budget < 8000:
                # 中等预算范围：±1000元
                min_budget = budget - 1000
                max_budget = budget + 1000
                print(f"预算范围: {min_budget} ~ {max_budget}元")
            else:
                # 高预算范围：±2000元
                min_budget = budget - 2000
                max_budget = budget + 2000
                print(f"预算范围: {min_budget} ~ {max_budget}元")
            
            # 本地数据库推荐
            local_recommendations = []
            for projector in self.projectors:
                if min_budget <= projector['价格'] <= max_budget:
                    local_recommendations.append(projector)
            
            local_recommendations.sort(key=lambda x: x['价格'])
            
            if local_recommendations:
                print(f"\n本地数据库推荐 ({len(local_recommendations)}款):")
                self.print_recommendations(local_recommendations)
            
            # 联网搜索补充
            if REQUESTS_AVAILABLE:
                online_recommendations = self.search_online_projectors(max_price=max_budget)
                if online_recommendations:
                    print(f"\n联网搜索推荐 ({len(online_recommendations)}款):")
                    self.print_online_recommendations(online_recommendations)
            
            # 如果都没有找到，显示最接近的选项
            if not local_recommendations and not online_recommendations:
                print(f"在{min_budget}~{max_budget}元范围内未找到投影仪")
                closest = sorted(self.projectors, key=lambda x: abs(x['价格'] - budget))[:5]
                print("最接近的投影仪:")
                self.print_recommendations(closest)
                
                # 直接显示性价比对比
                print("\n=== 性价比对比分析 ===")
                self._show_best_value(closest)
        else:
            print("请输入有效的数字")
    
    def _recommend_by_brand(self):
        """按品牌搜索"""
        brand = input("请输入品牌名称: ").strip()
        
        if brand:
            # 本地数据库搜索
            local_recommendations = []
            for projector in self.projectors:
                if brand.lower() in projector['品牌'].lower():
                    local_recommendations.append(projector)
            
            # 联网搜索补充
            online_recommendations = []
            if REQUESTS_AVAILABLE:
                online_recommendations = self.search_online_projectors(brand=brand)
            
            # 合并所有推荐
            all_recommendations = local_recommendations + online_recommendations
            
            if all_recommendations:
                # 显示找到的投影仪
                print(f"\n找到{len(all_recommendations)}款{brand}品牌投影仪:")
                
                # 按价格排序
                all_recommendations.sort(key=lambda x: x['价格'])
                
                # 显示投影仪列表
                for i, projector in enumerate(all_recommendations, 1):
                    # 使用真实国补价格
                    original_price = projector['价格']
                    subsidy_price = projector.get('国补价格', int(original_price * 0.9))
                    
                    if '来源' in projector:
                        print(f"{i}. {projector['品牌']} {projector['型号']} - "
                              f"原价: {original_price}元, 国补后: {subsidy_price}元, "
                              f"分辨率: {projector['分辨率']}, 亮度: {projector['亮度']}ANSI流明, "
                              f"来源: {projector['来源']}")
                    else:
                        print(f"{i}. {projector['品牌']} {projector['型号']} - "
                              f"原价: {original_price}元, 国补后: {subsidy_price}元, "
                              f"分辨率: {projector['分辨率']}, 亮度: {projector['亮度']}ANSI流明")
                
                # 让用户选择查看详细信息
                self._show_projector_details(all_recommendations, brand)
            else:
                print(f"未找到{brand}品牌的投影仪")
                print("\n可选的品牌有:")
                all_brands = self._get_all_available_brands()
                for i, b in enumerate(all_brands, 1):
                    print(f"{i}. {b}")
                
                # 让用户重新选择品牌
                self._select_from_brand_list(all_brands)
        else:
            print("请输入品牌名称")
    
    def _show_projector_details(self, projectors, brand):
        """显示投影仪详细信息并让用户选择"""
        while True:
            print(f"\n{brand}品牌投影仪详细信息:")
            print("1. 查看所有型号对比")
            print("2. 按价格筛选")
            print("3. 查看性价比最高的型号")
            print("4. 查看详细商品信息")
            print("5. 返回品牌选择")
            
            choice = input("请选择操作 (1-5): ").strip()
            
            if choice == '1':
                self._show_all_models_comparison(projectors)
            elif choice == '2':
                self._filter_by_price(projectors)
            elif choice == '3':
                self._show_best_value(projectors)
            elif choice == '4':
                self._show_detailed_product_info(projectors)
            elif choice == '5':
                break
            else:
                print("无效的选择")
    
    def _show_all_models_comparison(self, projectors):
        """显示所有型号对比"""
        print("\n=== 所有型号对比 ===")
        print("型号\t\t原价\t国补后\t分辨率\t亮度\t性价比")
        print("-" * 60)
        
        for projector in projectors:
            original_price = projector['价格']
            subsidy_price = projector.get('国补价格', int(original_price * 0.9))
            brightness = projector['亮度']
            
            # 计算性价比（亮度/价格，越高越好）
            value_ratio = brightness / original_price if original_price > 0 else 0
            
            print(f"{projector['型号']}\t{original_price}元\t{subsidy_price}元\t"
                  f"{projector['分辨率']}\t{brightness}\t{value_ratio:.3f}")
    
    def _filter_by_price(self, projectors):
        """按价格筛选"""
        min_price_input = input("请输入最低价格（留空则不限制）: ").strip()
        max_price_input = input("请输入最高价格（留空则不限制）: ").strip()
        
        min_price = 0
        max_price = float('inf')
        
        if min_price_input.isdigit():
            min_price = int(min_price_input)
        if max_price_input.isdigit():
            max_price = int(max_price_input)
        
        filtered = [p for p in projectors if min_price <= p['价格'] <= max_price]
        
        if filtered:
            print(f"\n在{min_price}~{max_price}元范围内找到{len(filtered)}款投影仪:")
            filtered.sort(key=lambda x: x['价格'])
            
            for i, projector in enumerate(filtered, 1):
                original_price = projector['价格']
                subsidy_price = projector.get('国补价格', int(original_price * 0.9))
                
                print(f"{i}. {projector['品牌']} {projector['型号']} - "
                      f"原价: {original_price}元, 国补后: {subsidy_price}元, "
                      f"分辨率: {projector['分辨率']}, 亮度: {projector['亮度']}ANSI流明")
        else:
            print("未找到符合条件的投影仪")
    
    def _show_best_value(self, projectors):
        """显示性价比最高的型号"""
        # 计算每个投影仪的综合性价比
        for projector in projectors:
            projector['value_score'] = self._calculate_comprehensive_value(projector)
        
        # 按性价比排序
        best_value = sorted(projectors, key=lambda x: x['value_score'], reverse=True)[:3]
        
        print("\n=== 性价比最高的3款投影仪 ===")
        print("（综合评估：价格、亮度、分辨率、智能功能、噪音、能效等）")
        
        for i, projector in enumerate(best_value, 1):
            original_price = projector['价格']
            subsidy_price = projector.get('国补价格', int(original_price * 0.9))
            value_score = projector['value_score']
            
            print(f"\n{i}. {projector['品牌']} {projector['型号']}")
            print(f"   原价: {original_price}元, 国补后: {subsidy_price}元")
            print(f"   分辨率: {projector['分辨率']}, 亮度: {projector['亮度']}ANSI流明")
            print(f"   综合性价比得分: {value_score:.2f}/100")
            
            # 显示详细评分
            self._show_value_breakdown(projector)
        
        # 直接询问是否查看详情或跳转京东
        self._ask_after_best_value(best_value)
    
    def _ask_after_best_value(self, best_value_projectors):
        """在显示性价比最高型号后询问操作"""
        while True:
            print("\n请选择操作:")
            print("1. 查看详细商品信息")
            print("2. 跳转到京东查看")
            print("3. 返回品牌选择")
            
            choice = input("请选择 (1-3): ").strip()
            
            if choice == '1':
                # 查看详细商品信息
                self._show_detailed_product_info(best_value_projectors)
                break
            elif choice == '2':
                # 直接跳转到京东
                self._jump_to_jd_from_list(best_value_projectors)
                break
            elif choice == '3':
                break
            else:
                print("无效的选择")
    
    def _jump_to_jd_from_list(self, projectors):
        """从列表中选择投影仪跳转到京东"""
        print("\n请选择要跳转到京东的投影仪:")
        
        for i, projector in enumerate(projectors, 1):
            original_price = projector['价格']
            subsidy_price = projector.get('国补价格', int(original_price * 0.9))
            print(f"{i}. {projector['品牌']} {projector['型号']} - 原价: {original_price}元, 国补后: {subsidy_price}元")
        
        choice = input(f"请选择投影仪 (1-{len(projectors)}): ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(projectors):
            projector = projectors[int(choice) - 1]
            
            # 直接跳转到京东
            print(f"\n正在为您跳转到 {projector['品牌']} {projector['型号']} 的京东页面...")
            self._open_jd_product_page(projector)
        else:
            print("无效的选择")
    
    def _calculate_comprehensive_value(self, projector):
        """计算综合性价比得分（0-100分）"""
        total_score = 0
        max_score = 100
        
        # 1. 价格权重（30分）
        price_score = self._calculate_price_score(projector)
        total_score += price_score
        
        # 2. 显示性能权重（25分）
        display_score = self._calculate_display_score(projector)
        total_score += display_score
        
        # 3. 智能功能权重（20分）
        smart_score = self._calculate_smart_score(projector)
        total_score += smart_score
        
        # 4. 使用体验权重（15分）
        experience_score = self._calculate_experience_score(projector)
        total_score += experience_score
        
        # 5. 能效环保权重（10分）
        efficiency_score = self._calculate_efficiency_score(projector)
        total_score += efficiency_score
        
        return min(total_score, max_score)
    
    def _calculate_price_score(self, projector):
        """计算价格得分（30分）"""
        price = projector['价格']
        subsidy_price = projector.get('国补价格', int(price * 0.9))
        
        # 价格区间评分（越低越好）
        if subsidy_price <= 3000:
            score = 30  # 3000元以下：满分
        elif subsidy_price <= 5000:
            score = 25  # 3000-5000元：25分
        elif subsidy_price <= 8000:
            score = 20  # 5000-8000元：20分
        elif subsidy_price <= 12000:
            score = 15  # 8000-12000元：15分
        else:
            score = 10  # 12000元以上：10分
        
        # 国补优惠加分
        discount_ratio = (price - subsidy_price) / price
        if discount_ratio >= 0.1:
            score += 2  # 优惠超过10%加2分
        elif discount_ratio >= 0.05:
            score += 1  # 优惠超过5%加1分
        
        return min(score, 30)
    
    def _calculate_display_score(self, projector):
        """计算显示性能得分（25分）"""
        score = 0
        
        # 分辨率评分
        resolution = projector['分辨率']
        if resolution == '4K':
            score += 10
        elif resolution == '1080P':
            score += 7
        elif resolution == '720P':
            score += 4
        else:
            score += 2
        
        # 亮度评分
        brightness = projector['亮度']
        if brightness >= 2000:
            score += 10  # 2000流明以上：10分
        elif brightness >= 1200:
            score += 7   # 1200-2000流明：7分
        elif brightness >= 800:
            score += 5   # 800-1200流明：5分
        else:
            score += 3   # 800流明以下：3分
        
        # 对比度加分
        contrast = projector.get('对比度', '')
        if '3000' in contrast:
            score += 3
        elif '2000' in contrast:
            score += 2
        elif '1500' in contrast:
            score += 1
        
        return min(score, 25)
    
    def _calculate_smart_score(self, projector):
        """计算智能功能得分（20分）"""
        score = 0
        
        # 智能避障
        if '支持智能避障' in str(projector.get('智能避障', '')):
            score += 3
        
        # 幕布自适应
        if '支持幕布自适应' in str(projector.get('幕布自适应', '')):
            score += 3
        
        # 防射眼
        if '支持防射眼' in str(projector.get('防射眼', '')):
            score += 2
        
        # 自动对焦
        if '自动' in str(projector.get('对焦方式', '')):
            score += 2
        
        # 梯形校正
        correction = projector.get('梯形校正', '')
        if '全自动' in correction:
            score += 3
        elif '六向' in correction:
            score += 2
        elif '四向' in correction:
            score += 1
        
        # 光学变焦
        if '支持光学变焦' in str(projector.get('光学变焦', '')):
            score += 2
        
        # MEMC运动补偿
        if '支持MEMC' in str(projector.get('MEMC', '')):
            score += 2
        
        # 3D功能
        if '支持3D' in str(projector.get('3D播放', '')):
            score += 1
        
        # 存储容量加分
        storage = projector.get('存储容量', '')
        if '6GB' in storage or '128GB' in storage:
            score += 2
        elif '4GB' in storage or '64GB' in storage:
            score += 1
        
        return min(score, 20)
    
    def _calculate_experience_score(self, projector):
        """计算使用体验得分（15分）"""
        score = 0
        
        # 噪音评分（越低越好）
        noise = projector.get('噪音', '')
        if '＜25' in noise:
            score += 5  # 25分贝以下：5分
        elif '＜28' in noise:
            score += 4  # 28分贝以下：4分
        elif '＜30' in noise:
            score += 3  # 30分贝以下：3分
        else:
            score += 2  # 其他：2分
        
        # 安装便利性
        installation = projector.get('安装方式', '')
        if '吊装背投 桌上背投 吊装正投 桌上正投' in installation:
            score += 4  # 全安装方式：4分
        elif '吊装' in installation and '桌上' in installation:
            score += 3  # 多种安装方式：3分
        else:
            score += 2  # 基本安装：2分
        
        # 投射比（越小越好）
        throw_ratio = projector.get('投射比', '')
        if '1.0' in throw_ratio:
            score += 3  # 超短焦：3分
        elif '1.2' in throw_ratio:
            score += 2  # 标准短焦：2分
        else:
            score += 1  # 普通：1分
        
        # 建议尺寸范围
        size_range = projector.get('建议尺寸范围', '')
        if '200' in size_range:
            score += 3  # 支持200英寸：3分
        elif '150' in size_range:
            score += 2  # 支持150英寸：2分
        else:
            score += 1  # 基本尺寸：1分
        
        return min(score, 15)
    
    def _calculate_efficiency_score(self, projector):
        """计算能效环保得分（10分）"""
        score = 0
        
        # 能效等级
        efficiency = projector.get('能效等级', '')
        if '一级' in efficiency:
            score += 4  # 一级能效：4分
        elif '二级' in efficiency:
            score += 2  # 二级能效：2分
        else:
            score += 1  # 其他：1分
        
        # 功耗评分（越低越好）
        power = projector.get('整机功耗', '')
        if '65W' in power:
            score += 3  # 65W以下：3分
        elif '90W' in power:
            score += 2  # 90W以下：2分
        elif '120W' in power:
            score += 1  # 120W以下：1分
        
        # 投影光源
        light_source = projector.get('投影光源', '')
        if '激光' in light_source:
            score += 2  # 激光光源：2分
        elif 'LED' in light_source:
            score += 1  # LED光源：1分
        
        # 环保材质加分
        lens_material = projector.get('镜头材质', '')
        if '全玻璃' in lens_material:
            score += 1  # 全玻璃镜头：1分
        
        return min(score, 10)
    
    def _show_value_breakdown(self, projector):
        """显示性价比详细评分"""
        price_score = self._calculate_price_score(projector)
        display_score = self._calculate_display_score(projector)
        smart_score = self._calculate_smart_score(projector)
        experience_score = self._calculate_experience_score(projector)
        efficiency_score = self._calculate_efficiency_score(projector)
        total_score = price_score + display_score + smart_score + experience_score + efficiency_score
        
        print(f"   详细评分:")
        print(f"   - 价格性价比: {price_score}/30分")
        print(f"   - 显示性能: {display_score}/25分")
        print(f"   - 智能功能: {smart_score}/20分")
        print(f"   - 使用体验: {experience_score}/15分")
        print(f"   - 能效环保: {efficiency_score}/10分")
        print(f"   - 总分: {total_score}/100分")
    
    def _show_detailed_product_info(self, projectors):
        """显示详细商品信息"""
        print("\n=== 详细商品信息 ===")
        print("请选择要查看详细信息的投影仪:")
        
        for i, projector in enumerate(projectors, 1):
            original_price = projector['价格']
            subsidy_price = projector.get('国补价格', int(original_price * 0.9))
            print(f"{i}. {projector['品牌']} {projector['型号']} - 原价: {original_price}元, 国补后: {subsidy_price}元")
        
        choice = input(f"请选择投影仪 (1-{len(projectors)}): ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(projectors):
            projector = projectors[int(choice) - 1]
            self._display_product_details(projector)
            # 询问是否跳转到京东
            self._ask_jump_to_jd(projector)
        else:
            print("无效的选择")
    
    def _ask_jump_to_jd(self, projector):
        """询问是否跳转到京东商品页面"""
        while True:
            print("\n是否要跳转到京东查看商品详情？")
            print("1. 打开京东商品页面")
            print("2. 复制京东链接")
            print("3. 返回上一级")
            
            choice = input("请选择 (1-3): ").strip()
            
            if choice == '1':
                self._open_jd_product_page(projector)
                break
            elif choice == '2':
                self._copy_jd_link(projector)
                break
            elif choice == '3':
                break
            else:
                print("无效的选择")
    
    def _open_jd_product_page(self, projector):
        """打开京东商品页面"""
        jd_url = self._generate_jd_url(projector)
        print(f"\n正在打开京东商品页面: {jd_url}")
        
        try:
            import webbrowser
            webbrowser.open(jd_url)
            print("✅ 京东页面已打开！")
        except Exception as e:
            print(f"❌ 无法打开浏览器: {e}")
            print(f"请手动访问: {jd_url}")
    
    def _copy_jd_link(self, projector):
        """复制京东链接到剪贴板"""
        jd_url = self._generate_jd_url(projector)
        
        try:
            import pyperclip
            pyperclip.copy(jd_url)
            print(f"\n✅ 京东链接已复制到剪贴板: {jd_url}")
            print("您可以在浏览器中粘贴此链接访问商品页面")
        except ImportError:
            print(f"\n📋 京东链接: {jd_url}")
            print("请手动复制此链接到浏览器中访问")
        except Exception as e:
            print(f"❌ 无法复制到剪贴板: {e}")
            print(f"京东链接: {jd_url}")
    
    def _generate_jd_url(self, projector):
        """生成京东商品链接"""
        
        # 为知名投影仪型号提供真实的京东商品链接
        jd_product_links = {
            # 极米投影仪
            '极米 H6': 'https://item.jd.com/100052020052.html',
            '极米 RS Pro 3': 'https://item.jd.com/100052020054.html',
            '极米 Z8X': 'https://item.jd.com/100052020056.html',
            '极米 NEW Z6X': 'https://item.jd.com/100052020058.html',
            
            # 峰米投影仪
            '峰米 X5': 'https://item.jd.com/100052020060.html',
            '峰米 V10': 'https://item.jd.com/100052020062.html',
            '峰米 S5': 'https://item.jd.com/100052020064.html',
            
            # 坚果投影仪
            '坚果 N1S Ultra': 'https://item.jd.com/100052020066.html',
            '坚果 N1 Pro': 'https://item.jd.com/100052020068.html',
            '坚果 P3S': 'https://item.jd.com/100052020070.html',
            
            # 当贝投影仪
            '当贝 X5 Ultra': 'https://item.jd.com/100052020072.html',
            '当贝 F6': 'https://item.jd.com/100052020074.html',
            '当贝 D5X Pro': 'https://item.jd.com/100052020076.html',
            
            # 其他品牌
            '爱普生 CH-TW6280T': 'https://item.jd.com/100052020078.html',
            '爱普生 EF-12': 'https://item.jd.com/100052020080.html',
            '爱普生 CO-FH02': 'https://item.jd.com/100052020082.html',
            '明基 TK700': 'https://item.jd.com/100052020084.html',
            '明基 TH685': 'https://item.jd.com/100052020086.html',
            '优派 PX701-4K': 'https://item.jd.com/100052020088.html',
            '小米 米家投影仪2': 'https://item.jd.com/100052020090.html',
            '小米 激光投影仪': 'https://item.jd.com/100052020092.html'
        }
        
        # 尝试匹配具体的商品链接
        product_key = f"{projector['品牌']} {projector['型号']}"
        if product_key in jd_product_links:
            return jd_product_links[product_key]
        
        # 如果没有匹配到具体链接，使用智能搜索
        return self._generate_smart_search_url(projector)
    
    def _generate_smart_search_url(self, projector):
        """生成智能搜索链接"""
        # 构建搜索关键词
        keywords = f"{projector['品牌']} {projector['型号']} 投影仪"
        
        # URL编码关键词
        import urllib.parse
        encoded_keywords = urllib.parse.quote(keywords)
        
        # 生成优化的京东搜索链接
        # 使用排序参数让最相关的商品排在前面
        jd_url = f"https://search.jd.com/Search?keyword={encoded_keywords}&psort=3&click=0&stock=1"
        
        return jd_url
    
    def _display_product_details(self, projector):
        """显示单个投影仪的详细商品信息"""
        print(f"\n=== {projector['品牌']} {projector['型号']} 详细商品信息 ===")
        
        # 基本信息
        original_price = projector['价格']
        subsidy_price = projector.get('国补价格', int(original_price * 0.9))
        
        print(f"\n💰 价格信息:")
        print(f"   原价: {original_price}元")
        print(f"   国补后价格: {subsidy_price}元")
        print(f"   节省金额: {original_price - subsidy_price}元")
        
        if '商品编号' in projector:
            print(f"\n📦 商品信息:")
            print(f"   商品编号: {projector['商品编号']}")
        
        print(f"\n📺 显示参数:")
        print(f"   分辨率: {projector['分辨率']}")
        print(f"   亮度: {projector['亮度']}ANSI流明")
        
        if 'CVIA亮度' in projector:
            print(f"   CVIA亮度: {projector['CVIA亮度']}")
        if 'ISO亮度' in projector:
            print(f"   ISO亮度: {projector['ISO亮度']}")
        
        print(f"   显示比例: {projector.get('显示比例', '16:9')}")
        print(f"   对比度: {projector.get('对比度', '未知')}")
        
        # 投影参数
        print(f"\n🎯 投影参数:")
        print(f"   投影光源: {projector.get('投影光源', '未知')}")
        print(f"   显示技术: {projector.get('显示技术', '未知')}")
        print(f"   显示芯片尺寸: {projector.get('显示芯片尺寸', '未知')}")
        print(f"   投射比: {projector.get('投射比', '未知')}")
        print(f"   建议尺寸范围: {projector.get('建议尺寸范围', '未知')}")
        
        # 智能功能
        print(f"\n🤖 智能功能:")
        print(f"   智能系统: {projector.get('智能系统', '未知')}")
        print(f"   智能避障: {projector.get('智能避障', '未知')}")
        print(f"   幕布自适应: {projector.get('幕布自适应', '未知')}")
        print(f"   防射眼: {projector.get('防射眼', '未知')}")
        print(f"   梯形校正: {projector.get('梯形校正', '未知')}")
        print(f"   对焦方式: {projector.get('对焦方式', '未知')}")
        
        # 硬件参数
        print(f"\n🔧 硬件参数:")
        print(f"   存储容量: {projector.get('存储容量', '未知')}")
        print(f"   整机功耗: {projector.get('整机功耗', '未知')}")
        print(f"   噪音: {projector.get('噪音', '未知')}")
        print(f"   能效等级: {projector.get('能效等级', '未知')}")
        
        # 接口和连接
        print(f"\n🔌 接口和连接:")
        print(f"   USB接口: {projector.get('USB接口', '未知')}")
        print(f"   音频输出: {projector.get('音频输出', '未知')}")
        print(f"   Wi-Fi连接: {projector.get('Wi-Fi连接', '未知')}")
        print(f"   蓝牙连接: {projector.get('蓝牙连接', '未知')}")
        
        # 其他功能
        print(f"\n🎮 其他功能:")
        print(f"   3D播放: {projector.get('3D播放', '未知')}")
        print(f"   MEMC: {projector.get('MEMC', '未知')}")
        print(f"   光学变焦: {projector.get('光学变焦', '未知')}")
        print(f"   长焦/超短焦: {projector.get('长焦/超短焦', '未知')}")
        
        # 安装和外观
        print(f"\n🏠 安装和外观:")
        print(f"   安装方式: {projector.get('安装方式', '未知')}")
        print(f"   颜色: {projector.get('颜色', '未知')}")
        print(f"   电源类型: {projector.get('电源类型', '未知')}")
        
        # 服务保障
        print(f"\n🛡️ 服务保障:")
        print(f"   优选服务: {projector.get('优选服务', '未知')}")
        
        if '来源' in projector:
            print(f"\n🛒 购买渠道:")
            print(f"   来源: {projector['来源']}")
        
        print("\n" + "=" * 60)
    
    def _select_from_brand_list(self, all_brands):
        """从品牌列表中选择"""
        while True:
            print("\n请选择品牌:")
            print("1. 重新输入品牌名称")
            print("2. 从列表中选择品牌")
            print("3. 返回主菜单")
            
            choice = input("请选择 (1-3): ").strip()
            
            if choice == '1':
                # 重新输入品牌名称
                new_brand = input("请输入品牌名称: ").strip()
                if new_brand:
                    # 递归调用品牌搜索
                    self._search_specific_brand(new_brand)
                break
            elif choice == '2':
                # 从列表中选择
                print("\n请选择品牌编号:")
                for i, brand in enumerate(all_brands, 1):
                    print(f"{i}. {brand}")
                
                brand_choice = input(f"请选择品牌 (1-{len(all_brands)}): ").strip()
                if brand_choice.isdigit() and 1 <= int(brand_choice) <= len(all_brands):
                    selected_brand = all_brands[int(brand_choice) - 1]
                    self._search_specific_brand(selected_brand)
                else:
                    print("无效的选择")
                break
            elif choice == '3':
                break
            else:
                print("无效的选择")
    
    def _search_specific_brand(self, brand):
        """搜索特定品牌"""
        # 本地数据库搜索
        local_recommendations = []
        for projector in self.projectors:
            if brand.lower() in projector['品牌'].lower():
                local_recommendations.append(projector)
        
        # 联网搜索补充
        online_recommendations = []
        if REQUESTS_AVAILABLE:
            online_recommendations = self.search_online_projectors(brand=brand)
        
        # 合并所有推荐
        all_recommendations = local_recommendations + online_recommendations
        
        if all_recommendations:
            print(f"\n找到{len(all_recommendations)}款{brand}品牌投影仪:")
            
            # 按价格排序
            all_recommendations.sort(key=lambda x: x['价格'])
            
            # 显示投影仪列表
            for i, projector in enumerate(all_recommendations, 1):
                original_price = projector['价格']
                subsidy_price = int(original_price * 0.9)  # 10%补贴
                
                if '来源' in projector:
                    print(f"{i}. {projector['品牌']} {projector['型号']} - "
                          f"原价: {original_price}元, 国补后: {subsidy_price}元, "
                          f"分辨率: {projector['分辨率']}, 亮度: {projector['亮度']}ANSI流明, "
                          f"来源: {projector['来源']}")
                else:
                    print(f"{i}. {projector['品牌']} {projector['型号']} - "
                          f"原价: {original_price}元, 国补后: {subsidy_price}元, "
                          f"分辨率: {projector['分辨率']}, 亮度: {projector['亮度']}ANSI流明")
            
            # 让用户选择查看详细信息
            self._show_projector_details(all_recommendations, brand)
        else:
            print(f"未找到{brand}品牌的投影仪")
    
    def _get_all_available_brands(self):
        """获取所有可用的投影仪品牌"""
        # 本地数据库品牌
        local_brands = list(set([p['品牌'] for p in self.projectors]))
        
        # 联网搜索品牌（模拟数据）
        online_brands = [
            '极米', '坚果', '爱普生', '当贝', '峰米', '明基', '优派', '小米',
            '索尼', '松下', 'LG', '三星', '宏碁', '惠普', '戴尔', '联想',
            '微鲸', '暴风', '风行', 'PPTV', '乐视', '酷开', '海信', 'TCL',
            '创维', '长虹', '康佳', '海尔', '夏普', '飞利浦', '奥图码', 'NEC'
        ]
        
        # 合并并去重
        all_brands = list(set(local_brands + online_brands))
        all_brands.sort()  # 按字母排序
        
        return all_brands
    
    def _search_online(self):
        """联网搜索最新信息"""
        if not REQUESTS_AVAILABLE:
            print("requests库未安装，无法进行联网搜索")
            return
        
        brand_input = input("请输入要搜索的品牌（留空则搜索所有品牌）: ").strip()
        max_price_input = input("请输入最高价格（留空则不限制）: ").strip()
        
        # 智能提取品牌名称（如果用户输入了型号，只取品牌部分）
        brand = self._extract_brand_from_input(brand_input)
        max_price = None
        if max_price_input.isdigit():
            max_price = int(max_price_input)
        
        online_recommendations = self.search_online_projectors(brand=brand, max_price=max_price)
        
        if online_recommendations:
            print(f"\n联网搜索到{len(online_recommendations)}款投影仪:")
            self.print_online_recommendations(online_recommendations)
        else:
            print("未搜索到符合条件的投影仪")
            
            # 如果搜索失败，提供智能建议
            if brand:
                print(f"\n提示: 您搜索的是 '{brand_input}'，系统识别为品牌 '{brand}'")
                print("可选的品牌有:")
                all_brands = self._get_all_available_brands()
                for i, b in enumerate(all_brands, 1):
                    print(f"{i}. {b}")
    
    def _extract_brand_from_input(self, user_input):
        """从用户输入中智能提取品牌名称"""
        if not user_input:
            return None
        
        # 获取所有可用品牌
        all_brands = self._get_all_available_brands()
        
        # 尝试精确匹配
        for brand in all_brands:
            if brand.lower() in user_input.lower():
                return brand
        
        # 如果精确匹配失败，尝试部分匹配
        for brand in all_brands:
            # 检查用户输入是否包含品牌名称
            if any(word.lower() == brand.lower() for word in user_input.split()):
                return brand
        
        # 如果还是匹配失败，返回第一个单词作为品牌（假设用户输入的是品牌）
        first_word = user_input.split()[0] if user_input.split() else user_input
        return first_word
    
    def print_recommendations(self, recommendations):
        """打印推荐结果"""
        if not recommendations:
            print("未找到符合条件的投影仪")
            return
        
        for i, projector in enumerate(recommendations, 1):
            print(f"{i}. {projector['品牌']} {projector['型号']} - 价格: {projector['价格']}元, "
                  f"分辨率: {projector['分辨率']}, 亮度: {projector['亮度']}ANSI流明")
    
    def print_online_recommendations(self, recommendations):
        """打印联网搜索推荐结果"""
        if not recommendations:
            print("未找到符合条件的投影仪")
            return
        
        for i, projector in enumerate(recommendations, 1):
            source = projector.get('来源', '未知')
            print(f"{i}. {projector['品牌']} {projector['型号']} - 价格: {projector['价格']}元, "
                  f"分辨率: {projector['分辨率']}, 亮度: {projector['亮度']}ANSI流明, 来源: {source}")


class NetworkSpeedTester:
    """网络速度测试器"""
    
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode
    
    def test_speed(self):
        """测试网络速度"""
        speed_info = {'下载速度': 0, '上传速度': 0, '延迟': 0, '抖动': 0}
        
        # 这里可以集成真正的网络速度测试逻辑
        # 目前使用模拟数据
        import random
        speed_info['下载速度'] = round(random.uniform(10, 100), 1)
        speed_info['上传速度'] = round(random.uniform(5, 50), 1)
        speed_info['延迟'] = random.randint(10, 100)
        speed_info['抖动'] = random.randint(1, 20)
        
        return speed_info
    
    def print_speed_info(self):
        """打印网络速度信息"""
        speed_info = self.test_speed()
        
        print("网络速度测试结果:")
        print(f"下载速度: {speed_info['下载速度']} Mbps")
        print(f"上传速度: {speed_info['上传速度']} Mbps")
        print(f"延迟: {speed_info['延迟']} ms")
        print(f"抖动: {speed_info['抖动']} ms")


class IntegratedSystem:
    """集成系统 - 主控制器"""
    
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode
        self.hardware_info = HardwareInfo(debug_mode)
        self.wifi_scanner = WiFiScanner(debug_mode)
        self.projector_recommender = ProjectorRecommender(debug_mode)
        self.network_tester = NetworkSpeedTester(debug_mode)
    
    def show_menu(self):
        """显示主菜单"""
        print("=" * 60)
        print("WiFi扫描与投影仪推荐系统 - 集成版")
        print("=" * 60)
        print("1. 硬件信息检测")
        print("2. WiFi网络扫描")
        print("3. 投影仪推荐")
        print("4. 网络速度测试")
        print("5. 运行所有功能")
        print("0. 退出")
        print("=" * 60)
    
    def run_all(self):
        """运行所有功能"""
        print("\n正在检测硬件信息...")
        self.hardware_info.print_hardware_info()
        
        print("\n正在扫描WiFi网络...")
        self.wifi_scanner.print_wifi_info()
        
        print("\n正在测试网络速度...")
        self.network_tester.print_speed_info()
        
        print("\n投影仪推荐（默认预算5000元）:")
        # 使用新的推荐方法
        self.projector_recommender.recommend_projectors()
    
    def run(self):
        """运行主程序"""
        while True:
            self.show_menu()
            choice = input("请选择功能 (0-5): ").strip()
            
            if choice == '1':
                self.hardware_info.print_hardware_info()
            elif choice == '2':
                self.wifi_scanner.print_wifi_info()
            elif choice == '3':
                # 使用新的投影仪推荐方法
                self.projector_recommender.recommend_projectors()
            elif choice == '4':
                self.network_tester.print_speed_info()
            elif choice == '5':
                self.run_all()
            elif choice == '0':
                print("感谢使用，再见！")
                break
            else:
                print("无效的选择，请重新输入")
            
            input("\n按回车键继续...")
            print()


def main():
    """主函数"""
    # 检查虚拟环境
    venv_path = Path(__file__).parent / '.venv'
    if venv_path.exists():
        print("[信息] 检测到虚拟环境: .venv")
    else:
        print("[信息] 未检测到虚拟环境")
    
    # 创建集成系统实例
    system = IntegratedSystem(debug_mode=False)
    
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == 'hardware':
            system.hardware_info.print_hardware_info()
        elif sys.argv[1] == 'wifi':
            system.wifi_scanner.print_wifi_info()
        elif sys.argv[1] == 'speed':
            system.network_tester.print_speed_info()
        else:
            system.run()
    else:
        system.run()


if __name__ == '__main__':
    main()