"""
基础智能体类 - 所有专业化智能体的基类
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..config.default_config import get_config
from ..agents.utils.memory import MemoryManager

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """基础智能体抽象类"""
    
    def __init__(self, 
                 agent_id: str,
                 agent_type: str,
                 llm_client=None,
                 memory_manager: Optional[MemoryManager] = None):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.llm_client = llm_client
        self.memory_manager = memory_manager
        self.config = get_config()
        self.agent_config = self._get_agent_config()
        self.conversation_history = []
        self.analysis_count = 0
        
        logger.info(f"初始化智能体: {self.agent_id} ({self.agent_type})")
    
    def _get_agent_config(self) -> Dict[str, Any]:
        """获取智能体特定配置"""
        config = self.config["agents"]
        
        # 根据智能体类型查找配置
        for category, agents in config.items():
            if isinstance(agents, dict):
                for agent_name, agent_config in agents.items():
                    if agent_name in self.agent_id.lower():
                        return agent_config
                # 如果是单个智能体配置
                if category in self.agent_id.lower():
                    return agents
        
        # 默认配置
        return {
            "llm_type": "quick_think",
            "system_prompt": f"你是{self.agent_type}智能体。",
            "tools": []
        }
    
    @abstractmethod
    async def analyze(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行分析任务的抽象方法
        
        Args:
            input_data: 输入数据
            context: 上下文信息
            
        Returns:
            分析结果字典
        """
        pass
    
    async def process_with_memory(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        带记忆系统的处理方法
        """
        try:
            # 检索相关记忆
            relevant_memories = []
            if self.memory_manager:
                query = self._extract_query_from_input(input_data)
                relevant_memories = await self.memory_manager.search_memories(
                    query, 
                    agent_id=self.agent_id,
                    limit=5
                )
            
            # 将记忆添加到上下文
            enhanced_context = {
                **context,
                "relevant_memories": relevant_memories,
                "agent_id": self.agent_id,
                "agent_type": self.agent_type
            }
            
            # 执行分析
            result = await self.analyze(input_data, enhanced_context)
            
            # 保存新的记忆
            if self.memory_manager and result.get("status") == "success":
                await self._save_analysis_memory(input_data, result)
            
            # 更新统计
            self.analysis_count += 1
            
            return result
            
        except Exception as e:
            logger.error(f"智能体 {self.agent_id} 处理失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_query_from_input(self, input_data: Dict[str, Any]) -> str:
        """从输入数据中提取查询字符串"""
        if isinstance(input_data, dict):
            return input_data.get("query", "") or input_data.get("symbol", "") or str(input_data)
        return str(input_data)
    
    async def _save_analysis_memory(self, input_data: Dict[str, Any], result: Dict[str, Any]):
        """保存分析记忆"""
        if not self.memory_manager:
            return
            
        memory_content = {
            "input": input_data,
            "output": result,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "timestamp": datetime.now().isoformat(),
            "analysis_type": result.get("analysis_type", "general")
        }
        
        await self.memory_manager.add_memory(
            content=str(memory_content),
            metadata={
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    async def get_llm_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """
        获取LLM响应的通用方法
        """
        if not self.llm_client:
            raise ValueError(f"智能体 {self.agent_id} 未配置LLM客户端")
        
        # 构建系统提示
        system_prompt = self.agent_config.get("system_prompt", "")
        
        # 添加上下文信息
        if context and context.get("relevant_memories"):
            memory_context = "\n".join([
                f"相关经验 {i+1}: {memory['content'][:200]}..." 
                for i, memory in enumerate(context["relevant_memories"][:3])
            ])
            system_prompt += f"\n\n相关历史经验:\n{memory_context}"
        
        # 调用LLM
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.llm_client.process_async(
                messages, 
                context or {}
            )
            return response.get("content", "")
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            return f"LLM调用失败: {str(e)}"
    
    def get_status(self) -> Dict[str, Any]:
        """获取智能体状态"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "analysis_count": self.analysis_count,
            "has_memory": self.memory_manager is not None,
            "has_llm": self.llm_client is not None,
            "config": self.agent_config
        }
