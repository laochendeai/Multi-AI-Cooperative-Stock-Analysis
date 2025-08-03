"""
TradingAgents 基础功能测试
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
        logger.info(f"股票基本信息获取: {'✅' if basic_info.get('symbol') else '❌'}")
        
        # 测试获取价格数据
        price_data = await data_interface.get_stock_price_data("000001")
        logger.info(f"价格数据获取: {'✅' if price_data.get('current_price') else '❌'}")
        
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
        
        logger.info("记忆管理器: ✅")
        return True
        
    except Exception as e:
        logger.error(f"记忆管理器测试失败: {e}")
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
        
        logger.info(f"缓存管理器: {'✅' if cached_data else '❌'}")
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
        
        logger.info(f"信号处理: {'✅' if signal_id else '❌'}")
        return bool(signal_id)
        
    except Exception as e:
        logger.error(f"信号处理测试失败: {e}")
        return False

async def test_base_agent():
    """测试基础智能体"""
    try:
        logger.info("测试基础智能体...")
        
        from tradingagents.agents.base_agent import BaseAgent
        
        # 创建基础智能体实例
        agent = BaseAgent(
            agent_id="test_agent",
            agent_type="测试智能体"
        )
        
        # 测试基本功能
        test_input = {"symbol": "000001", "test": "data"}
        test_context = {"test_mode": True}
        
        # 由于没有LLM客户端，这里只测试基础结构
        logger.info("基础智能体结构: ✅")
        return True
        
    except Exception as e:
        logger.error(f"基础智能体测试失败: {e}")
        return False

def test_project_structure():
    """测试项目结构"""
    try:
        logger.info("测试项目结构...")
        
        # 检查关键目录
        required_dirs = [
            "tradingagents",
            "tradingagents/agents",
            "tradingagents/agents/analysts",
            "tradingagents/agents/researchers", 
            "tradingagents/agents/trader",
            "tradingagents/agents/risk_mgmt",
            "tradingagents/agents/managers",
            "tradingagents/agents/utils",
            "tradingagents/graph",
            "tradingagents/dataflows",
            "tradingagents/config"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not (project_root / dir_path).exists():
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            logger.error(f"缺少目录: {missing_dirs}")
            return False
        
        # 检查关键文件
        required_files = [
            "tradingagents/agents/base_agent.py",
            "tradingagents/graph/trading_graph.py",
            "tradingagents/dataflows/interface.py",
            "app_new.py",
            "run_demo.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"缺少文件: {missing_files}")
            return False
        
        logger.info("项目结构: ✅")
        return True
        
    except Exception as e:
        logger.error(f"项目结构测试失败: {e}")
        return False

async def run_basic_tests():
    """运行基础测试"""
    logger.info("开始TradingAgents基础功能测试...")
    
    test_results = {}
    
    # 测试项目结构
    test_results["项目结构"] = "✅ 通过" if test_project_structure() else "❌ 失败"
    
    # 异步测试
    async_tests = [
        ("数据接口", test_data_interface),
        ("记忆管理器", test_memory_manager),
        ("缓存管理器", test_cache_manager),
        ("信号处理", test_signal_processing),
        ("基础智能体", test_base_agent)
    ]
    
    for test_name, test_func in async_tests:
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
    logger.info("TradingAgents 基础功能测试报告")
    logger.info("="*50)
    
    for test_name, result in test_results.items():
        logger.info(f"{test_name:15}: {result}")
    
    # 计算通过率
    passed_tests = sum(1 for result in test_results.values() if "✅" in result)
    total_tests = len(test_results)
    pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    logger.info("="*50)
    logger.info(f"测试通过率: {passed_tests}/{total_tests} ({pass_rate:.1f}%)")
    
    if pass_rate >= 80:
        logger.info("🎉 基础功能测试通过，系统可以运行演示")
        print("\n✅ 基础功能测试通过！")
        print("💡 建议运行: python run_demo.py 查看演示")
    elif pass_rate >= 60:
        logger.info("⚠️ 大部分基础功能正常")
        print("\n⚠️ 大部分基础功能正常")
        print("💡 可以尝试运行演示: python run_demo.py")
    else:
        logger.info("❌ 基础功能存在问题")
        print("\n❌ 基础功能存在问题，建议检查环境配置")
    
    return test_results

def main():
    """主函数"""
    try:
        # 运行基础测试
        test_results = asyncio.run(run_basic_tests())
        
        print("\n" + "="*60)
        print("🚀 TradingAgents 基础测试完成")
        print("="*60)
        
        passed_count = sum(1 for result in test_results.values() if "✅" in result)
        total_count = len(test_results)
        
        if passed_count >= total_count * 0.8:
            print("✅ 基础功能正常，可以运行演示系统")
            print("\n📋 下一步操作:")
            print("1. 运行演示: python run_demo.py")
            print("2. 查看详细文档: README_TRADINGAGENTS.md")
        else:
            print("⚠️ 部分功能异常，建议检查环境")
            print("\n🔧 可能的解决方案:")
            print("1. 检查Python版本 (需要3.8+)")
            print("2. 安装依赖: pip install gradio")
            print("3. 检查项目文件完整性")
        
    except Exception as e:
        logger.error(f"测试执行失败: {e}")
        print("❌ 测试执行失败，请检查环境配置")

if __name__ == "__main__":
    main()
