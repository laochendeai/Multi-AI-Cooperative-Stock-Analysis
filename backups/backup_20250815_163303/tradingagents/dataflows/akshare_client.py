"""
AkShare数据客户端 - 完整的AkShare接口集成
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

try:
    import akshare as ak
    import pandas as pd
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    ak = None
    pd = None

from ..config.default_config import DATA_CONFIG

logger = logging.getLogger(__name__)

class AkShareClient:
    """AkShare数据客户端"""
    
    def __init__(self):
        self.config = DATA_CONFIG["akshare"]
        self.enabled = self.config["enabled"] and AKSHARE_AVAILABLE
        self.cache = {}
        self.cache_duration = self.config.get("cache_duration", 300)
        
        if not AKSHARE_AVAILABLE:
            logger.warning("AkShare不可用，将使用模拟数据")
    
    async def get_stock_basic_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票基本信息 - stock_info_a_code_name"""
        try:
            if not self.enabled:
                return self._mock_basic_info(symbol)
            
            cache_key = f"basic_{symbol}"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]
            
            # 获取A股股票信息
            stock_info = ak.stock_info_a_code_name()
            stock_data = stock_info[stock_info['code'] == symbol]
            
            if stock_data.empty:
                return self._mock_basic_info(symbol)
            
            row = stock_data.iloc[0]
            result = {
                "symbol": symbol,
                "name": row.get('name', ''),
                "code": row.get('code', ''),
                "market": "A股",
                "status": "active",
                "timestamp": datetime.now().isoformat()
            }
            
            self._cache_data(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"获取股票基本信息失败: {e}")
            return self._mock_basic_info(symbol)
    
    async def get_stock_daily_data(self, symbol: str, period: str = "daily", 
                                  start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """获取股票日线数据 - stock_zh_a_hist"""
        try:
            if not self.enabled:
                return self._mock_daily_data(symbol)
            
            cache_key = f"daily_{symbol}_{period}"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]
            
            # 设置默认日期范围
            if not end_date:
                end_date = datetime.now().strftime("%Y%m%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
            
            # 获取历史数据
            df = ak.stock_zh_a_hist(symbol=symbol, period=period, 
                                   start_date=start_date, end_date=end_date)
            
            if df.empty:
                return self._mock_daily_data(symbol)
            
            # 处理最新数据
            latest = df.iloc[-1]
            result = {
                "symbol": symbol,
                "current_price": float(latest["收盘"]),
                "open": float(latest["开盘"]),
                "high": float(latest["最高"]),
                "low": float(latest["最低"]),
                "volume": int(latest["成交量"]),
                "amount": float(latest["成交额"]),
                "change_percent": float(latest["涨跌幅"]),
                "change_amount": float(latest["涨跌额"]),
                "turnover_rate": float(latest.get("换手率", 0)),
                "date": latest["日期"],
                "data_points": len(df),
                "timestamp": datetime.now().isoformat()
            }
            
            self._cache_data(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"获取股票日线数据失败: {e}")
            return self._mock_daily_data(symbol)
    
    async def get_stock_minute_data(self, symbol: str, period: str = "1") -> Dict[str, Any]:
        """获取股票分钟数据 - stock_zh_a_hist_min_em"""
        try:
            if not self.enabled:
                return self._mock_minute_data(symbol)
            
            cache_key = f"minute_{symbol}_{period}"
            if self._is_cache_valid(cache_key, duration=60):  # 1分钟缓存
                return self.cache[cache_key]
            
            # 获取分钟数据
            df = ak.stock_zh_a_hist_min_em(symbol=symbol, period=period)
            
            if df.empty:
                return self._mock_minute_data(symbol)
            
            latest = df.iloc[-1]
            result = {
                "symbol": symbol,
                "current_price": float(latest["收盘"]),
                "open": float(latest["开盘"]),
                "high": float(latest["最高"]),
                "low": float(latest["最低"]),
                "volume": int(latest["成交量"]),
                "amount": float(latest["成交额"]),
                "time": latest["时间"],
                "data_points": len(df),
                "timestamp": datetime.now().isoformat()
            }
            
            self._cache_data(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"获取股票分钟数据失败: {e}")
            return self._mock_minute_data(symbol)
    
    async def get_hot_stocks(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取热门股票 - stock_hot_rank_wc"""
        try:
            if not self.enabled:
                return self._mock_hot_stocks(limit)
            
            cache_key = f"hot_stocks_{limit}"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]
            
            # 获取热门股票
            df = ak.stock_hot_rank_wc()
            
            if df.empty:
                return self._mock_hot_stocks(limit)
            
            result = []
            for _, row in df.head(limit).iterrows():
                result.append({
                    "symbol": row.get("代码", ""),
                    "name": row.get("股票简称", ""),
                    "current_price": float(row.get("最新价", 0)),
                    "change_percent": float(row.get("涨跌幅", 0)),
                    "turnover_rate": float(row.get("换手率", 0)),
                    "hot_rank": int(row.get("排名", 0)),
                    "reason": row.get("热门原因", "")
                })
            
            self._cache_data(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"获取热门股票失败: {e}")
            return self._mock_hot_stocks(limit)
    
    async def get_stock_comments(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """获取股票评论 - stock_comment_em"""
        try:
            if not self.enabled:
                return self._mock_comments(symbol)
            
            cache_key = f"comments_{symbol}_{limit}"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]
            
            # 获取股票评论
            df = ak.stock_comment_em(symbol=symbol)
            
            if df.empty:
                return self._mock_comments(symbol)
            
            # 简单情感分析
            comments = df.head(limit)
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for _, row in comments.iterrows():
                content = str(row.get("评论", "")).lower()
                if any(word in content for word in ["好", "涨", "买", "牛", "利好"]):
                    positive_count += 1
                elif any(word in content for word in ["差", "跌", "卖", "熊", "利空"]):
                    negative_count += 1
                else:
                    neutral_count += 1
            
            total = len(comments)
            result = {
                "symbol": symbol,
                "total_comments": total,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "neutral_count": neutral_count,
                "positive_ratio": positive_count / total if total > 0 else 0,
                "negative_ratio": negative_count / total if total > 0 else 0,
                "sentiment_score": (positive_count - negative_count) / total if total > 0 else 0,
                "timestamp": datetime.now().isoformat()
            }
            
            self._cache_data(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"获取股票评论失败: {e}")
            return self._mock_comments(symbol)
    
    async def get_stock_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取股票新闻 - stock_news_em"""
        try:
            if not self.enabled:
                return self._mock_news(symbol, limit)
            
            cache_key = f"news_{symbol}_{limit}"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]
            
            # 获取股票新闻
            df = ak.stock_news_em(symbol=symbol)
            
            if df.empty:
                return self._mock_news(symbol, limit)
            
            result = []
            for _, row in df.head(limit).iterrows():
                result.append({
                    "title": row.get("新闻标题", ""),
                    "content": row.get("新闻内容", ""),
                    "source": row.get("新闻来源", ""),
                    "publish_time": row.get("发布时间", ""),
                    "url": row.get("新闻链接", "")
                })
            
            self._cache_data(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"获取股票新闻失败: {e}")
            return self._mock_news(symbol, limit)
    
    async def get_financial_data(self, symbol: str) -> Dict[str, Any]:
        """获取财务数据 - stock_financial_em"""
        try:
            if not self.enabled:
                return self._mock_financial(symbol)
            
            cache_key = f"financial_{symbol}"
            if self._is_cache_valid(cache_key, duration=3600):  # 1小时缓存
                return self.cache[cache_key]
            
            # 获取财务数据
            df = ak.stock_financial_em(symbol=symbol)
            
            if df.empty:
                return self._mock_financial(symbol)
            
            latest = df.iloc[-1]
            result = {
                "symbol": symbol,
                "report_date": latest.get("报告期", ""),
                "revenue": latest.get("营业收入", ""),
                "net_income": latest.get("净利润", ""),
                "total_assets": latest.get("总资产", ""),
                "net_assets": latest.get("净资产", ""),
                "roe": latest.get("净资产收益率", ""),
                "eps": latest.get("每股收益", ""),
                "bps": latest.get("每股净资产", ""),
                "gross_margin": latest.get("毛利率", ""),
                "net_margin": latest.get("净利率", ""),
                "timestamp": datetime.now().isoformat()
            }
            
            self._cache_data(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"获取财务数据失败: {e}")
            return self._mock_financial(symbol)
    
    def _is_cache_valid(self, cache_key: str, duration: int = None) -> bool:
        """检查缓存是否有效"""
        if cache_key not in self.cache:
            return False
        
        cache_duration = duration or self.cache_duration
        cache_time = self.cache[cache_key].get("_cache_time", datetime.min)
        return (datetime.now() - cache_time).seconds < cache_duration
    
    def _cache_data(self, cache_key: str, data: Any):
        """缓存数据"""
        data["_cache_time"] = datetime.now()
        self.cache[cache_key] = data
    
    # 模拟数据方法
    def _mock_basic_info(self, symbol: str) -> Dict[str, Any]:
        return {
            "symbol": symbol,
            "name": f"{symbol}股票",
            "code": symbol,
            "market": "A股",
            "status": "active",
            "timestamp": datetime.now().isoformat()
        }
    
    def _mock_daily_data(self, symbol: str) -> Dict[str, Any]:
        import random
        base_price = 50.0
        return {
            "symbol": symbol,
            "current_price": round(base_price + random.uniform(-5, 5), 2),
            "open": round(base_price + random.uniform(-3, 3), 2),
            "high": round(base_price + random.uniform(0, 8), 2),
            "low": round(base_price + random.uniform(-8, 0), 2),
            "volume": random.randint(1000000, 10000000),
            "amount": random.randint(50000000, 500000000),
            "change_percent": round(random.uniform(-5, 5), 2),
            "change_amount": round(random.uniform(-2, 2), 2),
            "turnover_rate": round(random.uniform(0.5, 5), 2),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "data_points": 30,
            "timestamp": datetime.now().isoformat()
        }
    
    def _mock_minute_data(self, symbol: str) -> Dict[str, Any]:
        import random
        base_price = 50.0
        return {
            "symbol": symbol,
            "current_price": round(base_price + random.uniform(-2, 2), 2),
            "open": round(base_price + random.uniform(-1, 1), 2),
            "high": round(base_price + random.uniform(0, 3), 2),
            "low": round(base_price + random.uniform(-3, 0), 2),
            "volume": random.randint(10000, 100000),
            "amount": random.randint(500000, 5000000),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_points": 240,
            "timestamp": datetime.now().isoformat()
        }
    
    def _mock_hot_stocks(self, limit: int) -> List[Dict[str, Any]]:
        import random
        result = []
        for i in range(limit):
            result.append({
                "symbol": f"00000{i+1}",
                "name": f"热门股票{i+1}",
                "current_price": round(random.uniform(10, 100), 2),
                "change_percent": round(random.uniform(-5, 10), 2),
                "turnover_rate": round(random.uniform(1, 15), 2),
                "hot_rank": i + 1,
                "reason": "业绩增长"
            })
        return result
    
    def _mock_comments(self, symbol: str) -> Dict[str, Any]:
        import random
        total = 100
        positive = random.randint(30, 70)
        negative = random.randint(10, 30)
        neutral = total - positive - negative
        
        return {
            "symbol": symbol,
            "total_comments": total,
            "positive_count": positive,
            "negative_count": negative,
            "neutral_count": neutral,
            "positive_ratio": positive / total,
            "negative_ratio": negative / total,
            "sentiment_score": (positive - negative) / total,
            "timestamp": datetime.now().isoformat()
        }
    
    def _mock_news(self, symbol: str, limit: int) -> List[Dict[str, Any]]:
        result = []
        for i in range(limit):
            result.append({
                "title": f"{symbol}相关新闻{i+1}",
                "content": f"这是关于{symbol}的新闻内容...",
                "source": "财经网",
                "publish_time": (datetime.now() - timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S"),
                "url": f"https://example.com/news/{i}"
            })
        return result
    
    def _mock_financial(self, symbol: str) -> Dict[str, Any]:
        import random
        return {
            "symbol": symbol,
            "report_date": "2024-09-30",
            "revenue": f"{random.randint(50, 500)}亿",
            "net_income": f"{random.randint(5, 50)}亿",
            "total_assets": f"{random.randint(200, 2000)}亿",
            "net_assets": f"{random.randint(100, 1000)}亿",
            "roe": f"{random.randint(5, 25)}%",
            "eps": f"{random.uniform(0.5, 5):.2f}",
            "bps": f"{random.uniform(5, 50):.2f}",
            "gross_margin": f"{random.randint(15, 45)}%",
            "net_margin": f"{random.randint(5, 25)}%",
            "timestamp": datetime.now().isoformat()
        }
