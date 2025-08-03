"""
TradingAgents 默认配置文件
"""

import os
from typing import Dict, Any

# LLM配置
LLM_CONFIG = {
    # 支持的LLM提供商
    "providers": {
        "deepseek": {
            "api_key_env": "DEEPSEEK_API_KEY",
            "base_url": "https://api.deepseek.com/v1",
            "models": {
                "deep_think": "deepseek-chat",
                "quick_think": "deepseek-chat"
            }
        },
        "openai": {
            "api_key_env": "OPENAI_API_KEY", 
            "base_url": "https://api.openai.com/v1",
            "models": {
                "deep_think": "gpt-4",
                "quick_think": "gpt-3.5-turbo"
            }
        },
        "google": {
            "api_key_env": "GOOGLE_API_KEY",
            "base_url": "https://generativelanguage.googleapis.com/v1",
            "models": {
                "deep_think": "gemini-2.5-pro",
                "quick_think": "gemini-2.0-flash"
            }
        },
        "moonshot": {
            "api_key_env": "MOONSHOT_API_KEY",
            "base_url": "https://api.moonshot.cn/v1",
            "models": {
                "deep_think": "moonshot-v1-32k",
                "quick_think": "moonshot-v1-8k"
            }
        }
    },
    
    # 默认配置
    "default_provider": "deepseek",
    "deep_think_llm": "deepseek-chat",
    "quick_think_llm": "deepseek-chat",
    "max_tokens": 2000,
    "temperature": 0.7
}

# 智能体配置
AGENT_CONFIG = {
    "analysts": {
        "market_analyst": {
            "llm_type": "quick_think",
            "system_prompt": "你是专业的市场技术分析师，擅长技术指标分析和价格走势预测。",
            "tools": ["technical_indicators", "chart_analysis"]
        },
        "social_media_analyst": {
            "llm_type": "quick_think", 
            "system_prompt": "你是专业的社交媒体情感分析师，擅长分析市场情绪和舆情。",
            "tools": ["sentiment_analysis", "social_data"]
        },
        "news_analyst": {
            "llm_type": "quick_think",
            "system_prompt": "你是专业的新闻分析师，擅长分析全球新闻和宏观经济事件。",
            "tools": ["news_analysis", "macro_data"]
        },
        "fundamentals_analyst": {
            "llm_type": "quick_think",
            "system_prompt": "你是专业的基本面分析师，擅长分析公司财务数据和基本面指标。",
            "tools": ["financial_data", "fundamental_analysis"]
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
    
    "risk_debators": {
        "aggressive": {
            "llm_type": "deep_think",
            "system_prompt": "你是激进分析师，倡导高风险高回报的投资策略。",
            "tools": ["risk_analysis"]
        },
        "conservative": {
            "llm_type": "deep_think",
            "system_prompt": "你是保守分析师，强调风险控制和稳健策略。", 
            "tools": ["risk_analysis"]
        },
        "neutral": {
            "llm_type": "deep_think",
            "system_prompt": "你是中性分析师，提供平衡的观点和中庸策略。",
            "tools": ["risk_analysis"]
        }
    }
}

# 数据源配置
DATA_CONFIG = {
    "akshare": {
        "enabled": True,
        "apis": {
            "stock_basic": "stock_info_a_code_name",
            "stock_daily": "stock_zh_a_hist", 
            "stock_indicators": "stock_zh_a_hist_min_em",
            "stock_hot": "stock_hot_rank_wc",
            "stock_sentiment": "stock_comment_em",
            "stock_news": "stock_news_em",
            "stock_financial": "stock_financial_em"
        },
        "cache_duration": 300  # 5分钟缓存
    },
    "yahoo_finance": {
        "enabled": False,
        "apis": {
            "stock_daily": "download",
            "stock_info": "info"
        }
    },
    "network": {
        "timeout": 5,
        "max_retries": 2
    }
}

# 记忆系统配置
MEMORY_CONFIG = {
    "chromadb": {
        "persist_directory": "./data/memory",
        "collection_name": "trading_memory",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
    },
    "max_memories": 1000,
    "similarity_threshold": 0.7
}

# 工作流配置
WORKFLOW_CONFIG = {
    "debate_rounds": {
        "shallow": 1,
        "medium": 3, 
        "deep": 5
    },
    "max_tokens_per_round": {
        "shallow": 500,
        "medium": 1000,
        "deep": 2000
    },
    "enable_strategy_backtrack": {
        "shallow": False,
        "medium": False,
        "deep": True
    }
}

def get_config() -> Dict[str, Any]:
    """获取完整配置"""
    return {
        "llm": LLM_CONFIG,
        "agents": AGENT_CONFIG,
        "data": DATA_CONFIG,
        "memory": MEMORY_CONFIG,
        "workflow": WORKFLOW_CONFIG
    }

def get_api_key(provider: str) -> str:
    """获取API密钥"""
    env_var = LLM_CONFIG["providers"][provider]["api_key_env"]
    return os.getenv(env_var, "")
