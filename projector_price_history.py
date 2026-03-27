#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投影仪价格历史追踪器 - 记录和对比历史价格
"""

import json
import os
from datetime import datetime, timedelta


class ProjectorPriceHistory:
    """投影仪价格历史追踪器"""
    
    def __init__(self, history_file=None):
        self.history_file = history_file or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            'projector_price_history.json'
        )
        self.config = {
            'retention_days': 30,
            'default_days': 30
        }
        self.price_history = self._load_json(self.history_file).get('history', {})
    
    def _load_json(self, file_path):
        """加载JSON数据"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"加载数据失败 {file_path}: {e}")
            return {}
    
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
    
    def _cleanup_old_records(self, projector_id_str, days=None):
        """清理旧记录"""
        if projector_id_str not in self.price_history:
            return
        
        days = days or self.config['retention_days']
        records = self.price_history[projector_id_str]['records']
        cutoff_time = datetime.now() - timedelta(days=days)
        
        self.price_history[projector_id_str]['records'] = [
            record for record in records
            if datetime.fromisoformat(record['timestamp']) > cutoff_time
        ]
    
    def _create_price_record(self, original_price, subsidy_price, 
                           subsidy_amount, subsidy_rate, platform='默认'):
        """创建价格记录"""
        return {
            'timestamp': datetime.now().isoformat(),
            'original_price': original_price,
            'subsidy_price': subsidy_price,
            'subsidy_amount': subsidy_amount,
            'subsidy_rate': subsidy_rate,
            'platform': platform
        }
    
    def _filter_records_by_date(self, records, days=None):
        """根据日期过滤记录"""
        days = days or self.config['default_days']
        cutoff_time = datetime.now() - timedelta(days=days)
        
        return [
            record for record in records
            if datetime.fromisoformat(record['timestamp']) > cutoff_time
        ]
    
    def _calculate_price_stats(self, records, key):
        """计算价格统计"""
        if not records:
            return None
        
        values = [record[key] for record in records]
        return {
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'count': len(values)
        }
    
    def add_price_record(self, projector_id, original_price, subsidy_price, 
                      subsidy_amount, subsidy_rate, platform='默认'):
        """添加价格记录"""
        projector_id_str = str(projector_id)
        
        if projector_id_str not in self.price_history:
            self.price_history[projector_id_str] = {'records': []}
        
        record = self._create_price_record(
            original_price, subsidy_price, 
            subsidy_amount, subsidy_rate, platform
        )
        
        self.price_history[projector_id_str]['records'].append(record)
        self._cleanup_old_records(projector_id_str)
        self._save_json(self.history_file, {'history': self.price_history})
        
        return record
    
    def get_price_history(self, projector_id, days=None):
        """获取价格历史"""
        projector_id_str = str(projector_id)
        
        if projector_id_str not in self.price_history:
            return []
        
        records = self.price_history[projector_id_str]['records']
        filtered_records = self._filter_records_by_date(records, days)
        
        return sorted(filtered_records, key=lambda x: x['timestamp'])
    
    def get_price_trend(self, projector_id, days=None):
        """获取价格趋势"""
        history = self.get_price_history(projector_id, days)
        
        if len(history) < 2:
            return None
        
        latest, earliest = history[-1], history[0]
        
        return {
            'original_price_change': latest['original_price'] - earliest['original_price'],
            'original_price_change_rate': (
                (latest['original_price'] - earliest['original_price']) / earliest['original_price'] * 100
                if earliest['original_price'] > 0 else 0
            ),
            'subsidy_price_change': latest['subsidy_price'] - earliest['subsidy_price'],
            'subsidy_price_change_rate': (
                (latest['subsidy_price'] - earliest['subsidy_price']) / earliest['subsidy_price'] * 100
                if earliest['subsidy_price'] > 0 else 0
            ),
            'earliest_price': earliest['original_price'],
            'latest_price': latest['original_price'],
            'earliest_subsidy_price': earliest['subsidy_price'],
            'latest_subsidy_price': latest['subsidy_price'],
            'record_count': len(history),
            'days': days or self.config['default_days']
        }
    
    def get_lowest_price(self, projector_id, days=None):
        """获取最低价格"""
        history = self.get_price_history(projector_id, days)
        
        if not history:
            return None
        
        lowest_record = min(history, key=lambda x: x['subsidy_price'])
        
        return {
            'original_price': lowest_record['original_price'],
            'subsidy_price': lowest_record['subsidy_price'],
            'timestamp': lowest_record['timestamp'],
            'platform': lowest_record['platform']
        }
    
    def get_highest_price(self, projector_id, days=None):
        """获取最高价格"""
        history = self.get_price_history(projector_id, days)
        
        if not history:
            return None
        
        highest_record = max(history, key=lambda x: x['original_price'])
        
        return {
            'original_price': highest_record['original_price'],
            'subsidy_price': highest_record['subsidy_price'],
            'timestamp': highest_record['timestamp'],
            'platform': highest_record['platform']
        }
    
    def get_average_price(self, projector_id, days=None):
        """获取平均价格"""
        history = self.get_price_history(projector_id, days)
        
        if not history:
            return None
        
        return {
            'average_original_price': sum(r['original_price'] for r in history) / len(history),
            'average_subsidy_price': sum(r['subsidy_price'] for r in history) / len(history),
            'record_count': len(history)
        }
    
    def get_all_projectors_history(self, days=None):
        """获取所有投影仪的价格历史摘要"""
        return {
            int(projector_id_str): {
                'trend': self.get_price_trend(int(projector_id_str), days),
                'lowest': self.get_lowest_price(int(projector_id_str), days),
                'highest': self.get_highest_price(int(projector_id_str), days),
                'average': self.get_average_price(int(projector_id_str), days)
            }
            for projector_id_str in self.price_history
        }
    
    def export_price_history_csv(self, projector_id, output_file=None):
        """导出价格历史为CSV"""
        history = self.get_price_history(projector_id)
        
        if not history:
            return False
        
        output_file = output_file or f"projector_{projector_id}_price_history.csv"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("时间,原价,国补价,优惠金额,优惠比例,平台\n")
                
                for record in history:
                    f.write(
                        f"{record['timestamp']},{record['original_price']},"
                        f"{record['subsidy_price']},{record['subsidy_amount']},"
                        f"{record['subsidy_rate']*100:.1f}%,{record['platform']}\n"
                    )
            
            return True
        except Exception as e:
            print(f"导出CSV失败: {e}")
            return False


def main():
    """主函数"""
    print("=== 投影仪价格历史追踪器测试 ===")
    print()
    
    tracker = ProjectorPriceHistory()
    
    print("添加测试价格记录...")
    tracker.add_price_record(
        projector_id=1,
        original_price=4999,
        subsidy_price=3990,
        subsidy_amount=1009,
        subsidy_rate=0.20,
        platform='京东'
    )
    
    tracker.add_price_record(
        projector_id=3,
        original_price=2699,
        subsidy_price=2150,
        subsidy_amount=549,
        subsidy_rate=0.20,
        platform='天猫'
    )
    
    print("✅ 价格记录已添加")
    print()
    
    print("价格趋势分析:")
    trend = tracker.get_price_trend(1, days=30)
    
    if trend:
        print(f"投影仪ID: 1")
        print(f"记录数量: {trend['record_count']}")
        print(f"原价变化: ¥{trend['original_price_change']} ({trend['original_price_change_rate']:.1f}%)")
        print(f"国补价变化: ¥{trend['subsidy_price_change']} ({trend['subsidy_price_change_rate']:.1f}%)")
        print(f"最早价格: ¥{trend['earliest_price']}")
        print(f"最新价格: ¥{trend['latest_price']}")
    
    print()
    
    print("最低价格:")
    lowest = tracker.get_lowest_price(1, days=30)
    
    if lowest:
        print(f"最低原价: ¥{lowest['original_price']}")
        print(f"最低国补价: ¥{lowest['subsidy_price']}")
        print(f"记录时间: {lowest['timestamp']}")
        print(f"平台: {lowest['platform']}")
    
    print()
    
    print("平均价格:")
    average = tracker.get_average_price(1, days=30)
    
    if average:
        print(f"平均原价: ¥{average['average_original_price']:.2f}")
        print(f"平均国补价: ¥{average['average_subsidy_price']:.2f}")
        print(f"记录数量: {average['record_count']}")


if __name__ == '__main__':
    main()