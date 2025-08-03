"""
直接测试_call_dashscope方法
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app_enhanced import EnhancedTradingAgentsApp

async def test_dashscope_method():
    """测试_call_dashscope方法"""
    print("🧪 测试_call_dashscope方法")
    print("="*50)
    
    app = EnhancedTradingAgentsApp()
    
    # 测试参数
    api_key = "test_key"  # 使用测试密钥
    model = "qwen-turbo"
    prompt = "测试提示"
    agent_id = "social_media_analyst"  # 需要联网的智能体
    
    print(f"🔧 测试参数:")
    print(f"  API密钥: {api_key}")
    print(f"  模型: {model}")
    print(f"  智能体: {agent_id}")
    print(f"  提示: {prompt}")
    
    try:
        # 调用方法
        result = await app._call_dashscope(api_key, model, prompt, agent_id)
        
        print(f"\n📝 调用结果:")
        print(f"  结果类型: {type(result)}")
        print(f"  结果长度: {len(result)} 字符")
        print(f"  结果内容: {result}")
        
        # 检查是否是导入错误
        if "dashscope未安装" in result:
            print("❌ 检测到dashscope导入问题")
            
            # 尝试直接导入测试
            print("\n🔍 直接导入测试:")
            try:
                import dashscope
                print("✅ 直接导入dashscope成功")
                print(f"  dashscope模块: {dashscope}")
                print(f"  Generation类: {hasattr(dashscope, 'Generation')}")
            except ImportError as e:
                print(f"❌ 直接导入dashscope失败: {e}")
            
            return False
        else:
            print("✅ dashscope导入正常")
            return True
            
    except Exception as e:
        print(f"❌ 方法调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_different_agents():
    """测试不同智能体的调用"""
    print("\n🧪 测试不同智能体调用")
    print("="*50)
    
    app = EnhancedTradingAgentsApp()
    
    # 测试不同的智能体
    test_agents = [
        ("market_analyst", "市场分析师", False),  # 不需要联网
        ("social_media_analyst", "情感分析师", True),  # 需要联网
        ("news_analyst", "新闻分析师", True),  # 需要联网
        ("fundamentals_analyst", "基本面分析师", True),  # 需要联网
    ]
    
    results = {}
    
    for agent_id, agent_name, need_internet in test_agents:
        print(f"\n📊 测试 {agent_name} ({agent_id})")
        print(f"  需要联网: {need_internet}")
        
        try:
            result = await app._call_dashscope("test_key", "qwen-turbo", "测试", agent_id)
            
            if "dashscope未安装" in result:
                print(f"  ❌ 导入失败")
                results[agent_id] = False
            else:
                print(f"  ✅ 导入成功")
                results[agent_id] = True
                
        except Exception as e:
            print(f"  ❌ 调用异常: {e}")
            results[agent_id] = False
    
    return results

async def main():
    """主测试函数"""
    print("🎯 DashScope方法直接测试")
    print("="*80)
    
    # 测试1: 基本方法调用
    method_test = await test_dashscope_method()
    
    # 测试2: 不同智能体调用
    agent_tests = await test_different_agents()
    
    # 总结
    print("\n" + "="*80)
    print("📊 测试结果总结")
    print("="*80)
    print(f"基本方法调用: {'✅ 通过' if method_test else '❌ 失败'}")
    
    print(f"智能体调用测试:")
    for agent_id, success in agent_tests.items():
        print(f"  - {agent_id}: {'✅ 通过' if success else '❌ 失败'}")
    
    all_passed = method_test and all(agent_tests.values())
    
    if all_passed:
        print("\n🎉 所有测试通过！")
        print("\n💡 如果Web界面仍显示错误，请:")
        print("1. 重启主程序: python app_enhanced.py")
        print("2. 清除浏览器缓存")
        print("3. 检查是否使用了正确的Python环境")
    else:
        print("\n❌ 部分测试失败")
        print("\n🔧 可能的解决方案:")
        print("1. 重新安装dashscope: pip install --upgrade dashscope")
        print("2. 检查Python环境一致性")
        print("3. 重启Python解释器")

if __name__ == "__main__":
    asyncio.run(main())
