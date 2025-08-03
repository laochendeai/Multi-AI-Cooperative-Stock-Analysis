"""
TradingAgents 系统测试脚本
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_data_interface():
    """测试数据接口"""
    try:
        logger.info("测试数据接口...")
        
        from tradingagents.dataflows.interface import DataInterface
        
        data_interface = DataInterface()
        
        # 测试获取股票基本信息
        basic_info = await data_interface.get_stock_basic_info("000001")
        logger.info(f"股票基本信息: {basic_info}")
        
        # 测试获取价格数据
        price_data = await data_interface.get_stock_price_data("000001")
        logger.info(f"价格数据: {price_data}")
        
        # 测试获取综合数据
        comprehensive_data = await data_interface.get_comprehensive_data("000001")
        logger.info(f"综合数据质量: {comprehensive_data.get('data_quality', {})}")
        
        return True
        
    except Exception as e:
        logger.error(f"数据接口测试失败: {e}")
        return False

async def test_memory_manager():
    """测试记忆管理器"""
    try:
        logger.info("测试记忆管理器...")
        
        from tradingagents.agents.utils.memory import MemoryManager
        
        memory_manager = MemoryManager()
        await memory_manager.initialize()
        
        # 测试添加记忆
        await memory_manager.add_memory(
            content="测试记忆内容",
            metadata={"type": "test", "timestamp": datetime.now().isoformat()}
        )
        
        # 测试搜索记忆
        memories = await memory_manager.search_memories("测试", limit=5)
        logger.info(f"搜索到记忆数量: {len(memories)}")
        
        # 测试状态
        status = memory_manager.get_status()
        logger.info(f"记忆系统状态: {status}")
        
        return True
        
    except Exception as e:
        logger.error(f"记忆管理器测试失败: {e}")
        return False

async def test_single_agent():
    """测试单个智能体"""
    try:
        logger.info("测试单个智能体...")
        
        from tradingagents.agents.analysts.market_analyst import MarketAnalyst
        from core.llm_orchestrator import GradioLLMOrchestrator

        # 创建LLM客户端 (使用模拟模式)
        llm_client = GradioLLMOrchestrator()
        
        # 创建市场分析师
        market_analyst = MarketAnalyst(llm_client)
        
        # 准备测试数据
        test_input = {
            "symbol": "000001",
            "price_data": {
                "current_price": 50.0,
                "open": 49.5,
                "high": 51.0,
                "low": 49.0,
                "volume": 1000000,
                "change_percent": 1.0
            },
            "technical_indicators": {
                "rsi": 55.5,
                "macd": 0.8,
                "ma5": 49.0,
                "ma20": 48.0
            }
        }
        
        # 执行分析
        result = await market_analyst.analyze(test_input, {"test_mode": True})
        logger.info(f"分析结果状态: {result.get('status', 'unknown')}")
        
        return result.get("status") == "success"
        
    except Exception as e:
        logger.error(f"单个智能体测试失败: {e}")
        return False

async def test_trading_graph():
    """测试交易工作流图"""
    try:
        logger.info("测试交易工作流图...")
        
        from tradingagents.graph.trading_graph import TradingGraph, AnalysisDepth
        from core.llm_orchestrator import GradioLLMOrchestrator

        # 创建交易图
        llm_client = GradioLLMOrchestrator()
        trading_graph = TradingGraph(llm_client)
        
        # 测试浅层分析
        result = await trading_graph.analyze_stock("000001", AnalysisDepth.SHALLOW)
        
        logger.info(f"工作流结果状态: {result.get('status', 'unknown')}")
        logger.info(f"分析符号: {result.get('symbol', 'unknown')}")
        
        # 测试状态获取
        status = trading_graph.get_analysis_status()
        logger.info(f"工作流状态: {status}")
        
        return result.get("status") in ["completed", "running"]
        
    except Exception as e:
        logger.error(f"交易工作流图测试失败: {e}")
        return False

async def test_cache_manager():
    """测试缓存管理器"""
    try:
        logger.info("测试缓存管理器...")
        
        from tradingagents.dataflows.cache_manager import CacheManager
        
        cache_manager = CacheManager()
        
        # 测试设置缓存
        test_data = {"test": "data", "timestamp": datetime.now().isoformat()}
        cache_manager.set("test_key", test_data, ttl=60)
        
        # 测试获取缓存
        cached_data = cache_manager.get("test_key")
        logger.info(f"缓存数据: {cached_data}")
        
        # 测试缓存信息
        cache_info = cache_manager.get_cache_info()
        logger.info(f"缓存信息: {cache_info}")
        
        return cached_data is not None
        
    except Exception as e:
        logger.error(f"缓存管理器测试失败: {e}")
        return False

async def test_signal_processing():
    """测试信号处理"""
    try:
        logger.info("测试信号处理...")
        
        from tradingagents.graph.signal_processing import SignalProcessor, Signal, SignalType, SignalPriority
        
        signal_processor = SignalProcessor()
        
        # 创建测试信号
        test_signal = Signal(
            signal_type=SignalType.ANALYSIS_COMPLETE,
            sender="test_agent",
            receiver="test_receiver",
            data={"test": "data"},
            priority=SignalPriority.MEDIUM
        )
        
        # 发送信号
        signal_id = await signal_processor.send_signal(test_signal)
        logger.info(f"信号已发送: {signal_id}")
        
        # 启动处理器
        processing_task = asyncio.create_task(signal_processor.start_processing())
        
        # 等待一段时间
        await asyncio.sleep(1)
        
        # 停止处理器
        await signal_processor.stop_processing()
        processing_task.cancel()
        
        # 检查状态
        status = signal_processor.get_signal_status()
        logger.info(f"信号处理状态: {status}")
        
        return True
        
    except Exception as e:
        logger.error(f"信号处理测试失败: {e}")
        return False

async def test_reflection_engine():
    """测试反思引擎"""
    try:
        logger.info("测试反思引擎...")
        
        from tradingagents.graph.reflection import ReflectionEngine
        
        reflection_engine = ReflectionEngine()
        
        # 创建模拟分析会话
        mock_session = {
            "symbol": "000001",
            "status": "completed",
            "results": {
                "market_data": {"data_quality": {"quality_score": 0.8}},
                "analyst_reports": {"market_analysis": {"status": "success"}},
                "research_results": {"debate_rounds": 3},
                "trading_strategy": {"status": "success"},
                "final_decision": {"status": "success"}
            }
        }
        
        # 执行反思
        reflection_result = await reflection_engine.reflect_on_analysis(mock_session)
        logger.info(f"反思结果: {reflection_result.get('overall_score', 'unknown')}")
        
        # 获取性能摘要
        performance_summary = reflection_engine.get_performance_summary()
        logger.info(f"性能摘要: {performance_summary}")
        
        return reflection_result.get("overall_score", 0) > 0
        
    except Exception as e:
        logger.error(f"反思引擎测试失败: {e}")
        return False

async def run_comprehensive_test():
    """运行综合测试"""
    logger.info("开始TradingAgents系统综合测试...")
    
    test_results = {}
    
    # 测试各个组件
    tests = [
        ("数据接口", test_data_interface),
        ("记忆管理器", test_memory_manager),
        ("单个智能体", test_single_agent),
        ("缓存管理器", test_cache_manager),
        ("信号处理", test_signal_processing),
        ("反思引擎", test_reflection_engine),
        ("交易工作流图", test_trading_graph)  # 最后测试，因为最复杂
    ]
    
    for test_name, test_func in tests:
        try:
            logger.info(f"开始测试: {test_name}")
            result = await test_func()
            test_results[test_name] = "✅ 通过" if result else "❌ 失败"
            logger.info(f"{test_name}: {'通过' if result else '失败'}")
        except Exception as e:
            test_results[test_name] = f"❌ 错误: {str(e)}"
            logger.error(f"{test_name} 测试异常: {e}")
    
    # 输出测试报告
    logger.info("\n" + "="*50)
    logger.info("TradingAgents 系统测试报告")
    logger.info("="*50)
    
    for test_name, result in test_results.items():
        logger.info(f"{test_name:20}: {result}")
    
    # 计算通过率
    passed_tests = sum(1 for result in test_results.values() if "✅" in result)
    total_tests = len(test_results)
    pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    logger.info("="*50)
    logger.info(f"测试通过率: {passed_tests}/{total_tests} ({pass_rate:.1f}%)")
    
    if pass_rate >= 80:
        logger.info("🎉 系统测试基本通过，可以运行演示")
    elif pass_rate >= 60:
        logger.info("⚠️ 系统部分功能正常，建议检查失败项")
    else:
        logger.info("❌ 系统存在较多问题，建议修复后再运行")
    
    return test_results

def main():
    """主函数"""
    try:
        # 运行测试
        test_results = asyncio.run(run_comprehensive_test())
        
        # 根据测试结果给出建议
        passed_count = sum(1 for result in test_results.values() if "✅" in result)
        total_count = len(test_results)
        
        print("\n" + "="*60)
        print("🚀 TradingAgents 系统测试完成")
        print("="*60)
        
        if passed_count == total_count:
            print("✅ 所有测试通过！系统可以正常运行")
            print("💡 建议运行: python run_demo.py 查看演示")
        elif passed_count >= total_count * 0.8:
            print("⚠️ 大部分测试通过，系统基本可用")
            print("💡 建议运行: python run_demo.py 查看演示")
            print("🔧 可以检查失败的组件并修复")
        else:
            print("❌ 多个组件测试失败，建议先修复问题")
            print("🔧 请检查依赖项安装和配置")
        
        print("\n📋 下一步操作:")
        print("1. 运行演示: python run_demo.py")
        print("2. 配置LLM API后运行完整系统: python app_new.py")
        print("3. 查看详细文档: README_TRADINGAGENTS.md")
        
    except Exception as e:
        logger.error(f"测试执行失败: {e}")
        print("❌ 测试执行失败，请检查环境配置")

if __name__ == "__main__":
    main()
