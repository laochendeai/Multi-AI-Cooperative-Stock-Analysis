"""
测试界面集成功能
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app_enhanced import EnhancedTradingAgentsApp, _get_model_choices

def test_llm_providers():
    """测试LLM提供商配置"""
    print("🧪 测试LLM提供商配置")
    print("="*50)
    
    app = EnhancedTradingAgentsApp()
    
    # 测试可用模型
    available_models = app.get_available_models()
    print(f"📊 可用模型提供商: {list(available_models.keys())}")
    
    # 检查阿里百炼是否包含
    if "阿里百炼" in available_models:
        print("✅ 阿里百炼已包含在可用模型中")
        print(f"   支持的模型: {available_models['阿里百炼']}")
    else:
        print("❌ 阿里百炼未包含在可用模型中")
        return False
    
    # 测试模型推荐
    dashscope_models = app.get_common_models_for_provider("阿里百炼")
    print(f"📋 阿里百炼推荐模型: {dashscope_models}")
    
    return True

def test_model_choices():
    """测试模型选择列表"""
    print("\n🧪 测试模型选择列表")
    print("="*50)
    
    app = EnhancedTradingAgentsApp()
    
    # 模拟配置阿里百炼
    app.llm_config["阿里百炼"] = "test_key"
    
    # 获取模型选择
    choices = _get_model_choices()
    print(f"📋 模型选择列表 ({len(choices)} 个):")
    
    dashscope_choices = [choice for choice in choices if choice.startswith("阿里百炼:")]
    
    if dashscope_choices:
        print("✅ 阿里百炼模型已包含在选择列表中:")
        for choice in dashscope_choices:
            print(f"   - {choice}")
        return True
    else:
        print("❌ 阿里百炼模型未包含在选择列表中")
        print(f"所有选择: {choices}")
        return False

def test_agent_configuration():
    """测试智能体配置"""
    print("\n🧪 测试智能体配置")
    print("="*50)
    
    app = EnhancedTradingAgentsApp()
    
    # 模拟配置阿里百炼
    app.llm_config["阿里百炼"] = "test_key"
    
    # 测试智能体列表
    agents = app.get_agent_list()
    print(f"📊 智能体数量: {len(agents)}")
    
    # 测试关键智能体
    key_agents = ["social_media_analyst", "news_analyst", "fundamentals_analyst"]
    
    for agent_id in key_agents:
        agent_info = next((agent for agent in agents if agent["id"] == agent_id), None)
        if agent_info:
            print(f"✅ {agent_info['name']} 配置正常")
        else:
            print(f"❌ {agent_id} 未找到")
            return False
    
    # 测试模型配置更新
    test_config = "阿里百炼:qwen-plus-2025-04-28"
    result = app.update_agent_model("social_media_analyst", test_config)
    
    if result.get("status") == "success":
        print("✅ 智能体模型配置更新成功")
        
        # 验证配置是否保存
        saved_config = app.agent_model_config.get("social_media_analyst")
        if saved_config == test_config:
            print("✅ 配置保存验证成功")
            return True
        else:
            print(f"❌ 配置保存验证失败: {saved_config} != {test_config}")
            return False
    else:
        print(f"❌ 智能体模型配置更新失败: {result}")
        return False

def test_internet_capability_detection():
    """测试联网能力检测"""
    print("\n🧪 测试联网能力检测")
    print("="*50)

    import asyncio

    app = EnhancedTradingAgentsApp()

    # 测试阿里百炼联网能力检测
    test_cases = [
        ("阿里百炼", "qwen-turbo", True),
        ("阿里百炼", "qwen-plus", True),
        ("阿里百炼", "qwen-max", True),
        ("阿里百炼", "qwen-plus-2025-04-28", True),
        ("deepseek", "deepseek-chat", False),
        ("openai", "gpt-4", True),  # OpenAI GPT-4 支持联网
    ]

    all_passed = True

    async def run_test():
        nonlocal all_passed
        for provider, model, expected in test_cases:
            result = await app.data_collector.check_llm_internet_capability(provider, model, "test_key")

            if result == expected:
                status = "✅"
            else:
                status = "❌"
                all_passed = False

            print(f"{status} {provider}:{model} 联网能力检测: {result} (期望: {expected})")

    # 运行异步测试
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(run_test())

    return all_passed

def main():
    """主测试函数"""
    print("🎯 TradingAgents 界面集成测试")
    print("="*80)
    
    # 测试1: LLM提供商配置
    providers_test = test_llm_providers()
    
    # 测试2: 模型选择列表
    choices_test = test_model_choices()
    
    # 测试3: 智能体配置
    agent_test = test_agent_configuration()
    
    # 测试4: 联网能力检测
    internet_test = test_internet_capability_detection()
    
    # 总结
    print("\n" + "="*80)
    print("📊 测试结果总结")
    print("="*80)
    print(f"LLM提供商配置: {'✅ 通过' if providers_test else '❌ 失败'}")
    print(f"模型选择列表: {'✅ 通过' if choices_test else '❌ 失败'}")
    print(f"智能体配置: {'✅ 通过' if agent_test else '❌ 失败'}")
    print(f"联网能力检测: {'✅ 通过' if internet_test else '❌ 失败'}")
    
    if all([providers_test, choices_test, agent_test, internet_test]):
        print("\n🎉 所有界面集成测试通过！")
        print("\n💡 现在可以:")
        print("1. 运行 python app_enhanced.py")
        print("2. 在 '⚙️ LLM配置' 中配置阿里百炼API密钥")
        print("3. 在 '🤖 智能体配置' 中看到阿里百炼模型选项")
        print("4. 为情感、新闻、基本面分析师选择支持联网的模型")
        print("5. 享受真实的联网搜索分析功能")
    else:
        print("\n❌ 部分测试失败，需要进一步检查")
        
        if not providers_test:
            print("- 检查 get_available_models() 方法")
        if not choices_test:
            print("- 检查 _get_model_choices() 函数")
        if not agent_test:
            print("- 检查智能体配置保存逻辑")
        if not internet_test:
            print("- 检查联网能力检测逻辑")

if __name__ == "__main__":
    main()
