"""
测试新的阿里百炼OpenAI兼容API调用方式
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app_enhanced import EnhancedTradingAgentsApp

async def test_new_dashscope_api():
    """测试新的DashScope API调用"""
    print("🧪 测试新的阿里百炼OpenAI兼容API")
    print("="*60)
    
    # 检查环境变量
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ 未设置 DASHSCOPE_API_KEY 环境变量")
        print("💡 请设置环境变量: export DASHSCOPE_API_KEY=your_api_key")
        print("或者在测试中手动输入API密钥")
        
        # 允许手动输入API密钥进行测试
        manual_key = input("请输入您的DashScope API密钥 (或按Enter跳过): ").strip()
        if manual_key:
            api_key = manual_key
        else:
            return False
    
    app = EnhancedTradingAgentsApp()
    
    print(f"🔧 测试配置:")
    print(f"  API密钥: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else api_key}")
    print(f"  API端点: https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
    print()
    
    # 测试不同的模型和智能体
    test_cases = [
        {
            "model": "qwen-turbo",
            "agent_id": "market_analyst",
            "agent_name": "市场分析师",
            "need_internet": False,
            "prompt": "请简单分析一下股票投资的基本概念，控制在100字以内。"
        },
        {
            "model": "qwen-plus", 
            "agent_id": "social_media_analyst",
            "agent_name": "情感分析师",
            "need_internet": True,
            "prompt": "请搜索贵州茅台(600519)今天的社交媒体情绪和投资者情感。"
        },
        {
            "model": "qwen-max",
            "agent_id": "news_analyst", 
            "agent_name": "新闻分析师",
            "need_internet": True,
            "prompt": "请搜索并分析今天影响贵州茅台(600519)的最新新闻。"
        }
    ]
    
    results = {}
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📊 测试 {i}: {test_case['agent_name']} ({test_case['model']})")
        print(f"  联网搜索: {'✅ 启用' if test_case['need_internet'] else '❌ 关闭'}")
        print(f"  提示: {test_case['prompt'][:50]}...")
        
        try:
            result = await app._call_dashscope(
                api_key=api_key,
                model=test_case['model'],
                prompt=test_case['prompt'],
                agent_id=test_case['agent_id']
            )
            
            print(f"  📝 响应长度: {len(result)} 字符")
            
            if result.startswith("❌"):
                print(f"  ❌ 调用失败: {result}")
                results[test_case['agent_id']] = False
            else:
                print(f"  ✅ 调用成功")
                print(f"  📄 响应预览: {result[:150]}...")
                
                # 检查联网搜索结果
                if test_case['need_internet']:
                    if "📡 **搜索来源**" in result or "[ref_" in result:
                        print(f"  🌐 联网搜索: ✅ 检测到搜索结果")
                    else:
                        print(f"  🌐 联网搜索: ⚠️ 未检测到明显的搜索标识")
                
                results[test_case['agent_id']] = True
            
        except Exception as e:
            print(f"  ❌ 调用异常: {e}")
            results[test_case['agent_id']] = False
        
        print()
    
    return results

async def test_http_direct_call():
    """直接测试HTTP API调用"""
    print("🌐 直接测试HTTP API调用")
    print("="*60)
    
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ 需要DASHSCOPE_API_KEY环境变量")
        return False
    
    try:
        import httpx
        
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 测试基础调用
        data = {
            "model": "qwen-turbo",
            "messages": [
                {"role": "user", "content": "你好，请简单介绍一下你自己。"}
            ],
            "max_tokens": 100
        }
        
        print(f"🔧 直接HTTP调用测试:")
        print(f"  URL: {url}")
        print(f"  模型: qwen-turbo")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=data)
            
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result:
                    content = result["choices"][0]["message"]["content"]
                    print(f"  ✅ 调用成功")
                    print(f"  📄 响应: {content[:100]}...")
                    return True
                else:
                    print(f"  ❌ 响应格式异常: {result}")
                    return False
            else:
                print(f"  ❌ HTTP错误: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ 直接HTTP调用失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🎯 阿里百炼新API调用方式测试")
    print("="*80)
    
    # 测试1: 直接HTTP调用
    http_test = await test_http_direct_call()
    
    # 测试2: 应用集成调用
    if http_test:
        app_tests = await test_new_dashscope_api()
    else:
        print("⚠️ 跳过应用集成测试（HTTP调用失败）")
        app_tests = {}
    
    # 总结
    print("="*80)
    print("📊 测试结果总结")
    print("="*80)
    print(f"直接HTTP调用: {'✅ 通过' if http_test else '❌ 失败'}")
    
    if app_tests:
        print(f"应用集成测试:")
        for agent_id, success in app_tests.items():
            print(f"  - {agent_id}: {'✅ 通过' if success else '❌ 失败'}")
        
        all_app_tests_passed = all(app_tests.values())
        print(f"应用集成总体: {'✅ 通过' if all_app_tests_passed else '❌ 失败'}")
    else:
        all_app_tests_passed = False
        print("应用集成测试: ❌ 未执行")
    
    if http_test and all_app_tests_passed:
        print("\n🎉 所有测试通过！新的API调用方式工作正常！")
        print("\n💡 现在可以:")
        print("1. 重启主程序: python app_enhanced.py")
        print("2. 在界面中配置阿里百炼API密钥")
        print("3. 选择支持联网的模型: qwen-max, qwen-plus, qwen-turbo")
        print("4. 享受真实的联网搜索分析功能")
    else:
        print("\n❌ 部分测试失败")
        print("\n🔧 排查建议:")
        if not http_test:
            print("1. 检查DASHSCOPE_API_KEY是否正确")
            print("2. 确认API密钥有效且有余额")
            print("3. 检查网络连接")
        if not all_app_tests_passed:
            print("4. 检查应用代码集成")
            print("5. 查看详细错误信息")

if __name__ == "__main__":
    asyncio.run(main())
