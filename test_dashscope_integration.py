"""
测试阿里百炼DashScope联网搜索集成功能
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app_enhanced import EnhancedTradingAgentsApp

async def test_dashscope_basic():
    """测试基础DashScope调用"""
    print("🧪 测试基础DashScope调用")
    print("="*50)
    
    # 检查环境变量
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ 未设置 DASHSCOPE_API_KEY 环境变量")
        print("💡 请设置环境变量: export DASHSCOPE_API_KEY=your_api_key")
        return False
    
    app = EnhancedTradingAgentsApp()
    
    # 测试基础调用
    test_prompt = "请简单介绍一下股票投资的基本概念，控制在100字以内。"
    model = "qwen-turbo"
    agent_id = "market_analyst"  # 不需要联网的智能体
    
    print(f"🔧 测试配置:")
    print(f"  模型: {model}")
    print(f"  智能体: {agent_id}")
    print(f"  提示: {test_prompt[:30]}...")
    
    try:
        response = await app._call_dashscope(api_key, model, test_prompt, agent_id)
        
        print(f"\n📝 响应结果:")
        print(f"  长度: {len(response)} 字符")
        print(f"  内容: {response[:200]}...")
        
        if "❌" in response:
            print("❌ 基础调用失败")
            return False
        else:
            print("✅ 基础调用成功")
            return True
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

async def test_dashscope_internet_search():
    """测试DashScope联网搜索功能"""
    print("\n" + "="*50)
    print("🌐 测试DashScope联网搜索功能")
    print("="*50)
    
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ 未设置 DASHSCOPE_API_KEY 环境变量")
        return False
    
    app = EnhancedTradingAgentsApp()
    
    # 测试联网搜索
    test_prompt = "请搜索贵州茅台(600519)今天的最新新闻和股价表现，分析其投资价值。"
    model = "qwen-plus-2025-04-28"  # 支持联网的模型
    agent_id = "news_analyst"  # 需要联网的智能体
    
    print(f"🔧 测试配置:")
    print(f"  模型: {model}")
    print(f"  智能体: {agent_id} (启用联网搜索)")
    print(f"  提示: {test_prompt[:50]}...")
    
    try:
        response = await app._call_dashscope(api_key, model, test_prompt, agent_id)
        
        print(f"\n📝 响应结果:")
        print(f"  长度: {len(response)} 字符")
        print(f"  内容预览: {response[:300]}...")
        
        # 检查是否包含搜索来源
        if "📡 **搜索来源**" in response:
            print("✅ 联网搜索成功 - 包含搜索来源")
            return True
        elif "[ref_" in response:
            print("✅ 联网搜索成功 - 包含引用标注")
            return True
        elif "❌" in response:
            print("❌ 联网搜索失败")
            return False
        else:
            print("⚠️ 联网搜索状态不明确")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

async def test_intelligent_agents_with_dashscope():
    """测试智能体与DashScope集成"""
    print("\n" + "="*50)
    print("🤖 测试智能体与DashScope集成")
    print("="*50)
    
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ 未设置 DASHSCOPE_API_KEY 环境变量")
        return False
    
    app = EnhancedTradingAgentsApp()
    
    # 配置阿里百炼
    app.llm_config["阿里百炼"] = api_key
    
    # 配置智能体使用阿里百炼
    test_agents = {
        "social_media_analyst": "阿里百炼:qwen-plus-2025-04-28",
        "news_analyst": "阿里百炼:qwen-plus-2025-04-28",
        "fundamentals_analyst": "阿里百炼:qwen-plus-2025-04-28"
    }
    
    for agent_id, model_config in test_agents.items():
        app.agent_model_config[agent_id] = model_config
    
    print(f"🔧 测试配置:")
    print(f"  配置的智能体: {list(test_agents.keys())}")
    print(f"  使用模型: qwen-plus-2025-04-28 (支持联网)")
    
    # 测试股票数据
    test_symbol = "600519"
    
    try:
        # 获取股票数据
        stock_data = await app._collect_stock_data(test_symbol)
        if "error" in stock_data:
            print(f"❌ 股票数据获取失败: {stock_data['error']}")
            return False
        
        print(f"✅ 股票数据获取成功: {stock_data['price_data']['current_price']}")
        
        # 测试情感分析师
        print(f"\n📊 测试情感分析师...")
        sentiment_result = await app._call_sentiment_analyst(test_symbol, stock_data)
        
        if "requires_internet" in sentiment_result:
            print("❌ 情感分析师检测到模型不支持联网")
            return False
        elif "error" in sentiment_result:
            print(f"❌ 情感分析师调用失败: {sentiment_result['error']}")
            return False
        else:
            analysis = sentiment_result.get("analysis", "")
            print(f"✅ 情感分析师调用成功: {analysis[:100]}...")
        
        # 测试新闻分析师
        print(f"\n📰 测试新闻分析师...")
        news_result = await app._call_news_analyst(test_symbol, stock_data)
        
        if "requires_internet" in news_result:
            print("❌ 新闻分析师检测到模型不支持联网")
            return False
        elif "error" in news_result:
            print(f"❌ 新闻分析师调用失败: {news_result['error']}")
            return False
        else:
            analysis = news_result.get("analysis", "")
            print(f"✅ 新闻分析师调用成功: {analysis[:100]}...")
        
        print("✅ 智能体与DashScope集成测试成功")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("🎯 阿里百炼DashScope联网搜索集成测试")
    print("="*80)
    
    # 检查dashscope安装
    try:
        import dashscope
        print("✅ dashscope 已安装")
    except ImportError:
        print("❌ dashscope 未安装")
        print("💡 请运行: python install_dashscope.py")
        return
    
    # 测试1: 基础调用
    basic_test = await test_dashscope_basic()
    
    # 测试2: 联网搜索
    if basic_test:
        internet_test = await test_dashscope_internet_search()
    else:
        print("⚠️ 跳过联网搜索测试（基础调用失败）")
        internet_test = False
    
    # 测试3: 智能体集成
    if basic_test:
        agent_test = await test_intelligent_agents_with_dashscope()
    else:
        print("⚠️ 跳过智能体集成测试（基础调用失败）")
        agent_test = False
    
    # 总结
    print("\n" + "="*80)
    print("📊 测试结果总结")
    print("="*80)
    print(f"基础调用测试: {'✅ 通过' if basic_test else '❌ 失败'}")
    print(f"联网搜索测试: {'✅ 通过' if internet_test else '❌ 失败'}")
    print(f"智能体集成测试: {'✅ 通过' if agent_test else '❌ 失败'}")
    
    if basic_test and internet_test and agent_test:
        print("\n🎉 恭喜！阿里百炼联网搜索功能完全正常！")
        print("\n💡 使用建议:")
        print("1. 在TradingAgents界面中配置阿里百炼API密钥")
        print("2. 为需要联网的智能体选择 qwen-plus-2025-04-28 模型")
        print("3. 情感分析师、新闻分析师、基本面分析师将自动获取实时数据")
        print("4. 查看分析结果中的搜索来源和引用标注")
    else:
        print("\n❌ 部分功能测试失败")
        print("\n🔧 排查建议:")
        if not basic_test:
            print("1. 检查DASHSCOPE_API_KEY环境变量是否正确设置")
            print("2. 确认API密钥有效且有足够余额")
        if not internet_test:
            print("3. 确认使用支持联网的模型 qwen-plus-2025-04-28")
            print("4. 检查网络连接是否正常")
        if not agent_test:
            print("5. 检查智能体配置是否正确")

if __name__ == "__main__":
    asyncio.run(main())
