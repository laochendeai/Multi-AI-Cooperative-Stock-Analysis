"""
测试600330股票名称获取
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app_enhanced import EnhancedTradingAgentsApp

def test_600330_name():
    """测试600330股票名称获取"""
    print("🧪 测试600330股票名称获取")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    data_collector = app.data_collector
    
    # 测试不同情况的股票名称获取
    test_cases = [
        # (symbol, raw_name, expected_name)
        ("600330", "恒顺醋业", "恒顺醋业"),  # 正常情况
        ("600330", "", "恒顺醋业"),  # 空名称，使用映射
        ("600330", None, "恒顺醋业"),  # None名称，使用映射
        ("600330", "600330", "恒顺醋业"),  # 名称等于代码，使用映射
        ("600330", "股票600330", "恒顺醋业"),  # 错误格式，使用映射
    ]
    
    print("📊 600330股票名称获取测试:")
    all_passed = True
    
    for symbol, raw_name, expected in test_cases:
        result = data_collector.get_stock_name(symbol, raw_name)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {symbol} + '{raw_name}' → '{result}' (期望: '{expected}')")
        if result != expected:
            all_passed = False
    
    # 检查映射表
    print(f"\n📋 映射表中600330: {data_collector.stock_name_mapping.get('600330', '未找到')}")
    
    # 测试提示生成
    print(f"\n📝 提示生成测试:")
    stock_name = data_collector.get_stock_name("600330", "")
    prompt_sample = f"请分析股票600330（{stock_name}）的技术指标和价格走势。"
    print(f"  生成的提示: {prompt_sample}")
    
    if "股票600330（股票600330）" in prompt_sample:
        print(f"  ❌ 仍有格式问题")
        all_passed = False
    else:
        print(f"  ✅ 格式正常")
    
    return all_passed

def test_mapping_table():
    """测试映射表完整性"""
    print("\n🧪 测试映射表完整性")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    data_collector = app.data_collector
    
    print("📋 完整的股票名称映射表:")
    for symbol, name in sorted(data_collector.stock_name_mapping.items()):
        print(f"  {symbol} → {name}")
    
    print(f"\n📊 映射表包含 {len(data_collector.stock_name_mapping)} 个股票")
    
    # 检查是否有重复的键
    symbols = list(data_collector.stock_name_mapping.keys())
    unique_symbols = set(symbols)
    
    if len(symbols) != len(unique_symbols):
        print("⚠️ 映射表中有重复的股票代码")
        duplicates = [s for s in symbols if symbols.count(s) > 1]
        print(f"  重复的代码: {set(duplicates)}")
        return False
    else:
        print("✅ 映射表中没有重复的股票代码")
    
    return True

def test_edge_cases():
    """测试边界情况"""
    print("\n🧪 测试边界情况")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    data_collector = app.data_collector
    
    # 边界情况测试
    edge_cases = [
        ("600330", "  ", "恒顺醋业"),  # 空白名称
        ("600330", "   恒顺醋业   ", "恒顺醋业"),  # 带空格的名称
        ("SH600330", "恒顺醋业", "恒顺醋业"),  # 带前缀的代码（不在映射表中）
        ("999999", "", "999999"),  # 未知股票
    ]
    
    print("🔍 边界情况测试:")
    all_passed = True
    
    for symbol, raw_name, expected in edge_cases:
        try:
            result = data_collector.get_stock_name(symbol, raw_name)
            print(f"  📊 '{symbol}' + '{raw_name}' → '{result}'")
            
            if expected and result != expected:
                print(f"    ⚠️ 期望: '{expected}'")
                all_passed = False
            else:
                print(f"    ✅ 结果正确")
        except Exception as e:
            print(f"  ❌ 异常: {e}")
            all_passed = False
    
    return all_passed

def main():
    """主测试函数"""
    print("🎯 600330股票名称修复测试")
    print("="*80)
    
    # 执行各项测试
    tests = [
        ("600330名称获取", test_600330_name),
        ("映射表完整性", test_mapping_table),
        ("边界情况", test_edge_cases),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} 测试失败: {e}")
            results[test_name] = False
    
    # 总结
    print("\n" + "="*80)
    print("📊 600330股票名称修复测试总结")
    print("="*80)
    
    for test_name, success in results.items():
        print(f"{test_name}: {'✅ 通过' if success else '❌ 失败'}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 600330股票名称问题已修复！")
        print("\n💡 修复内容:")
        print("1. ✅ 添加了600330 → 恒顺醋业的映射")
        print("2. ✅ 股票名称获取逻辑正常工作")
        print("3. ✅ 提示格式不再出现'股票600330（股票600330）'")
        print("4. ✅ 边界情况处理正常")
        
        print("\n🚀 现在可以:")
        print("1. 重启主程序: python app_enhanced.py")
        print("2. 分析600330股票，应该显示'恒顺醋业'")
        print("3. 所有分析结果都会使用正确的股票名称")
    else:
        print("\n❌ 部分测试失败")
        print("需要检查失败的测试项目")

if __name__ == "__main__":
    main()
