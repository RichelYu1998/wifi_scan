#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硬件信息检测器 - 检测CPU、显卡、内存等硬件信息
"""

import platform
import re

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil库未安装，硬件信息检测功能将受限")
    print("💡 安装命令: pip install psutil")

from common_imports import CrossPlatformUtils, get_cross_platform_utils, EscapeManager, get_escape_manager

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
            escape_manager = EscapeManager()  # 关闭调试模式
        if cross_platform_utils is None:
            cross_platform_utils = get_cross_platform_utils()  # 关闭调试模式
            
        self.escape_manager = escape_manager
        self.cross_platform_utils = cross_platform_utils
        
        # 使用硬件性能数据更新器获取最新数据
        self.performance_updater = HardwarePerformanceUpdater()
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
            'system': self._get_system_info(),
            'bios': self._get_bios_info(),
            'motherboard': self._get_motherboard_info(),
            'disk': self._get_disk_info()
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
                    # 过滤掉空行，选择第一个有效的CPU名称
                    valid_cpus = []
                    for line in lines:
                        cpu_name = line.strip()
                        if cpu_name and cpu_name != 'Name':
                            valid_cpus.append(cpu_name)
                    
                    if valid_cpus:
                        cpu_info['名称'] = valid_cpus[0]
                    else:
                        self.escape_manager.debug_log(f"WMIC CPU命令返回空结果: {result}")
                else:
                    self.escape_manager.debug_log("WMIC CPU命令执行失败")
                
                if PSUTIL_AVAILABLE:
                    cpu_info['核心数'] = psutil.cpu_count(logical=False)
                    try:
                        cpu_info['频率_MHz'] = int(psutil.cpu_freq().current) if psutil.cpu_freq() else 0
                    except Exception as e:
                        self.escape_manager.debug_log(f"获取CPU频率失败: {e}")
                
            else:  # Linux
                with open('/proc/cpuinfo', 'r') as f:
                    cpuinfo = f.read()
                    model_match = re.search(r'model name\s+:\s+(.+)', cpuinfo)
                    if model_match:
                        cpu_info['名称'] = model_match.group(1).strip()
                
                if PSUTIL_AVAILABLE:
                    cpu_info['核心数'] = psutil.cpu_count(logical=False)
                    cpu_info['频率_MHz'] = int(psutil.cpu_freq().current) if psutil.cpu_freq() else 0
                
        except Exception as e:
            self.escape_manager.debug_log(f"获取CPU信息失败: {e}")
            # 使用psutil作为备选方案
            if PSUTIL_AVAILABLE:
                cpu_info['核心数'] = psutil.cpu_count(logical=False) or 1
                cpu_info['频率_MHz'] = int(psutil.cpu_freq().current) if psutil.cpu_freq() else 0
        
        return cpu_info
    
    def _get_gpu_info(self):
        """获取显卡信息"""
        gpu_info = {'名称': '未知', '品牌': '未知', '型号': '未知', 'GPU芯片': '未知', '显存_MB': 0, '类型': '未知'}
        
        # 常见显卡制造商的子系统供应商ID
        subsystem_vendors = {
            '0000': 'Colorful (七彩虹)',
            '1043': 'ASUS (华硕)',
            '1462': 'MSI (微星)',
            '1458': 'Gigabyte (技嘉)',
            '19da': 'Zotac (索泰)',
            '1682': 'XFX (讯景)',
            '174b': 'Sapphire (蓝宝石)',
            '178b': 'EVGA',
            '3842': 'Palit (柏能)',
            '1b4b': 'Gainward (耕升)',
            '1d05': 'Leadtek (丽台)',
            '1d6f': 'Galax (影驰)',
            '1e0f': 'KFA2',
            '1f0f': 'Galax (影驰)',
            '26b2': 'Zotac (索泰)',
            '196e': 'PNY',
            '1acc': 'Club 3D',
            '1b1a': 'KFA2',
        }
        
        try:
            system = platform.system()
            if system == 'Darwin':
                # macOS使用system_profiler获取显卡信息
                result = self.cross_platform_utils.run_command(['system_profiler', 'SPDisplaysDataType'])
                if result:
                    # 解析显卡信息
                    chip_match = re.search(r'Chipset Model:\s+(.+)', result)
                    if chip_match:
                        gpu_name = chip_match.group(1).strip()
                        gpu_info['名称'] = gpu_name
                        gpu_info['GPU芯片'], gpu_info['型号'] = self._parse_gpu_name(gpu_name)
                        gpu_info['品牌'] = 'Apple'  # macOS默认为Apple
                        gpu_info['类型'] = '集成' if 'Intel' in gpu_name or 'Apple' in gpu_name else '独立'
                    
                    # 解析显存
                    vram_match = re.search(r'VRAM.*?(\d+)\s*MB', result)
                    if vram_match:
                        gpu_info['显存_MB'] = int(vram_match.group(1))
                    else:
                        # Apple Silicon使用统一内存，根据总内存估算
                        if PSUTIL_AVAILABLE:
                            mem_info = psutil.virtual_memory()
                            total_gb = mem_info.total // (1024**3)
                            gpu_info['显存_MB'] = min(total_gb * 512, 8192)  # 估算显存
                        
            elif system == 'Windows':
                # Windows使用WMIC获取显卡信息
                result = self.cross_platform_utils.run_command(['wmic', 'path', 'win32_VideoController', 'get', 'name'])
                if result:
                    lines = result.strip().split('\n')
                    valid_gpus = []
                    for i, line in enumerate(lines):
                        if i == 0:  # 跳过标题行
                            continue
                        gpu_name = line.strip()
                        # 跳过虚拟显卡
                        if gpu_name and not any(virtual in gpu_name.lower() for virtual in ['virtual', 'remote', 'rdp', 'mirror']):
                            valid_gpus.append(gpu_name)
                    
                    if valid_gpus:
                        gpu_name = valid_gpus[0]
                        gpu_info['名称'] = gpu_name
                        gpu_info['GPU芯片'], gpu_info['型号'] = self._parse_gpu_name(gpu_name)
                        gpu_info['类型'] = self._determine_gpu_type(gpu_name)
                        
                        # 获取显卡制造商（如七彩虹、华硕、微星等）通过子系统ID
                        pnp_result = self.cross_platform_utils.run_command(['wmic', 'path', 'win32_VideoController', 'get', 'PNPDeviceID'])
                        if pnp_result:
                            pnp_lines = pnp_result.strip().split('\n')
                            for i, line in enumerate(pnp_lines):
                                if i == 0:  # 跳过标题行
                                    continue
                                if 'PCI\\' in line and 'SUBSYS_' in line:
                                    # 提取子系统ID
                                    subsys_part = line.split('SUBSYS_')[1].split('&')[0]
                                    subsys_vendor_id = subsys_part[:4].lower()
                                    if subsys_vendor_id in subsystem_vendors:
                                        gpu_info['品牌'] = subsystem_vendors[subsys_vendor_id]
                                        break
                    else:
                        self.escape_manager.debug_log(f"未找到有效的物理显卡，所有结果: {lines}")
                else:
                    self.escape_manager.debug_log("WMIC GPU命令执行失败")
                
                # 尝试获取显存信息
                try:
                    vram_result = self.cross_platform_utils.run_command(['wmic', 'path', 'win32_VideoController', 'get', 'AdapterRAM'])
                    if vram_result:
                        vram_lines = vram_result.strip().split('\n')
                        # 选择第一个有效显卡的显存（与显卡名称对应）
                        valid_vrams = []
                        for i, line in enumerate(vram_lines):
                            if i == 0:  # 跳过标题行
                                continue
                            vram_value = line.strip()
                            if vram_value and vram_value.isdigit():
                                # 转换字节为MB
                                vram_mb = int(vram_value) // (1024 * 1024)
                                if vram_mb > 0:
                                    valid_vrams.append(vram_mb)
                        
                        # 选择最大的显存值（通常是独立显卡）
                        if valid_vrams:
                            gpu_info['显存_MB'] = max(valid_vrams)
                except Exception as e:
                    self.escape_manager.debug_log(f"获取GPU显存失败: {e}")
                
            else:  # Linux
                # Linux使用lspci获取显卡信息
                result = self.cross_platform_utils.run_command(['lspci'])
                if result:
                    gpu_lines = [line for line in result.split('\n') if 'VGA' in line or '3D' in line]
                    if gpu_lines:
                        gpu_name = gpu_lines[0].split(':')[2].strip()
                        gpu_info['名称'] = gpu_name
                        gpu_info['GPU芯片'], gpu_info['型号'] = self._parse_gpu_name(gpu_name)
                        gpu_info['类型'] = self._determine_gpu_type(gpu_name)
                        gpu_info['品牌'] = '未知'  # Linux默认为未知，需要额外命令获取
                        
        except Exception as e:
            self.escape_manager.debug_log(f"获取显卡信息失败: {e}")
        
        return gpu_info
    
    def _parse_gpu_name(self, gpu_name):
        """解析显卡名称，提取品牌和型号"""
        gpu_name_lower = gpu_name.lower()
        
        # 识别显卡品牌
        brand = '未知'
        if 'nvidia' in gpu_name_lower or 'geforce' in gpu_name_lower or 'gtx' in gpu_name_lower or 'rtx' in gpu_name_lower or 'quadro' in gpu_name_lower:
            brand = 'NVIDIA'
        elif 'amd' in gpu_name_lower or 'radeon' in gpu_name_lower or 'rx' in gpu_name_lower:
            brand = 'AMD'
        elif 'intel' in gpu_name_lower:
            brand = 'Intel'
        elif 'apple' in gpu_name_lower:
            brand = 'Apple'
        elif 'arc' in gpu_name_lower:
            brand = 'Intel'
        
        # 识别显卡型号
        model = '未知'
        if 'rtx' in gpu_name_lower:
            rtx_match = re.search(r'RTX\s*(\d+\s*[A-Za-z]*)', gpu_name, re.IGNORECASE)
            if rtx_match:
                model = f"RTX {rtx_match.group(1).strip()}"
        elif 'gtx' in gpu_name_lower:
            gtx_match = re.search(r'GTX\s*(\d+\s*[A-Za-z]*)', gpu_name, re.IGNORECASE)
            if gtx_match:
                model = f"GTX {gtx_match.group(1).strip()}"
        elif 'rx' in gpu_name_lower:
            rx_match = re.search(r'RX\s*(\d+\s*[A-Za-z]*)', gpu_name, re.IGNORECASE)
            if rx_match:
                model = f"RX {rx_match.group(1).strip()}"
        elif 'geforce' in gpu_name_lower:
            geforce_match = re.search(r'GeForce\s+(.+)', gpu_name, re.IGNORECASE)
            if geforce_match:
                model = geforce_match.group(1).strip()
        elif 'radeon' in gpu_name_lower:
            radeon_match = re.search(r'Radeon\s+(.+)', gpu_name, re.IGNORECASE)
            if radeon_match:
                model = radeon_match.group(1).strip()
        elif 'm1' in gpu_name_lower or 'm2' in gpu_name_lower or 'm3' in gpu_name_lower:
            apple_match = re.search(r'(M[1-3](?:\s+(?:Pro|Max|Ultra))?)', gpu_name, re.IGNORECASE)
            if apple_match:
                model = apple_match.group(1).strip()
        elif 'iris' in gpu_name_lower:
            iris_match = re.search(r'Iris\s+(.+)', gpu_name, re.IGNORECASE)
            if iris_match:
                model = iris_match.group(1).strip()
        elif 'uhd' in gpu_name_lower:
            uhd_match = re.search(r'UHD\s+(\d+)', gpu_name, re.IGNORECASE)
            if uhd_match:
                model = f"UHD {uhd_match.group(1)}"
        
        return brand, model
    
    def _determine_gpu_type(self, gpu_name):
        """判断显卡类型（独立/集成）"""
        gpu_name_lower = gpu_name.lower()
        
        # 集成显卡特征
        integrated_keywords = ['intel', 'iris', 'uhd', 'hd graphics', 'arc', 'apple', 'm1', 'm2', 'm3']
        
        for keyword in integrated_keywords:
            if keyword in gpu_name_lower:
                return '集成'
        
        # 独立显卡特征
        dedicated_keywords = ['nvidia', 'geforce', 'gtx', 'rtx', 'quadro', 'amd', 'radeon', 'rx']
        
        for keyword in dedicated_keywords:
            if keyword in gpu_name_lower:
                return '独立'
        
        return '未知'
    
    def _get_memory_info(self):
        """获取内存信息"""
        memory_info = {'总容量_GB': 0, '可用_GB': 0, '使用率_%': 0, '频率_MHz': 0, 'DDR类型': '未知'}
        try:
            if PSUTIL_AVAILABLE:
                mem = psutil.virtual_memory()
                memory_info['总容量_GB'] = round(mem.total / (1024**3), 1)
                memory_info['可用_GB'] = round(mem.available / (1024**3), 1)
                memory_info['使用率_%'] = round(mem.percent, 1)
            else:
                # 使用系统命令获取内存信息
                if self.cross_platform_utils.is_windows():
                    result = self.cross_platform_utils.run_command(['wmic', 'OS', 'get', 'TotalVisibleMemorySize,FreePhysicalMemory'])
                    if result:
                        lines = result.strip().split('\n')
                        # WMIC返回的数据可能在第2行或第3行
                        for line in lines:
                            line = line.strip()
                            if line and 'TotalVisibleMemorySize' not in line:
                                # 尝试从空格分隔的数据中提取数值
                                parts = line.split()
                                # 查找两个有效的数值
                                values = []
                                for part in parts:
                                    try:
                                        value = int(part)
                                        if value > 1000:  # 内存值应该大于1000KB
                                            values.append(value)
                                    except ValueError:
                                        pass
                                
                                if len(values) >= 2:
                                    total_kb = values[0]
                                    free_kb = values[1]
                                    memory_info['总容量_GB'] = round(total_kb / (1024**2), 1)
                                    memory_info['可用_GB'] = round(free_kb / (1024**2), 1)
                                    memory_info['使用率_%'] = round((total_kb - free_kb) / total_kb * 100, 1)
                                    break
            
            # 获取内存详细信息（频率和DDR类型）- 独立于psutil
            if self.cross_platform_utils.is_windows():
                memory_detail_result = self.cross_platform_utils.run_command(['wmic', 'memorychip', 'get', 'Speed'])
                self.escape_manager.debug_log(f"WMIC内存频率原始输出: {repr(memory_detail_result)}")
                if memory_detail_result:
                    self.escape_manager.debug_log(f"WMIC内存频率输出长度: {len(memory_detail_result)}")
                    memory_lines = memory_detail_result.strip().split('\n')
                    self.escape_manager.debug_log(f"分割后的行数: {len(memory_lines)}")
                    speeds = []
                    for line in memory_lines:
                        line = line.strip()
                        self.escape_manager.debug_log(f"处理内存频率行: '{line}'")
                        if line and 'Speed' not in line:
                            # WMIC返回的数据格式：每行一个数值，如 2400
                            try:
                                speed = int(line)
                                if speed > 0:
                                    speeds.append(speed)
                                    self.escape_manager.debug_log(f"成功解析内存频率: {speed}MHz")
                            except ValueError as e:
                                self.escape_manager.debug_log(f"解析内存频率失败: {e}")
                                pass
                    
                    self.escape_manager.debug_log(f"解析到的内存频率列表: {speeds}")
                    
                    if speeds:
                        # 取平均频率
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
                
                elif self.cross_platform_utils.is_linux():
                    result = self.cross_platform_utils.run_command(['cat', '/proc/meminfo'])
                    if result:
                        meminfo = {}
                        for line in result.split('\n'):
                            if ':' in line:
                                key, value = line.split(':', 1)
                                meminfo[key.strip()] = value.strip()
                        
                        total_kb = int(meminfo.get('MemTotal', '0 kB').split()[0])
                        free_kb = int(meminfo.get('MemFree', '0 kB').split()[0])
                        memory_info['总容量_GB'] = round(total_kb / (1024**2), 1)
                        memory_info['可用_GB'] = round(free_kb / (1024**2), 1)
                        memory_info['使用率_%'] = round((total_kb - free_kb) / total_kb * 100, 1)
                    
                    # 尝试获取内存详细信息
                    try:
                        dmidecode_result = self.cross_platform_utils.run_command(['dmidecode', '-t', 'memory'])
                        if dmidecode_result:
                            speeds = []
                            for line in dmidecode_result.split('\n'):
                                if 'Speed:' in line:
                                    speed_match = re.search(r'Speed:\s*(\d+)\s*MHz', line)
                                    if speed_match:
                                        speeds.append(int(speed_match.group(1)))
                            
                            if speeds:
                                memory_info['频率_MHz'] = round(sum(speeds) / len(speeds))
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
                    except Exception as e:
                        self.escape_manager.debug_log(f"获取Linux内存详细信息失败: {e}")
                        
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
    
    def _get_bios_info(self):
        """获取BIOS信息"""
        bios_info = {'版本': '未知', '制造商': '未知', '发布日期': '未知', '是否最新': '未知'}
        try:
            system = platform.system()
            if system == 'Windows':
                # Windows使用WMIC获取BIOS信息
                result = self.cross_platform_utils.run_command(['wmic', 'bios', 'get', 'SMBIOSBIOSVersion,Manufacturer,ReleaseDate'])
                if result:
                    lines = result.strip().split('\n')
                    # 查找包含数据的行（跳过标题行和空行）
                    for line in lines:
                        line = line.strip()
                        if line and 'SMBIOSBIOSVersion' not in line:
                            # 使用更智能的解析方法
                            # 从右向左解析，因为版本号在最右边
                            parts = line.split()
                            if len(parts) >= 3:
                                # 版本号是最后一个字段
                                bios_info['版本'] = parts[-1]
                                # 发布日期是倒数第二个字段
                                raw_date = parts[-2]
                                # 解析并格式化日期
                                bios_info['发布日期'] = self._parse_bios_date(raw_date)
                                # 制造商是前面的所有部分
                                bios_info['制造商'] = ' '.join(parts[:-2])
                                break
                
            elif system == 'Darwin':
                # macOS使用system_profiler获取BIOS信息
                result = self.cross_platform_utils.run_command(['system_profiler', 'SPHardwareDataType'])
                if result:
                    boot_version = re.search(r'Boot ROM Version:\s+(.+)', result)
                    if boot_version:
                        bios_info['版本'] = boot_version.group(1).strip()
                    
                    manufacturer = re.search(r'Manufacturer:\s+(.+)', result)
                    if manufacturer:
                        bios_info['制造商'] = manufacturer.group(1).strip()
            
            else:  # Linux
                # Linux使用dmidecode获取BIOS信息
                result = self.cross_platform_utils.run_command(['dmidecode', '-t', 'bios'])
                if result:
                    version = re.search(r'Version:\s+(.+)', result)
                    if version:
                        bios_info['版本'] = version.group(1).strip()
                    
                    vendor = re.search(r'Vendor:\s+(.+)', result)
                    if vendor:
                        bios_info['制造商'] = vendor.group(1).strip()
                    
                    date = re.search(r'Release Date:\s+(.+)', result)
                    if date:
                        bios_info['发布日期'] = date.group(1).strip()
                
                # 检查BIOS是否为最新版本（使用主板制造商而不是BIOS制造商）
                try:
                    self.escape_manager.debug_log(f"开始检查BIOS最新版本，当前BIOS版本: {bios_info['版本']}")
                    motherboard_info = self._get_motherboard_info()
                    self.escape_manager.debug_log(f"主板信息: {motherboard_info}")
                    latest_version = self._get_latest_bios_version(motherboard_info['制造商'], motherboard_info['型号'])
                    self.escape_manager.debug_log(f"最新BIOS版本: {latest_version}")
                    bios_info['是否最新'] = self._check_bios_latest_version(motherboard_info['制造商'], bios_info['版本'], motherboard_info['型号'])
                    self.escape_manager.debug_log(f"BIOS是否最新: {bios_info['是否最新']}")
                except Exception as e:
                    self.escape_manager.debug_log(f"检查BIOS最新版本失败: {e}")
                    bios_info['是否最新'] = '无法检测'
                        
        except Exception as e:
            self.escape_manager.debug_log(f"获取BIOS信息失败: {e}")
        
        return bios_info
    
    def _get_motherboard_info(self):
        """获取主板信息"""
        motherboard_info = {'型号': '未知', '制造商': '未知', '芯片组': '未知'}
        try:
            system = platform.system()
            if system == 'Windows':
                # Windows使用WMIC获取主板信息
                result = self.cross_platform_utils.run_command(['wmic', 'baseboard', 'get', 'Product,Manufacturer'])
                if result:
                    lines = result.strip().split('\n')
                    # 查找包含数据的行（跳过标题行和空行）
                    for line in lines:
                        line = line.strip()
                        if line and 'Product' not in line:
                            # 使用更智能的解析方法
                            # 从右向左解析，因为型号在最右边
                            parts = line.split()
                            if len(parts) >= 3:
                                # 型号是最后一个字段
                                motherboard_info['型号'] = ' '.join(parts[3:])
                                # 制造商是前面的部分
                                motherboard_info['制造商'] = ' '.join(parts[:3])
                            elif len(parts) >= 2:
                                # 如果只有2个部分，使用前1个作为制造商
                                motherboard_info['型号'] = ' '.join(parts[1:])
                                motherboard_info['制造商'] = parts[0]
                            break
                
            elif system == 'Darwin':
                # macOS使用system_profiler获取主板信息
                result = self.cross_platform_utils.run_command(['system_profiler', 'SPHardwareDataType'])
                if result:
                    model = re.search(r'Model Identifier:\s+(.+)', result)
                    if model:
                        motherboard_info['型号'] = model.group(1).strip()
                    
                    manufacturer = re.search(r'Manufacturer:\s+(.+)', result)
                    if manufacturer:
                        motherboard_info['制造商'] = manufacturer.group(1).strip()
            
            else:  # Linux
                # Linux使用dmidecode获取主板信息
                result = self.cross_platform_utils.run_command(['dmidecode', '-t', 'baseboard'])
                if result:
                    product = re.search(r'Product Name:\s+(.+)', result)
                    if product:
                        motherboard_info['型号'] = product.group(1).strip()
                    
                    manufacturer = re.search(r'Manufacturer:\s+(.+)', result)
                    if manufacturer:
                        motherboard_info['制造商'] = manufacturer.group(1).strip()
                        
        except Exception as e:
            self.escape_manager.debug_log(f"获取主板信息失败: {e}")
        
        return motherboard_info
    
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
    
    def _check_bios_latest_version(self, motherboard_manufacturer, current_version, motherboard_model):
        """检查BIOS是否为最新版本"""
        try:
            # 根据制造商和主板型号查询最新BIOS版本
            latest_version = self._get_latest_bios_version(motherboard_manufacturer, motherboard_model)
            
            if latest_version and latest_version != '未知':
                # 比较版本号
                if self._compare_bios_versions(current_version, latest_version):
                    return '是'
                else:
                    return f'否 (最新: {latest_version})'
            else:
                return '无法检测'
                
        except Exception as e:
            self.escape_manager.debug_log(f"检查BIOS最新版本失败: {e}")
            return '无法检测'
    
    def _get_latest_bios_version(self, manufacturer, motherboard_model):
        """获取最新BIOS版本"""
        try:
            # 首先尝试从本地JSON文件中获取已知版本
            try:
                import json
                import os
                
                bios_versions_file = os.path.join(os.path.dirname(__file__), 'bios_versions.json')
                if os.path.exists(bios_versions_file):
                    with open(bios_versions_file, 'r', encoding='utf-8') as f:
                        bios_data = json.load(f)
                    
                    # 查找匹配的主板型号
                    for model, version in bios_data.get('bios_versions', {}).items():
                        if model.lower() in motherboard_model.lower() or motherboard_model.lower() in model.lower():
                            return version
            except Exception as e:
                self.escape_manager.debug_log(f"从本地文件读取BIOS版本失败: {e}")
            
            # 这里可以添加网络查询逻辑，查询各厂商官网的BIOS更新
            # 由于网络查询比较复杂，这里提供一个基础框架
            
            # 常见主板制造商的BIOS下载页面URL模式
            bios_urls = {
                'ASUS': f"https://www.asus.com.cn/motherboards-components/motherboards/all-series/products/?search={motherboard_model}",
                'MSI': f"https://www.msi.com/Motherboard/Support/{motherboard_model}",
                'GIGABYTE': f"https://www.gigabyte.com/Motherboard/{motherboard_model}/support#support-dl-bios",
                'ASRock': f"https://www.asrock.com/MB/index.asp?Search={motherboard_model}",
            }
            
            # 尝试网络查询
            try:
                import urllib.request
                import urllib.parse
                
                # 根据制造商选择对应的URL
                manufacturer_upper = manufacturer.upper()
                for key, url_template in bios_urls.items():
                    if key in manufacturer_upper:
                        # 对主板型号进行URL编码
                        encoded_model = urllib.parse.quote(motherboard_model)
                        url = url_template.replace(motherboard_model, encoded_model)
                        break
                else:
                    # 如果没有匹配的制造商，返回未知
                    return "未知"
                
                # 构造请求头，模拟浏览器访问
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                # 发送HTTP请求
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as response:
                    # 使用utf-8编码读取内容
                    html_content = response.read().decode('utf-8', errors='ignore')
                
                # 解析HTML内容，提取BIOS版本号
                # 这里需要根据不同厂商的HTML结构进行解析
                # 由于HTML解析比较复杂，这里提供基础框架
                
                # 尝试从HTML中提取版本号
                # 针对不同厂商使用不同的解析策略
                version_patterns = []
                
                if 'ASUS' in manufacturer_upper:
                    # ASUS特定的版本号模式
                    version_patterns = [
                        r'BIOS\s*[:\s]*([0-9]{4})',
                        r'Version\s*[:\s]*([0-9]{4})',
                        r'BIOS\s*Version\s*[:\s]*([0-9]{4})',
                        r'([0-9]{4})\s*BIOS',
                    ]
                elif 'MSI' in manufacturer_upper:
                    # MSI特定的版本号模式
                    version_patterns = [
                        r'BIOS\s*[:\s]*([0-9A-Z.]+)',
                        r'Version\s*[:\s]*([0-9A-Z.]+)',
                        r'v([0-9A-Z.]+)',
                    ]
                elif 'GIGABYTE' in manufacturer_upper:
                    # 技嘉特定的版本号模式
                    version_patterns = [
                        r'BIOS\s*[:\s]*([0-9A-Z.]+)',
                        r'Version\s*[:\s]*([0-9A-Z.]+)',
                        r'v([0-9A-Z.]+)',
                    ]
                else:
                    # 通用版本号模式
                    version_patterns = [
                        r'BIOS\s*Version\s*[:\s]*([0-9.]+)',
                        r'Version\s*[:\s]*([0-9.]+)',
                        r'v([0-9.]+)',
                    ]
                
                for pattern in version_patterns:
                    matches = re.findall(pattern, html_content)
                    if matches:
                        # 返回找到的第一个版本号
                        return matches[0]
                
                # 如果没有找到版本号，返回未知
                return "未知"
                
            except Exception as e:
                self.escape_manager.debug_log(f"网络查询BIOS版本失败: {e}")
                return "未知"
            
        except Exception as e:
            self.escape_manager.debug_log(f"获取最新BIOS版本失败: {e}")
            return "未知"
    
    def _compare_bios_versions(self, current_version, latest_version):
        """比较BIOS版本号"""
        try:
            # 移除版本号中的非数字字符
            current_clean = re.sub(r'[^\d.]', '', current_version)
            latest_clean = re.sub(r'[^\d.]', '', latest_version)
            
            # 分割版本号
            current_parts = [int(x) for x in current_clean.split('.') if x]
            latest_parts = [int(x) for x in latest_clean.split('.') if x]
            
            # 比较版本号
            for i in range(max(len(current_parts), len(latest_parts))):
                current_val = current_parts[i] if i < len(current_parts) else 0
                latest_val = latest_parts[i] if i < len(latest_parts) else 0
                
                if current_val < latest_val:
                    return False
                elif current_val > latest_val:
                    return True
            
            return True  # 版本号相同
            
        except Exception as e:
            self.escape_manager.debug_log(f"比较BIOS版本号失败: {e}")
            return False
    
    def _parse_bios_date(self, raw_date):
        """解析并格式化BIOS日期"""
        try:
            # WMIC返回的日期格式：20210710000000.000000+000
            # 需要解析为可读格式
            if '.' in raw_date:
                # 分离日期和时间部分
                date_part = raw_date.split('.')[0]
                
                # 解析日期部分：YYYYMMDDHHMMSS
                if len(date_part) >= 8:
                    year = date_part[0:4]
                    month = date_part[4:6]
                    day = date_part[6:8]
                    
                    # 格式化为YYYY-MM-DD
                    formatted_date = f"{year}-{month}-{day}"
                    return formatted_date
            
            # 如果解析失败，返回原始值
            return raw_date
            
        except Exception as e:
            self.escape_manager.debug_log(f"解析BIOS日期失败: {e}")
            return raw_date
    
    def _get_disk_info(self):
        """获取硬盘信息"""
        disk_info = {
            '总数': 0,
            '总容量_TB': 0,
            '硬盘列表': []
        }
        
        try:
            system = platform.system()
            
            if system == 'Windows':
                # Windows使用WMIC获取硬盘信息
                result = self.cross_platform_utils.run_command(['wmic', 'diskdrive', 'get', 'Model,Size,InterfaceType'])
                if result:
                    lines = result.strip().split('\n')
                    disk_count = 0
                    total_size = 0
                    
                    for i, line in enumerate(lines):
                        if i == 0:  # 跳过标题行
                            continue
                        
                        line = line.strip()
                        if not line:
                            continue
                        
                        # 解析硬盘信息
                        parts = line.split()
                        if len(parts) >= 2:
                            disk_count += 1
                            
                            # 提取型号和大小
                            model = ' '.join(parts[:-1])
                            size_bytes = int(parts[-1]) if parts[-1].isdigit() else 0
                            size_gb = round(size_bytes / (1024**3), 2)
                            size_tb = round(size_gb / 1024, 2)
                            total_size += size_gb
                            
                            disk_info['硬盘列表'].append({
                                '型号': model,
                                '容量_GB': size_gb,
                                '容量_TB': size_tb,
                                '接口类型': '未知'
                            })
                    
                    disk_info['总数'] = disk_count
                    disk_info['总容量_TB'] = round(total_size / 1024, 2)
                
                # 获取硬盘读写速率
                disk_info['读写速率'] = self._get_disk_performance()
                
            elif system == 'Darwin':
                # macOS使用diskutil获取硬盘信息
                result = self.cross_platform_utils.run_command(['diskutil', 'list'])
                if result:
                    # 解析硬盘信息
                    disk_matches = re.findall(r'/dev/\w+.*?Type:\s+(\w+).*?Total Size:\s+([0-9.]+\s+\w+)', result, re.DOTALL)
                    disk_count = 0
                    total_size = 0
                    
                    for match in disk_matches:
                        disk_count += 1
                        disk_type = match.group(1)
                        size_str = match.group(2)
                        
                        # 解析大小
                        size_gb = 0
                        if 'GB' in size_str:
                            size_gb = float(size_str.split()[0])
                        elif 'TB' in size_str:
                            size_gb = float(size_str.split()[0]) * 1024
                        
                        size_tb = round(size_gb / 1024, 2)
                        total_size += size_gb
                        
                        disk_info['硬盘列表'].append({
                            '型号': f'硬盘{disk_count}',
                            '容量_GB': round(size_gb, 2),
                            '容量_TB': size_tb,
                            '接口类型': disk_type
                        })
                    
                    disk_info['总数'] = disk_count
                    disk_info['总容量_TB'] = round(total_size / 1024, 2)
                
                # 获取硬盘读写速率
                disk_info['读写速率'] = self._get_disk_performance()
                
            elif system == 'Linux':
                # Linux使用lsblk获取硬盘信息
                result = self.cross_platform_utils.run_command(['lsblk', '-d', '-o', 'NAME,SIZE,ROTA'])
                if result:
                    lines = result.strip().split('\n')
                    disk_count = 0
                    total_size = 0
                    
                    for i, line in enumerate(lines):
                        if i == 0:  # 跳过标题行
                            continue
                        
                        parts = line.split()
                        if len(parts) >= 3:
                            disk_count += 1
                            name = parts[0]
                            size_str = parts[1]
                            
                            # 解析大小
                            size_gb = 0
                            if 'G' in size_str:
                                size_gb = float(size_str.replace('G', ''))
                            elif 'T' in size_str:
                                size_gb = float(size_str.replace('T', '')) * 1024
                            
                            size_tb = round(size_gb / 1024, 2)
                            total_size += size_gb
                            
                            disk_info['硬盘列表'].append({
                                '型号': name,
                                '容量_GB': round(size_gb, 2),
                                '容量_TB': size_tb,
                                '接口类型': '未知'
                            })
                    
                    disk_info['总数'] = disk_count
                    disk_info['总容量_TB'] = round(total_size / 1024, 2)
                
                # 获取硬盘读写速率
                disk_info['读写速率'] = self._get_disk_performance()
        
        except Exception as e:
            self.escape_manager.debug_log(f"获取硬盘信息失败: {e}")
        
        return disk_info
    
    def _get_disk_performance(self):
        """获取硬盘读写速率"""
        disk_performance = {
            '读取速率_MB/s': 0,
            '写入速率_MB/s': 0,
            '理论读取速率_MB/s': 0,
            '理论写入速率_MB/s': 0
        }
        
        try:
            system = platform.system()
            
            if system == 'Windows':
                # Windows使用wmic获取硬盘性能信息
                result = self.cross_platform_utils.run_command(['wmic', 'diskdrive', 'get', 'Model'])
                if result:
                    # 获取硬盘型号
                    disk_models = []
                    lines = result.strip().split('\n')
                    for i, line in enumerate(lines):
                        if i == 0:  # 跳过标题行
                            continue
                        model = line.strip()
                        if model:
                            disk_models.append(model)
                    
                    # 根据硬盘型号估算理论速率
                    for model in disk_models:
                        theoretical_rate = self._estimate_disk_speed(model)
                        if theoretical_rate > 0:
                            disk_performance['理论读取速率_MB/s'] = max(disk_performance['理论读取速率_MB/s'], theoretical_rate)
                            disk_performance['理论写入速率_MB/s'] = max(disk_performance['理论写入速率_MB/s'], theoretical_rate * 0.8)  # 写入通常比读取慢20%
                
                # 获取实际读写速率（需要psutil）
                if PSUTIL_AVAILABLE:
                    import psutil
                    import time
                    
                    # 获取两次IO统计信息，计算速率
                    io1 = psutil.disk_io_counters(perdisk=False)
                    time.sleep(1)  # 等待1秒
                    io2 = psutil.disk_io_counters(perdisk=False)
                    
                    if io1 and io2:
                        # 计算每秒的读写速率（字节/秒 -> MB/s）
                        read_bytes_diff = io2.read_bytes - io1.read_bytes
                        write_bytes_diff = io2.write_bytes - io1.write_bytes
                        
                        read_rate = read_bytes_diff / (1024 * 1024)  # MB/s
                        write_rate = write_bytes_diff / (1024 * 1024)  # MB/s
                        
                        disk_performance['读取速率_MB/s'] = round(read_rate, 2)
                        disk_performance['写入速率_MB/s'] = round(write_rate, 2)
            
            elif system == 'Darwin':
                # macOS使用iostat获取硬盘性能
                result = self.cross_platform_utils.run_command(['iostat', '-d', '1', '1'])
                if result:
                    # 解析IO统计信息
                    io_match = re.search(r'([0-9.]+)\s+([0-9.]+)', result)
                    if io_match:
                        disk_performance['读取速率_MB/s'] = round(float(io_match.group(1)), 2)
                        disk_performance['写入速率_MB/s'] = round(float(io_match.group(2)), 2)
            
            elif system == 'Linux':
                # Linux使用iostat获取硬盘性能
                result = self.cross_platform_utils.run_command(['iostat', '-d', '-k', '1', '1'])
                if result:
                    # 解析IO统计信息
                    io_match = re.search(r'([0-9.]+)\s+([0-9.]+)', result)
                    if io_match:
                        disk_performance['读取速率_MB/s'] = round(float(io_match.group(1)), 2)
                        disk_performance['写入速率_MB/s'] = round(float(io_match.group(2)), 2)
        
        except Exception as e:
            self.escape_manager.debug_log(f"获取硬盘性能失败: {e}")
        
        return disk_performance
    
    def _estimate_disk_speed(self, disk_model):
        """根据硬盘型号估算理论读写速率"""
        disk_model_lower = disk_model.lower()
        
        # 根据硬盘类型和接口估算速率
        speed_map = {
            # SSD SATA
            'ssd': 550,
            'sata': 550,
            
            # NVMe SSD
            'nvme': 3500,
            'm.2': 3500,
            'pcie': 3500,
            
            # HDD
            'hdd': 150,
            'hard disk': 150,
            
            # 特定品牌
            'samsung': 3000,
            'intel': 3000,
            'wd': 150,
            'seagate': 150,
        }
        
        # 查找匹配的速率
        for keyword, speed in speed_map.items():
            if keyword in disk_model_lower:
                return speed
        
        # 默认返回SSD速率
        return 550
    
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
    print(f"显卡品牌: {info['gpu']['品牌']}")
    print(f"显卡型号: {info['gpu']['型号']}")
    print(f"GPU芯片: {info['gpu']['GPU芯片']}")
    print(f"显卡类型: {info['gpu']['类型']}")
    print(f"显存: {info['gpu']['显存_MB']}MB")
    print(f"内存: {info['memory']['总容量_GB']}GB")
    print(f"内存频率: {info['memory']['频率_MHz']}MHz")
    print(f"DDR类型: {info['memory']['DDR类型']}")
    print(f"BIOS版本: {info['bios']['版本']}")
    print(f"BIOS制造商: {info['bios']['制造商']}")
    print(f"BIOS发布日期: {info['bios']['发布日期']}")
    print(f"BIOS是否最新: {info['bios']['是否最新']}")
    print(f"主板型号: {info['motherboard']['型号']}")
    print(f"主板制造商: {info['motherboard']['制造商']}")
    
    # 显示硬盘信息
    print(f"硬盘总数: {info['disk']['总数']}")
    print(f"硬盘总容量: {info['disk']['总容量_TB']}TB")
    for i, disk in enumerate(info['disk']['硬盘列表'], 1):
        print(f"硬盘{i}: {disk['型号']} - {disk['容量_GB']}GB ({disk['容量_TB']}TB)")
    
    # 显示硬盘读写速率
    if '读写速率' in info['disk']:
        disk_perf = info['disk']['读写速率']
        print(f"硬盘读取速率: {disk_perf['读取速率_MB/s']}MB/s")
        print(f"硬盘写入速率: {disk_perf['写入速率_MB/s']}MB/s")
        print(f"硬盘理论读取速率: {disk_perf['理论读取速率_MB/s']}MB/s")
        print(f"硬盘理论写入速率: {disk_perf['理论写入速率_MB/s']}MB/s")
    
    print(f"性能评分: {info['performance_score']}")