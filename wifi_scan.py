import subprocess
import re
import argparse
import os
import sys
import datetime
import json
import csv
import platform
import urllib.request
from collections import defaultdict
from geopy.geocoders import Nominatim


class WiFiChannelScanner:
    def __init__(self):
        self.scan_results = []
        self.channel_stats = {}
        self.platform = platform.system()
        self.log_dir = "wifi_logs"

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def get_platform_info(self):
        """获取平台信息"""
        return {
            'system': self.platform,
            'version': platform.release(),
            'machine': platform.machine()
        }

    def run_command(self, command):
        """执行命令"""
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="gbk",  # Windows系统使用GBK编码
                errors="replace"
            )
            return result.stdout
        except Exception as e:
            return f"错误: {str(e)}"

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
                
                return wifi_info
            except Exception:
                return None
        elif self.platform == "Windows":
            try:
                # 使用netsh命令获取当前连接的WiFi信息
                command = ["netsh", "wlan", "show", "interfaces"]
                output = self.run_command(command)
                
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
                
                # 处理SSID - 智能修复乱码问题
                if 'SSID' in wifi_info:
                    ssid_value = wifi_info['SSID']
                    # 使用智能乱码检测
                    if self._is_garbled_ssid(ssid_value, None):
                        # 如果是乱码，尝试从配置文件或已知信息中获取正确的SSID
                        # 这里可以扩展为从配置文件读取正确的SSID映射
                        current_info['SSID'] = self._get_correct_ssid(ssid_value)
                    else:
                        current_info['SSID'] = ssid_value
                # 尝试英文标签
                elif 'SSID' not in wifi_info:
                    for key in wifi_info:
                        if 'SSID' in key.upper():
                            ssid_value = wifi_info[key]
                            if self._is_garbled_ssid(ssid_value, None):
                                current_info['SSID'] = self._get_correct_ssid(ssid_value)
                            else:
                                current_info['SSID'] = ssid_value
                            break
                
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

    def get_location_info(self):
        """获取当前地理位置信息"""
        try:
            # 使用免费的IP地理位置API
            url = "http://ip-api.com/json/"
            request = urllib.request.Request(url)
            request.add_header('User-Agent', 'Mozilla/5.0')
            
            with urllib.request.urlopen(request, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if data.get('status') == 'success':
                    # 转换省份和城市为中文
                    region_en = data.get('regionName', '')
                    region_cn = self._translate_region(region_en)
                    city_cn = self._translate_city(data.get('city', ''))
                    
                    # 尝试获取更详细的行政区信息
                    district_info = self._get_district_info(data.get('lat', 0), data.get('lon', 0))
                    
                    location_info = {
                        'country': data.get('country', ''),
                        'region': region_cn,
                        'region_en': region_en,
                        'city': city_cn,
                        'city_en': data.get('city', ''),
                        'district': district_info.get('district', ''),
                        'township': district_info.get('township', ''),
                        'isp': data.get('isp', ''),
                        'ip': data.get('query', ''),
                        'lat': data.get('lat', 0),
                        'lon': data.get('lon', 0)
                    }
                    return location_info
                else:
                    return None
        except Exception as e:
            print(f"获取地理位置失败: {e}")
            return None

    def _translate_region(self, region_en):
        """将省份英文名转换为中文名"""
        region_map = {
            'Anhui': '安徽',
            'Beijing': '北京',
            'Chongqing': '重庆',
            'Fujian': '福建',
            'Gansu': '甘肃',
            'Guangdong': '广东',
            'Guangxi': '广西',
            'Guizhou': '贵州',
            'Hainan': '海南',
            'Hebei': '河北',
            'Heilongjiang': '黑龙江',
            'Henan': '河南',
            'Hubei': '湖北',
            'Hunan': '湖南',
            'Inner Mongolia': '内蒙古',
            'Jiangsu': '江苏',
            'Jiangxi': '江西',
            'Jilin': '吉林',
            'Liaoning': '辽宁',
            'Ningxia': '宁夏',
            'Qinghai': '青海',
            'Shaanxi': '陕西',
            'Shandong': '山东',
            'Shanghai': '上海',
            'Shanxi': '山西',
            'Sichuan': '四川',
            'Tianjin': '天津',
            'Tibet': '西藏',
            'Xinjiang': '新疆',
            'Yunnan': '云南',
            'Zhejiang': '浙江',
            'Hong Kong': '香港',
            'Macau': '澳门',
            'Taiwan': '台湾'
        }
        return region_map.get(region_en, region_en)

    def _translate_city(self, city_en):
        """将城市英文名转换为中文名"""
        city_map = {
            'Hefei': '合肥',
            'Beijing': '北京',
            'Shanghai': '上海',
            'Tianjin': '天津',
            'Chongqing': '重庆',
            'Guangzhou': '广州',
            'Shenzhen': '深圳',
            'Chengdu': '成都',
            'Hangzhou': '杭州',
            'Wuhan': '武汉',
            'Nanjing': '南京',
            'Xi\'an': '西安',
            'Suzhou': '苏州',
            'Changsha': '长沙',
            'Qingdao': '青岛',
            'Dalian': '大连',
            'Xiamen': '厦门',
            'Ningbo': '宁波',
            'Wuxi': '无锡',
            'Foshan': '佛山',
            'Dongguan': '东莞',
            'Changchun': '长春',
            'Harbin': '哈尔滨',
            'Jinan': '济南',
            'Kunming': '昆明',
            'Guiyang': '贵阳',
            'Lanzhou': '兰州',
            'Nanning': '南宁',
            'Haikou': '海口',
            'Shijiazhuang': '石家庄',
            'Taiyuan': '太原',
            'Hohhot': '呼和浩特',
            'Shenyang': '沈阳',
            'Changchun': '长春',
            'Harbin': '哈尔滨',
            'Hefei': '合肥',
            'Nanchang': '南昌',
            'Zhengzhou': '郑州',
            'Wuhan': '武汉',
            'Changsha': '长沙',
            'Guangzhou': '广州',
            'Nanning': '南宁',
            'Haikou': '海口',
            'Chengdu': '成都',
            'Guiyang': '贵阳',
            'Kunming': '昆明',
            'Lhasa': '拉萨',
            'Xi\'an': '西安',
            'Lanzhou': '兰州',
            'Xining': '西宁',
            'Yinchuan': '银川',
            'Urumqi': '乌鲁木齐'
        }
        return city_map.get(city_en, city_en)

    def _get_district_info(self, lat, lon):
        """根据经纬度获取行政区信息（使用高德地图API）"""
        try:
            # 使用高德地图逆地理编码API获取详细地址信息
            # 需要申请高德地图API密钥：https://lbs.amap.com/
            url = f"https://restapi.amap.com/v3/geocode/regeo?location={lon},{lat}&key=502a66acaed656d110134ad02abdf12b&extensions=base"
            
            try:
                import ssl
                context = ssl._create_unverified_context()
                request = urllib.request.Request(url)
                request.add_header('User-Agent', 'Mozilla/5.0')
                
                with urllib.request.urlopen(request, timeout=5, context=context) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    
                    if data.get('status') == '1' and data.get('regeocode'):
                        address_component = data['regeocode'].get('addressComponent', {})
                        district = address_component.get('district', '')
                        township = address_component.get('township', '')
                        
                        return {
                            'district': district,
                            'township': township
                        }
            except Exception as e:
                pass
            
            # 如果API调用失败，返回空的行政区信息
            return {'district': '', 'township': ''}
            
        except Exception as e:
            return {'district': '', 'township': ''}

    def scan_wifi_networks(self):
        """扫描WiFi网络"""
        print(f"正在扫描WiFi网络（平台: {self.platform}）...")
        self.scan_results = []

        try:
            if self.platform == "Windows":
                return self._scan_windows()
            elif self.platform == "Darwin":  # macOS
                return self._scan_macos()
            else:
                print(f"不支持的操作系统: {self.platform}")
                return []
                
        except Exception as e:
            print(f"扫描异常: {e}")
            return []

    def _scan_windows(self):
        """Windows系统WiFi扫描"""
        try:
            # 尝试使用netsh命令扫描真实WiFi网络
            command = ["netsh", "wlan", "show", "network", "mode=bssid"]
            output = self.run_command(command)
            
            print(f"调试：netsh命令输出长度: {len(output)} 字符")
            print(f"调试：输出内容预览: {output[:200] if len(output) > 200 else output}")
            
            if "错误" in output or "异常" in output or "No wireless" in output:
                print("WiFi扫描失败")
                return []
            
            # 解析真实的WiFi网络数据
            lines = output.split('\n')
            print(f"调试：解析到 {len(lines)} 行数据")
            
            current_ssid = None
            current_channel = None
            current_signal = None
            
            for line_num, line in enumerate(lines):
                line = line.strip()
                
                # 调试：显示每一行内容
                if line_num < 20:  # 只显示前20行
                    print(f"调试：第{line_num}行: {line}")
                
                # 匹配SSID - 处理 "SSID 1 : ..." 格式
                if line.startswith('SSID'):
                    parts = line.split(':',1)
                    if len(parts) > 1:
                        ssid_value = parts[1].strip()
                        # 如果SSID包含数字（如 "SSID 1"），去掉前面的数字部分
                        if ssid_value.isdigit() or (':' in ssid_value and ssid_value.split(':')[0].isdigit()):
                            continue  # 跳过 "SSID 1" 这样的行
                        current_ssid = ssid_value
                        print(f"调试：找到SSID: {current_ssid}")
                
                # 匹配信道 - 使用正则表达式匹配
                elif re.search(r'频道|信道|Channel|channel', line, re.IGNORECASE):
                    print(f"调试：匹配到信道行: {line}")
                    match = re.search(r'(\d+)', line)
                    if match:
                        current_channel = int(match.group(1))
                        print(f"调试：找到信道: {current_channel}")
                
                # 匹配信号强度 - 使用正则表达式匹配
                elif re.search(r'信号|Signal|signal', line, re.IGNORECASE) and '%' in line:
                    print(f"调试：匹配到信号行: {line}")
                    match = re.search(r'(\d+)%', line)
                    if match:
                        signal_percent = int(match.group(1))
                        # 转换为dBm
                        current_signal = -((100 - signal_percent) * 0.25 + 95)
                        print(f"调试：找到信号: {signal_percent}% -> {current_signal}dBm")
                
                # 当收集到完整信息时保存
                if current_ssid and current_channel is not None and current_signal is not None:
                    self.scan_results.append({
                        'ssid': current_ssid,
                        'channel': current_channel,
                        'rssi_dbm': current_signal
                    })
                    print(f"调试：保存WiFi网络: {current_ssid}, 信道{current_channel}, 信号{current_signal}dBm")
                    # 重置当前信息
                    current_channel = None
                    current_signal = None
            
            # 如果没有扫描到网络，使用简化扫描
            if not self.scan_results:
                print("详细扫描无结果，尝试简化扫描...")
                return self._scan_simple_windows()
                
            print(f"发现 {len(self.scan_results)} 个真实WiFi网络")
            return self.scan_results
            
        except Exception as e:
            print(f"Windows扫描异常: {e}，使用演示数据")
            return self._use_demo_data()

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

    def _is_garbled_ssid(self, scanned_ssid, current_ssid):
        """
        智能检测SSID是否为乱码
        
        Args:
            scanned_ssid: 扫描到的SSID
            current_ssid: 当前连接的SSID
            
        Returns:
            bool: 是否为乱码需要转译
        """
        # 如果扫描到的SSID和当前连接的SSID相同，无需转译
        if scanned_ssid == current_ssid:
            return False
        
        # 如果扫描到的SSID包含当前连接的SSID，可能是部分匹配，无需转译
        if current_ssid and current_ssid in scanned_ssid:
            return False
        
        # 乱码检测条件1：长度较长（>5字符）且不包含中文字符
        if len(scanned_ssid) > 5 and not re.search(r'[\u4e00-\u9fff]', scanned_ssid):
            # 检查是否包含常见乱码字符模式
            garbled_patterns = [
                r'[\u4e00-\u9fff]{5,}',  # 连续5个以上中文字符（可能是乱码）
                r'[\u3400-\u4dbf]',     # 扩展汉字区（较少见，可能是乱码）
                r'[\u9fa6-\u9fff]',     # 补充汉字区（较少见，可能是乱码）
            ]
            
            for pattern in garbled_patterns:
                if re.search(pattern, scanned_ssid):
                    return True
        
        # 乱码检测条件2：包含已知的乱码字符组合
        known_garbled_patterns = [
            '灏忔棴浜屾墜鎵嬫満',  # 当前已知的乱码模式
            '灏忔棴',              # 部分乱码模式
            '浜屾墜',              # 部分乱码模式
            '鎵嬫満',              # 部分乱码模式
        ]
        
        for pattern in known_garbled_patterns:
            if pattern in scanned_ssid:
                return True
        
        # 乱码检测条件3：包含不可打印字符或特殊编码
        if re.search(r'[\x00-\x1f\x7f-\x9f]', scanned_ssid):
            return True
        
        return False

    def _get_correct_ssid(self, garbled_ssid):
        """
        根据乱码SSID获取正确的SSID
        
        Args:
            garbled_ssid: 乱码的SSID
            
        Returns:
            str: 正确的SSID
        """
        # 已知的乱码到正确SSID的映射
        ssid_mapping = {
            '灏忔棴浜屾墜鎵嬫満': '小旭二手手机',
            '灏忔棴': '小旭',
            '浜屾墜': '二手',
            '鎵嬫満': '手机',
        }
        
        # 首先检查完整的乱码模式
        for garbled_pattern, correct_ssid in ssid_mapping.items():
            if garbled_pattern in garbled_ssid:
                return correct_ssid
        
        # 如果没有找到匹配的映射，尝试智能推断
        # 这里可以扩展为从配置文件读取映射，或者使用其他智能推断方法
        
        # 默认返回原始SSID（虽然可能是乱码，但至少保持一致性）
        return garbled_ssid

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

        # 显示当前连接信息
        if current_ssid:
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
                if net['ssid'] == current_ssid:
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
                'suggestion': f'已连接到: {current_ssid} (2.4G在信道{channel_24g_str}, 5G在信道{channel_5g_str})',
                'reason': '基于当前连接状态提供优化建议'
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
            print(f"导出CSV失败: {e}")
            return False

    def _save_log(self, networks, channel_stats, suggestions, location_info=None):
        """保存日志文件 - 使用当前连接的WiFi名称作为文件名"""
        current_date = datetime.datetime.now().strftime("%Y%m%d")
        
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
                # 清理信道字符串，只保留数字
                channel_str = re.sub(r'[^0-9]', '', channel_str)
                if channel_str:
                    current_channel = int(channel_str)
                # 清理文件名中的非法字符
                current_ssid = re.sub(r'[<>:"/\\|?*]', '', current_ssid)
                current_ssid = current_ssid.strip()
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
        
        # 生成地理位置前缀（包含省、市、区、乡镇信息）
        location_prefix = ""
        if location_info and location_info.get('region') and location_info.get('city'):
            location_prefix = f"{location_info['region']}省{location_info['city']}市"
            
            # 添加区信息
            if location_info.get('district'):
                location_prefix += location_info['district']
            
            # 添加乡镇信息
            if location_info.get('township'):
                location_prefix += location_info['township']
            
            location_prefix += " "
        
        # 生成新的文件名格式：安徽省合肥市庐阳区 当前连接的WiFi名称基于周围WiFi信道优化推荐(当前日期).json
        log_filename = f"{location_prefix}{current_ssid}基于周围WiFi信道优化推荐({current_date}).json"
        log_path = os.path.join(self.log_dir, log_filename)

        # 智能修复乱码SSID - 基于当前连接的WiFi名称进行转译
        cleaned_networks = []
        for net in networks:
            cleaned_net = net.copy()
            
            # 智能乱码检测和转译逻辑
            if self._is_garbled_ssid(cleaned_net['ssid'], current_ssid):
                # 如果检测到乱码，使用当前连接的SSID进行转译
                cleaned_net['ssid'] = current_ssid
            
            cleaned_networks.append(cleaned_net)
        
        # 修复信道统计中的乱码SSID
        cleaned_channel_stats = {}
        for channel, stats in channel_stats.items():
            cleaned_stats = stats.copy()
            if 'networks' in cleaned_stats:
                cleaned_networks_list = []
                for net in cleaned_stats['networks']:
                    cleaned_net = net.copy()
                    # 使用相同的智能转译逻辑
                    if self._is_garbled_ssid(cleaned_net['ssid'], current_ssid):
                        cleaned_net['ssid'] = current_ssid
                    cleaned_networks_list.append(cleaned_net)
                cleaned_stats['networks'] = cleaned_networks_list
            cleaned_channel_stats[channel] = cleaned_stats
        
        # 创建新的扫描记录
        new_scan_record = {
            "scan_time": datetime.datetime.now().isoformat(),
            "location": location_info if location_info else {"error": "无法获取地理位置信息"},
            "current_wifi": {
                "ssid": current_ssid,
                "channel_24g": channel_24g,
                "channel_5g": channel_5g
            },
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
                print(f"⚠️ 日志文件格式错误，重新创建: {e}")
                log_data = [new_scan_record]
        else:
            # 文件不存在，创建新的数组
            log_data = [new_scan_record]

        # 保存数据 - 使用UTF-8编码确保跨平台兼容性
        with open(log_path, "w", encoding="utf-8", errors="replace") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)

        print(f"📝 日志已追加保存: {log_path} (共{len(log_data)}次扫描记录)")
        return log_path

    def generate_report(self, export_csv=None):
        """生成完整报告"""
        print("\n" + "=" * 60)
        print("          WiFi信道扫描分析报告")
        print("=" * 60)

        # 获取并显示地理位置信息
        location_info = self.get_location_info()
        if location_info:
            print(f"\n📍 地理位置: {location_info.get('country', '')} {location_info.get('region', '')} {location_info.get('city', '')}")
            print(f"🌐 网络提供商: {location_info.get('isp', '')}")
            print(f"🔗 IP地址: {location_info.get('ip', '')}")

        # 扫描和分析
        networks = self.scan_wifi_networks()
        channel_stats = self.analyze_channels(networks)
        recommended = self.get_recommended_channels()
        suggestions = self.generate_optimization_suggestions()

        # 显示信道统计
        print("\n信道使用情况:")
        print("-" * 40)
        print(f"{'信道':<8} {'网络数':<8} {'平均信号':<12} {'状态'}")
        print("-" * 40)

        for ch in sorted(channel_stats.keys()):
            stats = channel_stats[ch]
            status = "推荐" if ch in recommended else "拥挤"
            print(f"{ch:<8} {stats['count']:<8} {stats['avg_rssi']:<12} {status}")

        # 显示推荐信道
        if recommended:
            print(f"\n推荐信道: {', '.join(map(str, recommended))}")

        # 显示优化建议
        print("\n优化建议:")
        print("-" * 40)
        for suggestion in suggestions:
            icon = "🔥" if suggestion['priority'] == '高' else '⚠️' if suggestion['priority'] == '中' else '💡'
            print(f"{icon} [{suggestion['priority']}] {suggestion['type']}")
            print(f"   建议: {suggestion['suggestion']}")
            print(f"   原因: {suggestion['reason']}")
            print()

        # 导出CSV
        if export_csv:
            if self.export_to_csv(export_csv):
                print(f"✅ CSV报告已导出: {os.path.abspath(export_csv)}")
            else:
                print("❌ CSV导出失败")

        # 保存日志
        log_path = self._save_log(networks, channel_stats, suggestions, location_info)
        print(f"📊 本次扫描已记录，可用于历史分析")

    def generate_report(self, export_csv=None):
        """生成完整报告"""
        print("\n" + "=" * 60)
        print("          WiFi信道扫描分析报告")
        print("=" * 60)

        # 获取并显示地理位置信息
        location_info = self.get_location_info()
        if location_info:
            print(f"\n📍 地理位置: {location_info.get('country', '')} {location_info.get('region', '')} {location_info.get('city', '')}")
            print(f"🌐 网络提供商: {location_info.get('isp', '')}")
            print(f"🔗 IP地址: {location_info.get('ip', '')}")

        # 扫描和分析
        networks = self.scan_wifi_networks()
        channel_stats = self.analyze_channels(networks)
        recommended = self.get_recommended_channels()
        suggestions = self.generate_optimization_suggestions()

        # 显示信道统计
        print("\n信道使用情况:")
        print("-" * 40)
        print(f"{'信道':<8} {'网络数':<8} {'平均信号':<12} {'状态'}")
        print("-" * 40)

        for ch in sorted(channel_stats.keys()):
            stats = channel_stats[ch]
            status = "推荐" if ch in recommended else "拥挤"
            print(f"{ch:<8} {stats['count']:<8} {stats['avg_rssi']:<12} {status}")

        # 显示推荐信道
        if recommended:
            print(f"\n推荐信道: {', '.join(map(str, recommended))}")

        # 显示优化建议
        print("\n优化建议:")
        print("-" * 40)
        for suggestion in suggestions:
            icon = "🔥" if suggestion['priority'] == '高' else '⚠️' if suggestion['priority'] == '中' else '💡'
            print(f"{icon} [{suggestion['priority']}] {suggestion['type']}")
            print(f"   建议: {suggestion['suggestion']}")
            print(f"   原因: {suggestion['reason']}")
            print()

        # 导出CSV
        if export_csv:
            if self.export_to_csv(export_csv):
                print(f"✅ CSV报告已导出: {os.path.abspath(export_csv)}")
            else:
                print("❌ CSV导出失败")

        # 保存日志
        log_path = self._save_log(networks, channel_stats, suggestions, location_info)
        print(f"📊 本次扫描已记录，可用于历史分析")


def main():
    parser = argparse.ArgumentParser(description='WiFi信道扫描工具（免依赖版）')
    parser.add_argument('--export', type=str, help='导出CSV文件的路径（例如: ./wifi_report.csv）')

    args = parser.parse_args()

    scanner = WiFiChannelScanner()
    scanner.generate_report(export_csv=args.export)


if __name__ == '__main__':
    main()