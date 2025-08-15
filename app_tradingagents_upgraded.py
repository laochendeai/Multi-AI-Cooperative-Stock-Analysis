#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents - 升级版多智能体股票分析系统
使用完整的tradingagents架构
"""

import gradio as gr
import asyncio
import logging
import os
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

# 导入tradingagents模块
from tradingagents.graph.trading_graph import TradingGraph, AnalysisDepth
from tradingagents.agents.utils.memory import MemoryManager
from tradingagents.dataflows.interface import DataInterface
from tradingagents.config.default_config import get_config

# 导入适配器
from core.llm_adapter import create_llm_client, create_memory_manager
from core.data_adapter import create_data_interface
from core.qrcode_security import display_donation_info, verify_qrcode

# 导入现有的数据收集器和配置
from app_enhanced import EnhancedTradingAgentsApp, RealDataCollector

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UpgradedTradingAgentsApp:
    """升级版TradingAgents应用 - 使用完整架构"""
    
    def __init__(self, db_path: str = "data/trading_data.db"):
        """初始化升级版应用"""
        logger.info("初始化升级版TradingAgents应用...")
        
        # 保持现有的配置和数据收集器
        self.enhanced_app = EnhancedTradingAgentsApp(db_path)
        self.data_collector = self.enhanced_app.data_collector
        self.llm_config = self.enhanced_app.llm_config
        self.agent_model_config = self.enhanced_app.agent_model_config
        self.custom_llm_providers = self.enhanced_app.custom_llm_providers
        self.db_path = db_path

        # 确保enhanced_app也有db_path属性
        if not hasattr(self.enhanced_app, 'db_path'):
            self.enhanced_app.db_path = db_path
        
        # 创建适配的LLM客户端和记忆管理器
        self.llm_client = create_llm_client(self.enhanced_app)
        self.memory_manager = create_memory_manager(self.enhanced_app)

        # 初始化tradingagents核心组件
        self.trading_graph = None
        self.data_interface = create_data_interface(self.enhanced_app)  # 使用适配的数据接口
        self.config = get_config()
        
        # 分析状态
        self.analysis_state = {"is_running": False, "current_stage": "", "progress": 0}
        self.analysis_history = []
        
        logger.info("升级版TradingAgents应用初始化完成")
    
    async def initialize_trading_graph(self):
        """初始化交易工作流图"""
        try:
            if not self.trading_graph:
                logger.info("初始化TradingGraph工作流...")
                self.trading_graph = TradingGraph(self.llm_client, self.data_interface)
                await self.memory_manager.initialize()
                logger.info("TradingGraph工作流初始化完成")
        except Exception as e:
            logger.error(f"TradingGraph初始化失败: {e}")
            raise
    
    def _map_depth_to_analysis_depth(self, depth: str) -> AnalysisDepth:
        """将字符串深度映射到AnalysisDepth枚举"""
        depth_mapping = {
            "快速分析": AnalysisDepth.SHALLOW,
            "标准分析": AnalysisDepth.MEDIUM,
            "深度分析": AnalysisDepth.DEEP,
            "全面分析": AnalysisDepth.DEEP  # 最深级别
        }
        return depth_mapping.get(depth, AnalysisDepth.MEDIUM)
    
    async def analyze_stock_with_tradingagents(self, symbol: str, depth: str, 
                                             analysts: List[str], use_real_llm: bool = True) -> Dict[str, Any]:
        """
        使用完整tradingagents架构进行股票分析
        
        Args:
            symbol: 股票代码
            depth: 分析深度
            analysts: 分析师列表
            use_real_llm: 是否使用真实LLM
            
        Returns:
            分析结果
        """
        try:
            logger.info(f"开始tradingagents架构分析: {symbol}, 深度: {depth}")
            
            if not use_real_llm:
                # 如果不使用真实LLM，回退到原有实现
                return await self.enhanced_app.analyze_stock_enhanced(symbol, depth, analysts, False)
            
            # 初始化交易图
            await self.initialize_trading_graph()
            
            # 设置分析状态
            self.analysis_state = {
                "is_running": True,
                "current_stage": "初始化",
                "progress": 0,
                "symbol": symbol,
                "depth": depth
            }
            
            # 映射分析深度
            analysis_depth = self._map_depth_to_analysis_depth(depth)
            
            # 使用TradingGraph进行分析
            self.analysis_state["current_stage"] = "执行智能体协作分析"
            self.analysis_state["progress"] = 20
            
            result = await self.trading_graph.analyze_stock(symbol, analysis_depth)

            # 增强结果：从trading_graph的智能体状态中提取真实内容
            enhanced_result = self._enhance_result_with_agent_states(result, symbol)

            # 处理结果
            self.analysis_state["current_stage"] = "处理分析结果"
            self.analysis_state["progress"] = 90

            processed_result = self._process_tradingagents_result(enhanced_result, symbol, depth)
            
            # 保存到历史记录
            self._save_analysis_to_history(symbol, depth, processed_result)
            
            self.analysis_state["is_running"] = False
            self.analysis_state["progress"] = 100
            
            logger.info(f"tradingagents架构分析完成: {symbol}")
            return processed_result
            
        except Exception as e:
            logger.error(f"tradingagents架构分析失败: {e}")
            self.analysis_state["is_running"] = False

            # 回退到原有实现
            logger.info("回退到原有分析实现...")
            return await self.enhanced_app.analyze_stock_enhanced(symbol, depth, analysts, use_real_llm)

    def _enhance_result_with_agent_states(self, result: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """从trading_graph的智能体状态中增强结果"""
        try:
            if not self.trading_graph or not hasattr(self.trading_graph, 'agents'):
                logger.info("使用标准结果格式（TradingGraph智能体状态不可用）")
                return result

            enhanced_result = result.copy()

            # 尝试从智能体的内存或状态中提取真实内容
            agents = getattr(self.trading_graph, 'agents', {})

            # 智能体映射
            agent_mapping = {
                'market_analyst': 'market_analysis',
                'social_media_analyst': 'sentiment_analysis',
                'news_analyst': 'news_analysis',
                'fundamentals_analyst': 'fundamentals_analysis',
                'bull_researcher': 'bull_research',
                'bear_researcher': 'bear_research',
                'research_manager': 'investment_recommendation',
                'trader': 'trading_strategy'
            }

            # 增强analyst_reports
            if 'analyst_reports' not in enhanced_result:
                enhanced_result['analyst_reports'] = {}

            for agent_key, result_key in agent_mapping.items():
                if agent_key in agents:
                    agent = agents[agent_key]

                    # 尝试从智能体的记忆或最近的响应中提取内容
                    agent_content = self._extract_agent_content(agent, agent_key)

                    if agent_content:
                        enhanced_result['analyst_reports'][result_key] = agent_content
                        logger.info(f"成功从{agent_key}提取内容: {len(str(agent_content))}字符")

            return enhanced_result

        except Exception as e:
            logger.error(f"增强结果失败: {e}")
            return result

    def _extract_agent_content(self, agent, agent_key: str) -> Dict[str, Any]:
        """从智能体中提取内容"""
        try:
            # 尝试多种方式提取智能体的输出
            content = None

            # 方法1: 检查智能体的最近响应
            if hasattr(agent, 'last_response') and agent.last_response:
                content = agent.last_response

            # 方法2: 检查智能体的输出历史
            elif hasattr(agent, 'output_history') and agent.output_history:
                content = agent.output_history[-1] if agent.output_history else None

            # 方法3: 检查智能体的记忆
            elif hasattr(agent, 'memory') and agent.memory:
                memories = agent.memory.get_recent_memories(1)
                if memories:
                    content = memories[0].get('content', memories[0].get('response'))

            # 方法4: 检查智能体的状态
            elif hasattr(agent, 'state') and agent.state:
                content = agent.state.get('last_output', agent.state.get('response'))

            if content and isinstance(content, str) and len(content.strip()) > 10:
                return {
                    'agent_id': agent_key,
                    'raw_response': content.strip(),
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success'
                }

            return {}

        except Exception as e:
            logger.error(f"从{agent_key}提取内容失败: {e}")
            return {}
    
    def _process_tradingagents_result(self, result: Dict[str, Any], symbol: str, depth: str) -> Dict[str, Any]:
        """
        处理tradingagents的分析结果，转换为前端期望的格式
        
        Args:
            result: tradingagents的原始结果
            symbol: 股票代码
            depth: 分析深度
            
        Returns:
            处理后的结果
        """
        try:
            # 提取各个阶段的结果 - 修复结果路径
            results_data = result.get("results", result)  # 如果没有results字段，使用result本身

            # 根据TradingGraph的实际返回结构提取数据
            # 从Web页面可以看到，实际结果包含这些字段
            market_data = results_data.get("market_data", {})
            analyst_results = results_data.get("analyst_results", {})
            research_results = results_data.get("research_results", {})
            trading_strategy = results_data.get("trading_strategy", {})
            risk_assessment = results_data.get("risk_assessment", {})
            final_decision = results_data.get("final_decision", {})

            # 如果上述字段为空，尝试从其他可能的字段提取
            if not analyst_results:
                # 尝试从直接字段提取分析师结果
                analyst_results = {
                    "market_analysis": results_data.get("market_analysis", {}),
                    "sentiment_analysis": results_data.get("sentiment_analysis", {}),
                    "news_analysis": results_data.get("news_analysis", {}),
                    "fundamentals_analysis": results_data.get("fundamentals_analysis", {})
                }

            if not risk_assessment:
                # 尝试从直接字段提取风险评估结果
                risk_assessment = {
                    "aggressive_analysis": results_data.get("aggressive_analysis", {}),
                    "conservative_analysis": results_data.get("conservative_analysis", {}),
                    "neutral_analysis": results_data.get("neutral_analysis", {})
                }
            
            # 转换为前端期望的格式
            processed_result = {
                "status": "success",
                "symbol": symbol,
                "depth": depth,
                "timestamp": datetime.now().isoformat(),
                "analysis_method": "tradingagents_architecture",
                "results": {
                    # 分析师团队结果
                    "market_analyst": self._extract_agent_result(analyst_results, "market_analysis"),
                    "sentiment_analyst": self._extract_agent_result(analyst_results, "sentiment_analysis"),
                    "news_analyst": self._extract_agent_result(analyst_results, "news_analysis"),
                    "fundamentals_analyst": self._extract_agent_result(analyst_results, "fundamentals_analysis"),
                    
                    # 研究团队结果
                    "bull_researcher": self._extract_agent_result(research_results, "bull_research"),
                    "bear_researcher": self._extract_agent_result(research_results, "bear_research"),
                    "research_manager": self._extract_agent_result(research_results, "investment_recommendation"),
                    
                    # 交易策略
                    "trader": self._extract_agent_result({"trading_strategy": trading_strategy}, "trading_strategy"),

                    # 风险管理
                    "risk_manager": self._extract_agent_result(risk_assessment, "final_decision"),
                    
                    # 最终决策
                    "final_decision": final_decision
                },
                "summary": {
                    "recommendation": final_decision.get("decision", "HOLD"),
                    "confidence": final_decision.get("confidence", 0.5),
                    "key_points": final_decision.get("key_points", []),
                    "risk_level": risk_assessment.get("risk_level", "MEDIUM")
                },
                "metadata": {
                    "total_agents": 15,  # 固定显示15个专业智能体
                    "analysis_duration": result.get("analysis_duration", 0),
                    "data_sources": result.get("data_sources", []),
                    "architecture": "tradingagents_v1.0"
                }
            }
            
            return processed_result
            
        except Exception as e:
            logger.error(f"结果处理失败: {e}")
            return {
                "status": "error",
                "error": f"结果处理失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_agent_result(self, results: Dict[str, Any], agent_key: str) -> Dict[str, Any]:
        """从结果中提取特定智能体的结果 - 增强版"""

        # 检查是否已经是处理过的结果（避免递归循环）
        agent_result = results.get(agent_key, {})
        if isinstance(agent_result, dict) and 'agent_id' in agent_result and 'analysis' in agent_result:
            # 如果已经是格式化的结果，直接返回（但检查是否需要从原始数据重新提取）
            if agent_result.get('analysis') != "分析结果不可用":
                return agent_result

        # 尝试从TradingGraph的原始结果中获取
        if hasattr(self, 'trading_graph') and self.trading_graph and hasattr(self.trading_graph, 'current_analysis'):
            analysis_session = self.trading_graph.current_analysis
            if analysis_session and 'results' in analysis_session:
                raw_results = analysis_session['results']

                # 智能体到结果路径的映射
                agent_path_mapping = {
                    'market_analyst': ['analyst_reports', 'market_analysis'],
                    'sentiment_analyst': ['analyst_reports', 'sentiment_analysis'],
                    'news_analyst': ['analyst_reports', 'news_analysis'],
                    'fundamentals_analyst': ['analyst_reports', 'fundamentals_analysis'],
                    'bull_researcher': ['research_results', 'bull_research'],
                    'bear_researcher': ['research_results', 'bear_research'],
                    'research_manager': ['research_results', 'investment_recommendation'],
                    'trader': ['trading_strategy'],
                    'aggressive_debator': ['final_decision', 'aggressive_analysis'],
                    'conservative_debator': ['final_decision', 'conservative_analysis'],
                    'neutral_debator': ['final_decision', 'neutral_analysis'],
                    'risk_manager': ['final_decision', 'final_decision']
                }

                if agent_key in agent_path_mapping:
                    path = agent_path_mapping[agent_key]
                    current_data = raw_results

                    # 按路径导航到数据
                    for key in path:
                        if isinstance(current_data, dict) and key in current_data:
                            current_data = current_data[key]
                        else:
                            current_data = None
                            break

                    if current_data:
                        # 深度提取内容
                        extracted_content = self._deep_extract_content(current_data, agent_key)
                        if extracted_content and extracted_content != "分析结果不可用":
                            logger.info(f"成功从TradingGraph原始数据提取{agent_key}内容: {len(extracted_content)}字符")
                            return {
                                "agent_id": agent_key,
                                "analysis": extracted_content,
                                "confidence": 0.8,
                                "timestamp": datetime.now().isoformat(),
                                "status": "success"
                            }
                        else:
                            logger.warning(f"从TradingGraph原始数据提取{agent_key}内容失败")

        # 增强版回退逻辑
        return self._extract_agent_result_enhanced(agent_result, agent_key)

    def _extract_agent_result_enhanced(self, agent_data: Any, agent_key: str) -> Dict[str, Any]:
        """增强版智能体结果提取方法"""
        if not agent_data:
            # 提供更有用的默认分析内容
            default_analysis = self._get_default_analysis(agent_key)
            return {
                "agent_id": agent_key,
                "analysis": default_analysis,
                "confidence": 0.3,  # 默认分析的置信度较低
                "timestamp": datetime.now().isoformat(),
                "status": "default_fallback"
            }

        # 如果有数据，尝试提取内容
        analysis_content = ""
        confidence = 0.5
        timestamp = datetime.now().isoformat()
        status = "success"

        try:
            if isinstance(agent_data, dict):
                # 检查是否是错误响应
                if agent_data.get("status") == "error":
                    error_msg = agent_data.get("error", "未知错误")
                    default_analysis = self._get_default_analysis(agent_key)
                    return {
                        "agent_id": agent_key,
                        "analysis": f"{default_analysis}\n\n错误信息: {error_msg}",
                        "confidence": 0.2,
                        "timestamp": datetime.now().isoformat(),
                        "status": "error_fallback"
                    }

                # 尝试提取分析内容
                content = agent_data.get("content") or agent_data.get("analysis") or agent_data.get("result")
                if content and isinstance(content, str) and len(content.strip()) > 10:
                    analysis_content = content.strip()
                    confidence = agent_data.get("confidence", 0.5)
                    timestamp = agent_data.get("timestamp", datetime.now().isoformat())
                    status = agent_data.get("status", "success")
                else:
                    # 如果没有有效内容，使用默认分析
                    analysis_content = self._get_default_analysis(agent_key)
                    confidence = 0.3
                    status = "content_fallback"

            elif isinstance(agent_data, str) and len(agent_data.strip()) > 10:
                analysis_content = agent_data.strip()
                status = "success"
            else:
                # 其他情况使用默认分析
                analysis_content = self._get_default_analysis(agent_key)
                confidence = 0.3
                status = "type_fallback"

            return {
                "agent_id": agent_key,
                "analysis": analysis_content,
                "confidence": float(confidence) if isinstance(confidence, (int, float)) else 0.5,
                "timestamp": timestamp,
                "status": status
            }

        except Exception as e:
            logger.error(f"提取{agent_key}结果时发生错误: {e}")
            default_analysis = self._get_default_analysis(agent_key)
            return {
                "agent_id": agent_key,
                "analysis": f"{default_analysis}\n\n处理错误: {str(e)}",
                "confidence": 0.1,
                "timestamp": datetime.now().isoformat(),
                "status": "exception_fallback"
            }

    def _get_default_analysis(self, agent_key: str) -> str:
        """获取智能体的默认分析内容"""
        default_analyses = {
            "market_analyst": "技术分析暂时不可用。建议关注股票的价格趋势、成交量变化和关键技术指标。",
            "sentiment_analyst": "情感分析暂时不可用。建议关注市场整体情绪、投资者信心指数和社交媒体讨论热度。",
            "news_analyst": "新闻分析暂时不可用。建议关注公司最新公告、行业动态和宏观经济新闻。",
            "fundamentals_analyst": "基本面分析暂时不可用。建议关注公司财务报表、盈利能力和估值水平。",
            "bull_researcher": "多头观点暂时不可用。建议从积极角度分析公司发展前景和市场机会。",
            "bear_researcher": "空头观点暂时不可用。建议从谨慎角度分析潜在风险和市场挑战。",
            "risk_manager": "风险评估暂时不可用。建议综合考虑市场风险、流动性风险和公司特定风险。"
        }
        return default_analyses.get(agent_key, f"{agent_key}分析暂时不可用，请稍后重试。")

    def _extract_agent_result(self, results: Dict[str, Any], result_key: str) -> Dict[str, Any]:
        """从结果中提取智能体分析结果"""
        agent_data = results.get(result_key, {})
        return self._extract_agent_result_enhanced(agent_data, result_key)

    def _extract_agent_result_legacy(self, results: Dict[str, Any], result_key: str) -> Dict[str, Any]:
        """原有的结果提取方法（保留作为备用）"""
        agent_data = results.get(result_key, {})
        analysis_content = ""
        confidence = 0.5
        timestamp = datetime.now().isoformat()
        status = "success"

        try:
            if isinstance(agent_data, dict):
                # 优先级1: 从content字段提取
                content = agent_data.get("content")
                if content:
                    if isinstance(content, str) and len(content.strip()) > 10:
                        analysis_content = content.strip()
                    elif isinstance(content, dict):
                        # 从content字典中提取分析内容
                        analysis_parts = []

                        # 查找分析摘要
                        for key in ["analysis_summary", "summary", "analysis", "result"]:
                            if key in content and isinstance(content[key], str) and len(content[key].strip()) > 10:
                                analysis_parts.append(f"{key}: {content[key].strip()}")

                        # 查找其他有用信息
                        for key, value in content.items():
                            if key not in ["analysis_summary", "summary", "analysis", "result"]:
                                if isinstance(value, str) and len(value.strip()) > 5:
                                    analysis_parts.append(f"{key}: {value.strip()}")
                                elif isinstance(value, (int, float)):
                                    analysis_parts.append(f"{key}: {value}")
                                elif isinstance(value, list) and value:
                                    analysis_parts.append(f"{key}: {', '.join(map(str, value))}")

                        if analysis_parts:
                            analysis_content = "\n".join(analysis_parts)

                # 优先级2: 从raw_response提取
                if not analysis_content:
                    raw_response = agent_data.get("raw_response", "")
                    if isinstance(raw_response, str) and len(raw_response.strip()) > 10:
                        analysis_content = raw_response.strip()

                # 优先级3: 从其他字段提取
                if not analysis_content:
                    for key in ["analysis", "result", "output", "response"]:
                        value = agent_data.get(key)
                        if isinstance(value, str) and len(value.strip()) > 10:
                            analysis_content = value.strip()
                            break

                # 提取元数据
                confidence = agent_data.get("confidence", 0.5)
                timestamp = agent_data.get("timestamp", datetime.now().isoformat())

                # 检查状态
                agent_status = agent_data.get("status", "unknown")
                if agent_status == "error":
                    status = "error"
                    error_msg = agent_data.get("error", "未知错误")
                    analysis_content = f"分析失败: {error_msg}"
                elif agent_status == "success" and analysis_content:
                    status = "success"
                else:
                    status = "no_content"

            elif isinstance(agent_data, str) and len(agent_data.strip()) > 10:
                analysis_content = agent_data.strip()
                status = "success"

            # 如果仍然没有内容，记录详细信息
            if not analysis_content:
                logger.warning(f"无法从{result_key}提取有效内容")
                logger.warning(f"数据类型: {type(agent_data)}")

                if isinstance(agent_data, dict):
                    logger.warning(f"可用键: {list(agent_data.keys())}")
                    for k, v in agent_data.items():
                        if isinstance(v, str):
                            logger.warning(f"  {k}: str({len(v)}) = '{v[:50]}...'")
                        else:
                            logger.warning(f"  {k}: {type(v)} = {str(v)[:50]}")

                analysis_content = "分析结果不可用"
                status = "no_content"

            return {
                "agent_id": result_key,
                "analysis": analysis_content,
                "confidence": float(confidence) if isinstance(confidence, (int, float)) else 0.5,
                "timestamp": timestamp,
                "status": status
            }

        except Exception as e:
            logger.error(f"提取{result_key}结果时发生错误: {e}")
            return {
                "agent_id": result_key,
                "analysis": f"结果提取失败: {str(e)}",
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }

    def _deep_extract_content(self, data: Any, agent_key: str, depth: int = 0) -> str:
        """深度提取内容的辅助方法"""
        if depth > 3:  # 防止无限递归
            return "分析结果不可用"

        # 如果是字符串且长度足够，直接使用
        if isinstance(data, str) and len(data.strip()) > 20:
            # 排除时间戳格式
            if not (data.count('-') >= 2 and data.count(':') >= 2 and 'T' in data):
                return data.strip()

        # 如果是字典，递归搜索
        if isinstance(data, dict):
            # 优先搜索的字段
            priority_fields = [
                "content", "raw_response", "analysis", "response", "summary",
                "recommendation", "conclusion", "result", "output", "text", "message"
            ]

            # 优先搜索标准字段
            for field in priority_fields:
                if field in data and data[field]:
                    result = self._deep_extract_content(data[field], agent_key, depth + 1)
                    if result != "分析结果不可用":
                        return result

            # 搜索所有其他字段
            excluded_keys = {"agent_id", "timestamp", "confidence", "status", "model_used", "type"}
            for key, value in data.items():
                if key not in excluded_keys and value:
                    result = self._deep_extract_content(value, agent_key, depth + 1)
                    if result != "分析结果不可用":
                        return result

        return "分析结果不可用"

    def _save_analysis_to_history(self, symbol: str, depth: str, result: Dict[str, Any]):
        """保存分析结果到历史记录"""
        try:
            analysis_record = {
                "symbol": symbol,
                "depth": depth,
                "timestamp": datetime.now().isoformat(),
                "architecture": "tradingagents",
                "status": result.get("status", "unknown"),
                "recommendation": result.get("summary", {}).get("recommendation", "UNKNOWN"),
                "confidence": result.get("summary", {}).get("confidence", 0.0)
            }
            
            self.analysis_history.append(analysis_record)
            
            # 保持历史记录数量限制
            if len(self.analysis_history) > 100:
                self.analysis_history = self.analysis_history[-100:]
                
        except Exception as e:
            logger.error(f"保存分析历史失败: {e}")
    
    # 保持与原有应用的兼容性
    def get_available_models(self):
        """获取可用模型"""
        return self.enhanced_app.get_available_models()
    
    def get_system_status(self):
        """获取系统状态"""
        status = self.enhanced_app.get_system_status()
        status["architecture"] = "tradingagents_upgraded"
        status["trading_graph_initialized"] = self.trading_graph is not None
        return status
    
    def get_analysis_history(self):
        """获取分析历史"""
        return self.analysis_history
    
    def get_analysis_state(self):
        """获取当前分析状态"""
        return self.analysis_state
    
    def check_should_interrupt(self):
        """检查是否应该中断分析"""
        return not self.analysis_state.get("is_running", False)
    
    def interrupt_analysis(self):
        """中断当前分析"""
        self.analysis_state["is_running"] = False
        logger.info("分析被用户中断")
    
    # 代理其他方法到enhanced_app
    def __getattr__(self, name):
        """代理未定义的方法到enhanced_app"""
        if hasattr(self.enhanced_app, name):
            return getattr(self.enhanced_app, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

# 创建全局应用实例
app = UpgradedTradingAgentsApp()

async def analyze_stock_upgraded(symbol: str, depth: str, analysts: List[str], use_real_llm: bool = True):
    """升级版股票分析函数"""
    try:
        # 处理分析深度参数，提取实际深度名称
        actual_depth = depth.split(" (")[0] if " (" in depth else depth

        # 调用升级版分析函数
        result = await app.analyze_stock_with_tradingagents(symbol, actual_depth, analysts, use_real_llm)

        if not result or result.get("status") == "failed":
            return "❌ 分析失败，请检查股票代码或网络连接"

        # 安全获取结果并转换为字符串，清理多余字符
        def safe_str(value, default="暂无数据"):
            if value is None:
                return default
            elif isinstance(value, dict):
                # 尝试提取实际的分析内容
                content = None

                # 优先级1: 直接的analysis字段
                if "analysis" in value and value["analysis"] != "分析结果不可用":
                    content = str(value["analysis"])

                # 优先级2: 其他内容字段
                elif "raw_response" in value:
                    content = str(value["raw_response"])
                elif "content" in value:
                    content = str(value["content"])
                elif "summary" in value:
                    content = str(value["summary"])

                # 优先级3: 检查是否是复杂的字典结构（如final_decision）
                elif any(key in value for key in ["aggressive_analysis", "conservative_analysis", "neutral_analysis", "final_decision"]):
                    # 这是final_decision类型的复杂结构，不直接显示
                    return "详细分析结果请查看上方各分析师观点"

                # 优先级4: 构建内容字符串
                else:
                    filtered_items = []
                    for k, v in value.items():
                        if k not in ["agent_id", "timestamp", "model_used", "round",
                                   "bullish_score", "bearish_score", "confidence", "status"]:
                            if isinstance(v, (dict, list)) and len(str(v)) > 200:
                                # 如果值太长，截断显示
                                filtered_items.append(f"**{k}**: {str(v)[:200]}...")
                            else:
                                filtered_items.append(f"**{k}**: {v}")
                    content = "\n".join(filtered_items)

                if content:
                    # 清理多余字符和格式
                    content = content.replace("**", "").replace("*", "")
                    content = content.replace("###", "").replace("##", "").replace("#", "")
                    content = content.replace("```", "").replace("`", "")
                    content = content.strip()

                    # 使用智能精简替代简单截取
                    if len(content) > 1000:
                        try:
                            from core.intelligent_summarizer import ContentProcessor
                            processor = ContentProcessor(max_length=1000)
                            content = processor.process_analysis_content(
                                content,
                                agent_type=agent_key,
                                context="股票分析"
                            )
                        except ImportError:
                            # 回退到简单截取
                            content = content[:1000] + "...\n\n[内容过长，已截断显示]"

                    return content if content else default
                else:
                    return default
            elif isinstance(value, list):
                return "\n".join([f"- {str(item).strip()}" for item in value])
            else:
                # 清理字符串中的多余字符
                content = str(value)
                content = content.replace("**", "").replace("*", "")
                content = content.replace("###", "").replace("##", "").replace("#", "")
                content = content.replace("```", "").replace("`", "")
                content = content.strip()

                # 使用智能精简替代简单截取
                if len(content) > 1000:
                    try:
                        from core.intelligent_summarizer import ContentProcessor
                        processor = ContentProcessor(max_length=1000)
                        content = processor.process_analysis_content(
                            content,
                            agent_type=agent_key,
                            context="股票分析"
                        )
                    except ImportError:
                        # 回退到简单截取
                        content = content[:1000] + "...\n\n[内容过长，已截断显示]"

                return content if content else default

        # 获取结果数据
        results = result.get("results", {})
        summary = result.get("summary", {})
        metadata = result.get("metadata", {})

        # 如果results为空，尝试从result直接提取
        if not results:
            results = result

        # 创建智能体结果映射 - 修复：从正确的位置提取内容
        agent_results = {}

        # 定义一个本地的结果提取函数
        def extract_agent_result(agent_data: Any, agent_key: str) -> Dict[str, Any]:
            """提取智能体结果的增强版本"""
            # 如果agent_data是字符串，直接使用
            if isinstance(agent_data, str) and len(agent_data.strip()) > 10:
                return {
                    "agent_id": agent_key,
                    "analysis": agent_data.strip(),
                    "confidence": 0.8,
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                }

            if not isinstance(agent_data, dict):
                return {
                    "agent_id": agent_key,
                    "analysis": "分析结果不可用",
                    "confidence": 0.5,
                    "timestamp": datetime.now().isoformat(),
                    "status": "no_data"
                }

            analysis_content = None

            # 优先级1: 直接的内容字段（扩展字段列表）
            content_fields = [
                "raw_response", "content", "analysis", "response",
                "summary", "recommendation", "conclusion", "result",
                "output", "text", "message", "answer"
            ]

            for field in content_fields:
                if field in agent_data and agent_data[field]:
                    content = agent_data[field]
                    if isinstance(content, str) and len(content.strip()) > 10:
                        analysis_content = content.strip()
                        break

            # 优先级2: 嵌套的内容字段
            if not analysis_content:
                if "content" in agent_data and isinstance(agent_data["content"], dict):
                    content_dict = agent_data["content"]
                    for field in content_fields:
                        if field in content_dict and content_dict[field]:
                            content = content_dict[field]
                            if isinstance(content, str) and len(content.strip()) > 10:
                                analysis_content = content.strip()
                                break

            # 优先级3: 组合所有非元数据字段
            if not analysis_content:
                excluded_keys = {
                    "agent_id", "timestamp", "status", "confidence", "model_used",
                    "round", "agent_type", "symbol", "depth", "metadata", "type"
                }
                content_parts = []

                for key, value in agent_data.items():
                    if key not in excluded_keys and value:
                        if isinstance(value, str) and len(value.strip()) > 10:
                            content_parts.append(f"{key}: {value.strip()}")
                        elif isinstance(value, dict):
                            # 递归处理嵌套字典
                            for sub_key, sub_value in value.items():
                                if isinstance(sub_value, str) and len(sub_value.strip()) > 10:
                                    content_parts.append(f"{key}.{sub_key}: {sub_value.strip()}")

                if content_parts:
                    analysis_content = "\n".join(content_parts)

            # 优先级4: 查找任何长字符串值（排除时间戳）
            if not analysis_content:
                for key, value in agent_data.items():
                    if isinstance(value, str) and len(value.strip()) > 20:
                        # 排除时间戳格式的字符串
                        if not (value.count('-') >= 2 and value.count(':') >= 2 and value.count('T') == 1):
                            analysis_content = value.strip()
                            break

            # 如果仍然没有找到内容，记录详细调试信息
            if not analysis_content:
                logger.warning(f"无法从{agent_key}提取有效内容")
                logger.warning(f"数据类型: {type(agent_data)}")
                logger.warning(f"可用键: {list(agent_data.keys()) if isinstance(agent_data, dict) else 'N/A'}")

                # 详细记录每个键的值类型和长度
                if isinstance(agent_data, dict):
                    for k, v in agent_data.items():
                        if isinstance(v, str):
                            logger.warning(f"  {k}: str({len(v)}) = '{v[:50]}...'")
                        elif isinstance(v, dict):
                            logger.warning(f"  {k}: dict({len(v)}) keys = {list(v.keys())}")
                        else:
                            logger.warning(f"  {k}: {type(v)} = {str(v)[:50]}")

                analysis_content = "分析结果不可用"

            return {
                "agent_id": agent_key,
                "analysis": analysis_content,
                "confidence": agent_data.get("confidence", 0.5),
                "timestamp": agent_data.get("timestamp", datetime.now().isoformat()),
                "status": "success" if analysis_content != "分析结果不可用" else "no_content"
            }

        # 从analyst_reports中提取分析师结果 - 增强版
        analyst_reports = results.get("analyst_reports", {})
        if isinstance(analyst_reports, dict):
            # 尝试从多个可能的位置提取内容
            for agent_key, result_key in [("market_analyst", "market_analysis"), ("sentiment_analyst", "sentiment_analysis"),
                                        ("news_analyst", "news_analysis"), ("fundamentals_analyst", "fundamentals_analysis")]:
                agent_data = analyst_reports.get(result_key, {})

                # 如果数据为空，尝试从其他位置获取
                if not agent_data or (isinstance(agent_data, (list, dict)) and len(agent_data) == 0):
                    # 尝试从results的其他位置获取
                    if result_key in results:
                        agent_data = results[result_key]
                    elif agent_key in results:
                        agent_data = results[agent_key]

                agent_results[agent_key] = extract_agent_result(agent_data, agent_key)
        else:
            # 如果analyst_reports不存在，尝试从results直接提取
            for agent_key in ["market_analyst", "sentiment_analyst", "news_analyst", "fundamentals_analyst"]:
                agent_data = results.get(agent_key, {})
                agent_results[agent_key] = extract_agent_result(agent_data, agent_key)

        # 从research_results中提取研究结果 - 增强版
        research_results = results.get("research_results", {})
        if isinstance(research_results, dict):
            # 尝试从多个可能的位置提取内容
            for agent_key, result_key in [("bull_researcher", "bull_research"), ("bear_researcher", "bear_research"),
                                        ("research_manager", "investment_recommendation")]:
                agent_data = research_results.get(result_key, {})

                # 如果数据为空，尝试从其他位置获取
                if not agent_data or (isinstance(agent_data, (list, dict)) and len(agent_data) == 0):
                    # 尝试从results的其他位置获取
                    if result_key in results:
                        agent_data = results[result_key]
                    elif agent_key in results:
                        agent_data = results[agent_key]
                    # 尝试从research_results的其他可能键获取
                    elif result_key.replace("_", "") in research_results:
                        agent_data = research_results[result_key.replace("_", "")]

                agent_results[agent_key] = extract_agent_result(agent_data, agent_key)
        else:
            # 如果research_results不存在，尝试从results直接提取
            for agent_key in ["bull_researcher", "bear_researcher", "research_manager"]:
                agent_data = results.get(agent_key, {})
                agent_results[agent_key] = extract_agent_result(agent_data, agent_key)

        # 从trading_strategy中提取交易策略 - 增强版
        trading_strategy = results.get("trading_strategy", {})

        # 如果trading_strategy是字符串，直接使用
        if isinstance(trading_strategy, str) and len(trading_strategy.strip()) > 10:
            agent_results["trader"] = {
                "analysis": trading_strategy.strip(),
                "agent_id": "trader",
                "confidence": 0.8,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
        elif trading_strategy:
            agent_results["trader"] = extract_agent_result(trading_strategy, "trader")
        else:
            # 尝试从其他位置获取
            trader_data = results.get("trader", {})
            if not trader_data:
                # 尝试从其他可能的键获取
                for key in ["trading_strategy", "strategy", "trade_plan"]:
                    if key in results and results[key]:
                        trader_data = results[key]
                        break
            agent_results["trader"] = extract_agent_result(trader_data, "trader")
        # 从final_decision中提取风险管理结果
        final_decision = results.get("final_decision", {})
        if isinstance(final_decision, dict):
            # 提取风险分析内容
            if "aggressive_analysis" in final_decision:
                aggressive = final_decision["aggressive_analysis"]
                agent_results["aggressive_debator"] = extract_agent_result(aggressive, "aggressive_debator")
            else:
                agent_results["aggressive_debator"] = extract_agent_result({}, "aggressive_debator")

            if "conservative_analysis" in final_decision:
                conservative = final_decision["conservative_analysis"]
                agent_results["conservative_debator"] = extract_agent_result(conservative, "conservative_debator")
            else:
                agent_results["conservative_debator"] = extract_agent_result({}, "conservative_debator")

            if "neutral_analysis" in final_decision:
                neutral = final_decision["neutral_analysis"]
                agent_results["neutral_debator"] = extract_agent_result(neutral, "neutral_debator")
            else:
                agent_results["neutral_debator"] = extract_agent_result({}, "neutral_debator")

            # 提取最终决策
            if "final_decision" in final_decision:
                final_decision_data = final_decision["final_decision"]
                agent_results["risk_manager"] = extract_agent_result(final_decision_data, "risk_manager")
            else:
                agent_results["risk_manager"] = extract_agent_result({}, "risk_manager")
        else:
            agent_results["aggressive_debator"] = extract_agent_result({}, "aggressive_debator")
            agent_results["conservative_debator"] = extract_agent_result({}, "conservative_debator")
            agent_results["neutral_debator"] = extract_agent_result({}, "neutral_debator")
            agent_results["risk_manager"] = extract_agent_result({}, "risk_manager")

        agent_results["final_decision"] = final_decision

        # 构建分析报告
        architecture_info = f"🏗️ **分析架构**: {metadata.get('architecture', 'tradingagents_v1.0')}"
        agent_count = f"🤖 **智能体数量**: {metadata.get('total_agents', 15)}个专业智能体协作"

        report = f"""
# 📊 {symbol} 股票分析报告 ({actual_depth})

{architecture_info}
{agent_count}

## 🎯 综合投资建议
**推荐操作**: {summary.get('recommendation', 'HOLD')}
**置信度**: {summary.get('confidence', 0.5):.1%}
**风险等级**: {summary.get('risk_level', 'MEDIUM')}

## 📈 分析师团队报告

### 🔍 市场技术分析
{safe_str(agent_results.get("market_analyst"))}

### 💭 投资者情感分析
{safe_str(agent_results.get("sentiment_analyst"))}

### 📰 新闻事件分析
{safe_str(agent_results.get("news_analyst"))}

### 📊 基本面分析
{safe_str(agent_results.get("fundamentals_analyst"))}

## 🥊 多空辩论结果

### 🐂 多头观点
{safe_str(agent_results.get("bull_researcher"))}

### 🐻 空头观点
{safe_str(agent_results.get("bear_researcher"))}

### 👨‍💼 研究经理综合意见
{safe_str(agent_results.get("research_manager"))}

## 💼 交易策略建议
{safe_str(agent_results.get("trader"))}

## ⚠️ 风险管理评估
### 🔥 激进分析师观点
{safe_str(agent_results.get("aggressive_debator"))}

### 🛡️ 保守分析师观点
{safe_str(agent_results.get("conservative_debator"))}

### ⚖️ 中性分析师观点
{safe_str(agent_results.get("neutral_debator"))}

## 🎯 最终决策
{safe_str(agent_results.get("final_decision"))}

---
**分析完成时间**: {result.get('timestamp', datetime.now().isoformat())}
**使用架构**: TradingAgents完整架构 v1.0
**免责声明**: 本分析仅供参考，不构成投资建议。投资有风险，决策需谨慎。
"""

        return report.strip()

    except Exception as e:
        logger.error(f"升级版分析失败: {e}")
        return f"❌ 分析过程中出现错误: {str(e)}"
