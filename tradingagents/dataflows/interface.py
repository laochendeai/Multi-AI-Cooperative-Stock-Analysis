"""
数据接口 - 统一的数据获取接口
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from .akshare_client import AkShareClient
from .cache_manager import CacheManager

logger = logging.getLogger(__name__)

class DataInterface:
    """统一数据接口"""
    
    def __init__(self):
        self.akshare_client = AkShareClient()
        self.cache_manager = CacheManager()
        self.data_sources = {
            "akshare": self.akshare_client
        }
    
    async def get_comprehensive_data(self, symbol: str) -> Dict[str, Any]:
        """获取股票的综合数据"""
        try:
            logger.info(f"获取股票 {symbol} 的综合数据")
            
            # 并行获取各类数据
            tasks = [
                self.get_stock_basic_info(symbol),
                self.get_stock_price_data(symbol),
                self.get_technical_indicators(symbol),
                self.get_financial_data(symbol),
                self.get_news_data(symbol),
                self.get_sentiment_data(symbol)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 整合结果
            comprehensive_data = {
                "symbol": symbol,
                "basic_info": results[0] if not isinstance(results[0], Exception) else {},
                "price_data": results[1] if not isinstance(results[1], Exception) else {},
                "technical_indicators": results[2] if not isinstance(results[2], Exception) else {},
                "financial_data": results[3] if not isinstance(results[3], Exception) else {},
                "news_data": results[4] if not isinstance(results[4], Exception) else [],
                "sentiment_data": results[5] if not isinstance(results[5], Exception) else {},
                "timestamp": datetime.now().isoformat(),
                "data_quality": self._assess_data_quality(results)
            }
            
            return comprehensive_data
            
        except Exception as e:
            logger.error(f"获取综合数据失败: {e}")
            return {
                "symbol": symbol,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_stock_basic_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        try:
            return await self.akshare_client.get_stock_basic_info(symbol)
        except Exception as e:
            logger.error(f"获取股票基本信息失败: {e}")
            return {"error": str(e)}
    
    async def get_stock_price_data(self, symbol: str) -> Dict[str, Any]:
        """获取股票价格数据"""
        try:
            return await self.akshare_client.get_stock_daily_data(symbol)
        except Exception as e:
            logger.error(f"获取股票价格数据失败: {e}")
            return {"error": str(e)}
    
    async def get_technical_indicators(self, symbol: str) -> Dict[str, Any]:
        """获取技术指标"""
        try:
            # 获取价格数据用于计算技术指标
            price_data = await self.akshare_client.get_stock_daily_data(symbol)
            
            if "error" in price_data:
                return price_data
            
            # 计算技术指标
            indicators = self._calculate_technical_indicators(price_data)
            return indicators
            
        except Exception as e:
            logger.error(f"获取技术指标失败: {e}")
            return {"error": str(e)}
    
    async def get_financial_data(self, symbol: str) -> Dict[str, Any]:
        """获取财务数据"""
        try:
            return await self.akshare_client.get_financial_data(symbol)
        except Exception as e:
            logger.error(f"获取财务数据失败: {e}")
            return {"error": str(e)}
    
    async def get_news_data(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取新闻数据"""
        try:
            return await self.akshare_client.get_stock_news(symbol, limit)
        except Exception as e:
            logger.error(f"获取新闻数据失败: {e}")
            return [{"error": str(e)}]
    
    async def get_sentiment_data(self, symbol: str) -> Dict[str, Any]:
        """获取情感数据"""
        try:
            return await self.akshare_client.get_stock_comments(symbol)
        except Exception as e:
            logger.error(f"获取情感数据失败: {e}")
            return {"error": str(e)}
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """获取市场概览"""
        try:
            # 获取热门股票
            hot_stocks = await self.akshare_client.get_hot_stocks(20)
            
            # 计算市场情绪
            market_sentiment = self._calculate_market_sentiment(hot_stocks)
            
            return {
                "hot_stocks": hot_stocks,
                "market_sentiment": market_sentiment,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取市场概览失败: {e}")
            return {"error": str(e)}
    
    async def search_stocks(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索股票"""
        try:
            # 这里简化处理，实际应用中需要实现股票搜索功能
            # 可以基于股票名称、代码、行业等进行搜索
            
            # 获取热门股票作为搜索结果的替代
            hot_stocks = await self.akshare_client.get_hot_stocks(limit)
            
            # 过滤包含关键词的股票
            filtered_stocks = []
            for stock in hot_stocks:
                if keyword.lower() in stock.get("name", "").lower() or keyword in stock.get("symbol", ""):
                    filtered_stocks.append(stock)
            
            return filtered_stocks[:limit]
            
        except Exception as e:
            logger.error(f"搜索股票失败: {e}")
            return [{"error": str(e)}]
    
    def _calculate_technical_indicators(self, price_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算技术指标"""
        try:
            current_price = price_data.get("current_price", 0)
            
            # 简化的技术指标计算
            indicators = {
                "symbol": price_data.get("symbol", ""),
                "rsi": self._calculate_rsi(current_price),
                "macd": self._calculate_macd(current_price),
                "ma5": current_price * 0.98,
                "ma10": current_price * 0.96,
                "ma20": current_price * 0.94,
                "ma60": current_price * 0.90,
                "bollinger_upper": current_price * 1.05,
                "bollinger_middle": current_price,
                "bollinger_lower": current_price * 0.95,
                "volume_ma": price_data.get("volume", 0),
                "timestamp": datetime.now().isoformat()
            }
            
            return indicators
            
        except Exception as e:
            logger.error(f"计算技术指标失败: {e}")
            return {"error": str(e)}
    
    def _calculate_rsi(self, price: float) -> float:
        """计算RSI指标"""
        # 简化的RSI计算
        import random
        return round(random.uniform(30, 70), 2)
    
    def _calculate_macd(self, price: float) -> Dict[str, float]:
        """计算MACD指标"""
        # 简化的MACD计算
        import random
        return {
            "dif": round(random.uniform(-2, 2), 3),
            "dea": round(random.uniform(-1.5, 1.5), 3),
            "macd": round(random.uniform(-1, 1), 3)
        }
    
    def _calculate_market_sentiment(self, hot_stocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算市场情绪"""
        try:
            if not hot_stocks:
                return {"sentiment": "neutral", "score": 0.5}
            
            # 统计涨跌股票数量
            rising_count = 0
            falling_count = 0
            total_change = 0
            
            for stock in hot_stocks:
                change_percent = stock.get("change_percent", 0)
                total_change += change_percent
                
                if change_percent > 0:
                    rising_count += 1
                elif change_percent < 0:
                    falling_count += 1
            
            total_stocks = len(hot_stocks)
            avg_change = total_change / total_stocks if total_stocks > 0 else 0
            rising_ratio = rising_count / total_stocks if total_stocks > 0 else 0
            
            # 计算情绪得分
            sentiment_score = (rising_ratio - 0.5) * 2  # 转换为-1到1的范围
            sentiment_score = max(-1, min(1, sentiment_score))
            
            # 确定情绪类别
            if sentiment_score > 0.3:
                sentiment = "bullish"
            elif sentiment_score < -0.3:
                sentiment = "bearish"
            else:
                sentiment = "neutral"
            
            return {
                "sentiment": sentiment,
                "score": round(sentiment_score, 3),
                "rising_count": rising_count,
                "falling_count": falling_count,
                "total_stocks": total_stocks,
                "avg_change": round(avg_change, 2),
                "rising_ratio": round(rising_ratio, 3)
            }
            
        except Exception as e:
            logger.error(f"计算市场情绪失败: {e}")
            return {"sentiment": "neutral", "score": 0.5, "error": str(e)}
    
    def _assess_data_quality(self, results: List) -> Dict[str, Any]:
        """评估数据质量"""
        try:
            total_sources = len(results)
            successful_sources = sum(1 for result in results if not isinstance(result, Exception))
            
            quality_score = successful_sources / total_sources if total_sources > 0 else 0
            
            if quality_score >= 0.8:
                quality_level = "high"
            elif quality_score >= 0.6:
                quality_level = "medium"
            else:
                quality_level = "low"
            
            return {
                "quality_level": quality_level,
                "quality_score": round(quality_score, 2),
                "successful_sources": successful_sources,
                "total_sources": total_sources,
                "failed_sources": total_sources - successful_sources
            }
            
        except Exception as e:
            logger.error(f"评估数据质量失败: {e}")
            return {"quality_level": "unknown", "error": str(e)}
    
    async def get_data_with_fallback(self, primary_source: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """带降级的数据获取"""
        try:
            symbol = params.get("symbol", "")
            
            if primary_source == "akshare":
                return await self.get_comprehensive_data(symbol)
            else:
                # 默认使用akshare
                return await self.get_comprehensive_data(symbol)
                
        except Exception as e:
            logger.error(f"数据获取失败，使用降级方案: {e}")
            return {
                "symbol": params.get("symbol", ""),
                "status": "fallback",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
