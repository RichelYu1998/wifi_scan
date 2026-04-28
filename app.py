from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = os.path.join(BASE_DIR, 'json')

BRAND_ALIAS = {
    '小米': '米家',
    '小爱': '米家',
}

ISP_ALIAS = {
    'Chinanet': '中国电信',
    'ChinaUnicom': '中国联通',
    'ChinaMobile': '中国移动',
    'CT': '中国电信',
    'CU': '中国联通',
    'CM': '中国移动',
}

def load_wireless_card_config():
    config_file = os.path.join(JSON_DIR, 'config', 'wireless_card_brands.json')
    return load_json(config_file, {'wireless_card_brands': {}, 'wireless_card_types': {}})

def load_network_card_models():
    config_file = os.path.join(JSON_DIR, 'config', 'network_card_models.json')
    return load_json(config_file, {'network_card_models': {}})

def load_json(file_path, default=None):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except: pass
    return default

def get_wifi_data():
    data = {'networks': [], 'location': {}, 'recommendation': {'channels': []}, 'history': {'channels': [], 'networks': []}}
    
    network_file = os.path.join(JSON_DIR, 'network', '安徽_合肥', 'network_info.json')
    info = load_json(network_file, [])
    
    if info and len(info) > 0:
        latest = info[-1]
        loc_info = latest.get('location_info', {})
        data['location'] = {
            'full': f"{loc_info.get('country', '中国')} {loc_info.get('region', '安徽')} {loc_info.get('city', '合肥')}",
            'isp': ISP_ALIAS.get(loc_info.get('isp', 'Chinanet'), loc_info.get('isp', 'Chinanet')),
            'ip': loc_info.get('ip', '')
        }
        
        all_channels = []
        all_networks = []
        
        for record in info[-10:]:
            for net in record.get('networks', []):
                ch = net.get('channel')
                if ch:
                    all_channels.append(ch)
                    all_networks.append(net.get('ssid', '未知'))
        
        channel_count = {}
        for ch in all_channels:
            channel_count[ch] = channel_count.get(ch, 0) + 1
        
        sorted_channels = sorted(channel_count.items(), key=lambda x: x[1], reverse=True)
        history_channels = [ch for ch, _ in sorted_channels[:10]]
        
        used_2g = [ch for ch in history_channels if ch <= 14]
        used_5g = [ch for ch in history_channels if ch > 14]
        
        rec_2g = []
        for ch in [1, 6, 11]:
            if ch not in history_channels[:5]:
                rec_2g.append(ch)
        if not rec_2g:
            for ch in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
                if ch not in history_channels[:3]:
                    rec_2g.append(ch)
                    if len(rec_2g) >= 2:
                        break
        
        rec_5g = [36, 40, 44, 48, 149, 153, 157, 161]
        rec_5g = [ch for ch in rec_5g if ch not in history_channels[:5]][:3]
        
        data['recommendation'] = {'channels': rec_2g + rec_5g}
        data['history'] = {
            'channels': history_channels[:10],
            'networks': list(set(all_networks))[:10]
        }
    
    return data

def get_hardware_data():
    hardware_file = os.path.join(JSON_DIR, 'hardware', 'hardware_info.json')
    info = load_json(hardware_file, [])
    
    data = {'cpu': {}, 'gpu': {}, 'memory': {}, 'system': {}, 'motherboard': {}, 'network': {}}
    
    if info and len(info) > 0:
        latest = info[-1]
        hw = latest.get('hardware_info', {})
        
        cpu = hw.get('cpu', {})
        data['cpu'] = {
            'name': cpu.get('name', 'Apple M2 Pro'),
            'architecture': cpu.get('architecture', 'arm64'),
            'cores': str(cpu.get('cores', 10)),
            'frequency': cpu.get('frequency', '3200 MHz')
        }
        
        gpu = hw.get('gpu', {})
        data['gpu'] = {
            'name': gpu.get('name', 'Apple M2 Pro'),
            'memory': gpu.get('memory', '8.0 GB')
        }
        
        mem = hw.get('memory', {})
        data['memory'] = {
            'total': mem.get('total', '16.0 GB'),
            'usage': mem.get('usage', '70%')
        }
        
        sys_info = hw.get('system', {})
        data['system'] = {
            'os': sys_info.get('操作系统', 'macOS'),
            'version': sys_info.get('版本', '13.7.8')
        }
        
        sys_info_str = sys_info.get('操作系统', '')
        if 'Apple' in sys_info_str or 'macOS' in sys_info_str or 'Mac' in sys_info_str:
            data['network'] = {
                'name': 'AirPort (Wi-Fi)',
                'type': 'WiFi 6 (802.11ax)',
                'max_speed': '2.4 Gbps',
                'band': '2.4GHz / 5GHz',
                'brand': 'Apple',
                'model': 'M2 Pro 集成'
            }
        else:
            data['network'] = {
                'name': '以太网',
                'type': '千兆',
                'max_speed': '1 Gbps',
                'band': '有线',
                'brand': '未知',
                'model': '未知'
            }
        
        card_config = load_wireless_card_config()
        card_models = load_network_card_models()
        
        data['wireless_card_types'] = list(card_config.get('wireless_card_types', {}).keys())
        data['network_card_brands'] = list(card_config.get('wireless_card_brands', {}).keys())
        
        network_cards = []
        for brand, info in card_models.get('network_card_models', {}).items():
            if isinstance(info, dict):
                network_cards.append({
                    'brand': info.get('brand', brand),
                    'type': '外置USB网卡' if info.get('models') else '内置无线网卡'
                })
        data['available_network_cards'] = network_cards[:10]
        
        mb = hw.get('motherboard', {})
        data['motherboard'] = {
            'manufacturer': mb.get('manufacturer', mb.get('制造商', 'Apple')),
            'model': mb.get('model', mb.get('型号', 'Mac14,9'))
        }
        
        data['performance_score'] = hw.get('performance_score', '85')
    
    return data

def get_projectors_data():
    projector_file = os.path.join(JSON_DIR, 'projector', 'projector_data.json')
    data = load_json(projector_file, {'projectors': []})
    
    projectors = []
    for p in data.get('projectors', []):
        name = f"{p.get('brand', '')} {p.get('model', '')}"
        search_name = name.replace(' ', '+')
        
        projectors.append({
            'name': name,
            'price': str(p.get('price', 0)),
            'brand': p.get('brand', ''),
            'model': p.get('model', ''),
            'resolution': p.get('resolution', ''),
            'brightness': f"{p.get('brightness', 0)}流明",
            'contrast': f"{p.get('contrast', 0)}:1",
            'scenario': p.get('usage_scenario', '家庭娱乐'),
            'reason': '',
            'jd_url': f"https://search.jd.com/search?keyword={search_name}",
            'tb_url': f"https://s.taobao.com/search?q={search_name}",
            'tmall_url': f"https://list.tmall.com/search_product.htm?q={search_name}"
        })
    
    return {'projectors': projectors}

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/api/wifi-scan')
def wifi_scan():
    return jsonify({'success': True, 'data': get_wifi_data()})

@app.route('/api/hardware')
def hardware():
    data = get_hardware_data()
    return jsonify({'success': True, 'data': data})

@app.route('/api/projector')
def projector():
    budget = request.args.get('budget')
    brand = request.args.get('brand')
    resolution = request.args.get('resolution')
    
    all_projectors = get_projectors_data()['projectors']
    filtered = all_projectors
    
    if brand:
        brand = BRAND_ALIAS.get(brand, brand)
        filtered = [p for p in filtered if brand.lower() in p['brand'].lower()]
    
    if resolution:
        filtered = [p for p in filtered if resolution in p['resolution']]
    
    if budget:
        try:
            min_budget = int(budget)
            max_budget = min_budget + 2000 if '-' not in budget else int(budget.split('-')[1])
            filtered = [p for p in filtered if min_budget <= int(p['price']) <= max_budget]
        except: pass
    
    return jsonify({'success': True, 'data': {'projectors': filtered}})

@app.route('/api/all-in-one')
def all_in_one():
    return jsonify({'success': True, 'data': get_wifi_data()})

@app.route('/api/status')
def status():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("✅ 服务器启动成功!")
    app.run(host='0.0.0.0', port=5001, debug=False)