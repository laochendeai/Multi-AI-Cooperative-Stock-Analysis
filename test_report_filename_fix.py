"""
测试报告文件名修复
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app_enhanced import EnhancedTradingAgentsApp

def test_stock_name_in_analysis_result():
    """测试分析结果中的股票名称保存"""
    print("🧪 测试分析结果中的股票名称保存")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    # 模拟分析结果
    mock_results = {
        "results": {
            "data_collection": {
                "name": "",  # 模拟空名称
                "symbol": "600330"
            },
            "sentiment_analysis": "股票600330（恒顺醋业）情绪分析...",
            "news_analysis": "股票600330（恒顺醋业）新闻分析...",
        }
    }
    
    symbol = "600330"
    
    # 测试股票名称获取逻辑
    stock_data = mock_results.get("results", {}).get("data_collection", {})
    raw_name = stock_data.get("name", "") if isinstance(stock_data, dict) else ""
    stock_name = app.data_collector.get_stock_name(symbol, raw_name)
    
    print(f"📊 股票代码: {symbol}")
    print(f"📊 原始名称: '{raw_name}'")
    print(f"📊 处理后名称: '{stock_name}'")
    
    if stock_name == "恒顺醋业":
        print("✅ 股票名称获取正确")
        return True
    else:
        print("❌ 股票名称获取错误")
        return False

def test_export_filename_generation():
    """测试导出文件名生成"""
    print("\n🧪 测试导出文件名生成")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    # 模拟分析结果
    app.last_analysis_result = {
        "symbol": "600330",
        "stock_name": "未知",  # 模拟错误的股票名称
        "analysis_time": "2025-08-03 21:00:00",
        "comprehensive_report": "测试报告内容..."
    }
    
    # 测试文件名生成逻辑
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    symbol = app.last_analysis_result.get('symbol', 'UNKNOWN')
    
    # 使用修复后的逻辑
    raw_stock_name = app.last_analysis_result.get('stock_name', '')
    stock_name = app.data_collector.get_stock_name(symbol, raw_stock_name)
    
    # 清理文件名
    safe_stock_name = "".join(c for c in stock_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_stock_name = safe_stock_name.replace(' ', '_')
    
    filename = f"{symbol}_{safe_stock_name}_{timestamp}.md"
    
    print(f"📊 股票代码: {symbol}")
    print(f"📊 原始名称: '{raw_stock_name}'")
    print(f"📊 处理后名称: '{stock_name}'")
    print(f"📊 安全名称: '{safe_stock_name}'")
    print(f"📊 生成文件名: {filename}")
    
    if "恒顺醋业" in filename and "未知" not in filename:
        print("✅ 文件名生成正确")
        return True
    else:
        print("❌ 文件名仍包含'未知'")
        return False

def test_different_scenarios():
    """测试不同场景的股票名称处理"""
    print("\n🧪 测试不同场景的股票名称处理")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    test_cases = [
        {
            "symbol": "600330",
            "raw_name": "",
            "expected": "恒顺醋业",
            "description": "空名称"
        },
        {
            "symbol": "600330", 
            "raw_name": "未知",
            "expected": "恒顺醋业",
            "description": "未知名称"
        },
        {
            "symbol": "600330",
            "raw_name": "600330",
            "expected": "恒顺醋业", 
            "description": "代码作为名称"
        },
        {
            "symbol": "600330",
            "raw_name": "股票600330",
            "expected": "恒顺醋业",
            "description": "错误格式"
        },
        {
            "symbol": "600519",
            "raw_name": "贵州茅台",
            "expected": "贵州茅台",
            "description": "正确名称"
        }
    ]
    
    all_passed = True
    
    for case in test_cases:
        symbol = case["symbol"]
        raw_name = case["raw_name"]
        expected = case["expected"]
        description = case["description"]
        
        result = app.data_collector.get_stock_name(symbol, raw_name)
        status = "✅" if result == expected else "❌"
        
        print(f"  {status} {description}: {symbol} + '{raw_name}' → '{result}'")
        
        if result != expected:
            all_passed = False
            print(f"    期望: '{expected}'")
    
    return all_passed

def test_mock_export_process():
    """测试模拟导出过程"""
    print("\n🧪 测试模拟导出过程")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    # 模拟完整的分析结果
    app.last_analysis_result = {
        "symbol": "600330",
        "stock_name": "未知",  # 模拟问题情况
        "analysis_time": "2025-08-03 21:00:00",
        "comprehensive_report": "## 600330（恒顺醋业）综合分析报告\n\n这是测试报告...",
        "market_analysis": "技术分析内容...",
        "sentiment_analysis": "情感分析内容...",
        "news_analysis": "新闻分析内容...",
        "fundamentals_analysis": "基本面分析内容...",
        "bull_arguments": "多头观点...",
        "bear_arguments": "空头观点...",
        "investment_recommendation": "投资建议...",
        "trading_strategy": "交易策略...",
        "risk_assessment": "风险评估..."
    }
    
    # 测试报告内容生成
    try:
        report_content = app.export_analysis_report("markdown")
        
        if report_content.startswith("❌"):
            print(f"❌ 报告生成失败: {report_content}")
            return False
        
        print("✅ 报告内容生成成功")
        print(f"📏 内容长度: {len(report_content)} 字符")
        
        # 测试文件名生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        symbol = app.last_analysis_result.get('symbol', 'UNKNOWN')
        raw_stock_name = app.last_analysis_result.get('stock_name', '')
        stock_name = app.data_collector.get_stock_name(symbol, raw_stock_name)
        
        safe_stock_name = "".join(c for c in stock_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_stock_name = safe_stock_name.replace(' ', '_')
        
        filename = f"{symbol}_{safe_stock_name}_{timestamp}.md"
        
        print(f"📄 生成的文件名: {filename}")
        
        if "恒顺醋业" in filename:
            print("✅ 文件名包含正确的股票名称")
            return True
        else:
            print("❌ 文件名不包含正确的股票名称")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        return False

def main():
    """主测试函数"""
    print("🎯 报告文件名修复测试")
    print("="*80)
    
    # 执行各项测试
    tests = [
        ("分析结果股票名称", test_stock_name_in_analysis_result),
        ("导出文件名生成", test_export_filename_generation),
        ("不同场景处理", test_different_scenarios),
        ("模拟导出过程", test_mock_export_process),
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
    print("📊 报告文件名修复测试总结")
    print("="*80)
    
    for test_name, success in results.items():
        print(f"{test_name}: {'✅ 通过' if success else '❌ 失败'}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 报告文件名问题已修复！")
        print("\n💡 修复内容:")
        print("1. ✅ 修复了分析结果中的股票名称获取逻辑")
        print("2. ✅ 修复了导出报告时的文件名生成逻辑")
        print("3. ✅ 统一使用data_collector.get_stock_name()方法")
        print("4. ✅ 处理了各种边界情况和错误格式")
        
        print("\n🚀 现在可以:")
        print("1. 重启主程序: python app_enhanced.py")
        print("2. 分析600330股票并导出报告")
        print("3. 文件名应该是: 600330_恒顺醋业_YYYYMMDD_HHMMSS.md")
        print("4. 不再出现'600330_未知_YYYYMMDD_HHMMSS.md'")
    else:
        print("\n❌ 部分测试失败")
        print("需要检查失败的测试项目")

if __name__ == "__main__":
    main()
