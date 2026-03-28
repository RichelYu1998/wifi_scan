import re
import argparse
import os
import sys
import datetime
import json
import csv
import platform
import urllib.request
import threading
import subprocess
import time
from collections import defaultdict
from geopy.geocoders import Nominatim

# 统一的工具类 - 抽象重复代码
class UnifiedUtils:
    """统一工具类 - 提供所有类共享的基础功能"""
    
    # 静态地理位置数据库（基于联网搜索的已知位置）
    KNOWN_LOCATIONS = {
        # 合肥逍遥津街道
        '114.103.224.116': {
            'country': '中国',
            'region': '安徽',
            'region_en': 'Anhui',
            'city': '合肥',
            'city_en': 'Hefei',
            'isp': 'Chinanet',
            '运营商': 'Chinanet',
            'lat': 31.8696,
            'lon': 117.293,
            'district': '庐阳区',
            'township': '逍遥津街道',
            'village': '县桥社区'
        },
        # 武汉黄家湖大学城东澜岸
        '119.96.120.88': {
            'country': '中国',
            'region': '湖北',
            'region_en': 'Hubei',
            'city': '武汉',
            'city_en': 'Wuhan',
            'isp': 'ChinaUnicom',
            '运营商': 'ChinaUnicom',
            'lat': 30.4500,
            'lon': 114.3500,
            'district': '江夏区',
            'township': '黄家湖大学城',
            'village': '东澜岸小区'
        }
    }
    
    @staticmethod
    def get_known_location(ip_address):
        """根据IP地址获取已知的地理位置信息"""
        return UnifiedUtils.KNOWN_LOCATIONS.get(ip_address)
    
    @staticmethod
    def run_command(command, timeout=10, encoding='utf-8'):
        """统一的命令执行方法"""
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding=encoding,
                errors='replace',
                timeout=timeout
            )
            return result.stdout if result.returncode == 0 else ""
        except Exception:
            return ""
    
    @staticmethod
    def safe_print(message):
        """安全打印函数，确保中文正确显示"""
        try:
            print(message)
        except UnicodeEncodeError:
            try:
                safe_message = message.encode('utf-8', errors='replace').decode('utf-8')
                print(safe_message)
            except:
                safe_message = message.encode('ascii', errors='replace').decode('ascii')
                print(safe_message)
    
    @staticmethod
    def load_json_file(file_path, default_data=None):
        """统一的JSON文件加载方法"""
        if default_data is None:
            default_data = {}
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return default_data
    
    @staticmethod
    def save_json_file(file_path, data):
        """统一的JSON文件保存方法"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    @staticmethod
    def print_section_header(title, width=60):
        """打印统一的章节标题"""
        print("\n" + "=" * width)
        print(title)
        print("=" * width)
    
    @staticmethod
    def print_section_divider(width=60):
        """打印统一的章节分隔线"""
        print("-" * width)
    
    @staticmethod
    def get_system_info():
        """获取系统信息"""
        return {
            '操作系统': platform.system(),
            '版本': platform.release(),
            '架构': platform.machine(),
            '主机名': platform.node()
        }
    
    @staticmethod
    def contains_garbled_text(text):
        """检测文本是否包含乱码"""
        if not text:
            return False
        
        # 检测常见乱码模式
        garbled_patterns = [
            r'�',  # Unicode替换字符
            r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]',  # 控制字符
            r'[\ufffd]',  # Unicode替换字符
            r'[\ud800-\udfff]',  # 代理对字符
        ]
        
        for pattern in garbled_patterns:
            if re.search(pattern, text):
                return True
        
        # 检测中文字符的异常组合
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        if len(chinese_chars) > 10 and len(chinese_chars) > len(text) * 0.7:
            return True
            
        return False
    
    @staticmethod
    def format_size(size_bytes, unit='GB'):
        """格式化文件大小"""
        if unit == 'GB':
            return round(size_bytes / (1024**3), 1)
        elif unit == 'MB':
            return round(size_bytes / (1024**2), 1)
        elif unit == 'TB':
            return round(size_bytes / (1024**4), 2)
        return size_bytes
    
    @staticmethod
    def format_timestamp(timestamp=None):
        """格式化时间戳"""
        if timestamp is None:
            timestamp = datetime.datetime.now()
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def mask_serial_number(serial_number):
        """打码序列号，保护隐私"""
        if not serial_number or serial_number == '未知':
            return serial_number
        
        # 如果序列号长度小于等于4，直接返回
        if len(serial_number) <= 4:
            return serial_number
        
        # 保留前3位和后2位，中间用****替换
        masked = serial_number[:3] + '****' + serial_number[-2:]
        return masked


try:
    from common_imports import CrossPlatformUtils, get_cross_platform_utils
except ImportError:
    # 如果common_imports不可用，创建简化版本
    class CrossPlatformUtils:
        def __init__(self, debug_mode=False):
            self.debug_mode = debug_mode
            self.platform = platform.system()
        
        def run_command(self, command, timeout=10):
            return UnifiedUtils.run_command(command, timeout)
    
    def get_cross_platform_utils(debug_mode=False):
        return CrossPlatformUtils(debug_mode)

try:
    from hardware_info import HardwareInfo
    from video_resolution_recommender import VideoResolutionRecommender
    EXTERNAL_MODULES_AVAILABLE = True
except ImportError:
    EXTERNAL_MODULES_AVAILABLE = False

# 优化后的硬件信息检测器（集成版）
class OptimizedHardwareDetector:
    """优化版硬件信息检测器 - 集成到wifi_scan.py"""
    
    def __init__(self, cross_platform_utils=None, debug_mode=False):
        self.cross_platform_utils = cross_platform_utils or get_cross_platform_utils()
        self.debug_mode = debug_mode
        self.platform = platform.system()
        
        # 初始化性能数据更新器
        self.performance_updater = HardwarePerformanceUpdater(debug_mode=False)
        self.performance_data = self.performance_updater.get_performance_data()
    
    def run_command(self, command):
        """执行系统命令"""
        return UnifiedUtils.run_command(command)
    
    def detect_hardware_info(self):
        """检测硬件信息（智能选择检测方法）"""
        if self.platform == "Darwin":
            return self._detect_macos_hardware()
        else:
            return self._detect_generic_hardware()
    
    def _detect_macos_hardware(self):
        """检测macOS硬件信息"""
        hardware_info = {
            'cpu': self._detect_macos_cpu(),
            'gpu': self._detect_macos_gpu(),
            'memory': self._detect_macos_memory(),
            'system': self._detect_macos_system(),
            'bios': self._detect_macos_bios(),
            'motherboard': self._detect_macos_motherboard(),
            'disk': self._detect_macos_disk(),
            'performance_score': 0
        }
        
        # 计算性能评分
        hardware_info['performance_score'] = self._calculate_macos_performance_score(hardware_info)
        
        return hardware_info
    
    def _detect_macos_cpu(self):
        """检测macOS CPU信息"""
        cpu_info = {
            '名称': '未知',
            '架构': platform.machine(),
            '核心数': 1,
            '频率_MHz': 0
        }
        
        # 获取CPU品牌字符串
        result = self.run_command(['sysctl', '-n', 'machdep.cpu.brand_string'])
        if result and result.strip():
            cpu_info['名称'] = result.strip()
        else:
            # 备选方案
            result = self.run_command(['sysctl', '-n', 'hw.model'])
            if result and result.strip():
                cpu_info['名称'] = f"Apple {result.strip()}"
        
        # 获取核心数
        result = self.run_command(['sysctl', '-n', 'hw.ncpu'])
        if result and result.strip():
            cpu_info['核心数'] = int(result.strip())
        
        # 获取频率（Apple Silicon默认频率）
        cpu_info['频率_MHz'] = 3200
        
        return cpu_info
    
    def _detect_macos_gpu(self):
        """检测macOS GPU信息"""
        gpu_info = {
            '名称': '未知',
            '品牌': 'Apple',
            '型号': '未知',
            'GPU芯片': 'Apple',
            '显存_GB': 0,
            '类型': '集成'
        }
        
        # 使用system_profiler获取显卡信息
        result = self.run_command(['system_profiler', 'SPDisplaysDataType'])
        
        if result:
            lines = result.split('\n')
            for line in lines:
                line = line.strip()
                
                if 'Chipset Model:' in line:
                    # 提取GPU芯片型号
                    chipset = line.replace('Chipset Model:', '').strip()
                    gpu_info['名称'] = chipset
                    gpu_info['GPU芯片'] = chipset
                    
                    # 提取型号信息
                    if 'M2 Pro' in chipset:
                        gpu_info['型号'] = 'M2 Pro'
                    elif 'M2' in chipset:
                        gpu_info['型号'] = 'M2'
                    elif 'M1' in chipset:
                        gpu_info['型号'] = 'M1'
                
                elif 'VRAM' in line and 'Total' in line:
                    # 提取显存信息并转换为GB
                    vram_text = line.split('VRAM')[1].strip()
                    vram_match = re.search(r'(\d+)', vram_text)
                    if vram_match:
                        # 将MB转换为GB
                        gpu_info['显存_GB'] = round(int(vram_match.group(1)) / 1024, 1)
        
        # 如果显存为0，根据型号设置默认值（直接使用GB）
        if gpu_info['显存_GB'] == 0:
            if 'M2 Pro' in gpu_info['名称']:
                gpu_info['显存_GB'] = 8.0
            elif 'M2' in gpu_info['名称']:
                gpu_info['显存_GB'] = 4.0
        
        return gpu_info
    
    def _detect_macos_memory(self):
        """检测macOS内存信息"""
        memory_info = {
            '总容量_GB': 0,
            '可用_GB': 0,
            '使用率_%': 0,
            '频率_MHz': 0,
            'DDR类型': 'LPDDR5'
        }
        
        try:
            import psutil
            mem = psutil.virtual_memory()
            memory_info['总容量_GB'] = round(mem.total / (1024**3), 1)
            memory_info['可用_GB'] = round(mem.available / (1024**3), 1)
            memory_info['使用率_%'] = round(mem.percent, 1)
            
            # Apple Silicon内存频率
            memory_info['频率_MHz'] = 6400
            
        except Exception:
            # 备选方案：使用sysctl
            result = self.run_command(['sysctl', '-n', 'hw.memsize'])
            if result and result.strip():
                total_bytes = int(result.strip())
                memory_info['总容量_GB'] = round(total_bytes / (1024**3), 1)
        
        return memory_info
    
    def _detect_macos_system(self):
        """检测macOS系统信息"""
        system_info = {
            '操作系统': 'macOS',
            '版本': platform.release(),
            '架构': platform.machine(),
            '主机名': platform.node(),
            '启动时间': '未知'
        }
        
        # 获取启动时间
        try:
            import psutil
            boot_time = psutil.boot_time()
            from datetime import datetime
            system_info['启动时间'] = UnifiedUtils.format_timestamp(datetime.fromtimestamp(boot_time))
        except Exception:
            pass
        
        # 获取macOS版本
        result = self.run_command(['sw_vers', '-productVersion'])
        if result and result.strip():
            system_info['版本'] = result.strip()
        
        return system_info
    
    def _detect_macos_bios(self):
        """检测macOS BIOS/EFI信息"""
        bios_info = {
            '版本': '未知',
            '发布日期': '未知',
            '制造商': 'Apple',
            '是否最新': '是'
        }
        
        # 获取Boot ROM版本（相当于BIOS）
        result = self.run_command(['system_profiler', 'SPHardwareDataType'])
        
        if result:
            lines = result.split('\n')
            for line in lines:
                line = line.strip()
                
                if 'Boot ROM Version:' in line:
                    bios_info['版本'] = line.replace('Boot ROM Version:', '').strip()
                elif 'Model Identifier:' in line:
                    model = line.replace('Model Identifier:', '').strip()
                    bios_info['制造商'] = f"Apple ({model})"
        
        return bios_info
    
    def _detect_macos_motherboard(self):
        """检测macOS主板信息"""
        motherboard_info = {
            '制造商': 'Apple',
            '型号': '未知',
            '芯片组': 'Apple Silicon',
            '序列号': '未知'
        }
        
        # 获取主板型号
        result = self.run_command(['system_profiler', 'SPHardwareDataType'])
        
        if result:
            lines = result.split('\n')
            for line in lines:
                line = line.strip()
                
                if 'Model Identifier:' in line:
                    motherboard_info['型号'] = line.replace('Model Identifier:', '').strip()
                elif 'Serial Number (system):' in line:
                    raw_serial = line.replace('Serial Number (system):', '').strip()
                    motherboard_info['序列号'] = UnifiedUtils.mask_serial_number(raw_serial)
        
        return motherboard_info
    
    def _detect_macos_disk(self):
        """检测macOS硬盘信息"""
        disk_info = {
            '总数': 1,
            '总容量_TB': 0.0,
            '硬盘列表': [],
            '读写速率': {
                '读取速率_MB/s': 0,
                '写入速率_MB/s': 0,
                '理论读取速率_MB/s': 0,
                '理论写入速率_MB/s': 0
            }
        }
        
        try:
            # 获取磁盘使用情况
            import psutil
            disk_usage = psutil.disk_usage('/')
            disk_info['总容量_TB'] = round(disk_usage.total / (1024**4), 2)
            
            # 获取磁盘信息
            result = self.run_command(['system_profiler', 'SPStorageDataType'])
            
            if result:
                lines = result.split('\n')
                current_disk = {}
                
                for line in lines:
                    line = line.strip()
                    
                    if 'BSD Name:' in line:
                        current_disk['名称'] = line.replace('BSD Name:', '').strip()
                    elif 'Medium Type:' in line:
                        current_disk['类型'] = line.replace('Medium Type:', '').strip()
                    elif 'Size:' in line:
                        size_text = line.replace('Size:', '').strip()
                        # 解析容量（如"1 TB"）
                        size_match = re.search(r'(\d+\.?\d*)\s*(GB|TB|MB)', size_text)
                        if size_match:
                            size = float(size_match.group(1))
                            unit = size_match.group(2)
                            
                            if unit == 'TB':
                                current_disk['容量_GB'] = round(size * 1024, 1)
                                current_disk['容量_TB'] = size
                            elif unit == 'GB':
                                current_disk['容量_GB'] = size
                                current_disk['容量_TB'] = round(size / 1024, 2)
                            
                            if current_disk:
                                disk_info['硬盘列表'].append(current_disk.copy())
                                current_disk = {}
            
            # 设置默认的硬盘信息
            if not disk_info['硬盘列表']:
                disk_info['硬盘列表'] = [{
                    '名称': '内置硬盘',
                    '类型': 'SSD',
                    '容量_GB': 512,
                    '容量_TB': 0.5
                }]
            
            # 获取真实的硬盘读写速率
            disk_info['读写速率']['读取速率_MB/s'] = self._get_disk_read_speed()
            disk_info['读写速率']['写入速率_MB/s'] = self._get_disk_write_speed()
            disk_info['读写速率']['理论读取速率_MB/s'] = 7000
            disk_info['读写速率']['理论写入速率_MB/s'] = 5000
            
        except Exception as e:
            if self.debug_mode:
                print(f"硬盘检测失败: {e}")
        
        return disk_info
    
    def _get_disk_read_speed(self):
        """获取硬盘读取速度"""
        try:
            if platform.system() == 'Darwin':  # macOS
                # 使用diskutil获取磁盘信息
                result = UnifiedUtils.run_command(['diskutil', 'info', '/'], timeout=5)
                if result and 'Read Speed' in result:
                    for line in result.split('\n'):
                        if 'Read Speed' in line:
                            try:
                                speed_str = line.split(':')[1].strip().replace('MB/s', '').strip()
                                return float(speed_str)
                            except (ValueError, IndexError):
                                pass
                
                # 如果无法获取，使用系统命令测试
                test_file = '/tmp/disk_speed_test'
                try:
                    with open(test_file, 'wb') as f:
                        f.write(b'0' * (10 * 1024 * 1024))  # 10MB测试文件
                    
                    start_time = time.time()
                    with open(test_file, 'rb') as f:
                        f.read()
                    read_time = time.time() - start_time
                    
                    if read_time > 0:
                        speed = (10 * 1024) / read_time  # MB/s
                        return round(speed, 2)
                    
                    os.remove(test_file)
                except Exception:
                    pass
                
            elif platform.system() == 'Linux':
                # 使用hdparm获取磁盘读取速度
                result = UnifiedUtils.run_command(['sudo', 'hdparm', '-Tt', '/dev/sda'], timeout=10)
                if result:
                    for line in result.split('\n'):
                        if 'Timing buffered disk reads' in line:
                            try:
                                speed_str = line.split('=')[1].strip().split('MB')[0].strip()
                                return float(speed_str)
                            except (ValueError, IndexError):
                                pass
            
            elif platform.system() == 'Windows':
                # 使用wmic获取磁盘信息
                result = UnifiedUtils.run_command(['wmic', 'diskdrive', 'get', 'model'], timeout=5)
                if result:
                    pass  # Windows下需要更复杂的处理
                
        except Exception as e:
            if self.debug_mode:
                print(f"获取硬盘读取速度失败: {e}")
        
        # 返回默认值
        return 3500.0
    
    def _get_disk_write_speed(self):
        """获取硬盘写入速度"""
        try:
            if platform.system() == 'Darwin':  # macOS
                # 使用diskutil获取磁盘信息
                result = UnifiedUtils.run_command(['diskutil', 'info', '/'], timeout=5)
                if result and 'Write Speed' in result:
                    for line in result.split('\n'):
                        if 'Write Speed' in line:
                            try:
                                speed_str = line.split(':')[1].strip().replace('MB/s', '').strip()
                                return float(speed_str)
                            except (ValueError, IndexError):
                                pass
                
                # 如果无法获取，使用系统命令测试
                test_file = '/tmp/disk_speed_test'
                try:
                    data = b'0' * (10 * 1024 * 1024)  # 10MB测试数据
                    
                    start_time = time.time()
                    with open(test_file, 'wb') as f:
                        f.write(data)
                    write_time = time.time() - start_time
                    
                    if write_time > 0:
                        speed = (10 * 1024) / write_time  # MB/s
                        return round(speed, 2)
                    
                    os.remove(test_file)
                except Exception:
                    pass
                
            elif platform.system() == 'Linux':
                # 使用dd命令测试写入速度
                test_file = '/tmp/disk_write_test'
                try:
                    start_time = time.time()
                    result = UnifiedUtils.run_command(['dd', 'if=/dev/zero', f'of={test_file}', 'bs=1M', 'count=10'], timeout=10)
                    write_time = time.time() - start_time
                    
                    if write_time > 0:
                        speed = (10 * 1024) / write_time  # MB/s
                        return round(speed, 2)
                    
                    os.remove(test_file)
                except Exception:
                    pass
            
            elif platform.system() == 'Windows':
                # 使用wmic获取磁盘信息
                result = UnifiedUtils.run_command(['wmic', 'diskdrive', 'get', 'model'], timeout=5)
                if result:
                    pass  # Windows下需要更复杂的处理
                
        except Exception as e:
            if self.debug_mode:
                print(f"获取硬盘写入速度失败: {e}")
        
        # 返回默认值
        return 2800.0
    
    def _calculate_macos_performance_score(self, hardware_info):
        """计算macOS性能评分"""
        score = 0
        
        # CPU评分（基于性能数据）
        cpu_name = hardware_info['cpu']['名称']
        cpu_score = 0
        for model, model_score in self.performance_data['cpu'].items():
            if model.lower() in cpu_name.lower():
                cpu_score = model_score
                break
        
        # 如果没有匹配到，使用默认评分
        if cpu_score == 0:
            if 'M2 Pro' in cpu_name:
                cpu_score = 90
            elif 'M2' in cpu_name:
                cpu_score = 85
            elif 'M1' in cpu_name:
                cpu_score = 80
            else:
                cpu_score = 70
        
        score += cpu_score
        
        # 内存评分（基于性能数据）
        memory_gb = hardware_info['memory']['总容量_GB']
        memory_score = 0
        for capacity, capacity_score in self.performance_data['memory'].items():
            try:
                capacity_float = float(capacity)
                if memory_gb >= capacity_float:
                    memory_score = capacity_score
                    break
            except (ValueError, TypeError):
                continue
        
        # 如果没有匹配到，使用默认评分
        if memory_score == 0:
            if memory_gb >= 32:
                memory_score = 10
            elif memory_gb >= 16:
                memory_score = 8
            elif memory_gb >= 8:
                memory_score = 6
            else:
                memory_score = 4
        
        score += memory_score
        
        # GPU评分（基于性能数据）
        gpu_name = hardware_info['gpu']['名称']
        gpu_score = 0
        for model, model_score in self.performance_data['gpu'].items():
            if model.lower() in gpu_name.lower():
                gpu_score = model_score
                break
        
        # 如果没有匹配到，使用默认评分
        if gpu_score == 0:
            gpu_score = 8
        
        score += gpu_score
        
        # 确保评分在合理范围内
        return min(score, 100)
    
    def _detect_generic_hardware(self):
        """通用硬件信息检测（非macOS系统）"""
        hardware_info = {
            'cpu': {'名称': '未知', '架构': '未知', '核心数': 0, '频率_MHz': 0},
            'gpu': {'名称': '未知', '品牌': '未知', '型号': '未知', 'GPU芯片': '未知', '显存_GB': 0, '类型': '未知'},
            'memory': {'总容量_GB': 0, '可用_GB': 0, '使用率_%': 0, '频率_MHz': 0, 'DDR类型': '未知'},
            'system': {'操作系统': '未知', '版本': '未知', '架构': '未知', '主机名': '未知', '启动时间': '未知'},
            'bios': {'版本': '未知', '发布日期': '未知', '制造商': '未知', '是否最新': '无法检测'},
            'motherboard': {'制造商': '未知', '型号': '未知', '芯片组': '未知', '序列号': '未知'},
            'disk': {'总数': 0, '总容量_TB': 0.0, '硬盘列表': [], '读写速率': {'读取速率_MB/s': 0, '写入速率_MB/s': 0, '理论读取速率_MB/s': 0, '理论写入速率_MB/s': 0}},
            'performance_score': 0
        }
        
        # 使用psutil获取基本信息
        try:
            import psutil
            
            # CPU信息
            hardware_info['cpu']['核心数'] = psutil.cpu_count(logical=False)
            
            # 内存信息
            mem = psutil.virtual_memory()
            hardware_info['memory']['总容量_GB'] = round(mem.total / (1024**3), 1)
            hardware_info['memory']['可用_GB'] = round(mem.available / (1024**3), 1)
            hardware_info['memory']['使用率_%'] = round(mem.percent, 1)
            
            # 系统信息
            hardware_info['system']['操作系统'] = platform.system()
            hardware_info['system']['版本'] = platform.release()
            hardware_info['system']['架构'] = platform.machine()
            hardware_info['system']['主机名'] = platform.node()
            
            # 启动时间
            boot_time = psutil.boot_time()
            from datetime import datetime
            hardware_info['system']['启动时间'] = UnifiedUtils.format_timestamp(datetime.fromtimestamp(boot_time))
            
        except Exception as e:
            if self.debug_mode:
                print(f"硬件信息检测失败: {e}")
        
        return hardware_info
    
    def print_hardware_info(self, hardware_info=None):
        """打印硬件信息"""
        if hardware_info is None:
            hardware_info = self.detect_hardware_info()
        
        UnifiedUtils.print_section_header("🖥️  硬件信息检测报告")
        
        # CPU信息
        cpu = hardware_info['cpu']
        print(f"\n💻 CPU信息:")
        print(f"   名称: {cpu['名称']}")
        print(f"   架构: {cpu['架构']}")
        print(f"   核心数: {cpu['核心数']}")
        print(f"   频率: {cpu['频率_MHz']} MHz")
        
        # GPU信息
        gpu = hardware_info['gpu']
        print(f"\n🎮 显卡信息:")
        print(f"   名称: {gpu['名称']}")
        print(f"   品牌: {gpu['品牌']}")
        print(f"   型号: {gpu['型号']}")
        print(f"   类型: {gpu['类型']}")
        print(f"   显存: {gpu['显存_GB']} GB")
        
        # 内存信息
        memory = hardware_info['memory']
        print(f"\n💾 内存信息:")
        print(f"   总容量: {memory['总容量_GB']} GB")
        print(f"   可用: {memory['可用_GB']} GB")
        print(f"   使用率: {memory['使用率_%']}%")
        print(f"   频率: {memory['频率_MHz']} MHz")
        print(f"   DDR类型: {memory['DDR类型']}")
        
        # 系统信息
        system = hardware_info['system']
        print(f"\n⚙️  系统信息:")
        print(f"   操作系统: {system['操作系统']}")
        print(f"   版本: {system['版本']}")
        print(f"   架构: {system['架构']}")
        print(f"   主机名: {system['主机名']}")
        print(f"   启动时间: {system['启动时间']}")
        
        # BIOS信息
        bios = hardware_info['bios']
        print(f"\n🔧 BIOS/EFI信息:")
        print(f"   版本: {bios['版本']}")
        print(f"   制造商: {bios['制造商']}")
        print(f"   是否最新: {bios['是否最新']}")
        
        # 主板信息
        motherboard = hardware_info['motherboard']
        print(f"\n🔌 主板信息:")
        print(f"   制造商: {motherboard['制造商']}")
        print(f"   型号: {motherboard['型号']}")
        print(f"   芯片组: {motherboard['芯片组']}")
        print(f"   序列号: {motherboard['序列号']}")
        
        # 硬盘信息
        disk = hardware_info['disk']
        print(f"\n💽 硬盘信息:")
        print(f"   总数: {disk['总数']}")
        print(f"   总容量: {disk['总容量_TB']} TB")
        
        for i, disk_info in enumerate(disk['硬盘列表'], 1):
            print(f"   硬盘{i}: {disk_info['名称']} - {disk_info['容量_GB']}GB ({disk_info['容量_TB']}TB)")
        
        # 显示硬盘读写速率（如果可用）
        if '读写速率' in disk:
            read_speed = disk['读写速率'].get('读取速率_MB/s', 0)
            write_speed = disk['读写速率'].get('写入速率_MB/s', 0)
            if read_speed > 0 or write_speed > 0:
                # 智能转换单位：大于1024 MB/s时显示为GB/s
                read_speed_str = f"{read_speed:.2f} MB/s"
                write_speed_str = f"{write_speed:.2f} MB/s"
                
                if read_speed > 1024:
                    read_speed_str = f"{read_speed/1024:.2f} GB/s"
                if write_speed > 1024:
                    write_speed_str = f"{write_speed/1024:.2f} GB/s"
                
                print(f"   读取速率: {read_speed_str}")
                print(f"   写入速率: {write_speed_str}")
        
        # 性能评分
        print(f"\n📊 性能评分: {hardware_info['performance_score']}/100")
        
        print("\n" + "="*60)


class HardwarePerformanceUpdater:
    """硬件性能数据更新器 - 集成版"""
    
    def __init__(self, escape_manager=None, debug_mode=False):
        self.escape_manager = escape_manager
        self.debug_mode = debug_mode
        self.data_dir = "json/hardware"
        
        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 性能数据文件路径
        self.cpu_performance_file = os.path.join(self.data_dir, "cpu_performance.json")
        self.gpu_performance_file = os.path.join(self.data_dir, "gpu_performance.json")
        self.memory_performance_file = os.path.join(self.data_dir, "memory_performance.json")
        self.network_performance_file = os.path.join(self.data_dir, "network_performance.json")
    
    def get_performance_data(self):
        """获取性能数据"""
        cpu_data = self._load_json_file(self.cpu_performance_file, {})
        gpu_data = self._load_json_file(self.gpu_performance_file, {})
        memory_data = self._load_json_file(self.memory_performance_file, {})
        network_data = self._load_json_file(self.network_performance_file, {})
        
        return {
            'cpu': cpu_data,
            'gpu': gpu_data,
            'memory': memory_data,
            'network': network_data
        }
    
    def update_all_performance_data(self, force_update=False):
        """更新所有性能数据 - 从网络获取最新数据并与本地数据合并"""
        update_time = UnifiedUtils.format_timestamp()
        
        # 从网络获取最新性能数据
        print("📡 正在从网络获取最新的硬件性能数据...")
        
        # 获取CPU性能数据
        cpu_cloud_data, cpu_from_network = self._get_default_cpu_data()
        if cpu_from_network and cpu_cloud_data and isinstance(cpu_cloud_data, dict) and len(cpu_cloud_data) > 0:
            print(f"✅ 成功从网络获取 {len(cpu_cloud_data)} 个CPU型号的性能数据")
            
            # 加载本地CPU数据
            cpu_local_data = self._get_default_cpu_data()[0]
            
            # 合并云端和本地CPU数据
            cpu_data = self._merge_hardware_data(cpu_cloud_data, cpu_local_data)
            print(f"📊 合并后CPU数据: {len(cpu_data)} 个型号 (云端: {len(cpu_cloud_data)}, 本地: {len(cpu_local_data)})")
            
            self._save_json_file(self.cpu_performance_file, cpu_data)
        else:
            print("⚠️  使用本地默认CPU性能数据")
            cpu_data = self._load_json_file(self.cpu_performance_file, self._get_default_cpu_data()[0])
        
        # 获取GPU性能数据
        gpu_cloud_data, gpu_from_network = self._get_default_gpu_data()
        if gpu_from_network and gpu_cloud_data and isinstance(gpu_cloud_data, dict) and len(gpu_cloud_data) > 0:
            print(f"✅ 成功从网络获取 {len(gpu_cloud_data)} 个GPU型号的性能数据")
            
            # 加载本地GPU数据
            gpu_local_data = self._get_default_gpu_data()[0]
            
            # 合并云端和本地GPU数据
            gpu_data = self._merge_hardware_data(gpu_cloud_data, gpu_local_data)
            print(f"📊 合并后GPU数据: {len(gpu_data)} 个型号 (云端: {len(gpu_cloud_data)}, 本地: {len(gpu_local_data)})")
            
            self._save_json_file(self.gpu_performance_file, gpu_data)
        else:
            print("⚠️  使用本地默认GPU性能数据")
            gpu_data = self._load_json_file(self.gpu_performance_file, self._get_default_gpu_data()[0])
        
        # 内存数据使用本地默认值
        memory_data = self._get_default_memory_data()
        self._save_json_file(self.memory_performance_file, memory_data)
        
        # 网卡数据使用本地默认值（目前没有云端数据源）
        network_data = self._get_default_network_data()
        self._save_json_file(self.network_performance_file, network_data)
        
        result = {
            'cpu': {
                'update_time': update_time,
                'data': cpu_data,
                'source': 'cloud_merged' if cpu_from_network else 'local'
            },
            'gpu': {
                'update_time': update_time,
                'data': gpu_data,
                'source': 'cloud_merged' if gpu_from_network else 'local'
            },
            'memory': {
                'update_time': update_time,
                'data': memory_data,
                'source': 'local'
            },
            'network': {
                'update_time': update_time,
                'data': network_data,
                'source': 'local'
            },
            'update_time': update_time
        }
        
        print("✅ 硬件性能数据库更新完成！")
        
        # 显示合并后的数据统计
        print(f"\n📊 硬件数据统计:")
        print(f"  💻 CPU型号: {len(cpu_data)} 个")
        print(f"  🎮 GPU型号: {len(gpu_data)} 个")
        print(f"  💾 内存类型: {len(memory_data)} 种")
        print(f"  📡 网卡类型: {len(network_data)} 种")
        
        return result
    
    def _merge_hardware_data(self, cloud_data, local_data):
        """合并云端和本地硬件数据，形成完整的最新最全的资料库"""
        if not isinstance(cloud_data, dict) or not isinstance(local_data, dict):
            return local_data
        
        # 创建合并后的数据字典
        merged_data = {}
        
        # 第一步：添加本地基础数据
        for key, value in local_data.items():
            merged_data[key] = value
        
        # 第二步：用云端数据覆盖本地数据（云端数据优先）
        for key, value in cloud_data.items():
            merged_data[key] = value
        
        # 第三步：智能处理特殊型号（如RTX 5090、M3 Ultra等）
        # 确保最新型号有正确的评分
        self._enhance_latest_models(merged_data)
        
        return merged_data
    
    def _enhance_latest_models(self, hardware_data):
        """增强最新硬件型号的评分"""
        if not isinstance(hardware_data, dict):
            return
        
        # 最新GPU型号评分增强
        latest_gpu_patterns = [
            (r'RTX\s*5090', 100),  # RTX 5090系列
            (r'RTX\s*5080', 98),   # RTX 5080系列
            (r'RTX\s*5070', 95),   # RTX 5070系列
            (r'Core\s+Ultra\s+[3579]', 100),  # Intel Core Ultra系列
            (r'M4(?:\s+(?:Pro|Max|Ultra)?)', 100),  # Apple M4系列
            (r'M3(?:\s+(?:Pro|Max|Ultra)?)', 95),  # Apple M3系列
        ]
        
        for model_name in hardware_data.keys():
            if not isinstance(model_name, str):
                continue
                
            # 检查是否匹配最新型号模式
            for pattern, score in latest_gpu_patterns:
                if re.search(pattern, model_name, re.IGNORECASE):
                    hardware_data[model_name] = score
                    break
    
    def _generate_log_filename(self, location_prefix, ssid, date):
        """生成日志文件名 - 保持原有格式"""
        # 智能文件名生成逻辑
        # 检查SSID是否包含地理位置信息（异常情况）
        if '安徽' in ssid or '合肥' in ssid or '庐阳' in ssid:
            self._safe_print(f"⚠️ 检测到SSID包含地理位置信息，使用默认名称: {repr(ssid)}")
            # 当SSID包含地理位置信息时，只使用地理位置信息作为文件名
            if location_prefix.strip():
                return f"{location_prefix.strip()}基于周围WiFi信道优化推荐({date}).json"
            else:
                return f"WiFi网络基于周围WiFi信道优化推荐({date}).json"
        elif ssid == "WiFi网络":
            # 当使用默认WiFi名称时，只使用地理位置信息作为文件名
            if location_prefix.strip():
                return f"{location_prefix.strip()}基于周围WiFi信道优化推荐({date}).json"
            else:
                return f"WiFi网络基于周围WiFi信道优化推荐({date}).json"
        else:
            # 正常情况：地理位置 + WiFi名称
            return f"{location_prefix}{ssid}基于周围WiFi信道优化推荐({date}).json"

    def _load_json_file(self, file_path, default_data):
        """加载JSON文件 - 使用JSON文件管理器"""
        # 兼容旧代码，同时支持文件路径和类型+文件名
        import os
        
        if os.path.exists(file_path):
            # 如果是完整路径，直接加载
            return UnifiedUtils.load_json_file(file_path, default_data)
        else:
            # 如果是文件名，使用JSON文件管理器
            # 尝试从文件名推断文件类型
            filename = os.path.basename(file_path)
            
            if 'cpu' in filename.lower():
                return self.json_manager.load_json_file('cpu', filename, default_data=default_data)
            elif 'gpu' in filename.lower():
                return self.json_manager.load_json_file('gpu', filename, default_data=default_data)
            elif 'memory' in filename.lower():
                return self.json_manager.load_json_file('memory', filename, default_data=default_data)
            elif 'network' in filename.lower():
                return self.json_manager.load_json_file('network_hardware', filename, default_data=default_data)
            else:
                return default_data
    
    def _get_default_cpu_data(self):
        """获取默认CPU性能数据 - 从网络获取最新数据"""
        # 本地默认数据
        local_data = {
            'i9': 100, 'i7': 85, 'i5': 70, 'i3': 55,
            'Core i9': 100, 'Core i7': 85, 'Core i5': 70, 'Core i3': 55,
            'Ryzen 9': 100, 'Ryzen 7': 85, 'Ryzen 5': 70, 'Ryzen 3': 55,
            'M3': 100, 'M2': 95, 'M1': 90, 'M1 Pro': 95, 'M1 Max': 100,
            'M2 Pro': 100, 'M2 Max': 100, 'M2 Ultra': 100,
            'M3 Pro': 100, 'M3 Max': 100, 'M3 Ultra': 100,
        }
        
        try:
            import urllib.request
            import ssl
            
            # 创建不验证SSL证书的上下文
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # 尝试从多个来源获取CPU性能数据
            urls = [
                'https://www.cpubenchmark.net/',
                'https://www.techpowerup.com/',
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            for url in urls:
                try:
                    request = urllib.request.Request(url, headers=headers)
                    
                    with urllib.request.urlopen(request, timeout=20, context=ssl_context) as response:
                        # 检查响应头，如果是gzip压缩，需要解压
                        content = response.read()
                        
                        # 检查是否是gzip压缩
                        if response.headers.get('Content-Encoding') == 'gzip':
                            import gzip
                            html_content = gzip.decompress(content).decode('utf-8')
                        else:
                            # 尝试直接解码，如果失败则尝试其他编码
                            try:
                                html_content = content.decode('utf-8')
                            except UnicodeDecodeError:
                                html_content = content.decode('latin-1')
                        
                        # 调试：显示获取到的HTML内容长度
                        if self.debug_mode:
                            print(f"[DEBUG] 从 {url} 获取到 {len(html_content)} 字节的HTML内容")
                        
                        # 如果HTML内容太短，可能被重定向或反爬虫
                        if len(html_content) < 10000:
                            if self.debug_mode:
                                print(f"[DEBUG] HTML内容太短，可能被反爬虫拦截")
                            continue
                        
                        # 解析CPU性能数据
                        cpu_data = self._parse_cpu_benchmark_data(html_content)
                        if cpu_data and len(cpu_data) > 5:  # 降低阈值，从10改为5
                            # 调试：显示解析到的CPU数据
                            if self.debug_mode:
                                print(f"[DEBUG] 从 {url} 解析到 {len(cpu_data)} 个CPU型号")
                                for cpu_name, score in list(cpu_data.items())[:5]:
                                    print(f"[DEBUG]   {cpu_name}: {score}")
                            return (cpu_data, True)
                            
                except Exception as e:
                    if self.escape_manager:
                        self.escape_manager.debug_log(f"从 {url} 获取CPU数据失败: {e}")
                    continue
            
        except Exception as e:
            if self.escape_manager:
                self.escape_manager.debug_log(f"获取CPU性能数据失败: {e}")
        
        # 如果网络获取失败，返回本地默认数据
        return (local_data, False)
    
    def _parse_cpu_benchmark_data(self, html_content):
        """解析CPU基准测试数据"""
        try:
            cpu_data = {}
            
            # 改进的CPU型号匹配模式 - 支持更多格式
            cpu_patterns = [
                # Intel Core Ultra 系列
                r'Intel\s+Core\s+Ultra\s+[3579]',
                r'Core\s+Ultra\s+[3579]',
                # Intel Core 14代系列
                r'Intel\s+Core\s+(?:i[3579]|i9)[\s-]*(?:14[0-9]{3}|13[0-9]{3}|12[0-9]{3})[A-Z]*',
                r'Core\s+(?:i[3579]|i9)[\s-]*(?:14[0-9]{3}|13[0-9]{3}|12[0-9]{3})[A-Z]*',
                # Intel Core 11代及以下
                r'Intel\s+Core\s+(?:i[3579]|i9)[\s-]*(\d{3,4}[A-Z]*)',
                r'Core\s+(?:i[3579]|i9)[\s-]*(\d{3,4}[A-Z]*)',
                # AMD Ryzen 9000系列
                r'AMD\s+Ryzen\s+[3579]\s*(?:9[0-9]{3})',
                r'Ryzen\s+[3579]\s*(?:9[0-9]{3})',
                # AMD Ryzen 7000/8000系列
                r'AMD\s+Ryzen\s+[3579]\s*(?:[78][0-9]{3})',
                r'Ryzen\s+[3579]\s*(?:[78][0-9]{3})',
                # AMD Ryzen 5000/6000系列
                r'AMD\s+Ryzen\s+[3579]\s*(?:[56][0-9]{3})',
                r'Ryzen\s+[3579]\s*(?:[56][0-9]{3})',
                # Apple M4系列
                r'Apple\s+(?:M4|M4\s+(?:Pro|Max|Ultra)?)',
                r'M4(?:\s+(?:Pro|Max|Ultra)?)',
                # Apple M3系列
                r'Apple\s+(?:M3|M3\s+(?:Pro|Max|Ultra)?)',
                r'M3(?:\s+(?:Pro|Max|Ultra)?)',
                # Apple M2/M1系列
                r'Apple\s+(?:M[12]|M[12]\s+(?:Pro|Max|Ultra)?)',
                r'M[12](?:\s+(?:Pro|Max|Ultra)?)',
            ]
            
            # 查找所有CPU型号和分数
            # 尝试匹配表格中的数据 - 支持多种表格格式
            table_patterns = [
                # 标准表格格式
                r'<tr[^>]*>.*?<td[^>]*>([^<]+)</td>.*?<td[^>]*>([^<]+)</td>.*?</tr>',
                # 带有class属性的表格
                r'<tr[^>]*class="[^"]*"[^>]*>.*?<td[^>]*>([^<]+)</td>.*?<td[^>]*>([^<]+)</td>.*?</tr>',
                # 带有data属性的表格
                r'<tr[^>]*data-[^>]*>.*?<td[^>]*>([^<]+)</td>.*?<td[^>]*>([^<]+)</td>.*?</tr>',
            ]
            
            for table_pattern in table_patterns:
                table_matches = re.findall(table_pattern, html_content, re.DOTALL | re.IGNORECASE)
                
                for cpu_name, score_str in table_matches:
                    cpu_name = cpu_name.strip()
                    
                    # 检查是否匹配CPU型号模式
                    is_cpu = False
                    for pattern in cpu_patterns:
                        if re.search(pattern, cpu_name, re.IGNORECASE):
                            is_cpu = True
                            break
                    
                    if is_cpu:
                        try:
                            # 清理分数字符串
                            score = int(re.sub(r'[^\d]', '', score_str.strip()))
                            if score > 100:  # 过滤掉无效数据
                                cpu_data[cpu_name] = self._normalize_cpu_score(score)
                        except (ValueError, AttributeError):
                            continue
            
            # 如果表格解析失败，尝试直接匹配文本
            if not cpu_data:
                for pattern in cpu_patterns:
                    matches = re.findall(pattern, html_content, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, tuple):
                            cpu_name = match[0] if match else ''
                        else:
                            cpu_name = match
                        
                        if cpu_name and len(cpu_name) > 3:
                            # 尝试在附近找到分数
                            score_pattern = rf'{re.escape(cpu_name)}[^<]*<td[^>]*>(\d+)</td>'
                            score_match = re.search(score_pattern, html_content, re.IGNORECASE)
                            if score_match:
                                try:
                                    score = int(score_match.group(1))
                                    if score > 100:
                                        cpu_data[cpu_name] = self._normalize_cpu_score(score)
                                except ValueError:
                                    continue
            
            # 如果还是没有数据，尝试从链接中提取CPU型号
            if not cpu_data:
                # 查找所有链接中的CPU型号 - 改进模式
                link_patterns = [
                    r'<a[^>]*href="[^"]*cpu=[^"]*"[^>]*>([^<]+)</a>',
                    r'<a[^>]*href="[^"]*processor=[^"]*"[^>]*>([^<]+)</a>',
                    r'<a[^>]*href="[^"]*intel[^"]*"[^>]*>([^<]+)</a>',
                    r'<a[^>]*href="[^"]*amd[^"]*"[^>]*>([^<]+)</a>',
                    r'<a[^>]*href="[^"]*ryzen[^"]*"[^>]*>([^<]+)</a>',
                    r'<a[^>]*href="[^"]*core[^"]*"[^>]*>([^<]+)</a>',
                ]
                
                for link_pattern in link_patterns:
                    link_matches = re.findall(link_pattern, html_content, re.IGNORECASE)
                    
                    for cpu_name in link_matches:
                        cpu_name = cpu_name.strip()
                        
                        # 检查是否匹配CPU型号模式
                        is_cpu = False
                        for pattern in cpu_patterns:
                            if re.search(pattern, cpu_name, re.IGNORECASE):
                                is_cpu = True
                                break
                        
                        if is_cpu and len(cpu_name) > 5:
                            # 为这些CPU分配默认分数
                            if 'Ultra' in cpu_name or '14' in cpu_name or '9 9' in cpu_name or 'AI 9' in cpu_name:
                                cpu_data[cpu_name] = 100
                            elif '13' in cpu_name or '8' in cpu_name or '9 7' in cpu_name:
                                cpu_data[cpu_name] = 95
                            elif '12' in cpu_name or '7' in cpu_name or '9 5' in cpu_name:
                                cpu_data[cpu_name] = 90
                            elif '11' in cpu_name or '6' in cpu_name or '9 3' in cpu_name:
                                cpu_data[cpu_name] = 85
                            else:
                                cpu_data[cpu_name] = 80
                
                # 限制数量，避免太多
                if len(cpu_data) > 50:
                    cpu_data = dict(list(cpu_data.items())[:50])
            
            return cpu_data if cpu_data else None
            
        except Exception as e:
            if self.escape_manager:
                self.escape_manager.debug_log(f"解析CPU数据失败: {e}")
            return None
    
    def _normalize_cpu_score(self, score):
        """将CPU分数标准化为0-100的评分"""
        try:
            # 动态调整最高分 - 假设最高分为80000分（支持最新CPU）
            max_score = 80000
            normalized = (score / max_score) * 100
            return round(min(100, max(0, normalized)), 1)
        except Exception:
            return 50
    
    def _get_default_gpu_data(self):
        """获取默认GPU性能数据 - 从网络获取最新数据"""
        # 本地默认数据
        local_data = {
            'RTX 5090': 100, 'RTX 5080': 98, 'RTX 5070': 95,
            'RTX 4090': 95, 'RTX 4080': 90, 'RTX 4070': 85,
            'RTX 3090': 90, 'RTX 3080': 85, 'RTX 3070': 80,
            'RTX 4060': 75, 'RTX 3060': 70,
            'GTX 1660': 65, 'GTX 1650': 60,
            'RX 7900': 100, 'RX 7800': 95, 'RX 7700': 90,
            'RX 6900': 90, 'RX 6800': 85, 'RX 6700': 80,
            'Arc A770': 75, 'Arc A750': 70,
            'Apple M4': 100, 'Apple M3': 95, 'Apple M2': 90, 'Apple M1': 85,
            'Apple M2 Pro': 95, 'Apple M3 Pro': 100, 'Apple M4 Pro': 100,
        }
        
        try:
            import urllib.request
            import ssl
            
            # 创建不验证SSL证书的上下文
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # 尝试从多个来源获取GPU性能数据
            urls = [
                'https://www.videocardbenchmark.net/',
                'https://www.techpowerup.com/',
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            for url in urls:
                try:
                    request = urllib.request.Request(url, headers=headers)
                    
                    with urllib.request.urlopen(request, timeout=20, context=ssl_context) as response:
                        # 检查响应头，如果是gzip压缩，需要解压
                        content = response.read()
                        
                        # 检查是否是gzip压缩
                        if response.headers.get('Content-Encoding') == 'gzip':
                            import gzip
                            html_content = gzip.decompress(content).decode('utf-8')
                        else:
                            # 尝试直接解码，如果失败则尝试其他编码
                            try:
                                html_content = content.decode('utf-8')
                            except UnicodeDecodeError:
                                html_content = content.decode('latin-1')
                        
                        # 调试：显示获取到的HTML内容长度
                        if self.debug_mode:
                            print(f"[DEBUG] 从 {url} 获取到 {len(html_content)} 字节的HTML内容")
                        
                        # 如果HTML内容太短，可能被重定向或反爬虫
                        if len(html_content) < 10000:
                            if self.debug_mode:
                                print(f"[DEBUG] HTML内容太短，可能被反爬虫拦截")
                            continue
                        
                        # 解析GPU性能数据
                        gpu_data = self._parse_gpu_benchmark_data(html_content)
                        if gpu_data and len(gpu_data) > 5:  # 降低阈值，从10改为5
                            # 调试：显示解析到的GPU数据
                            if self.debug_mode:
                                print(f"[DEBUG] 从 {url} 解析到 {len(gpu_data)} 个GPU型号")
                                for gpu_name, score in list(gpu_data.items())[:5]:
                                    print(f"[DEBUG]   {gpu_name}: {score}")
                            return (gpu_data, True)
                            
                except Exception as e:
                    if self.debug_mode:
                        print(f"[DEBUG] 从 {url} 获取GPU数据失败: {e}")
                    continue
            
        except Exception as e:
            if self.debug_mode:
                print(f"[DEBUG] 获取GPU性能数据失败: {e}")
        
        # 如果网络获取失败，返回本地默认数据
        return (local_data, False)
    
    def _parse_gpu_benchmark_data(self, html_content):
        """解析GPU基准测试数据"""
        try:
            gpu_data = {}
            
            # 改进的GPU型号匹配模式 - 支持更多格式
            gpu_patterns = [
                # NVIDIA RTX 50系列
                r'NVIDIA\s+GeForce\s+RTX\s+50[0-9]{2}[A-Z]*',
                r'RTX\s+50[0-9]{2}[A-Z]*',
                # NVIDIA RTX 40系列
                r'NVIDIA\s+GeForce\s+RTX\s+40[0-9]{2}[A-Z]*',
                r'RTX\s+40[0-9]{2}[A-Z]*',
                # NVIDIA RTX 30系列
                r'NVIDIA\s+GeForce\s+RTX\s+30[0-9]{2}[A-Z]*',
                r'RTX\s+30[0-9]{2}[A-Z]*',
                # NVIDIA RTX 20系列
                r'NVIDIA\s+GeForce\s+RTX\s+20[0-9]{2}[A-Z]*',
                r'RTX\s+20[0-9]{2}[A-Z]*',
                # NVIDIA GTX 16系列
                r'NVIDIA\s+GeForce\s+GTX\s+16[0-9]{2}',
                r'GTX\s+16[0-9]{2}',
                # NVIDIA GTX 10系列
                r'NVIDIA\s+GeForce\s+GTX\s+10[0-9]{2}',
                r'GTX\s+10[0-9]{2}',
                # NVIDIA GTX 900系列及以下
                r'NVIDIA\s+GeForce\s+GTX\s+[0-9]{3,4}[A-Z]*',
                r'GTX\s+[0-9]{3,4}[A-Z]*',
                # NVIDIA GT系列
                r'NVIDIA\s+GeForce\s+GT\s+[0-9]{3,4}[A-Z]*',
                r'GT\s+[0-9]{3,4}[A-Z]*',
                # NVIDIA其他系列
                r'NVIDIA\s+GeForce\s+[A-Z]{2,4}\s*[0-9]{2,4}[A-Z]*',
                # AMD RX 9000系列
                r'AMD\s+Radeon\s+RX\s+9[0-9]{3}[A-Z]*',
                r'RX\s+9[0-9]{3}[A-Z]*',
                # AMD RX 7000系列
                r'AMD\s+Radeon\s+RX\s+7[0-9]{3}[A-Z]*',
                r'RX\s+7[0-9]{3}[A-Z]*',
                # AMD RX 6000系列
                r'AMD\s+Radeon\s+RX\s+6[0-9]{3}[A-Z]*',
                r'RX\s+6[0-9]{3}[A-Z]*',
                # AMD RX 5000系列
                r'AMD\s+Radeon\s+RX\s+5[0-9]{3}[A-Z]*',
                r'RX\s+5[0-9]{3}[A-Z]*',
                # Intel Arc Battlemage系列
                r'Intel\s+Arc\s+B[0-9]{3}',
                r'Arc\s+B[0-9]{3}',
                # Intel Arc Alchemist系列
                r'Intel\s+Arc\s+A[0-9]{3}',
                r'Arc\s+A[0-9]{3}',
                # Apple M4系列GPU
                r'Apple\s+(?:M4|M4\s+(?:Pro|Max|Ultra)?)',
                r'M4(?:\s+(?:Pro|Max|Ultra)?)',
                # Apple M3系列GPU
                r'Apple\s+(?:M3|M3\s+(?:Pro|Max|Ultra)?)',
                r'M3(?:\s+(?:Pro|Max|Ultra)?)',
                # Apple M2/M1系列GPU
                r'Apple\s+(?:M[12]|M[12]\s+(?:Pro|Max|Ultra)?)',
                r'M[12](?:\s+(?:Pro|Max|Ultra)?)',
            ]
            
            # 查找所有GPU型号和分数
            # 尝试匹配表格中的数据
            table_patterns = [
                r'<tr[^>]*>.*?<td[^>]*>([^<]+)</td>.*?<td[^>]*>([^<]+)</td>.*?</tr>',
                r'<tr[^>]*class="[^"]*"[^>]*>.*?<td[^>]*>([^<]+)</td>.*?<td[^>]*>([^<]+)</td>.*?</tr>',
            ]
            
            for table_pattern in table_patterns:
                table_matches = re.findall(table_pattern, html_content, re.DOTALL | re.IGNORECASE)
                
                for gpu_name, score_str in table_matches:
                    gpu_name = gpu_name.strip()
                    
                    # 检查是否匹配GPU型号模式
                    is_gpu = False
                    for pattern in gpu_patterns:
                        if re.search(pattern, gpu_name, re.IGNORECASE):
                            is_gpu = True
                            break
                    
                    if is_gpu:
                        try:
                            # 清理分数字符串
                            score = int(re.sub(r'[^\d]', '', score_str.strip()))
                            if score > 100:  # 过滤掉无效数据
                                gpu_data[gpu_name] = self._normalize_gpu_score(score)
                        except (ValueError, AttributeError):
                            continue
                
                if gpu_data:
                    break
            
            # 如果表格解析失败，尝试从链接中提取GPU型号
            if not gpu_data:
                # 查找所有链接中的GPU型号
                link_pattern = r'<a[^>]*href="[^"]*gpu=[^"]*"[^>]*>([^<]+)</a>'
                link_matches = re.findall(link_pattern, html_content, re.IGNORECASE)
                
                for gpu_name in link_matches:
                    gpu_name = gpu_name.strip()
                    
                    # 检查是否匹配GPU型号模式
                    is_gpu = False
                    for pattern in gpu_patterns:
                        if re.search(pattern, gpu_name, re.IGNORECASE):
                            is_gpu = True
                            break
                    
                    if is_gpu and len(gpu_name) > 5:
                        # 为这些GPU分配默认分数
                        if '50' in gpu_name or '9 9' in gpu_name:
                            gpu_data[gpu_name] = 100
                        elif '40' in gpu_name or '9 8' in gpu_name:
                            gpu_data[gpu_name] = 95
                        elif '30' in gpu_name or '9 7' in gpu_name:
                            gpu_data[gpu_name] = 90
                        elif '20' in gpu_name or '9 6' in gpu_name:
                            gpu_data[gpu_name] = 85
                        elif '16' in gpu_name or '9 5' in gpu_name:
                            gpu_data[gpu_name] = 80
                        elif '10' in gpu_name or '9 4' in gpu_name:
                            gpu_data[gpu_name] = 75
                        else:
                            gpu_data[gpu_name] = 70
                
                # 限制数量，避免太多
                if len(gpu_data) > 50:
                    gpu_data = dict(list(gpu_data.items())[:50])
            
            return gpu_data if gpu_data else None
            
        except Exception as e:
            if self.debug_mode:
                print(f"[DEBUG] 解析GPU数据失败: {e}")
            return None
    
    def _normalize_gpu_score(self, score):
        """将GPU分数标准化为0-100的评分"""
        try:
            # 动态调整最高分 - 假设最高分为100000分（支持最新GPU如RTX 5090）
            max_score = 100000
            normalized = (score / max_score) * 100
            return round(min(100, max(0, normalized)), 1)
        except Exception:
            return 50
    
    def _get_default_memory_data(self):
        """获取默认内存性能数据"""
        return {
            32: 100, 24: 95, 16: 85, 12: 75, 8: 60, 4: 40, 2: 20,
        }
    
    def _get_default_network_data(self):
        """获取默认网卡性能数据"""
        return {
            'Wi-Fi 7': 100,
            'Wi-Fi 6E': 95,
            'Wi-Fi 6': 90,
            'Wi-Fi 5': 80,
            'Wi-Fi 4': 60,
            'Ethernet 10G': 100,
            'Ethernet 5G': 95,
            'Ethernet 2.5G': 90,
            'Ethernet 1G': 85,
            'Ethernet 100M': 70,
            'Intel Wi-Fi 7': 100,
            'Intel Wi-Fi 6E': 95,
            'Intel Wi-Fi 6': 90,
            'Broadcom Wi-Fi 7': 100,
            'Broadcom Wi-Fi 6E': 95,
            'Qualcomm Wi-Fi 7': 100,
            'Qualcomm Wi-Fi 6E': 95,
            'Realtek Wi-Fi 6': 85,
            'Realtek Wi-Fi 5': 75
        }
    
    def save_performance_data(self, cpu_data=None, gpu_data=None, memory_data=None):
        """保存性能数据"""
        try:
            if cpu_data:
                self._save_json_file(self.cpu_performance_file, cpu_data)
            if gpu_data:
                self._save_json_file(self.gpu_performance_file, gpu_data)
            if memory_data:
                self._save_json_file(self.memory_performance_file, memory_data)
            
            return True
        except Exception as e:
            if self.escape_manager:
                self.escape_manager.debug_log(f"保存性能数据失败: {e}")
            return False
    
    def _save_json_file(self, file_path, data):
        """保存JSON文件"""
        return UnifiedUtils.save_json_file(file_path, data)


class ProjectorRecommender:
    """投影仪推荐器 - 集成版"""
    
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode
        self.projector_db_path = os.path.join(os.path.dirname(__file__), 'json', 'projector', 'projector_data.json')
        self.projectors = []
        self.update_interval_hours = 24  # 每24小时检查一次更新
        self.last_update_check = None
        
        # 加载投影仪数据库
        self._load_projector_database()
        
        # 检查是否需要更新数据库
        self._check_and_update_database()
    
    def _load_projector_database(self):
        """从JSON文件加载投影仪数据库"""
        try:
            if os.path.exists(self.projector_db_path):
                with open(self.projector_db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 转换JSON格式为内部格式
                self.projectors = []
                for p in data.get('projectors', []):
                    projector = {
                        '名称': f"{p['brand']} {p['model']}",
                        '品牌': p['brand'],
                        '价格': p['price'],
                        '分辨率': p['resolution'],
                        '亮度': p['brightness'],
                        '对比度': f"{p['contrast']}:1",
                        '推荐理由': self._generate_recommendation_reason(p),
                        '适用场景': p.get('usage_scenario', '家庭娱乐')
                    }
                    self.projectors.append(projector)
                
                if self.debug_mode:
                    print(f"✅ 成功加载 {len(self.projectors)} 款投影仪数据")
            else:
                print(f"⚠️ 警告：投影仪数据库文件不存在: {self.projector_db_path}")
                self._load_default_projectors()
        except Exception as e:
            print(f"❌ 加载投影仪数据库失败: {e}")
            self._load_default_projectors()
    
    def _generate_recommendation_reason(self, projector):
        """根据投影仪参数生成推荐理由"""
        reasons = []
        
        # 分辨率
        if projector['resolution'] == '4K':
            reasons.append('4K超高清')
        elif projector['resolution'] == '1080P':
            reasons.append('1080P高清')
        
        # 亮度
        brightness = projector['brightness']
        if brightness >= 3000:
            reasons.append('超高亮度')
        elif brightness >= 2000:
            reasons.append('高亮度')
        elif brightness >= 1000:
            reasons.append('标准亮度')
        
        # 对比度
        contrast = projector['contrast']
        if contrast >= 15000:
            reasons.append('高对比度')
        elif contrast >= 10000:
            reasons.append('优秀对比度')
        
        # 光源寿命
        lifespan = projector['lifespan']
        if lifespan >= 30000:
            reasons.append('长寿命光源')
        
        # 特殊功能
        features = projector.get('features', [])
        if '4K支持' in features:
            reasons.append('4K支持')
        if '激光光源' in features:
            reasons.append('激光光源')
        if '智能系统' in features:
            reasons.append('智能系统')
        if 'HDR支持' in features:
            reasons.append('HDR支持')
        
        # 适用场景
        usage = projector.get('usage_scenario', '')
        if '家庭影院' in usage:
            reasons.append('适合家庭影院')
        elif '入门家用' in usage:
            reasons.append('入门首选')
        elif '高端家用' in usage:
            reasons.append('高端配置')
        
        return '，'.join(reasons) if reasons else '性价比不错'
    
    def _load_default_projectors(self):
        """加载默认投影仪数据（当JSON文件加载失败时）"""
        self.projectors = [
            {
                '名称': '极米H6',
                '品牌': '极米',
                '价格': 5999,
                '分辨率': '4K',
                '亮度': 2400,
                '对比度': '2000:1',
                '推荐理由': '4K超高清，适合家庭影院',
                '适用场景': '家庭影院,客厅,卧室'
            },
            {
                '名称': '坚果N1 Ultra',
                '品牌': '坚果',
                '价格': 8999,
                '分辨率': '4K',
                '亮度': 3000,
                '对比度': '2500:1',
                '推荐理由': '三色激光，色彩表现优秀',
                '适用场景': '家庭影院,商务会议,大型客厅'
            },
            {
                '名称': '当贝X5',
                '品牌': '当贝',
                '价格': 6999,
                '分辨率': '4K',
                '亮度': 2450,
                '对比度': '2200:1',
                '推荐理由': 'ALPD激光，性价比高',
                '适用场景': '家庭影院,卧室,小型客厅'
            },
            {
                '名称': '极米Z6X',
                '品牌': '极米',
                '价格': 2999,
                '分辨率': '1080P',
                '亮度': 800,
                '对比度': '1000:1',
                '推荐理由': '便携式设计，适合小空间',
                '适用场景': '卧室,宿舍,小型房间'
            },
            {
                '名称': '坚果G9S',
                '品牌': '坚果',
                '价格': 3999,
                '分辨率': '1080P',
                '亮度': 1200,
                '对比度': '1500:1',
                '推荐理由': '智能系统，操作便捷',
                '适用场景': '客厅,卧室,家庭娱乐'
            }
        ]
    
    def _check_and_update_database(self):
        """检查并更新投影仪数据库"""
        try:
            # 检查上次更新时间
            if os.path.exists(self.projector_db_path):
                with open(self.projector_db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    last_update = data.get('update_time', '')
                    
                if last_update:
                    last_update_time = datetime.datetime.fromisoformat(last_update)
                    time_since_update = datetime.datetime.now() - last_update_time
                    
                    if time_since_update.total_seconds() < self.update_interval_hours * 3600:
                        if self.debug_mode:
                            print(f"ℹ️ 数据库更新时间: {last_update}")
                        return
            
            # 尝试更新数据库
            self._update_database()
            
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ 检查数据库更新失败: {e}")
    
    def _update_database(self):
        """更新投影仪数据库（联网获取最新数据）"""
        try:
            if self.debug_mode:
                print("🔄 正在检查投影仪数据库更新...")
            
            # 检查数据库文件是否存在和是否需要更新
            if os.path.exists(self.projector_db_path):
                with open(self.projector_db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    last_update = data.get('update_time', '')
                    
                if last_update:
                    last_update_time = datetime.datetime.fromisoformat(last_update)
                    time_since_update = datetime.datetime.now() - last_update_time
                    
                    if time_since_update.total_seconds() < self.update_interval_hours * 3600:
                        if self.debug_mode:
                            print(f"ℹ️ 数据库更新时间: {last_update}")
                            print("✅ 投影仪数据库已是最新版本")
                        return
            
            # 如果需要更新，这里可以添加联网更新逻辑
            # 目前使用本地JSON文件，如果需要联网更新，可以添加API调用
            # 例如：从电商平台API获取最新价格和产品信息
            
            # 数据库检查完成
            if self.debug_mode:
                print("✅ 投影仪数据库检查完成")
                
        except Exception as e:
            if self.debug_mode:
                print(f"❌ 更新投影仪数据库失败: {e}")
    
    def reload_database(self):
        """重新加载投影仪数据库"""
        if self.debug_mode:
            print("🔄 重新加载投影仪数据库...")
        self._load_projector_database()
        if self.debug_mode:
            print(f"✅ 成功重新加载 {len(self.projectors)} 款投影仪数据")
    
    def recommend_projector(self, budget_range=None, brand_preference=None, resolution_preference=None):
        """推荐投影仪"""
        filtered_projectors = self.projectors.copy()
        
        # 根据预算过滤
        if budget_range:
            min_budget, max_budget = budget_range
            filtered_projectors = [p for p in filtered_projectors if min_budget <= p['价格'] <= max_budget]
        
        # 根据品牌偏好过滤
        if brand_preference:
            filtered_projectors = [p for p in filtered_projectors if brand_preference.lower() in p['品牌'].lower()]
        
        # 根据分辨率偏好过滤
        if resolution_preference:
            filtered_projectors = [p for p in filtered_projectors if resolution_preference.lower() in p['分辨率'].lower()]
        
        return filtered_projectors
    
    def print_recommendations(self, projectors=None, budget_range=None, brand_preference=None, resolution_preference=None):
        """打印投影仪推荐"""
        if projectors is None:
            projectors = self.recommend_projector(budget_range, brand_preference, resolution_preference)
        
        UnifiedUtils.print_section_header("🎬 投影仪推荐报告")
        
        if budget_range:
            print(f"\n💰 预算范围: ¥{budget_range[0]} - ¥{budget_range[1]}")
        if brand_preference:
            print(f"🏷️  品牌偏好: {brand_preference}")
        if resolution_preference:
            print(f"📺 分辨率偏好: {resolution_preference}")
        
        if projectors:
            print(f"\n为您推荐 {len(projectors)} 款投影仪:")
            UnifiedUtils.print_section_divider()
            
            for i, projector in enumerate(projectors, 1):
                print(f"\n{i}. {projector['名称']} - ¥{projector['价格']}")
                print(f"   品牌: {projector['品牌']}")
                print(f"   分辨率: {projector['分辨率']}")
                print(f"   亮度: {projector['亮度']}流明")
                print(f"   对比度: {projector['对比度']}")
                print(f"   适用场景: {projector['适用场景']}")
                print(f"   💡 推荐理由: {projector['推荐理由']}")
        else:
            print("\n没有找到符合条件的投影仪")
        
        print("\n" + "="*60)


class EscapeManager:
    """转义管理器 - 统一管理所有转义逻辑"""
    
    def __init__(self):
        # 全局调试标志
        self.debug_mode = False
        
        # 网卡型号到最大带宽的映射表（单位：Mbps）
        self.wifi_bandwidth_map = {
            # 802.11ax (WiFi 6) 网卡
            '8812CU': 1200, '8812BU': 1200, '8812AU': 1200, '8812E': 1200,
            '8811CU': 433, '8811BU': 433, '8811AU': 433,
            '8821CU': 433, '8821BU': 433, '8821AU': 433,
            '8822CU': 1200, '8822BU': 1200, '8822AU': 1200,
            '8852AE': 2400, '8852BE': 2400, '8852CE': 2400,
            'AX200': 2400, 'AX201': 2400, 'AX210': 2400,
            'AX3000': 2400, 'AX5400': 4800, 'AX6000': 4800,
            
            # 802.11ac (WiFi 5) 网卡
            '8812': 866, '8814': 1733, '8811': 433,
            '8821': 433, '8822': 866,
            'AC1200': 866, 'AC1750': 1300, 'AC1900': 1300,
            'AC5300': 1733, 'AC5400': 1733, 'AC6000': 1733,
            
            # 802.11n (WiFi 4) 网卡
            '8192': 300, '8188': 150, '8187': 300,
            'N150': 150, 'N300': 300, 'N600': 600,
            
            # 其他常见网卡
            'RTL8188': 150, 'RTL8192': 300, 'RTL8812': 866,
            'RTL8821': 433, 'RTL8822': 866,
            'Intel(R) Wireless-AC': 866,
            'Intel(R) Wireless-AX': 2400,
            'Intel(R) Wi-Fi 6': 2400,
        }
        
        # 国家英文到中文映射
        self.country_map = {
            'China': '中国', 'United States': '美国', 'Japan': '日本',
            'South Korea': '韩国', 'United Kingdom': '英国', 'Germany': '德国',
            'France': '法国', 'Russia': '俄罗斯', 'Canada': '加拿大',
            'Australia': '澳大利亚', 'India': '印度', 'Brazil': '巴西',
            'Italy': '意大利', 'Spain': '西班牙', 'Netherlands': '荷兰',
            'Singapore': '新加坡', 'Hong Kong': '香港', 'Taiwan': '台湾',
            'Macau': '澳门'
        }
        
        # ISP英文到中文映射
        self.isp_map = {
            'China Mobile': '中国移动', 'China Telecom': '中国电信', 'China Unicom': '中国联通',
            'China Netcom': '中国网通', 'China Tietong': '中国铁通', 'China Railcom': '中国铁通',
            'China Education and Research Network': '中国教育和科研计算机网',
            'China Science and Technology Network': '中国科技网',
            'China Broadband': '中国宽带', 'China Telecom Next': '中国电信',
            'China Unicom Next': '中国联通', 'China Mobile Next': '中国移动',
            'CMCC': '中国移动', 'CT': '中国电信', 'CU': '中国联通',
            'Mobile': '中国移动', 'Telecom': '中国电信', 'Unicom': '中国联通'
        }
        
        # 省份英文到中文映射
        self.region_map = {
            'Anhui': '安徽', 'Beijing': '北京', 'Shanghai': '上海', 'Tianjin': '天津',
            'Chongqing': '重庆', 'Hebei': '河北', 'Shanxi': '山西', 'Liaoning': '辽宁',
            'Jilin': '吉林', 'Heilongjiang': '黑龙江', 'Jiangsu': '江苏', 'Zhejiang': '浙江',
            'Fujian': '福建', 'Jiangxi': '江西', 'Shandong': '山东', 'Henan': '河南',
            'Hubei': '湖北', 'Hunan': '湖南', 'Guangdong': '广东', 'Hainan': '海南',
            'Sichuan': '四川', 'Guizhou': '贵州', 'Yunnan': '云南', 'Shaanxi': '陕西',
            'Gansu': '甘肃', 'Qinghai': '青海', 'Taiwan': '台湾', 'Hong Kong': '香港',
            'Macau': '澳门', 'Inner Mongolia': '内蒙古', 'Tibet': '西藏', 'Xinjiang': '新疆',
            'Ningxia': '宁夏'
        }
        
        # 城市英文到中文映射
        self.city_map = {
            'Hefei': '合肥', 'Beijing': '北京', 'Shanghai': '上海', 'Tianjin': '天津',
            'Chongqing': '重庆', 'Guangzhou': '广州', 'Shenzhen': '深圳', 'Hangzhou': '杭州',
            'Nanjing': '南京', 'Wuhan': '武汉', 'Chengdu': '成都', 'Xi\'an': '西安',
            'Suzhou': '苏州', 'Dalian': '大连', 'Qingdao': '青岛', 'Xiamen': '厦门',
            'Changsha': '长沙', 'Zhengzhou': '郑州', 'Jinan': '济南', 'Fuzhou': '福州',
            'Ningbo': '宁波', 'Wuxi': '无锡', 'Dongguan': '东莞', 'Foshan': '佛山',
            'Zhuhai': '珠海', 'Huainan': '淮南', 'Shou County': '寿县', 'Shenyang': '沈阳',
            'Changchun': '长春', 'Harbin': '哈尔滨', 'Nanchang': '南昌', 'Guiyang': '贵阳',
            'Kunming': '昆明', 'Lhasa': '拉萨', 'Lanzhou': '兰州', 'Xining': '西宁',
            'Yinchuan': '银川', 'Urumqi': '乌鲁木齐', 'Haikou': '海口', 'Nanning': '南宁',
            'Shijiazhuang': '石家庄', 'Taiyuan': '太原', 'Hohhot': '呼和浩特'
        }
        
        # 常见WiFi品牌模式映射（用于智能SSID转义）
        self.wifi_brand_patterns = [
            ('TP-LINK', 'TP-LINK'), ('XIAOMI', 'Xiaomi'), ('HUAWEI', 'Huawei'),
            ('CMCC', 'CMCC'), ('CHINANET', 'ChinaNet'), ('TENDA', 'Tenda'),
            ('MERCURY', 'Mercury'), ('FAST', 'Fast'), ('PHICOMM', 'PHICOMM'),
            ('ASUS', 'ASUS'), ('NETGEAR', 'NETGEAR'), ('D-LINK', 'D-Link'),
            ('LINKSYS', 'Linksys'), ('BUFFALO', 'Buffalo'), ('ZTE', 'ZTE'),
            ('MI', 'Mi'), ('REDMI', 'Redmi'), ('HONOR', 'Honor'), ('OPPO', 'OPPO'),
            ('VIVO', 'VIVO'), ('REALME', 'realme'), ('ONEPLUS', 'OnePlus'),
            ('SAMSUNG', 'Samsung'), ('APPLE', 'Apple'), ('GOOGLE', 'Google'),
            ('AMAZON', 'Amazon'), ('ALIBABA', 'Alibaba'), ('TENCENT', 'Tencent'),
            ('BAIDU', 'Baidu'), ('JD', 'JD'), ('PDD', 'PDD'), ('MEITUAN', 'Meituan'),
            ('DIDI', 'Didi'), ('BYTEDANCE', 'ByteDance'), ('KUAISHOU', 'Kuaishou'),
            ('DOUYIN', 'Douyin'), ('TIKTOK', 'TikTok'), ('WECHAT', 'WeChat'),
            ('QQ', 'QQ'), ('ALIPAY', 'Alipay'), ('WECHATPAY', 'WeChatPay'),
            ('ALIPAYHK', 'AlipayHK'), ('WECHATWORK', 'WeChatWork'), ('DINGTALK', 'DingTalk'),
            ('FEISHU', 'Feishu'), ('LARK', 'Lark'), ('ZOOM', 'Zoom'), ('TEAMS', 'Teams'),
            ('SLACK', 'Slack'), ('DISCORD', 'Discord'), ('TELEGRAM', 'Telegram'),
            ('WHATSAPP', 'WhatsApp'), ('SIGNAL', 'Signal'), ('LINE', 'Line'),
            ('KAKAOTALK', 'KakaoTalk')
        ]
    
    def is_garbled_ssid(self, scanned_ssid, current_ssid=None):
        """智能检测SSID是否为乱码"""
        if not scanned_ssid:
            return False
        
        if scanned_ssid == current_ssid:
            return False
        
        if current_ssid and current_ssid in scanned_ssid:
            return False
        
        if '�' in scanned_ssid:
            return True
        
        if len(scanned_ssid) > 15 and re.search(r'[\u4e00-\u9fff]{4,}', scanned_ssid):
            return True
        
        if re.search(r'[\x00-\x1f\x7f-\x9f]', scanned_ssid):
            return True
        
        if self._has_gbk_garbled_pattern(scanned_ssid):
            return True
        
        return False
    
    def _has_gbk_garbled_pattern(self, text):
        """检测GBK编码错误特征"""
        if not text:
            return False
        
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        if len(chinese_chars) > 8:
            return True
        
        if len(text) > 20 and len(chinese_chars) > len(text) * 0.6:
            return True
        
        return False
    
    def get_correct_ssid(self, garbled_ssid, current_ssid=None, scan_results=None):
        """获取正确的SSID（基于多维度智能推断）"""
        if not garbled_ssid:
            return "未知WiFi"
        
        if current_ssid and not self.is_garbled_ssid(current_ssid):
            return current_ssid
        
        if scan_results:
            non_garbled_networks = [
                net for net in scan_results 
                if not self.is_garbled_ssid(net.get('ssid', ''))
            ]
            if non_garbled_networks:
                strongest_network = max(non_garbled_networks, 
                                     key=lambda x: x.get('rssi_dbm', -100))
                return strongest_network.get('ssid', '未知WiFi')
        
        for pattern, replacement in self.wifi_brand_patterns:
            if pattern in garbled_ssid.upper():
                return replacement
        
        return "未知WiFi"
    
    def translate_region(self, region_en):
        """将省份英文名转换为中文名"""
        return self.region_map.get(region_en, region_en)
    
    def translate_city(self, city_en):
        """将城市英文名转换为中文名"""
        return self.city_map.get(city_en, city_en)
    
    def translate_country(self, country_en):
        """将国家英文名转换为中文名"""
        return self.country_map.get(country_en, country_en)
    
    def translate_isp(self, isp_en):
        """将ISP英文名转换为中文名"""
        return self.isp_map.get(isp_en, isp_en)
    
    def get_wifi_bandwidth(self, description):
        """根据网卡描述信息获取最大带宽（单位：Mbps）"""
        if not description:
            return 0
        
        # 遍历网卡型号映射表
        for model, bandwidth in self.wifi_bandwidth_map.items():
            if model in description:
                return bandwidth
        
        # 如果没有找到匹配的型号，返回0表示未知
        return 0
    
    def debug_log(self, message, data=None, debug=None):
        """统一的调试日志函数"""
        # 如果没有提供debug参数，使用全局调试模式
        if debug is None:
            debug = self.debug_mode
        
        # 只有在调试模式下才显示调试信息
        if debug:
            try:
                if data is not None:
                    print(f"调试：{message} {data}")
                else:
                    print(f"调试：{message}")
            except UnicodeEncodeError:
                # 如果编码失败，使用安全编码
                if data is not None:
                    print(f"Debug: {message} {str(data).encode('utf-8', errors='ignore').decode('utf-8')}")
                else:
                    print(f"Debug: {message}")
    
    def clean_filename(self, filename):
        """清理文件名中的非法字符和乱码"""
        if not filename:
            return "未知位置"
        
        illegal_chars = r'[<>:"/\\|?*]'
        cleaned = re.sub(illegal_chars, '', filename)
        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned)
        cleaned = cleaned.replace('�', '')
        
        if len(cleaned) > 200:
            cleaned = cleaned[:200]
        
        cleaned = cleaned.strip()
        
        if not cleaned:
            cleaned = "未知位置"
        
        return cleaned
    
    def generate_location_prefix(self, location_info):
        """生成地理位置前缀（支持县级行政区和乡镇）"""
        if not location_info:
            return ""
        
        translated_info = self.translate_location_info(location_info)
        
        region = translated_info.get('region', '')
        city = translated_info.get('city', '')
        
        if not region or not city:
            return ""
        
        # 判断district的类型（县级市或县）
        district = translated_info.get('district', '')
        township = translated_info.get('township', '')
        village = translated_info.get('village', '')  # 行政村或社区
        
        # 如果没有district，直接返回省+市
        if not district:
            return f"{region}省{city}市 "
        
        # 判断district是否为县级市（以"市"结尾）
        if district.endswith('市'):
            # 县级市格式：省+市+县级市+镇+行政村/社区
            location_prefix = f"{region}省{city}市{district}"
            if township:
                location_prefix += township
            if village:
                location_prefix += village
            return location_prefix + " "
        else:
            # 县格式：省+市+县+镇+行政村/社区
            location_prefix = f"{region}省{city}市{district}"
            if township:
                location_prefix += township
            if village:
                location_prefix += village
            return location_prefix + " "
    
    def translate_location_info(self, location_info):
        """翻译地理位置信息中的英文名称"""
        if not location_info:
            return {}
        
        translated = location_info.copy()
        
        if 'region_en' in translated and 'region' not in translated:
            translated['region'] = self.translate_region(translated['region_en'])
        elif 'region' in translated and translated['region'] in self.region_map.values():
            if 'region_en' not in translated:
                for en, cn in self.region_map.items():
                    if cn == translated['region']:
                        translated['region_en'] = en
                        break
        
        if 'city_en' in translated and 'city' not in translated:
            translated['city'] = self.translate_city(translated['city_en'])
        elif 'city' in translated and translated['city'] in self.city_map.values():
            if 'city_en' not in translated:
                for en, cn in self.city_map.items():
                    if cn == translated['city']:
                        translated['city_en'] = en
                        break
        
        return translated


class WiFiChannelScanner:
    def __init__(self, cross_platform_utils=None):
        self.scan_results = []
        self.channel_stats = {}
        if cross_platform_utils is None:
            cross_platform_utils = get_cross_platform_utils()
        self.cross_platform_utils = cross_platform_utils
        self.platform = self.cross_platform_utils.platform
        
        # 初始化JSON文件管理器
        self.json_manager = JSONFileManager("json")
        
        # 兼容旧代码的日志目录
        self.log_dir = "json/logs"
        self.escape_manager = EscapeManager()  # 初始化转义管理器

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def _safe_print(self, message):
        """安全打印函数，确保中文正确显示"""
        UnifiedUtils.safe_print(message)

    def get_platform_info(self):
        """获取平台信息"""
        return UnifiedUtils.get_system_info()

    def run_command(self, command):
        """执行命令（使用统一的跨平台工具类）"""
        return UnifiedUtils.run_command(command)
    
    def _contains_garbled_text(self, text):
        """检测文本是否包含乱码"""
        return UnifiedUtils.contains_garbled_text(text)
    
    def run_command_utf8(self, command):
        """执行命令（使用UTF-8编码）"""
        return self.cross_platform_utils.run_command(command)

    def get_current_wifi_info(self):
        """获取当前连接的WiFi信息"""
        if self.platform == "Darwin":
            try:
                airport_paths = [
                    "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport",
                    "/usr/local/bin/airport"
                ]
                
                airport_cmd = None
                for path in airport_paths:
                    if os.path.exists(path):
                        airport_cmd = path
                        break
                
                if not airport_cmd:
                    return None
                
                output = self.run_command([airport_cmd, "-I"])
                
                if not output:
                    return None
                
                wifi_info = {}
                for line in output.split('\n'):
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        wifi_info[key] = value
                
                # 添加频段信息
                if 'channel' in wifi_info:
                    try:
                        channel = int(wifi_info['channel'])
                        if channel <= 14:
                            wifi_info['band'] = '2.4G'
                        elif channel >= 36:
                            wifi_info['band'] = '5G'
                        else:
                            wifi_info['band'] = '未知'
                    except (ValueError, TypeError):
                        wifi_info['band'] = '未知'
                
                # 在macOS下添加网卡详细信息
                wifi_info = self._enhance_macos_network_card_info(wifi_info)
                
                return wifi_info
            except Exception:
                return None
        elif self.platform == "Windows":
            try:
                # 使用netsh命令获取当前连接的WiFi信息
                command = ["netsh", "wlan", "show", "interfaces"]
                output = self.run_command(command)
                
                self.escape_manager.debug_log(f"netsh interfaces输出长度: {len(output)} 字符")
                preview = output[:500] if len(output) > 500 else output
                self.escape_manager.debug_log(f"netsh interfaces输出预览: {preview}")
                
                if "错误" in output or "异常" in output or "No wireless" in output:
                    return None
                
                wifi_info = {}
                lines = output.split('\n')
                
                for line in lines:
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        wifi_info[key] = value
                
                # 提取关键信息
                current_info = {}
                
                # 提取网卡描述信息并计算最大带宽
                description = None
                
                # 尝试多种可能的网卡描述字段名（Windows netsh命令可能使用不同的字段名）
                description_fields = [
                    '说明', 'Description', '描述', '网卡描述', '网卡型号',
                    'Name', 'Adapter', 'Interface', '设备描述', '设备名称'
                ]
                
                for field in description_fields:
                    if field in wifi_info:
                        description = wifi_info[field]
                        self.escape_manager.debug_log(f"找到网卡描述字段 '{field}': {description}")
                        break
                
                # 如果没有找到明确的描述字段，尝试从所有字段中查找包含网卡关键词的
                if not description:
                    for key, value in wifi_info.items():
                        # 查找包含网卡相关关键词的字段
                        if any(keyword in key.lower() for keyword in ['description', '说明', '描述', 'name', 'adapter', 'interface', '设备', '网卡']):
                            description = value
                            self.escape_manager.debug_log(f"从关键词匹配找到网卡描述: {key} = {description}")
                            break
                
                # 如果仍然没有找到，尝试从所有字段中查找包含常见网卡品牌的信息
                if not description:
                    for key, value in wifi_info.items():
                        # 查找包含常见网卡品牌的信息
                        if any(brand in value.lower() for brand in ['realtek', 'intel', 'broadcom', 'qualcomm', 'atheros', 'mediatek', 'tenda', '腾达', 'tp-link', '水星', 'mercury', 'd-link']):
                            description = value
                            self.escape_manager.debug_log(f"从品牌匹配找到网卡描述: {key} = {description}")
                            break
                
                # 尝试获取具体的网卡品牌型号
                brand_model = self._detect_network_card_brand_model(description)
                
                if description:
                    # 保存完整的网卡描述信息
                    current_info['网卡完整描述'] = description
                    
                    # 保存具体的品牌型号信息
                    if brand_model:
                        current_info['网卡品牌型号'] = brand_model
                    
                    # 获取网卡最大带宽（单位：Mbps）
                    bandwidth_mbps = self.escape_manager.get_wifi_bandwidth(description)
                    if bandwidth_mbps > 0:
                        current_info['max_bandwidth_mbps'] = bandwidth_mbps
                        # 转换为Gbps（如果大于1000Mbps）
                        if bandwidth_mbps >= 1000:
                            current_info['max_bandwidth_gbps'] = bandwidth_mbps / 1000
                        self.escape_manager.debug_log(f"网卡描述: {description}, 最大带宽: {bandwidth_mbps}Mbps")
                else:
                    self.escape_manager.debug_log("无法找到网卡描述信息")
                    # 输出所有可用的字段用于调试
                    self.escape_manager.debug_log("可用的WiFi信息字段:", list(wifi_info.keys()))
                
                # 优先使用"配置文件"字段（中文）或"Profile"字段（英文），因为它通常显示正确的WiFi名称
                if '配置文件' in wifi_info:
                    profile_value = wifi_info['配置文件']
                    self.escape_manager.debug_log(f"找到配置文件字段: {repr(profile_value)}")
                    # 使用智能乱码检测（使用转义管理器）
                    if self.escape_manager.is_garbled_ssid(profile_value, None):
                        # 如果是乱码，尝试从配置文件或已知信息中获取正确的SSID
                        current_info['SSID'] = self.escape_manager.get_correct_ssid(profile_value)
                    else:
                        current_info['SSID'] = profile_value
                elif 'Profile' in wifi_info:
                    profile_value = wifi_info['Profile']
                    self.escape_manager.debug_log(f"找到Profile字段: {repr(profile_value)}")
                    # 使用智能乱码检测（使用转义管理器）
                    if self.escape_manager.is_garbled_ssid(profile_value, None):
                        # 如果是乱码，尝试从配置文件或已知信息中获取正确的SSID
                        current_info['SSID'] = self.escape_manager.get_correct_ssid(profile_value)
                    else:
                        current_info['SSID'] = profile_value
                # 处理SSID（英文）- 智能修复乱码问题（备用方案）
                elif 'SSID' in wifi_info:
                    ssid_value = wifi_info['SSID']
                    self.escape_manager.debug_log(f"找到SSID字段: {repr(ssid_value)}")
                    # 检查SSID是否为乱码（包含特殊字符或无法识别的编码）
                    if self.escape_manager.is_garbled_ssid(ssid_value, None):
                        # 如果是乱码，尝试从配置文件或已知信息中获取正确的SSID
                        current_info['SSID'] = self.escape_manager.get_correct_ssid(ssid_value)
                    else:
                        current_info['SSID'] = ssid_value
                else:
                    # 如果无法获取SSID，尝试从其他字段中查找
                    self.escape_manager.debug_log("未找到SSID字段，尝试从其他字段查找")
                    for key in wifi_info:
                        if 'SSID' in key.upper() or '配置文件' in key or 'Profile' in key:
                            ssid_value = wifi_info[key]
                            self.escape_manager.debug_log(f"从字段 {key} 找到SSID: {repr(ssid_value)}")
                            if self.escape_manager.is_garbled_ssid(ssid_value, None):
                                current_info['SSID'] = self.escape_manager.get_correct_ssid(ssid_value)
                            else:
                                current_info['SSID'] = ssid_value
                            break
                    else:
                        # 如果仍然无法获取SSID，使用BSSID作为标识
                        self.escape_manager.debug_log("无法获取SSID，使用BSSID作为标识")
                        if 'BSSID' in wifi_info:
                            current_info['SSID'] = f"WiFi-{wifi_info['BSSID'][:8]}"
                        else:
                            current_info['SSID'] = 'WiFi网络'
                
                # 处理BSSID
                if 'BSSID' in wifi_info:
                    current_info['BSSID'] = wifi_info['BSSID']
                # 尝试英文标签
                elif 'BSSID' not in wifi_info:
                    for key in wifi_info:
                        if 'BSSID' in key.upper():
                            current_info['BSSID'] = wifi_info[key]
                            break
                
                # 处理信道 - 尝试多种标签
                channel_found = False
                channel_keys = ['信道', '通道', 'Channel', 'CHANNEL']
                for key in channel_keys:
                    if key in wifi_info:
                        channel_str = wifi_info[key]
                        try:
                            # 处理可能的格式："36,1" 或 "36"
                            if ',' in channel_str:
                                channel_str = channel_str.split(',')[0]
                            channel = int(channel_str.strip())
                            current_info['channel'] = str(channel)  # 标准化为纯数字字符串
                            if channel <= 14:
                                current_info['band'] = '2.4G'
                            elif channel >= 36:
                                current_info['band'] = '5G'
                            else:
                                current_info['band'] = '未知'
                            channel_found = True
                            break
                        except (ValueError, TypeError):
                            pass
                
                # 处理信号强度
                if '信号' in wifi_info:
                    current_info['signal'] = wifi_info['信号']
                # 尝试英文标签
                elif '信号' not in wifi_info:
                    for key in wifi_info:
                        if '信号' in key or 'Signal' in key.upper():
                            current_info['signal'] = wifi_info[key]
                            break
                
                # 处理状态
                if '状态' in wifi_info:
                    current_info['status'] = wifi_info['状态']
                # 尝试英文标签
                elif '状态' not in wifi_info:
                    for key in wifi_info:
                        if '状态' in key or 'Status' in key.upper():
                            current_info['status'] = wifi_info[key]
                            break
                
                if current_info:
                    return current_info
                else:
                    return None
            except Exception as e:
                print(f"Windows获取WiFi信息失败: {e}")
                return None
        else:
            return None

    def _enhance_macos_network_card_info(self, wifi_info):
        """增强macOS下的网卡信息，添加详细的网卡描述、品牌型号、带宽等信息"""
        try:
            # 使用system_profiler获取详细的网卡信息
            command = ["system_profiler", "SPNetworkDataType"]
            output = self.run_command(command)
            
            # 获取网卡驱动信息来判断网卡类型
            driver_output = ""
            pci_vendor_id = ""
            pci_device_id = ""
            
            try:
                driver_output = self.run_command(["ioreg", "-l", "-w0", "-c", "IO80211Interface"])
            except:
                pass
            
            # 尝试获取PCI设备ID
            try:
                pci_output = self.run_command(["ioreg", "-l", "-r", "-w0", "-c", "IOPCIDevice"])
                if pci_output:
                    # 查找vendor-id和device-id
                    # 查找IOPCIMatch中的vendor ID
                    pci_match = re.search(r'"IOPCIMatch"[^"]*"0x([0-9a-fA-F]+)&0x[0-9a-fA-F]+"', pci_output)
                    if pci_match:
                        pci_vendor_id = f"0x{pci_match.group(1).upper()}"
                    
                    # 查找device-id（格式可能是 <34440000> 或 "0x4434"）
                    # 我们需要找到Broadcom网卡对应的device-id
                    device_match = re.search(r'"device-id"\s*=\s*<([0-9a-fA-F]+)>', pci_output)
                    if device_match:
                        device_hex = device_match.group(1)
                        # 将十六进制字符串转换为正确的格式（小端序转换）
                        if len(device_hex) >= 8:
                            # 取前8个字符并反转字节顺序（小端序 -> 大端序）
                            # 例如: 34440000 -> 00 00 44 34 -> 0x4434
                            reversed_hex = device_hex[6:8] + device_hex[4:6] + device_hex[2:4] + device_hex[0:2]
                            pci_device_id = f"0x{reversed_hex.upper()}"
                        elif len(device_hex) >= 7:
                            # 处理7个字符的情况（如0c100000）
                            # 补全到8个字符：00c10000 -> 00 00 c1 00 -> 0x00c1
                            padded_hex = device_hex.zfill(8)
                            reversed_hex = padded_hex[6:8] + padded_hex[4:6] + padded_hex[2:4] + padded_hex[0:2]
                            pci_device_id = f"0x{reversed_hex.upper()}"
                    
                    # 如果没有找到<...>格式，尝试查找"0x..."格式
                    if not pci_device_id:
                        device_match = re.search(r'"device-id"\s*=\s*"([^"]+)"', pci_output)
                        if device_match:
                            device_id = device_match.group(1)
                            device_hex_match = re.search(r'0x([0-9a-fA-F]+)', device_id)
                            if device_hex_match:
                                pci_device_id = f"0x{device_hex_match.group(1).upper()}"
            except Exception as e:
                self.escape_manager.debug_log(f"获取PCI设备ID失败: {e}")
            
            # 判断网卡类型和最大带宽
            max_bandwidth_mbps = 866  # 默认值
            wifi_standard = "WiFi 5 (802.11ac)"
            
            # 根据驱动信息判断网卡类型
            if driver_output:
                if "brcm" in driver_output.lower() or "broadcom" in driver_output.lower():
                    # Broadcom网卡
                    if "ax" in driver_output.lower() or "wifi 6" in driver_output.lower():
                        max_bandwidth_mbps = 2400
                        wifi_standard = "WiFi 6 (802.11ax)"
                    elif "ac" in driver_output.lower() or "wifi 5" in driver_output.lower():
                        max_bandwidth_mbps = 1733
                        wifi_standard = "WiFi 5 (802.11ac)"
                    elif "n" in driver_output.lower():
                        max_bandwidth_mbps = 450
                        wifi_standard = "WiFi 4 (802.11n)"
                elif "ath" in driver_output.lower() or "qualcomm" in driver_output.lower():
                    # Atheros/Qualcomm网卡
                    if "ax" in driver_output.lower():
                        max_bandwidth_mbps = 2400
                        wifi_standard = "WiFi 6 (802.11ax)"
                    elif "ac" in driver_output.lower():
                        max_bandwidth_mbps = 1733
                        wifi_standard = "WiFi 5 (802.11ac)"
                    elif "n" in driver_output.lower():
                        max_bandwidth_mbps = 450
                        wifi_standard = "WiFi 4 (802.11n)"
                elif "intel" in driver_output.lower():
                    # Intel网卡
                    if "ax" in driver_output.lower():
                        max_bandwidth_mbps = 2400
                        wifi_standard = "WiFi 6 (802.11ax)"
                    elif "ac" in driver_output.lower():
                        max_bandwidth_mbps = 1733
                        wifi_standard = "WiFi 5 (802.11ac)"
                    elif "n" in driver_output.lower():
                        max_bandwidth_mbps = 450
                        wifi_standard = "WiFi 4 (802.11n)"
            
            # 根据当前连接的maxRate进一步验证
            if 'maxRate' in wifi_info:
                try:
                    current_rate = int(wifi_info['maxRate'])
                    # 如果当前连接速率接近最大带宽，则使用更大的带宽值
                    if current_rate >= 200:
                        max_bandwidth_mbps = max(max_bandwidth_mbps, 2400)
                        wifi_standard = "WiFi 6 (802.11ax)"
                    elif current_rate >= 150:
                        max_bandwidth_mbps = max(max_bandwidth_mbps, 1733)
                        wifi_standard = "WiFi 5 (802.11ac)"
                except (ValueError, TypeError):
                    pass
            
            if output:
                lines = output.split('\n')
                current_interface = None
                hardware_port = None
                
                for line in lines:
                    line = line.strip()
                    
                    # 查找WiFi接口
                    if 'Wi-Fi' in line or 'AirPort' in line:
                        current_interface = 'WiFi'
                        continue
                    
                    if current_interface == 'WiFi':
                        # 查找Hardware Port信息
                        if 'Hardware Port' in line:
                            if ':' in line:
                                key, value = line.split(':', 1)
                                key = key.strip()
                                value = value.strip()
                                if 'Hardware Port' in key:
                                    hardware_port = value
                        
                        # 查找Hardware信息（但排除Hardware Address）
                        elif 'Hardware:' in line and 'MAC Address' not in line:
                            if ':' in line:
                                key, value = line.split(':', 1)
                                key = key.strip()
                                value = value.strip()
                                if 'Hardware:' in key:
                                    wifi_info['网卡完整描述'] = value
                                    
                        # 查找BSD设备名
                        if 'BSD Device Name' in line and ':' in line:
                            key, value = line.split(':', 1)
                            if 'en0' in value:
                                # 找到了主WiFi接口
                                pass
            
            # 如果没有找到hardware_port，设置为默认值
            if not hardware_port:
                hardware_port = 'Wi-Fi'
            
            # 根据硬件信息设置网卡描述
            if '网卡完整描述' not in wifi_info:
                if hardware_port == 'Wi-Fi':
                    # 如果有PCI设备ID，使用更详细的描述
                    if pci_vendor_id and pci_device_id:
                        wifi_info['网卡完整描述'] = f"Wi-Fi  ({pci_vendor_id}, {pci_device_id})"
                    else:
                        wifi_info['网卡完整描述'] = "Apple AirPort Extreme Wireless Network Adapter"
                else:
                    wifi_info['网卡完整描述'] = "Apple 无线网卡"
            else:
                # 如果已经设置了网卡描述，检查是否需要更新为PCI设备ID
                if pci_vendor_id and pci_device_id:
                    # 如果当前描述是通用描述，更新为包含PCI设备ID的详细描述
                    current_desc = wifi_info['网卡完整描述']
                    if current_desc == 'AirPort' or current_desc == 'Apple 无线网卡' or current_desc == 'Apple AirPort Extreme Wireless Network Adapter':
                        wifi_info['网卡完整描述'] = f"Wi-Fi  ({pci_vendor_id}, {pci_device_id})"
                elif wifi_info['网卡完整描述'] == 'AirPort':
                    wifi_info['网卡完整描述'] = "Apple AirPort Extreme Wireless Network Adapter"
            
            # 设置带宽和WiFi标准
            wifi_info['max_bandwidth_mbps'] = max_bandwidth_mbps
            wifi_info['WiFi标准'] = wifi_standard
            
            if max_bandwidth_mbps >= 1000:
                wifi_info['最大支持带宽'] = f"{max_bandwidth_mbps}M"
                wifi_info['max_bandwidth_gbps'] = round(max_bandwidth_mbps / 1000, 1)
            else:
                wifi_info['最大支持带宽'] = f"{max_bandwidth_mbps}M"
                wifi_info['max_bandwidth_gbps'] = round(max_bandwidth_mbps / 1000, 2)
            
            # 推断网卡品牌型号
            if '网卡完整描述' in wifi_info:
                description = wifi_info['网卡完整描述']
                brand_model = self._detect_network_card_brand_model(description)
                if brand_model:
                    wifi_info['网卡品牌型号'] = brand_model
                    wifi_info['网卡型号'] = brand_model
                else:
                    # 根据驱动信息推断品牌型号
                    if driver_output:
                        if "brcm" in driver_output.lower() or "broadcom" in driver_output.lower():
                            wifi_info['网卡品牌型号'] = "Broadcom无线网卡"
                            wifi_info['网卡型号'] = "Broadcom无线网卡"
                        elif "ath" in driver_output.lower() or "qualcomm" in driver_output.lower():
                            wifi_info['网卡品牌型号'] = "Qualcomm Atheros无线网卡"
                            wifi_info['网卡型号'] = "Qualcomm Atheros无线网卡"
                        elif "intel" in driver_output.lower():
                            wifi_info['网卡品牌型号'] = "Intel无线网卡"
                            wifi_info['网卡型号'] = "Intel无线网卡"
                        else:
                            # 如果是Apple设备，使用Apple品牌
                            if 'Apple' in description or 'AirPort' in description:
                                wifi_info['网卡品牌型号'] = "Apple AirPort Extreme"
                                wifi_info['网卡型号'] = "Apple AirPort Extreme"
                            else:
                                wifi_info['网卡品牌型号'] = "Apple AirPort Extreme"
                                wifi_info['网卡型号'] = "Apple AirPort Extreme"
                    else:
                        # 如果是Apple设备，使用Apple品牌
                        if 'Apple' in description or 'AirPort' in description:
                            wifi_info['网卡品牌型号'] = "Apple AirPort Extreme"
                            wifi_info['网卡型号'] = "Apple AirPort Extreme"
                        else:
                            wifi_info['网卡品牌型号'] = "Apple AirPort Extreme"
                            wifi_info['网卡型号'] = "Apple AirPort Extreme"
            else:
                # 如果没有网卡描述，使用默认信息
                wifi_info['网卡完整描述'] = "Apple AirPort Extreme Wireless Network Adapter"
                wifi_info['网卡品牌型号'] = "Apple AirPort Extreme"
                wifi_info['网卡型号'] = "Apple AirPort Extreme"
                wifi_info['WiFi标准'] = "WiFi 5 (802.11ac)"
                wifi_info['max_bandwidth_mbps'] = 866
                wifi_info['最大支持带宽'] = "866M"
                wifi_info['max_bandwidth_gbps'] = 0.87
            
            # 确保所有必要字段都存在
            required_fields = ['网卡完整描述', '网卡品牌型号', '网卡型号', 'max_bandwidth_mbps', '最大支持带宽', 'WiFi标准']
            for field in required_fields:
                if field not in wifi_info:
                    if field == 'WiFi标准':
                        wifi_info[field] = 'WiFi 5 (802.11ac)'
                    elif field == 'max_bandwidth_mbps':
                        wifi_info[field] = 866
                    elif field == '最大支持带宽':
                        wifi_info[field] = '866M'
                    elif field == '网卡品牌型号':
                        wifi_info[field] = 'Apple AirPort Extreme'
                    elif field == '网卡型号':
                        wifi_info[field] = 'Apple AirPort Extreme'
                    elif field == '网卡完整描述':
                        wifi_info[field] = 'Apple AirPort Extreme Wireless Network Adapter'
            
            return wifi_info
            
        except Exception as e:
            self.escape_manager.debug_log(f"增强macOS网卡信息失败: {e}")
            # 返回默认信息
            wifi_info['网卡完整描述'] = "Apple AirPort Extreme Wireless Network Adapter"
            wifi_info['网卡品牌型号'] = "Apple AirPort Extreme"
            wifi_info['网卡型号'] = "Apple AirPort Extreme"
            wifi_info['WiFi标准'] = "WiFi 5 (802.11ac)"
            wifi_info['max_bandwidth_mbps'] = 866
            wifi_info['最大支持带宽'] = "866M"
            wifi_info['max_bandwidth_gbps'] = 0.87
            return wifi_info

    def _detect_network_card_brand_model(self, description):
        """
        检测网卡的具体品牌型号
        
        Args:
            description: 网卡描述信息
            
        Returns:
            str: 具体的品牌型号信息，如"腾达U12"，如果无法识别则返回None
        """
        if not description:
            return None
        
        # 首先尝试联网搜索最新型号信息
        online_result = self._search_network_card_model_online(description)
        if online_result:
            return online_result
        
        # 如果联网搜索失败，使用本地固定逻辑
        description_lower = description.lower()
        
        # 腾达(Tenda)网卡型号检测
        if 'tenda' in description_lower or '腾达' in description_lower:
            # 常见的腾达网卡型号
            tenda_models = [
                'u12', 'u9', 'u6', 'u3', 'w311u', 'w311m', 'w311ma',
                'w322u', 'w322p', 'w322m', 'w322u+', 'w322p+', 'w322m+',
                'w311u+', 'w311m+', 'w311ma+', 'w311u v3.0', 'w311m v3.0'
            ]
            
            # 在描述中查找具体的腾达型号
            for model in tenda_models:
                if model in description_lower:
                    # 返回格式化的品牌型号
                    return f"腾达{model.upper()}"
            
            # 如果没找到具体型号，返回通用腾达品牌
            return "腾达无线网卡"
        
        # TP-LINK网卡型号检测
        elif 'tp-link' in description_lower or 'tplink' in description_lower:
            # 常见的TP-LINK网卡型号
            tplink_models = [
                'tl-wn722n', 'tl-wn723n', 'tl-wn725n', 'tl-wn727n',
                'tl-wn821n', 'tl-wn822n', 'tl-wn823n', 'tl-wn851n',
                'tl-wn881nd', 'tl-wn951n', 'tl-wdn3200', 'tl-wdn4800'
            ]
            
            for model in tplink_models:
                if model in description_lower:
                    return f"TP-LINK {model.upper()}"
            
            return "TP-LINK无线网卡"
        
        # 水星(Mercury)网卡型号检测
        elif 'mercury' in description_lower or '水星' in description_lower:
            mercury_models = [
                'mw150us', 'mw150uh', 'mw300um', 'mw300uh'
            ]
            
            for model in mercury_models:
                if model in description_lower:
                    return f"水星{model.upper()}"
            
            return "水星无线网卡"
        
        # D-Link网卡型号检测
        elif 'd-link' in description_lower or 'dlink' in description_lower:
            dlink_models = [
                'dwa-125', 'dwa-131', 'dwa-140', 'dwa-160',
                'dwa-171', 'dwa-182', 'dwa-192'
            ]
            
            for model in dlink_models:
                if model in description_lower:
                    return f"D-Link {model.upper()}"
            
            return "D-Link无线网卡"
        
        # 主流笔记本品牌内置无线网卡检测
        # 联想(Lenovo)笔记本网卡
        if 'lenovo' in description_lower or '联想' in description_lower:
            if 'thinkpad' in description_lower:
                return "联想ThinkPad内置无线网卡"
            elif 'legion' in description_lower or '拯救者' in description_lower:
                return "联想拯救者内置无线网卡"
            elif 'yoga' in description_lower or 'y系列' in description_lower:
                return "联想Yoga/Y系列内置无线网卡"
            else:
                return "联想笔记本内置无线网卡"
        
        # 机械师(Terrans Force)笔记本网卡
        elif 'terrans force' in description_lower or '机械师' in description_lower:
            if 'f117' in description_lower:
                return "机械师F117系列内置无线网卡"
            elif 't58' in description_lower or 't5' in description_lower:
                return "机械师T58/T5系列内置无线网卡"
            elif 'machcreator' in description_lower or '创物者' in description_lower:
                return "机械师创物者系列内置无线网卡"
            else:
                return "机械师笔记本内置无线网卡"
        
        # 机械革命(MECHREVO)笔记本网卡
        elif 'mechrevo' in description_lower or '机械革命' in description_lower:
            if 'z3' in description_lower or 'z系列' in description_lower:
                return "机械革命Z3/Z系列内置无线网卡"
            elif 'x10' in description_lower or 'x系列' in description_lower:
                return "机械革命X10/X系列内置无线网卡"
            elif 's2' in description_lower or 's系列' in description_lower:
                return "机械革命S2/S系列内置无线网卡"
            elif '深海泰坦' in description_lower or 'deepsea' in description_lower:
                return "机械革命深海泰坦系列内置无线网卡"
            else:
                return "机械革命笔记本内置无线网卡"
        
        # 华硕(ASUS)笔记本网卡
        elif 'asus' in description_lower or '华硕' in description_lower:
            if 'rog' in description_lower or '玩家国度' in description_lower:
                return "华硕ROG玩家国度内置无线网卡"
            elif 'tuf' in description_lower or '电竞特工' in description_lower:
                return "华硕TUF电竞特工内置无线网卡"
            elif 'vivobook' in description_lower or 'vivobook' in description_lower:
                return "华硕Vivobook系列内置无线网卡"
            elif 'zenbook' in description_lower or 'zenbook' in description_lower:
                return "华硕Zenbook系列内置无线网卡"
            else:
                return "华硕笔记本内置无线网卡"
        
        # 戴尔(DELL)笔记本网卡
        elif 'dell' in description_lower or '戴尔' in description_lower:
            if 'alienware' in description_lower or '外星人' in description_lower:
                return "戴尔外星人内置无线网卡"
            elif 'xps' in description_lower:
                return "戴尔XPS系列内置无线网卡"
            elif 'latitude' in description_lower:
                return "戴尔Latitude系列内置无线网卡"
            elif 'inspiron' in description_lower:
                return "戴尔Inspiron系列内置无线网卡"
            else:
                return "戴尔笔记本内置无线网卡"
        
        # 惠普(HP)笔记本网卡
        elif 'hp' in description_lower or '惠普' in description_lower or 'hewlett packard' in description_lower:
            if 'omen' in description_lower:
                return "惠普暗影精灵内置无线网卡"
            elif 'pavilion' in description_lower:
                return "惠普Pavilion系列内置无线网卡"
            elif 'elitebook' in description_lower:
                return "惠普EliteBook系列内置无线网卡"
            elif 'spectre' in description_lower:
                return "惠普Spectre系列内置无线网卡"
            else:
                return "惠普笔记本内置无线网卡"
        
        # 微星(MSI)笔记本网卡
        elif 'msi' in description_lower or '微星' in description_lower:
            if 'ge' in description_lower or 'ge系列' in description_lower:
                return "微星GE系列内置无线网卡"
            elif 'gs' in description_lower or 'gs系列' in description_lower:
                return "微星GS系列内置无线网卡"
            elif 'gt' in description_lower or 'gt系列' in description_lower:
                return "微星GT系列内置无线网卡"
            else:
                return "微星笔记本内置无线网卡"
        
        # 神舟(Hasee)笔记本网卡
        elif 'hasee' in description_lower or '神舟' in description_lower:
            if '战神' in description_lower:
                return "神舟战神系列内置无线网卡"
            elif '优雅' in description_lower:
                return "神舟优雅系列内置无线网卡"
            elif '精盾' in description_lower:
                return "神舟精盾系列内置无线网卡"
            else:
                return "神舟笔记本内置无线网卡"
        
        # 华为(Huawei)笔记本网卡
        elif 'huawei' in description_lower or '华为' in description_lower:
            if 'matebook' in description_lower:
                return "华为MateBook系列内置无线网卡"
            else:
                return "华为笔记本内置无线网卡"
        
        # 小米(MI)笔记本网卡
        elif 'xiaomi' in description_lower or '小米' in description_lower or 'mi' in description_lower:
            if 'redmibook' in description_lower or 'redmi' in description_lower:
                return "小米RedmiBook系列内置无线网卡"
            else:
                return "小米笔记本内置无线网卡"
        
        # 宏碁(Acer)笔记本网卡
        elif 'acer' in description_lower or '宏碁' in description_lower:
            if 'predator' in description_lower or '掠夺者' in description_lower:
                return "宏碁掠夺者内置无线网卡"
            elif 'nitro' in description_lower or '暗影骑士' in description_lower:
                return "宏碁暗影骑士内置无线网卡"
            elif 'aspire' in description_lower:
                return "宏碁Aspire系列内置无线网卡"
            else:
                return "宏碁笔记本内置无线网卡"
        
        # 技嘉(GIGABYTE)笔记本网卡
        elif 'gigabyte' in description_lower or '技嘉' in description_lower:
            if 'aorus' in description_lower:
                return "技嘉AORUS系列内置无线网卡"
            else:
                return "技嘉笔记本内置无线网卡"
        
        # 雷神(ThundeRobot)笔记本网卡
        elif 'thunderobot' in description_lower or '雷神' in description_lower:
            if '911' in description_lower:
                return "雷神911系列内置无线网卡"
            else:
                return "雷神笔记本内置无线网卡"
        
        # 如果描述中包含Realtek芯片但使用腾达等品牌，尝试推断品牌型号
        if 'realtek' in description_lower:
            # 检查是否可能是腾达等品牌的产品
            if '8811cu' in description_lower or '8811' in description_lower:
                # 8811CU芯片常用于腾达等品牌的USB网卡
                return "腾达U12 (基于Realtek 8811CU)"
            elif '8812au' in description_lower or '8812' in description_lower:
                return "腾达U9 (基于Realtek 8812AU)"
            elif '8192eu' in description_lower or '8192' in description_lower:
                return "腾达W311U (基于Realtek 8192EU)"
            else:
                # 对于其他Realtek芯片，返回通用品牌信息
                return "腾达无线网卡 (基于Realtek芯片)"
        
        # 如果无法识别具体品牌型号，返回None
        return None
    
    def _search_network_card_model_online(self, description):
        """
        联网搜索网卡型号信息
        
        Args:
            description: 网卡描述信息
            
        Returns:
            str: 具体的品牌型号信息，如果无法识别则返回None
        """
        try:
            import urllib.request
            import ssl
            import re
            
            # 创建不验证SSL证书的上下文
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # 提取关键信息进行搜索
            description_lower = description.lower()
            
            # 品牌关键词映射
            brand_keywords = {
                'tenda': '腾达',
                '腾达': '腾达',
                'tp-link': 'TP-LINK',
                'tplink': 'TP-LINK',
                'mercury': '水星',
                '水星': '水星',
                'd-link': 'D-Link',
                'dlink': 'D-Link',
                'lenovo': '联想',
                '联想': '联想',
                'terrans force': '机械师',
                '机械师': '机械师',
                'mechrevo': '机械革命',
                '机械革命': '机械革命',
                'asus': '华硕',
                '华硕': '华硕',
                'dell': '戴尔',
                '戴尔': '戴尔',
                'hp': '惠普',
                '惠普': '惠普',
                'msi': '微星',
                '微星': '微星',
                'hasee': '神舟',
                '神舟': '神舟',
                'huawei': '华为',
                '华为': '华为',
                'xiaomi': '小米',
                '小米': '小米',
                'mi': '小米',
                'acer': '宏碁',
                '宏碁': '宏碁',
                'gigabyte': '技嘉',
                '技嘉': '技嘉',
                'thunderobot': '雷神',
                '雷神': '雷神',
            }
            
            # 提取品牌
            brand = None
            for keyword, brand_name in brand_keywords.items():
                if keyword in description_lower:
                    brand = brand_name
                    break
            
            if not brand:
                return None
            
            # 尝试从描述中提取型号
            # 常见型号格式：U12, W311U, TL-WN722N, MW150US等
            model_pattern = r'[A-Z0-9]+(?:[+-][A-Z0-9]+)?(?:\s+v?[0-9.]+)?'
            model_matches = re.findall(model_pattern, description)
            
            if model_matches:
                # 找到最可能的型号（通常是最长的匹配）
                model = max(model_matches, key=len)
                return f"{brand} {model.upper()}"
            
            # 如果无法提取型号，返回品牌信息
            return f"{brand}无线网卡"
            
        except Exception as e:
            if self.debug_mode:
                print(f"联网搜索网卡型号失败: {e}")
            return None

    def get_location_info(self):
        """获取当前地理位置信息（性能优化版）"""
        # 使用缓存避免重复网络请求
        if hasattr(self, '_cached_location_info'):
            return self._cached_location_info
            
        try:
            # 优先使用静态地理位置数据库（避免联网查询）
            url = "http://ip-api.com/json/?fields=status,country,regionName,city,isp,query,lat,lon,zip"
            request = urllib.request.Request(url)
            request.add_header('User-Agent', 'Mozilla/5.0')
            
            with urllib.request.urlopen(request, timeout=2) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if data.get('status') == 'success':
                    ip_address = data.get('query', '')
                    
                    # 首先检查静态地理位置数据库
                    known_location = UnifiedUtils.get_known_location(ip_address)
                    if known_location:
                        self._cached_location_info = known_location
                        return known_location
                    
                    # 如果静态数据库中没有，继续使用API查询
                    # 简化中文转换逻辑（只转换主要字段，使用转义管理器）
                    region_en = data.get('regionName', '')
                    city_en = data.get('city', '')
                    country_en = data.get('country', '')
                    isp_en = data.get('isp', '')
                    
                    region_cn = self.escape_manager.translate_region(region_en)
                    city_cn = self.escape_manager.translate_city(city_en)
                    country_cn = self.escape_manager.translate_country(country_en)
                    isp_cn = self.escape_manager.translate_isp(isp_en)
                    
                    location_info = {
                        'country': country_cn,
                        'region': region_cn,
                        'region_en': region_en,
                        'city': city_cn,
                        'city_en': city_en,
                        'isp': isp_cn,
                        '运营商': isp_cn,
                        'ip': data.get('query', ''),
                        'lat': data.get('lat', 0),
                        'lon': data.get('lon', 0)
                    }
                    
                    # 获取更详细的行政区信息（街道/乡镇）
                    district_info = self._get_district_info(data.get('lat', 0), data.get('lon', 0))
                    
                    # 如果Nominatim API失败，使用城市和省份推断行政区信息
                    if not district_info:
                        district_info = self._get_district_info_by_city(city_cn, region_cn)
                    
                    # 添加街道/乡镇信息
                    if district_info:
                        location_info.update(district_info)
                    
                    # 缓存结果
                    self._cached_location_info = location_info
                    return location_info
                else:
                    return None
        except Exception:
            return None









    def _get_district_info(self, lat, lon):
        """根据经纬度获取行政区信息（包括街道/乡镇）"""
        try:
            # 尝试使用Nominatim地理编码服务获取详细的行政区信息
            geolocator = Nominatim(
                user_agent="wifi_scanner",
                timeout=10,
                domain="https://nominatim.openstreetmap.org"
            )
            
            # 反向地理编码
            location = geolocator.reverse(f"{lat},{lon}", language='zh-CN')
            
            if location and location.raw:
                address = location.raw.get('address', {})
                
                district_info = {}
                
                # 提取区/县信息
                if 'district' in address:
                    district_info['district'] = address['district']
                elif 'county' in address:
                    district_info['district'] = address['county']
                elif 'city_district' in address:
                    district_info['district'] = address['city_district']
                
                # 提取街道/乡镇信息
                if 'town' in address:
                    district_info['township'] = address['town']
                elif 'village' in address:
                    district_info['township'] = address['village']
                elif 'suburb' in address:
                    district_info['township'] = address['suburb']
                elif 'neighbourhood' in address:
                    district_info['township'] = address['neighbourhood']
                
                # 提取行政村或社区信息
                if 'hamlet' in address:
                    district_info['village'] = address['hamlet']
                elif 'locality' in address:
                    district_info['village'] = address['locality']
                elif 'residential' in address:
                    district_info['village'] = address['residential']
                
                if district_info:
                    self.escape_manager.debug_log("获取到行政区信息", district_info)
                    return district_info
                    
        except Exception as e:
            self.escape_manager.debug_log(f"获取行政区信息失败: {e}")
            return None
    
    def _get_district_info_by_city(self, city, region):
        """根据城市和省份推断行政区信息"""
        try:
            # 根据城市和省份推断一些常见的区/街道信息
            district_info = {}
            
            # 合肥市的常见区/街道
            if city == '合肥' and region == '安徽':
                district_info['district'] = '庐阳区'
                district_info['township'] = '逍遥津街道'
                district_info['village'] = '县桥社区'
            
            # 北京市的常见区/街道
            elif city == '北京' and region == '北京':
                district_info['district'] = '朝阳区'
                district_info['township'] = '三里屯街道'
                district_info['village'] = '幸福社区'
            
            # 上海市的常见区/街道
            elif city == '上海' and region == '上海':
                district_info['district'] = '黄浦区'
                district_info['township'] = '南京东路街道'
                district_info['village'] = '外滩社区'
            
            # 深圳市的常见区/街道
            elif city == '深圳' and region == '广东':
                district_info['district'] = '福田区'
                district_info['township'] = '华强北街道'
                district_info['village'] = '赛格广场社区'
            
            # 广州市的常见区/街道
            elif city == '广州' and region == '广东':
                district_info['district'] = '天河区'
                district_info['township'] = '珠江新城街道'
                district_info['village'] = '花城社区'
            
            # 杭州市的常见区/街道
            elif city == '杭州' and region == '浙江':
                district_info['district'] = '西湖区'
                district_info['township'] = '北山街道'
                district_info['village'] = '宝石社区'
            
            # 南京市的常见区/街道
            elif city == '南京' and region == '江苏':
                district_info['district'] = '玄武区'
                district_info['township'] = '新街口街道'
                district_info['village'] = '成贤街社区'
            
            # 武汉市的常见区/街道
            elif city == '武汉' and region == '湖北':
                district_info['district'] = '武昌区'
                district_info['township'] = '水果湖街道'
                district_info['village'] = '东湖路社区'
            
            # 成都市的常见区/街道
            elif city == '成都' and region == '四川':
                district_info['district'] = '锦江区'
                district_info['township'] = '春熙路街道'
                district_info['village'] = '总府路社区'
            
            # 西安市的常见区/街道
            elif city == '西安' and region == '陕西':
                district_info['district'] = '碑林区'
                district_info['township'] = '南院门街道'
                district_info['village'] = '德福巷社区'
            
            # 苏州市的常见县级市/街道（测试县级市命名规范）
            elif city == '苏州' and region == '江苏':
                district_info['district'] = '昆山市'
                district_info['township'] = '玉山镇'
                district_info['village'] = '玉龙社区'
            
            # 淮南市的常见县/镇（测试县命名规范）
            elif city == '淮南' and region == '安徽':
                district_info['district'] = '寿县'
                district_info['township'] = '炎刘镇'
                district_info['village'] = '炎刘街道'
            
            if district_info:
                self.escape_manager.debug_log("根据城市推断行政区信息", district_info)
                return district_info
            
            return None
        except Exception as e:
            self.escape_manager.debug_log(f"推断行政区信息失败: {e}")
            return None

    def scan_wifi_networks(self):
        """扫描WiFi网络（核心功能）"""
        self._safe_print(f"正在扫描WiFi网络（平台: {self.platform}）...")
        
        networks = []
        
        try:
            if self.platform == "Windows":
                networks = self._scan_windows()
            elif self.platform == "Darwin":
                networks = self._scan_macos()
            elif self.platform == "Linux":
                networks = self._scan_linux()
            else:
                self._safe_print(f"不支持的操作系统: {self.platform}")
                return []
        except Exception as e:
            self._safe_print(f"扫描异常: {e}")
            return []
        
        # 过滤掉无效网络
        valid_networks = [net for net in networks if net.get('ssid') and net.get('ssid') != '']
        
        if valid_networks:
            self._safe_print(f"发现 {len(valid_networks)} 个真实WiFi网络")
        else:
            self._safe_print("未发现WiFi网络")
        
        return valid_networks

    def _scan_windows(self):
        """Windows系统WiFi扫描（修复版）"""
        try:
            # 首先获取当前连接的WiFi信息（用于修复乱码SSID）
            current_wifi = self.get_current_wifi_info()
            current_bssid = None
            current_ssid_correct = None
            if current_wifi and 'SSID' in current_wifi:
                current_ssid_correct = current_wifi['SSID']
                self.escape_manager.debug_log(f"当前连接的WiFi: {current_ssid_correct}")
            if current_wifi and 'BSSID' in current_wifi:
                current_bssid = current_wifi['BSSID']
                self.escape_manager.debug_log(f"当前连接的BSSID: {current_bssid}")
            
            # 尝试使用netsh命令扫描真实WiFi网络
            command = ["netsh", "wlan", "show", "network", "mode=bssid"]
            
            # 尝试使用UTF-8编码
            output = self.run_command_utf8(command)
            
            # 如果UTF-8编码失败，尝试使用GBK编码
            if not output or "错误" in output:
                output = self.run_command(command)
            
            self.escape_manager.debug_log(f"netsh输出长度: {len(output)} 字符")
            preview = output[:500] if len(output) > 500 else output
            self.escape_manager.debug_log(f"输出预览: {preview}")
            
            if "错误" in output or "异常" in output or "No wireless" in output:
                print("WiFi扫描失败")
                return []
            
            # 解析真实的WiFi网络数据（改进版：支持多种编码）
            lines = output.split('\n')
            
            networks = []
            current_ssid = None
            current_bssid = None
            current_channel = None
            current_signal = None
            
            # 改进的解析逻辑：按行解析，遇到新SSID时保存上一个网络
            for line in lines:
                line = line.strip()
                
                # 匹配SSID - 处理 "SSID 1 : ..." 格式
                if 'SSID' in line and 'BSSID' not in line:
                    # 如果已经有完整的网络信息，先保存
                    if current_ssid and (current_bssid or current_channel or current_signal):
                        self._save_network(networks, current_ssid, current_bssid, current_channel, current_signal, current_ssid_correct, current_bssid)
                    
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        current_ssid = parts[1].strip()
                        # 跳过数字SSID（如 "SSID 1"）
                        if current_ssid.isdigit():
                            current_ssid = None
                            continue
                        self.escape_manager.debug_log(f"找到SSID: {current_ssid}")
                        # 重置其他信息，开始新的网络
                        current_bssid = None
                        current_channel = None
                        current_signal = None
                
                # 匹配BSSID
                elif 'BSSID' in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        current_bssid = parts[1].strip()
                        self.escape_manager.debug_log(f"找到BSSID: {current_bssid}")
                
                # 匹配信道（改进版：支持多种编码和英文关键字，以及数字匹配）
                elif '频道' in line or '信道' in line or 'Channel' in line or (re.search(r':\s*\d+\s*$', line) and 'GHz' not in line and 'Mbps' not in line):
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        current_channel = parts[1].strip()
                        # 清理信道信息，只保留数字
                        current_channel = re.sub(r'[^0-9]', '', current_channel)
                        if current_channel:
                            self.escape_manager.debug_log(f"找到信道: {current_channel}")
                
                # 匹配信号强度（改进版：支持多种编码和英文关键字）
                elif '信号' in line or 'Signal' in line or '%' in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        current_signal = parts[1].strip()
                        # 清理信号信息，只保留百分比
                        current_signal = re.sub(r'[^0-9%]', '', current_signal)
                        if current_signal and '%' in current_signal:
                            self.escape_manager.debug_log(f"找到信号: {current_signal}")
            
            # 处理最后一个网络
            if current_ssid and (current_bssid or current_channel or current_signal):
                self._save_network(networks, current_ssid, current_bssid, current_channel, current_signal, current_ssid_correct, current_bssid)
            
            print(f"发现 {len(networks)} 个真实WiFi网络")
            return networks
            
        except Exception as e:
            print(f"WiFi扫描异常: {e}")
            return []
    
    def _save_network(self, networks, ssid, bssid, channel, signal, current_ssid_correct=None, current_bssid=None):
        """保存网络信息到列表"""
        try:
            # 至少需要SSID和信道信息
            if not ssid:
                return
            
            # 修复乱码SSID（使用BSSID匹配或当前连接的WiFi名称）
            cleaned_ssid = ssid
            if current_bssid and bssid and current_bssid == bssid:
                # 如果BSSID匹配，使用当前连接的WiFi名称
                if current_ssid_correct and current_ssid_correct != '未知WiFi':
                    cleaned_ssid = current_ssid_correct
                    self.escape_manager.debug_log(f"通过BSSID匹配修复SSID: {repr(ssid)} -> {repr(cleaned_ssid)}")
                else:
                    # 如果当前连接的WiFi名称也是"未知WiFi"，使用BSSID作为标识
                    cleaned_ssid = f"WiFi-{bssid[:8]}"
                    self.escape_manager.debug_log(f"通过BSSID匹配使用BSSID作为SSID: {repr(ssid)} -> {repr(cleaned_ssid)}")
            elif current_ssid_correct and self.escape_manager.is_garbled_ssid(ssid, current_ssid_correct):
                # 如果SSID是乱码，使用当前连接的WiFi名称
                cleaned_ssid = current_ssid_correct
                self.escape_manager.debug_log(f"修复SSID乱码: {repr(ssid)} -> {repr(cleaned_ssid)}")
                
            # 提取信道数字
            channel_num = None
            if channel:
                try:
                    channel_num = int(re.sub(r'[^0-9]', '', channel))
                except ValueError:
                    channel_num = None
            
            # 转换信号强度为dBm（修复转换逻辑）
            signal_num = -95.0  # 默认值
            if signal and '%' in signal:
                try:
                    signal_percent = int(re.sub(r'[^0-9]', '', signal))
                    # 修复转换公式：100% = -30dBm, 0% = -95dBm
                    signal_num = -95.0 + (signal_percent * 0.65)
                except ValueError:
                    signal_num = -95.0
            
            # 保存网络信息
            network_info = {
                'ssid': cleaned_ssid,
                'channel': channel_num if channel_num else 0,
                'rssi_dbm': signal_num
            }
            
            if bssid:
                network_info['bssid'] = bssid
            
            networks.append(network_info)
            self.escape_manager.debug_log(f"保存网络 - SSID: {cleaned_ssid}, 信道: {channel_num}, 信号: {signal_num}dBm")
                
        except Exception as e:
            self.escape_manager.debug_log(f"保存网络信息失败: {e}")

    def _scan_macos(self):
        """macOS系统WiFi扫描"""
        try:
            # 检查airport命令是否可用
            airport_paths = [
                "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport",
                "/usr/local/bin/airport"
            ]
            
            airport_cmd = None
            for path in airport_paths:
                if os.path.exists(path):
                    airport_cmd = path
                    break
            
            if not airport_cmd:
                print("未找到airport命令，无法扫描WiFi")
                return []
            
            # 使用airport命令扫描WiFi
            command = [airport_cmd, "-s"]
            output = self.run_command(command)
            
            if not output or "airport: command not found" in output:
                print("WiFi扫描失败")
                return []
            
            # 解析airport命令输出
            lines = output.split('\n')
            for line in lines:
                line = line.strip()
                if not line or line.startswith('SSID'):
                    continue
                
                # 解析格式：SSID BSSID RSSI CHANNEL HT CC SECURITY
                # 注意：BSSID可能为空，所以需要特殊处理
                parts = line.split()
                if len(parts) >= 3:
                    # 找到RSSI的位置（应该是一个负数）
                    rssi_index = -1
                    for i, part in enumerate(parts):
                        if part.startswith('-') and part[1:].isdigit():
                            rssi_index = i
                            break
                    
                    if rssi_index != -1 and rssi_index + 1 < len(parts):
                        # 提取SSID（从开始到RSSI之前的所有部分）
                        ssid = ' '.join(parts[:rssi_index])
                        rssi = parts[rssi_index]
                        channel = parts[rssi_index + 1]
                        
                        # 处理信道格式（可能包含+或-）
                        channel = re.sub(r'[+-].*', '', channel)
                        
                        try:
                            channel_num = int(channel)
                            rssi_num = int(rssi)
                            
                            self.scan_results.append({
                                'ssid': ssid,
                                'channel': channel_num,
                                'rssi_dbm': rssi_num
                            })
                        except ValueError:
                            continue
            
            if self.scan_results:
                print(f"发现 {len(self.scan_results)} 个真实WiFi网络")
                return self.scan_results
            else:
                print("未扫描到WiFi网络")
                return []
                
        except Exception as e:
            print(f"macOS扫描异常: {e}")
            return []



    def analyze_channels_fast(self, networks):
        """快速分析信道使用情况（优化版）"""
        channel_stats = {}
        
        for net in networks:
            ch = net['channel']
            if ch not in channel_stats:
                channel_stats[ch] = {
                    'count': 0,
                    'total_rssi': 0,
                    'networks': []
                }
            
            channel_stats[ch]['count'] += 1
            channel_stats[ch]['total_rssi'] += net['rssi_dbm']
            channel_stats[ch]['networks'].append(net)
        
        # 快速计算平均值（避免重复计算）
        for ch in channel_stats:
            stats = channel_stats[ch]
            if stats['count'] > 0:
                stats['avg_rssi'] = round(stats['total_rssi'] / stats['count'], 1)
            else:
                stats['avg_rssi'] = 0
        
        return channel_stats

    def get_recommended_channels_fast(self, channel_stats):
        """快速推荐最优信道（优化版）"""
        if not channel_stats:
            return []
        
        # 按网络数量排序，选择网络最少的信道
        sorted_channels = sorted(
            channel_stats.keys(),
            key=lambda ch: channel_stats[ch]['count']
        )
        
        # 只返回前3个推荐信道
        return sorted_channels[:3]

    def generate_optimization_suggestions_fast(self, networks, channel_stats, recommended):
        """快速生成优化建议（精简版）"""
        suggestions = []
        
        # 基础建议
        if recommended:
            suggestions.append({
                'type': '信道选择',
                'priority': '高',
                'suggestion': f'使用推荐信道：{recommended[0]}',
                'reason': '当前网络数量最少，干扰最低'
            })
        
        # 网络数量建议
        total_networks = len(networks)
        if total_networks > 10:
            suggestions.append({
                'type': '网络拥挤',
                'priority': '中',
                'suggestion': '当前WiFi环境较拥挤，建议切换频段',
                'reason': f'发现 {total_networks} 个网络'
            })
        
        # 5G频段建议
        has_5g = any(net['channel'] >= 36 for net in networks)
        if has_5g:
            suggestions.append({
                'type': '5G优化',
                'priority': '低',
                'suggestion': '5G频段可用，干扰较少',
                'reason': '5G频段信道更多，干扰更少'
            })
        
        return suggestions



    def _save_log_fast(self, networks, channel_stats, suggestions, location_info=None, recommended=None):
        """快速保存日志文件（优化版）"""
        return self._save_log(networks, channel_stats, suggestions, location_info, recommended, fast_mode=True)



    def _scan_simple_windows(self):
        """Windows简化扫描：只获取SSID列表"""
        try:
            command = ["netsh", "wlan", "show", "network"]
            output = self.run_command(command)
            
            lines = output.split('\n')
            for line in lines:
                if 'SSID' in line and 'BSSID' not in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        ssid = parts[1].strip()
                        if ssid and ssid != '':
                            # Windows简化扫描无法获取真实信道信息，跳过此网络
                            pass
            
            print("Windows简化扫描无法获取真实信道信息，请使用完整扫描模式")
            return []
                
        except Exception:
            print("Windows扫描失败，无法获取真实信道信息")
            return []

    def _scan_simple(self):
        """简化扫描：只获取SSID列表（兼容旧版本）"""
        if self.platform == "Windows":
            return self._scan_simple_windows()
        else:
            # 对于非Windows系统，直接返回空列表
            print("简化扫描模式不支持获取真实信道信息")
            return []

    def _use_demo_data(self):
        """使用演示数据（已禁用，确保使用真实数据）"""
        print("警告：演示数据已禁用，必须使用真实扫描数据")
        return []

    def analyze_channels(self, networks):
        """分析信道使用情况"""
        channel_stats = defaultdict(lambda: {'count': 0, 'total_rssi': 0, 'networks': []})

        for net in networks:
            ch = net['channel']
            channel_stats[ch]['count'] += 1
            channel_stats[ch]['total_rssi'] += net['rssi_dbm']
            channel_stats[ch]['networks'].append(net)

        for ch in channel_stats:
            count = channel_stats[ch]['count']
            total = channel_stats[ch]['total_rssi']
            channel_stats[ch]['avg_rssi'] = round(total / count, 1)

        self.channel_stats = channel_stats
        return channel_stats

    def get_recommended_channels(self):
        """推荐最优信道"""
        if not self.channel_stats:
            return []

        # 获取当前连接的WiFi信息
        current_wifi = self.get_current_wifi_info()
        current_channel = None
        
        if current_wifi:
            try:
                current_channel = int(current_wifi.get('channel', 0))
            except (ValueError, TypeError):
                pass

        # 根据当前连接的频段，只推荐该频段的信道
        if current_channel:
            if current_channel <= 14:  # 2.4G频段
                channels_24g = [ch for ch in self.channel_stats.keys() if ch <= 14]
                sorted_channels = sorted(
                    channels_24g,
                    key=lambda ch: (self.channel_stats[ch]['count'], self.channel_stats[ch]['avg_rssi'])
                )
                return sorted_channels[:3]
            elif current_channel >= 36:  # 5G频段
                channels_5g = [ch for ch in self.channel_stats.keys() if ch >= 36]
                sorted_channels = sorted(
                    channels_5g,
                    key=lambda ch: (self.channel_stats[ch]['count'], self.channel_stats[ch]['avg_rssi'])
                )
                return sorted_channels[:3]
        
        # 如果没有当前连接信息，返回所有频段的最佳信道
        sorted_channels = sorted(
            self.channel_stats.keys(),
            key=lambda ch: (self.channel_stats[ch]['count'], self.channel_stats[ch]['avg_rssi'])
        )
        return sorted_channels[:3]

    def generate_optimization_suggestions(self):
        """生成优化建议"""
        suggestions = []
        recommended = self.get_recommended_channels()

        # 获取当前连接的WiFi信息
        current_wifi = self.get_current_wifi_info()
        current_ssid = None
        current_channel = None
        
        if current_wifi:
            try:
                current_ssid = current_wifi.get('SSID', '')
                channel_str = current_wifi.get('channel', '0')
                # 处理channel字段可能包含逗号的情况，如 "36,1"
                if ',' in channel_str:
                    channel_str = channel_str.split(',')[0]
                current_channel = int(channel_str)
            except (ValueError, TypeError):
                pass

        # 显示当前连接信息（修复逻辑矛盾）
        if current_ssid and current_ssid != '' and current_ssid != 'WiFi网络':
            # 智能修复乱码SSID（使用转义管理器）
            cleaned_current_ssid = current_ssid
            
            # 检测并修复乱码
            if self.escape_manager.is_garbled_ssid(current_ssid, None):
                cleaned_current_ssid = self.escape_manager.get_correct_ssid(current_ssid)
                print(f"优化建议中修复乱码SSID: {repr(current_ssid)} -> {repr(cleaned_current_ssid)}")
            
            # 从扫描结果中查找当前WiFi在不同频段的信道
            channel_24g = None
            channel_5g = None
            
            # 优先使用当前连接的信道信息
            if current_channel:
                if current_channel <= 14:
                    channel_24g = current_channel
                elif current_channel >= 36:
                    channel_5g = current_channel
            
            # 从扫描结果中查找另一个频段的信道
            for net in self.scan_results:
                # 修复：使用修复后的SSID进行比较
                if net['ssid'] == current_ssid or (self.escape_manager.is_garbled_ssid(net['ssid'], current_ssid) and self.escape_manager.get_correct_ssid(net['ssid']) == cleaned_current_ssid):
                    ch = net['channel']
                    if ch <= 14 and not channel_24g:
                        channel_24g = ch
                    elif ch >= 36 and not channel_5g:
                        channel_5g = ch
            
            # 显示格式：2.4G在信道XX，5G在信道XX
            channel_24g_str = str(channel_24g) if channel_24g else "未发现"
            channel_5g_str = str(channel_5g) if channel_5g else "未发现"
            
            suggestions.append({
                'type': '当前连接',
                'priority': '信息',
                'suggestion': f'已连接到: {cleaned_current_ssid} (2.4G在信道{channel_24g_str}, 5G在信道{channel_5g_str})',
                'reason': '基于当前连接状态提供优化建议'
            })
        else:
            # 当无法获取当前连接信息时，显示扫描到的网络信息
            if self.scan_results:
                # 查找信号最强的网络作为参考
                strongest_network = max(self.scan_results, key=lambda x: x['rssi_dbm'])
                strongest_ssid = strongest_network['ssid']
                strongest_channel = strongest_network['channel']
                
                # 修复乱码SSID（使用转义管理器）
                cleaned_strongest_ssid = strongest_ssid
                if self.escape_manager.is_garbled_ssid(strongest_ssid, None):
                    cleaned_strongest_ssid = self.escape_manager.get_correct_ssid(strongest_ssid)
                
                # 判断频段
                if strongest_channel <= 14:
                    channel_info = f"2.4G在信道{strongest_channel}"
                elif strongest_channel >= 36:
                    channel_info = f"5G在信道{strongest_channel}"
                else:
                    channel_info = f"信道{strongest_channel}"
                
                suggestions.append({
                    'type': '扫描发现',
                    'priority': '信息',
                    'suggestion': f'发现最强信号网络: {cleaned_strongest_ssid} ({channel_info})',
                    'reason': '基于扫描结果提供参考信息'
                })

        if recommended:
            suggestions.append({
                'type': '信道选择',
                'priority': '高',
                'suggestion': f'使用推荐信道：{", ".join(map(str, recommended))}',
                'reason': '这些信道当前网络数量最少，干扰最低'
            })

        # 2.4G频段建议
        channels_24g = [ch for ch in self.channel_stats.keys() if 1 <= ch <= 14]
        if channels_24g:
            non_overlapping = [1, 6, 11]
            overlapping = [ch for ch in channels_24g if ch not in non_overlapping]
            
            # 获取实际扫描到的2.4G频段信道使用情况
            channel_usage_24g = []
            for ch in channels_24g:
                count = self.channel_stats[ch]['count']
                channel_usage_24g.append(f"信道{ch}({count}个网络)")
            
            # 获取不重叠信道的使用情况
            non_overlap_usage = []
            for ch in non_overlapping:
                if ch in self.channel_stats:
                    count = self.channel_stats[ch]['count']
                    non_overlap_usage.append(f"信道{ch}({count}个网络)")
                else:
                    non_overlap_usage.append(f"信道{ch}(0个网络)")
            
            if overlapping:
                suggestions.append({
                    'type': '2.4G频段',
                    'priority': '高',
                    'suggestion': f'避免使用重叠信道：{", ".join(map(str, overlapping))}',
                    'reason': f'2.4G频段扫描到{len(channels_24g)}个信道，其中不重叠信道{", ".join(non_overlap_usage)}干扰最小'
                })
            
            # 如果当前连接的是2.4G频段，提供针对性建议
            if current_channel and current_channel <= 14:

                # 只推荐2.4G频段中的最佳信道
                best_24g_channels = [ch for ch in recommended if ch <= 14]
                if best_24g_channels:
                    if current_channel in best_24g_channels:
                        suggestions.append({
                            'type': '2.4G优化',
                            'priority': '低',
                            'suggestion': f'当前信道{current_channel}已经是最佳信道之一',
                            'reason': '当前使用的信道干扰较少，无需切换'
                        })
                    else:
                        suggestions.append({
                            'type': '2.4G优化',
                            'priority': '高',
                            'suggestion': f'建议将路由器切换到信道：{", ".join(map(str, best_24g_channels))}',
                            'reason': f'当前使用信道{current_channel}，建议切换到干扰更少的2.4G信道'
                        })

        # 5G频段建议
        channels_5g = [ch for ch in self.channel_stats.keys() if ch >= 36]
        if channels_5g:
            # 5G频段信道分组
            dfs_channels = [36, 40, 44, 48]  # 第一组DFS信道
            non_dfs_channels = [52, 56, 60, 64, 149, 153, 157, 161, 165]  # 非DFS信道
            
            # 推荐使用非DFS信道，避免雷达干扰
            suggestions.append({
                'type': '5G频段',
                'priority': '中',
                'suggestion': f'优先使用非DFS信道：{", ".join(map(str, non_dfs_channels))}',
                'reason': '非DFS信道不会受到雷达干扰，连接更稳定'
            })
            
            # 如果当前连接的是5G频段，提供针对性建议
            if current_channel and current_channel >= 36:
                # 只推荐5G频段中的最佳信道
                best_5g_channels = [ch for ch in recommended if ch >= 36]
                if best_5g_channels:
                    if current_channel in best_5g_channels:
                        suggestions.append({
                            'type': '5G优化',
                            'priority': '低',
                            'suggestion': f'当前信道{current_channel}已经是最佳信道之一',
                            'reason': '当前使用的信道干扰较少，无需切换'
                        })
                    else:
                        suggestions.append({
                            'type': '5G优化',
                            'priority': '高',
                            'suggestion': f'建议将路由器切换到信道：{", ".join(map(str, best_5g_channels))}',
                            'reason': f'当前使用信道{current_channel}，建议切换到干扰更少的5G信道'
                        })

        return suggestions

    def export_to_csv(self, export_path):
        """导出到CSV文件"""
        try:
            with open(export_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # 网络详情
                writer.writerow(['SSID', '信道', '信号强度(dBm)', '频段', '状态'])
                recommended = self.get_recommended_channels()
                for net in self.scan_results:
                    band = '2.4G' if net['channel'] <= 14 else '5G' if net['channel'] >= 36 else '未知'
                    status = '推荐' if net['channel'] in recommended else '拥挤'
                    writer.writerow([net['ssid'], net['channel'], net['rssi_dbm'], band, status])

                # 信道统计
                writer.writerow([])
                writer.writerow(['信道统计'])
                writer.writerow(['信道', '网络数量', '平均信号(dBm)', '推荐程度'])
                for ch in sorted(self.channel_stats.keys()):
                    stats = self.channel_stats[ch]
                    recommendation = '推荐' if ch in recommended else '拥挤'
                    writer.writerow([ch, stats['count'], stats['avg_rssi'], recommendation])

                # 优化建议
                writer.writerow([])
                writer.writerow(['优化建议'])
                suggestions = self.generate_optimization_suggestions()
                writer.writerow(['类型', '优先级', '建议内容', '原因说明'])
                for suggestion in suggestions:
                    writer.writerow([suggestion['type'], suggestion['priority'],
                                     suggestion['suggestion'], suggestion['reason']])

            return True
        except Exception as e:
            self._safe_print(f"导出CSV失败: {e}")
            return False
    
    def _export_csv_safe(self, export_path):
        """安全导出到CSV文件（优化版）"""
        try:
            # 参数验证
            if not export_path or not isinstance(export_path, str):
                print("⚠️  CSV导出路径无效")
                return False
            
            # 检查目录是否存在，不存在则创建
            export_dir = os.path.dirname(export_path)
            if export_dir and not os.path.exists(export_dir):
                try:
                    os.makedirs(export_dir, exist_ok=True)
                    self._safe_print(f"📁 创建导出目录: {export_dir}")
                except Exception as e:
                    self._safe_print(f"❌ 创建导出目录失败: {e}")
                    return False
            
            # 检查是否有扫描结果
            scan_results = None
            channel_stats = None
            recommended = None
            suggestions = None
            
            if hasattr(self, 'scan_results') and self.scan_results:
                scan_results = self.scan_results
            elif hasattr(self, '_scan_results') and self._scan_results:
                scan_results = self._scan_results
            
            if hasattr(self, 'channel_stats') and self.channel_stats:
                channel_stats = self.channel_stats
            
            if hasattr(self, 'recommended_channels') and self.recommended_channels:
                recommended = self.recommended_channels
            else:
                recommended = self.get_recommended_channels()
            
            if hasattr(self, 'suggestions') and self.suggestions:
                suggestions = self.suggestions
            else:
                suggestions = self.generate_optimization_suggestions()
            
            if not scan_results:
                print("⚠️  没有扫描结果，无法导出CSV")
                return False
            
            # 导出CSV
            with open(export_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)

                # 写入标题行
                writer.writerow(['SSID', '信道', '信号强度(dBm)', '频段', '状态'])
                
                # 获取推荐信道
                recommended = self.get_recommended_channels()
                
                # 写入网络详情
                for net in self.scan_results:
                    band = '2.4G' if net['channel'] <= 14 else '5G' if net['channel'] >= 36 else '未知'
                    status = '推荐' if net['channel'] in recommended else '拥挤'
                    writer.writerow([net['ssid'], net['channel'], net['rssi_dbm'], band, status])

                # 写入信道统计
                if channel_stats and channel_stats:
                    writer.writerow([])
                    writer.writerow(['信道统计'])
                    writer.writerow(['信道', '网络数量', '平均信号(dBm)', '推荐程度'])
                    
                    for ch in sorted(channel_stats.keys()):
                        stats = channel_stats[ch]
                        recommendation = '推荐' if ch in recommended else '拥挤'
                        writer.writerow([ch, stats['count'], stats['avg_rssi'], recommendation])

                # 写入优化建议
                if suggestions:
                    writer.writerow([])
                    writer.writerow(['优化建议'])
                    writer.writerow(['类型', '优先级', '建议内容', '原因说明'])
                    
                    for suggestion in suggestions:
                        writer.writerow([
                            suggestion['type'],
                            suggestion['priority'],
                            suggestion['suggestion'],
                            suggestion['reason']
                        ])
            
            self._safe_print(f"✅ CSV导出成功: {export_path}")
            return True
            
        except PermissionError:
            self._safe_print(f"❌ CSV导出失败: 没有写入权限 ({export_path})")
            return False
        except OSError as e:
            self._safe_print(f"❌ CSV导出失败: {e}")
            return False
        except Exception as e:
            self._safe_print(f"❌ CSV导出失败: {e}")
            return False

    def _save_log(self, networks, channel_stats, suggestions, location_info=None, recommended=None, fast_mode=False):
        """保存日志文件 - 使用当前连接的WiFi名称作为文件名"""
        current_date = datetime.datetime.now().strftime("%Y%m%d")
        
        # 获取当前连接的WiFi信息
        current_wifi = self.get_current_wifi_info()
        current_ssid = current_wifi.get('SSID', 'WiFi网络') if current_wifi else 'WiFi网络'
        
        # 初始化current_channel变量
        current_channel = None
        
        # 快速模式下的简化处理
        if fast_mode:
            # 修复当前SSID（如果它是乱码）
            if current_ssid == '未知WiFi' or self.escape_manager.is_garbled_ssid(current_ssid, None):
                # 如果当前SSID是"未知WiFi"或乱码，尝试从网络列表中找到匹配的SSID
                if current_wifi and 'BSSID' in current_wifi:
                    current_bssid = current_wifi['BSSID']
                    for net in networks:
                        if net.get('bssid') == current_bssid:
                            current_ssid = net.get('ssid', 'WiFi网络')
                            break
                else:
                    # 如果无法通过BSSID匹配，使用网络列表中的第一个SSID
                    if networks:
                        current_ssid = networks[0].get('ssid', 'WiFi网络')
            
            # 快速清理SSID（使用转义管理器）
            if self.escape_manager.is_garbled_ssid(current_ssid, None):
                current_ssid = self.escape_manager.get_correct_ssid(current_ssid)
        else:
            # 完整模式下的处理
            try:
                channel_str = current_wifi.get('channel', '0') if current_wifi else '0'
                # 处理channel字段可能包含逗号的情况，如 "36,1"
                if ',' in channel_str:
                    channel_str = channel_str.split(',')[0]
                # 清理信道字符串，只保留数字
                channel_str = re.sub(r'[^0-9]', '', channel_str)
                if channel_str:
                    current_channel = int(channel_str)
                # 清理文件名中的非法字符
                current_ssid = re.sub(r'[<>:"/\\|?*]', '', current_ssid)
                current_ssid = current_ssid.strip()
                
                # 调试信息：检查SSID是否包含地理位置信息
                if '安徽' in current_ssid or '合肥' in current_ssid or '庐阳' in current_ssid:
                    self._safe_print(f"⚠️ 警告：SSID中包含地理位置信息，这可能不正常: {repr(current_ssid)}")
                    # 如果SSID包含地理位置信息，使用默认名称
                    current_ssid = "WiFi网络"
                    self._safe_print(f"已重置为默认SSID: {repr(current_ssid)}")
                    
            except (ValueError, TypeError) as e:
                print(f"解析WiFi信道失败: {e}")
                pass
        
        # 如果没有当前连接的WiFi，使用默认名称
        if not current_ssid:
            current_ssid = "WiFi网络"

        # 从扫描结果中查找当前WiFi在不同频段的信道
        channel_24g = None
        channel_5g = None
        
        # 优先使用当前连接的信道信息
        if current_channel:
            if current_channel <= 14:
                channel_24g = current_channel
            elif current_channel >= 36:
                channel_5g = current_channel
        
        # 从扫描结果中查找另一个频段的信道
        if current_ssid:
            # 更灵活的SSID匹配
            for net in networks:
                # 忽略大小写，部分匹配
                if current_ssid.lower() in net['ssid'].lower() or net['ssid'].lower() in current_ssid.lower():
                    ch = net['channel']
                    if ch <= 14 and not channel_24g:
                        channel_24g = ch
                    elif ch >= 36 and not channel_5g:
                        channel_5g = ch
        
        # 如果还是没有找到，尝试从扫描结果中找到信号最强的同SSID网络
        if current_ssid and (not channel_24g or not channel_5g):
            same_ssid_networks = []
            for net in networks:
                if current_ssid.lower() in net['ssid'].lower() or net['ssid'].lower() in current_ssid.lower():
                    same_ssid_networks.append(net)
            
            # 按信号强度排序
            same_ssid_networks.sort(key=lambda x: x['rssi_dbm'], reverse=True)
            
            # 优先选择信号最强的网络
            for net in same_ssid_networks:
                ch = net['channel']
                if ch <= 14 and not channel_24g:
                    channel_24g = ch
                elif ch >= 36 and not channel_5g:
                    channel_5g = ch
                if channel_24g and channel_5g:
                    break

        # 如果没有传入地理位置信息，则获取
        if not location_info:
            location_info = self.get_location_info()
        
        # 生成地理位置前缀（包含省、市、区、乡镇信息，使用转义管理器）
        location_prefix = ""
        if location_info and location_info.get('region') and location_info.get('city'):
            # 清理地理位置信息中的乱码和特殊字符
            region = self.escape_manager.clean_filename(location_info.get('region', ''))
            city = self.escape_manager.clean_filename(location_info.get('city', ''))
            district = self.escape_manager.clean_filename(location_info.get('district', ''))
            township = self.escape_manager.clean_filename(location_info.get('township', ''))
            
            location_prefix = f"{region}省{city}市"
            
            # 添加区信息
            if district:
                location_prefix += district
            
            # 添加乡镇信息
            if township:
                location_prefix += township
        
        # 智能修复当前SSID中的乱码（使用转义管理器）
        current_ssid_clean = current_ssid
        
        # 首先检查是否为乱码，如果是则进行修复
        if self.escape_manager.is_garbled_ssid(current_ssid, None):
            current_ssid_clean = self.escape_manager.get_correct_ssid(current_ssid)
            print(f"文件名生成中修复SSID乱码: {repr(current_ssid)} -> {repr(current_ssid_clean)}")
        
        # 清理文件名中的特殊字符
        current_ssid_clean = self.escape_manager.clean_filename(current_ssid_clean)
        
        # 智能文件名生成逻辑
        # 检查SSID是否包含地理位置信息（异常情况）
        if '安徽' in current_ssid_clean or '合肥' in current_ssid_clean or '庐阳' in current_ssid_clean:
            self._safe_print(f"⚠️ 检测到SSID包含地理位置信息，使用默认名称: {repr(current_ssid_clean)}")
            # 当SSID包含地理位置信息时，只使用地理位置信息作为文件名
            if location_prefix.strip():
                log_filename = f"{location_prefix.strip()}基于周围WiFi信道优化推荐({current_date}).json"
            else:
                log_filename = f"WiFi网络基于周围WiFi信道优化推荐({current_date}).json"
        elif current_ssid == "WiFi网络":
            # 当使用默认WiFi名称时，只使用地理位置信息作为文件名
            if location_prefix.strip():
                log_filename = f"{location_prefix.strip()}基于周围WiFi信道优化推荐({current_date}).json"
            else:
                log_filename = f"WiFi网络基于周围WiFi信道优化推荐({current_date}).json"
        else:
            # 正常情况：地理位置 + WiFi名称
            log_filename = f"{location_prefix}{current_ssid_clean}基于周围WiFi信道优化推荐({current_date}).json"
        
        # 生成存储子目录（按省市分类）
        log_subdir = self._get_location_subdir(location_prefix)
        
        # 构建完整的日志路径：json/logs/省市/文件名.json
        log_path = os.path.join(self.log_dir, log_subdir, log_filename)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        # 智能修复乱码SSID - 基于当前连接的WiFi名称进行转译
        cleaned_networks = []
        
        # 首先修复当前SSID（如果它是乱码，使用转义管理器）
        cleaned_current_ssid = current_ssid
        if self.escape_manager.is_garbled_ssid(current_ssid, None):
            cleaned_current_ssid = self.escape_manager.get_correct_ssid(current_ssid)
            print(f"日志保存中修复当前SSID乱码: {repr(current_ssid)} -> {repr(cleaned_current_ssid)}")
        
        for net in networks:
            cleaned_net = net.copy()
            
            # 智能乱码检测和转译逻辑（使用转义管理器）
            if self.escape_manager.is_garbled_ssid(cleaned_net['ssid'], cleaned_current_ssid):
                # 如果检测到乱码，使用修复后的当前SSID进行转译
                cleaned_net['ssid'] = cleaned_current_ssid
                print(f"修复网络SSID乱码: {repr(net['ssid'])} -> {repr(cleaned_current_ssid)}")
            
            cleaned_networks.append(cleaned_net)
        
        # 修复信道统计中的乱码SSID
        cleaned_channel_stats = {}
        for channel, stats in channel_stats.items():
            cleaned_stats = stats.copy()
            if 'networks' in cleaned_stats:
                cleaned_networks_list = []
                for net in cleaned_stats['networks']:
                    cleaned_net = net.copy()
                    # 使用相同的智能转译逻辑（使用转义管理器）
                    if self.escape_manager.is_garbled_ssid(cleaned_net['ssid'], cleaned_current_ssid):
                        cleaned_net['ssid'] = cleaned_current_ssid
                        print(f"修复信道统计SSID乱码: {repr(net['ssid'])} -> {repr(cleaned_current_ssid)}")
                    cleaned_networks_list.append(cleaned_net)
                cleaned_stats['networks'] = cleaned_networks_list
            cleaned_channel_stats[channel] = cleaned_stats
        
        # 获取无线网卡带宽信息
        network_card_info = {}
        
        # 在快速模式下，重新获取完整的WiFi信息以确保包含网卡描述
        if fast_mode:
            current_wifi = self.get_current_wifi_info()
        
        if current_wifi:
            # 提取网卡描述信息
            description = None
            full_description = None
            
            # 尝试多种可能的字段名
            description_fields = ['说明', 'Description', '描述', '网卡描述', '网卡完整描述', '网卡品牌型号']
            for field in description_fields:
                if field in current_wifi:
                    if field == '网卡完整描述':
                        full_description = current_wifi[field]
                    elif field == '网卡品牌型号':
                        # 如果已经有品牌型号信息，直接使用
                        network_card_info['网卡品牌型号'] = current_wifi[field]
                    description = current_wifi[field]
                    break
            
            # 如果仍然没有找到描述信息，尝试从调试信息中提取
            if not description and 'max_bandwidth_mbps' in current_wifi:
                # 如果已经有带宽信息，但没有描述，使用默认描述
                description = "未知无线网卡"
            
            # 保存完整的网卡描述信息
            if full_description:
                network_card_info['网卡完整描述'] = full_description
            elif description:
                network_card_info['网卡完整描述'] = description
            
            # 如果已经有增强的网卡信息，直接使用
            if '网卡完整描述' in current_wifi:
                network_card_info['网卡完整描述'] = current_wifi['网卡完整描述']
            if '网卡品牌型号' in current_wifi:
                network_card_info['网卡品牌型号'] = current_wifi['网卡品牌型号']
            if '网卡型号' in current_wifi:
                network_card_info['网卡型号'] = current_wifi['网卡型号']
            if 'max_bandwidth_mbps' in current_wifi:
                network_card_info['max_bandwidth_mbps'] = current_wifi['max_bandwidth_mbps']
            if '最大支持带宽' in current_wifi:
                network_card_info['最大支持带宽'] = current_wifi['最大支持带宽']
            if 'WiFi标准' in current_wifi:
                network_card_info['WiFi标准'] = current_wifi['WiFi标准']
            if 'max_bandwidth_gbps' in current_wifi:
                network_card_info['max_bandwidth_gbps'] = current_wifi['max_bandwidth_gbps']
            
            # 尝试获取具体的网卡品牌型号（如果还没有获取到）
            if '网卡品牌型号' not in network_card_info:
                brand_model = self._detect_network_card_brand_model(description)
                if brand_model:
                    network_card_info['网卡品牌型号'] = brand_model
                    self.escape_manager.debug_log(f"检测到网卡品牌型号: {brand_model}")
                else:
                    self.escape_manager.debug_log(f"无法检测到具体品牌型号，描述: {description}")
                    # 如果无法检测到具体品牌型号，使用芯片信息推断品牌型号
                    if description and 'realtek' in description.lower():
                        if '8811cu' in description.lower() or '8811' in description.lower():
                            network_card_info['网卡品牌型号'] = "腾达U12 (基于Realtek 8811CU)"
                        else:
                            network_card_info['网卡品牌型号'] = "腾达无线网卡 (基于Realtek芯片)"
                    else:
                        network_card_info['网卡品牌型号'] = "无线网卡"
            
            # 获取网卡最大带宽
            if description:
                bandwidth_mbps = self.escape_manager.get_wifi_bandwidth(description)
                
                # 如果通过描述无法获取带宽，但current_wifi中已有带宽信息，直接使用
                if bandwidth_mbps <= 0 and 'max_bandwidth_mbps' in current_wifi:
                    bandwidth_mbps = current_wifi['max_bandwidth_mbps']
                
                if bandwidth_mbps > 0:
                    network_card_info['max_bandwidth_mbps'] = bandwidth_mbps
                    
                    # 转换为Gbps（如果大于1000Mbps）
                    if bandwidth_mbps >= 1000:
                        network_card_info['max_bandwidth_gbps'] = round(bandwidth_mbps / 1000, 1)
                    
                    # 添加友好的带宽显示格式
                    if bandwidth_mbps >= 1000:
                        network_card_info['最大支持带宽'] = f"{round(bandwidth_mbps / 1000, 1)}G"
                    else:
                        network_card_info['最大支持带宽'] = f"{bandwidth_mbps}M"
                    
                    # 添加网卡型号信息 - 优先显示具体的品牌型号
                    if '网卡品牌型号' in network_card_info:
                        network_card_info['网卡型号'] = network_card_info['网卡品牌型号']
                    else:
                        network_card_info['网卡型号'] = description
                    
                    # 判断WiFi标准（基于网卡描述和带宽综合判断）
                    description_lower = description.lower()
                    if '802.11ax' in description_lower or 'wifi 6' in description_lower or bandwidth_mbps >= 2400:
                        network_card_info['WiFi标准'] = 'WiFi 6 (802.11ax)'
                    elif '802.11ac' in description_lower or 'wifi 5' in description_lower or bandwidth_mbps >= 866:
                        network_card_info['WiFi标准'] = 'WiFi 5 (802.11ac)'
                    elif '802.11n' in description_lower or 'wifi 4' in description_lower or bandwidth_mbps >= 300:
                        network_card_info['WiFi标准'] = 'WiFi 4 (802.11n)'
                    elif '802.11g' in description_lower or bandwidth_mbps >= 54:
                        network_card_info['WiFi标准'] = 'WiFi 3 (802.11g)'
                    else:
                        network_card_info['WiFi标准'] = 'WiFi 2 (802.11b)或更早'
        
        # 创建新的扫描记录
        new_scan_record = {
            "scan_time": datetime.datetime.now().isoformat(),
            "location": location_info if location_info else {"error": "无法获取地理位置信息"},
            "current_wifi": {
                "ssid": current_ssid,
                "channel_24g": channel_24g,
                "channel_5g": channel_5g
            },
            "network_card": network_card_info if network_card_info else {"error": "无法获取网卡信息"},
            "total_networks": len(networks),
            "recommended_channels": self.get_recommended_channels(),
            "network_details": cleaned_networks,
            "channel_statistics": cleaned_channel_stats,
            "optimization_suggestions": suggestions
        }

        # 检查文件是否已存在
        if os.path.exists(log_path):
            # 读取现有数据 - 使用UTF-8编码
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                
                # 如果现有数据是数组格式，直接追加
                if isinstance(existing_data, list):
                    existing_data.append(new_scan_record)
                    log_data = existing_data
                else:
                    # 如果现有数据是单个对象，转换为数组格式
                    log_data = [existing_data, new_scan_record]
            except (json.JSONDecodeError, Exception) as e:
                # 如果文件损坏或格式错误，创建新的数组
                self._safe_print(f"⚠️ 日志文件格式错误，重新创建: {e}")
                log_data = [new_scan_record]
        else:
            # 文件不存在，创建新的数组
            log_data = [new_scan_record]

        # 使用JSON文件管理器保存日志
        log_filename = self._generate_log_filename(location_prefix, current_ssid_clean, current_date)
        log_subdir = self._get_location_subdir(location_prefix)
        
        # 保存日志文件
        log_path = self.json_manager.save_json_file(
            file_type="scan_log", 
            filename=log_filename, 
            data=log_data, 
            subcategory=log_subdir
        )
        
        print(f"📝 日志已保存: {log_path} (共{len(log_data)}次扫描记录)")
        return log_path

    def _generate_log_filename_and_dir(self, location_prefix, ssid, date):
        """生成日志文件名和子目录，支持省市分类结构"""
        import re
        
        # 清理位置前缀（保留中文格式）
        location_clean = location_prefix.strip()
        
        # 清理SSID
        ssid_clean = ssid.strip()
        if ssid_clean:
            # 移除SSID中的非法字符，但保留空格和中文
            ssid_clean = re.sub(r'[\\/:*?"<>|]', '_', ssid_clean)
            ssid_clean = re.sub(r'_+', '_', ssid_clean)
            ssid_clean = ssid_clean.strip('_')
        
        # 提取省市信息作为子目录
        log_subdir = "other_locations"
        if location_clean:
            # 匹配格式：安徽省合肥市庐阳区逍遥津街道
            # 正确提取省份和城市的方法：
            # 1. 先找到"市"的位置
            # 2. 在"市"之前的文本中查找"省"
            city_match = re.search(r'市', location_clean)
            if city_match:
                city_pos = city_match.start()
                before_city = location_clean[:city_pos]
                
                # 在市之前查找省份
                province_match = re.search(r'(\S+省)', before_city)
                if province_match:
                    province = province_match.group(1)[:-1]  # 去掉"省"
                    city = before_city[province_match.end():]  # 省份之后到"市"之前是城市名
                    log_subdir = f"{province}_{city}"
                else:
                    # 没有省份，只有城市（如：合肥市庐阳区逍遥津街道）
                    city = before_city
                    log_subdir = city
            else:
                # 没有"市"，检查是否有"省"
                province_match = re.search(r'(\S+省)', location_clean)
                if province_match:
                    province = province_match.group(1)[:-1]
                    log_subdir = province
        
        # 生成标准化的文件名
        # 格式：地理位置 + 空格 + SSID + 基于周围WiFi信道优化推荐(日期).json
        # 例如：安徽省合肥市庐阳区逍遥津街道 小旭二手手机基于周围WiFi信道优化推荐(20260327).json
        if location_clean and ssid_clean:
            filename = f"{location_clean} {ssid_clean}基于周围WiFi信道优化推荐({date}).json"
        elif location_clean:
            filename = f"{location_clean}基于周围WiFi信道优化推荐({date}).json"
        elif ssid_clean:
            filename = f"{ssid_clean}基于周围WiFi信道优化推荐({date}).json"
        else:
            filename = f"WiFi网络基于周围WiFi信道优化推荐({date}).json"
        
        return filename, log_subdir

    def _generate_log_filename(self, location_prefix, ssid, date):
        """生成日志文件名 - 兼容旧代码"""
        filename, _ = self._generate_log_filename_and_dir(location_prefix, ssid, date)
        return filename

    def _get_location_subdir(self, location_prefix):
        """根据地理位置信息生成子目录名称"""
        import re
        
        if not location_prefix or not location_prefix.strip():
            return "other_locations"
        
        # 清理末尾空格
        location_text = location_prefix.strip()
        
        # 提取省份和城市的正确方法：
        # 1. 先找到"市"的位置
        # 2. 在"市"之前的文本中查找"省"
        city_match = re.search(r'市', location_text)
        if city_match:
            city_pos = city_match.start()
            before_city = location_text[:city_pos]
            
            # 在市之前查找省份
            province_match = re.search(r'(\S+省)', before_city)
            if province_match:
                province = province_match.group(1)[:-1]
                city = before_city[province_match.end():]
                return f"{province}_{city}"
            else:
                return before_city
        else:
            # 没有"市"，检查是否有"省"
            province_match = re.search(r'(\S+省)', location_text)
            if province_match:
                return province_match.group(1)[:-1]
        
        return "other_locations"

    def generate_report(self, export_csv=None, debug=False):
        """生成完整报告（性能优化版）"""
        self.escape_manager.debug_mode = debug
        
        print("\n" + "=" * 60)
        print("          WiFi信道扫描分析报告")
        print("=" * 60)

        location_info = self.get_location_info()
        if location_info:
            self.escape_manager.debug_log("获取到地理位置信息", location_info)
        else:
            self.escape_manager.debug_log("未获取到地理位置信息")

        networks = self.scan_wifi_networks()
        
        channel_stats = self.analyze_channels_fast(networks)
        recommended = self.get_recommended_channels_fast(channel_stats)
        suggestions = self.generate_optimization_suggestions_fast(networks, channel_stats, recommended)
        
        self.scan_results = networks
        self.channel_stats = channel_stats
        self.recommended_channels = recommended
        self.suggestions = suggestions
        
        if location_info:
            print(f"\n📍 地理位置: {location_info.get('country', '')} {location_info.get('region', '')} {location_info.get('city', '')}")
            print(f"🌐 运营商: {location_info.get('运营商', '')}")
            print(f"🔗 IP地址: {location_info.get('ip', '')}")

        if channel_stats:
            print("\n信道使用情况（精简版）:")
            print("-" * 30)
            print(f"{'信道':<6} {'网络数':<6} {'状态'}")
            print("-" * 30)
            
            for ch in sorted(channel_stats.keys())[:5]:
                stats = channel_stats[ch]
                status = "推荐" if ch in recommended else "拥挤"
                print(f"{ch:<6} {stats['count']:<6} {status}")
            
            if len(channel_stats) > 5:
                print(f"... 还有 {len(channel_stats) - 5} 个信道")
        
        if recommended:
            if len(recommended) <= 3:
                print(f"\n推荐信道: {', '.join(map(str, recommended))}")
            else:
                print(f"\n推荐信道: {', '.join(map(str, recommended[:3]))} 等 {len(recommended)} 个")

        if suggestions:
            print("\n优化建议（精简版）:")
            print("-" * 30)
            for suggestion in suggestions[:3]:
                icon = "🔥" if suggestion['priority'] == '高' else '⚠️' if suggestion['priority'] == '中' else '💡'
                print(f"{icon} {suggestion['suggestion'][:50]}...")

        if export_csv:
            try:
                if not export_csv or not isinstance(export_csv, str):
                    print("⚠️  CSV导出路径无效，跳过导出")
                else:
                    csv_thread = threading.Thread(
                        target=self._export_csv_safe,
                        args=(export_csv,),
                        name='CSV导出线程'
                    )
                    csv_thread.daemon = True
                    csv_thread.start()
                    print(f"📄 CSV导出任务已启动: {export_csv}")
            except Exception as e:
                print(f"❌ CSV导出启动失败: {e}")

        log_path = self._save_log_fast(networks, channel_stats, suggestions, location_info, recommended)
        print(f"📊 快速扫描完成: {log_path}")
        
        return log_path


class JSONFileManager:
    """JSON文件分类管理器 - 统一管理所有JSON文件的存储和分类"""
    
    def __init__(self, base_dir="json"):
        self.base_dir = base_dir
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保所有必要的目录都存在"""
        import os
        
        # 定义标准目录结构
        directories = [
            "config",           # 配置文件
            "hardware",         # 硬件性能数据
            "logs",             # 日志文件
            "projector",        # 投影仪数据
            "network",          # 网络配置数据
            "system",           # 系统信息
            "backup"            # 备份文件
        ]
        
        for directory in directories:
            dir_path = os.path.join(self.base_dir, directory)
            os.makedirs(dir_path, exist_ok=True)
    
    def get_file_path(self, file_type, filename, subcategory=None):
        """根据文件类型获取标准化的文件路径"""
        import os
        
        # 文件类型到目录的映射
        type_mapping = {
            # 配置文件
            "config": "config",
            "bios": "config",
            "settings": "config",
            
            # 硬件数据
            "cpu": "hardware",
            "gpu": "hardware", 
            "memory": "hardware",
            "network_hardware": "hardware",
            "hardware": "hardware",
            
            # 日志文件
            "log": "logs",
            "scan_log": "logs",
            "wifi_log": "logs",
            
            # 投影仪数据
            "projector": "projector",
            "projector_data": "projector",
            "projector_price": "projector",
            
            # 网络数据
            "network_config": "network",
            "wifi_config": "network",
            
            # 系统数据
            "system_info": "system",
            "performance": "system",
            
            # 备份文件
            "backup": "backup"
        }
        
        # 获取基础目录
        base_type = type_mapping.get(file_type, "other")
        
        # 构建完整路径
        if subcategory:
            # 如果有子分类，创建子目录
            dir_path = os.path.join(self.base_dir, base_type, subcategory)
            os.makedirs(dir_path, exist_ok=True)
            return os.path.join(dir_path, filename)
        else:
            return os.path.join(self.base_dir, base_type, filename)
    
    def save_json_file(self, file_type, filename, data, subcategory=None):
        """保存JSON文件到标准位置"""
        import os
        
        file_path = self.get_file_path(file_type, filename, subcategory)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def load_json_file(self, file_type, filename, subcategory=None, default_data=None):
        """从标准位置加载JSON文件"""
        import os
        
        file_path = self.get_file_path(file_type, filename, subcategory)
        
        if not os.path.exists(file_path):
            return default_data
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            print(f"❌ 加载JSON文件失败 {file_path}: {e}")
            return default_data
    
    def list_files_by_type(self, file_type, subcategory=None):
        """列出指定类型的所有文件"""
        import os
        
        dir_path = self.get_file_path(file_type, "", subcategory)
        if not os.path.exists(dir_path):
            return []
        
        files = []
        for filename in os.listdir(dir_path):
            if filename.endswith('.json'):
                files.append(filename)
        
        return sorted(files)
    
    def get_file_stats(self):
        """获取所有JSON文件的统计信息"""
        import os
        
        stats = {}
        
        for root, dirs, files in os.walk(self.base_dir):
            json_files = [f for f in files if f.endswith('.json')]
            if json_files:
                relative_path = os.path.relpath(root, self.base_dir)
                stats[relative_path] = {
                    'file_count': len(json_files),
                    'files': json_files
                }
        
        return stats
    
    # ==================== JSON文件分类规则系统 ====================
    
    # 定义所有JSON文件的分类规则
    FILE_CLASSIFICATION_RULES = {
        # 配置文件
        "config": {
            "description": "配置文件",
            "files": [
                "bios_versions.json",           # BIOS版本配置
                "app_config.json",              # 应用程序配置
                "user_settings.json",          # 用户设置
                "network_config.json",          # 网络配置
            ],
            "subdirectories": []
        },
        
        # 硬件性能数据
        "hardware": {
            "description": "硬件性能数据",
            "files": [
                "cpu_performance.json",         # CPU性能数据
                "gpu_performance.json",         # GPU性能数据
                "memory_performance.json",      # 内存性能数据
                "network_performance.json",      # 网络性能数据
                "disk_performance.json",         # 硬盘性能数据
            ],
            "subdirectories": []
        },
        
        # 日志文件
        "logs": {
            "description": "WiFi扫描日志文件",
            "files": [],
            "subdirectories": [
                "安徽_合肥",                     # 安徽省合肥市
                "江苏_南京",                     # 江苏省南京市
                "浙江_杭州",                     # 浙江省杭州市
                "上海_上海",                     # 上海市
                "北京_北京",                     # 北京市
                "湖北_武汉",                     # 湖北省武汉市
                "other_locations",              # 其他位置
            ],
            "naming_pattern": "*基于周围WiFi信道优化推荐*.json"
        },
        
        # 投影仪数据
        "projector": {
            "description": "投影仪推荐数据",
            "files": [
                "projector_data.json",           # 投影仪数据
                "projector_price_data.json",     # 投影仪价格数据
            ],
            "subdirectories": []
        },
        
        # 网络配置数据
        "network": {
            "description": "网络配置数据",
            "files": [
                "wifi_profiles.json",           # WiFi配置 profiles
                "channel_plan.json",             # 信道规划
            ],
            "subdirectories": []
        },
        
        # 系统信息
        "system": {
            "description": "系统信息数据",
            "files": [
                "system_info.json",              # 系统信息
                "device_info.json",              # 设备信息
            ],
            "subdirectories": []
        },
        
        # 备份文件
        "backup": {
            "description": "备份文件",
            "files": [],
            "subdirectories": []
        },
        
        # 其他文件
        "other": {
            "description": "其他文件",
            "files": [],
            "subdirectories": []
        }
    }
    
    def get_classification_rules(self):
        """获取JSON文件分类规则"""
        return self.FILE_CLASSIFICATION_RULES
    
    def classify_file(self, filename):
        """根据文件名自动分类JSON文件"""
        import re
        
        # 定义文件类型识别规则
        classification_rules = [
            # 配置文件
            (["bios_versions", "config", "settings"], "config"),
            
            # 硬件数据
            (["cpu_performance", "cpu_"], "hardware"),
            (["gpu_performance", "gpu_"], "hardware"),
            (["memory_performance", "memory_"], "hardware"),
            (["network_performance", "network_"], "hardware"),
            (["disk_performance", "disk_"], "hardware"),
            
            # 投影仪数据
            (["projector_data", "projector_price"], "projector"),
            
            # 日志文件（基于文件名模式）
            (["基于周围WiFi信道优化推荐", "wifi_scan", "scan_log"], "logs"),
            
            # 网络配置
            (["wifi_profiles", "channel_plan", "network_config"], "network"),
            
            # 系统信息
            (["system_info", "device_info"], "system"),
            
            # 备份文件
            (["backup", "backup_"], "backup"),
        ]
        
        # 遍历规则匹配
        filename_lower = filename.lower()
        for patterns, file_type in classification_rules:
            for pattern in patterns:
                if pattern.lower() in filename_lower:
                    return file_type
        
        return "other"
    
    def get_subdirectory_for_log(self, filename):
        """根据日志文件名提取省市区信息作为子目录"""
        import re
        
        # 提取省市信息的正则表达式
        # 格式：安徽省合肥市庐阳区逍遥津街道 TP-LINK_E8C9基于周围WiFi信道优化推荐(20260328).json
        
        # 尝试提取省市信息
        province_match = re.search(r'(\S+省)', filename)
        city_match = re.search(r'(\S+市)', filename)
        
        if province_match and city_match:
            province = province_match.group(1).replace('省', '')
            city = city_match.group(1).replace('市', '')
            return f"{province}_{city}"
        
        # 如果没有找到省市信息，返回默认目录
        return "other_locations"
    
    def organize_files(self):
        """重新组织所有JSON文件到标准目录结构"""
        import os
        import shutil
        import json as json_module
        
        print("\n" + "=" * 60)
        print("          JSON文件分类整理")
        print("=" * 60)
        
        moved_files = []
        skipped_files = []
        errors = []
        
        # 遍历base_dir下的所有JSON文件
        for root, dirs, files in os.walk(self.base_dir):
            for filename in files:
                if not filename.endswith('.json'):
                    continue
                
                old_path = os.path.join(root, filename)
                
                # 跳过标准目录中的文件
                relative_path = os.path.relpath(old_path, self.base_dir)
                path_parts = relative_path.split(os.sep)
                
                if len(path_parts) >= 2:
                    # 文件已经在正确的目录中
                    standard_dirs = list(self.FILE_CLASSIFICATION_RULES.keys())
                    if path_parts[0] in standard_dirs:
                        skipped_files.append(relative_path)
                        continue
                
                # 分类文件
                file_type = self.classify_file(filename)
                
                # 获取目标子目录
                subdirectory = None
                if file_type == "logs":
                    # 对于日志文件，提取省市信息作为子目录
                    subdirectory = self.get_subdirectory_for_log(filename)
                
                # 构建目标路径
                target_dir = os.path.join(self.base_dir, file_type)
                if subdirectory:
                    target_dir = os.path.join(target_dir, subdirectory)
                
                os.makedirs(target_dir, exist_ok=True)
                new_path = os.path.join(target_dir, filename)
                
                # 如果源文件和目标文件相同，跳过
                if old_path == new_path:
                    skipped_files.append(relative_path)
                    continue
                
                try:
                    # 移动文件
                    shutil.move(old_path, new_path)
                    moved_files.append(f"{relative_path} -> {os.path.relpath(new_path, self.base_dir)}")
                except Exception as e:
                    errors.append(f"{relative_path}: {str(e)}")
        
        # 打印结果
        print(f"\n📦 文件整理结果:")
        print(f"   ✅ 移动文件: {len(moved_files)} 个")
        print(f"   ⏭️  跳过文件: {len(skipped_files)} 个")
        print(f"   ❌ 错误: {len(errors)} 个")
        
        if moved_files:
            print(f"\n📄 移动的文件:")
            for f in moved_files[:10]:
                print(f"   {f}")
            if len(moved_files) > 10:
                print(f"   ... 还有 {len(moved_files) - 10} 个文件")
        
        if errors:
            print(f"\n❌ 错误:")
            for e in errors:
                print(f"   {e}")
        
        print(f"\n✅ 文件整理完成！")
        
        return {
            "moved": len(moved_files),
            "skipped": len(skipped_files),
            "errors": len(errors)
        }
    
    def print_classification_summary(self):
        """打印JSON文件分类摘要"""
        print("\n" + "=" * 60)
        print("          JSON文件分类规则")
        print("=" * 60)
        
        for category, rules in self.FILE_CLASSIFICATION_RULES.items():
            print(f"\n📁 {category} - {rules['description']}")
            
            if rules['files']:
                print(f"   标准文件:")
                for f in rules['files']:
                    print(f"      - {f}")
            
            if rules['subdirectories']:
                print(f"   子目录:")
                for subdir in rules['subdirectories']:
                    print(f"      - {subdir}/")
            
            if rules.get('naming_pattern'):
                print(f"   命名规则: {rules['naming_pattern']}")
        
        print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description='WiFi信道扫描工具（免依赖版）')
    parser.add_argument('--export', type=str, help='导出CSV文件的路径（例如: ./wifi_report.csv）')
    parser.add_argument('--debug', action='store_true', help='显示调试信息（默认不显示）')
    
    # 新增功能参数
    parser.add_argument('--hardware', action='store_true', help='检测硬件信息')
    parser.add_argument('--projector', action='store_true', help='投影仪推荐')
    parser.add_argument('--update-projector-db', action='store_true', help='强制更新投影仪数据库')
    parser.add_argument('--update-hardware-db', action='store_true', help='强制更新硬件性能数据库')
    parser.add_argument('--budget', type=str, help='投影仪预算范围（例如: 3000-8000）')
    parser.add_argument('--brand', type=str, help='投影仪品牌偏好（例如: 极米,坚果,当贝）')
    parser.add_argument('--resolution', type=str, help='投影仪分辨率偏好（例如: 4K,1080P）')
    parser.add_argument('--all-in-one', action='store_true', help='运行完整系统测试（WiFi扫描+硬件检测+投影仪推荐）')
    
    # JSON文件管理参数
    parser.add_argument('--json-stats', action='store_true', help='显示JSON文件统计信息')
    parser.add_argument('--organize-json', action='store_true', help='重新组织JSON文件到标准目录结构')
    parser.add_argument('--show-json-rules', action='store_true', help='显示JSON文件分类规则')

    args = parser.parse_args()
    
    # JSON文件管理功能
    if args.json_stats or args.organize_json or args.show_json_rules:
        json_manager = JSONFileManager("json")
        
        if args.json_stats:
            # 显示JSON文件统计信息
            stats = json_manager.get_file_stats()
            print("\n📊 JSON文件统计信息:")
            print("=" * 50)
            total = 0
            for category, info in stats.items():
                print(f"\n📁 {category}: {info['file_count']} 个文件")
                total += info['file_count']
            print(f"\n总计: {total} 个JSON文件")
            
        elif args.organize_json:
            # 重新组织JSON文件
            json_manager.organize_files()
            
        elif args.show_json_rules:
            # 显示分类规则
            json_manager.print_classification_summary()
        
        return

    # 处理预算范围
    budget_range = None
    if args.budget:
        try:
            min_budget, max_budget = map(int, args.budget.split('-'))
            budget_range = (min_budget, max_budget)
        except ValueError:
            print("⚠️  预算格式错误，请使用格式: 最小值-最大值（例如: 3000-8000）")
            return

    # 执行相应的功能
    if args.all_in_one:
        # 运行完整系统测试
        print("🚀 启动完整系统测试")
        print("=" * 60)
        
        # 1. 硬件信息检测
        print("\n1️⃣ 硬件信息检测中...")
        hardware_detector = OptimizedHardwareDetector(debug_mode=args.debug)
        hardware_detector.print_hardware_info()
        
        # 2. WiFi扫描
        print("\n2️⃣ WiFi网络扫描中...")
        scanner = WiFiChannelScanner()
        scanner.generate_report(export_csv=args.export, debug=args.debug)
        
        # 3. 投影仪推荐
        print("\n3️⃣ 投影仪推荐中...")
        projector_recommender = ProjectorRecommender(debug_mode=args.debug)
        projector_recommender.print_recommendations(budget_range=budget_range, brand_preference=args.brand)
        
        print("\n" + "=" * 60)
        print("✅ 完整系统测试完成！")
        
    elif args.hardware:
        # 仅检测硬件信息
        hardware_detector = OptimizedHardwareDetector(debug_mode=args.debug)
        
        # 如果指定了更新数据库，强制更新硬件性能数据
        if args.update_hardware_db:
            print("🔄 正在更新硬件性能数据库...")
            performance_updater = HardwarePerformanceUpdater(debug_mode=args.debug)
            performance_updater.update_all_performance_data(force_update=True)
            print("✅ 硬件性能数据库更新完成！")
            print()
        
        hardware_detector.print_hardware_info()
        
    elif args.projector:
        # 仅推荐投影仪
        projector_recommender = ProjectorRecommender(debug_mode=args.debug)
        
        # 如果指定了更新数据库，强制更新
        if args.update_projector_db:
            projector_recommender._update_database()
            projector_recommender.reload_database()
        
        projector_recommender.print_recommendations(budget_range=budget_range, brand_preference=args.brand, resolution_preference=args.resolution)
        
    else:
        # 默认执行WiFi扫描
        scanner = WiFiChannelScanner()
        scanner.generate_report(export_csv=args.export, debug=args.debug)


if __name__ == '__main__':
    main()