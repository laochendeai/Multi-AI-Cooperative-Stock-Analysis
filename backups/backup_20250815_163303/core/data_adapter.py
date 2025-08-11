#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据适配器 - 为tradingagents架构提供数据支持
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DataAdapter:
    """数据适配器 - 桥接现有数据收集器和tradingagents架构"""
    
    def __init__(self, enhanced_app):
        """
        初始化数据适配器
        
        Args:
            enhanced_app: EnhancedTradingAgentsApp实例
        """
        self.enhanced_app = enhanced_app
        self.data_collector = enhanced_app.data_collector
        
    async def get_comprehensive_data(self, symbol: str) -> Dict[str, Any]:
        """
        获取股票综合数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            综合数据字典
        """
        try:
            logger.info(f"获取股票 {symbol} 的综合数据")
            
            # 使用现有的数据收集器
            stock_data = await self._collect_stock_data(symbol)
            
            # 转换为tradingagents期望的格式
            comprehensive_data = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "price_data": stock_data.get("price_data", {}),
                "technical_indicators": stock_data.get("technical_indicators", {}),
                "financial_data": stock_data.get("financial_data", {}),
                "news_data": stock_data.get("news_data", []),
                "market_data": stock_data.get("market_data", {}),
                "sentiment_data": stock_data.get("sentiment_data", {}),
                "data_sources": ["enhanced_app_collector"],
                "data_quality": "high" if stock_data else "low"
            }
            
            return comprehensive_data
            
        except Exception as e:
            logger.error(f"获取综合数据失败: {e}")
            return self._get_mock_comprehensive_data(symbol)
    
    async def _collect_stock_data(self, symbol: str) -> Dict[str, Any]:
        """使用现有数据收集器获取数据"""
        try:
            # 调用现有的数据收集方法
            stock_data = await self.enhanced_app._collect_stock_data(symbol)
            return stock_data
        except Exception as e:
            logger.error(f"数据收集失败: {e}")
            return {}
    
    def _get_mock_comprehensive_data(self, symbol: str) -> Dict[str, Any]:
        """获取模拟综合数据"""
        return {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "price_data": {
                "current_price": 100.0,
                "open_price": 98.5,
                "high_price": 102.0,
                "low_price": 97.0,
                "volume": 1000000,
                "change": 1.5,
                "change_percent": 1.52
            },
            "technical_indicators": {
                "rsi": 55.8,
                "macd": 0.5,
                "ma5": 99.2,
                "ma10": 98.8,
                "ma20": 97.5
            },
            "financial_data": {
                "pe_ratio": 15.2,
                "pb_ratio": 2.1,
                "market_cap": 50000000000,
                "revenue": 10000000000,
                "profit": 1000000000
            },
            "news_data": [
                {
                    "title": f"{symbol}相关新闻标题",
                    "content": "模拟新闻内容",
                    "timestamp": datetime.now().isoformat(),
                    "sentiment": "positive"
                }
            ],
            "market_data": {
                "market_status": "open",
                "trading_volume": 1000000,
                "turnover_rate": 2.5
            },
            "sentiment_data": {
                "overall_sentiment": "positive",
                "sentiment_score": 0.75,
                "social_mentions": 100
            },
            "data_sources": ["mock_data"],
            "data_quality": "mock"
        }

class TradingAgentsDataInterface:
    """TradingAgents数据接口适配器"""
    
    def __init__(self, enhanced_app):
        self.adapter = DataAdapter(enhanced_app)
        self.enhanced_app = enhanced_app
    
    async def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """
        获取股票数据 - tradingagents.dataflows.interface期望的接口
        
        Args:
            symbol: 股票代码
            
        Returns:
            股票数据
        """
        return await self.adapter.get_comprehensive_data(symbol)
    
    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """获取市场数据"""
        comprehensive_data = await self.adapter.get_comprehensive_data(symbol)
        return {
            "market_data": comprehensive_data.get("market_data", {}),
            "price_data": comprehensive_data.get("price_data", {}),
            "technical_indicators": comprehensive_data.get("technical_indicators", {})
        }
    
    async def get_financial_data(self, symbol: str) -> Dict[str, Any]:
        """获取财务数据"""
        comprehensive_data = await self.adapter.get_comprehensive_data(symbol)
        return {
            "financial_data": comprehensive_data.get("financial_data", {}),
            "symbol": symbol,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_news_data(self, symbol: str) -> List[Dict[str, Any]]:
        """获取新闻数据"""
        comprehensive_data = await self.adapter.get_comprehensive_data(symbol)
        return comprehensive_data.get("news_data", [])
    
    async def get_sentiment_data(self, symbol: str) -> Dict[str, Any]:
        """获取情感数据"""
        comprehensive_data = await self.adapter.get_comprehensive_data(symbol)
        return comprehensive_data.get("sentiment_data", {})

    async def get_comprehensive_data(self, symbol: str) -> Dict[str, Any]:
        """获取综合数据 - TradingGraph期望的方法"""
        return await self.adapter.get_comprehensive_data(symbol)

    async def get_market_overview(self) -> Dict[str, Any]:
        """获取市场概览"""
        return {
            "market_status": "open",
            "market_trend": "stable",
            "major_indices": {
                "shanghai_composite": {"value": 3000.0, "change": 0.5},
                "shenzhen_component": {"value": 10000.0, "change": -0.2},
                "csi_300": {"value": 4000.0, "change": 0.1}
            },
            "trading_volume": 500000000000,
            "timestamp": datetime.now().isoformat()
        }

def create_data_interface(enhanced_app) -> TradingAgentsDataInterface:
    """
    创建适配的数据接口
    
    Args:
        enhanced_app: EnhancedTradingAgentsApp实例
        
    Returns:
        TradingAgentsDataInterface实例
    """
    return TradingAgentsDataInterface(enhanced_app)
