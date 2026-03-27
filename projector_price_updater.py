#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投影仪价格更新器 - 支持实时价格更新和国补对比
"""

import json
import os
import time
from datetime import datetime, timedelta
import urllib.request
import urllib.error


class ProjectorPriceUpdater:
    """投影仪价格更新器"""
    
    def __init__(self, price_data_file=None, projector_data_file=None):
        self.price_data_file = price_data_file or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            'projector_price_data.json'
        )
        self.projector_data_file = projector_data_file or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            'projector_data.json'
        )
        
        self.config = {
            'update_interval_days': 7,
            'national_subsidy_rate': 0.20,
            'data_sources': {
                'price': [
                    'https://raw.githubusercontent.com/RichelYu1998/wifi_scan/main/projector_price_data.json',
                    'https://cdn.jsdelivr.net/gh/RichelYu1998/wifi_scan@main/projector_price_data.json',
                ]
            }
        }
    
    def _load_json(self, file_path):
        """加载JSON数据"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"加载数据失败 {file_path}: {e}")
            return None
    
    def _save_json(self, file_path, data):
        """保存JSON数据"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存数据失败 {file_path}: {e}")
            return False
    
    def _download_json(self, url, timeout=10):
        """从URL下载JSON数据"""
        try:
            request = urllib.request.Request(url)
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
            
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"下载失败 {url}: {e}")
            return None
    
    def _download_from_multiple_sources(self, data_type, timeout=10):
        """从多个数据源尝试下载数据"""
        urls = self.config['data_sources'].get(data_type, [])
        
        for i, url in enumerate(urls):
            print(f"尝试从数据源 {i+1}/{len(urls)} 下载数据: {url}")
            data = self._download_json(url, timeout)
            
            if data and 'prices' in data:
                print(f"✅ 成功从数据源 {i+1} 下载价格数据")
                data['source'] = url
                return data
        
        print(f"❌ 所有数据源都无法下载价格数据")
        return None
    
    def _calculate_subsidy_price(self, price):
        """计算国补价格"""
        if price <= 0:
            return price
        
        subsidy_amount = price * self.config['national_subsidy_rate']
        subsidy_price = price - subsidy_amount
        
        return int(subsidy_price // 10) * 10
    
    def _is_data_expired(self, file_path):
        """检查数据是否过期"""
        data = self._load_json(file_path)
        
        if not data:
            return True
        
        update_time_str = data.get('update_time', '')
        if not update_time_str:
            return True
        
        try:
            update_time = datetime.fromisoformat(update_time_str)
            expiry_time = update_time + timedelta(days=self.config['update_interval_days'])
            return datetime.now() > expiry_time
        except:
            return True
    
    def _create_price_info(self, projector_id, base_price, platform='默认'):
        """创建价格信息"""
        subsidy_price = self._calculate_subsidy_price(base_price)
        
        return {
            'original_price': base_price,
            'subsidy_price': subsidy_price,
            'subsidy_amount': base_price - subsidy_price,
            'has_subsidy': True,
            'subsidy_rate': self.config['national_subsidy_rate'],
            'platform': platform,
            'update_time': datetime.now().isoformat()
        }
    
    def _get_default_price_data(self):
        """获取默认价格数据"""
        projectors = self._load_json(self.projector_data_file)
        if not projectors:
            projectors = []
        
        price_data = {
            'update_time': datetime.now().isoformat(),
            'source': 'default',
            'prices': {}
        }
        
        for projector in projectors.get('projectors', []):
            projector_id = projector.get('id')
            base_price = projector.get('price', 0)
            price_data['prices'][str(projector_id)] = self._create_price_info(projector_id, base_price)
        
        return price_data
    
    def load_price_data(self):
        """加载价格数据"""
        return self._load_json(self.price_data_file) or {}
    
    def save_price_data(self, price_data):
        """保存价格数据"""
        return self._save_json(self.price_data_file, price_data)
    
    def load_projector_data(self):
        """加载投影仪数据"""
        data = self._load_json(self.projector_data_file)
        return data.get('projectors', []) if data else []
    
    def update_price_data(self, force_update=False):
        """更新价格数据"""
        print("=== 投影仪价格更新器 ===")
        print()
        
        if not force_update and not self._is_data_expired(self.price_data_file):
            print("✅ 价格数据是最新的，无需更新")
            return self.load_price_data()
        
        print("🔄 开始更新投影仪价格数据...")
        print()
        
        network_data = self._download_from_multiple_sources('price')
        price_data = network_data if network_data else self._get_default_price_data()
        
        print("✅ 成功从网络获取价格数据" if network_data else "⚠️ 使用默认价格数据（基于投影仪基础价格计算）")
        
        if self.save_price_data(price_data):
            print(f"✅ 价格数据已保存到: {self.price_data_file}")
        else:
            print("❌ 保存价格数据失败")
        
        print()
        print("📊 价格数据统计:")
        print(f"   更新时间: {price_data.get('update_time', 'N/A')}")
        print(f"   数据来源: {price_data.get('source', 'N/A')}")
        print(f"   投影仪数量: {len(price_data.get('prices', {}))}")
        print()
        
        return price_data
    
    def get_projector_price(self, projector_id, use_subsidy=False):
        """获取投影仪价格"""
        price_data = self.load_price_data()
        
        if not price_data:
            return None
        
        projector_price = price_data.get('prices', {}).get(str(projector_id))
        
        if not projector_price:
            return None
        
        return {
            'price': projector_price.get('subsidy_price' if use_subsidy else 'original_price', 0),
            'original_price': projector_price.get('original_price', 0),
            'subsidy_amount': projector_price.get('subsidy_amount', 0) if use_subsidy else 0,
            'has_subsidy': projector_price.get('has_subsidy', False) and use_subsidy,
            'subsidy_rate': projector_price.get('subsidy_rate', 0) if use_subsidy else 0
        }
    
    def get_all_prices(self, use_subsidy=False):
        """获取所有投影仪价格"""
        price_data = self.load_price_data()
        
        if not price_data:
            return {}
        
        return {
            int(projector_id): {
                'price': price_info.get('subsidy_price' if use_subsidy else 'original_price', 0),
                'original_price': price_info.get('original_price', 0),
                'subsidy_price': price_info.get('subsidy_price', 0),
                'subsidy_amount': price_info.get('subsidy_amount', 0),
                'has_subsidy': price_info.get('has_subsidy', False) and use_subsidy,
                'subsidy_rate': price_info.get('subsidy_rate', 0) if use_subsidy else 0,
                'platform': price_info.get('platform', '默认'),
                'update_time': price_info.get('update_time', '')
            }
            for projector_id, price_info in price_data.get('prices', {}).items()
        }
    
    def compare_prices(self, projector_id):
        """对比原价和国补价格"""
        price_data = self.load_price_data()
        
        if not price_data:
            return None
        
        projector_price = price_data.get('prices', {}).get(str(projector_id))
        
        if not projector_price:
            return None
        
        original_price = projector_price.get('original_price', 0)
        subsidy_price = projector_price.get('subsidy_price', 0)
        subsidy_amount = projector_price.get('subsidy_amount', 0)
        subsidy_rate = projector_price.get('subsidy_rate', 0)
        
        return {
            'original_price': original_price,
            'subsidy_price': subsidy_price,
            'subsidy_amount': subsidy_amount,
            'subsidy_rate': subsidy_rate,
            'savings_rate': (subsidy_amount / original_price * 100) if original_price > 0 else 0,
            'has_subsidy': projector_price.get('has_subsidy', False),
            'platform': projector_price.get('platform', '默认'),
            'update_time': projector_price.get('update_time', '')
        }


def main():
    """主函数"""
    updater = ProjectorPriceUpdater()
    
    price_data = updater.update_price_data(force_update=True)
    
    print("="*60)
    print("价格数据示例:")
    print("="*60)
    
    for i, (projector_id, price_info) in enumerate(list(price_data.get('prices', {}).items())[:5], 1):
        print(f"\n{i}. 投影仪ID: {projector_id}")
        print(f"   原价: ¥{price_info['original_price']}")
        print(f"   国补价: ¥{price_info['subsidy_price']}")
        print(f"   优惠金额: ¥{price_info['subsidy_amount']}")
        print(f"   优惠比例: {price_info['subsidy_rate']*100:.0f}%")
        print(f"   平台: {price_info['platform']}")
    
    print("\n" + "="*60)
    print("✅ 价格数据更新完成！")
    print("="*60)


if __name__ == '__main__':
    main()