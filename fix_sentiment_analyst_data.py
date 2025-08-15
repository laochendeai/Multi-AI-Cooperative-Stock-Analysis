#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents sentiment_analyst数据为空问题修复脚本
修复social_media_analyst智能体数据获取问题
"""

import sys
import os
import asyncio
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analyze_sentiment_analyst_issue():
    """分析sentiment_analyst问题"""
    print("🔍 分析sentiment_analyst数据为空问题...")
    
    print("📊 问题症状:")
    print("   • agent_id: 'social_media_analyst'")
    print("   • analysis: '智能体数据为空'")
    print("   • confidence: 0.0")
    print("   • status: 'no_data'")
    
    print("\n🎯 可能原因:")
    print("   1. social_media_analyst执行时出现异常")
    print("   2. 输入数据为空或格式不正确")
    print("   3. LLM调用失败")
    print("   4. 网络连接问题")
    print("   5. API密钥配置问题")
    
    return True

def test_social_media_analyst_directly():
    """直接测试social_media_analyst"""
    print("\n🧪 直接测试social_media_analyst...")
    
    try:
        from tradingagents.agents.analysts.social_media_analyst import SocialMediaAnalyst
        from tradingagents.core.llm_client import LLMClient
        
        print("   ✅ 成功导入SocialMediaAnalyst")
        
        # 创建测试用的LLM客户端
        llm_client = LLMClient()
        print("   ✅ 成功创建LLM客户端")
        
        # 创建social_media_analyst实例
        analyst = SocialMediaAnalyst(llm_client, None)  # memory_manager可以为None
        print("   ✅ 成功创建SocialMediaAnalyst实例")
        
        # 准备测试输入数据
        test_input = {
            "symbol": "000001",
            "social_data": {
                "sentiment_score": 0.6,
                "discussion_volume": "高",
                "key_topics": ["业绩", "增长", "前景"]
            },
            "news_sentiment": {
                "positive_count": 15,
                "negative_count": 5,
                "neutral_count": 10
            }
        }
        
        print("   📝 准备测试输入数据:")
        print(f"      symbol: {test_input['symbol']}")
        print(f"      social_data: {test_input['social_data']}")
        print(f"      news_sentiment: {test_input['news_sentiment']}")
        
        return True, analyst, test_input
        
    except ImportError as e:
        print(f"   ❌ 导入失败: {e}")
        return False, None, None
    except Exception as e:
        print(f"   ❌ 创建失败: {e}")
        return False, None, None

async def run_sentiment_analysis_test(analyst, test_input):
    """运行情感分析测试"""
    print("\n🚀 运行情感分析测试...")
    
    try:
        # 运行分析
        print("   🔄 执行情感分析...")
        result = await analyst.process_with_memory(test_input, {"analysis_type": "sentiment"})
        
        print("   📊 分析结果:")
        print(f"      状态: {result.get('status', 'unknown')}")
        print(f"      智能体ID: {result.get('agent_id', 'unknown')}")
        
        if result.get('status') == 'success':
            content = result.get('content', {})
            raw_response = result.get('raw_response', '')
            
            print(f"      内容类型: {type(content)}")
            if isinstance(content, dict):
                print(f"      内容键: {list(content.keys())}")
                for k, v in content.items():
                    print(f"        {k}: {v}")
            else:
                print(f"      内容: {content}")
            
            print(f"      原始响应长度: {len(raw_response)}字符")
            if raw_response:
                print(f"      原始响应预览: {raw_response[:100]}...")
            
            return True, result
        else:
            error = result.get('error', 'unknown error')
            print(f"      ❌ 分析失败: {error}")
            return False, result
            
    except Exception as e:
        print(f"   ❌ 测试执行失败: {e}")
        return False, {"error": str(e)}

def check_llm_configuration():
    """检查LLM配置"""
    print("\n🔧 检查LLM配置...")
    
    try:
        from tradingagents.core.llm_client import LLMClient
        
        # 创建LLM客户端
        llm_client = LLMClient()
        
        # 检查配置
        print("   📋 LLM配置检查:")
        
        # 检查是否有可用的提供商
        if hasattr(llm_client, 'providers'):
            providers = llm_client.providers
            print(f"      可用提供商: {list(providers.keys()) if providers else '无'}")
        
        # 检查默认提供商
        if hasattr(llm_client, 'default_provider'):
            default_provider = llm_client.default_provider
            print(f"      默认提供商: {default_provider}")
        
        # 尝试简单的LLM调用测试
        print("   🧪 测试LLM调用...")
        
        # 这里可能需要根据实际的LLMClient接口调整
        test_prompt = "请简单回答：今天天气如何？"
        
        # 注意：这里可能需要异步调用
        # result = await llm_client.get_response(test_prompt)
        print("   ⚠️ LLM调用测试需要在异步环境中进行")
        
        return True
        
    except Exception as e:
        print(f"   ❌ LLM配置检查失败: {e}")
        return False

def create_mock_sentiment_analyst():
    """创建模拟的sentiment_analyst"""
    print("\n🎭 创建模拟sentiment_analyst...")
    
    mock_result = {
        "status": "success",
        "agent_id": "social_media_analyst",
        "agent_type": "情感分析师",
        "analysis_type": "sentiment_analysis",
        "symbol": "000001",
        "content": {
            "sentiment_score": 0.65,
            "market_mood": "乐观",
            "discussion_volume": "高",
            "key_topics": ["业绩增长", "市场前景", "政策利好"],
            "analysis_summary": "基于社交媒体数据分析，投资者对该股票整体情绪偏向乐观，讨论热度较高，主要关注业绩增长和市场前景。预期短期内可能有积极表现。",
            "confidence_level": "中等",
            "risk_factors": ["市场波动", "政策变化"],
            "recommendation": "谨慎乐观"
        },
        "raw_response": "详细的LLM分析响应：根据社交媒体平台的讨论数据，投资者对000001股票的情绪整体偏向乐观...",
        "confidence": 0.75,
        "timestamp": datetime.now().isoformat()
    }
    
    print("   📊 模拟结果结构:")
    print(f"      状态: {mock_result['status']}")
    print(f"      智能体ID: {mock_result['agent_id']}")
    print(f"      内容键: {list(mock_result['content'].keys())}")
    print(f"      分析摘要长度: {len(mock_result['content']['analysis_summary'])}字符")
    print(f"      原始响应长度: {len(mock_result['raw_response'])}字符")
    
    return mock_result

def suggest_fixes():
    """建议修复方案"""
    print("\n🔧 建议修复方案:")
    
    fixes = [
        {
            "问题": "LLM配置问题",
            "解决方案": [
                "检查API密钥配置",
                "验证LLM提供商设置",
                "测试网络连接"
            ]
        },
        {
            "问题": "输入数据为空",
            "解决方案": [
                "为social_media_analyst提供默认输入数据",
                "添加输入数据验证",
                "实现数据获取失败时的备选方案"
            ]
        },
        {
            "问题": "智能体执行异常",
            "解决方案": [
                "添加更详细的异常处理",
                "实现智能体执行超时机制",
                "提供智能体执行失败时的默认结果"
            ]
        },
        {
            "问题": "结果提取逻辑问题",
            "解决方案": [
                "改进_extract_agent_result方法",
                "添加对error状态的处理",
                "实现智能体结果验证机制"
            ]
        }
    ]
    
    for i, fix in enumerate(fixes, 1):
        print(f"\n   {i}. {fix['问题']}:")
        for solution in fix['解决方案']:
            print(f"      • {solution}")
    
    return fixes

async def main():
    """主函数"""
    print("=" * 60)
    print("🔧 TradingAgents sentiment_analyst数据为空问题修复")
    print("=" * 60)
    print(f"📅 修复时间: {datetime.now()}")
    print()
    
    # 分析问题
    analyze_sentiment_analyst_issue()
    
    # 检查LLM配置
    llm_ok = check_llm_configuration()
    
    # 测试social_media_analyst
    test_ok, analyst, test_input = test_social_media_analyst_directly()
    
    if test_ok and analyst:
        # 运行实际测试
        success, result = await run_sentiment_analysis_test(analyst, test_input)
        
        if success:
            print("\n✅ sentiment_analyst测试成功！")
            print("   💡 问题可能在于实际运行时的输入数据或环境配置")
        else:
            print("\n❌ sentiment_analyst测试失败")
            print("   🔍 需要进一步检查智能体实现和LLM配置")
    
    # 创建模拟结果
    mock_result = create_mock_sentiment_analyst()
    
    # 建议修复方案
    suggest_fixes()
    
    print("\n" + "=" * 60)
    print("📊 修复建议总结")
    print("=" * 60)
    
    print("🎯 立即可行的修复:")
    print("   1. 为social_media_analyst提供默认的社交媒体数据")
    print("   2. 改进错误处理，在智能体失败时提供有意义的默认结果")
    print("   3. 添加智能体执行状态的详细日志")
    print("   4. 实现智能体结果验证和备选机制")
    
    print("\n💡 长期改进:")
    print("   • 实现真实的社交媒体数据获取")
    print("   • 优化智能体提示词和分析逻辑")
    print("   • 建立智能体性能监控机制")
    print("   • 添加智能体A/B测试功能")

if __name__ == "__main__":
    asyncio.run(main())
