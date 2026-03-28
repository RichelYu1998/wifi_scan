#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的品牌搜索功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from integrated_system import ProjectorRecommender

def test_brand_search():
    """测试品牌搜索功能"""
    print("=== 测试品牌搜索功能 ===")
    recommender = ProjectorRecommender()
    
    # 测试所有可用品牌
    all_brands = recommender._get_all_available_brands()
    print(f"所有可用品牌 ({len(all_brands)}个):")
    for i, brand in enumerate(all_brands, 1):
        print(f"{i}. {brand}")
    
    # 测试不存在的品牌
    print("\n=== 测试不存在的品牌 ===")
    test_brands = ['爱奇艺', '腾讯', '百度', '阿里巴巴', '华为']
    
    for brand in test_brands:
        print(f"\n搜索品牌: {brand}")
        
        # 本地数据库搜索
        local_recommendations = []
        for projector in recommender.projectors:
            if brand.lower() in projector['品牌'].lower():
                local_recommendations.append(projector)
        
        # 模拟联网搜索
        online_recommendations = []
        
        if not local_recommendations and not online_recommendations:
            print(f"未找到{brand}品牌的投影仪")
            print("可选的品牌有:")
            all_brands = recommender._get_all_available_brands()
            for b in all_brands:
                print(f"- {b}")

def main():
    """主测试函数"""
    print("品牌搜索功能测试")
    print("=" * 50)
    
    test_brand_search()
    
    print("\n测试完成！")

if __name__ == '__main__':
    main()