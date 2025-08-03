"""
最终验证600330股票名称修复
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app_enhanced import EnhancedTradingAgentsApp

def test_complete_600330_fix():
    """完整测试600330修复"""
    print("🎯 完整验证600330股票名称修复")
    print("="*80)
    
    app = EnhancedTradingAgentsApp()
    
    # 测试各种情况的股票名称获取
    test_scenarios = [
        {"raw_name": "", "description": "空名称"},
        {"raw_name": None, "description": "None名称"},
        {"raw_name": "600330", "description": "代码作为名称"},
        {"raw_name": "股票600330", "description": "错误格式"},
        {"raw_name": "未知", "description": "未知名称"},
        {"raw_name": "UNKNOWN", "description": "UNKNOWN名称"},
        {"raw_name": "恒顺醋业", "description": "正确名称"},
    ]
    
    print("📊 600330股票名称获取测试:")
    all_passed = True
    
    for scenario in test_scenarios:
        raw_name = scenario["raw_name"]
        description = scenario["description"]
        
        result = app.data_collector.get_stock_name("600330", raw_name)
        expected = "恒顺醋业"
        
        if result == expected:
            print(f"  ✅ {description}: '{raw_name}' → '{result}'")
        else:
            print(f"  ❌ {description}: '{raw_name}' → '{result}' (期望: '{expected}')")
            all_passed = False
    
    # 测试分析结果中的股票名称处理
    print(f"\n📊 分析结果股票名称处理测试:")
    
    # 模拟分析结果
    mock_results = {
        "results": {
            "data_collection": {
                "name": "未知",  # 模拟问题情况
                "symbol": "600330"
            }
        }
    }
    
    # 使用修复后的逻辑
    stock_data = mock_results.get("results", {}).get("data_collection", {})
    raw_name = stock_data.get("name", "") if isinstance(stock_data, dict) else ""
    stock_name = app.data_collector.get_stock_name("600330", raw_name)
    
    print(f"  原始数据: {stock_data}")
    print(f"  提取的原始名称: '{raw_name}'")
    print(f"  处理后的股票名称: '{stock_name}'")
    
    if stock_name == "恒顺醋业":
        print(f"  ✅ 分析结果股票名称处理正确")
    else:
        print(f"  ❌ 分析结果股票名称处理错误")
        all_passed = False
    
    # 测试导出文件名生成
    print(f"\n📊 导出文件名生成测试:")
    
    # 模拟last_analysis_result
    app.last_analysis_result = {
        "symbol": "600330",
        "stock_name": "未知",  # 模拟问题情况
        "analysis_time": "2025-08-03 21:00:00"
    }
    
    # 使用修复后的逻辑
    symbol = app.last_analysis_result.get('symbol', 'UNKNOWN')
    raw_stock_name = app.last_analysis_result.get('stock_name', '')
    stock_name = app.data_collector.get_stock_name(symbol, raw_stock_name)
    
    # 生成安全文件名
    safe_stock_name = "".join(c for c in stock_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_stock_name = safe_stock_name.replace(' ', '_')
    
    filename = f"{symbol}_{safe_stock_name}_20250803_210000.md"
    
    print(f"  原始分析结果股票名称: '{raw_stock_name}'")
    print(f"  处理后股票名称: '{stock_name}'")
    print(f"  安全文件名: '{safe_stock_name}'")
    print(f"  生成的文件名: {filename}")
    
    if "恒顺醋业" in filename and "未知" not in filename:
        print(f"  ✅ 导出文件名生成正确")
    else:
        print(f"  ❌ 导出文件名仍有问题")
        all_passed = False
    
    # 测试映射表
    print(f"\n📊 映射表验证:")
    mapping = app.data_collector.stock_name_mapping
    
    if "600330" in mapping:
        mapped_name = mapping["600330"]
        print(f"  ✅ 600330在映射表中: {mapped_name}")
        
        if mapped_name == "恒顺醋业":
            print(f"  ✅ 映射名称正确")
        else:
            print(f"  ❌ 映射名称错误: {mapped_name}")
            all_passed = False
    else:
        print(f"  ❌ 600330不在映射表中")
        all_passed = False
    
    # 总结
    print(f"\n" + "="*80)
    print("📊 600330股票名称修复验证总结")
    print("="*80)
    
    if all_passed:
        print("🎉 所有测试通过！600330股票名称问题已完全修复！")
        print("\n💡 修复效果:")
        print("1. ✅ 股票名称获取：所有无效格式都能正确回退到'恒顺醋业'")
        print("2. ✅ 分析结果处理：即使原始数据是'未知'，也能显示正确名称")
        print("3. ✅ 导出文件名：文件名将是'600330_恒顺醋业_时间戳.md'")
        print("4. ✅ 映射表完整：600330 → 恒顺醋业映射正确")
        
        print("\n🚀 现在的效果:")
        print("• 分析界面显示：股票600330（恒顺醋业）")
        print("• 报告文件名：600330_恒顺醋业_20250803_210000.md")
        print("• 不再出现：600330_未知_20250803_210000.md")
        
        return True
    else:
        print("❌ 部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    test_complete_600330_fix()
