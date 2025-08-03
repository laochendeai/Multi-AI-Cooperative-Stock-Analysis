"""
交易工作流图 - 协调所有智能体的工作流程
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from ..agents.analysts.market_analyst import MarketAnalyst
from ..agents.analysts.social_media_analyst import SocialMediaAnalyst
from ..agents.analysts.news_analyst import NewsAnalyst
from ..agents.analysts.fundamentals_analyst import FundamentalsAnalyst
from ..agents.researchers.bull_researcher import BullResearcher
from ..agents.researchers.bear_researcher import BearResearcher
from ..agents.managers.research_manager import ResearchManager
from ..agents.trader.trader import Trader
from ..agents.risk_mgmt.aggressive_debator import AggressiveDebator
from ..agents.risk_mgmt.conservative_debator import ConservativeDebator
from ..agents.risk_mgmt.neutral_debator import NeutralDebator
from ..agents.managers.risk_manager import RiskManager
from ..agents.utils.memory import MemoryManager
from ..dataflows.interface import DataInterface
from ..config.default_config import WORKFLOW_CONFIG

logger = logging.getLogger(__name__)

class AnalysisDepth(Enum):
    """分析深度枚举"""
    SHALLOW = "shallow"
    MEDIUM = "medium"
    DEEP = "deep"

class TradingGraph:
    """交易工作流图 - 核心协调器"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.memory_manager = MemoryManager()
        self.data_interface = DataInterface()
        self.workflow_config = WORKFLOW_CONFIG
        
        # 初始化所有智能体
        self._initialize_agents()
        
        # 工作流状态
        self.current_analysis = None
        self.analysis_history = []
    
    def _initialize_agents(self):
        """初始化所有智能体"""
        # 分析师团队
        self.market_analyst = MarketAnalyst(self.llm_client, self.memory_manager)
        self.social_media_analyst = SocialMediaAnalyst(self.llm_client, self.memory_manager)
        self.news_analyst = NewsAnalyst(self.llm_client, self.memory_manager)
        self.fundamentals_analyst = FundamentalsAnalyst(self.llm_client, self.memory_manager)
        
        # 研究团队
        self.bull_researcher = BullResearcher(self.llm_client, self.memory_manager)
        self.bear_researcher = BearResearcher(self.llm_client, self.memory_manager)
        self.research_manager = ResearchManager(self.llm_client, self.memory_manager)
        
        # 交易团队
        self.trader = Trader(self.llm_client, self.memory_manager)
        
        # 风险管理团队
        self.aggressive_debator = AggressiveDebator(self.llm_client, self.memory_manager)
        self.conservative_debator = ConservativeDebator(self.llm_client, self.memory_manager)
        self.neutral_debator = NeutralDebator(self.llm_client, self.memory_manager)
        self.risk_manager = RiskManager(self.llm_client, self.memory_manager)
        
        logger.info("所有智能体初始化完成")
    
    async def analyze_stock(self, symbol: str, depth: AnalysisDepth = AnalysisDepth.MEDIUM) -> Dict[str, Any]:
        """
        执行完整的股票分析流程
        
        Args:
            symbol: 股票代码
            depth: 分析深度
            
        Returns:
            完整的分析结果
        """
        try:
            logger.info(f"开始分析股票 {symbol}，深度: {depth.value}")
            
            # 初始化记忆系统
            await self.memory_manager.initialize()
            
            # 创建分析会话
            analysis_session = {
                "symbol": symbol,
                "depth": depth.value,
                "start_time": datetime.now().isoformat(),
                "status": "running",
                "results": {}
            }
            self.current_analysis = analysis_session
            
            # 第一阶段：数据收集
            logger.info("第一阶段：数据收集")
            market_data = await self._collect_market_data(symbol)
            analysis_session["results"]["market_data"] = market_data
            
            # 第二阶段：分析师团队分析
            logger.info("第二阶段：分析师团队分析")
            analyst_reports = await self._run_analyst_team(symbol, market_data)
            analysis_session["results"]["analyst_reports"] = analyst_reports
            
            # 第三阶段：研究团队辩论
            logger.info("第三阶段：研究团队辩论")
            research_results = await self._run_research_debate(symbol, analyst_reports, depth)
            analysis_session["results"]["research_results"] = research_results
            
            # 第四阶段：交易策略制定
            logger.info("第四阶段：交易策略制定")
            trading_strategy = await self._develop_trading_strategy(symbol, research_results, market_data)
            analysis_session["results"]["trading_strategy"] = trading_strategy
            
            # 第五阶段：风险管理评估
            logger.info("第五阶段：风险管理评估")
            final_decision = await self._risk_management_evaluation(symbol, trading_strategy, research_results)
            analysis_session["results"]["final_decision"] = final_decision
            
            # 完成分析
            analysis_session["status"] = "completed"
            analysis_session["end_time"] = datetime.now().isoformat()
            
            # 保存到历史记录
            self.analysis_history.append(analysis_session)
            
            logger.info(f"股票 {symbol} 分析完成")
            return analysis_session
            
        except Exception as e:
            logger.error(f"股票分析失败: {e}")
            if self.current_analysis:
                self.current_analysis["status"] = "failed"
                self.current_analysis["error"] = str(e)
                self.current_analysis["end_time"] = datetime.now().isoformat()
            
            return {
                "symbol": symbol,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _collect_market_data(self, symbol: str) -> Dict[str, Any]:
        """收集市场数据"""
        try:
            # 获取综合数据
            comprehensive_data = await self.data_interface.get_comprehensive_data(symbol)
            
            # 获取市场概览
            market_overview = await self.data_interface.get_market_overview()
            
            return {
                "symbol": symbol,
                "comprehensive_data": comprehensive_data,
                "market_overview": market_overview,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"数据收集失败: {e}")
            return {"error": str(e)}
    
    async def _run_analyst_team(self, symbol: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """运行分析师团队"""
        try:
            comprehensive_data = market_data.get("comprehensive_data", {})
            
            # 准备分析师输入数据
            analyst_input = {
                "symbol": symbol,
                "price_data": comprehensive_data.get("price_data", {}),
                "technical_indicators": comprehensive_data.get("technical_indicators", {}),
                "financial_data": comprehensive_data.get("financial_data", {}),
                "news_data": comprehensive_data.get("news_data", []),
                "sentiment_data": comprehensive_data.get("sentiment_data", {}),
                "social_data": comprehensive_data.get("sentiment_data", {}),
                "macro_events": []  # 可以扩展添加宏观事件
            }
            
            # 并行运行所有分析师
            tasks = [
                self.market_analyst.process_with_memory(analyst_input, {"analysis_type": "technical"}),
                self.social_media_analyst.process_with_memory(analyst_input, {"analysis_type": "sentiment"}),
                self.news_analyst.process_with_memory(analyst_input, {"analysis_type": "news"}),
                self.fundamentals_analyst.process_with_memory(analyst_input, {"analysis_type": "fundamentals"})
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return {
                "market_analysis": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
                "sentiment_analysis": results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])},
                "news_analysis": results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])},
                "fundamentals_analysis": results[3] if not isinstance(results[3], Exception) else {"error": str(results[3])},
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"分析师团队运行失败: {e}")
            return {"error": str(e)}
    
    async def _run_research_debate(self, symbol: str, analyst_reports: Dict[str, Any], depth: AnalysisDepth) -> Dict[str, Any]:
        """运行研究团队辩论"""
        try:
            # 准备研究输入数据
            research_input = {
                "symbol": symbol,
                "analyst_reports": [
                    analyst_reports.get("market_analysis", {}),
                    analyst_reports.get("sentiment_analysis", {}),
                    analyst_reports.get("news_analysis", {}),
                    analyst_reports.get("fundamentals_analysis", {})
                ],
                "market_data": {}  # 可以添加额外的市场数据
            }
            
            # 初始研究
            bull_research_task = self.bull_researcher.process_with_memory(research_input, {"position": "bull"})
            bear_research_task = self.bear_researcher.process_with_memory(research_input, {"position": "bear"})
            
            bull_research, bear_research = await asyncio.gather(bull_research_task, bear_research_task)
            
            # 根据深度进行辩论
            debate_rounds = self.workflow_config["debate_rounds"][depth.value]
            debate_results = []
            
            for round_num in range(debate_rounds):
                logger.info(f"辩论第 {round_num + 1} 轮")
                
                # 多头反驳空头
                bull_response = await self.bull_researcher.participate_debate(
                    round_num + 1,
                    bear_research.get("content", {}).get("key_risks", []),
                    {"symbol": symbol}
                )
                
                # 空头反驳多头
                bear_response = await self.bear_researcher.participate_debate(
                    round_num + 1,
                    bull_research.get("content", {}).get("key_arguments", []),
                    {"symbol": symbol}
                )
                
                debate_results.append({
                    "round": round_num + 1,
                    "bull_response": bull_response,
                    "bear_response": bear_response
                })
            
            # 研究经理做出投资建议
            manager_input = {
                "symbol": symbol,
                "bull_research": bull_research.get("content", {}),
                "bear_research": bear_research.get("content", {}),
                "debate_results": debate_results
            }
            
            investment_recommendation = await self.research_manager.process_with_memory(
                manager_input, {"analysis_type": "investment_recommendation"}
            )
            
            return {
                "bull_research": bull_research,
                "bear_research": bear_research,
                "debate_results": debate_results,
                "investment_recommendation": investment_recommendation,
                "debate_rounds": debate_rounds,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"研究辩论失败: {e}")
            return {"error": str(e)}
    
    async def _develop_trading_strategy(self, symbol: str, research_results: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """制定交易策略"""
        try:
            # 准备交易员输入数据
            trader_input = {
                "symbol": symbol,
                "research_recommendation": research_results.get("investment_recommendation", {}).get("content", {}),
                "market_data": market_data.get("comprehensive_data", {}).get("price_data", {}),
                "portfolio_context": {
                    "available_cash": "1000000",  # 可配置
                    "current_positions": {},
                    "risk_exposure": "medium",
                    "concentration": "low"
                }
            }
            
            trading_strategy = await self.trader.process_with_memory(
                trader_input, {"analysis_type": "trading_strategy"}
            )
            
            return trading_strategy
            
        except Exception as e:
            logger.error(f"交易策略制定失败: {e}")
            return {"error": str(e)}
    
    async def _risk_management_evaluation(self, symbol: str, trading_strategy: Dict[str, Any], research_results: Dict[str, Any]) -> Dict[str, Any]:
        """风险管理评估"""
        try:
            # 准备风险分析输入数据
            risk_input = {
                "symbol": symbol,
                "trading_strategy": trading_strategy.get("content", {}),
                "market_conditions": {
                    "market_trend": "neutral",
                    "volatility": "medium",
                    "liquidity": "high",
                    "sentiment": "neutral"
                }
            }
            
            # 并行运行三个风险分析师
            aggressive_task = self.aggressive_debator.process_with_memory(risk_input, {"stance": "aggressive"})
            conservative_task = self.conservative_debator.process_with_memory(risk_input, {"stance": "conservative"})
            neutral_task = self.neutral_debator.process_with_memory(risk_input, {"stance": "neutral"})
            
            aggressive_analysis, conservative_analysis, neutral_analysis = await asyncio.gather(
                aggressive_task, conservative_task, neutral_task
            )
            
            # 风险经理做出最终决策
            risk_manager_input = {
                "symbol": symbol,
                "trading_strategy": trading_strategy.get("content", {}),
                "aggressive_analysis": aggressive_analysis.get("content", {}),
                "conservative_analysis": conservative_analysis.get("content", {}),
                "neutral_analysis": neutral_analysis.get("content", {}),
                "research_recommendation": research_results.get("investment_recommendation", {}).get("content", {})
            }
            
            final_decision = await self.risk_manager.process_with_memory(
                risk_manager_input, {"analysis_type": "final_decision"}
            )
            
            return {
                "aggressive_analysis": aggressive_analysis,
                "conservative_analysis": conservative_analysis,
                "neutral_analysis": neutral_analysis,
                "final_decision": final_decision,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"风险管理评估失败: {e}")
            return {"error": str(e)}
    
    def get_analysis_status(self) -> Dict[str, Any]:
        """获取当前分析状态"""
        if self.current_analysis:
            return {
                "current_analysis": self.current_analysis,
                "total_analyses": len(self.analysis_history),
                "memory_status": self.memory_manager.get_status() if self.memory_manager else {}
            }
        else:
            return {
                "current_analysis": None,
                "total_analyses": len(self.analysis_history),
                "memory_status": self.memory_manager.get_status() if self.memory_manager else {}
            }
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取分析历史"""
        return self.analysis_history[-limit:] if self.analysis_history else []
    
    async def cleanup(self):
        """清理资源"""
        try:
            if self.memory_manager:
                await self.memory_manager.clear_memories()
            logger.info("TradingGraph资源清理完成")
        except Exception as e:
            logger.error(f"资源清理失败: {e}")
