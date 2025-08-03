"""
测试优化后的系统功能
"""

import asyncio
import sys
import time
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app_enhanced import EnhancedTradingAgentsApp

async def test_data_collection_speed():
    """测试数据收集速度优化"""
    print("🚀 测试数据收集速度优化")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    test_symbol = "600519"
    
    # 第一次分析（应该从akshare获取）
    print(f"📊 第一次分析 {test_symbol} (从akshare获取)")
    start_time = time.time()
    
    result1 = await app._collect_stock_data(test_symbol)
    
    first_time = time.time() - start_time
    print(f"⏱️ 第一次耗时: {first_time:.2f}秒")
    
    if "error" in result1:
        print(f"❌ 第一次获取失败: {result1['error']}")
        return False
    
    print(f"✅ 第一次获取成功")
    print(f"   当前价格: {result1['price_data']['current_price']}")
    print(f"   数据来源: {result1['data_source']}")
    
    # 等待1秒
    await asyncio.sleep(1)
    
    # 第二次分析（应该使用缓存）
    print(f"\n📊 第二次分析 {test_symbol} (应该使用缓存)")
    start_time = time.time()
    
    result2 = await app._collect_stock_data(test_symbol)
    
    second_time = time.time() - start_time
    print(f"⏱️ 第二次耗时: {second_time:.2f}秒")
    
    if "error" in result2:
        print(f"❌ 第二次获取失败: {result2['error']}")
        return False
    
    print(f"✅ 第二次获取成功")
    print(f"   当前价格: {result2['price_data']['current_price']}")
    print(f"   数据来源: {result2['data_source']}")
    
    # 性能对比
    print(f"\n📈 性能对比:")
    print(f"   第一次: {first_time:.2f}秒")
    print(f"   第二次: {second_time:.2f}秒")
    
    if second_time < first_time * 0.5:
        print(f"   🎉 缓存优化成功！速度提升 {((first_time - second_time) / first_time * 100):.1f}%")
        return True
    else:
        print(f"   ⚠️ 缓存优化效果不明显")
        return False

async def test_google_api():
    """测试Google API修复"""
    print("\n" + "="*60)
    print("🔧 测试Google API修复")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    # 检查Google配置
    if "google" not in app.llm_config:
        print("❌ Google API密钥未配置")
        print("💡 请在界面中配置Google API密钥以测试此功能")
        return False
    
    api_key = app.llm_config["google"]
    model = "gemini-pro"
    test_prompt = "请简单介绍一下股票投资的基本概念，控制在100字以内。"
    
    print(f"🧪 测试Google API调用...")
    print(f"   模型: {model}")
    print(f"   提示: {test_prompt[:30]}...")
    
    try:
        start_time = time.time()
        response = await app._call_google(api_key, model, test_prompt)
        call_time = time.time() - start_time
        
        print(f"⏱️ 调用耗时: {call_time:.2f}秒")
        print(f"📝 响应内容:")
        print(f"   {response[:200]}...")
        
        # 检查是否还是模拟响应
        if "(模拟响应)" in response:
            print("❌ 仍然是模拟响应，API修复失败")
            return False
        elif "❌" in response:
            print(f"❌ API调用失败: {response}")
            return False
        else:
            print("✅ Google API修复成功！")
            return True
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

async def test_real_analysis_with_optimizations():
    """测试带优化的真实分析"""
    print("\n" + "="*60)
    print("🎯 测试带优化的真实分析")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    if not app.llm_config:
        print("❌ 没有配置LLM提供商")
        return False
    
    test_symbol = "600519"
    test_depth = "浅层分析"  # 使用浅层分析加快测试
    test_analysts = ["market_analyst"]  # 只测试一个分析师
    
    print(f"🚀 开始优化后的真实分析...")
    print(f"   股票: {test_symbol}")
    print(f"   深度: {test_depth}")
    print(f"   分析师: {test_analysts}")
    
    try:
        start_time = time.time()
        
        result = await app.analyze_stock_enhanced(
            symbol=test_symbol,
            depth=test_depth,
            analysts=test_analysts,
            use_real_llm=True
        )
        
        total_time = time.time() - start_time
        print(f"⏱️ 总耗时: {total_time:.2f}秒")
        
        if result.get("status") == "completed":
            print("✅ 分析完成！")
            
            # 显示数据收集阶段信息
            stages = result.get("analysis_stages", {})
            data_collection = stages.get("data_collection", {})
            
            if data_collection:
                data_source = data_collection.get("data_source", "未知")
                print(f"📊 数据来源: {data_source}")
                
                if data_source == "cache":
                    print("🎉 使用了缓存数据，速度优化成功！")
                elif data_source == "akshare":
                    print("📡 从akshare获取了新数据")
            
            return True
        else:
            error = result.get("error", "未知错误")
            print(f"❌ 分析失败: {error}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("🎯 TradingAgents 系统优化测试")
    print("="*80)
    
    # 测试1: 数据收集速度优化
    speed_test = await test_data_collection_speed()
    
    # 测试2: Google API修复
    google_test = await test_google_api()
    
    # 测试3: 带优化的真实分析
    analysis_test = await test_real_analysis_with_optimizations()
    
    # 总结
    print("\n" + "="*80)
    print("📊 优化测试结果总结")
    print("="*80)
    print(f"数据收集速度优化: {'✅ 成功' if speed_test else '❌ 失败'}")
    print(f"Google API修复: {'✅ 成功' if google_test else '❌ 失败'}")
    print(f"优化后真实分析: {'✅ 成功' if analysis_test else '❌ 失败'}")
    
    if speed_test and analysis_test:
        print("\n🎉 系统优化成功！")
        print("\n💡 优化效果:")
        print("1. ⚡ 数据收集速度大幅提升（缓存机制）")
        print("2. 📊 智能增量更新，避免重复下载")
        print("3. 🗄️ 本地数据库持久化存储")
        if google_test:
            print("4. 🔧 Google API调用修复完成")
        
        print("\n🚀 现在可以享受更快的分析体验！")
    else:
        print("\n⚠️ 部分优化功能需要进一步调试")
        
        if not speed_test:
            print("- 数据收集缓存机制需要检查")
        if not google_test:
            print("- Google API配置或调用需要检查")
        if not analysis_test:
            print("- 整体分析流程需要检查")

if __name__ == "__main__":
    asyncio.run(main())
