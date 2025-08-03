"""
测试真实LLM智能体调用功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app_enhanced import EnhancedTradingAgentsApp

async def test_real_llm_analysis():
    """测试真实LLM分析功能"""
    print("🧪 测试真实LLM智能体协作分析")
    print("="*60)
    
    # 创建应用实例
    app = EnhancedTradingAgentsApp()
    
    print(f"📊 系统状态:")
    print(f"  - LLM配置数量: {len(app.llm_config)}")
    print(f"  - 自定义提供商: {len(app.custom_llm_providers)}")
    print(f"  - ChromaDB状态: {'✅ 可用' if app.chromadb_available else '❌ 不可用'}")
    print(f"  - 智能体配置: {len(app.agent_model_config)}")
    print()
    
    # 检查是否有可用的LLM配置
    if not app.llm_config:
        print("❌ 没有配置LLM提供商，无法进行真实测试")
        print("💡 请先在界面中配置至少一个LLM提供商的API密钥")
        return False
    
    print(f"✅ 发现 {len(app.llm_config)} 个已配置的LLM提供商:")
    for provider in app.llm_config.keys():
        print(f"  - {provider}")
    print()
    
    # 测试股票代码
    test_symbol = "600519"
    test_depth = "中等分析"
    test_analysts = ["market_analyst", "sentiment_analyst"]
    
    print(f"🎯 开始测试分析:")
    print(f"  - 股票代码: {test_symbol}")
    print(f"  - 分析深度: {test_depth}")
    print(f"  - 参与智能体: {test_analysts}")
    print(f"  - 使用真实LLM: ✅")
    print()
    
    try:
        # 执行真实LLM分析
        print("🚀 启动真实智能体分析...")
        result = await app.analyze_stock_enhanced(
            symbol=test_symbol,
            depth=test_depth,
            analysts=test_analysts,
            use_real_llm=True
        )
        
        print("📊 分析结果:")
        print(f"  - 状态: {result.get('status', '未知')}")
        print(f"  - LLM类型: {result.get('llm_used', '未知')}")
        
        if result.get("status") == "completed":
            print("✅ 分析成功完成！")
            
            # 显示分析阶段
            stages = result.get("analysis_stages", {})
            print(f"\n📋 分析阶段结果:")
            for stage_name, stage_data in stages.items():
                print(f"  - {stage_name}: {'✅ 完成' if stage_data and not stage_data.get('error') else '❌ 失败'}")
            
            # 显示智能体结果
            analyst_team = stages.get("analyst_team", {})
            if analyst_team:
                print(f"\n👥 分析师团队结果:")
                for agent_id, agent_result in analyst_team.items():
                    if agent_result and not agent_result.get('error'):
                        analysis = agent_result.get('analysis', '')
                        print(f"  - {agent_id}: {analysis[:100]}...")
                    else:
                        error = agent_result.get('error', '未知错误')
                        print(f"  - {agent_id}: ❌ {error}")
            
            # 显示最终决策
            final_decision = stages.get("final_decision", {})
            if final_decision:
                decision = final_decision.get("decision", "HOLD")
                reasoning = final_decision.get("reasoning", "")
                print(f"\n🎯 最终决策:")
                print(f"  - 决策: {decision}")
                print(f"  - 理由: {reasoning[:150]}...")
            
            return True
            
        else:
            error = result.get("error", "未知错误")
            print(f"❌ 分析失败: {error}")
            return False
            
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_communication_logs():
    """测试通信日志功能"""
    print("\n" + "="*60)
    print("📡 测试通信日志功能")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    # 检查通信日志
    logs = app.get_communication_logs(10)
    print(f"📋 当前通信日志数量: {len(logs)}")
    
    if logs:
        print(f"\n📝 最近的通信记录:")
        for i, log in enumerate(logs[-3:], 1):  # 显示最近3条
            print(f"  {i}. {log['timestamp'][:19]} | {log['agent_id']} -> {log['provider']}:{log['model']}")
            print(f"     状态: {log['status']} | 提示长度: {log['prompt_length']} | 响应长度: {log['response_length']}")
    else:
        print("📝 暂无通信日志记录")
    
    return len(logs) > 0

async def test_agent_model_config():
    """测试智能体模型配置"""
    print("\n" + "="*60)
    print("🤖 测试智能体模型配置")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    # 显示当前配置
    print(f"⚙️ 当前智能体模型配置:")
    agents = app.get_agent_list()
    for agent in agents[:5]:  # 显示前5个
        agent_id = agent["id"]
        model_config = app.agent_model_config.get(agent_id, "未配置")
        print(f"  - {agent['name']}: {model_config}")
    
    print(f"  ... 共 {len(app.agent_model_config)} 个智能体已配置")
    
    # 测试模型推荐
    print(f"\n💡 测试模型推荐功能:")
    test_providers = ["claude", "通义千问", "文心一言"]
    for provider in test_providers:
        models = app.get_common_models_for_provider(provider)
        print(f"  - {provider}: {models[:3]}...")  # 显示前3个推荐模型
    
    return True

async def main():
    """主测试函数"""
    print("🎯 TradingAgents 真实LLM智能体功能测试")
    print("="*80)
    
    # 测试1: 智能体模型配置
    config_test = await test_agent_model_config()
    
    # 测试2: 真实LLM分析
    analysis_test = await test_real_llm_analysis()
    
    # 测试3: 通信日志
    logs_test = await test_communication_logs()
    
    # 总结
    print("\n" + "="*80)
    print("📊 测试结果总结")
    print("="*80)
    print(f"智能体配置测试: {'✅ 通过' if config_test else '❌ 失败'}")
    print(f"真实LLM分析测试: {'✅ 通过' if analysis_test else '❌ 失败'}")
    print(f"通信日志测试: {'✅ 通过' if logs_test else '❌ 失败'}")
    
    if analysis_test:
        print("\n🎉 恭喜！真实LLM智能体功能正常工作！")
        print("\n💡 使用建议:")
        print("1. 在界面中勾选 '🤖 使用真实LLM智能体协作'")
        print("2. 确保已配置相应的LLM提供商API密钥")
        print("3. 在 '📡 通信监控' 页面查看实时通信过程")
        print("4. 在 '🤖 智能体配置' 页面调整模型配置")
    else:
        print("\n❌ 真实LLM功能测试失败")
        print("\n🔧 排查建议:")
        print("1. 检查LLM提供商API密钥是否正确配置")
        print("2. 确认网络连接正常")
        print("3. 查看错误日志了解具体问题")
        print("4. 可以先使用模拟模式测试基本功能")

if __name__ == "__main__":
    asyncio.run(main())
