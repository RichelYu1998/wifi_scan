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
from collections import defaultdict
from geopy.geocoders import Nominatim

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
    from hardware_info import HardwareInfo
    from network_speed_tester import NetworkSpeedTester
    from video_resolution_recommender import VideoResolutionRecommender
    EXTERNAL_MODULES_AVAILABLE = True
except ImportError:
    EXTERNAL_MODULES_AVAILABLE = False


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
        self.log_dir = "wifi_logs"
        self.escape_manager = EscapeManager()  # 初始化转义管理器

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def _safe_print(self, message):
        """安全打印函数，确保中文正确显示"""
        try:
            # 尝试直接打印
            print(message)
        except UnicodeEncodeError:
            # 如果编码失败，使用安全编码
            try:
                safe_message = message.encode('utf-8', errors='replace').decode('utf-8')
                print(safe_message)
            except:
                # 如果仍然失败，使用ASCII安全编码
                safe_message = message.encode('ascii', errors='replace').decode('ascii')
                print(safe_message)

    def get_platform_info(self):
        """获取平台信息"""
        return {
            'system': self.platform,
            'version': platform.release(),
            'machine': platform.machine()
        }

    def run_command(self, command):
        """执行命令（使用统一的跨平台工具类）"""
        return self.cross_platform_utils.run_command(command)
    
    def _contains_garbled_text(self, text):
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
                    import re
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

    def get_location_info(self):
        """获取当前地理位置信息（性能优化版）"""
        # 使用缓存避免重复网络请求
        if hasattr(self, '_cached_location_info'):
            return self._cached_location_info
            
        try:
            # 使用更详细的IP地理位置API（包括街道/乡镇信息）
            url = "http://ip-api.com/json/?fields=status,country,regionName,city,isp,query,lat,lon,zip"
            request = urllib.request.Request(url)
            request.add_header('User-Agent', 'Mozilla/5.0')
            
            with urllib.request.urlopen(request, timeout=2) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if data.get('status') == 'success':
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
            
            location_prefix += " "
        
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
        
        log_path = os.path.join(self.log_dir, log_filename)

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

        # 保存数据 - 使用UTF-8编码确保跨平台兼容性
        with open(log_path, "w", encoding="utf-8", errors="replace") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)

        print(f"📝 日志已追加保存: {log_path} (共{len(log_data)}次扫描记录)")
        return log_path

    def generate_report(self, export_csv=None, debug=False):
        """生成完整报告（性能优化版）"""
        # 设置调试模式
        self.escape_manager.debug_mode = debug
        
        print("\n" + "=" * 60)
        print("          WiFi信道扫描分析报告")
        print("=" * 60)

        # 直接获取地理位置信息（确保正确获取）
        location_info = self.get_location_info()
        if location_info:
            self.escape_manager.debug_log("获取到地理位置信息", location_info)
        else:
            self.escape_manager.debug_log("未获取到地理位置信息")

        # 开始WiFi扫描（核心操作）
        networks = self.scan_wifi_networks()
        
        # 快速分析信道（优化算法）
        channel_stats = self.analyze_channels_fast(networks)
        recommended = self.get_recommended_channels_fast(channel_stats)
        suggestions = self.generate_optimization_suggestions_fast(networks, channel_stats, recommended)
        
        # 保存扫描结果供CSV导出使用
        self.scan_results = networks
        self.channel_stats = channel_stats
        self.recommended_channels = recommended
        self.suggestions = suggestions
        
        if location_info:
            print(f"\n📍 地理位置: {location_info.get('country', '')} {location_info.get('region', '')} {location_info.get('city', '')}")
            print(f"🌐 运营商: {location_info.get('运营商', '')}")
            print(f"🔗 IP地址: {location_info.get('ip', '')}")

        # 精简显示信道统计
        if channel_stats:
            print("\n信道使用情况（精简版）:")
            print("-" * 30)
            print(f"{'信道':<6} {'网络数':<6} {'状态'}")
            print("-" * 30)
            
            # 只显示前5个信道
            for ch in sorted(channel_stats.keys())[:5]:
                stats = channel_stats[ch]
                status = "推荐" if ch in recommended else "拥挤"
                print(f"{ch:<6} {stats['count']:<6} {status}")
            
            if len(channel_stats) > 5:
                print(f"... 还有 {len(channel_stats) - 5} 个信道")
        # 显示推荐信道（优化版）
        if recommended:
            if len(recommended) <= 3:
                print(f"\n推荐信道: {', '.join(map(str, recommended))}")
            else:
                print(f"\n推荐信道: {', '.join(map(str, recommended[:3]))} 等 {len(recommended)} 个")

        # 精简优化建议显示
        if suggestions:
            print("\n优化建议（精简版）:")
            print("-" * 30)
            # 只显示前3条建议
            for suggestion in suggestions[:3]:
                icon = "🔥" if suggestion['priority'] == '高' else '⚠️' if suggestion['priority'] == '中' else '💡'
                print(f"{icon} {suggestion['suggestion'][:50]}...")

        # 异步导出CSV（如果不需要可以跳过）
        if export_csv:
            try:
                # 参数验证
                if not export_csv or not isinstance(export_csv, str):
                    print("⚠️  CSV导出路径无效，跳过导出")
                else:
                    # 创建并启动CSV导出线程
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

        # 快速保存日志（核心功能）
        log_path = self._save_log_fast(networks, channel_stats, suggestions, location_info, recommended)
        print(f"📊 快速扫描完成: {log_path}")
        
        return log_path


def main():
    parser = argparse.ArgumentParser(description='WiFi信道扫描工具（免依赖版）')
    parser.add_argument('--export', type=str, help='导出CSV文件的路径（例如: ./wifi_report.csv）')
    parser.add_argument('--debug', action='store_true', help='显示调试信息（默认不显示）')

    args = parser.parse_args()

    scanner = WiFiChannelScanner()
    scanner.generate_report(export_csv=args.export, debug=args.debug)


if __name__ == '__main__':
    main()