#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromaDB向量记忆系统 - 修复版
"""

import asyncio
import logging
import os
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ChromaDBMemoryManager:
    """ChromaDB向量记忆管理器 - 修复版"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化ChromaDB记忆管理器

        Args:
            config: 配置字典
        """
        self.config = config or self._get_default_config()

        # 确保配置完整性
        default_config = self._get_default_config()
        for key, value in default_config.items():
            if key not in self.config:
                self.config[key] = value

        self.client = None
        self.collection = None
        self.embedding_model = None
        self.initialized = False
        self.use_simple_fallback = False

        # 简单存储作为备用
        self.simple_memories = []
        
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "persist_directory": "data/memory/chromadb",
            "collection_name": "agent_memories",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "max_memories": 1000,
            "similarity_threshold": 0.7,
            "enable_chromadb": True
        }
    
    async def initialize(self) -> bool:
        """
        初始化ChromaDB记忆系统
        
        Returns:
            是否初始化成功
        """
        try:
            logger.info("🧠 初始化ChromaDB向量记忆系统...")
            logger.info(f"📋 配置信息: {list(self.config.keys())}")
            logger.info(f"📁 持久化目录: {self.config.get('persist_directory', 'NOT_SET')}")

            # 检查ChromaDB是否可用
            if not self._check_chromadb_available():
                logger.error("ChromaDB不可用！必须修复依赖问题")
                raise Exception("ChromaDB依赖缺失，请安装: pip install chromadb sentence-transformers")
            
            # 初始化ChromaDB客户端
            await self._initialize_chromadb()
            
            # 初始化嵌入模型
            await self._initialize_embedding_model()
            
            self.initialized = True
            logger.info("✅ ChromaDB向量记忆系统初始化成功")
            return True

        except Exception as e:
            logger.error(f"ChromaDB初始化失败: {e}")
            logger.error("❌ 禁用简单存储回退，必须修复ChromaDB问题")
            # 打印详细错误信息
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
            raise Exception(f"ChromaDB初始化失败，必须修复: {e}")
    
    def _check_chromadb_available(self) -> bool:
        """检查ChromaDB是否可用"""
        try:
            import chromadb
            import sentence_transformers
            return True
        except ImportError as e:
            logger.warning(f"ChromaDB依赖不可用: {e}")
            return False
    
    async def _initialize_chromadb(self):
        """初始化ChromaDB客户端"""
        try:
            import chromadb
            from chromadb.config import Settings

            # 确保目录存在
            persist_dir = self.config.get("persist_directory", "data/memory/chromadb")
            os.makedirs(persist_dir, exist_ok=True)
            
            # 创建客户端
            self.client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # 获取或创建集合
            self.collection = self.client.get_or_create_collection(
                name=self.config["collection_name"],
                metadata={"description": "TradingAgents智能体记忆"}
            )
            
            logger.info(f"ChromaDB客户端初始化成功，集合: {self.config['collection_name']}")
            
        except Exception as e:
            logger.error(f"ChromaDB客户端初始化失败: {e}")
            raise
    
    async def _initialize_embedding_model(self):
        """初始化嵌入模型"""
        try:
            from sentence_transformers import SentenceTransformer
            
            model_name = self.config["embedding_model"]
            logger.info(f"加载嵌入模型: {model_name}")
            
            # 使用更稳定的模型加载方式
            self.embedding_model = SentenceTransformer(
                model_name,
                cache_folder="data/models",  # 指定缓存目录
                device="cpu"  # 强制使用CPU，避免GPU问题
            )
            
            logger.info("嵌入模型加载成功")
            
        except Exception as e:
            logger.error(f"嵌入模型加载失败: {e}")
            # 尝试使用更小的模型
            try:
                logger.info("尝试使用备用模型...")
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer(
                    "paraphrase-MiniLM-L6-v2",
                    cache_folder="data/models",
                    device="cpu"
                )
                logger.info("备用嵌入模型加载成功")
            except Exception as e2:
                logger.error(f"备用模型也失败: {e2}")
                raise
    
    async def add_memory(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """
        添加记忆
        
        Args:
            content: 记忆内容
            metadata: 元数据
            
        Returns:
            记忆ID
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            memory_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # 准备元数据
            full_metadata = {
                "timestamp": timestamp,
                "content_length": len(content),
                **(metadata or {})
            }
            
            if self.use_simple_fallback or not self.collection:
                # 使用简单存储
                memory = {
                    "id": memory_id,
                    "content": content,
                    "metadata": full_metadata
                }
                self.simple_memories.append(memory)
                
                # 限制记忆数量
                max_memories = self.config.get("max_memories", 1000)
                if len(self.simple_memories) > max_memories:
                    self.simple_memories = self.simple_memories[-max_memories:]
                
                logger.debug(f"添加简单记忆: {memory_id}")
                
            else:
                # 使用ChromaDB
                embedding = self.embedding_model.encode([content])[0].tolist()
                
                self.collection.add(
                    ids=[memory_id],
                    embeddings=[embedding],
                    documents=[content],
                    metadatas=[full_metadata]
                )
                
                logger.debug(f"添加ChromaDB记忆: {memory_id}")
            
            return memory_id
            
        except Exception as e:
            logger.error(f"添加记忆失败: {e}")
            return ""
    
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
            if not self.initialized:
                await self.initialize()
            
            if self.use_simple_fallback or not self.collection:
                # 使用简单搜索
                results = []
                for memory in self.simple_memories:
                    # 简单的关键词匹配
                    if query.lower() in memory["content"].lower():
                        if agent_id is None or memory["metadata"].get("agent_id") == agent_id:
                            results.append({
                                "content": memory["content"],
                                "metadata": memory["metadata"],
                                "relevance_score": 0.8  # 固定相关性分数
                            })
                
                return results[:limit]
                
            else:
                # 使用ChromaDB向量搜索
                query_embedding = self.embedding_model.encode([query])[0].tolist()
                
                # 构建过滤条件
                where_filter = {}
                if agent_id:
                    where_filter["agent_id"] = agent_id
                
                search_results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=limit,
                    where=where_filter if where_filter else None
                )
                
                results = []
                if search_results["documents"]:
                    for i, doc in enumerate(search_results["documents"][0]):
                        metadata = search_results["metadatas"][0][i] if search_results["metadatas"] else {}
                        distance = search_results["distances"][0][i] if search_results["distances"] else 0.5
                        
                        results.append({
                            "content": doc,
                            "metadata": metadata,
                            "relevance_score": 1.0 - distance  # 转换为相关性分数
                        })
                
                return results
                
        except Exception as e:
            logger.error(f"搜索记忆失败: {e}")
            return []
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        try:
            if self.use_simple_fallback:
                return {
                    "total_memories": len(self.simple_memories),
                    "storage_type": "simple",
                    "initialized": self.initialized
                }
            else:
                count = self.collection.count() if self.collection else 0
                return {
                    "total_memories": count,
                    "storage_type": "chromadb",
                    "initialized": self.initialized,
                    "collection_name": self.config["collection_name"]
                }
        except Exception as e:
            logger.error(f"获取记忆统计失败: {e}")
            return {"error": str(e)}
    
    async def clear_memories(self, agent_id: str = None):
        """清理记忆"""
        try:
            if self.use_simple_fallback:
                if agent_id:
                    self.simple_memories = [
                        m for m in self.simple_memories 
                        if m["metadata"].get("agent_id") != agent_id
                    ]
                else:
                    self.simple_memories.clear()
            else:
                if self.collection:
                    if agent_id:
                        # 删除特定智能体的记忆
                        results = self.collection.get(where={"agent_id": agent_id})
                        if results["ids"]:
                            self.collection.delete(ids=results["ids"])
                    else:
                        # 清空所有记忆
                        self.collection.delete()
            
            logger.info(f"清理记忆完成: {agent_id or '全部'}")
            
        except Exception as e:
            logger.error(f"清理记忆失败: {e}")

def create_chromadb_memory_manager(config: Dict[str, Any] = None) -> ChromaDBMemoryManager:
    """
    创建ChromaDB记忆管理器
    
    Args:
        config: 配置字典
        
    Returns:
        ChromaDBMemoryManager实例
    """
    return ChromaDBMemoryManager(config)
