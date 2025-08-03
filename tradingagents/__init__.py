"""
TradingAgents - 多智能体协作股票分析系统
基于专业化LLM智能体的金融交易框架
"""

from .graph.trading_graph import TradingGraph
from .agents.base_agent import BaseAgent
from .dataflows.interface import DataInterface

__version__ = "1.0.0"
__author__ = "TradingAgents Team"

__all__ = [
    'TradingGraph',
    'BaseAgent', 
    'DataInterface'
]
