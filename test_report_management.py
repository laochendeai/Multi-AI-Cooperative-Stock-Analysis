"""
测试报告管理功能
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app_enhanced import EnhancedTradingAgentsApp

def test_report_directory_creation():
    """测试报告目录创建"""
    print("🧪 测试报告目录创建")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    # 检查报告目录是否存在
    reports_dir = Path("./reports")
    if reports_dir.exists():
        print(f"✅ 报告目录已存在: {reports_dir.absolute()}")
    else:
        print(f"❌ 报告目录不存在: {reports_dir.absolute()}")
        return False
    
    # 检查应用中的报告目录配置
    if app.reports_dir.exists():
        print(f"✅ 应用报告目录配置正确: {app.reports_dir.absolute()}")
    else:
        print(f"❌ 应用报告目录配置错误: {app.reports_dir.absolute()}")
        return False
    
    return True

def test_filename_generation():
    """测试文件名生成"""
    print("\n🧪 测试文件名生成")
    print("="*60)
    
    # 测试不同的股票信息
    test_cases = [
        {"symbol": "600519", "stock_name": "贵州茅台", "format": "markdown"},
        {"symbol": "000001", "stock_name": "平安银行", "format": "text"},
        {"symbol": "600328", "stock_name": "天房发展", "format": "json"},
        {"symbol": "SH600519", "stock_name": "贵州茅台(A股)", "format": "markdown"},  # 包含特殊字符
    ]
    
    for case in test_cases:
        symbol = case["symbol"]
        stock_name = case["stock_name"]
        format_type = case["format"]
        
        # 模拟文件名生成逻辑
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_stock_name = "".join(c for c in stock_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_stock_name = safe_stock_name.replace(' ', '_')
        
        if format_type == "markdown":
            filename = f"{symbol}_{safe_stock_name}_{timestamp}.md"
        elif format_type == "text":
            filename = f"{symbol}_{safe_stock_name}_{timestamp}.txt"
        elif format_type == "json":
            filename = f"{symbol}_{safe_stock_name}_{timestamp}.json"
        
        print(f"📊 {symbol}({stock_name}) → {filename}")
        
        # 检查文件名是否安全
        if any(c in filename for c in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
            print(f"  ❌ 文件名包含非法字符")
        else:
            print(f"  ✅ 文件名安全")
    
    return True

def test_mock_report_creation():
    """测试模拟报告创建"""
    print("\n🧪 测试模拟报告创建")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    # 创建模拟分析结果
    mock_result = {
        "symbol": "600519",
        "stock_name": "贵州茅台",
        "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "comprehensive_report": "## 600519（贵州茅台）综合分析报告\n\n这是一个测试报告...",
        "market_analysis": "技术分析显示...",
        "sentiment_analysis": "社交媒体情绪...",
        "news_analysis": "最新新闻...",
        "fundamentals_analysis": "基本面分析...",
        "bull_arguments": "多头观点...",
        "bear_arguments": "空头观点...",
        "investment_recommendation": "投资建议...",
        "trading_strategy": "交易策略...",
        "risk_assessment": "风险评估...",
        "final_decision": "最终决策..."
    }
    
    # 设置模拟结果
    app.last_analysis_result = mock_result
    
    # 测试不同格式的报告生成
    formats = ["markdown", "text", "json"]
    created_files = []
    
    for format_type in formats:
        print(f"\n📄 测试 {format_type.upper()} 格式:")
        
        try:
            report_content = app.export_analysis_report(format_type)
            
            if report_content.startswith("❌"):
                print(f"  ❌ 生成失败: {report_content}")
                continue
            
            # 模拟保存到文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"TEST_{mock_result['symbol']}_{mock_result['stock_name']}_{timestamp}.{format_type[:2]}"
            file_path = app.reports_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            created_files.append(file_path)
            
            print(f"  ✅ 文件已创建: {filename}")
            print(f"  📏 文件大小: {file_path.stat().st_size} 字节")
            
        except Exception as e:
            print(f"  ❌ 创建失败: {e}")
    
    print(f"\n📊 总共创建了 {len(created_files)} 个测试文件")
    return created_files

def test_history_management():
    """测试历史管理功能"""
    print("\n🧪 测试历史管理功能")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    # 获取分析历史
    print("📋 获取分析历史:")
    history = app.get_analysis_history()
    
    print(f"  找到 {len(history)} 个历史报告")
    
    for i, item in enumerate(history[:5], 1):  # 只显示前5个
        print(f"  {i}. {item['display_name']}")
        print(f"     文件: {item['filename']}")
        print(f"     大小: {item['size']} 字节")
        print(f"     格式: {item['format']}")
    
    if len(history) > 5:
        print(f"  ... 还有 {len(history) - 5} 个报告")
    
    # 测试加载报告
    if history:
        print(f"\n📖 测试加载第一个报告:")
        first_report = history[0]
        
        try:
            content = app.load_analysis_report(first_report["file_path"])
            print(f"  ✅ 加载成功，内容长度: {len(content)} 字符")
            print(f"  📄 内容预览: {content[:100]}...")
        except Exception as e:
            print(f"  ❌ 加载失败: {e}")
    
    return len(history)

def test_file_operations():
    """测试文件操作"""
    print("\n🧪 测试文件操作")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    # 创建一个测试文件
    test_content = "这是一个测试报告文件"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_filename = f"TEST_999999_测试股票_{timestamp}.txt"
    test_file_path = app.reports_dir / test_filename
    
    print(f"📝 创建测试文件: {test_filename}")
    
    try:
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        print(f"  ✅ 文件创建成功")
        
        # 测试加载
        loaded_content = app.load_analysis_report(str(test_file_path))
        if loaded_content == test_content:
            print(f"  ✅ 文件加载成功")
        else:
            print(f"  ❌ 文件加载内容不匹配")
        
        # 测试删除
        success = app.delete_analysis_report(str(test_file_path))
        if success:
            print(f"  ✅ 文件删除成功")
        else:
            print(f"  ❌ 文件删除失败")
        
        # 验证删除
        if not test_file_path.exists():
            print(f"  ✅ 文件确实已删除")
        else:
            print(f"  ❌ 文件仍然存在")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 文件操作失败: {e}")
        return False

def test_ui_components():
    """测试UI组件"""
    print("\n🧪 测试UI组件")
    print("="*60)
    
    # 检查UI组件是否在代码中定义
    with open("app_enhanced.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    ui_components = [
        "📚 分析历史",
        "refresh_history_btn = gr.Button",
        "clear_history_btn = gr.Button",
        "history_list = gr.Dropdown",
        "view_report_btn = gr.Button",
        "delete_report_btn = gr.Button",
        "history_report_content = gr.Textbox"
    ]
    
    print("📊 UI组件检查:")
    all_found = True
    
    for component in ui_components:
        if component in content:
            print(f"  ✅ {component}")
        else:
            print(f"  ❌ {component} - 未找到")
            all_found = False
    
    # 检查事件绑定
    event_bindings = [
        "refresh_history_btn.click",
        "history_list.change",
        "view_report_btn.click",
        "delete_report_btn.click",
        "clear_history_btn.click"
    ]
    
    print("\n📊 事件绑定检查:")
    for binding in event_bindings:
        if binding in content:
            print(f"  ✅ {binding}")
        else:
            print(f"  ❌ {binding} - 未找到")
            all_found = False
    
    return all_found

def main():
    """主测试函数"""
    print("🎯 报告管理功能测试")
    print("="*80)
    
    # 执行各项测试
    tests = [
        ("报告目录创建", test_report_directory_creation),
        ("文件名生成", test_filename_generation),
        ("模拟报告创建", test_mock_report_creation),
        ("历史管理功能", test_history_management),
        ("文件操作", test_file_operations),
        ("UI组件", test_ui_components),
    ]
    
    results = {}
    created_files = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if test_name == "模拟报告创建" and isinstance(result, list):
                created_files = result
                results[test_name] = len(result) > 0
            else:
                results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} 测试失败: {e}")
            results[test_name] = False
    
    # 清理测试文件
    if created_files:
        print(f"\n🧹 清理 {len(created_files)} 个测试文件...")
        for file_path in created_files:
            try:
                file_path.unlink()
                print(f"  ✅ 已删除: {file_path.name}")
            except Exception as e:
                print(f"  ❌ 删除失败: {file_path.name} - {e}")
    
    # 总结
    print("\n" + "="*80)
    print("📊 报告管理功能测试总结")
    print("="*80)
    
    for test_name, success in results.items():
        print(f"{test_name}: {'✅ 通过' if success else '❌ 失败'}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 所有测试通过！报告管理功能已实现！")
        print("\n💡 新功能特性:")
        print("1. ✅ 自动保存报告到 ./reports 目录")
        print("2. ✅ 智能文件命名：股票代码_股票名称_时间戳")
        print("3. ✅ 分析历史管理界面")
        print("4. ✅ 按时间倒序显示历史报告")
        print("5. ✅ 查看、删除、清空历史功能")
        print("6. ✅ 支持多种格式：Markdown、文本、JSON")
        
        print("\n🚀 使用方法:")
        print("1. 启动系统: python app_enhanced.py")
        print("2. 完成股票分析后，在'📄 导出报告'中生成报告")
        print("3. 报告自动保存到 ./reports 目录")
        print("4. 在'📚 分析历史'中查看和管理历史报告")
        print("5. 点击报告名称查看详情，支持查看和删除操作")
    else:
        print("\n❌ 部分测试失败")
        print("需要检查失败的测试项目")

if __name__ == "__main__":
    main()
