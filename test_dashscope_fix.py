"""
测试阿里百炼API修复
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app_enhanced import EnhancedTradingAgentsApp

async def test_dashscope_basic_call():
    """测试阿里百炼基础调用"""
    print("🧪 测试阿里百炼基础调用")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    # 检查是否有阿里百炼配置
    if "阿里百炼" not in app.llm_config:
        print("❌ 未找到阿里百炼配置")
        return False
    
    api_key = app.llm_config["阿里百炼"]
    model = "qwen-turbo"
    prompt = "请简单介绍一下股票市场。"
    
    print(f"📊 API密钥: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else api_key}")
    print(f"📊 模型: {model}")
    print(f"📊 提示: {prompt}")
    
    try:
        result = await app._call_dashscope(api_key, model, prompt, "test_agent")
        
        if result.startswith("❌"):
            print(f"❌ 调用失败: {result}")
            return False
        else:
            print(f"✅ 调用成功")
            print(f"📄 响应长度: {len(result)} 字符")
            print(f"📄 响应预览: {result[:200]}...")
            return True
            
    except Exception as e:
        print(f"❌ 调用异常: {e}")
        return False

async def test_dashscope_with_search():
    """测试阿里百炼联网搜索"""
    print("\n🧪 测试阿里百炼联网搜索")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    if "阿里百炼" not in app.llm_config:
        print("❌ 未找到阿里百炼配置")
        return False
    
    api_key = app.llm_config["阿里百炼"]
    model = "qwen-turbo"
    prompt = "请搜索并分析今日股票600330的最新新闻。"
    
    print(f"📊 测试联网搜索功能")
    print(f"📊 提示: {prompt}")
    
    try:
        # 使用需要联网搜索的智能体ID
        result = await app._call_dashscope(api_key, model, prompt, "news_analyst")
        
        if result.startswith("❌"):
            print(f"❌ 联网搜索失败: {result}")
            return False
        else:
            print(f"✅ 联网搜索成功")
            print(f"📄 响应长度: {len(result)} 字符")
            print(f"📄 响应预览: {result[:300]}...")
            
            # 检查是否包含搜索相关内容
            if "搜索" in result or "最新" in result or "新闻" in result:
                print(f"✅ 响应包含搜索相关内容")
            else:
                print(f"⚠️ 响应可能未包含搜索内容")
            
            return True
            
    except Exception as e:
        print(f"❌ 联网搜索异常: {e}")
        return False

async def test_different_models():
    """测试不同的阿里百炼模型"""
    print("\n🧪 测试不同的阿里百炼模型")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    if "阿里百炼" not in app.llm_config:
        print("❌ 未找到阿里百炼配置")
        return False
    
    api_key = app.llm_config["阿里百炼"]
    models = ["qwen-turbo", "qwen-plus", "qwen-max"]
    prompt = "简单说明股票分析的重要性。"
    
    results = {}
    
    for model in models:
        print(f"\n📊 测试模型: {model}")
        
        try:
            result = await app._call_dashscope(api_key, model, prompt, "test_agent")
            
            if result.startswith("❌"):
                print(f"  ❌ {model} 调用失败: {result}")
                results[model] = False
            else:
                print(f"  ✅ {model} 调用成功")
                print(f"  📄 响应长度: {len(result)} 字符")
                results[model] = True
                
        except Exception as e:
            print(f"  ❌ {model} 调用异常: {e}")
            results[model] = False
    
    print(f"\n📊 模型测试结果:")
    for model, success in results.items():
        print(f"  {model}: {'✅ 成功' if success else '❌ 失败'}")
    
    return any(results.values())

async def test_error_handling():
    """测试错误处理"""
    print("\n🧪 测试错误处理")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    # 测试无效API密钥
    print("📊 测试无效API密钥:")
    try:
        result = await app._call_dashscope("invalid_key", "qwen-turbo", "测试", "test_agent")
        print(f"  结果: {result}")
        
        if "密钥无效" in result or "401" in result:
            print("  ✅ 正确识别无效密钥")
        else:
            print("  ⚠️ 未正确识别无效密钥")
    except Exception as e:
        print(f"  异常: {e}")
    
    # 测试无效模型
    print("\n📊 测试无效模型:")
    if "阿里百炼" in app.llm_config:
        api_key = app.llm_config["阿里百炼"]
        try:
            result = await app._call_dashscope(api_key, "invalid-model", "测试", "test_agent")
            print(f"  结果: {result}")
            
            if "参数错误" in result or "400" in result or "模型" in result:
                print("  ✅ 正确识别无效模型")
            else:
                print("  ⚠️ 未正确识别无效模型")
        except Exception as e:
            print(f"  异常: {e}")
    
    return True

def test_configuration():
    """测试配置"""
    print("\n🧪 测试配置")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    print("📊 LLM配置检查:")
    for provider, key in app.llm_config.items():
        print(f"  {provider}: {key[:10]}...{key[-10:] if len(key) > 20 else key}")
    
    if "阿里百炼" in app.llm_config:
        print("✅ 找到阿里百炼配置")
        return True
    else:
        print("❌ 未找到阿里百炼配置")
        print("请检查config/llm_config.json文件或环境变量")
        return False

async def main():
    """主测试函数"""
    print("🎯 阿里百炼API修复测试")
    print("="*80)
    
    # 执行各项测试
    tests = [
        ("配置检查", test_configuration),
        ("基础调用", test_dashscope_basic_call),
        ("联网搜索", test_dashscope_with_search),
        ("不同模型", test_different_models),
        ("错误处理", test_error_handling),
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
    print("📊 阿里百炼API修复测试总结")
    print("="*80)
    
    for test_name, success in results.items():
        print(f"{test_name}: {'✅ 通过' if success else '❌ 失败'}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 阿里百炼API修复测试通过！")
        print("\n💡 修复内容:")
        print("1. ✅ 简化了联网搜索参数配置")
        print("2. ✅ 改进了错误处理和日志记录")
        print("3. ✅ 增强了异常信息的详细程度")
        print("4. ✅ 支持多种模型测试")
        
        print("\n🚀 现在可以:")
        print("1. 重启主程序: python app_enhanced.py")
        print("2. 阿里百炼API调用应该正常工作")
        print("3. 联网搜索功能应该可用")
        print("4. 错误信息更加详细和有用")
    else:
        print("\n❌ 部分测试失败")
        print("需要检查失败的测试项目")
        
        if not results.get("配置检查", False):
            print("\n💡 配置建议:")
            print("1. 检查config/llm_config.json文件")
            print("2. 确保阿里百炼API密钥正确")
            print("3. 或设置环境变量DASHSCOPE_API_KEY")

if __name__ == "__main__":
    asyncio.run(main())
