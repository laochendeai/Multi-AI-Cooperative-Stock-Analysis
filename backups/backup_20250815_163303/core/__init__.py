"""
TradingAgents核心模块
零知识迁移版本 - 安全多LLM协作系统
"""

from .secure_llm_manager import SecureLLMClient, LLMSlotConfig
from .llm_orchestrator import GradioLLMOrchestrator, CrossLLMStateManager
from .secure_data_manager import DataSourceAuthManager, DataSourceClient

__version__ = "2.0.0-SECURE"
__author__ = "TradingAgents Team"

__all__ = [
    'SecureLLMClient',
    'LLMSlotConfig', 
    'GradioLLMOrchestrator',
    'CrossLLMStateManager',
    'DataSourceAuthManager',
    'DataSourceClient'
]