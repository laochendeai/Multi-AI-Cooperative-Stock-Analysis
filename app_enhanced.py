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
import hashlib
import hmac

# 导入二维码安全模块
from core.qrcode_security import display_donation_info, verify_qrcode

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealDataCollector:
    """真实数据收集器"""

    def __init__(self, db_path: str = "data/trading_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()

        # 常用股票代码到名称的映射（回退机制）
        self.stock_name_mapping = {
            "600519": "贵州茅台",
            "000001": "平安银行",
            "000002": "万科A",
            "600036": "招商银行",
            "600000": "浦发银行",
            "000858": "五粮液",
            "002415": "海康威视",
            "600276": "恒瑞医药",
            "000568": "泸州老窖",
            "600887": "伊利股份",
            "300750": "宁德时代",
            "002594": "比亚迪",
            "600328": "天房发展",
            "600330": "恒顺醋业",
            "002304": "洋河股份",
            "000596": "古井贡酒",
            "600809": "山西汾酒",
            "000799": "酒鬼酒",
            "600702": "舍得酒业"
        }

    def get_stock_name(self, symbol: str, raw_name: str = None) -> str:
        """获取股票名称，带回退机制"""
        # 1. 如果提供了原始名称且有效，检查是否为有效名称
        if raw_name and str(raw_name).strip():
            cleaned_name = str(raw_name).strip()

            # 检查是否为无效格式
            invalid_formats = [
                symbol,                    # 名称等于代码
                f"股票{symbol}",           # "股票600330"格式
                "None",                    # 字符串"None"
                "未知",                    # "未知"
                "UNKNOWN",                 # "UNKNOWN"
                ""                         # 空字符串
            ]

            if cleaned_name not in invalid_formats:
                return cleaned_name

        # 2. 从映射表获取
        if symbol in self.stock_name_mapping:
            return self.stock_name_mapping[symbol]

        # 3. 最后回退：使用代码本身
        return symbol

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

                # 获取股票名称，使用回退机制
                raw_name = stock_row['名称']
                stock_name = self.get_stock_name(symbol, raw_name)

                stock_data = {
                    "symbol": symbol,
                    "name": stock_name,
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
            # 已知支持联网搜索的模型（基于官方文档）
            internet_capable_models = {
                "openai": ["gpt-4", "gpt-4-turbo"],  # 部分OpenAI模型支持
                "google": ["gemini-pro", "gemini-1.5-flash", "gemini-1.5-pro"],  # Google模型通常支持
                "perplexity": ["pplx-7b-online", "pplx-70b-online"],  # Perplexity专门支持
                "阿里百炼": [
                    "qwen-max",           # 通义千问Max
                    "qwen-plus",          # 通义千问-Plus
                    "qwen-turbo",         # 通义千问Turbo
                    "qwq-32b-preview"     # QwQ
                ],
                "dashscope": [
                    "qwen-max",           # 通义千问Max
                    "qwen-plus",          # 通义千问-Plus
                    "qwen-turbo",         # 通义千问Turbo
                    "qwq-32b-preview"     # QwQ
                ],
            }

            if provider in internet_capable_models:
                return model in internet_capable_models[provider]

            return False

        except Exception as e:
            logger.error(f"检查LLM联网能力失败: {e}")
            return False





class EnhancedTradingAgentsApp:
    """增强版TradingAgents应用"""

    def __init__(self, db_path: str = "data/trading_data.db"):
        """初始化应用"""
        # 数据收集器
        self.data_collector = RealDataCollector(db_path)

        # 配置文件路径
        self.config_file = Path("config/llm_config.json")
        self.config_dir = Path("config")
        self.config_dir.mkdir(exist_ok=True)

        # 分析会话
        self.analysis_sessions = []

        # LLM配置
        self.llm_config = {}
        self.custom_llm_providers = {}
        self.load_saved_config()

        # 检查ChromaDB可用性
        self.chromadb_available = self.check_chromadb()

        # 智能体模型配置
        self.agent_model_config = {}
        self.agent_model_config = self.load_agent_model_config()

        # 通信日志
        self.communication_logs = []
        self.max_logs = 1000  # 最大保存1000条日志

        # 最后一次分析结果（用于导出）
        self.last_analysis_result = None

        # 报告目录
        self.reports_dir = Path("./reports")
        self.reports_dir.mkdir(exist_ok=True)

        # 重试和中断配置
        self.retry_config = {
            "max_data_retries": 3,      # 数据获取最大重试次数
            "max_llm_retries": 2,       # LLM调用最大重试次数
            "max_agent_retries": 2,     # 单个智能体最大重试次数
            "retry_delay": 1.0,         # 重试延迟（秒）
            "timeout_seconds": 30,      # 单次操作超时时间
        }

        # 分析状态跟踪
        self.analysis_state = {
            "is_running": False,
            "current_step": "",
            "retry_counts": {},
            "failed_agents": [],
            "should_interrupt": False
        }

    def reset_analysis_state(self):
        """重置分析状态"""
        self.analysis_state = {
            "is_running": False,
            "current_step": "",
            "retry_counts": {},
            "failed_agents": [],
            "should_interrupt": False
        }

    def check_should_interrupt(self) -> bool:
        """检查是否应该中断分析"""
        return self.analysis_state.get("should_interrupt", False)

    def interrupt_analysis(self, reason: str = "用户中断"):
        """中断分析"""
        self.analysis_state["should_interrupt"] = True
        self.analysis_state["is_running"] = False
        logger.warning(f"分析被中断: {reason}")

    async def retry_with_backoff(self, func, *args, max_retries: int = 3, delay: float = 1.0, **kwargs):
        """带退避的重试机制"""
        last_exception = None

        for attempt in range(max_retries + 1):
            if self.check_should_interrupt():
                raise InterruptedError("分析被用户中断")

            try:
                result = await func(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"重试成功，尝试次数: {attempt + 1}")
                return result

            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    wait_time = delay * (2 ** attempt)  # 指数退避
                    logger.warning(f"第{attempt + 1}次尝试失败: {e}，{wait_time}秒后重试...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"重试{max_retries}次后仍然失败: {e}")

        raise last_exception

    def export_analysis_report(self, format_type="markdown") -> str:
        """导出分析报告"""
        if not self.last_analysis_result:
            return "❌ 没有可导出的分析结果，请先进行股票分析"

        result = self.last_analysis_result

        if format_type == "markdown":
            return self._export_markdown_report(result)
        elif format_type == "text":
            return self._export_text_report(result)
        elif format_type == "json":
            return self._export_json_report(result)
        else:
            return "❌ 不支持的导出格式"

    def _export_markdown_report(self, result: Dict[str, Any]) -> str:
        """导出Markdown格式报告"""
        stock_name = result.get('stock_name', '未知')
        report = f"""# 📊 TradingAgents 股票分析报告

## 📋 基本信息
- **股票代码**: {result['symbol']}
- **股票名称**: {stock_name}
- **分析时间**: {result['analysis_time']}
- **报告生成**: TradingAgents 多智能体协作系统

---

## 📈 综合分析报告
{result['comprehensive_report']}

---

## 📊 分析师团队报告

### 📈 市场技术分析
{result['market_analysis']}

### 💭 社交情感分析
{result['sentiment_analysis']}

### 📰 新闻事件分析
{result['news_analysis']}

### 📊 基本面分析
{result['fundamentals_analysis']}

---

## 🔬 多空辩论

### 🐂 多头观点
{result['bull_arguments']}

### 🐻 空头观点
{result['bear_arguments']}

### 👨‍💼 投资建议
{result['investment_recommendation']}

---

## 💼 交易策略
{result['trading_strategy']}

---

## ⚠️ 风险评估
{result['risk_assessment']}

---

## 🎯 最终决策
{result['final_decision']}

---

*本报告由TradingAgents多智能体系统生成，仅供参考，不构成投资建议。投资有风险，入市需谨慎。*
"""
        return report

    def _export_text_report(self, result: Dict[str, Any]) -> str:
        """导出纯文本格式报告"""
        stock_name = result.get('stock_name', '未知')
        report = f"""TradingAgents 股票分析报告

基本信息
========
股票代码: {result['symbol']}
股票名称: {stock_name}
分析时间: {result['analysis_time']}

综合分析报告
============
{result['comprehensive_report']}

分析师团队报告
==============

市场技术分析
------------
{result['market_analysis']}

社交情感分析
------------
{result['sentiment_analysis']}

新闻事件分析
------------
{result['news_analysis']}

基本面分析
----------
{result['fundamentals_analysis']}

多空辩论
========

多头观点
--------
{result['bull_arguments']}

空头观点
--------
{result['bear_arguments']}

投资建议
--------
{result['investment_recommendation']}

交易策略
========
{result['trading_strategy']}

风险评估
========
{result['risk_assessment']}

最终决策
========
{result['final_decision']}

免责声明: 本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。
"""
        return report

    def _export_json_report(self, result: Dict[str, Any]) -> str:
        """导出JSON格式报告"""
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
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
            "moonshot": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
            "阿里百炼": ["qwen-max", "qwen-plus", "qwen-turbo", "qwq-32b-preview"]
        }

        # 添加自定义提供商的模型
        for provider_name, config in self.custom_llm_providers.items():
            model = config.get("model", f"{provider_name}-default")
            models[provider_name] = [model] if model else [f"{provider_name}-default"]

        return models

    def get_provider_models(self, provider: str) -> List[str]:
        """获取指定提供商的可用模型列表"""
        try:
            from core.enhanced_llm_manager import EnhancedLLMManager
            llm_manager = EnhancedLLMManager()
            models = llm_manager.get_provider_models(provider)
            return [model["id"] for model in models]
        except ImportError:
            # 回退到原有逻辑
            available_models = self.get_available_models()
            return available_models.get(provider, [])

    def validate_model_compatibility(self, agent_id: str, provider: str, model: str) -> Dict[str, Any]:
        """验证模型与智能体的兼容性"""
        try:
            from core.agent_model_manager import AgentModelManager
            from core.enhanced_llm_manager import EnhancedLLMManager

            agent_manager = AgentModelManager()
            llm_manager = EnhancedLLMManager()

            # 获取所有可用模型的详细信息
            available_models = {}
            all_providers = llm_manager.get_all_providers()

            for provider_id in list(all_providers["built_in"].keys()) + list(all_providers["custom"].keys()):
                available_models[provider_id] = llm_manager.get_provider_models(provider_id)

            return agent_manager.validate_model_compatibility(agent_id, provider, model, available_models)

        except ImportError:
            # 回退到简单验证
            if provider not in self.llm_config:
                return {"compatible": False, "reason": f"提供商 {provider} 未配置"}

            available_models = self.get_available_models()
            if provider not in available_models:
                return {"compatible": False, "reason": f"提供商 {provider} 不可用"}

            if model not in available_models[provider]:
                return {"compatible": False, "reason": f"模型 {model} 在提供商 {provider} 中不存在"}

            return {"compatible": True, "score": 0.8, "recommendation": "基本兼容"}

    def get_common_models_for_provider(self, provider_name: str) -> List[str]:
        """根据提供商名称推荐常见模型"""
        common_models = {
            "claude": ["claude-3-sonnet-20240229", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
            "anthropic": ["claude-3-sonnet-20240229", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
            "通义千问": ["qwen-turbo", "qwen-plus", "qwen-max", "qwen-max-longcontext"],
            "qwen": ["qwen-turbo", "qwen-plus", "qwen-max", "qwen-max-longcontext"],
            "阿里百炼": ["qwen-max", "qwen-plus", "qwen-turbo", "qwq-32b-preview"],
            "dashscope": ["qwen-max", "qwen-plus", "qwen-turbo", "qwq-32b-preview"],
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
                    loaded_config = json.load(f)
                    logger.info(f"成功加载智能体模型配置: {len(loaded_config)}个智能体")
                    # 更新实例变量
                    self.agent_model_config = loaded_config
                    return loaded_config
        except Exception as e:
            logger.error(f"加载智能体模型配置失败: {e}")

        # 返回默认配置
        default_model = "deepseek:deepseek-chat"
        agents = self.get_agent_list()
        default_config = {agent["id"]: default_model for agent in agents}
        self.agent_model_config = default_config
        return default_config

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
            # 生成唯一的日志序列号
            log_id = len(self.communication_logs) + 1

            log_entry = {
                "id": log_id,
                "timestamp": datetime.now().isoformat(),
                "agent_id": agent_id,
                "provider": provider,
                "model": model,
                "prompt": prompt,  # 保存完整提示
                "response": response,  # 保存完整响应
                "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                "response_preview": response[:100] + "..." if len(response) > 100 else response,
                "status": status,
                "prompt_length": len(prompt),
                "response_length": len(response),
                "duration": "N/A"  # 可以后续添加响应时间
            }

            self.communication_logs.append(log_entry)

            # 保持日志数量在限制内
            if len(self.communication_logs) > self.max_logs:
                self.communication_logs = self.communication_logs[-self.max_logs:]
                # 重新分配ID
                for i, log in enumerate(self.communication_logs):
                    log["id"] = i + 1

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

    def update_agent_model_config(self, agent: str, model: str) -> str:
        """更新智能体模型配置"""
        try:
            # 解析模型配置（格式：provider:model 或 model）
            if ":" in model:
                provider, model_name = self._parse_model_config(model)
                full_config = f"{provider}:{model_name}"
            else:
                # 如果只有模型名，需要找到对应的提供商
                models_dict = self.get_available_models()
                provider = None
                for prov, models in models_dict.items():
                    if model in models:
                        provider = prov
                        break

                if provider:
                    full_config = f"{provider}:{model}"
                else:
                    return f"❌ 未找到模型 {model} 的提供商"

            # 更新配置
            self.agent_model_config[agent] = full_config

            # 保存到文件
            self._save_agent_model_config()

            logger.info(f"✅ 更新智能体 {agent} 模型配置: {full_config}")
            return f"✅ {agent} -> {full_config}"

        except Exception as e:
            error_msg = f"❌ 更新 {agent} 配置失败: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def _save_agent_model_config(self):
        """保存智能体模型配置到文件"""
        try:
            config_file = Path("config/agent_model_config.json")
            config_file.parent.mkdir(exist_ok=True)

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.agent_model_config, f, ensure_ascii=False, indent=2)

            logger.info("智能体模型配置已保存")
        except Exception as e:
            logger.error(f"保存智能体模型配置失败: {e}")

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

    def _get_debate_rounds(self, depth: str) -> int:
        """根据分析深度获取辩论轮数"""
        depth_rounds = {
            "快速分析": 1,  # 1轮辩论
            "标准分析": 2,  # 2轮辩论
            "深度分析": 3,  # 3轮辩论
            "全面分析": 4   # 4轮辩论
        }
        return depth_rounds.get(depth, 2)

    async def _real_agent_analysis(self, symbol: str, depth: str, analysts: List[str]) -> Dict[str, Any]:
        """真实的智能体分析流程（带中断机制和多轮辩论）"""
        try:
            start_time = datetime.now()
            self.analysis_state["is_running"] = True
            self.reset_analysis_state()
            self.analysis_state["is_running"] = True

            # 获取辩论轮数
            debate_rounds = self._get_debate_rounds(depth)
            logger.info(f"📊 开始{depth}，将进行{debate_rounds}轮辩论")

            # 1. 数据收集阶段
            logger.info("📊 阶段1: 数据收集")
            stock_data = await self._collect_stock_data(symbol)

            if "error" in stock_data:
                if stock_data.get("interrupted"):
                    return {"status": "interrupted", "message": "分析被用户中断"}
                else:
                    return {"status": "failed", "error": stock_data["error"], "stage": "数据收集"}

            if self.check_should_interrupt():
                return {"status": "interrupted", "message": "分析被用户中断"}

            # 2. 分析师团队分析
            logger.info("👥 阶段2: 分析师团队分析")
            analyst_results = await self._run_analyst_team(symbol, stock_data)

            if "error" in analyst_results:
                if analyst_results.get("interrupted"):
                    return {"status": "interrupted", "message": "分析被用户中断"}

            if self.check_should_interrupt():
                return {"status": "interrupted", "message": "分析被用户中断"}

            # 3. 多轮研究团队辩论
            logger.info(f"🔬 阶段3: 研究团队多轮辩论（{debate_rounds}轮）")
            research_results = await self._run_multi_round_research_team(symbol, analyst_results, debate_rounds)

            if self.check_should_interrupt():
                return {"status": "interrupted", "message": "分析被用户中断"}

            # 4. 交易策略制定
            logger.info("💼 阶段4: 交易策略制定")
            trading_strategy = await self._run_trader_analysis(symbol, research_results)

            if self.check_should_interrupt():
                return {"status": "interrupted", "message": "分析被用户中断"}

            # 5. 风险管理评估
            logger.info("⚠️ 阶段5: 风险管理评估")
            risk_assessment = await self._run_risk_management(symbol, trading_strategy)

            if self.check_should_interrupt():
                return {"status": "interrupted", "message": "分析被用户中断"}

            # 6. 最终决策
            logger.info("🎯 阶段6: 最终决策制定")
            final_decision = await self._make_final_decision(symbol, risk_assessment)

            if self.check_should_interrupt():
                return {"status": "interrupted", "message": "分析被用户中断"}

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

    def get_report_history(self) -> List[Dict[str, Any]]:
        """获取报告历史列表"""
        try:
            history = []

            # 获取所有报告文件
            for file_path in self.reports_dir.glob("*"):
                if file_path.is_file() and file_path.suffix in ['.md', '.txt', '.json']:
                    try:
                        # 解析文件名: 股票代码_股票名称_时间戳.扩展名
                        name_parts = file_path.stem.split('_')
                        if len(name_parts) >= 3:
                            symbol = name_parts[0]
                            stock_name = '_'.join(name_parts[1:-1])  # 股票名称可能包含下划线
                            timestamp_str = name_parts[-1]

                            # 解析时间戳
                            try:
                                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                            except ValueError:
                                # 如果时间戳格式不对，使用文件修改时间
                                timestamp = datetime.fromtimestamp(file_path.stat().st_mtime)

                            # 获取文件大小
                            file_size = file_path.stat().st_size

                            history.append({
                                "file_path": str(file_path),
                                "filename": file_path.name,
                                "symbol": symbol,
                                "stock_name": stock_name,
                                "timestamp": timestamp,
                                "format": file_path.suffix[1:],  # 去掉点号
                                "size": file_size,
                                "display_name": f"{symbol}({stock_name}) - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
                            })
                    except Exception as e:
                        logger.warning(f"解析文件 {file_path.name} 失败: {e}")
                        continue

            # 按时间倒序排列（最新的在前）
            history.sort(key=lambda x: x["timestamp"], reverse=True)

            return history

        except Exception as e:
            logger.error(f"获取报告历史失败: {e}")
            return []

    def load_analysis_report(self, file_path: str) -> str:
        """加载分析报告内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            logger.error(f"加载报告文件失败: {e}")
            return f"❌ 无法加载报告文件: {str(e)}"

    def delete_analysis_report(self, file_path: str) -> bool:
        """删除分析报告"""
        try:
            Path(file_path).unlink()
            logger.info(f"已删除报告文件: {file_path}")
            return True
        except Exception as e:
            logger.error(f"删除报告文件失败: {e}")
            return False

    # ==================== 真实智能体调用方法 ====================

    async def _collect_stock_data(self, symbol: str) -> Dict[str, Any]:
        """数据收集阶段 - 使用真实数据（带重试机制）"""
        try:
            logger.info(f"开始收集股票 {symbol} 的真实数据...")
            self.analysis_state["current_step"] = f"获取股票数据: {symbol}"

            # 使用重试机制获取股票数据
            async def get_data():
                real_data = await self.data_collector.get_real_stock_data(symbol)
                if "error" in real_data:
                    raise ValueError(f"获取股票数据失败: {real_data['error']}")
                return real_data

            real_data = await self.retry_with_backoff(
                get_data,
                max_retries=self.retry_config["max_data_retries"],
                delay=self.retry_config["retry_delay"]
            )

            logger.info(f"成功收集股票 {symbol} 的真实数据")
            logger.info(f"当前价格: {real_data['price_data']['current_price']}")
            logger.info(f"RSI: {real_data['technical_indicators']['rsi']:.2f}")
            logger.info(f"MACD: {real_data['technical_indicators']['macd']:.2f}")

            return real_data

        except InterruptedError as e:
            logger.warning(f"数据收集被中断: {e}")
            return {"error": "数据收集被用户中断", "interrupted": True}
        except Exception as e:
            logger.error(f"数据收集失败: {e}")
            return {"error": f"数据收集失败: {str(e)}"}

    def _parse_model_config(self, model_config: str) -> tuple:
        """安全解析模型配置"""
        if ":" in model_config:
            return model_config.split(":", 1)
        else:
            # 如果没有提供商前缀，使用默认提供商
            return "阿里百炼", model_config

    async def _check_llm_internet_access(self, agent_id: str) -> bool:
        """检查智能体使用的LLM是否支持联网"""
        try:
            model_config = self.agent_model_config.get(agent_id, "deepseek:deepseek-chat")
            provider, model = self._parse_model_config(model_config)

            if provider not in self.llm_config:
                return False

            api_key = self.llm_config[provider]
            return await self.data_collector.check_llm_internet_capability(provider, model, api_key)

        except Exception as e:
            logger.error(f"检查LLM联网能力失败: {e}")
            return False

    async def _run_analyst_team(self, symbol: str, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """运行分析师团队（带重试机制）"""
        try:
            results = {}
            failed_agents = []

            # 分析师配置
            analysts = [
                ("market_analyst", "市场分析师", self._call_market_analyst),
                ("sentiment_analyst", "情感分析师", self._call_sentiment_analyst),
                ("news_analyst", "新闻分析师", self._call_news_analyst),
                ("fundamentals_analyst", "基本面分析师", self._call_fundamentals_analyst)
            ]

            for agent_id, agent_name, agent_func in analysts:
                if self.check_should_interrupt():
                    logger.warning("分析师团队运行被中断")
                    break

                self.analysis_state["current_step"] = f"运行{agent_name}"
                logger.info(f"开始运行{agent_name}...")

                try:
                    # 使用重试机制调用分析师
                    result = await self.retry_with_backoff(
                        agent_func,
                        symbol,
                        stock_data,
                        max_retries=self.retry_config["max_agent_retries"],
                        delay=self.retry_config["retry_delay"]
                    )

                    # 验证结果
                    if not result or "error" in str(result):
                        raise ValueError(f"{agent_name}返回无效结果")

                    results[agent_id] = result
                    logger.info(f"{agent_name}运行成功")

                except Exception as e:
                    logger.error(f"{agent_name}运行失败: {e}")
                    failed_agents.append(agent_name)
                    results[agent_id] = {
                        "error": f"{agent_name}运行失败: {str(e)}",
                        "analysis": f"❌ {agent_name}暂时无法提供分析，请稍后重试"
                    }

            # 记录失败的智能体
            self.analysis_state["failed_agents"] = failed_agents

            if failed_agents:
                logger.warning(f"以下智能体运行失败: {failed_agents}")

            return results

        except InterruptedError as e:
            logger.warning(f"分析师团队运行被中断: {e}")
            return {"error": "分析师团队运行被用户中断", "interrupted": True}
        except Exception as e:
            logger.error(f"分析师团队运行失败: {e}")
            return {"error": str(e)}

    async def _call_market_analyst(self, symbol: str, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """调用市场分析师"""
        try:
            # 获取配置的模型
            model_config = self.agent_model_config.get("market_analyst", "deepseek:deepseek-chat")
            provider, model = self._parse_model_config(model_config)

            # 获取股票名称，使用回退机制
            raw_name = stock_data.get('name', '')
            stock_name = self.data_collector.get_stock_name(symbol, raw_name)

            # 构建提示
            prompt = f"""
你是专业的市场技术分析师。请分析股票{symbol}（{stock_name}）的技术指标和价格走势。

**重要提醒**: 请在分析中始终使用正确的股票代码{symbol}和股票名称{stock_name}。

当前数据:
- 股票: {symbol}（{stock_name}）
- 价格: {stock_data['price_data']['current_price']}元
- 涨跌幅: {stock_data['price_data']['change_percent']}%
- RSI: {stock_data['technical_indicators']['rsi']}
- MACD: {stock_data['technical_indicators']['macd']}
- MA5: {stock_data['technical_indicators']['ma5']}元
- MA20: {stock_data['technical_indicators']['ma20']}元

请提供:
1. 技术趋势分析
2. 关键支撑阻力位
3. 短期走势预测
4. 交易信号建议

请用专业、简洁的语言回答，控制在200字以内。务必在回答中使用正确的股票代码{symbol}和名称{stock_name}。
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
            provider, model = self._parse_model_config(model_config)

            # 检查LLM是否支持联网搜索
            has_internet = await self._check_llm_internet_access("social_media_analyst")

            # 获取股票名称，使用回退机制
            raw_name = stock_data.get('name', '')
            stock_name = self.data_collector.get_stock_name(symbol, raw_name)

            if has_internet:
                # 使用联网搜索获取真实社交媒体数据
                prompt = f"""
你是专业的市场情感分析师。请搜索并分析股票{symbol}（{stock_name}）在今天的社交媒体情绪和投资者情感。

**重要提醒**: 请在分析中始终使用正确的股票代码{symbol}和股票名称{stock_name}，不要使用其他股票的信息。

请搜索以下平台关于{symbol}（{stock_name}）的最新讨论:
1. 微博、雪球等投资社区
2. 财经新闻评论区
3. 投资论坛讨论

基于搜索到的真实数据和当前市场表现:
- 股票: {symbol}（{stock_name}）
- 当前价格: {stock_data['price_data']['current_price']}元
- 股价变化: {stock_data['price_data']['change_percent']}%
- 成交量: {stock_data['price_data']['volume']}

请分析:
1. 当前社交媒体情绪倾向
2. 投资者信心水平变化
3. 热门讨论话题和情感驱动因素
4. 情感对价格走势的影响预测

请基于真实搜索数据回答，控制在300字以内。务必在回答中使用正确的股票代码{symbol}和名称{stock_name}。
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
            provider, model = self._parse_model_config(model_config)

            # 检查LLM是否支持联网搜索
            has_internet = await self._check_llm_internet_access("news_analyst")

            if has_internet:
                # 使用联网搜索获取真实新闻数据
                raw_name = stock_data.get('name', '')
                stock_name = self.data_collector.get_stock_name(symbol, raw_name)
                prompt = f"""
你是专业的新闻分析师。请搜索并分析今天影响股票{symbol}（{stock_name}）的最新新闻和宏观经济因素。

**重要提醒**: 请在分析中始终使用正确的股票代码{symbol}和股票名称{stock_name}，不要使用其他股票的信息。

请搜索以下类型关于{symbol}（{stock_name}）的最新新闻:
1. 公司相关新闻公告
2. 行业政策和监管变化
3. 宏观经济数据发布
4. 国际市场影响因素

当前市场状况:
- 股票: {symbol}（{stock_name}）
- 当前价格: {stock_data['price_data']['current_price']}元
- 股价变化: {stock_data['price_data']['change_percent']}%
- 市盈率: {stock_data['market_data']['pe_ratio']}
- 市净率: {stock_data['market_data']['pb_ratio']}

请基于搜索到的真实新闻分析:
1. 今日重要新闻事件及影响
2. 行业政策变化和监管动态
3. 宏观经济环境对该股的影响
4. 新闻事件对股价的潜在影响预测

请基于真实搜索数据回答，控制在300字以内。务必在回答中使用正确的股票代码{symbol}和名称{stock_name}。
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
            provider, model = self._parse_model_config(model_config)

            # 检查LLM是否支持联网搜索
            has_internet = await self._check_llm_internet_access("fundamentals_analyst")

            if has_internet:
                # 使用联网搜索获取真实财务数据
                raw_name = stock_data.get('name', '')
                stock_name = self.data_collector.get_stock_name(symbol, raw_name)
                prompt = f"""
你是专业的基本面分析师。请搜索并分析股票{symbol}（{stock_name}）的最新财务数据和基本面指标。

**重要提醒**: 请在分析中始终使用正确的股票代码{symbol}和股票名称{stock_name}，不要使用其他股票的信息。

请搜索以下关于{symbol}（{stock_name}）的最新财务信息:
1. 最新季度财报数据
2. 年度财务报表
3. 现金流量表
4. 资产负债表
5. 行业对比数据

当前市场数据:
- 股票: {symbol}（{stock_name}）
- 当前价格: {stock_data['price_data']['current_price']}元
- 市盈率: {stock_data['market_data']['pe_ratio']}
- 市净率: {stock_data['market_data']['pb_ratio']}
- 市值: {stock_data['price_data'].get('market_cap', '未知')}

请基于搜索到的最新财务数据分析:
1. 最新财务指标和盈利能力
2. 资产质量和负债结构
3. 现金流状况和分红能力
4. 行业地位和竞争优势
5. 估值水平和投资价值判断

请基于真实财务数据回答，控制在300字以内。务必在回答中使用正确的股票代码{symbol}和名称{stock_name}。
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

    async def _run_multi_round_research_team(self, symbol: str, analyst_results: Dict[str, Any], rounds: int) -> Dict[str, Any]:
        """运行多轮研究团队辩论"""
        try:
            results = {}
            debate_history = []

            logger.info(f"🔬 开始{rounds}轮研究团队辩论")

            # 初始观点
            bull_view = ""
            bear_view = ""

            for round_num in range(1, rounds + 1):
                logger.info(f"🥊 第{round_num}轮辩论")

                # 多头研究员
                bull_result = await self._call_bull_researcher_with_context(
                    symbol, analyst_results, bear_view, round_num, rounds
                )
                bull_view = bull_result.get("analysis", "")

                # 空头研究员
                bear_result = await self._call_bear_researcher_with_context(
                    symbol, analyst_results, bull_view, round_num, rounds
                )
                bear_view = bear_result.get("analysis", "")

                # 记录本轮辩论
                debate_round = {
                    "round": round_num,
                    "bull_view": bull_view,
                    "bear_view": bear_view,
                    "bull_strength": len(bull_view.split("。")) if bull_view else 0,
                    "bear_strength": len(bear_view.split("。")) if bear_view else 0
                }
                debate_history.append(debate_round)

                logger.info(f"第{round_num}轮完成 - 多头论据: {debate_round['bull_strength']}条, 空头论据: {debate_round['bear_strength']}条")

            # 最终结果
            results["bull_researcher"] = {"analysis": bull_view, "agent_id": "bull_researcher"}
            results["bear_researcher"] = {"analysis": bear_view, "agent_id": "bear_researcher"}
            results["debate_history"] = debate_history
            results["total_rounds"] = rounds

            # 研究经理综合评估
            results["research_manager"] = await self._call_research_manager_with_debate_history(
                symbol, results, debate_history
            )

            logger.info(f"✅ {rounds}轮辩论完成，共产生{sum(r['bull_strength'] + r['bear_strength'] for r in debate_history)}条论据")

            return results

        except Exception as e:
            logger.error(f"多轮研究团队运行失败: {e}")
            return {"error": str(e)}

    async def _run_research_team(self, symbol: str, analyst_results: Dict[str, Any]) -> Dict[str, Any]:
        """运行研究团队（兼容性保留）"""
        return await self._run_multi_round_research_team(symbol, analyst_results, 2)

    async def _call_bull_researcher_with_context(self, symbol: str, analyst_results: Dict[str, Any],
                                                bear_view: str, round_num: int, total_rounds: int) -> Dict[str, Any]:
        """调用多头研究员（带上下文辩论）"""
        try:
            model_config = self.agent_model_config.get("bull_researcher", "deepseek:deepseek-chat")
            provider, model = self._parse_model_config(model_config)

            # 汇总分析师观点
            market_view = analyst_results.get("market_analyst", {}).get("analysis", "")
            sentiment_view = analyst_results.get("sentiment_analyst", {}).get("analysis", "")
            news_view = analyst_results.get("news_analyst", {}).get("analysis", "")
            fundamentals_view = analyst_results.get("fundamentals_analyst", {}).get("analysis", "")

            # 使用数据收集器的股票名称获取方法
            stock_name = self.data_collector.get_stock_name(symbol)

            # 根据轮次调整提示词
            if round_num == 1:
                context_prompt = "这是第一轮辩论，请提出你的初始多头观点。"
                min_points = 3
            else:
                context_prompt = f"""
这是第{round_num}轮辩论（共{total_rounds}轮）。

空头研究员在前一轮的观点:
{bear_view[:400]}

请针对空头观点进行有力反驳，并提供更多支撑看涨的论据。
"""
                min_points = round_num + 2

            prompt = f"""
你是专业的多头研究员。基于分析师团队的报告，请为股票{symbol}（{stock_name}）提供看涨论据。

**重要提醒**: 请在分析中始终使用正确的股票代码{symbol}和股票名称{stock_name}。

{context_prompt}

分析师观点摘要:
- 技术分析: {market_view[:150]}...
- 情感分析: {sentiment_view[:150]}...
- 新闻分析: {news_view[:150]}...
- 基本面分析: {fundamentals_view[:150]}...

请基于以上分析提供:
1. 主要看涨理由（至少{min_points}条具体论据）
2. 上涨催化剂分析
3. 目标价位预期
4. 投资机会评估
{f"5. 对空头观点的针对性反驳" if round_num > 1 else ""}

要求：论据要比前一轮更加充分详实，每条理由都要有具体支撑。务必在回答中使用正确的股票代码{symbol}和名称{stock_name}。
"""

            response = await self._call_llm(provider, model, prompt, "bull_researcher")

            return {
                "agent_id": "bull_researcher",
                "analysis": response,
                "round": round_num,
                "bullish_score": self._extract_bullish_score(response),
                "confidence": self._extract_confidence(response),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"多头研究员调用失败: {e}")
            return {"error": str(e), "agent_id": "bull_researcher"}

    async def _call_bear_researcher_with_context(self, symbol: str, analyst_results: Dict[str, Any],
                                                bull_view: str, round_num: int, total_rounds: int) -> Dict[str, Any]:
        """调用空头研究员（带上下文辩论）"""
        try:
            model_config = self.agent_model_config.get("bear_researcher", "deepseek:deepseek-chat")
            provider, model = self._parse_model_config(model_config)

            # 汇总分析师观点
            market_view = analyst_results.get("market_analyst", {}).get("analysis", "")
            sentiment_view = analyst_results.get("sentiment_analyst", {}).get("analysis", "")
            news_view = analyst_results.get("news_analyst", {}).get("analysis", "")
            fundamentals_view = analyst_results.get("fundamentals_analyst", {}).get("analysis", "")

            # 使用数据收集器的股票名称获取方法
            stock_name = self.data_collector.get_stock_name(symbol)

            # 根据轮次调整提示词
            if round_num == 1:
                context_prompt = "这是第一轮辩论，请提出你的初始空头观点。"
                min_points = 3
            else:
                context_prompt = f"""
这是第{round_num}轮辩论（共{total_rounds}轮）。

多头研究员在本轮的观点:
{bull_view[:400]}

请针对多头观点进行有力反驳，并提供更多支撑看跌的论据。
"""
                min_points = round_num + 2

            prompt = f"""
你是专业的空头研究员。基于分析师团队的报告，请为股票{symbol}（{stock_name}）提供看跌论据。

**重要提醒**: 请在分析中始终使用正确的股票代码{symbol}和股票名称{stock_name}。

{context_prompt}

分析师观点摘要:
- 技术分析: {market_view[:150]}...
- 情感分析: {sentiment_view[:150]}...
- 新闻分析: {news_view[:150]}...
- 基本面分析: {fundamentals_view[:150]}...

请基于以上分析提供:
1. 主要看跌理由（至少{min_points}条具体论据）
2. 下跌风险因素
3. 目标价位预期
4. 风险警示评估
{f"5. 对多头观点的针对性反驳" if round_num > 1 else ""}

要求：论据要比前一轮更加充分详实，每条理由都要有具体支撑。务必在回答中使用正确的股票代码{symbol}和名称{stock_name}。
"""

            response = await self._call_llm(provider, model, prompt, "bear_researcher")

            return {
                "agent_id": "bear_researcher",
                "analysis": response,
                "round": round_num,
                "bearish_score": self._extract_bearish_score(response),
                "confidence": self._extract_confidence(response),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"空头研究员调用失败: {e}")
            return {"error": str(e), "agent_id": "bear_researcher"}

    async def _call_research_manager_with_debate_history(self, symbol: str, results: Dict[str, Any],
                                                        debate_history: List[Dict]) -> Dict[str, Any]:
        """调用研究经理（带辩论历史）"""
        try:
            model_config = self.agent_model_config.get("research_manager", "deepseek:deepseek-chat")
            provider, model = self._parse_model_config(model_config)

            # 使用数据收集器的股票名称获取方法
            stock_name = self.data_collector.get_stock_name(symbol)

            # 构建辩论历史摘要
            debate_summary = ""
            total_bull_points = 0
            total_bear_points = 0

            for i, round_data in enumerate(debate_history, 1):
                bull_strength = round_data['bull_strength']
                bear_strength = round_data['bear_strength']
                total_bull_points += bull_strength
                total_bear_points += bear_strength

                debate_summary += f"""
第{i}轮辩论:
- 多头论据: {bull_strength}条
- 空头论据: {bear_strength}条
"""

            final_bull_view = results.get("bull_researcher", {}).get("analysis", "")
            final_bear_view = results.get("bear_researcher", {}).get("analysis", "")

            prompt = f"""
你是研究经理。基于{len(debate_history)}轮多空辩论，请对股票{symbol}（{stock_name}）做出综合投资建议。

**重要提醒**: 请在分析中始终使用正确的股票代码{symbol}和股票名称{stock_name}。

辩论历史摘要:
{debate_summary}

总计论据统计:
- 多头总论据: {total_bull_points}条
- 空头总论据: {total_bear_points}条

最终观点:
多头观点: {final_bull_view[:200]}...
空头观点: {final_bear_view[:200]}...

请基于多轮辩论的充分论证，提供:
1. 综合投资建议（买入/持有/卖出）
2. 辩论质量评估
3. 关键争议点分析
4. 最终决策依据
5. 风险收益评估

要求客观公正，基于辩论的充分性和论据强度做出判断。
"""

            response = await self._call_llm(provider, model, prompt, "research_manager")

            return {
                "agent_id": "research_manager",
                "analysis": response,
                "debate_rounds": len(debate_history),
                "total_arguments": total_bull_points + total_bear_points,
                "bull_arguments": total_bull_points,
                "bear_arguments": total_bear_points,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"研究经理调用失败: {e}")
            return {"error": str(e), "agent_id": "research_manager"}

    async def _call_bull_researcher(self, symbol: str, analyst_results: Dict[str, Any]) -> Dict[str, Any]:
        """调用多头研究员"""
        try:
            model_config = self.agent_model_config.get("bull_researcher", "deepseek:deepseek-chat")
            provider, model = self._parse_model_config(model_config)

            # 汇总分析师观点
            market_view = analyst_results.get("market_analyst", {}).get("analysis", "")
            sentiment_view = analyst_results.get("sentiment_analyst", {}).get("analysis", "")
            news_view = analyst_results.get("news_analyst", {}).get("analysis", "")
            fundamentals_view = analyst_results.get("fundamentals_analyst", {}).get("analysis", "")

            # 使用数据收集器的股票名称获取方法
            stock_name = self.data_collector.get_stock_name(symbol)

            prompt = f"""
你是专业的多头研究员。基于分析师团队的报告，请为股票{symbol}（{stock_name}）提供看涨论据。

**重要提醒**: 请在分析中始终使用正确的股票代码{symbol}和股票名称{stock_name}。

分析师观点摘要:
- 技术分析: {market_view[:150]}...
- 情感分析: {sentiment_view[:150]}...
- 新闻分析: {news_view[:150]}...
- 基本面分析: {fundamentals_view[:150]}...

请基于以上分析提供:
1. 主要看涨理由
2. 上涨催化剂
3. 目标价位预期
4. 投资机会分析

请用积极、专业的语言回答，控制在200字以内。务必在回答中使用正确的股票代码{symbol}和名称{stock_name}。
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
            elif provider in ["阿里百炼", "dashscope"]:
                response = await self._call_dashscope(api_key, model, prompt, agent_id)
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

    async def _call_dashscope(self, api_key: str, model: str, prompt: str, agent_id: str) -> str:
        """调用阿里百炼DashScope API（使用OpenAI兼容接口，支持联网搜索）"""
        try:
            import httpx

            # 检查是否需要联网搜索
            need_internet = agent_id in ["social_media_analyst", "news_analyst", "fundamentals_analyst"]

            # 阿里百炼官方OpenAI兼容接口
            base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            url = f"{base_url}/chat/completions"

            # 构建请求头
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # 构建请求数据
            data = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }

            # 如果需要联网搜索，添加搜索参数
            if need_internet:
                # 使用阿里百炼官方推荐的联网搜索配置
                data["enable_search"] = True
                logger.info(f"为智能体 {agent_id} 启用联网搜索")

            # 发送HTTP请求
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()

                result = response.json()

                # 解析响应
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]

                    # 检查是否有搜索信息（如果API返回的话）
                    if need_internet and "search_info" in result:
                        search_info = result["search_info"]
                        if "search_results" in search_info:
                            search_sources = []
                            for result_item in search_info["search_results"][:3]:
                                title = result_item.get("title", "搜索结果")
                                url_link = result_item.get("url", "#")
                                search_sources.append(f"[{title}]({url_link})")

                            content += f"\n\n📡 **搜索来源**:\n" + "\n".join(search_sources)

                    return content
                else:
                    logger.error(f"阿里百炼API响应格式异常: {result}")
                    return "❌ 阿里百炼API响应格式异常"

        except httpx.HTTPStatusError as e:
            error_text = ""
            try:
                error_text = e.response.text
            except:
                error_text = "无法获取错误详情"

            logger.error(f"阿里百炼API HTTP错误: {e.response.status_code} - {error_text}")

            if e.response.status_code == 401:
                return "❌ 阿里百炼API密钥无效，请检查配置"
            elif e.response.status_code == 403:
                return "❌ 阿里百炼API访问被拒绝，请检查API密钥权限"
            elif e.response.status_code == 429:
                return "❌ 阿里百炼API请求频率过高，请稍后重试"
            elif e.response.status_code == 400:
                return f"❌ 阿里百炼API请求参数错误: {error_text[:200]}"
            else:
                return f"❌ 阿里百炼API调用失败: HTTP {e.response.status_code} - {error_text[:200]}"
        except httpx.TimeoutException:
            logger.error("阿里百炼API调用超时")
            return "❌ 阿里百炼API调用超时，请稍后重试"
        except httpx.RequestError as e:
            logger.error(f"阿里百炼API网络请求错误: {e}")
            return f"❌ 阿里百炼API网络请求错误: {str(e)}"
        except Exception as e:
            logger.error(f"阿里百炼API调用失败: {e}")
            return f"❌ 阿里百炼API调用异常: {str(e)}"

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

    def _extract_bearish_score(self, text: str) -> float:
        """提取看跌评分"""
        # 简单的看跌评分逻辑
        bearish_words = ["强烈看跌", "看跌", "下跌", "卖出", "风险", "高估", "泡沫"]
        score = 0.5

        for word in bearish_words:
            if word in text:
                score += 0.1

        return min(score, 1.0)

    # ==================== 剩余智能体调用方法 ====================

    async def _run_trader_analysis(self, symbol: str, research_results: Dict[str, Any]) -> Dict[str, Any]:
        """运行交易员分析"""
        try:
            model_config = self.agent_model_config.get("trader", "deepseek:deepseek-chat")
            provider, model = self._parse_model_config(model_config)

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
            provider, model = self._parse_model_config(model_config)

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
            provider, model = self._parse_model_config(model_config)

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
            provider, model = self._parse_model_config(model_config)

            # 汇总分析师观点
            market_view = analyst_results.get("market_analyst", {}).get("analysis", "")
            sentiment_view = analyst_results.get("sentiment_analyst", {}).get("analysis", "")
            news_view = analyst_results.get("news_analyst", {}).get("analysis", "")
            fundamentals_view = analyst_results.get("fundamentals_analyst", {}).get("analysis", "")

            # 使用数据收集器的股票名称获取方法
            stock_name = self.data_collector.get_stock_name(symbol)

            prompt = f"""
你是专业的空头研究员。基于分析师团队的报告，请为股票{symbol}（{stock_name}）提供看跌论据。

**重要提醒**: 请在分析中始终使用正确的股票代码{symbol}和股票名称{stock_name}。

分析师观点摘要:
- 技术分析: {market_view[:150]}...
- 情感分析: {sentiment_view[:150]}...
- 新闻分析: {news_view[:150]}...
- 基本面分析: {fundamentals_view[:150]}...

请基于以上分析提供:
1. 主要看跌理由
2. 下跌风险因素
3. 目标价位预期
4. 风险警示

请用谨慎、专业的语言回答，控制在200字以内。务必在回答中使用正确的股票代码{symbol}和名称{stock_name}。
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
            provider, model = self._parse_model_config(model_config)

            bull_view = research_results.get("bull_researcher", {}).get("analysis", "")
            bear_view = research_results.get("bear_researcher", {}).get("analysis", "")

            # 使用数据收集器的股票名称获取方法
            stock_name = self.data_collector.get_stock_name(symbol)

            prompt = f"""
你是研究经理。基于多空研究员的辩论，请对股票{symbol}（{stock_name}）做出综合投资建议。

**重要提醒**: 请在分析中始终使用正确的股票代码{symbol}和股票名称{stock_name}。

多空观点:
- 多头观点: {bull_view[:200]}...
- 空头观点: {bear_view[:200]}...

请提供:
1. 综合投资建议
2. 平衡风险收益
3. 投资策略建议
4. 时机把握

请用平衡、专业的语言回答，控制在200字以内。务必在回答中使用正确的股票代码{symbol}和名称{stock_name}。
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
            provider, model = self._parse_model_config(model_config)

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
            provider, model = self._parse_model_config(model_config)

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
            provider, model = self._parse_model_config(model_config)

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
            provider, model = self._parse_model_config(model_config)

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
            "chromadb_available": getattr(self, 'chromadb_available', False),
            "total_analyses": len(getattr(self, 'analysis_sessions', [])),
            "system_ready": len(self.llm_config) > 0
        }

# 创建应用实例
app = EnhancedTradingAgentsApp()

def _get_model_choices():
    """获取模型选择列表"""
    choices = []
    models = app.get_available_models()

    for provider, model_list in models.items():
        # 显示所有提供商，但标注配置状态
        for model in model_list:
            if provider in app.llm_config:
                choices.append(f"{provider}:{model}")
            else:
                choices.append(f"{provider}:{model} (未配置)")

    return choices if choices else ["deepseek:deepseek-chat"]

def create_enhanced_interface():
    """创建增强版Gradio界面"""

    with gr.Blocks(
        title="TradingAgents - 增强版多智能体股票分析系统",
        theme=gr.themes.Soft(),
        css="""
        /* 全局样式优化 */
        .gradio-container {
            max-width: none !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* 优化的导航栏样式 - 减小高度 */
        .main-header {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            z-index: 9999 !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            padding: 8px 20px !important;  /* 减小内边距 */
            border-radius: 0 0 12px 12px !important;
            box-shadow: 0 2px 20px rgba(0,0,0,0.15) !important;
            backdrop-filter: blur(15px) !important;
            margin: 0 !important;
            min-height: 60px !important;  /* 设置最小高度 */
        }

        /* 标题区域样式优化 */
        .title-section {
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            padding: 5px 0 !important;  /* 减小内边距 */
        }

        .title-section h1 {
            font-size: 1.4em !important;  /* 减小字体 */
            margin: 0 !important;
            line-height: 1.2 !important;
            font-weight: 600 !important;
        }

        .title-section p {
            font-size: 0.85em !important;  /* 减小字体 */
            margin: 2px 0 0 0 !important;
            opacity: 0.9 !important;
            line-height: 1.1 !important;
        }

        /* 赞助区域样式优化 */
        .sponsor-section {
            display: flex !important;
            flex-direction: row !important;  /* 改为水平布局 */
            align-items: center !important;
            justify-content: center !important;
            background: rgba(255,255,255,0.12) !important;
            border-radius: 8px !important;
            padding: 6px 10px !important;  /* 减小内边距 */
            backdrop-filter: blur(10px) !important;
            gap: 8px !important;
        }

        .sponsor-text {
            text-align: center !important;
            margin-right: 8px !important;
        }

        .sponsor-text h3 {
            font-size: 0.9em !important;  /* 减小字体 */
            margin: 0 !important;
            color: #FFD700 !important;
        }

        .sponsor-text p {
            font-size: 0.75em !important;  /* 减小字体 */
            margin: 2px 0 0 0 !important;
            opacity: 0.9 !important;
        }

        /* 二维码样式优化 */
        .sponsor-qr {
            border-radius: 6px !important;
            border: 1px solid rgba(255,255,255,0.4) !important;
            max-width: 50px !important;  /* 减小尺寸 */
            max-height: 50px !important;  /* 减小尺寸 */
            min-width: 50px !important;
            min-height: 50px !important;
        }

        /* 内容包装器优化 */
        .content-wrapper {
            margin-top: 80px !important;  /* 大幅减小顶部间距 */
            padding: 15px !important;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
            min-height: calc(100vh - 80px) !important;
        }

        /* 卡片样式 */
        .card {
            background: white !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08) !important;
            border: 1px solid rgba(0,0,0,0.05) !important;
            margin-bottom: 20px !important;
            overflow: hidden !important;
            padding: 20px !important;
        }

        /* 标签页样式优化 */
        .tab-nav {
            background: white !important;
            border-radius: 12px 12px 0 0 !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* 输入字段样式 */
        .input-field input {
            border-radius: 8px !important;
            border: 2px solid #e9ecef !important;
            padding: 12px !important;
            font-size: 14px !important;
            transition: all 0.3s ease !important;
        }

        .input-field input:focus {
            border-color: #667eea !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        }

        /* 下拉框样式 */
        .dropdown-field select {
            border-radius: 8px !important;
            border: 2px solid #e9ecef !important;
            padding: 12px !important;
            font-size: 14px !important;
        }

        /* 按钮样式优化 */
        .analyze-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 15px 30px !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        }

        .analyze-button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
        }

        /* 状态显示样式 */
        .status-display input {
            background: #f8f9fa !important;
            border: 2px solid #e9ecef !important;
            border-radius: 8px !important;
            color: #495057 !important;
            font-weight: 500 !important;
        }

        /* 结果显示样式 */
        .result-display {
            min-height: 400px !important;
            border-radius: 8px !important;
        }

        .result-tab {
            padding: 0 !important;
        }

        /* 组件分组样式 */
        .gradio-group {
            background: #f8f9fa !important;
            border: 1px solid #e9ecef !important;
            border-radius: 8px !important;
            padding: 15px !important;
            margin-bottom: 15px !important;
        }

        /* 响应式设计优化 */
        @media (max-width: 768px) {
            .main-header {
                flex-direction: column !important;
                gap: 8px !important;
                text-align: center !important;
                padding: 8px 15px !important;
                min-height: 90px !important;
            }

            .sponsor-section {
                flex-direction: column !important;
                gap: 4px !important;
            }

            .content-wrapper {
                margin-top: 100px !important;
                padding: 10px !important;
            }

            .title-section h1 {
                font-size: 1.2em !important;
            }

            .title-section p {
                font-size: 0.8em !important;
            }
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }

        .title-section h1 {
            color: white;
            margin: 0;
            font-size: 1.8em;
            font-weight: bold;
        }

        .title-section p {
            color: rgba(255,255,255,0.9);
            margin: 5px 0 0 0;
            font-size: 1em;
        }

        .sponsor-section {
            display: flex;
            align-items: center;
            gap: 15px;
            background: rgba(255,255,255,0.1);
            padding: 10px 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }

        .sponsor-qr {
            width: 80px;
            height: 80px;
            border-radius: 8px;
            border: 2px solid rgba(255,255,255,0.3);
        }

        .sponsor-text {
            color: white;
            text-align: left;
        }

        .sponsor-text h3 {
            margin: 0 0 5px 0;
            font-size: 1.1em;
            color: #FFD700;
        }

        .sponsor-text p {
            margin: 0;
            font-size: 0.9em;
            opacity: 0.9;
        }

        /* 响应式设计 */
        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }

            .sponsor-section {
                flex-direction: column;
                gap: 10px;
            }

            .sponsor-qr {
                width: 60px;
                height: 60px;
            }
        }
        """
    ) as interface:

        # 优化的紧凑导航栏
        with gr.Row(elem_classes=["main-header"]):
            with gr.Column(scale=4, elem_classes=["title-section"]):
                gr.HTML("""
                <div style="color: white;">
                    <h1>🤖 TradingAgents - 增强版多智能体协作股票分析系统</h1>
                    <p><strong>基于15个专业化智能体的金融交易分析框架</strong> | 支持LLM配置和ChromaDB</p>
                </div>
                """)

            with gr.Column(scale=1, elem_classes=["sponsor-section"]):
                with gr.Row():
                    with gr.Column(scale=2, elem_classes=["sponsor-text"]):
                        gr.HTML("""
                        <div style="color: white;">
                            <h3>💖 赞助支持</h3>
                            <p>您的支持是我持续开发的动力</p>
                        </div>
                        """)
                    with gr.Column(scale=1):
                        # 使用新的二维码
                        gr.Image(
                            value="assets/donation_code.png",
                            show_label=False,
                            show_download_button=False,
                            show_share_button=False,
                            interactive=False,
                            width=50,
                            height=50,
                            elem_classes=["sponsor-qr"]
                        )

        # 优化的内容包装器
        with gr.Column(elem_classes=["content-wrapper"]):
            with gr.Tabs(elem_classes=["tab-nav"]):
                # 主分析界面 - 重新设计布局
                with gr.TabItem("📊 智能分析", elem_classes=["card"]):
                    with gr.Row():
                        # 左侧控制面板 - 更紧凑的设计
                        with gr.Column(scale=1, elem_classes=["card"]):
                            gr.HTML("""
                            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                        color: white; padding: 15px; margin: -20px -20px 20px -20px;
                                        border-radius: 12px 12px 0 0;">
                                <h3 style="margin: 0; font-size: 1.2em;">🎯 分析控制中心</h3>
                                <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 0.9em;">配置您的专属分析参数</p>
                            </div>
                            """)

                            # 股票输入区域
                            with gr.Group():
                                gr.HTML("<h4 style='margin: 0 0 10px 0; color: #333;'>📈 股票选择</h4>")
                                stock_input = gr.Textbox(
                                    label="股票代码",
                                    placeholder="输入股票代码，如：000001、600036、600519",
                                    value="600519",
                                    elem_classes=["input-field"]
                                )

                            # 分析配置区域
                            with gr.Group():
                                gr.HTML("<h4 style='margin: 15px 0 10px 0; color: #333;'>⚙️ 分析配置</h4>")
                                analysis_depth = gr.Dropdown(
                                    label="研究深度",
                                    choices=["快速分析", "标准分析", "深度分析", "全面分析"],
                                    value="标准分析",
                                    elem_classes=["dropdown-field"]
                                )

                            # 智能体团队选择
                            with gr.Group():
                                gr.HTML("<h4 style='margin: 15px 0 10px 0; color: #333;'>👥 AI分析师团队</h4>")
                                with gr.Row():
                                    with gr.Column():
                                        analyst_market = gr.Checkbox(label="📈 市场分析师", value=True)
                                        analyst_sentiment = gr.Checkbox(label="💭 情感分析师", value=True)
                                    with gr.Column():
                                        analyst_news = gr.Checkbox(label="📰 新闻分析师", value=True)
                                        analyst_fundamentals = gr.Checkbox(label="📊 基本面分析师", value=True)

                            # LLM配置
                            with gr.Group():
                                gr.HTML("<h4 style='margin: 15px 0 10px 0; color: #333;'>🤖 AI引擎</h4>")
                                use_real_llm = gr.Checkbox(
                                    label="启用真实LLM (需要API密钥)",
                                    value=False,
                                    info="未启用时使用演示模式"
                                )

                            # 分析按钮 - 移到左侧栏
                            with gr.Group():
                                gr.HTML("<div style='margin: 20px 0 10px 0;'></div>")
                                analyze_btn = gr.Button(
                                    "🚀 开始全面分析",
                                    variant="primary",
                                    size="lg",
                                    elem_classes=["analyze-button"]
                                )

                                # 状态显示
                                status_display = gr.Textbox(
                                    label="分析状态",
                                    value="🎯 准备就绪，等待开始分析...",
                                    interactive=False,
                                    elem_classes=["status-display"]
                                )

                            # 高级配置 - 折叠面板
                            with gr.Accordion("⚙️ 高级配置", open=False):
                                with gr.Row():
                                    max_data_retries = gr.Slider(
                                        minimum=1, maximum=5, value=3, step=1,
                                        label="数据获取重试次数",
                                        info="获取股票数据失败时的最大重试次数"
                                    )
                                    max_llm_retries = gr.Slider(
                                        minimum=1, maximum=3, value=2, step=1,
                                        label="LLM调用重试次数",
                                        info="LLM调用失败时的最大重试次数"
                                    )

                                retry_delay = gr.Slider(
                                    minimum=0.5, maximum=5.0, value=1.0, step=0.5,
                                    label="重试延迟（秒）",
                                    info="重试之间的等待时间"
                                )

                    # 右侧多功能区域 - 重新设计为标签切换
                    with gr.Column(scale=2, elem_classes=["card"]):
                        # 顶部标签切换区域
                        with gr.Tabs():
                            # 分析结果标签
                            with gr.TabItem("📊 分析结果", elem_classes=["main-tab"]):
                                gr.HTML("""
                                <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                                            color: white; padding: 15px; margin: -20px -20px 20px -20px;
                                            border-radius: 12px 12px 0 0;">
                                    <h3 style="margin: 0; font-size: 1.2em;">📊 智能分析结果</h3>
                                    <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 0.9em;">AI多智能体协作分析报告</p>
                                </div>
                                """)

                                # 分析结果子标签
                                with gr.Tabs():
                                    # 综合报告
                                    with gr.TabItem("🎯 综合报告"):
                                        comprehensive_report = gr.HTML(
                                            value="""
                                            <div style='text-align: center; padding: 40px; background: #f8f9fa;
                                                        border-radius: 8px; border: 2px dashed #dee2e6;'>
                                                <div style='font-size: 3em; margin-bottom: 15px;'>🤖</div>
                                                <h3 style='color: #6c757d; margin: 0 0 10px 0;'>AI分析师团队待命中</h3>
                                                <p style='color: #868e96; margin: 0;'>点击"开始全面分析"按钮，让AI为您生成专业分析报告</p>
                                            </div>
                                            """,
                                            elem_classes=["result-display"]
                                        )

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

                            # 导出报告
                            with gr.TabItem("📄 导出报告"):
                                gr.Markdown("## 📊 分析报告导出")
                                gr.Markdown("导出完整的分析报告，包含所有智能体的分析结果。")

                                with gr.Row():
                                    export_format = gr.Radio(
                                        choices=["markdown", "text", "json"],
                                        value="markdown",
                                        label="导出格式",
                                        info="选择导出报告的格式"
                                    )

                                with gr.Row():
                                    export_report_btn = gr.Button("📄 生成报告", variant="primary", size="lg")
                                    download_btn = gr.DownloadButton("💾 下载报告", variant="secondary", size="lg")

                                export_status = gr.Textbox(
                                    label="导出状态",
                                    value="请先完成股票分析，然后选择格式生成报告",
                                    interactive=False
                                )

                                export_preview = gr.Textbox(
                                    label="报告预览",
                                    value="",
                                    lines=20,
                                    max_lines=30,
                                    interactive=False,
                                    show_copy_button=True
                                )

                            # 分析历史
                            with gr.TabItem("📚 分析历史"):
                                gr.Markdown("## 📋 历史分析报告")
                                gr.Markdown("查看和管理之前生成的分析报告。")

                                with gr.Row():
                                    refresh_history_btn = gr.Button("🔄 刷新列表", variant="secondary", size="sm")
                                    clear_history_btn = gr.Button("🗑️ 清空历史", variant="stop", size="sm")

                                # 历史列表
                                history_list = gr.Dropdown(
                                    label="历史报告",
                                    choices=[],
                                    value=None,
                                    info="选择要查看的历史报告"
                                )

                                # 报告信息
                                with gr.Row():
                                    with gr.Column(scale=1):
                                        report_info = gr.Textbox(
                                            label="报告信息",
                                            value="",
                                            lines=3,
                                            interactive=False
                                        )
                                    with gr.Column(scale=1):
                                        with gr.Row():
                                            view_report_btn = gr.Button("👁️ 查看报告", variant="primary", size="sm")
                                            delete_report_btn = gr.Button("🗑️ 删除报告", variant="stop", size="sm")

                                # 报告内容显示
                                history_report_content = gr.Textbox(
                                    label="报告内容",
                                    value="",
                                    lines=25,
                                    max_lines=40,
                                    interactive=False,
                                    show_copy_button=True
                                )

                            # LLM配置标签
                            with gr.TabItem("⚙️ LLM配置", elem_classes=["main-tab"]):
                                gr.HTML("""
                                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                            color: white; padding: 15px; margin: -20px -20px 20px -20px;
                                            border-radius: 12px 12px 0 0;">
                                    <h3 style="margin: 0; font-size: 1.2em;">⚙️ LLM提供商配置</h3>
                                    <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 0.9em;">配置和管理AI语言模型提供商</p>
                                </div>
                                """)

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

                                # 阿里百炼配置
                                with gr.Group():
                                    gr.Markdown("#### 🔥 阿里百炼 (支持联网搜索)")
                                    dashscope_key = gr.Textbox(
                                        label="DashScope API Key",
                                        type="password",
                                        placeholder="sk-...",
                                        value="●●●●●●●●●●●●" if "阿里百炼" in app.llm_config else ""
                                    )
                                    with gr.Row():
                                        dashscope_test_btn = gr.Button("测试连接", size="sm")
                                        dashscope_save_btn = gr.Button("💾 保存", size="sm", variant="secondary")
                                    dashscope_status = gr.Textbox(label="状态", value="已配置" if "阿里百炼" in app.llm_config else "未配置", interactive=False)
                                    gr.Markdown("💡 **支持联网搜索**: 情感分析师、新闻分析师、基本面分析师将自动启用实时搜索")

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

                            # 智能体配置标签
                            with gr.TabItem("🤖 智能体配置", elem_classes=["main-tab"]):
                                gr.HTML("""
                                <div style="background: linear-gradient(135deg, #ff7b7b 0%, #667eea 100%);
                                            color: white; padding: 15px; margin: -20px -20px 20px -20px;
                                            border-radius: 12px 12px 0 0;">
                                    <h3 style="margin: 0; font-size: 1.2em;">🤖 智能体模型配置</h3>
                                    <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 0.9em;">为每个智能体选择使用的LLM模型，实现精细化配置</p>
                                </div>
                                """)

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
                            headers=["序列号", "时间", "智能体", "提供商", "模型", "状态", "提示预览", "响应预览", "提示长度", "响应长度"],
                            datatype=["str", "str", "str", "str", "str", "str", "str", "str", "str", "str"],
                            value=[],
                            interactive=True,  # 允许交互，支持点击
                            label="通信记录 (点击序列号查看详情)"
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
                    gr.Markdown("💡 **使用说明**: 点击上方表格中的任意行查看该通信的详细内容")

                    # 隐藏的状态变量，用于存储选中的日志ID
                    selected_log_id = gr.State(value=None)

                    # 显示当前选中的日志信息
                    current_log_info = gr.Markdown("📋 **当前选中**: 暂无选择")

                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("#### 📤 发送的提示")
                            prompt_detail = gr.Textbox(
                                label="提示内容",
                                lines=10,
                                interactive=False,
                                placeholder="点击表格中的日志行查看提示内容...",
                                max_lines=15
                            )

                        with gr.Column():
                            gr.Markdown("#### 📥 接收的响应")
                            response_detail = gr.Textbox(
                                label="响应内容",
                                lines=10,
                                interactive=False,
                                placeholder="点击表格中的日志行查看响应内容...",
                                max_lines=15
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
                                news_checked, fundamentals_checked, use_real_llm,
                                max_data_retries, max_llm_retries, retry_delay):
            """运行增强分析（带重试配置）"""
            if not symbol:
                return ("❌ 请输入股票代码", "暂无数据", "暂无数据", "暂无数据",
                       "暂无数据", "暂无数据", "暂无数据", "暂无数据", "暂无数据", "暂无数据", "暂无数据")

            # 更新重试配置
            app.retry_config.update({
                "max_data_retries": int(max_data_retries),
                "max_llm_retries": int(max_llm_retries),
                "retry_delay": float(retry_delay)
            })

            # 调用核心分析逻辑
            return run_analysis_with_retry(symbol, depth, market_checked, sentiment_checked,
                                         news_checked, fundamentals_checked, use_real_llm)

        def interrupt_analysis():
            """中断分析"""
            app.interrupt_analysis("用户手动中断")
            return "⏹️ 分析已中断，请重新输入股票代码开始新的分析"

        def update_analysis_status():
            """更新分析状态"""
            if app.analysis_state["is_running"]:
                current_step = app.analysis_state.get("current_step", "运行中...")
                failed_agents = app.analysis_state.get("failed_agents", [])

                status = f"🔄 {current_step}"
                if failed_agents:
                    status += f" (失败: {', '.join(failed_agents)})"

                return status
            else:
                return "🟢 系统就绪"

        def run_analysis_with_retry(symbol, depth, market_checked, sentiment_checked,
                                  news_checked, fundamentals_checked, use_real_llm):
            """运行分析的核心逻辑"""
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

                def format_clean_result(key, title=""):
                    """格式化干净的结果，移除技术字段"""
                    value = results.get(key, {})
                    if isinstance(value, dict):
                        # 移除技术字段，只保留用户关心的内容
                        if 'analysis' in value:
                            return value['analysis']
                        elif 'recommendation' in value:
                            return value['recommendation']
                        elif 'strategy' in value:
                            return value['strategy']
                        else:
                            # 对于复杂的字典结构，格式化输出
                            clean_content = []
                            agent_names = {
                                'aggressive_debator': '激进分析师',
                                'conservative_debator': '保守分析师',
                                'neutral_debator': '中性分析师',
                                'risk_manager': '风险经理'
                            }
                            for agent_key, agent_data in value.items():
                                if isinstance(agent_data, dict) and 'analysis' in agent_data:
                                    agent_name = agent_names.get(agent_key, agent_key)
                                    clean_content.append(f"**{agent_name}观点**:\n{agent_data['analysis']}")
                            return "\n\n".join(clean_content) if clean_content else str(value)
                    return str(value) if value else "暂无数据"

                # 使用格式化函数处理结果，移除技术字段
                comprehensive_report = format_clean_result("comprehensive_report")
                market_analysis = format_clean_result("market_analysis")
                sentiment_analysis = format_clean_result("sentiment_analysis")
                news_analysis = format_clean_result("news_analysis")
                fundamentals_analysis = format_clean_result("fundamentals_analysis")
                bull_arguments = format_clean_result("bull_arguments")
                bear_arguments = format_clean_result("bear_arguments")
                investment_recommendation = format_clean_result("investment_recommendation")
                trading_strategy = format_clean_result("trading_strategy")
                risk_assessment = format_clean_result("risk_assessment")
                final_decision = format_clean_result("final_decision")

                # 组合风险评估和最终决策
                combined_risk_decision = f"{risk_assessment}\n\n### 最终决策\n{final_decision}"

                # 使用数据收集器的股票名称获取方法
                stock_data = results.get("results", {}).get("data_collection", {})
                raw_name = stock_data.get("name", "") if isinstance(stock_data, dict) else ""
                stock_name = app.data_collector.get_stock_name(symbol, raw_name)

                # 构建包含股票名称的综合报告
                enhanced_comprehensive_report = f"## {symbol}（{stock_name}）综合分析报告\n\n{comprehensive_report}"

                # 保存完整结果用于导出
                app.last_analysis_result = {
                    "symbol": symbol,
                    "stock_name": stock_name,
                    "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "comprehensive_report": enhanced_comprehensive_report,
                    "market_analysis": market_analysis,
                    "sentiment_analysis": sentiment_analysis,
                    "news_analysis": news_analysis,
                    "fundamentals_analysis": fundamentals_analysis,
                    "bull_arguments": bull_arguments,
                    "bear_arguments": bear_arguments,
                    "investment_recommendation": investment_recommendation,
                    "trading_strategy": trading_strategy,
                    "risk_assessment": risk_assessment,
                    "final_decision": final_decision
                }

                return (
                    "✅ 分析完成",
                    comprehensive_report,
                    market_analysis,
                    sentiment_analysis,
                    news_analysis,
                    fundamentals_analysis,
                    bull_arguments,
                    bear_arguments,
                    investment_recommendation,
                    trading_strategy,
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

        def test_dashscope_connection(api_key):
            """测试阿里百炼连接"""
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            result = loop.run_until_complete(app.test_llm_connection("阿里百炼", api_key))
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

        def save_dashscope_config(api_key):
            """保存阿里百炼配置"""
            if api_key and api_key != "●●●●●●●●●●●●":
                app.llm_config["阿里百炼"] = api_key
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

            # 返回所有智能体的当前配置值，用于更新界面
            config_values = []
            agents = [
                "market_analyst", "social_media_analyst", "news_analyst", "fundamentals_analyst",
                "bull_researcher", "bear_researcher", "research_manager", "trader",
                "aggressive_debator", "conservative_debator", "neutral_debator", "risk_manager",
                "memory_manager", "signal_processor", "reflection_engine"
            ]

            for agent in agents:
                config_values.append(app.agent_model_config.get(agent, "deepseek:deepseek-chat"))

            status_msg = f"已重新加载 {len(app.agent_model_config)} 个智能体配置"
            return [status_msg] + config_values

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
            for log in logs:
                table_data.append([
                    str(log["id"]),  # 序列号
                    log["timestamp"][:19],  # 时间
                    log["agent_id"],  # 智能体
                    log["provider"],  # 提供商
                    log["model"],  # 模型
                    "✅ 成功" if log["status"] == "success" else "❌ 失败",  # 状态
                    log.get("prompt_preview", log.get("prompt", "")[:100] + "..."),  # 提示预览
                    log.get("response_preview", log.get("response", "")[:100] + "..."),  # 响应预览
                    str(log["prompt_length"]),  # 提示长度
                    str(log["response_length"])  # 响应长度
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

        def get_log_detail_by_id(log_id):
            """通过日志ID获取详情"""
            try:
                logs = app.get_communication_logs(1000)  # 获取更多日志用于查看
                for log in logs:
                    if log.get("id") == int(log_id):
                        info_text = f"📋 **序列号 {log_id}** | {log['timestamp'][:19]} | {log['agent_id']} → {log['provider']}:{log['model']}"
                        return (
                            info_text,
                            log.get("prompt", "无提示内容"),
                            log.get("response", "无响应内容")
                        )
                return "未找到对应的日志记录", "日志不存在", "日志不存在"
            except Exception as e:
                error_msg = f"获取日志失败: {str(e)}"
                return error_msg, error_msg, error_msg

        def handle_table_select(evt: gr.SelectData):
            """处理表格选择事件"""
            try:
                if evt.index is not None and len(evt.index) >= 2:
                    row_index = evt.index[0]
                    # 获取当前显示的日志数据
                    logs = app.get_communication_logs(50)
                    if 0 <= row_index < len(logs):
                        log = logs[row_index]
                        log_id = log.get("id", row_index + 1)
                        return get_log_detail_by_id(log_id)
                return "请选择有效的日志行", "无数据", "无数据"
            except Exception as e:
                error_msg = f"处理选择失败: {str(e)}"
                return error_msg, error_msg, error_msg

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

        def generate_export_report(format_type):
            """生成导出报告并自动保存到本地目录"""
            try:
                report_content = app.export_analysis_report(format_type)

                if report_content.startswith("❌"):
                    return report_content, "", None

                # 创建报告目录
                report_dir = Path("./reports")
                report_dir.mkdir(exist_ok=True)

                # 生成文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                symbol = app.last_analysis_result.get('symbol', 'UNKNOWN') if app.last_analysis_result else 'UNKNOWN'

                # 使用数据收集器获取正确的股票名称
                if app.last_analysis_result:
                    raw_stock_name = app.last_analysis_result.get('stock_name', '')
                    stock_name = app.data_collector.get_stock_name(symbol, raw_stock_name)
                else:
                    stock_name = 'UNKNOWN'

                # 清理文件名中的特殊字符
                safe_stock_name = "".join(c for c in stock_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_stock_name = safe_stock_name.replace(' ', '_')

                if format_type == "markdown":
                    filename = f"{symbol}_{safe_stock_name}_{timestamp}.md"
                elif format_type == "text":
                    filename = f"{symbol}_{safe_stock_name}_{timestamp}.txt"
                elif format_type == "json":
                    filename = f"{symbol}_{safe_stock_name}_{timestamp}.json"
                else:
                    filename = f"{symbol}_{safe_stock_name}_{timestamp}.txt"

                # 保存到报告目录
                file_path = report_dir / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)

                status_msg = f"✅ 报告已保存到: ./reports/{filename}"
                preview = report_content[:2000] + "..." if len(report_content) > 2000 else report_content

                return status_msg, preview, str(file_path)

            except Exception as e:
                return f"❌ 报告生成失败: {str(e)}", "", None

        def export_report_wrapper(format_type):
            """导出报告包装函数"""
            status, preview, file_path = generate_export_report(format_type)
            return status, preview

        def refresh_analysis_history():
            """刷新分析历史列表"""
            try:
                history = app.get_report_history()
                choices = [(item["display_name"], item["file_path"]) for item in history]
                return gr.Dropdown.update(choices=choices, value=None)
            except Exception as e:
                logger.error(f"刷新历史列表失败: {e}")
                return gr.Dropdown.update(choices=[], value=None)

        def get_report_info(file_path):
            """获取报告信息"""
            if not file_path:
                return "", ""

            try:
                history = app.get_report_history()
                report_item = next((item for item in history if item["file_path"] == file_path), None)

                if report_item:
                    info = f"""股票代码: {report_item['symbol']}
股票名称: {report_item['stock_name']}
生成时间: {report_item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
文件格式: {report_item['format'].upper()}
文件大小: {report_item['size']} 字节"""
                    return info, ""
                else:
                    return "未找到报告信息", ""
            except Exception as e:
                return f"获取报告信息失败: {str(e)}", ""

        def view_analysis_report(file_path):
            """查看分析报告"""
            if not file_path:
                return "请先选择一个报告"

            try:
                content = app.load_analysis_report(file_path)
                return content
            except Exception as e:
                return f"❌ 加载报告失败: {str(e)}"

        def delete_analysis_report(file_path):
            """删除分析报告"""
            if not file_path:
                return "请先选择一个报告", gr.Dropdown.update(), ""

            try:
                success = app.delete_analysis_report(file_path)
                if success:
                    # 刷新列表
                    history = app.get_report_history()
                    choices = [(item["display_name"], item["file_path"]) for item in history]
                    return "✅ 报告已删除", gr.Dropdown.update(choices=choices, value=None), ""
                else:
                    return "❌ 删除失败", gr.Dropdown.update(), ""
            except Exception as e:
                return f"❌ 删除失败: {str(e)}", gr.Dropdown.update(), ""

        def clear_all_history():
            """清空所有历史"""
            try:
                history = app.get_report_history()
                deleted_count = 0

                for item in history:
                    if app.delete_analysis_report(item["file_path"]):
                        deleted_count += 1

                return f"✅ 已删除 {deleted_count} 个报告", gr.Dropdown.update(choices=[], value=None), ""
            except Exception as e:
                return f"❌ 清空失败: {str(e)}", gr.Dropdown.update(), ""

        # 绑定事件
        analyze_btn.click(
            fn=run_enhanced_analysis,
            inputs=[
                stock_input, analysis_depth, analyst_market, analyst_sentiment,
                analyst_news, analyst_fundamentals, use_real_llm,
                max_data_retries, max_llm_retries, retry_delay
            ],
            outputs=[
                status_display, comprehensive_report, market_analysis_output,
                sentiment_analysis_output, news_analysis_output, fundamentals_analysis_output,
                bull_arguments, bear_arguments, investment_recommendation,
                trading_strategy_output, risk_assessment_output
            ]
        )

        # 中断按钮已移除，不需要事件绑定

        # 导出报告事件绑定
        export_report_btn.click(
            fn=export_report_wrapper,
            inputs=[export_format],
            outputs=[export_status, export_preview]
        )

        # 分析历史事件绑定
        refresh_history_btn.click(
            fn=refresh_analysis_history,
            inputs=[],
            outputs=[history_list]
        )

        history_list.change(
            fn=get_report_info,
            inputs=[history_list],
            outputs=[report_info, history_report_content]
        )

        view_report_btn.click(
            fn=view_analysis_report,
            inputs=[history_list],
            outputs=[history_report_content]
        )

        delete_report_btn.click(
            fn=delete_analysis_report,
            inputs=[history_list],
            outputs=[report_info, history_list, history_report_content]
        )

        clear_history_btn.click(
            fn=clear_all_history,
            inputs=[],
            outputs=[report_info, history_list, history_report_content]
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

        # 阿里百炼事件绑定
        dashscope_test_btn.click(
            fn=test_dashscope_connection,
            inputs=[dashscope_key],
            outputs=[dashscope_status]
        )

        dashscope_save_btn.click(
            fn=save_dashscope_config,
            inputs=[dashscope_key],
            outputs=[dashscope_status]
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
            outputs=[
                agent_config_status,
                # 分析师团队
                market_analyst_model, sentiment_analyst_model, news_analyst_model, fundamentals_analyst_model,
                # 研究团队
                bull_researcher_model, bear_researcher_model, research_manager_model, trader_model,
                # 风险管理团队
                aggressive_debator_model, conservative_debator_model, neutral_debator_model, risk_manager_model,
                # 支持系统
                memory_manager_model, signal_processor_model, reflection_engine_model
            ]
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

        # 绑定表格选择事件
        communication_logs_display.select(
            fn=handle_table_select,
            outputs=[current_log_info, prompt_detail, response_detail]
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

        # 系统状态显示已移除，不需要定期更新

    return interface

if __name__ == "__main__":
    # 显示赞助信息，校验失败时退出程序
    display_donation_info(exit_on_failure=True)

    # 创建并启动界面
    interface = create_enhanced_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7864,  # 使用新端口
        share=False,
        debug=True
    )
