#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置适配器 - 为tradingagents架构提供配置支持
"""

import os
from typing import Dict, Any

# 默认LLM配置
DEFAULT_LLM_CONFIG = {
    "deep_think_llm": "deepseek:deepseek-chat",
    "quick_think_llm": "deepseek:deepseek-chat",
    "providers": {
        "deepseek": {
            "base_url": "https://api.deepseek.com",
            "models": ["deepseek-chat", "deepseek-coder"]
        },
        "openai": {
            "base_url": "https://api.openai.com/v1",
            "models": ["gpt-4", "gpt-3.5-turbo"]
        },
        "google": {
            "base_url": "https://generativelanguage.googleapis.com/v1beta",
            "models": ["gemini-pro", "gemini-pro-vision"]
        }
    }
}

# 智能体配置
DEFAULT_AGENT_CONFIG = {
    "analysts": {
        "market_analyst": {
            "llm_type": "deep_think",
            "system_prompt": "你是专业的市场技术分析师，擅长分析股票价格走势和技术指标。",
            "tools": ["technical_analysis", "chart_analysis"]
        },
        "social_media_analyst": {
            "llm_type": "quick_think",
            "system_prompt": "你是社交媒体情感分析师，专注于分析投资者情绪和市场情感。",
            "tools": ["sentiment_analysis", "social_monitoring"]
        },
        "news_analyst": {
            "llm_type": "deep_think",
            "system_prompt": "你是新闻分析师，专门分析影响股票的新闻事件和宏观经济因素。",
            "tools": ["news_analysis", "macro_analysis"]
        },
        "fundamentals_analyst": {
            "llm_type": "deep_think",
            "system_prompt": "你是基本面分析师，专注于公司财务数据和基本面指标分析。",
            "tools": ["financial_analysis", "valuation_analysis"]
        }
    },
    "researchers": {
        "bull_researcher": {
            "llm_type": "deep_think",
            "system_prompt": "你是多头研究员，专注于寻找投资机会和看涨理由。",
            "tools": ["research_tools", "memory_system"]
        },
        "bear_researcher": {
            "llm_type": "deep_think", 
            "system_prompt": "你是空头研究员，专注于识别投资风险和看跌因素。",
            "tools": ["research_tools", "memory_system"]
        }
    },
    "managers": {
        "research_manager": {
            "llm_type": "deep_think",
            "system_prompt": "你是研究经理，负责协调多空辩论并做出投资建议。",
            "tools": ["decision_tools", "debate_coordination"]
        },
        "risk_manager": {
            "llm_type": "deep_think",
            "system_prompt": "你是风险经理，负责最终的风险评估和交易决策。",
            "tools": ["risk_assessment", "final_decision"]
        }
    },
    "trader": {
        "llm_type": "deep_think",
        "system_prompt": "你是专业交易员，负责制定具体的交易策略和执行计划。",
        "tools": ["trading_tools", "strategy_planning"]
    },
    "risk_mgmt": {
        "aggressive_debator": {
            "llm_type": "quick_think",
            "system_prompt": "你是激进分析师，倡导高风险高回报的投资策略。",
            "tools": ["risk_analysis"]
        },
        "conservative_debator": {
            "llm_type": "quick_think",
            "system_prompt": "你是保守分析师，强调风险控制和稳健投资。",
            "tools": ["risk_analysis"]
        },
        "neutral_debator": {
            "llm_type": "quick_think",
            "system_prompt": "你是中性分析师，提供平衡的投资观点。",
            "tools": ["risk_analysis"]
        }
    }
}

# 数据配置
DEFAULT_DATA_CONFIG = {
    "sources": {
        "akshare": {
            "enabled": True,
            "cache_ttl": 300  # 5分钟缓存
        },
        "tushare": {
            "enabled": False,
            "api_key": None
        },
        "yahoo_finance": {
            "enabled": True,
            "cache_ttl": 300
        }
    },
    "cache": {
        "enabled": True,
        "storage_path": "data/cache",
        "max_size": "100MB"
    }
}

# 记忆配置
DEFAULT_MEMORY_CONFIG = {
    "storage_path": "data/memory",
    "collection_name": "agent_memories",
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "max_memories": 1000,
    "similarity_threshold": 0.7,
    "use_chromadb": True,  # 启用ChromaDB
    "enable_chromadb": True,  # 启用ChromaDB
    "persist_directory": "data/memory/chromadb",
    "chromadb": {
        "persist_directory": "data/memory/chromadb",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
    }
}

# 工作流配置
DEFAULT_WORKFLOW_CONFIG = {
    "max_concurrent_agents": 5,
    "timeout_seconds": 300,
    "retry_attempts": 3,
    "enable_memory": True,
    "enable_reflection": True,
    "stages": {
        "data_collection": {
            "timeout": 60,
            "required": True
        },
        "analyst_team": {
            "timeout": 120,
            "required": True,
            "parallel": True
        },
        "research_team": {
            "timeout": 180,
            "required": True,
            "depends_on": ["analyst_team"]
        },
        "trading_strategy": {
            "timeout": 90,
            "required": True,
            "depends_on": ["research_team"]
        },
        "risk_assessment": {
            "timeout": 120,
            "required": True,
            "depends_on": ["trading_strategy"]
        }
    }
}

def get_config() -> Dict[str, Any]:
    """获取完整配置"""
    return {
        "llm": DEFAULT_LLM_CONFIG,
        "agents": DEFAULT_AGENT_CONFIG,
        "data": DEFAULT_DATA_CONFIG,
        "memory": DEFAULT_MEMORY_CONFIG,
        "workflow": DEFAULT_WORKFLOW_CONFIG
    }

def get_api_key(provider: str) -> str:
    """获取API密钥"""
    env_key = f"{provider.upper()}_API_KEY"
    return os.getenv(env_key, "")

# 导出配置常量
LLM_CONFIG = DEFAULT_LLM_CONFIG
AGENT_CONFIG = DEFAULT_AGENT_CONFIG
DATA_CONFIG = DEFAULT_DATA_CONFIG
MEMORY_CONFIG = DEFAULT_MEMORY_CONFIG
WORKFLOW_CONFIG = DEFAULT_WORKFLOW_CONFIG

class ConfigAdapter:
    """配置适配器"""
    
    def __init__(self, enhanced_app=None):
        self.enhanced_app = enhanced_app
        self._config = get_config()
    
    def get_agent_config(self, agent_id: str) -> Dict[str, Any]:
        """获取智能体配置"""
        # 从各个类别中查找智能体配置
        for category, agents in self._config["agents"].items():
            if isinstance(agents, dict):
                for agent_name, config in agents.items():
                    if agent_name in agent_id.lower():
                        return config
                # 如果是单个智能体配置
                if category in agent_id.lower():
                    return agents
        
        # 默认配置
        return {
            "llm_type": "quick_think",
            "system_prompt": f"你是{agent_id}智能体。",
            "tools": []
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """获取LLM配置"""
        if self.enhanced_app:
            return {
                "providers": self.enhanced_app.llm_config,
                "agent_models": self.enhanced_app.agent_model_config,
                "custom_providers": self.enhanced_app.custom_llm_providers
            }
        return self._config["llm"]
    
    def get_memory_config(self) -> Dict[str, Any]:
        """获取记忆配置"""
        return self._config["memory"]
    
    def get_workflow_config(self) -> Dict[str, Any]:
        """获取工作流配置"""
        return self._config["workflow"]
