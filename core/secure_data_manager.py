import asyncio
import logging
import os
import time
from typing import Dict, Any, List, Optional
import aiohttp

logger = logging.getLogger(__name__)

class DataSourceAuthManager:
    def __init__(self):
        self.auth_slots = {
            'akshare': "<AUTH_SLOT_F>",
            'news_api': "<AUTH_SLOT_G>", 
            'finnhub': "<AUTH_SLOT_H>",
            'alpha_vantage': "<AUTH_SLOT_I>"
        }
        self.clients = {}
        self.fallback_chains = {
            'akshare': ['finnhub', 'alpha_vantage'],
            'news_api': ['finnhub']
        }
    
    async def get_authenticated_client(self, source_id: str):
        """获取认证后的数据源客户端"""
        if source_id not in self.clients:
            auth_slot = self.auth_slots.get(source_id)
            if not auth_slot:
                raise ValueError(f"Unknown data source: {source_id}")
            
            # 从环境变量加载认证信息
            auth_key = os.getenv(f"{source_id.upper()}_API_KEY", "")
            
            self.clients[source_id] = DataSourceClient(
                source_id=source_id,
                auth_key=auth_key
            )
        
        return self.clients[source_id]
    
    async def get_data_with_fallback(self, source_id: str, request_params: Dict) -> Dict:
        """带降级的数据获取"""
        logger.info(f"Fetching data from {source_id} with params: {request_params}")

        try:
            client = await self.get_authenticated_client(source_id)
            result = await client.fetch_data(request_params)
            logger.info(f"Successfully fetched data from {source_id}")
            return result
        except Exception as e:
            logger.warning(f"Failed to fetch data from {source_id}: {e}")

            # 尝试降级数据源
            fallback_sources = self.fallback_chains.get(source_id, [])
            for fallback_source in fallback_sources:
                try:
                    logger.info(f"Trying fallback source: {fallback_source}")
                    fallback_client = await self.get_authenticated_client(fallback_source)
                    result = await fallback_client.fetch_data(request_params)
                    result['fallback_used'] = fallback_source
                    logger.info(f"Successfully fetched data from fallback source: {fallback_source}")
                    return result
                except Exception as fallback_error:
                    logger.warning(f"Fallback source {fallback_source} also failed: {fallback_error}")
                    continue

            # 所有数据源都失败，返回缓存或默认数据
            logger.error(f"All data sources failed for {source_id}")
            return {
                'status': 'fallback',
                'data': {},
                'error': str(e),
                'timestamp': time.time()
            }

class DataSourceClient:
    def __init__(self, source_id: str, auth_key: str):
        self.source_id = source_id
        self.auth_key = auth_key
        self.session = None
    
    async def fetch_data(self, params: Dict) -> Dict:
        """获取数据"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            if self.source_id == 'akshare':
                return await self._fetch_akshare_data(params)
            elif self.source_id == 'finnhub':
                return await self._fetch_finnhub_data(params)
            else:
                return {'status': 'error', 'error': f'Unsupported source: {self.source_id}'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    async def _fetch_akshare_data(self, params: Dict) -> Dict:
        """获取akshare数据"""
        # 模拟akshare数据获取
        await asyncio.sleep(0.1)  # 模拟网络延迟
        return {
            'status': 'success',
            'source': 'akshare',
            'data': {
                'symbol': params.get('symbol', 'UNKNOWN'),
                'price': 100.0,
                'change': 1.5
            },
            'timestamp': time.time()
        }
    
    async def _fetch_finnhub_data(self, params: Dict) -> Dict:
        """获取finnhub数据"""
        await asyncio.sleep(0.1)
        return {
            'status': 'success', 
            'source': 'finnhub',
            'data': {
                'symbol': params.get('symbol', 'UNKNOWN'),
                'price': 99.8,
                'change': 1.2
            },
            'timestamp': time.time()
        }
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()