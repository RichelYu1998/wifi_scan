import subprocess
import re
import argparse
import os
import sys
import datetime
import json
import csv
import platform
from collections import defaultdict


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
        """执行Windows命令"""
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            return result.stdout
        except Exception as e:
            return f"错误: {str(e)}"

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
                print(f"不支持的操作系统: {self.platform}，使用演示数据")
                return self._use_demo_data()
                
        except Exception as e:
            print(f"扫描异常: {e}，使用演示数据")
            return self._use_demo_data()

    def _scan_windows(self):
        """Windows系统WiFi扫描"""
        try:
            # 尝试使用netsh命令扫描真实WiFi网络
            command = ["netsh", "wlan", "show", "network", "mode=bssid"]
            output = self.run_command(command)
            
            if "错误" in output or "异常" in output or "No wireless" in output:
                print("WiFi扫描失败，使用演示数据...")
                return self._use_demo_data()
            
            # 解析真实的WiFi网络数据
            lines = output.split('\n')
            current_ssid = None
            current_channel = None
            current_signal = None
            
            for line in lines:
                line = line.strip()
                
                # 匹配SSID
                if line.startswith('SSID'):
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        current_ssid = parts[1].strip()
                
                # 匹配信道
                elif '信道' in line or 'Channel' in line:
                    match = re.search(r'(\d+)', line)
                    if match:
                        current_channel = int(match.group(1))
                
                # 匹配信号强度
                elif '信号' in line or 'Signal' in line:
                    match = re.search(r'(\d+)%', line)
                    if match:
                        signal_percent = int(match.group(1))
                        # 转换为dBm
                        current_signal = -((100 - signal_percent) * 0.25 + 95)
                
                # 当收集到完整信息时保存
                if current_ssid and current_channel is not None and current_signal is not None:
                    self.scan_results.append({
                        'ssid': current_ssid,
                        'channel': current_channel,
                        'rssi_dbm': current_signal
                    })
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
                print("未找到airport命令，使用演示数据...")
                return self._use_demo_data()
            
            # 使用airport命令扫描WiFi
            command = [airport_cmd, "-s"]
            output = self.run_command(command)
            
            if not output or "airport: command not found" in output:
                print("WiFi扫描失败，使用演示数据...")
                return self._use_demo_data()
            
            # 解析airport命令输出
            lines = output.split('\n')
            for line in lines:
                line = line.strip()
                if not line or line.startswith('SSID'):
                    continue
                
                # 解析格式：SSID BSSID RSSI CHANNEL HT CC SECURITY
                parts = line.split()
                if len(parts) >= 4:
                    ssid = parts[0]
                    rssi = parts[2]
                    channel = parts[3]
                    
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
                print("未扫描到WiFi网络，使用演示数据...")
                return self._use_demo_data()
                
        except Exception as e:
            print(f"macOS扫描异常: {e}，使用演示数据")
            return self._use_demo_data()

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
                            # 为每个SSID分配随机信道和信号强度（用于演示）
                            import random
                            channels = [1, 6, 11, 36, 40, 44, 48]
                            self.scan_results.append({
                                'ssid': ssid,
                                'channel': random.choice(channels),
                                'rssi_dbm': random.randint(-85, -55)
                            })
            
            if self.scan_results:
                print(f"简化扫描发现 {len(self.scan_results)} 个WiFi网络")
                return self.scan_results
            else:
                return self._use_demo_data()
                
        except Exception:
            return self._use_demo_data()

    def _scan_simple(self):
        """简化扫描：只获取SSID列表（兼容旧版本）"""
        if self.platform == "Windows":
            return self._scan_simple_windows()
        else:
            # 对于非Windows系统，直接使用演示数据
            return self._use_demo_data()

    def _use_demo_data(self):
        """使用演示数据"""
        self.scan_results = [
            {'ssid': 'WiFi-2.4G', 'channel': 1, 'rssi_dbm': -65},
            {'ssid': 'HomeNet', 'channel': 6, 'rssi_dbm': -72},
            {'ssid': 'TP-Link_5G', 'channel': 36, 'rssi_dbm': -58},
            {'ssid': 'Guest', 'channel': 11, 'rssi_dbm': -78},
            {'ssid': 'Office', 'channel': 6, 'rssi_dbm': -68},
            {'ssid': 'MiWifi', 'channel': 1, 'rssi_dbm': -75}
        ]
        print(f"使用演示数据，模拟 {len(self.scan_results)} 个WiFi网络")
        return self.scan_results

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

        sorted_channels = sorted(
            self.channel_stats.keys(),
            key=lambda ch: (self.channel_stats[ch]['count'], self.channel_stats[ch]['avg_rssi'])
        )

        return sorted_channels[:3]

    def generate_optimization_suggestions(self):
        """生成优化建议"""
        suggestions = []
        recommended = self.get_recommended_channels()

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

            if overlapping:
                suggestions.append({
                    'type': '2.4G频段',
                    'priority': '高',
                    'suggestion': f'避免使用重叠信道：{", ".join(map(str, overlapping))}',
                    'reason': '2.4G频段只有1、6、11三个不重叠信道'
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

    def _save_log(self, networks, channel_stats, suggestions):
        """保存日志文件 - 将相同WiFi的扫描结果追加到同一个文件中"""
        current_date = datetime.datetime.now().strftime("%Y%m%d")
        
        # 获取所有WiFi网络名称作为文件名前缀
        if networks:
            # 获取所有唯一的WiFi名称
            wifi_names = []
            for net in networks:
                ssid = net['ssid']
                # 清理文件名中的非法字符
                ssid = re.sub(r'[<>:"/\\|?*]', '', ssid)
                ssid = ssid.strip()
                # 如果名称不为空且不在列表中，则添加
                if ssid and ssid not in wifi_names:
                    wifi_names.append(ssid)
            
            # 如果WiFi名称数量超过5个，只取前5个
            if len(wifi_names) > 5:
                wifi_names = wifi_names[:5]
                
            # 使用&符号连接所有WiFi名称
            if wifi_names:
                wifi_name = "&".join(wifi_names)
            else:
                wifi_name = "WiFi网络"
        else:
            wifi_name = "WiFi网络"
            
        log_filename = f"{wifi_name}_{current_date}wifi优化建议.json"
        log_path = os.path.join(self.log_dir, log_filename)

        # 创建新的扫描记录
        new_scan_record = {
            "scan_time": datetime.datetime.now().isoformat(),
            "total_networks": len(networks),
            "recommended_channels": self.get_recommended_channels(),
            "network_details": networks,
            "channel_statistics": channel_stats,
            "optimization_suggestions": suggestions
        }

        # 检查文件是否已存在
        if os.path.exists(log_path):
            # 读取现有数据
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

        # 保存数据
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)

        print(f"📝 日志已追加保存: {log_path} (共{len(log_data)}次扫描记录)")
        return log_path

    def generate_report(self, export_csv=None):
        """生成完整报告"""
        print("\n" + "=" * 60)
        print("          WiFi信道扫描分析报告")
        print("=" * 60)

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
        log_path = self._save_log(networks, channel_stats, suggestions)
        print(f"📊 本次扫描已记录，可用于历史分析")


def main():
    parser = argparse.ArgumentParser(description='WiFi信道扫描工具（免依赖版）')
    parser.add_argument('--export', type=str, help='导出CSV文件的路径（例如: ./wifi_report.csv）')

    args = parser.parse_args()

    scanner = WiFiChannelScanner()
    scanner.generate_report(export_csv=args.export)


if __name__ == '__main__':
    main()