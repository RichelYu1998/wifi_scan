#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投影仪推荐功能测试脚本
测试新添加的品牌搜索功能和预算范围计算
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from integrated_system import ProjectorRecommender

def test_budget_recommendation():
    """测试预算推荐功能"""
    print("=== 测试预算推荐功能 ===")
    recommender = ProjectorRecommender()
    
    # 测试不同预算
    test_budgets = [500, 700, 3000, 5000, 8000]
    
    for budget in test_budgets:
        print(f"\n测试预算: {budget}元")
        min_budget = max(0, int(budget * 0.5))
        max_budget = int(budget * 1.5)
        print(f"预算范围: {min_budget} ~ {max_budget}元")
        
        recommendations = []
        for projector in recommender.projectors:
            if min_budget <= projector['价格'] <= max_budget:
                recommendations.append(projector)
        
        recommendations.sort(key=lambda x: x['价格'])
        
        if recommendations:
            print(f"找到{len(recommendations)}款投影仪:")
            for i, projector in enumerate(recommendations, 1):
                print(f"  {i}. {projector['品牌']} {projector['型号']} - 价格: {projector['价格']}元")
        else:
            print("未找到投影仪，显示最接近的选项:")
            closest = sorted(recommender.projectors, key=lambda x: abs(x['价格'] - budget))[:3]
            for i, projector in enumerate(closest, 1):
                print(f"  {i}. {projector['品牌']} {projector['型号']} - 价格: {projector['价格']}元")

def test_brand_search():
    """测试品牌搜索功能"""
    print("\n=== 测试品牌搜索功能 ===")
    recommender = ProjectorRecommender()
    
    # 测试不同品牌
    test_brands = ['极米', '坚果', '爱普生', '当贝', '峰米', '小米']
    
    for brand in test_brands:
        print(f"\n搜索品牌: {brand}")
        
        recommendations = []
        for projector in recommender.projectors:
            if brand.lower() in projector['品牌'].lower():
                recommendations.append(projector)
        
        if recommendations:
            print(f"找到{len(recommendations)}款{brand}品牌投影仪:")
            for i, projector in enumerate(recommendations, 1):
                print(f"  {i}. {projector['品牌']} {projector['型号']} - 价格: {projector['价格']}元")
        else:
            print(f"未找到{brand}品牌的投影仪")
            print("可选的品牌有:")
            brands = list(set([p['品牌'] for p in recommender.projectors]))
            for b in brands:
                print(f"  - {b}")

def test_projector_database():
    """显示投影仪数据库"""
    print("\n=== 投影仪数据库 ===")
    recommender = ProjectorRecommender()
    
    print("当前数据库中的投影仪:")
    for i, projector in enumerate(recommender.projectors, 1):
        print(f"{i}. {projector['品牌']} {projector['型号']} - 价格: {projector['价格']}元, "
              f"分辨率: {projector['分辨率']}, 亮度: {projector['亮度']}ANSI流明")

def main():
    """主测试函数"""
    print("投影仪推荐功能测试")
    print("=" * 50)
    
    test_projector_database()
    test_budget_recommendation()
    test_brand_search()
    
    print("\n测试完成！")

if __name__ == '__main__':
    main()