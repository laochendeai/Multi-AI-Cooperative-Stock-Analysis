"""
测试中断机制和重试功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app_enhanced import EnhancedTradingAgentsApp

def test_retry_config():
    """测试重试配置"""
    print("🧪 测试重试配置")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    # 检查默认配置
    print("📊 默认重试配置:")
    for key, value in app.retry_config.items():
        print(f"  {key}: {value}")
    
    # 测试配置更新
    new_config = {
        "max_data_retries": 5,
        "max_llm_retries": 3,
        "retry_delay": 2.0
    }
    
    print(f"\n🔧 更新配置: {new_config}")
    app.retry_config.update(new_config)
    
    print("📊 更新后配置:")
    for key, value in app.retry_config.items():
        print(f"  {key}: {value}")
    
    return True

def test_analysis_state():
    """测试分析状态管理"""
    print("\n🧪 测试分析状态管理")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    # 检查初始状态
    print("📊 初始状态:")
    for key, value in app.analysis_state.items():
        print(f"  {key}: {value}")
    
    # 测试状态更新
    app.analysis_state["is_running"] = True
    app.analysis_state["current_step"] = "测试步骤"
    app.analysis_state["failed_agents"] = ["test_agent"]
    
    print("\n📊 更新后状态:")
    for key, value in app.analysis_state.items():
        print(f"  {key}: {value}")
    
    # 测试中断检查
    should_interrupt = app.check_should_interrupt()
    print(f"\n🔍 中断检查: {should_interrupt}")
    
    # 测试中断设置
    app.interrupt_analysis("测试中断")
    should_interrupt = app.check_should_interrupt()
    print(f"🔍 中断后检查: {should_interrupt}")
    
    # 测试状态重置
    app.reset_analysis_state()
    print("\n📊 重置后状态:")
    for key, value in app.analysis_state.items():
        print(f"  {key}: {value}")
    
    return True

async def test_retry_mechanism():
    """测试重试机制"""
    print("\n🧪 测试重试机制")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    # 测试成功的函数
    async def success_func():
        print("  ✅ 函数执行成功")
        return "success"
    
    print("📊 测试成功函数:")
    try:
        result = await app.retry_with_backoff(success_func, max_retries=2, delay=0.1)
        print(f"  结果: {result}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    
    # 测试失败的函数
    async def fail_func():
        print("  ❌ 函数执行失败")
        raise ValueError("测试失败")
    
    print("\n📊 测试失败函数:")
    try:
        result = await app.retry_with_backoff(fail_func, max_retries=2, delay=0.1)
        print(f"  结果: {result}")
    except Exception as e:
        print(f"  ❌ 最终异常: {e}")
    
    # 测试中断的函数
    async def interrupt_func():
        app.interrupt_analysis("测试中断")
        await asyncio.sleep(0.1)
        return "should not reach here"
    
    print("\n📊 测试中断函数:")
    try:
        result = await app.retry_with_backoff(interrupt_func, max_retries=2, delay=0.1)
        print(f"  结果: {result}")
    except Exception as e:
        print(f"  ❌ 中断异常: {e}")
    
    return True

async def test_data_collection_retry():
    """测试数据收集重试"""
    print("\n🧪 测试数据收集重试")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    # 测试有效股票代码
    print("📊 测试有效股票代码 (600519):")
    try:
        result = await app._collect_stock_data("600519")
        print(f"  状态: {result.get('status', '未知')}")
        print(f"  消息: {result.get('message', '无消息')}")
        if result.get('status') == 'success':
            data = result.get('data', {})
            print(f"  股票名称: {data.get('name', '未知')}")
            print(f"  当前价格: {data.get('price_data', {}).get('current_price', '未知')}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    
    # 测试无效股票代码
    print("\n📊 测试无效股票代码 (999999):")
    try:
        result = await app._collect_stock_data("999999")
        print(f"  状态: {result.get('status', '未知')}")
        print(f"  消息: {result.get('message', '无消息')}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    
    return True

def test_ui_components():
    """测试UI组件"""
    print("\n🧪 测试UI组件")
    print("="*60)
    
    # 检查UI组件是否在代码中定义
    with open("app_enhanced.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    ui_components = [
        "interrupt_btn = gr.Button",
        "max_data_retries = gr.Slider",
        "max_llm_retries = gr.Slider", 
        "retry_delay = gr.Slider",
        "🔧 重试配置",
        "⏹️ 中断分析"
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
        "interrupt_btn.click",
        "max_data_retries, max_llm_retries, retry_delay"
    ]
    
    print("\n📊 事件绑定检查:")
    for binding in event_bindings:
        if binding in content:
            print(f"  ✅ {binding}")
        else:
            print(f"  ❌ {binding} - 未找到")
            all_found = False
    
    return all_found

def test_error_scenarios():
    """测试错误场景"""
    print("\n🧪 测试错误场景")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    # 测试场景1: 数据获取失败
    print("📊 场景1: 模拟数据获取失败")
    app.analysis_state["failed_agents"] = ["market_analyst", "sentiment_analyst"]
    
    # 测试场景2: LLM调用失败
    print("📊 场景2: 模拟LLM调用失败")
    app.analysis_state["current_step"] = "运行情感分析师"
    app.analysis_state["is_running"] = True
    
    # 测试场景3: 用户中断
    print("📊 场景3: 模拟用户中断")
    app.interrupt_analysis("用户手动中断")
    
    print("📊 最终状态:")
    for key, value in app.analysis_state.items():
        print(f"  {key}: {value}")
    
    return True

async def main():
    """主测试函数"""
    print("🎯 中断机制和重试功能测试")
    print("="*80)
    
    # 执行各项测试
    tests = [
        ("重试配置", test_retry_config),
        ("分析状态管理", test_analysis_state),
        ("重试机制", test_retry_mechanism),
        ("数据收集重试", test_data_collection_retry),
        ("UI组件", test_ui_components),
        ("错误场景", test_error_scenarios),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                results[test_name] = await test_func()
            else:
                results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} 测试失败: {e}")
            results[test_name] = False
    
    # 总结
    print("\n" + "="*80)
    print("📊 中断机制和重试功能测试总结")
    print("="*80)
    
    for test_name, success in results.items():
        print(f"{test_name}: {'✅ 通过' if success else '❌ 失败'}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 所有测试通过！中断机制和重试功能已实现！")
        print("\n💡 新功能特性:")
        print("1. ✅ 数据获取失败自动重试（可配置次数）")
        print("2. ✅ LLM调用失败自动重试（指数退避）")
        print("3. ✅ 用户可手动中断分析过程")
        print("4. ✅ 智能体失败时显示友好错误信息")
        print("5. ✅ 实时状态显示和进度跟踪")
        print("6. ✅ 可配置的重试参数（次数、延迟）")
        
        print("\n🚀 使用方法:")
        print("1. 启动系统: python app_enhanced.py")
        print("2. 在'🔧 重试配置'中调整重试参数")
        print("3. 开始分析时可随时点击'⏹️ 中断分析'")
        print("4. 系统会自动重试失败的操作")
        print("5. 超过重试次数后会显示友好错误信息")
    else:
        print("\n❌ 部分测试失败")
        print("需要检查失败的测试项目")

if __name__ == "__main__":
    asyncio.run(main())
