#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的预算范围计算逻辑
"""

def test_budget_range():
    """测试预算范围计算"""
    test_budgets = [50, 100, 500, 1000, 2000, 3000, 5000, 8000, 10000, 15000]
    
    print("=== 测试预算范围计算 ===")
    for budget in test_budgets:
        print(f"\n输入预算: {budget}元")
        
        # 智能预算范围计算
        if budget < 1000:
            # 如果预算过低，使用固定范围
            min_budget = 2000
            max_budget = 8000
            print(f"预算过低，为您推荐2000~8000元价位的投影仪")
        elif budget < 3000:
            # 低预算范围：±1000元
            min_budget = max(2000, budget - 1000)
            max_budget = budget + 1000
            print(f"预算范围: {min_budget} ~ {max_budget}元")
        elif budget < 8000:
            # 中等预算范围：±2000元
            min_budget = budget - 2000
            max_budget = budget + 2000
            print(f"预算范围: {min_budget} ~ {max_budget}元")
        else:
            # 高预算范围：±3000元
            min_budget = budget - 3000
            max_budget = budget + 3000
            print(f"预算范围: {min_budget} ~ {max_budget}元")

def main():
    """主测试函数"""
    print("预算范围计算逻辑测试")
    print("=" * 50)
    
    test_budget_range()
    
    print("\n测试完成！")

if __name__ == '__main__':
    main()