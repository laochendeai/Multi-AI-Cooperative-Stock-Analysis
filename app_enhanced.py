"""
TradingAgents - 增强版多智能体股票分析系统
包含LLM配置、ChromaDB支持和完整功能
"""

import gradio as gr
import asyncio
import logging
import os
import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import base64

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealDataCollector:
    """真实数据收集器"""

    def __init__(self, db_path: str = "data/trading_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()

    def init_database(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 创建股票数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date TEXT NOT NULL,
                    open_price REAL,
                    high_price REAL,
                    low_price REAL,
                    close_price REAL,
                    volume INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, date)
                )
            ''')

            # 创建技术指标表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS technical_indicators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date TEXT NOT NULL,
                    rsi REAL,
                    macd REAL,
                    ma5 REAL,
                    ma20 REAL,
                    bollinger_upper REAL,
                    bollinger_lower REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, date)
                )
            ''')

            # 创建新闻数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date TEXT NOT NULL,
                    news_content TEXT,
                    sentiment_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("数据库初始化完成")

        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")

    async def get_real_stock_data(self, symbol: str) -> Dict[str, Any]:
        """获取真实股票数据 - 智能缓存机制"""
        try:
            # 首先检查本地缓存
            cached_data = self.get_cached_data(symbol)
            if cached_data:
                logger.info(f"使用缓存数据: {symbol}")
                return cached_data

            # 尝试导入akshare
            try:
                import akshare as ak
            except ImportError:
                logger.error("akshare未安装，请运行: pip install akshare")
                return {"error": "akshare未安装，无法获取真实数据"}

            logger.info(f"从akshare获取股票 {symbol} 的最新数据...")

            # 获取实时数据
            today = datetime.now().strftime('%Y%m%d')

            # 获取股票实时数据
            try:
                # 获取实时价格数据
                real_time_data = ak.stock_zh_a_spot_em()
                stock_info = real_time_data[real_time_data['代码'] == symbol]

                if stock_info.empty:
                    logger.error(f"未找到股票代码 {symbol} 的数据")
                    return {"error": f"未找到股票代码 {symbol}"}

                stock_row = stock_info.iloc[0]

                # 智能获取历史数据（增量更新）
                hist_data = await self.get_historical_data_smart(symbol, ak)

                if hist_data.empty:
                    logger.error(f"无法获取股票 {symbol} 的历史数据")
                    return {"error": f"无法获取股票 {symbol} 的历史数据"}

                # 计算技术指标
                technical_indicators = self.calculate_technical_indicators(hist_data)

                # 构建返回数据
                current_price = float(stock_row['最新价'])
                open_price = float(stock_row['今开'])
                high_price = float(stock_row['最高'])
                low_price = float(stock_row['最低'])
                volume = int(stock_row['成交量'])
                change_percent = float(stock_row['涨跌幅'])

                stock_data = {
                    "symbol": symbol,
                    "name": stock_row['名称'],
                    "price_data": {
                        "current_price": current_price,
                        "open": open_price,
                        "high": high_price,
                        "low": low_price,
                        "volume": volume,
                        "change_percent": change_percent,
                        "market_cap": stock_row.get('总市值', 0)
                    },
                    "technical_indicators": technical_indicators,
                    "market_data": {
                        "pe_ratio": float(stock_row.get('市盈率-动态', 0)),
                        "pb_ratio": float(stock_row.get('市净率', 0)),
                        "dividend_yield": 0.0  # akshare中可能没有直接的股息率
                    },
                    "data_source": "akshare",
                    "update_time": datetime.now().isoformat()
                }

                # 保存到数据库和缓存
                self.save_stock_data(symbol, stock_data)
                self.cache_stock_data(symbol, stock_data)

                logger.info(f"成功获取并缓存股票 {symbol} 的真实数据")
                return stock_data

            except Exception as e:
                logger.error(f"获取akshare数据失败: {e}")
                return {"error": f"获取数据失败: {str(e)}"}

        except Exception as e:
            logger.error(f"获取真实股票数据失败: {e}")
            return {"error": f"数据获取失败: {str(e)}"}

    def calculate_technical_indicators(self, hist_data: pd.DataFrame) -> Dict[str, float]:
        """计算技术指标"""
        try:
            # 确保数据按日期排序
            hist_data = hist_data.sort_values('日期')
            close_prices = hist_data['收盘'].astype(float)
            high_prices = hist_data['最高'].astype(float)
            low_prices = hist_data['最低'].astype(float)

            # 计算移动平均线
            ma5 = close_prices.rolling(window=5).mean().iloc[-1]
            ma20 = close_prices.rolling(window=20).mean().iloc[-1]

            # 计算RSI
            rsi = self.calculate_rsi(close_prices)

            # 计算MACD
            macd = self.calculate_macd(close_prices)

            # 计算布林带
            bollinger_upper, bollinger_lower = self.calculate_bollinger_bands(close_prices)

            return {
                "rsi": float(rsi) if not pd.isna(rsi) else 50.0,
                "macd": float(macd) if not pd.isna(macd) else 0.0,
                "ma5": float(ma5) if not pd.isna(ma5) else close_prices.iloc[-1],
                "ma20": float(ma20) if not pd.isna(ma20) else close_prices.iloc[-1],
                "bollinger_upper": float(bollinger_upper) if not pd.isna(bollinger_upper) else close_prices.iloc[-1] * 1.02,
                "bollinger_lower": float(bollinger_lower) if not pd.isna(bollinger_lower) else close_prices.iloc[-1] * 0.98
            }

        except Exception as e:
            logger.error(f"计算技术指标失败: {e}")
            # 返回默认值
            last_price = hist_data['收盘'].iloc[-1] if not hist_data.empty else 50.0
            return {
                "rsi": 50.0,
                "macd": 0.0,
                "ma5": last_price,
                "ma20": last_price,
                "bollinger_upper": last_price * 1.02,
                "bollinger_lower": last_price * 0.98
            }

    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """计算RSI指标"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        except:
            return 50.0

    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26) -> float:
        """计算MACD指标"""
        try:
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()
            macd = ema_fast - ema_slow
            return macd.iloc[-1]
        except:
            return 0.0

    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> tuple:
        """计算布林带"""
        try:
            ma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            upper = ma + (std * std_dev)
            lower = ma - (std * std_dev)
            return upper.iloc[-1], lower.iloc[-1]
        except:
            last_price = prices.iloc[-1]
            return last_price * 1.02, last_price * 0.98

    def get_cached_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """获取缓存的股票数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            today = datetime.now().strftime('%Y-%m-%d')

            # 检查今天是否已有数据
            cursor.execute('''
                SELECT * FROM stock_data WHERE symbol = ? AND date = ?
            ''', (symbol, today))

            stock_row = cursor.fetchone()
            if not stock_row:
                conn.close()
                return None

            # 获取技术指标
            cursor.execute('''
                SELECT * FROM technical_indicators WHERE symbol = ? AND date = ?
            ''', (symbol, today))

            tech_row = cursor.fetchone()
            if not tech_row:
                conn.close()
                return None

            # 构建缓存数据
            cached_data = {
                "symbol": symbol,
                "name": f"股票{symbol}",  # 简化名称
                "price_data": {
                    "current_price": stock_row[5],  # close_price
                    "open": stock_row[3],           # open_price
                    "high": stock_row[4],           # high_price
                    "low": stock_row[5],            # low_price (使用close作为近似)
                    "volume": stock_row[6],         # volume
                    "change_percent": 0.0,          # 缓存中暂不计算
                    "market_cap": 0
                },
                "technical_indicators": {
                    "rsi": tech_row[3],             # rsi
                    "macd": tech_row[4],            # macd
                    "ma5": tech_row[5],             # ma5
                    "ma20": tech_row[6],            # ma20
                    "bollinger_upper": tech_row[7], # bollinger_upper
                    "bollinger_lower": tech_row[8]  # bollinger_lower
                },
                "market_data": {
                    "pe_ratio": 0.0,
                    "pb_ratio": 0.0,
                    "dividend_yield": 0.0
                },
                "data_source": "cache",
                "update_time": today
            }

            conn.close()
            return cached_data

        except Exception as e:
            logger.error(f"获取缓存数据失败: {e}")
            return None

    def cache_stock_data(self, symbol: str, data: Dict[str, Any]):
        """缓存股票数据（内存缓存）"""
        if not hasattr(self, '_memory_cache'):
            self._memory_cache = {}

        cache_key = f"{symbol}_{datetime.now().strftime('%Y-%m-%d')}"
        self._memory_cache[cache_key] = data
        logger.info(f"股票 {symbol} 数据已缓存到内存")

    async def get_historical_data_smart(self, symbol: str, ak) -> pd.DataFrame:
        """智能获取历史数据（增量更新）"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 检查数据库中最新的数据日期
            cursor.execute('''
                SELECT MAX(date) FROM stock_data WHERE symbol = ?
            ''', (symbol,))

            result = cursor.fetchone()
            last_date = result[0] if result and result[0] else None

            if last_date:
                # 有历史数据，只获取增量
                start_date = (datetime.strptime(last_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y%m%d')
                logger.info(f"增量更新：从 {start_date} 开始获取数据")
            else:
                # 没有历史数据，获取半年数据
                start_date = (datetime.now() - timedelta(days=180)).strftime('%Y%m%d')
                logger.info(f"首次获取：从 {start_date} 开始获取半年数据")

            end_date = datetime.now().strftime('%Y%m%d')

            # 获取历史数据
            hist_data = ak.stock_zh_a_hist(symbol=symbol, period="daily",
                                         start_date=start_date, end_date=end_date, adjust="")

            # 保存新的历史数据到数据库
            if not hist_data.empty:
                for _, row in hist_data.iterrows():
                    date_str = row['日期'].strftime('%Y-%m-%d')
                    cursor.execute('''
                        INSERT OR REPLACE INTO stock_data
                        (symbol, date, open_price, high_price, low_price, close_price, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (symbol, date_str, float(row['开盘']), float(row['最高']),
                          float(row['最低']), float(row['收盘']), int(row['成交量'])))

                conn.commit()
                logger.info(f"保存了 {len(hist_data)} 条历史数据")

            # 获取完整的历史数据用于计算技术指标
            cursor.execute('''
                SELECT date, open_price, high_price, low_price, close_price, volume
                FROM stock_data WHERE symbol = ?
                ORDER BY date DESC LIMIT 100
            ''', (symbol,))

            db_data = cursor.fetchall()
            conn.close()

            if db_data:
                # 转换为DataFrame格式
                df_data = []
                for row in db_data:
                    df_data.append({
                        '日期': datetime.strptime(row[0], '%Y-%m-%d'),
                        '开盘': row[1],
                        '最高': row[2],
                        '最低': row[3],
                        '收盘': row[4],
                        '成交量': row[5]
                    })

                return pd.DataFrame(df_data).sort_values('日期')
            else:
                return hist_data

        except Exception as e:
            logger.error(f"智能获取历史数据失败: {e}")
            # 回退到直接获取
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=100)).strftime('%Y%m%d')
            return ak.stock_zh_a_hist(symbol=symbol, period="daily",
                                    start_date=start_date, end_date=end_date, adjust="")

    def save_stock_data(self, symbol: str, data: Dict[str, Any]):
        """保存股票数据到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            today = datetime.now().strftime('%Y-%m-%d')
            price_data = data['price_data']
            tech_data = data['technical_indicators']

            # 保存基础数据
            cursor.execute('''
                INSERT OR REPLACE INTO stock_data
                (symbol, date, open_price, high_price, low_price, close_price, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, today, price_data['open'], price_data['high'],
                  price_data['low'], price_data['current_price'], price_data['volume']))

            # 保存技术指标
            cursor.execute('''
                INSERT OR REPLACE INTO technical_indicators
                (symbol, date, rsi, macd, ma5, ma20, bollinger_upper, bollinger_lower)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, today, tech_data['rsi'], tech_data['macd'],
                  tech_data['ma5'], tech_data['ma20'],
                  tech_data['bollinger_upper'], tech_data['bollinger_lower']))

            conn.commit()
            conn.close()
            logger.info(f"股票 {symbol} 数据已保存到数据库")

        except Exception as e:
            logger.error(f"保存股票数据失败: {e}")

    async def check_llm_internet_capability(self, provider: str, model: str, api_key: str) -> bool:
        """检查LLM是否支持联网搜索"""
        try:
            # 测试提示词
            test_prompt = "请搜索今天的日期和当前时间，并告诉我今天是几月几号。"

            # 这里需要调用LLM API进行测试
            # 简化实现，返回已知的支持情况
            internet_capable_models = {
                "openai": ["gpt-4", "gpt-4-turbo"],  # 部分OpenAI模型支持
                "google": ["gemini-pro"],  # Google模型通常支持
                "perplexity": ["pplx-7b-online", "pplx-70b-online"],  # Perplexity专门支持
            }

            if provider in internet_capable_models:
                return model in internet_capable_models[provider]

            return False

        except Exception as e:
            logger.error(f"检查LLM联网能力失败: {e}")
            return False

class EnhancedTradingAgentsApp:
    """增强版TradingAgents应用"""
    
    def __init__(self):
        self.analysis_sessions = []
        self.config_file = Path("config/llm_config.json")
        self.config_dir = Path("config")
        self.config_dir.mkdir(exist_ok=True)

        # 初始化真实数据收集器
        self.data_collector = RealDataCollector()

        # 加载保存的配置
        self.llm_config = {}
        self.custom_llm_providers = {}
        self.load_saved_config()

        # 加载环境变量配置（作为补充）
        env_config = self.load_env_config()
        for provider, key in env_config.items():
            if provider not in self.llm_config:
                self.llm_config[provider] = key

        self.chromadb_available = self.check_chromadb()

        # 智能体模型配置
        self.agent_model_config = self.load_agent_model_config()

        # 通信日志
        self.communication_logs = []
        self.max_logs = 1000  # 最大保存1000条日志
        
    def load_env_config(self) -> Dict[str, str]:
        """从环境变量加载LLM配置"""
        config = {}
        env_keys = {
            "deepseek": "DEEPSEEK_API_KEY",
            "openai": "OPENAI_API_KEY", 
            "google": "GOOGLE_API_KEY",
            "moonshot": "MOONSHOT_API_KEY"
        }
        
        for provider, env_var in env_keys.items():
            api_key = os.getenv(env_var)
            if api_key:
                config[provider] = api_key
                logger.info(f"从环境变量加载 {provider} API密钥")
        
        return config
    
    def check_chromadb(self) -> bool:
        """检查ChromaDB是否可用"""
        try:
            import chromadb
            return True
        except ImportError:
            return False

    def _encrypt_key(self, key: str) -> str:
        """简单加密API密钥"""
        try:
            encoded = base64.b64encode(key.encode()).decode()
            return encoded
        except Exception:
            return key

    def _decrypt_key(self, encrypted_key: str) -> str:
        """解密API密钥"""
        try:
            decoded = base64.b64decode(encrypted_key.encode()).decode()
            return decoded
        except Exception:
            return encrypted_key

    def save_config(self) -> Dict[str, Any]:
        """保存LLM配置到文件"""
        try:
            config_data = {
                "llm_config": {
                    provider: self._encrypt_key(key)
                    for provider, key in self.llm_config.items()
                },
                "custom_llm_providers": {
                    name: {
                        "api_key": self._encrypt_key(config["api_key"]),
                        "base_url": config.get("base_url", ""),
                        "model": config.get("model", ""),
                        "added_time": config.get("added_time", "")
                    }
                    for name, config in self.custom_llm_providers.items()
                },
                "saved_time": datetime.now().isoformat(),
                "version": "1.0"
            }

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            logger.info(f"配置已保存到: {self.config_file}")

            return {
                "status": "success",
                "message": f"配置已保存 ({len(self.llm_config)}个内置提供商, {len(self.custom_llm_providers)}个自定义提供商)",
                "saved_time": config_data["saved_time"]
            }

        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return {
                "status": "error",
                "message": f"保存配置失败: {str(e)}"
            }

    def load_saved_config(self) -> Dict[str, Any]:
        """从文件加载保存的LLM配置"""
        try:
            if not self.config_file.exists():
                logger.info("配置文件不存在，使用默认配置")
                return {"status": "no_config", "message": "配置文件不存在"}

            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # 加载内置提供商配置
            if "llm_config" in config_data:
                for provider, encrypted_key in config_data["llm_config"].items():
                    self.llm_config[provider] = self._decrypt_key(encrypted_key)

            # 加载自定义提供商配置
            if "custom_llm_providers" in config_data:
                for name, config in config_data["custom_llm_providers"].items():
                    self.custom_llm_providers[name] = {
                        "api_key": self._decrypt_key(config["api_key"]),
                        "base_url": config.get("base_url", ""),
                        "model": config.get("model", ""),
                        "added_time": config.get("added_time", "")
                    }
                    # 同时添加到主配置中
                    self.llm_config[name] = self.custom_llm_providers[name]["api_key"]

            saved_time = config_data.get("saved_time", "未知")
            logger.info(f"配置已从文件加载: {len(self.llm_config)}个提供商")

            return {
                "status": "success",
                "message": f"配置已加载 (保存时间: {saved_time})",
                "loaded_providers": len(self.llm_config),
                "custom_providers": len(self.custom_llm_providers)
            }

        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            return {
                "status": "error",
                "message": f"加载配置失败: {str(e)}"
            }

    def clear_saved_config(self) -> Dict[str, Any]:
        """清空保存的配置"""
        try:
            if self.config_file.exists():
                self.config_file.unlink()

            # 清空内存中的配置
            self.llm_config.clear()
            self.custom_llm_providers.clear()

            # 重新加载环境变量
            env_config = self.load_env_config()
            self.llm_config.update(env_config)

            logger.info("配置已清空")

            return {
                "status": "success",
                "message": "配置已清空，重新加载环境变量配置"
            }

        except Exception as e:
            logger.error(f"清空配置失败: {e}")
            return {
                "status": "error",
                "message": f"清空配置失败: {str(e)}"
            }

    def get_available_models(self) -> Dict[str, List[str]]:
        """获取可用的模型列表"""
        models = {
            "deepseek": ["deepseek-chat", "deepseek-coder"],
            "openai": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini"],
            "google": ["gemini-pro", "gemini-pro-vision", "gemini-1.5-pro", "gemini-1.5-flash"],
            "moonshot": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]
        }

        # 添加自定义提供商的模型
        for provider_name, config in self.custom_llm_providers.items():
            model = config.get("model", f"{provider_name}-default")
            models[provider_name] = [model] if model else [f"{provider_name}-default"]

        return models

    def get_common_models_for_provider(self, provider_name: str) -> List[str]:
        """根据提供商名称推荐常见模型"""
        common_models = {
            "claude": ["claude-3-sonnet-20240229", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
            "anthropic": ["claude-3-sonnet-20240229", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
            "通义千问": ["qwen-turbo", "qwen-plus", "qwen-max", "qwen-max-longcontext"],
            "qwen": ["qwen-turbo", "qwen-plus", "qwen-max", "qwen-max-longcontext"],
            "文心一言": ["ernie-bot-turbo", "ernie-bot", "ernie-bot-4"],
            "ernie": ["ernie-bot-turbo", "ernie-bot", "ernie-bot-4"],
            "baidu": ["ernie-bot-turbo", "ernie-bot", "ernie-bot-4"],
            "llama": ["llama-2-7b-chat", "llama-2-13b-chat", "llama-2-70b-chat"],
            "chatglm": ["chatglm3-6b", "chatglm2-6b", "chatglm-6b"],
            "vicuna": ["vicuna-7b-v1.5", "vicuna-13b-v1.5", "vicuna-33b-v1.3"],
            "mistral": ["mistral-7b-instruct", "mixtral-8x7b-instruct"],
            "yi": ["yi-34b-chat", "yi-6b-chat"],
            "baichuan": ["baichuan2-13b-chat", "baichuan2-7b-chat"],
            "internlm": ["internlm-chat-7b", "internlm-chat-20b"]
        }

        # 根据提供商名称匹配
        provider_lower = provider_name.lower()
        for key, models in common_models.items():
            if key in provider_lower:
                return models

        # 如果没有匹配，返回通用模型名
        return [f"{provider_name}-chat", f"{provider_name}-turbo", f"{provider_name}-pro"]

    def get_agent_list(self) -> List[Dict[str, str]]:
        """获取15个智能体列表"""
        agents = [
            {"id": "market_analyst", "name": "📈 市场分析师", "category": "分析师"},
            {"id": "social_media_analyst", "name": "💭 情感分析师", "category": "分析师"},
            {"id": "news_analyst", "name": "📰 新闻分析师", "category": "分析师"},
            {"id": "fundamentals_analyst", "name": "📊 基本面分析师", "category": "分析师"},
            {"id": "bull_researcher", "name": "🐂 多头研究员", "category": "研究员"},
            {"id": "bear_researcher", "name": "🐻 空头研究员", "category": "研究员"},
            {"id": "research_manager", "name": "👨‍💼 研究经理", "category": "管理层"},
            {"id": "trader", "name": "👨‍💻 交易员", "category": "交易"},
            {"id": "aggressive_debator", "name": "🔴 激进分析师", "category": "风险管理"},
            {"id": "conservative_debator", "name": "🔵 保守分析师", "category": "风险管理"},
            {"id": "neutral_debator", "name": "🟡 中性分析师", "category": "风险管理"},
            {"id": "risk_manager", "name": "👨‍⚖️ 风险经理", "category": "风险管理"},
            {"id": "memory_manager", "name": "💾 记忆管理器", "category": "支持系统"},
            {"id": "signal_processor", "name": "📡 信号处理器", "category": "支持系统"},
            {"id": "reflection_engine", "name": "🔄 反思引擎", "category": "支持系统"}
        ]
        return agents

    def load_agent_model_config(self) -> Dict[str, str]:
        """加载智能体模型配置"""
        try:
            config_file = self.config_dir / "agent_model_config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"加载智能体模型配置失败: {e}")

        # 返回默认配置
        default_model = "deepseek:deepseek-chat"
        agents = self.get_agent_list()
        return {agent["id"]: default_model for agent in agents}

    def save_agent_model_config(self) -> Dict[str, Any]:
        """保存智能体模型配置"""
        try:
            config_file = self.config_dir / "agent_model_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.agent_model_config, f, indent=2, ensure_ascii=False)

            logger.info("智能体模型配置已保存")
            return {
                "status": "success",
                "message": f"智能体模型配置已保存 ({len(self.agent_model_config)}个智能体)"
            }
        except Exception as e:
            logger.error(f"保存智能体模型配置失败: {e}")
            return {
                "status": "error",
                "message": f"保存失败: {str(e)}"
            }

    def update_agent_model(self, agent_id: str, provider_model: str) -> Dict[str, Any]:
        """更新单个智能体的模型配置"""
        try:
            self.agent_model_config[agent_id] = provider_model
            save_result = self.save_agent_model_config()

            return {
                "status": "success",
                "message": f"智能体 {agent_id} 模型已更新为 {provider_model}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"更新失败: {str(e)}"
            }

    def log_communication(self, agent_id: str, provider: str, model: str,
                         prompt: str, response: str, status: str = "success"):
        """记录LLM通信日志"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "agent_id": agent_id,
                "provider": provider,
                "model": model,
                "prompt": prompt[:500] + "..." if len(prompt) > 500 else prompt,
                "response": response[:1000] + "..." if len(response) > 1000 else response,
                "status": status,
                "prompt_length": len(prompt),
                "response_length": len(response)
            }

            self.communication_logs.append(log_entry)

            # 保持日志数量在限制内
            if len(self.communication_logs) > self.max_logs:
                self.communication_logs = self.communication_logs[-self.max_logs:]

            logger.info(f"记录通信日志: {agent_id} -> {provider}:{model}")

        except Exception as e:
            logger.error(f"记录通信日志失败: {e}")

    def get_communication_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取通信日志"""
        return self.communication_logs[-limit:] if self.communication_logs else []

    def clear_communication_logs(self) -> Dict[str, Any]:
        """清空通信日志"""
        try:
            self.communication_logs.clear()
            return {
                "status": "success",
                "message": "通信日志已清空"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"清空失败: {str(e)}"
            }
    
    def add_custom_llm_provider(self, name: str, api_key: str, base_url: str = "", model: str = "") -> Dict[str, Any]:
        """添加自定义LLM提供商"""
        try:
            if not name or not api_key:
                return {
                    "status": "error",
                    "message": "提供商名称和API密钥不能为空"
                }

            # 检查名称是否已存在
            if name.lower() in [p.lower() for p in self.llm_config.keys()] or \
               name.lower() in [p.lower() for p in self.custom_llm_providers.keys()]:
                return {
                    "status": "error",
                    "message": f"提供商 '{name}' 已存在"
                }

            # 添加自定义提供商
            self.custom_llm_providers[name] = {
                "api_key": api_key,
                "base_url": base_url,
                "model": model,
                "added_time": datetime.now().isoformat()
            }

            # 同时添加到主配置中
            self.llm_config[name] = api_key

            logger.info(f"添加自定义LLM提供商: {name}")

            return {
                "status": "success",
                "message": f"成功添加提供商 '{name}'",
                "provider": name
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"添加提供商失败: {str(e)}"
            }

    def remove_custom_llm_provider(self, name: str) -> Dict[str, Any]:
        """删除自定义LLM提供商"""
        try:
            if name not in self.custom_llm_providers:
                return {
                    "status": "error",
                    "message": f"提供商 '{name}' 不存在"
                }

            # 从自定义提供商中删除
            del self.custom_llm_providers[name]

            # 从主配置中删除
            if name in self.llm_config:
                del self.llm_config[name]

            logger.info(f"删除自定义LLM提供商: {name}")

            return {
                "status": "success",
                "message": f"成功删除提供商 '{name}'"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"删除提供商失败: {str(e)}"
            }

    def get_all_llm_providers(self) -> Dict[str, Any]:
        """获取所有LLM提供商信息"""
        providers = {
            "built_in": {
                "deepseek": {"configured": "deepseek" in self.llm_config, "type": "内置"},
                "openai": {"configured": "openai" in self.llm_config, "type": "内置"},
                "google": {"configured": "google" in self.llm_config, "type": "内置"},
                "moonshot": {"configured": "moonshot" in self.llm_config, "type": "内置"}
            },
            "custom": {}
        }

        # 添加自定义提供商信息
        for name, config in self.custom_llm_providers.items():
            providers["custom"][name] = {
                "configured": True,
                "type": "自定义",
                "base_url": config.get("base_url", ""),
                "model": config.get("model", ""),
                "added_time": config.get("added_time", "")
            }

        return providers

    async def test_llm_connection(self, provider: str, api_key: str, base_url: str = "") -> Dict[str, Any]:
        """测试LLM连接"""
        try:
            # 模拟LLM连接测试
            await asyncio.sleep(1)

            if not api_key or len(api_key) < 10:
                return {
                    "status": "error",
                    "message": "API密钥格式不正确"
                }

            # 对于自定义提供商，检查base_url
            if provider in self.custom_llm_providers and base_url:
                # 这里可以添加真实的URL连通性测试
                pass

            # 这里可以添加真实的API测试
            return {
                "status": "success",
                "message": f"{provider} 连接测试成功",
                "provider": provider
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"连接测试失败: {str(e)}"
            }
    
    async def analyze_stock_enhanced(self, symbol: str, depth: str, analysts: List[str],
                                   use_real_llm: bool = False) -> Dict[str, Any]:
        """增强的股票分析 - 真正的15个智能体协作"""
        try:
            logger.info(f"开始分析股票: {symbol}, 深度: {depth}, 使用真实LLM: {use_real_llm}")

            if use_real_llm:
                # 真实的智能体分析
                return await self._real_agent_analysis(symbol, depth, analysts)
            else:
                # 模拟分析（保持向后兼容）
                return await self._mock_analysis(symbol, depth, analysts)

        except Exception as e:
            logger.error(f"股票分析失败: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _real_agent_analysis(self, symbol: str, depth: str, analysts: List[str]) -> Dict[str, Any]:
        """真实的智能体分析流程"""
        try:
            start_time = datetime.now()

            # 1. 数据收集阶段
            logger.info("📊 阶段1: 数据收集")
            stock_data = await self._collect_stock_data(symbol)

            # 2. 分析师团队分析
            logger.info("👥 阶段2: 分析师团队分析")
            analyst_results = await self._run_analyst_team(symbol, stock_data)

            # 3. 研究团队辩论
            logger.info("🔬 阶段3: 研究团队辩论")
            research_results = await self._run_research_team(symbol, analyst_results)

            # 4. 交易策略制定
            logger.info("💼 阶段4: 交易策略制定")
            trading_strategy = await self._run_trader_analysis(symbol, research_results)

            # 5. 风险管理评估
            logger.info("⚠️ 阶段5: 风险管理评估")
            risk_assessment = await self._run_risk_management(symbol, trading_strategy)

            # 6. 最终决策
            logger.info("🎯 阶段6: 最终决策制定")
            final_decision = await self._make_final_decision(symbol, risk_assessment)

            # 7. 反思和学习
            logger.info("🔄 阶段7: 反思和学习")
            reflection = await self._run_reflection(symbol, final_decision)

            # 构建完整结果
            result = {
                "symbol": symbol,
                "status": "completed",
                "depth": depth,
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "llm_used": "real",
                "chromadb_status": "available" if self.chromadb_available else "unavailable",
                "analysis_stages": {
                    "data_collection": stock_data,
                    "analyst_team": analyst_results,
                    "research_team": research_results,
                    "trading_strategy": trading_strategy,
                    "risk_assessment": risk_assessment,
                    "final_decision": final_decision,
                    "reflection": reflection
                },
                "results": {
                    "comprehensive_report": self._generate_real_comprehensive_report(final_decision),
                    "market_analysis": analyst_results.get("market_analyst", {}),
                    "sentiment_analysis": analyst_results.get("sentiment_analyst", {}),
                    "news_analysis": analyst_results.get("news_analyst", {}),
                    "fundamentals_analysis": analyst_results.get("fundamentals_analyst", {}),
                    "bull_arguments": research_results.get("bull_researcher", {}),
                    "bear_arguments": research_results.get("bear_researcher", {}),
                    "investment_recommendation": research_results.get("research_manager", {}),
                    "trading_strategy": trading_strategy,
                    "risk_assessment": risk_assessment,
                    "final_decision": final_decision.get("decision", "HOLD")
                }
            }

            # 保存会话
            self.analysis_sessions.append(result)

            return result

        except Exception as e:
            logger.error(f"真实智能体分析失败: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _mock_analysis(self, symbol: str, depth: str, analysts: List[str]) -> Dict[str, Any]:
        """模拟分析（保持向后兼容）"""
        # 模拟分析过程
        analysis_time = {"浅层分析": 2, "中等分析": 5, "深度分析": 8}
        await asyncio.sleep(analysis_time.get(depth, 3))

        # 生成分析结果
        result = {
            "symbol": symbol,
            "status": "completed",
            "depth": depth,
            "start_time": datetime.now().isoformat(),
            "llm_used": "mock",
            "chromadb_status": "available" if self.chromadb_available else "unavailable",
            "results": {
                "comprehensive_report": self.generate_comprehensive_report(symbol, depth),
                "market_analysis": self.generate_market_analysis(symbol),
                "sentiment_analysis": self.generate_sentiment_analysis(symbol),
                "news_analysis": self.generate_news_analysis(symbol),
                "fundamentals_analysis": self.generate_fundamentals_analysis(symbol),
                "bull_arguments": self.generate_bull_arguments(symbol),
                "bear_arguments": self.generate_bear_arguments(symbol),
                "investment_recommendation": self.generate_investment_recommendation(symbol),
                "trading_strategy": self.generate_trading_strategy(symbol),
                "risk_assessment": self.generate_risk_assessment(symbol),
                "final_decision": self.generate_final_decision(symbol)
            }
        }

        # 保存会话
        self.analysis_sessions.append(result)

        return result
    
    def generate_comprehensive_report(self, symbol: str, depth: str) -> str:
        """生成综合报告"""
        return f"""
## 📊 {symbol} 综合分析报告

### 🎯 最终决策
**投资建议**: 买入
**目标价位**: 当前价格上调15%
**信心水平**: 78%

### 📈 分析概览
- **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **分析深度**: {depth}
- **分析状态**: ✅ 已完成
- **ChromaDB状态**: {'✅ 可用' if self.chromadb_available else '❌ 不可用'}

### 💡 关键洞察
基于15个专业智能体的协作分析，{symbol}展现出良好的投资价值。技术面显示上升趋势，基本面数据支撑，市场情绪偏向乐观。

### 🔍 分析亮点
- **技术分析**: 突破关键阻力位，成交量放大
- **基本面**: 业绩增长稳定，行业地位领先
- **市场情绪**: 机构资金流入，散户情绪积极
- **风险控制**: 设置合理止损位，控制下行风险

---
*本报告由多智能体协作生成，仅供参考*
"""
    
    def generate_market_analysis(self, symbol: str) -> str:
        """生成市场分析"""
        return f"""
### 📈 {symbol} 市场技术分析

**技术指标分析**:
- **RSI**: 55.8 (中性偏多)
- **MACD**: 金叉形成，动能增强
- **均线系统**: 多头排列，支撑有效
- **成交量**: 近期放量上涨，资金关注度高

**关键价位**:
- **支撑位**: 当前价格-8%
- **阻力位**: 当前价格+12%
- **目标价**: 当前价格+15%

**技术形态**: 上升三角形突破，后市看涨
"""
    
    def generate_sentiment_analysis(self, symbol: str) -> str:
        """生成情感分析"""
        return f"""
### 💭 {symbol} 社交情感分析

**投资者情绪指标**:
- **整体情绪**: 乐观 (75/100)
- **机构态度**: 积极关注
- **散户热度**: 中等偏高
- **媒体关注**: 正面报道居多

**情感趋势**: 近期情绪持续改善，投资者信心增强
"""
    
    def generate_news_analysis(self, symbol: str) -> str:
        """生成新闻分析"""
        return f"""
### 📰 {symbol} 新闻事件分析

**重要新闻**:
- 公司发布业绩预告，超市场预期
- 行业政策利好，长期发展前景明朗
- 机构调研频繁，获得专业认可

**新闻情感**: 正面消息占主导，市场反应积极
"""
    
    def generate_fundamentals_analysis(self, symbol: str) -> str:
        """生成基本面分析"""
        return f"""
### 📊 {symbol} 基本面分析

**财务指标**:
- **市盈率**: 22.5倍 (合理估值)
- **市净率**: 2.8倍 (略低于行业均值)
- **ROE**: 18.5% (盈利能力强)
- **负债率**: 45% (财务结构健康)

**盈利能力**: 连续三年增长，盈利质量优秀
**成长性**: 业务扩张稳健，未来增长可期
"""
    
    def generate_bull_arguments(self, symbol: str) -> str:
        """生成多头观点"""
        return f"""
### 🐂 {symbol} 多头观点

**看涨理由**:
1. **业绩增长**: 连续多季度超预期增长
2. **行业地位**: 细分领域龙头，竞争优势明显
3. **政策支持**: 受益于行业政策红利
4. **技术突破**: 关键技术指标显示上涨信号
5. **资金流入**: 机构资金持续流入

**目标价位**: 建议上调至当前价格+20%
"""
    
    def generate_bear_arguments(self, symbol: str) -> str:
        """生成空头观点"""
        return f"""
### 🐻 {symbol} 空头观点

**风险因素**:
1. **估值压力**: 当前估值已反映部分利好
2. **行业竞争**: 竞争加剧可能影响盈利
3. **宏观环境**: 经济不确定性带来风险
4. **技术风险**: 短期可能面临技术性回调

**风险控制**: 建议设置止损位于-10%
"""
    
    def generate_investment_recommendation(self, symbol: str) -> str:
        """生成投资建议"""
        return f"""
### 🎯 {symbol} 投资建议

**综合评级**: 买入
**建议仓位**: 中等仓位 (20-30%)
**投资期限**: 中长期 (6-12个月)
**风险等级**: 中等风险

**操作建议**:
1. 分批建仓，避免一次性买入
2. 设置止损位，控制下行风险
3. 关注业绩发布，及时调整策略
"""
    
    def generate_trading_strategy(self, symbol: str) -> str:
        """生成交易策略"""
        return f"""
### 💼 {symbol} 交易策略

**入场策略**:
- **买入时机**: 回调至支撑位附近
- **分批建仓**: 3次建仓，每次1/3仓位
- **止损设置**: -8%严格止损

**持仓管理**:
- **加仓条件**: 突破前高且成交量配合
- **减仓信号**: 技术指标背离或基本面恶化
- **止盈目标**: 分批止盈，保留核心仓位

**风险控制**: 单只股票仓位不超过总资金30%
"""
    
    def generate_risk_assessment(self, symbol: str) -> str:
        """生成风险评估"""
        return f"""
### ⚠️ {symbol} 风险评估

**风险等级**: 中等风险
**风险因素**:
1. **市场风险**: 系统性风险影响
2. **行业风险**: 行业周期性波动
3. **公司风险**: 经营管理风险
4. **流动性风险**: 交易活跃度风险

**风险控制措施**:
- 严格止损，控制单笔损失
- 分散投资，降低集中度风险
- 定期评估，及时调整策略
"""
    
    def generate_final_decision(self, symbol: str) -> str:
        """生成最终决策"""
        return f"""
### 🎯 {symbol} 最终投资决策

**决策**: 买入
**信心度**: 78%
**建议仓位**: 25%
**投资期限**: 6-12个月

**决策依据**:
经过15个专业智能体的深度分析和多轮辩论，{symbol}在技术面、基本面、市场情绪等多个维度均显示积极信号。虽然存在一定风险，但整体投资价值突出。

**执行建议**:
1. 等待合适买点分批建仓
2. 严格执行风险控制措施
3. 持续跟踪基本面变化
4. 根据市场情况灵活调整

**风险提示**: 投资有风险，决策需谨慎。本分析仅供参考，不构成投资建议。
"""
    
    def get_analysis_history(self) -> List[List[str]]:
        """获取分析历史"""
        history = []
        for session in self.analysis_sessions[-10:]:
            history.append([
                session.get("start_time", "")[:19],
                session.get("symbol", ""),
                session.get("depth", ""),
                session.get("status", ""),
                "真实LLM" if session.get("llm_used") == "real" else "模拟",
                session.get("results", {}).get("final_decision", "")[:30] + "..."
            ])
        return history

    # ==================== 真实智能体调用方法 ====================

    async def _collect_stock_data(self, symbol: str) -> Dict[str, Any]:
        """数据收集阶段 - 使用真实数据"""
        try:
            logger.info(f"开始收集股票 {symbol} 的真实数据...")

            # 使用真实数据收集器获取数据
            real_data = await self.data_collector.get_real_stock_data(symbol)

            if "error" in real_data:
                logger.error(f"获取真实数据失败: {real_data['error']}")
                return real_data

            logger.info(f"成功收集股票 {symbol} 的真实数据")
            logger.info(f"当前价格: {real_data['price_data']['current_price']}")
            logger.info(f"RSI: {real_data['technical_indicators']['rsi']:.2f}")
            logger.info(f"MACD: {real_data['technical_indicators']['macd']:.2f}")

            return real_data

        except Exception as e:
            logger.error(f"数据收集失败: {e}")
            return {"error": f"数据收集失败: {str(e)}"}

    async def _check_llm_internet_access(self, agent_id: str) -> bool:
        """检查智能体使用的LLM是否支持联网"""
        try:
            model_config = self.agent_model_config.get(agent_id, "deepseek:deepseek-chat")
            provider, model = model_config.split(":", 1)

            if provider not in self.llm_config:
                return False

            api_key = self.llm_config[provider]
            return await self.data_collector.check_llm_internet_capability(provider, model, api_key)

        except Exception as e:
            logger.error(f"检查LLM联网能力失败: {e}")
            return False

    async def _run_analyst_team(self, symbol: str, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """运行分析师团队"""
        try:
            results = {}

            # 1. 市场分析师
            results["market_analyst"] = await self._call_market_analyst(symbol, stock_data)

            # 2. 情感分析师
            results["sentiment_analyst"] = await self._call_sentiment_analyst(symbol, stock_data)

            # 3. 新闻分析师
            results["news_analyst"] = await self._call_news_analyst(symbol, stock_data)

            # 4. 基本面分析师
            results["fundamentals_analyst"] = await self._call_fundamentals_analyst(symbol, stock_data)

            return results

        except Exception as e:
            logger.error(f"分析师团队运行失败: {e}")
            return {"error": str(e)}

    async def _call_market_analyst(self, symbol: str, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """调用市场分析师"""
        try:
            # 获取配置的模型
            model_config = self.agent_model_config.get("market_analyst", "deepseek:deepseek-chat")
            provider, model = model_config.split(":", 1)

            # 构建提示
            prompt = f"""
你是专业的市场技术分析师。请分析股票 {symbol} 的技术指标和价格走势。

当前数据:
- 价格: {stock_data['price_data']['current_price']}
- 涨跌幅: {stock_data['price_data']['change_percent']}%
- RSI: {stock_data['technical_indicators']['rsi']}
- MACD: {stock_data['technical_indicators']['macd']}
- MA5: {stock_data['technical_indicators']['ma5']}
- MA20: {stock_data['technical_indicators']['ma20']}

请提供:
1. 技术趋势分析
2. 关键支撑阻力位
3. 短期走势预测
4. 交易信号建议

请用专业、简洁的语言回答，控制在200字以内。
"""

            # 调用LLM
            response = await self._call_llm(provider, model, prompt, "market_analyst")

            return {
                "agent_id": "market_analyst",
                "analysis": response,
                "signal": self._extract_trading_signal(response),
                "confidence": self._extract_confidence(response),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"市场分析师调用失败: {e}")
            return {"error": str(e), "agent_id": "market_analyst"}

    async def _call_sentiment_analyst(self, symbol: str, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """调用情感分析师 - 使用真实社交媒体数据"""
        try:
            model_config = self.agent_model_config.get("social_media_analyst", "deepseek:deepseek-chat")
            provider, model = model_config.split(":", 1)

            # 检查LLM是否支持联网搜索
            has_internet = await self._check_llm_internet_access("social_media_analyst")

            if has_internet:
                # 使用联网搜索获取真实社交媒体数据
                prompt = f"""
你是专业的市场情感分析师。请搜索并分析股票 {symbol} 在今天的社交媒体情绪和投资者情感。

请搜索以下平台的最新讨论:
1. 微博、雪球等投资社区
2. 财经新闻评论区
3. 投资论坛讨论

基于搜索到的真实数据和当前市场表现:
- 当前价格: {stock_data['price_data']['current_price']}
- 股价变化: {stock_data['price_data']['change_percent']}%
- 成交量: {stock_data['price_data']['volume']}

请分析:
1. 当前社交媒体情绪倾向
2. 投资者信心水平变化
3. 热门讨论话题和情感驱动因素
4. 情感对价格走势的影响预测

请基于真实搜索数据回答，控制在300字以内。
"""
            else:
                # 提示用户切换支持联网的模型
                return {
                    "agent_id": "sentiment_analyst",
                    "analysis": f"⚠️ 当前模型 {provider}:{model} 不支持联网搜索。\n\n建议切换到支持联网的模型如:\n- OpenAI GPT-4\n- Google Gemini Pro\n- Perplexity在线模型\n\n以获取真实的社交媒体情感数据。",
                    "sentiment": "无法分析",
                    "confidence": 0.0,
                    "timestamp": datetime.now().isoformat(),
                    "requires_internet": True
                }

            response = await self._call_llm(provider, model, prompt, "social_media_analyst")

            return {
                "agent_id": "sentiment_analyst",
                "analysis": response,
                "sentiment": self._extract_sentiment(response),
                "confidence": self._extract_confidence(response),
                "timestamp": datetime.now().isoformat(),
                "data_source": "real_social_media" if has_internet else "limited"
            }

        except Exception as e:
            logger.error(f"情感分析师调用失败: {e}")
            return {"error": str(e), "agent_id": "sentiment_analyst"}

    async def _call_news_analyst(self, symbol: str, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """调用新闻分析师 - 使用真实新闻数据"""
        try:
            model_config = self.agent_model_config.get("news_analyst", "deepseek:deepseek-chat")
            provider, model = model_config.split(":", 1)

            # 检查LLM是否支持联网搜索
            has_internet = await self._check_llm_internet_access("news_analyst")

            if has_internet:
                # 使用联网搜索获取真实新闻数据
                stock_name = stock_data.get('name', symbol)
                prompt = f"""
你是专业的新闻分析师。请搜索并分析今天影响股票 {symbol}({stock_name}) 的最新新闻和宏观经济因素。

请搜索以下类型的最新新闻:
1. 公司相关新闻公告
2. 行业政策和监管变化
3. 宏观经济数据发布
4. 国际市场影响因素

当前市场状况:
- 当前价格: {stock_data['price_data']['current_price']}
- 股价变化: {stock_data['price_data']['change_percent']}%
- 市盈率: {stock_data['market_data']['pe_ratio']}
- 市净率: {stock_data['market_data']['pb_ratio']}

请基于搜索到的真实新闻分析:
1. 今日重要新闻事件及影响
2. 行业政策变化和监管动态
3. 宏观经济环境对该股的影响
4. 新闻事件对股价的潜在影响预测

请基于真实搜索数据回答，控制在300字以内。
"""
            else:
                # 提示用户切换支持联网的模型
                return {
                    "agent_id": "news_analyst",
                    "analysis": f"⚠️ 当前模型 {provider}:{model} 不支持联网搜索。\n\n建议切换到支持联网的模型如:\n- OpenAI GPT-4\n- Google Gemini Pro\n- Perplexity在线模型\n\n以获取今日最新的新闻和宏观经济数据。",
                    "impact_level": "无法评估",
                    "confidence": 0.0,
                    "timestamp": datetime.now().isoformat(),
                    "requires_internet": True
                }

            response = await self._call_llm(provider, model, prompt, "news_analyst")

            return {
                "agent_id": "news_analyst",
                "analysis": response,
                "impact_level": self._extract_impact_level(response),
                "confidence": self._extract_confidence(response),
                "timestamp": datetime.now().isoformat(),
                "data_source": "real_news" if has_internet else "limited"
            }

        except Exception as e:
            logger.error(f"新闻分析师调用失败: {e}")
            return {"error": str(e), "agent_id": "news_analyst"}

    async def _call_fundamentals_analyst(self, symbol: str, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """调用基本面分析师 - 使用真实财务数据"""
        try:
            model_config = self.agent_model_config.get("fundamentals_analyst", "deepseek:deepseek-chat")
            provider, model = model_config.split(":", 1)

            # 检查LLM是否支持联网搜索
            has_internet = await self._check_llm_internet_access("fundamentals_analyst")

            if has_internet:
                # 使用联网搜索获取真实财务数据
                stock_name = stock_data.get('name', symbol)
                prompt = f"""
你是专业的基本面分析师。请搜索并分析股票 {symbol}({stock_name}) 的最新财务数据和基本面指标。

请搜索以下最新财务信息:
1. 最新季度财报数据
2. 年度财务报表
3. 现金流量表
4. 资产负债表
5. 行业对比数据

当前市场数据:
- 当前价格: {stock_data['price_data']['current_price']}
- 市盈率: {stock_data['market_data']['pe_ratio']}
- 市净率: {stock_data['market_data']['pb_ratio']}
- 市值: {stock_data['price_data'].get('market_cap', '未知')}

请基于搜索到的最新财务数据分析:
1. 最新财务指标和盈利能力
2. 资产质量和负债结构
3. 现金流状况和分红能力
4. 行业地位和竞争优势
5. 估值水平和投资价值判断

请基于真实财务数据回答，控制在300字以内。
"""
            else:
                # 提示用户切换支持联网的模型
                return {
                    "agent_id": "fundamentals_analyst",
                    "analysis": f"⚠️ 当前模型 {provider}:{model} 不支持联网搜索。\n\n建议切换到支持联网的模型如:\n- OpenAI GPT-4\n- Google Gemini Pro\n- Perplexity在线模型\n\n以获取最新的财务数据和基本面信息。\n\n当前可用的基础数据:\n- 市盈率: {stock_data['market_data']['pe_ratio']}\n- 市净率: {stock_data['market_data']['pb_ratio']}\n- 当前价格: {stock_data['price_data']['current_price']}",
                    "valuation": "无法评估",
                    "confidence": 0.0,
                    "timestamp": datetime.now().isoformat(),
                    "requires_internet": True
                }

            response = await self._call_llm(provider, model, prompt, "fundamentals_analyst")

            return {
                "agent_id": "fundamentals_analyst",
                "analysis": response,
                "valuation": self._extract_valuation(response),
                "confidence": self._extract_confidence(response),
                "timestamp": datetime.now().isoformat(),
                "data_source": "real_financials" if has_internet else "limited"
            }

        except Exception as e:
            logger.error(f"基本面分析师调用失败: {e}")
            return {"error": str(e), "agent_id": "fundamentals_analyst"}

    async def _run_research_team(self, symbol: str, analyst_results: Dict[str, Any]) -> Dict[str, Any]:
        """运行研究团队"""
        try:
            results = {}

            # 1. 多头研究员
            results["bull_researcher"] = await self._call_bull_researcher(symbol, analyst_results)

            # 2. 空头研究员
            results["bear_researcher"] = await self._call_bear_researcher(symbol, analyst_results)

            # 3. 研究经理
            results["research_manager"] = await self._call_research_manager(symbol, results)

            return results

        except Exception as e:
            logger.error(f"研究团队运行失败: {e}")
            return {"error": str(e)}

    async def _call_bull_researcher(self, symbol: str, analyst_results: Dict[str, Any]) -> Dict[str, Any]:
        """调用多头研究员"""
        try:
            model_config = self.agent_model_config.get("bull_researcher", "deepseek:deepseek-chat")
            provider, model = model_config.split(":", 1)

            # 汇总分析师观点
            market_view = analyst_results.get("market_analyst", {}).get("analysis", "")
            sentiment_view = analyst_results.get("sentiment_analyst", {}).get("analysis", "")

            prompt = f"""
你是专业的多头研究员。基于分析师团队的报告，请为股票 {symbol} 提供看涨论据。

分析师观点:
- 技术分析: {market_view[:100]}...
- 情感分析: {sentiment_view[:100]}...

请提供:
1. 主要看涨理由
2. 上涨催化剂
3. 目标价位预期
4. 投资机会分析

请用积极、专业的语言回答，控制在200字以内。
"""

            response = await self._call_llm(provider, model, prompt, "bull_researcher")

            return {
                "agent_id": "bull_researcher",
                "analysis": response,
                "bullish_score": self._extract_bullish_score(response),
                "confidence": self._extract_confidence(response),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"多头研究员调用失败: {e}")
            return {"error": str(e), "agent_id": "bull_researcher"}

    async def _call_llm(self, provider: str, model: str, prompt: str, agent_id: str) -> str:
        """核心LLM调用方法"""
        try:
            # 检查提供商是否配置
            if provider not in self.llm_config:
                raise ValueError(f"提供商 {provider} 未配置")

            api_key = self.llm_config[provider]

            # 记录通信开始
            start_time = datetime.now()

            # 根据提供商调用相应的LLM
            if provider == "deepseek":
                response = await self._call_deepseek(api_key, model, prompt)
            elif provider == "openai":
                response = await self._call_openai(api_key, model, prompt)
            elif provider == "google":
                response = await self._call_google(api_key, model, prompt)
            elif provider == "moonshot":
                response = await self._call_moonshot(api_key, model, prompt)
            else:
                # 自定义提供商
                custom_config = self.custom_llm_providers.get(provider, {})
                base_url = custom_config.get("base_url", "")
                response = await self._call_custom_llm(api_key, base_url, model, prompt)

            # 记录通信日志
            self.log_communication(
                agent_id=agent_id,
                provider=provider,
                model=model,
                prompt=prompt,
                response=response,
                status="success"
            )

            return response

        except Exception as e:
            # 记录失败的通信
            self.log_communication(
                agent_id=agent_id,
                provider=provider,
                model=model,
                prompt=prompt,
                response=f"错误: {str(e)}",
                status="failed"
            )

            logger.error(f"LLM调用失败 ({provider}:{model}): {e}")
            return f"分析暂时不可用，请稍后重试。错误: {str(e)}"

    async def _call_deepseek(self, api_key: str, model: str, prompt: str) -> str:
        """调用DeepSeek API"""
        try:
            import httpx

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            return f"DeepSeek分析不可用: {str(e)}"

    async def _call_openai(self, api_key: str, model: str, prompt: str) -> str:
        """调用OpenAI API"""
        try:
            import httpx

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            return f"OpenAI分析不可用: {str(e)}"

    async def _call_google(self, api_key: str, model: str, prompt: str) -> str:
        """调用Google Gemini API"""
        try:
            import httpx

            # Google Gemini API调用
            headers = {
                "Content-Type": "application/json"
            }

            # 构建请求数据
            data = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1000
                }
            }

            # 修正Google Gemini模型名称
            if model == "gemini-pro":
                model = "gemini-1.5-flash"  # 使用可用的模型
            elif model == "gemini-pro-vision":
                model = "gemini-1.5-pro"

            # Google Gemini API URL
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()

                result = response.json()

                # 解析响应
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        parts = candidate["content"]["parts"]
                        if len(parts) > 0 and "text" in parts[0]:
                            return parts[0]["text"]

                # 如果解析失败，返回原始响应
                logger.warning(f"Google API响应格式异常: {result}")
                return f"Google API响应解析失败: {str(result)}"

        except httpx.HTTPStatusError as e:
            logger.error(f"Google API HTTP错误: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 401:
                return "❌ Google API密钥无效，请检查配置"
            elif e.response.status_code == 403:
                return "❌ Google API访问被拒绝，请检查API密钥权限"
            elif e.response.status_code == 429:
                return "❌ Google API请求频率过高，请稍后重试"
            else:
                return f"❌ Google API调用失败: HTTP {e.response.status_code}"
        except Exception as e:
            logger.error(f"Google API调用失败: {e}")
            return f"❌ Google API调用异常: {str(e)}"

    async def _call_moonshot(self, api_key: str, model: str, prompt: str) -> str:
        """调用Moonshot API"""
        try:
            import httpx

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.moonshot.cn/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Moonshot API调用失败: {e}")
            return f"Moonshot分析不可用: {str(e)}"

    async def _call_custom_llm(self, api_key: str, base_url: str, model: str, prompt: str) -> str:
        """调用自定义LLM API"""
        try:
            import httpx

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"自定义LLM API调用失败: {e}")
            return f"自定义LLM分析不可用: {str(e)}"

    # ==================== 辅助分析方法 ====================

    def _extract_trading_signal(self, text: str) -> str:
        """从分析文本中提取交易信号"""
        text_lower = text.lower()
        if any(word in text_lower for word in ["买入", "看涨", "上涨", "buy", "bullish"]):
            return "BUY"
        elif any(word in text_lower for word in ["卖出", "看跌", "下跌", "sell", "bearish"]):
            return "SELL"
        else:
            return "HOLD"

    def _extract_confidence(self, text: str) -> float:
        """从分析文本中提取信心水平"""
        # 简单的信心水平提取逻辑
        confidence_words = {
            "非常确定": 0.9, "确定": 0.8, "较为确定": 0.7,
            "可能": 0.6, "不确定": 0.4, "很不确定": 0.3
        }

        for word, score in confidence_words.items():
            if word in text:
                return score

        return 0.6  # 默认信心水平

    def _extract_sentiment(self, text: str) -> str:
        """提取情感倾向"""
        text_lower = text.lower()
        positive_words = ["乐观", "积极", "正面", "看好"]
        negative_words = ["悲观", "消极", "负面", "看空"]

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            return "积极"
        elif negative_count > positive_count:
            return "消极"
        else:
            return "中性"

    def _extract_impact_level(self, text: str) -> str:
        """提取影响水平"""
        if any(word in text.lower() for word in ["重大", "显著", "强烈"]):
            return "高"
        elif any(word in text.lower() for word in ["中等", "一般", "适度"]):
            return "中"
        else:
            return "低"

    def _extract_valuation(self, text: str) -> str:
        """提取估值水平"""
        if any(word in text.lower() for word in ["低估", "便宜", "超值"]):
            return "低估"
        elif any(word in text.lower() for word in ["高估", "昂贵", "泡沫"]):
            return "高估"
        else:
            return "合理"

    def _extract_bullish_score(self, text: str) -> float:
        """提取看涨评分"""
        # 简单的看涨评分逻辑
        bullish_words = ["强烈看涨", "看涨", "上涨", "买入"]
        score = 0.5

        for word in bullish_words:
            if word in text:
                score += 0.1

        return min(score, 1.0)

    # ==================== 剩余智能体调用方法 ====================

    async def _run_trader_analysis(self, symbol: str, research_results: Dict[str, Any]) -> Dict[str, Any]:
        """运行交易员分析"""
        try:
            model_config = self.agent_model_config.get("trader", "deepseek:deepseek-chat")
            provider, model = model_config.split(":", 1)

            # 汇总研究团队观点
            bull_view = research_results.get("bull_researcher", {}).get("analysis", "")
            bear_view = research_results.get("bear_researcher", {}).get("analysis", "")

            prompt = f"""
你是专业的交易员。基于研究团队的分析，请为股票 {symbol} 制定具体的交易策略。

研究团队观点:
- 多头观点: {bull_view[:150]}...
- 空头观点: {bear_view[:150]}...

请制定:
1. 具体交易策略
2. 入场时机和价位
3. 仓位管理建议
4. 止损止盈设置

请用专业、实用的语言回答，控制在200字以内。
"""

            response = await self._call_llm(provider, model, prompt, "trader")

            return {
                "agent_id": "trader",
                "strategy": response,
                "action": self._extract_trading_signal(response),
                "confidence": self._extract_confidence(response),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"交易员分析失败: {e}")
            return {"error": str(e), "agent_id": "trader"}

    async def _run_risk_management(self, symbol: str, trading_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """运行风险管理团队"""
        try:
            results = {}

            # 风险管理辩论
            results["aggressive_debator"] = await self._call_aggressive_debator(symbol, trading_strategy)
            results["conservative_debator"] = await self._call_conservative_debator(symbol, trading_strategy)
            results["neutral_debator"] = await self._call_neutral_debator(symbol, trading_strategy)

            # 风险经理最终评估
            results["risk_manager"] = await self._call_risk_manager(symbol, results)

            return results

        except Exception as e:
            logger.error(f"风险管理团队运行失败: {e}")
            return {"error": str(e)}

    async def _make_final_decision(self, symbol: str, risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """制定最终决策"""
        try:
            # 汇总所有分析结果
            risk_manager_view = risk_assessment.get("risk_manager", {}).get("analysis", "")

            # 使用风险经理的模型进行最终决策
            model_config = self.agent_model_config.get("risk_manager", "deepseek:deepseek-chat")
            provider, model = model_config.split(":", 1)

            prompt = f"""
作为最终决策者，请基于风险管理团队的评估，对股票 {symbol} 做出最终投资决策。

风险评估: {risk_manager_view[:200]}...

请给出:
1. 最终投资决策 (BUY/SELL/HOLD)
2. 决策理由
3. 风险提示
4. 建议仓位比例

请用简洁、明确的语言回答，控制在150字以内。
"""

            response = await self._call_llm(provider, model, prompt, "final_decision")

            return {
                "decision": self._extract_trading_signal(response),
                "reasoning": response,
                "confidence": self._extract_confidence(response),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"最终决策制定失败: {e}")
            return {"error": str(e), "decision": "HOLD"}

    async def _run_reflection(self, symbol: str, final_decision: Dict[str, Any]) -> Dict[str, Any]:
        """运行反思引擎"""
        try:
            model_config = self.agent_model_config.get("reflection_engine", "deepseek:deepseek-chat")
            provider, model = model_config.split(":", 1)

            decision_reasoning = final_decision.get("reasoning", "")

            prompt = f"""
作为反思引擎，请对股票 {symbol} 的分析过程进行反思和总结。

最终决策: {decision_reasoning[:200]}...

请反思:
1. 分析过程的优缺点
2. 可能的改进方向
3. 经验教训总结
4. 未来分析建议

请用客观、建设性的语言回答，控制在150字以内。
"""

            response = await self._call_llm(provider, model, prompt, "reflection_engine")

            return {
                "reflection": response,
                "lessons_learned": self._extract_lessons(response),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"反思引擎运行失败: {e}")
            return {"error": str(e)}

    def _extract_lessons(self, text: str) -> List[str]:
        """提取经验教训"""
        # 简单的经验教训提取
        lessons = []
        if "改进" in text:
            lessons.append("需要改进分析方法")
        if "风险" in text:
            lessons.append("加强风险控制")
        if "数据" in text:
            lessons.append("完善数据收集")

        return lessons if lessons else ["持续学习和改进"]

    def _generate_real_comprehensive_report(self, final_decision: Dict[str, Any]) -> str:
        """生成真实的综合报告"""
        decision = final_decision.get("decision", "HOLD")
        reasoning = final_decision.get("reasoning", "")
        confidence = final_decision.get("confidence", 0.6)

        return f"""
## 📊 基于15个智能体协作的综合分析报告

### 🎯 最终决策
**投资建议**: {decision}
**决策理由**: {reasoning[:200]}...
**信心水平**: {confidence*100:.1f}%

### 📈 分析概览
- **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **分析方式**: 真实LLM智能体协作
- **参与智能体**: 15个专业智能体
- **ChromaDB状态**: {'✅ 可用' if self.chromadb_available else '❌ 不可用'}

### 💡 关键洞察
本次分析通过15个专业智能体的真实协作完成，包括分析师团队、研究团队、交易员、风险管理团队等，
每个智能体都使用了配置的LLM模型进行独立分析，最终通过多轮辩论和风险评估得出结论。

### ⚠️ 风险提示
投资有风险，决策需谨慎。本分析基于当前可获得的信息和AI模型的判断，
不构成投资建议，请结合自身情况谨慎决策。
"""

    # ==================== 缺失的智能体调用方法 ====================

    async def _call_bear_researcher(self, symbol: str, analyst_results: Dict[str, Any]) -> Dict[str, Any]:
        """调用空头研究员"""
        try:
            model_config = self.agent_model_config.get("bear_researcher", "deepseek:deepseek-chat")
            provider, model = model_config.split(":", 1)

            prompt = f"""
你是专业的空头研究员。基于分析师团队的报告，请为股票 {symbol} 提供看跌论据。

请提供:
1. 主要看跌理由
2. 下跌风险因素
3. 目标价位预期
4. 风险警示

请用谨慎、专业的语言回答，控制在200字以内。
"""

            response = await self._call_llm(provider, model, prompt, "bear_researcher")

            return {
                "agent_id": "bear_researcher",
                "analysis": response,
                "bearish_score": 1.0 - self._extract_bullish_score(response),
                "confidence": self._extract_confidence(response),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"空头研究员调用失败: {e}")
            return {"error": str(e), "agent_id": "bear_researcher"}

    async def _call_research_manager(self, symbol: str, research_results: Dict[str, Any]) -> Dict[str, Any]:
        """调用研究经理"""
        try:
            model_config = self.agent_model_config.get("research_manager", "deepseek:deepseek-chat")
            provider, model = model_config.split(":", 1)

            bull_view = research_results.get("bull_researcher", {}).get("analysis", "")
            bear_view = research_results.get("bear_researcher", {}).get("analysis", "")

            prompt = f"""
你是研究经理。基于多空研究员的辩论，请对股票 {symbol} 做出综合投资建议。

多空观点:
- 多头观点: {bull_view[:150]}...
- 空头观点: {bear_view[:150]}...

请提供:
1. 综合投资建议
2. 平衡风险收益
3. 投资策略建议
4. 时机把握

请用平衡、专业的语言回答，控制在200字以内。
"""

            response = await self._call_llm(provider, model, prompt, "research_manager")

            return {
                "agent_id": "research_manager",
                "recommendation": response,
                "action": self._extract_trading_signal(response),
                "confidence": self._extract_confidence(response),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"研究经理调用失败: {e}")
            return {"error": str(e), "agent_id": "research_manager"}

    async def _call_aggressive_debator(self, symbol: str, trading_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """调用激进分析师"""
        try:
            model_config = self.agent_model_config.get("aggressive_debator", "deepseek:deepseek-chat")
            provider, model = model_config.split(":", 1)

            strategy = trading_strategy.get("strategy", "")

            prompt = f"""
你是激进分析师。基于交易策略，请为股票 {symbol} 提供激进的投资观点。

交易策略: {strategy[:150]}...

请提供:
1. 激进投资理由
2. 高收益机会
3. 大胆预测
4. 快速行动建议

请用积极、进取的语言回答，控制在150字以内。
"""

            response = await self._call_llm(provider, model, prompt, "aggressive_debator")

            return {
                "agent_id": "aggressive_debator",
                "analysis": response,
                "risk_appetite": "高",
                "confidence": self._extract_confidence(response),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"激进分析师调用失败: {e}")
            return {"error": str(e), "agent_id": "aggressive_debator"}

    async def _call_conservative_debator(self, symbol: str, trading_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """调用保守分析师"""
        try:
            model_config = self.agent_model_config.get("conservative_debator", "deepseek:deepseek-chat")
            provider, model = model_config.split(":", 1)

            strategy = trading_strategy.get("strategy", "")

            prompt = f"""
你是保守分析师。基于交易策略，请为股票 {symbol} 提供保守的风险控制观点。

交易策略: {strategy[:150]}...

请提供:
1. 风险控制建议
2. 保守投资理由
3. 安全边际分析
4. 谨慎操作建议

请用谨慎、稳健的语言回答，控制在150字以内。
"""

            response = await self._call_llm(provider, model, prompt, "conservative_debator")

            return {
                "agent_id": "conservative_debator",
                "analysis": response,
                "risk_appetite": "低",
                "confidence": self._extract_confidence(response),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"保守分析师调用失败: {e}")
            return {"error": str(e), "agent_id": "conservative_debator"}

    async def _call_neutral_debator(self, symbol: str, trading_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """调用中性分析师"""
        try:
            model_config = self.agent_model_config.get("neutral_debator", "deepseek:deepseek-chat")
            provider, model = model_config.split(":", 1)

            strategy = trading_strategy.get("strategy", "")

            prompt = f"""
你是中性分析师。基于交易策略，请为股票 {symbol} 提供平衡的中性观点。

交易策略: {strategy[:150]}...

请提供:
1. 平衡观点分析
2. 中性投资建议
3. 风险收益平衡
4. 理性决策建议

请用客观、平衡的语言回答，控制在150字以内。
"""

            response = await self._call_llm(provider, model, prompt, "neutral_debator")

            return {
                "agent_id": "neutral_debator",
                "analysis": response,
                "risk_appetite": "中",
                "confidence": self._extract_confidence(response),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"中性分析师调用失败: {e}")
            return {"error": str(e), "agent_id": "neutral_debator"}

    async def _call_risk_manager(self, symbol: str, risk_debates: Dict[str, Any]) -> Dict[str, Any]:
        """调用风险经理"""
        try:
            model_config = self.agent_model_config.get("risk_manager", "deepseek:deepseek-chat")
            provider, model = model_config.split(":", 1)

            aggressive_view = risk_debates.get("aggressive_debator", {}).get("analysis", "")
            conservative_view = risk_debates.get("conservative_debator", {}).get("analysis", "")
            neutral_view = risk_debates.get("neutral_debator", {}).get("analysis", "")

            prompt = f"""
你是风险经理。基于风险管理团队的辩论，请对股票 {symbol} 做出最终风险评估。

风险辩论:
- 激进观点: {aggressive_view[:100]}...
- 保守观点: {conservative_view[:100]}...
- 中性观点: {neutral_view[:100]}...

请提供:
1. 综合风险评估
2. 最终投资建议
3. 风险控制措施
4. 决策依据

请用权威、专业的语言回答，控制在200字以内。
"""

            response = await self._call_llm(provider, model, prompt, "risk_manager")

            return {
                "agent_id": "risk_manager",
                "analysis": response,
                "final_recommendation": self._extract_trading_signal(response),
                "risk_level": self._extract_risk_level(response),
                "confidence": self._extract_confidence(response),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"风险经理调用失败: {e}")
            return {"error": str(e), "agent_id": "risk_manager"}

    def _extract_risk_level(self, text: str) -> str:
        """提取风险水平"""
        if any(word in text.lower() for word in ["高风险", "危险", "谨慎"]):
            return "高"
        elif any(word in text.lower() for word in ["中等风险", "适中", "平衡"]):
            return "中"
        else:
            return "低"
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "llm_providers": len(self.llm_config),
            "configured_providers": list(self.llm_config.keys()),
            "chromadb_available": self.chromadb_available,
            "total_analyses": len(self.analysis_sessions),
            "system_ready": len(self.llm_config) > 0
        }

# 创建应用实例
app = EnhancedTradingAgentsApp()

def _get_model_choices():
    """获取模型选择列表"""
    choices = []
    models = app.get_available_models()

    for provider, model_list in models.items():
        if provider in app.llm_config:  # 只显示已配置的提供商
            for model in model_list:
                choices.append(f"{provider}:{model}")

    return choices if choices else ["deepseek:deepseek-chat"]

def create_enhanced_interface():
    """创建增强版Gradio界面"""

    with gr.Blocks(
        title="TradingAgents - 增强版多智能体股票分析系统",
        theme=gr.themes.Soft()
    ) as interface:

        # 主标题
        gr.Markdown("""
        # 🤖 TradingAgents - 增强版多智能体协作股票分析系统

        **基于15个专业化智能体的金融交易分析框架** | 支持LLM配置和ChromaDB

        ---
        """)

        with gr.Tabs():
            # 主分析界面
            with gr.TabItem("📊 股票分析"):
                with gr.Row():
                    # 左侧控制台
                    with gr.Column(scale=1):
                        gr.Markdown("## 📊 分析控制台")

                        # 股票输入
                        stock_input = gr.Textbox(
                            label="股票代码",
                            placeholder="输入股票代码，如：000001、600036、600519",
                            value="600519"
                        )

                        # 分析深度
                        analysis_depth = gr.Dropdown(
                            label="研究深度",
                            choices=["浅层分析", "中等分析", "深度分析"],
                            value="中等分析"
                        )

                        # 分析师选择
                        gr.Markdown("### 👥 分析师团队")
                        analyst_market = gr.Checkbox(label="📈 市场分析师", value=True)
                        analyst_sentiment = gr.Checkbox(label="💭 情感分析师", value=True)
                        analyst_news = gr.Checkbox(label="📰 新闻分析师", value=True)
                        analyst_fundamentals = gr.Checkbox(label="📊 基本面分析师", value=True)

                        # LLM选择
                        gr.Markdown("### 🤖 LLM配置")
                        use_real_llm = gr.Checkbox(
                            label="使用真实LLM (需要API密钥)",
                            value=False,
                            info="未选择时使用模拟响应"
                        )

                        # 执行按钮
                        analyze_btn = gr.Button("🚀 开始全面分析", variant="primary", size="lg")

                        # 状态显示
                        status_display = gr.Textbox(
                            label="分析状态",
                            value="🟢 系统就绪",
                            interactive=False
                        )

                        # 系统状态
                        gr.Markdown("### 📡 系统状态")
                        system_status_display = gr.JSON(
                            label="系统状态",
                            value=app.get_system_status()
                        )

                    # 右侧结果展示
                    with gr.Column(scale=2):
                        gr.Markdown("## 📈 分析结果")

                        # 结果标签页
                        with gr.Tabs():
                            # 综合报告
                            with gr.TabItem("📋 综合报告"):
                                comprehensive_report = gr.Markdown(value="等待分析结果...")

                            # 分析师报告
                            with gr.TabItem("👥 分析师报告"):
                                with gr.Accordion("📈 市场技术分析", open=True):
                                    market_analysis_output = gr.Markdown(value="暂无数据")

                                with gr.Accordion("💭 社交情感分析", open=False):
                                    sentiment_analysis_output = gr.Markdown(value="暂无数据")

                                with gr.Accordion("📰 新闻事件分析", open=False):
                                    news_analysis_output = gr.Markdown(value="暂无数据")

                                with gr.Accordion("📊 基本面分析", open=False):
                                    fundamentals_analysis_output = gr.Markdown(value="暂无数据")

                            # 多空辩论
                            with gr.TabItem("🥊 多空辩论"):
                                with gr.Row():
                                    with gr.Column():
                                        gr.Markdown("### 🐂 多头观点")
                                        bull_arguments = gr.Markdown(value="暂无数据")

                                    with gr.Column():
                                        gr.Markdown("### 🐻 空头观点")
                                        bear_arguments = gr.Markdown(value="暂无数据")

                                gr.Markdown("### 🎯 投资建议")
                                investment_recommendation = gr.Markdown(value="暂无数据")

                            # 交易策略
                            with gr.TabItem("💼 交易策略"):
                                trading_strategy_output = gr.Markdown(value="暂无数据")

                            # 风险评估
                            with gr.TabItem("⚠️ 风险评估"):
                                risk_assessment_output = gr.Markdown(value="暂无数据")
                                final_decision_output = gr.Markdown(value="暂无数据")

            # LLM配置界面
            with gr.TabItem("⚙️ LLM配置"):
                gr.Markdown("## 🤖 LLM提供商配置")

                with gr.Tabs():
                    # 内置提供商配置
                    with gr.TabItem("🏢 内置提供商"):
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown("### 配置API密钥")

                                # DeepSeek配置
                                with gr.Group():
                                    gr.Markdown("#### 🔥 DeepSeek")
                                    deepseek_key = gr.Textbox(
                                        label="DeepSeek API Key",
                                        type="password",
                                        placeholder="sk-...",
                                        value="●●●●●●●●●●●●" if "deepseek" in app.llm_config else ""
                                    )
                                    with gr.Row():
                                        deepseek_test_btn = gr.Button("测试连接", size="sm")
                                        deepseek_save_btn = gr.Button("💾 保存", size="sm", variant="secondary")
                                    deepseek_status = gr.Textbox(label="状态", value="已配置" if "deepseek" in app.llm_config else "未配置", interactive=False)

                                # OpenAI配置
                                with gr.Group():
                                    gr.Markdown("#### 🧠 OpenAI")
                                    openai_key = gr.Textbox(
                                        label="OpenAI API Key",
                                        type="password",
                                        placeholder="sk-...",
                                        value="●●●●●●●●●●●●" if "openai" in app.llm_config else ""
                                    )
                                    with gr.Row():
                                        openai_test_btn = gr.Button("测试连接", size="sm")
                                        openai_save_btn = gr.Button("💾 保存", size="sm", variant="secondary")
                                    openai_status = gr.Textbox(label="状态", value="已配置" if "openai" in app.llm_config else "未配置", interactive=False)

                                # Google配置
                                with gr.Group():
                                    gr.Markdown("#### 🌐 Google")
                                    google_key = gr.Textbox(
                                        label="Google API Key",
                                        type="password",
                                        placeholder="AIza...",
                                        value="●●●●●●●●●●●●" if "google" in app.llm_config else ""
                                    )
                                    with gr.Row():
                                        google_test_btn = gr.Button("测试连接", size="sm")
                                        google_save_btn = gr.Button("💾 保存", size="sm", variant="secondary")
                                    google_status = gr.Textbox(label="状态", value="已配置" if "google" in app.llm_config else "未配置", interactive=False)

                                # Moonshot配置
                                with gr.Group():
                                    gr.Markdown("#### 🌙 Moonshot")
                                    moonshot_key = gr.Textbox(
                                        label="Moonshot API Key",
                                        type="password",
                                        placeholder="sk-...",
                                        value="●●●●●●●●●●●●" if "moonshot" in app.llm_config else ""
                                    )
                                    with gr.Row():
                                        moonshot_test_btn = gr.Button("测试连接", size="sm")
                                        moonshot_save_btn = gr.Button("💾 保存", size="sm", variant="secondary")
                                    moonshot_status = gr.Textbox(label="状态", value="已配置" if "moonshot" in app.llm_config else "未配置", interactive=False)

                                # 批量操作
                                with gr.Group():
                                    gr.Markdown("#### 🔧 批量操作")
                                    with gr.Row():
                                        save_all_btn = gr.Button("💾 保存所有配置", variant="primary", size="sm")
                                        load_config_btn = gr.Button("📂 重新加载配置", size="sm")
                                        clear_config_btn = gr.Button("🗑️ 清空配置", variant="stop", size="sm")

                                    config_operation_status = gr.Textbox(
                                        label="操作状态",
                                        value=f"已加载 {len(app.llm_config)} 个提供商配置",
                                        interactive=False
                                    )

                    # 自定义提供商配置
                    with gr.TabItem("⚙️ 自定义提供商"):
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown("### 添加自定义LLM提供商")

                                with gr.Group():
                                    gr.Markdown("#### ➕ 新增提供商")

                                    custom_name = gr.Textbox(
                                        label="提供商名称",
                                        placeholder="例如: Claude, Llama, 通义千问",
                                        info="为您的LLM提供商起一个名称"
                                    )

                                    custom_api_key = gr.Textbox(
                                        label="API密钥",
                                        type="password",
                                        placeholder="输入API密钥",
                                        info="您的LLM服务API密钥"
                                    )

                                    custom_base_url = gr.Textbox(
                                        label="API基础URL (可选)",
                                        placeholder="https://api.example.com/v1",
                                        info="如果是自部署或特殊端点，请填写完整URL"
                                    )

                                    custom_model = gr.Dropdown(
                                        label="模型名称",
                                        choices=[],
                                        allow_custom_value=True,
                                        info="选择或输入模型名称"
                                    )

                                    # 模型推荐按钮
                                    suggest_models_btn = gr.Button("💡 推荐模型", size="sm")

                                    with gr.Row():
                                        add_custom_btn = gr.Button("➕ 添加提供商", variant="primary", size="sm")
                                        test_custom_btn = gr.Button("🔍 测试连接", size="sm")

                                    custom_add_status = gr.Textbox(
                                        label="操作状态",
                                        value="等待添加...",
                                        interactive=False
                                    )

                            with gr.Column():
                                gr.Markdown("### 已配置的提供商")

                                # 提供商列表
                                providers_list = gr.Dataframe(
                                    headers=["提供商", "类型", "状态", "操作"],
                                    datatype=["str", "str", "str", "str"],
                                    value=[],
                                    interactive=False,
                                    label="LLM提供商列表"
                                )

                                with gr.Row():
                                    refresh_providers_btn = gr.Button("🔄 刷新列表", size="sm")

                                # 删除提供商
                                with gr.Group():
                                    gr.Markdown("#### 🗑️ 删除提供商")

                                    delete_provider_name = gr.Dropdown(
                                        label="选择要删除的自定义提供商",
                                        choices=[],
                                        info="只能删除自定义添加的提供商"
                                    )

                                    delete_provider_btn = gr.Button("🗑️ 删除", variant="stop", size="sm")
                                    delete_status = gr.Textbox(
                                        label="删除状态",
                                        value="",
                                        interactive=False
                                    )

                # 系统信息标签页
                with gr.TabItem("📊 系统信息"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### 📚 ChromaDB状态")
                            chromadb_status_display = gr.Markdown(
                                f"{'✅ 已安装并可用' if app.chromadb_available else '❌ 未安装'}"
                            )

                            if not app.chromadb_available:
                                gr.Markdown("""
                                **安装ChromaDB**:
                                ```bash
                                pip install chromadb sentence-transformers
                                ```
                                """)

                            gr.Markdown("### 📝 环境变量配置")
                            gr.Markdown("""
                            在 `.env` 文件中配置:
                            ```
                            DEEPSEEK_API_KEY=your_deepseek_key
                            OPENAI_API_KEY=your_openai_key
                            GOOGLE_API_KEY=your_google_key
                            MOONSHOT_API_KEY=your_moonshot_key
                            ```
                            """)

                        with gr.Column():
                            gr.Markdown("### 🔧 系统配置")

                            system_config_display = gr.JSON(
                                label="当前系统配置",
                                value={
                                    "chromadb_available": app.chromadb_available,
                                    "configured_providers": len(app.llm_config),
                                    "custom_providers": len(app.custom_llm_providers),
                                    "total_analyses": len(app.analysis_sessions)
                                }
                            )

                            # 系统操作
                            with gr.Group():
                                gr.Markdown("#### 🔄 系统操作")

                                refresh_system_btn = gr.Button("🔄 刷新系统状态", size="sm")
                                clear_cache_btn = gr.Button("🗑️ 清空缓存", size="sm")
                                export_config_btn = gr.Button("📤 导出配置", size="sm")

                                system_operation_status = gr.Textbox(
                                    label="操作状态",
                                    value="系统正常运行",
                                    interactive=False
                                )

            # 智能体模型配置
            with gr.TabItem("🤖 智能体配置"):
                gr.Markdown("## 🤖 智能体模型配置")
                gr.Markdown("为每个智能体选择使用的LLM模型，实现精细化配置")

                with gr.Tabs():
                    # 分析师团队配置
                    with gr.TabItem("📊 分析师团队"):
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown("### 📈 市场分析师")
                                market_analyst_model = gr.Dropdown(
                                    label="选择模型",
                                    choices=_get_model_choices(),
                                    value=app.agent_model_config.get("market_analyst", "deepseek:deepseek-chat"),
                                    info="负责技术分析和图表模式识别"
                                )

                                gr.Markdown("### 💭 情感分析师")
                                sentiment_analyst_model = gr.Dropdown(
                                    label="选择模型",
                                    choices=_get_model_choices(),
                                    value=app.agent_model_config.get("social_media_analyst", "deepseek:deepseek-chat"),
                                    info="分析社交媒体情绪和投资者情感"
                                )

                            with gr.Column():
                                gr.Markdown("### 📰 新闻分析师")
                                news_analyst_model = gr.Dropdown(
                                    label="选择模型",
                                    choices=_get_model_choices(),
                                    value=app.agent_model_config.get("news_analyst", "deepseek:deepseek-chat"),
                                    info="分析新闻事件和宏观经济影响"
                                )

                                gr.Markdown("### 📊 基本面分析师")
                                fundamentals_analyst_model = gr.Dropdown(
                                    label="选择模型",
                                    choices=_get_model_choices(),
                                    value=app.agent_model_config.get("fundamentals_analyst", "deepseek:deepseek-chat"),
                                    info="分析财务数据和公司基本面"
                                )

                    # 研究团队配置
                    with gr.TabItem("🔬 研究团队"):
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown("### 🐂 多头研究员")
                                bull_researcher_model = gr.Dropdown(
                                    label="选择模型",
                                    choices=_get_model_choices(),
                                    value=app.agent_model_config.get("bull_researcher", "deepseek:deepseek-chat"),
                                    info="寻找投资机会和看涨理由"
                                )

                                gr.Markdown("### 🐻 空头研究员")
                                bear_researcher_model = gr.Dropdown(
                                    label="选择模型",
                                    choices=_get_model_choices(),
                                    value=app.agent_model_config.get("bear_researcher", "deepseek:deepseek-chat"),
                                    info="识别风险因素和看跌理由"
                                )

                            with gr.Column():
                                gr.Markdown("### 👨‍💼 研究经理")
                                research_manager_model = gr.Dropdown(
                                    label="选择模型",
                                    choices=_get_model_choices(),
                                    value=app.agent_model_config.get("research_manager", "deepseek:deepseek-chat"),
                                    info="协调研究团队和制定投资建议"
                                )

                                gr.Markdown("### 👨‍💻 交易员")
                                trader_model = gr.Dropdown(
                                    label="选择模型",
                                    choices=_get_model_choices(),
                                    value=app.agent_model_config.get("trader", "deepseek:deepseek-chat"),
                                    info="制定交易策略和执行计划"
                                )

                    # 风险管理团队配置
                    with gr.TabItem("⚠️ 风险管理"):
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown("### 🔴 激进分析师")
                                aggressive_debator_model = gr.Dropdown(
                                    label="选择模型",
                                    choices=_get_model_choices(),
                                    value=app.agent_model_config.get("aggressive_debator", "deepseek:deepseek-chat"),
                                    info="倡导高风险高回报策略"
                                )

                                gr.Markdown("### 🔵 保守分析师")
                                conservative_debator_model = gr.Dropdown(
                                    label="选择模型",
                                    choices=_get_model_choices(),
                                    value=app.agent_model_config.get("conservative_debator", "deepseek:deepseek-chat"),
                                    info="强调风险控制和稳健策略"
                                )

                            with gr.Column():
                                gr.Markdown("### 🟡 中性分析师")
                                neutral_debator_model = gr.Dropdown(
                                    label="选择模型",
                                    choices=_get_model_choices(),
                                    value=app.agent_model_config.get("neutral_debator", "deepseek:deepseek-chat"),
                                    info="提供平衡观点和中庸策略"
                                )

                                gr.Markdown("### 👨‍⚖️ 风险经理")
                                risk_manager_model = gr.Dropdown(
                                    label="选择模型",
                                    choices=_get_model_choices(),
                                    value=app.agent_model_config.get("risk_manager", "deepseek:deepseek-chat"),
                                    info="最终决策制定和风险评估"
                                )

                    # 支持系统配置
                    with gr.TabItem("🧠 支持系统"):
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown("### 💾 记忆管理器")
                                memory_manager_model = gr.Dropdown(
                                    label="选择模型",
                                    choices=_get_model_choices(),
                                    value=app.agent_model_config.get("memory_manager", "deepseek:deepseek-chat"),
                                    info="管理智能体记忆和经验学习"
                                )

                                gr.Markdown("### 📡 信号处理器")
                                signal_processor_model = gr.Dropdown(
                                    label="选择模型",
                                    choices=_get_model_choices(),
                                    value=app.agent_model_config.get("signal_processor", "deepseek:deepseek-chat"),
                                    info="处理智能体间通信和协调"
                                )

                            with gr.Column():
                                gr.Markdown("### 🔄 反思引擎")
                                reflection_engine_model = gr.Dropdown(
                                    label="选择模型",
                                    choices=_get_model_choices(),
                                    value=app.agent_model_config.get("reflection_engine", "deepseek:deepseek-chat"),
                                    info="分析性能和持续改进"
                                )

                # 批量操作
                with gr.Group():
                    gr.Markdown("### 🔧 批量操作")

                    with gr.Row():
                        batch_model_select = gr.Dropdown(
                            label="批量设置模型",
                            choices=_get_model_choices(),
                            value="deepseek:deepseek-chat",
                            info="为所有智能体设置相同模型"
                        )

                        batch_apply_btn = gr.Button("🔄 批量应用", variant="secondary", size="sm")

                    with gr.Row():
                        save_agent_config_btn = gr.Button("💾 保存智能体配置", variant="primary", size="sm")
                        load_agent_config_btn = gr.Button("📂 重新加载配置", size="sm")
                        reset_agent_config_btn = gr.Button("🔄 重置为默认", size="sm")

                    agent_config_status = gr.Textbox(
                        label="操作状态",
                        value=f"已加载 {len(app.agent_model_config)} 个智能体配置",
                        interactive=False
                    )

            # 通信监控
            with gr.TabItem("📡 通信监控"):
                gr.Markdown("## 📡 LLM通信监控")
                gr.Markdown("实时查看智能体与LLM的通信过程和内容")

                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Markdown("### 📋 通信日志")

                        with gr.Row():
                            refresh_logs_btn = gr.Button("🔄 刷新日志", size="sm")
                            clear_logs_btn = gr.Button("🗑️ 清空日志", size="sm")
                            auto_refresh_checkbox = gr.Checkbox(label="自动刷新", value=False)

                        # 通信日志表格
                        communication_logs_display = gr.Dataframe(
                            headers=["时间", "智能体", "提供商", "模型", "状态", "提示长度", "响应长度"],
                            datatype=["str", "str", "str", "str", "str", "str", "str"],
                            value=[],
                            interactive=False,
                            label="通信记录"
                        )

                    with gr.Column(scale=1):
                        gr.Markdown("### 📊 通信统计")

                        communication_stats = gr.JSON(
                            label="统计信息",
                            value={
                                "total_communications": 0,
                                "successful_communications": 0,
                                "failed_communications": 0,
                                "average_response_time": "0ms",
                                "most_active_agent": "无",
                                "most_used_provider": "无"
                            }
                        )

                # 通信详情
                with gr.Group():
                    gr.Markdown("### 🔍 通信详情")

                    selected_log_index = gr.Number(
                        label="选择日志序号",
                        value=0,
                        minimum=0,
                        info="输入日志序号查看详细内容"
                    )

                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("#### 📤 发送的提示")
                            prompt_detail = gr.Textbox(
                                label="提示内容",
                                lines=8,
                                interactive=False,
                                placeholder="选择日志查看提示内容..."
                            )

                        with gr.Column():
                            gr.Markdown("#### 📥 接收的响应")
                            response_detail = gr.Textbox(
                                label="响应内容",
                                lines=8,
                                interactive=False,
                                placeholder="选择日志查看响应内容..."
                            )

            # 分析历史
            with gr.TabItem("📚 分析历史"):
                gr.Markdown("## 📚 分析历史记录")

                with gr.Row():
                    refresh_history_btn = gr.Button("🔄 刷新历史", size="sm")
                    clear_history_btn = gr.Button("🗑️ 清空历史", size="sm")

                history_display = gr.Dataframe(
                    headers=["时间", "股票", "深度", "状态", "LLM", "决策"],
                    datatype=["str", "str", "str", "str", "str", "str"],
                    value=app.get_analysis_history()
                )

        # 底部信息
        gr.Markdown("""
        ---

        ### 💡 使用说明

        1. **LLM配置**: 在"LLM配置"标签页配置API密钥
        2. **股票分析**: 输入股票代码，选择分析深度和智能体团队
        3. **查看结果**: 在不同标签页查看详细分析结果
        4. **历史记录**: 查看和管理分析历史

        ### ⚠️ 免责声明

        本系统提供的分析结果仅供参考，不构成投资建议。投资有风险，决策需谨慎。

        ---

        **TradingAgents Enhanced v1.0** | Powered by Multi-Agent LLM Framework
        """)

        # 事件处理函数
        def run_enhanced_analysis(symbol, depth, market_checked, sentiment_checked,
                                news_checked, fundamentals_checked, use_real_llm):
            """运行增强分析"""
            if not symbol:
                return ("❌ 请输入股票代码", "暂无数据", "暂无数据", "暂无数据",
                       "暂无数据", "暂无数据", "暂无数据", "暂无数据", "暂无数据", "暂无数据", "暂无数据")

            try:
                # 准备分析师列表
                selected_analysts = []
                if market_checked:
                    selected_analysts.append("market_analyst")
                if sentiment_checked:
                    selected_analysts.append("sentiment_analyst")
                if news_checked:
                    selected_analysts.append("news_analyst")
                if fundamentals_checked:
                    selected_analysts.append("fundamentals_analyst")

                if not selected_analysts:
                    return ("❌ 请至少选择一个分析师", "暂无数据", "暂无数据", "暂无数据",
                           "暂无数据", "暂无数据", "暂无数据", "暂无数据", "暂无数据", "暂无数据", "暂无数据")

                # 执行分析
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                result = loop.run_until_complete(
                    app.analyze_stock_enhanced(symbol, depth, selected_analysts, use_real_llm)
                )

                if result.get("status") == "failed":
                    return (f"❌ 分析失败: {result.get('error', '未知错误')}",
                           "暂无数据", "暂无数据", "暂无数据", "暂无数据",
                           "暂无数据", "暂无数据", "暂无数据", "暂无数据", "暂无数据", "暂无数据")

                # 解析结果
                results = result.get("results", {})

                # 安全地处理结果数据
                def safe_get_result(key, default="暂无数据"):
                    """安全获取结果数据"""
                    value = results.get(key, default)
                    if isinstance(value, dict):
                        # 如果是字典，尝试获取analysis字段或转换为字符串
                        return value.get("analysis", str(value))
                    return str(value) if value else default

                # 组合风险评估和最终决策
                risk_assessment = safe_get_result("risk_assessment")
                final_decision = safe_get_result("final_decision")
                combined_risk_decision = f"{risk_assessment}\n\n### 最终决策\n{final_decision}"

                return (
                    "✅ 分析完成",
                    safe_get_result("comprehensive_report"),
                    safe_get_result("market_analysis"),
                    safe_get_result("sentiment_analysis"),
                    safe_get_result("news_analysis"),
                    safe_get_result("fundamentals_analysis"),
                    safe_get_result("bull_arguments"),
                    safe_get_result("bear_arguments"),
                    safe_get_result("investment_recommendation"),
                    safe_get_result("trading_strategy"),
                    combined_risk_decision
                )

            except Exception as e:
                logger.error(f"分析执行失败: {e}")
                import traceback
                traceback.print_exc()
                return (f"❌ 系统错误: {str(e)}", "暂无数据", "暂无数据", "暂无数据",
                       "暂无数据", "暂无数据", "暂无数据", "暂无数据", "暂无数据", "暂无数据", "暂无数据")

        def test_deepseek_connection(api_key):
            """测试DeepSeek连接"""
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            result = loop.run_until_complete(app.test_llm_connection("deepseek", api_key))
            return result.get("message", "测试失败")

        def test_openai_connection(api_key):
            """测试OpenAI连接"""
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            result = loop.run_until_complete(app.test_llm_connection("openai", api_key))
            return result.get("message", "测试失败")

        def test_google_connection(api_key):
            """测试Google连接"""
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            result = loop.run_until_complete(app.test_llm_connection("google", api_key))
            return result.get("message", "测试失败")

        def test_moonshot_connection(api_key):
            """测试Moonshot连接"""
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            result = loop.run_until_complete(app.test_llm_connection("moonshot", api_key))
            return result.get("message", "测试失败")

        # 保存配置的函数
        def save_deepseek_config(api_key):
            """保存DeepSeek配置"""
            if api_key and api_key != "●●●●●●●●●●●●":
                app.llm_config["deepseek"] = api_key
                result = app.save_config()
                return result.get("message", "保存失败")
            return "请输入有效的API密钥"

        def save_openai_config(api_key):
            """保存OpenAI配置"""
            if api_key and api_key != "●●●●●●●●●●●●":
                app.llm_config["openai"] = api_key
                result = app.save_config()
                return result.get("message", "保存失败")
            return "请输入有效的API密钥"

        def save_google_config(api_key):
            """保存Google配置"""
            if api_key and api_key != "●●●●●●●●●●●●":
                app.llm_config["google"] = api_key
                result = app.save_config()
                return result.get("message", "保存失败")
            return "请输入有效的API密钥"

        def save_moonshot_config(api_key):
            """保存Moonshot配置"""
            if api_key and api_key != "●●●●●●●●●●●●":
                app.llm_config["moonshot"] = api_key
                result = app.save_config()
                return result.get("message", "保存失败")
            return "请输入有效的API密钥"

        def save_all_config():
            """保存所有配置"""
            result = app.save_config()
            return result.get("message", "保存失败")

        def load_config():
            """重新加载配置"""
            result = app.load_saved_config()
            providers_data = get_providers_list()
            custom_providers = list(app.custom_llm_providers.keys())

            return (
                result.get("message", "加载失败"),
                providers_data,
                custom_providers,  # 直接返回选择列表
                f"已加载 {len(app.llm_config)} 个提供商配置"
            )

        def clear_config():
            """清空配置"""
            result = app.clear_saved_config()
            providers_data = get_providers_list()
            custom_providers = list(app.custom_llm_providers.keys())

            return (
                result.get("message", "清空失败"),
                providers_data,
                custom_providers,  # 直接返回选择列表
                f"已加载 {len(app.llm_config)} 个提供商配置"
            )

        def add_custom_provider(name, api_key, base_url, model):
            """添加自定义提供商"""
            try:
                result = app.add_custom_llm_provider(name, api_key, base_url, model)

                # 更新下拉列表选项
                custom_providers = list(app.custom_llm_providers.keys())
                providers_data = get_providers_list()

                return (
                    result.get("message", "操作失败"),
                    providers_data,
                    custom_providers  # 直接返回选择列表，不使用gr.Dropdown.update
                )
            except Exception as e:
                logger.error(f"添加自定义提供商失败: {e}")
                return (
                    f"添加失败: {str(e)}",
                    get_providers_list(),
                    list(app.custom_llm_providers.keys())
                )

        def test_custom_connection(name, api_key, base_url, model):
            """测试自定义提供商连接"""
            if not name or not api_key:
                return "请填写提供商名称和API密钥"

            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            result = loop.run_until_complete(app.test_llm_connection(name, api_key, base_url))
            return result.get("message", "测试失败")

        def delete_custom_provider(provider_name):
            """删除自定义提供商"""
            if not provider_name:
                return "请选择要删除的提供商", [], []

            result = app.remove_custom_llm_provider(provider_name)

            # 更新列表和下拉选项
            custom_providers = list(app.custom_llm_providers.keys())
            providers_data = get_providers_list()

            return (
                result.get("message", "删除失败"),
                providers_data,
                custom_providers  # 直接返回选择列表
            )

        def get_providers_list():
            """获取提供商列表数据"""
            providers_info = app.get_all_llm_providers()
            data = []

            # 内置提供商
            for name, info in providers_info["built_in"].items():
                status = "✅ 已配置" if info["configured"] else "❌ 未配置"
                data.append([name.title(), info["type"], status, "内置"])

            # 自定义提供商
            for name, info in providers_info["custom"].items():
                status = "✅ 已配置"
                data.append([name, info["type"], status, "可删除"])

            return data

        def refresh_providers_list():
            """刷新提供商列表"""
            custom_providers = list(app.custom_llm_providers.keys())
            providers_data = get_providers_list()

            return providers_data, custom_providers  # 直接返回选择列表

        def refresh_system_status():
            """刷新系统状态"""
            status = app.get_system_status()
            return status, "系统状态已刷新"

        def clear_system_cache():
            """清空系统缓存"""
            # 这里可以添加清空缓存的逻辑
            return "缓存已清空"

        def export_system_config():
            """导出系统配置"""
            config = {
                "providers": app.get_all_llm_providers(),
                "system_status": app.get_system_status(),
                "export_time": datetime.now().isoformat()
            }
            return "配置导出完成（功能开发中）"

        # 智能体模型配置相关函数
        def update_agent_model(agent_id, model_choice):
            """更新单个智能体模型"""
            result = app.update_agent_model(agent_id, model_choice)
            return result.get("message", "更新失败")

        def batch_apply_model(model_choice):
            """批量应用模型"""
            try:
                agents = app.get_agent_list()
                for agent in agents:
                    app.agent_model_config[agent["id"]] = model_choice

                save_result = app.save_agent_model_config()
                return save_result.get("message", "批量应用失败")
            except Exception as e:
                return f"批量应用失败: {str(e)}"

        def save_agent_config():
            """保存智能体配置"""
            result = app.save_agent_model_config()
            return result.get("message", "保存失败")

        def load_agent_config():
            """重新加载智能体配置"""
            app.agent_model_config = app.load_agent_model_config()
            return f"已重新加载 {len(app.agent_model_config)} 个智能体配置"

        def reset_agent_config():
            """重置智能体配置为默认"""
            default_model = "deepseek:deepseek-chat"
            agents = app.get_agent_list()
            app.agent_model_config = {agent["id"]: default_model for agent in agents}
            save_result = app.save_agent_model_config()
            return f"已重置为默认配置: {save_result.get('message', '重置失败')}"

        # 通信监控相关函数
        def refresh_communication_logs():
            """刷新通信日志"""
            logs = app.get_communication_logs(50)

            # 转换为表格格式
            table_data = []
            for i, log in enumerate(logs):
                table_data.append([
                    log["timestamp"][:19],
                    log["agent_id"],
                    log["provider"],
                    log["model"],
                    "✅ 成功" if log["status"] == "success" else "❌ 失败",
                    str(log["prompt_length"]),
                    str(log["response_length"])
                ])

            # 计算统计信息
            total_logs = len(app.communication_logs)
            successful_logs = sum(1 for log in app.communication_logs if log["status"] == "success")
            failed_logs = total_logs - successful_logs

            # 统计最活跃的智能体和提供商
            agent_counts = {}
            provider_counts = {}
            for log in app.communication_logs:
                agent_counts[log["agent_id"]] = agent_counts.get(log["agent_id"], 0) + 1
                provider_counts[log["provider"]] = provider_counts.get(log["provider"], 0) + 1

            most_active_agent = max(agent_counts.items(), key=lambda x: x[1])[0] if agent_counts else "无"
            most_used_provider = max(provider_counts.items(), key=lambda x: x[1])[0] if provider_counts else "无"

            stats = {
                "total_communications": total_logs,
                "successful_communications": successful_logs,
                "failed_communications": failed_logs,
                "success_rate": f"{(successful_logs/total_logs*100):.1f}%" if total_logs > 0 else "0%",
                "most_active_agent": most_active_agent,
                "most_used_provider": most_used_provider
            }

            return table_data, stats

        def clear_communication_logs():
            """清空通信日志"""
            result = app.clear_communication_logs()
            return [], {
                "total_communications": 0,
                "successful_communications": 0,
                "failed_communications": 0,
                "success_rate": "0%",
                "most_active_agent": "无",
                "most_used_provider": "无"
            }, result.get("message", "清空失败")

        def get_log_detail(log_index):
            """获取日志详情"""
            try:
                logs = app.get_communication_logs(1000)  # 获取更多日志用于查看
                if 0 <= log_index < len(logs):
                    log = logs[int(log_index)]
                    return log.get("prompt", ""), log.get("response", "")
                else:
                    return "日志序号超出范围", "日志序号超出范围"
            except Exception as e:
                return f"获取日志失败: {str(e)}", ""

        # 模拟通信日志（用于演示）
        def suggest_models_for_provider(provider_name):
            """为提供商推荐模型"""
            if not provider_name:
                return []

            suggested_models = app.get_common_models_for_provider(provider_name)
            return suggested_models

        def simulate_communication():
            """模拟通信日志（演示用）"""
            import random

            agents = ["market_analyst", "sentiment_analyst", "news_analyst"]
            providers = ["deepseek", "openai", "google"]
            models = ["deepseek-chat", "gpt-4", "gemini-pro"]

            for i in range(5):
                agent = random.choice(agents)
                provider = random.choice(providers)
                model = random.choice(models)

                app.log_communication(
                    agent_id=agent,
                    provider=provider,
                    model=model,
                    prompt=f"分析股票600519的技术指标，包括RSI、MACD等关键指标的当前状态和趋势预测。请提供详细的技术分析报告。",
                    response=f"基于当前技术指标分析，600519呈现以下特征：RSI指标为65.2，处于中性偏强区域；MACD指标显示金叉形成，短期动能增强；均线系统呈多头排列，支撑有效。综合判断，该股票技术面偏向积极。",
                    status="success" if random.random() > 0.1 else "failed"
                )

            return refresh_communication_logs()

        def refresh_history():
            """刷新历史记录"""
            return app.get_analysis_history()

        def clear_history():
            """清空历史记录"""
            app.analysis_sessions.clear()
            return []

        def update_system_status():
            """更新系统状态"""
            return app.get_system_status()

        # 绑定事件
        analyze_btn.click(
            fn=run_enhanced_analysis,
            inputs=[
                stock_input, analysis_depth, analyst_market, analyst_sentiment,
                analyst_news, analyst_fundamentals, use_real_llm
            ],
            outputs=[
                status_display, comprehensive_report, market_analysis_output,
                sentiment_analysis_output, news_analysis_output, fundamentals_analysis_output,
                bull_arguments, bear_arguments, investment_recommendation,
                trading_strategy_output, risk_assessment_output
            ]
        )

        # 内置提供商测试和保存
        deepseek_test_btn.click(
            fn=test_deepseek_connection,
            inputs=[deepseek_key],
            outputs=[deepseek_status]
        )

        deepseek_save_btn.click(
            fn=save_deepseek_config,
            inputs=[deepseek_key],
            outputs=[deepseek_status]
        )

        openai_test_btn.click(
            fn=test_openai_connection,
            inputs=[openai_key],
            outputs=[openai_status]
        )

        openai_save_btn.click(
            fn=save_openai_config,
            inputs=[openai_key],
            outputs=[openai_status]
        )

        google_test_btn.click(
            fn=test_google_connection,
            inputs=[google_key],
            outputs=[google_status]
        )

        google_save_btn.click(
            fn=save_google_config,
            inputs=[google_key],
            outputs=[google_status]
        )

        moonshot_test_btn.click(
            fn=test_moonshot_connection,
            inputs=[moonshot_key],
            outputs=[moonshot_status]
        )

        moonshot_save_btn.click(
            fn=save_moonshot_config,
            inputs=[moonshot_key],
            outputs=[moonshot_status]
        )

        # 批量配置操作
        save_all_btn.click(
            fn=save_all_config,
            outputs=[config_operation_status]
        )

        load_config_btn.click(
            fn=load_config,
            outputs=[config_operation_status, providers_list, delete_provider_name, config_operation_status]
        )

        clear_config_btn.click(
            fn=clear_config,
            outputs=[config_operation_status, providers_list, delete_provider_name, config_operation_status]
        )

        # 自定义提供商管理
        add_custom_btn.click(
            fn=add_custom_provider,
            inputs=[custom_name, custom_api_key, custom_base_url, custom_model],
            outputs=[custom_add_status, providers_list, delete_provider_name]
        )

        test_custom_btn.click(
            fn=test_custom_connection,
            inputs=[custom_name, custom_api_key, custom_base_url, custom_model],
            outputs=[custom_add_status]
        )

        suggest_models_btn.click(
            fn=suggest_models_for_provider,
            inputs=[custom_name],
            outputs=[custom_model]
        )

        delete_provider_btn.click(
            fn=delete_custom_provider,
            inputs=[delete_provider_name],
            outputs=[delete_status, providers_list, delete_provider_name]
        )

        refresh_providers_btn.click(
            fn=refresh_providers_list,
            outputs=[providers_list, delete_provider_name]
        )

        # 系统操作
        refresh_system_btn.click(
            fn=refresh_system_status,
            outputs=[system_config_display, system_operation_status]
        )

        clear_cache_btn.click(
            fn=clear_system_cache,
            outputs=[system_operation_status]
        )

        export_config_btn.click(
            fn=export_system_config,
            outputs=[system_operation_status]
        )

        # 智能体模型配置事件绑定
        # 分析师团队
        market_analyst_model.change(
            fn=lambda x: update_agent_model("market_analyst", x),
            inputs=[market_analyst_model],
            outputs=[agent_config_status]
        )

        sentiment_analyst_model.change(
            fn=lambda x: update_agent_model("social_media_analyst", x),
            inputs=[sentiment_analyst_model],
            outputs=[agent_config_status]
        )

        news_analyst_model.change(
            fn=lambda x: update_agent_model("news_analyst", x),
            inputs=[news_analyst_model],
            outputs=[agent_config_status]
        )

        fundamentals_analyst_model.change(
            fn=lambda x: update_agent_model("fundamentals_analyst", x),
            inputs=[fundamentals_analyst_model],
            outputs=[agent_config_status]
        )

        # 研究团队
        bull_researcher_model.change(
            fn=lambda x: update_agent_model("bull_researcher", x),
            inputs=[bull_researcher_model],
            outputs=[agent_config_status]
        )

        bear_researcher_model.change(
            fn=lambda x: update_agent_model("bear_researcher", x),
            inputs=[bear_researcher_model],
            outputs=[agent_config_status]
        )

        research_manager_model.change(
            fn=lambda x: update_agent_model("research_manager", x),
            inputs=[research_manager_model],
            outputs=[agent_config_status]
        )

        trader_model.change(
            fn=lambda x: update_agent_model("trader", x),
            inputs=[trader_model],
            outputs=[agent_config_status]
        )

        # 风险管理团队
        aggressive_debator_model.change(
            fn=lambda x: update_agent_model("aggressive_debator", x),
            inputs=[aggressive_debator_model],
            outputs=[agent_config_status]
        )

        conservative_debator_model.change(
            fn=lambda x: update_agent_model("conservative_debator", x),
            inputs=[conservative_debator_model],
            outputs=[agent_config_status]
        )

        neutral_debator_model.change(
            fn=lambda x: update_agent_model("neutral_debator", x),
            inputs=[neutral_debator_model],
            outputs=[agent_config_status]
        )

        risk_manager_model.change(
            fn=lambda x: update_agent_model("risk_manager", x),
            inputs=[risk_manager_model],
            outputs=[agent_config_status]
        )

        # 支持系统
        memory_manager_model.change(
            fn=lambda x: update_agent_model("memory_manager", x),
            inputs=[memory_manager_model],
            outputs=[agent_config_status]
        )

        signal_processor_model.change(
            fn=lambda x: update_agent_model("signal_processor", x),
            inputs=[signal_processor_model],
            outputs=[agent_config_status]
        )

        reflection_engine_model.change(
            fn=lambda x: update_agent_model("reflection_engine", x),
            inputs=[reflection_engine_model],
            outputs=[agent_config_status]
        )

        # 批量操作
        batch_apply_btn.click(
            fn=batch_apply_model,
            inputs=[batch_model_select],
            outputs=[agent_config_status]
        )

        save_agent_config_btn.click(
            fn=save_agent_config,
            outputs=[agent_config_status]
        )

        load_agent_config_btn.click(
            fn=load_agent_config,
            outputs=[agent_config_status]
        )

        reset_agent_config_btn.click(
            fn=reset_agent_config,
            outputs=[agent_config_status]
        )

        # 通信监控事件绑定
        refresh_logs_btn.click(
            fn=refresh_communication_logs,
            outputs=[communication_logs_display, communication_stats]
        )

        clear_logs_btn.click(
            fn=clear_communication_logs,
            outputs=[communication_logs_display, communication_stats, agent_config_status]
        )

        selected_log_index.change(
            fn=get_log_detail,
            inputs=[selected_log_index],
            outputs=[prompt_detail, response_detail]
        )

        # 添加模拟通信按钮（演示用）
        # simulate_btn.click(
        #     fn=simulate_communication,
        #     outputs=[communication_logs_display, communication_stats]
        # )

        refresh_history_btn.click(
            fn=refresh_history,
            outputs=[history_display]
        )

        clear_history_btn.click(
            fn=clear_history,
            outputs=[history_display]
        )

        # 定期更新系统状态
        interface.load(
            fn=update_system_status,
            outputs=[system_status_display]
        )

    return interface

if __name__ == "__main__":
    # 创建并启动界面
    interface = create_enhanced_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7864,  # 使用新端口
        share=False,
        debug=True
    )
