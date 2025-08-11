#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM适配器 - 将app_enhanced.py的LLM调用方式适配到tradingagents架构
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMAdapter:
    """LLM适配器 - 桥接现有LLM调用和tradingagents架构"""
    
    def __init__(self, enhanced_app):
        """
        初始化适配器
        
        Args:
            enhanced_app: EnhancedTradingAgentsApp实例
        """
        self.enhanced_app = enhanced_app
        self.llm_config = enhanced_app.llm_config
        self.agent_model_config = enhanced_app.agent_model_config
        self.custom_llm_providers = enhanced_app.custom_llm_providers
        
    async def invoke(self, messages: List[Dict[str, str]], agent_id: str = "default") -> str:
        """
        统一的LLM调用接口，兼容tradingagents架构

        Args:
            messages: 消息列表，格式为[{"role": "user", "content": "..."}]
            agent_id: 智能体ID，用于获取对应的模型配置

        Returns:
            LLM响应内容
        """
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                # 获取智能体对应的模型配置
                model_config = self.agent_model_config.get(agent_id, "deepseek:deepseek-chat")
                provider, model = model_config.split(":", 1)

                # 提取用户消息内容
                prompt = ""
                for message in messages:
                    if message.get("role") == "user":
                        prompt = message.get("content", "")
                        break

                if not prompt:
                    # 如果没有用户消息，合并所有消息
                    prompt = "\n".join([msg.get("content", "") for msg in messages])

                # 调用现有的LLM方法
                response = await self.enhanced_app._call_llm(provider, model, prompt, agent_id)

                if response and response.strip():
                    return response
                else:
                    raise Exception("Empty response from LLM")

            except Exception as e:
                logger.warning(f"LLM调用失败 (尝试 {attempt + 1}/{max_retries}): {e}")

                if attempt < max_retries - 1:
                    # 尝试使用备用提供商
                    if "deepseek" in model_config:
                        backup_config = "阿里百炼:qwen-turbo"
                    else:
                        backup_config = "deepseek:deepseek-chat"

                    try:
                        backup_provider, backup_model = backup_config.split(":", 1)
                        response = await self.enhanced_app._call_llm(backup_provider, backup_model, prompt, agent_id)
                        if response and response.strip():
                            logger.info(f"使用备用LLM成功: {backup_config}")
                            return response
                    except Exception as backup_e:
                        logger.warning(f"备用LLM也失败: {backup_e}")

                    # 等待后重试
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    # 最后一次尝试失败，返回默认响应
                    logger.error(f"所有LLM调用尝试失败: {e}")
                    return f"由于API限制，{agent_id}暂时无法提供分析。请稍后重试。"
    
    async def get_llm_response(self, prompt: str, context: Dict[str, Any], agent_id: str = "default") -> str:
        """
        获取LLM响应的便捷方法
        
        Args:
            prompt: 提示词
            context: 上下文信息
            agent_id: 智能体ID
            
        Returns:
            LLM响应
        """
        messages = [{"role": "user", "content": prompt}]
        
        # 如果上下文中有系统消息，添加到消息列表
        if "system_prompt" in context:
            messages.insert(0, {"role": "system", "content": context["system_prompt"]})
        
        return await self.invoke(messages, agent_id)
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """获取可用的模型列表"""
        return self.enhanced_app.get_available_models()

    def get_provider_models(self, provider: str) -> List[str]:
        """获取指定提供商的可用模型列表"""
        return self.enhanced_app.get_provider_models(provider)

    def validate_model_compatibility(self, agent_id: str, provider: str, model: str) -> Dict[str, Any]:
        """验证模型与智能体的兼容性"""
        return self.enhanced_app.validate_model_compatibility(agent_id, provider, model)
    
    def get_provider_status(self, provider: str) -> Dict[str, Any]:
        """获取提供商状态"""
        return {
            "configured": provider in self.llm_config,
            "api_key_set": bool(self.llm_config.get(provider)),
            "models": self.enhanced_app.get_available_models().get(provider, [])
        }

class TradingAgentsLLMClient:
    """
    TradingAgents专用LLM客户端
    实现tradingagents架构期望的接口
    """
    
    def __init__(self, enhanced_app):
        self.adapter = LLMAdapter(enhanced_app)
        self.enhanced_app = enhanced_app
    
    async def invoke(self, messages, **kwargs) -> "LLMResponse":
        """
        调用LLM并返回响应对象

        Args:
            messages: 消息列表或字符串
            **kwargs: 额外参数

        Returns:
            LLMResponse对象
        """
        # 处理不同的输入格式
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        elif isinstance(messages, list) and len(messages) > 0:
            # 如果是字符串列表，转换为消息格式
            if isinstance(messages[0], str):
                messages = [{"role": "user", "content": msg} for msg in messages]

        agent_id = kwargs.get("agent_id", "default")
        response_text = await self.adapter.invoke(messages, agent_id)

        return LLMResponse(response_text)

    async def process_async(self, messages, context=None):
        """
        BaseAgent期望的process_async方法

        Args:
            messages: 消息列表
            context: 上下文信息

        Returns:
            包含content字段的字典
        """
        agent_id = context.get("agent_id", "default") if context else "default"
        response_text = await self.adapter.invoke(messages, agent_id)

        return {
            "content": response_text,
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id
        }
    
    async def bind_tools(self, tools: List[Any]):
        """
        绑定工具（暂时不实现，保持接口兼容）
        """
        return self
    
    def with_config(self, config: Dict[str, Any]):
        """
        配置LLM客户端（保持接口兼容）
        """
        return self

class LLMResponse:
    """LLM响应对象，兼容tradingagents架构"""
    
    def __init__(self, content: str):
        self.content = content
        self.timestamp = datetime.now().isoformat()
    
    def __str__(self):
        return self.content
    
    def __repr__(self):
        return f"LLMResponse(content='{self.content[:50]}...')"

class MemoryAdapter:
    """记忆系统适配器"""
    
    def __init__(self, enhanced_app):
        self.enhanced_app = enhanced_app
        self.db_path = enhanced_app.db_path
    
    async def initialize(self):
        """初始化记忆系统"""
        # 使用现有的数据库初始化
        logger.info("记忆系统适配器初始化完成")
    
    async def search_memories(self, query: str, agent_id: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        搜索相关记忆
        
        Args:
            query: 查询字符串
            agent_id: 智能体ID
            limit: 返回数量限制
            
        Returns:
            相关记忆列表
        """
        try:
            # 简化的记忆搜索实现
            # 在完整版本中，这里会使用ChromaDB进行向量搜索
            memories = []
            
            # 从数据库中获取历史分析记录
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 查询相关的历史分析
            cursor.execute("""
                SELECT symbol, analysis_result, timestamp 
                FROM analysis_history 
                WHERE analysis_result LIKE ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (f"%{query}%", limit))
            
            rows = cursor.fetchall()
            for row in rows:
                memories.append({
                    "content": f"历史分析: {row[0]} - {row[1][:100]}...",
                    "timestamp": row[2],
                    "relevance_score": 0.8,
                    "agent_id": agent_id
                })
            
            conn.close()
            return memories
            
        except Exception as e:
            logger.error(f"记忆搜索失败: {e}")
            return []
    
    async def save_memory(self, content: str, metadata: Dict[str, Any] = None):
        """
        保存记忆
        
        Args:
            content: 记忆内容
            metadata: 元数据
        """
        try:
            # 简化的记忆保存实现
            logger.info(f"保存记忆: {content[:50]}...")
            
        except Exception as e:
            logger.error(f"记忆保存失败: {e}")

def create_llm_client(enhanced_app) -> TradingAgentsLLMClient:
    """
    创建适配的LLM客户端
    
    Args:
        enhanced_app: EnhancedTradingAgentsApp实例
        
    Returns:
        TradingAgentsLLMClient实例
    """
    return TradingAgentsLLMClient(enhanced_app)

def create_memory_manager(enhanced_app) -> MemoryAdapter:
    """
    创建适配的记忆管理器
    
    Args:
        enhanced_app: EnhancedTradingAgentsApp实例
        
    Returns:
        MemoryAdapter实例
    """
    return MemoryAdapter(enhanced_app)
