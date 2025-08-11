"""
记忆管理系统 - 基于ChromaDB的向量数据库 (修复版)
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

# 优先使用修复版ChromaDB记忆管理器
try:
    from core.chromadb_memory import create_chromadb_memory_manager
    CHROMADB_MEMORY_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ 使用修复版ChromaDB记忆系统")
except ImportError:
    CHROMADB_MEMORY_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ 修复版ChromaDB不可用，使用原版")

# 备用：原版ChromaDB
try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None
    SentenceTransformer = None

try:
    from ...config.default_config import MEMORY_CONFIG
except ImportError:
    # 使用适配器配置
    from core.config_adapter import MEMORY_CONFIG

logger = logging.getLogger(__name__)

class MemoryManager:
    """智能体记忆管理器 - 修复版"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or MEMORY_CONFIG
        self.initialized = False

        # 优先使用修复版ChromaDB记忆管理器
        if CHROMADB_MEMORY_AVAILABLE:
            logger.info("🧠 使用修复版ChromaDB记忆管理器")
            self.chromadb_manager = create_chromadb_memory_manager(self.config)
            self.use_chromadb_manager = True
        else:
            logger.warning("修复版ChromaDB不可用，使用原版实现")
            self.use_chromadb_manager = False
            self.client = None
            self.collection = None
            self.embedding_model = None
            self.memories = []  # 简单内存存储
    
    async def initialize(self):
        """初始化记忆系统"""
        try:
            if self.use_chromadb_manager:
                # 使用修复版ChromaDB记忆管理器 - 强制成功
                logger.info("🔧 强制使用ChromaDB，禁用简单存储回退")
                success = await self.chromadb_manager.initialize()
                if success:
                    self.initialized = True
                    logger.info("✅ 修复版ChromaDB记忆系统初始化成功")
                    return
                else:
                    logger.error("❌ 修复版ChromaDB初始化失败，系统停止")
                    raise Exception("ChromaDB初始化失败，必须修复配置问题")

            # 使用原版实现
            if CHROMADB_AVAILABLE:
                await self._initialize_chromadb()
            else:
                await self._initialize_simple_storage()

            self.initialized = True
            logger.info("记忆系统初始化成功")

        except Exception as e:
            logger.error(f"记忆系统初始化失败: {e}")
            logger.error("❌ 禁用简单存储回退，必须修复ChromaDB")
            # 打印详细错误信息
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
            raise Exception(f"记忆系统初始化失败，必须修复ChromaDB: {e}")
    
    async def _initialize_chromadb(self):
        """初始化ChromaDB"""
        persist_dir = self.config["chromadb"]["persist_directory"]
        os.makedirs(persist_dir, exist_ok=True)
        
        # 创建ChromaDB客户端
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 获取或创建集合
        collection_name = self.config["chromadb"]["collection_name"]
        try:
            self.collection = self.client.get_collection(collection_name)
        except:
            self.collection = self.client.create_collection(collection_name)
        
        # 初始化嵌入模型
        try:
            model_name = self.config["chromadb"]["embedding_model"]
            self.embedding_model = SentenceTransformer(model_name)
        except Exception as e:
            logger.warning(f"嵌入模型初始化失败: {e}")
            logger.info("将使用简单存储模式")
            self.embedding_model = None
            # 降级到简单存储
            await self._initialize_simple_storage()
            return
        
        logger.info(f"ChromaDB初始化完成，集合: {collection_name}")
    
    async def _initialize_simple_storage(self):
        """初始化简单存储"""
        self.memories = []
        logger.info("使用简单内存存储作为记忆系统")
    
    async def add_memory(self, 
                        content: str, 
                        metadata: Dict[str, Any] = None,
                        memory_id: str = None) -> str:
        """
        添加记忆
        
        Args:
            content: 记忆内容
            metadata: 元数据
            memory_id: 记忆ID（可选）
            
        Returns:
            记忆ID
        """
        if not self.initialized:
            await self.initialize()
        
        memory_id = memory_id or f"memory_{datetime.now().timestamp()}"
        metadata = metadata or {}
        metadata["timestamp"] = datetime.now().isoformat()
        
        try:
            if self.use_chromadb_manager and self.chromadb_manager:
                # 使用修复版ChromaDB记忆管理器
                return await self.chromadb_manager.add_memory(content, metadata)

            elif CHROMADB_AVAILABLE and self.collection and self.embedding_model:
                # 使用原版ChromaDB存储
                embedding = self.embedding_model.encode([content])[0].tolist()

                self.collection.add(
                    embeddings=[embedding],
                    documents=[content],
                    metadatas=[metadata],
                    ids=[memory_id]
                )
            else:
                # 使用简单存储
                self.memories.append({
                    "id": memory_id,
                    "content": content,
                    "metadata": metadata
                })

                # 限制记忆数量
                max_memories = self.config.get("max_memories", 1000)
                if len(self.memories) > max_memories:
                    self.memories = self.memories[-max_memories:]

            logger.debug(f"添加记忆: {memory_id}")
            return memory_id

        except Exception as e:
            logger.error(f"添加记忆失败: {e}")
            return ""
    
    async def search_memories(self, 
                             query: str, 
                             agent_id: str = None,
                             limit: int = 5,
                             similarity_threshold: float = None) -> List[Dict[str, Any]]:
        """
        搜索相关记忆
        
        Args:
            query: 查询字符串
            agent_id: 智能体ID（可选，用于过滤）
            limit: 返回结果数量限制
            similarity_threshold: 相似度阈值
            
        Returns:
            相关记忆列表
        """
        if not self.initialized:
            await self.initialize()
        
        similarity_threshold = similarity_threshold or self.config.get("similarity_threshold", 0.7)
        
        try:
            if self.use_chromadb_manager and self.chromadb_manager:
                # 使用修复版ChromaDB记忆管理器
                return await self.chromadb_manager.search_memories(query, agent_id, limit)

            elif CHROMADB_AVAILABLE and self.collection and self.embedding_model:
                # 使用原版ChromaDB搜索
                query_embedding = self.embedding_model.encode([query])[0].tolist()
                
                # 构建过滤条件
                where_filter = {}
                if agent_id:
                    where_filter["agent_id"] = agent_id
                
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=limit,
                    where=where_filter if where_filter else None
                )
                
                memories = []
                for i, (doc, metadata, distance) in enumerate(zip(
                    results["documents"][0],
                    results["metadatas"][0], 
                    results["distances"][0]
                )):
                    similarity = 1 - distance  # 转换为相似度
                    if similarity >= similarity_threshold:
                        memories.append({
                            "content": doc,
                            "metadata": metadata,
                            "similarity": similarity
                        })
                
                return memories
            
            else:
                # 使用简单搜索
                memories = []
                query_lower = query.lower()
                
                for memory in self.memories:
                    # 简单的关键词匹配
                    content_lower = memory["content"].lower()
                    if query_lower in content_lower:
                        # 计算简单相似度
                        similarity = len(query_lower) / len(content_lower)
                        
                        # 检查智能体过滤
                        if agent_id and memory["metadata"].get("agent_id") != agent_id:
                            continue
                        
                        if similarity >= similarity_threshold:
                            memories.append({
                                "content": memory["content"],
                                "metadata": memory["metadata"],
                                "similarity": similarity
                            })
                
                # 按相似度排序并限制数量
                memories.sort(key=lambda x: x["similarity"], reverse=True)
                return memories[:limit]
                
        except Exception as e:
            logger.error(f"搜索记忆失败: {e}")
            return []
    
    async def get_agent_memories(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取特定智能体的记忆"""
        return await self.search_memories("", agent_id=agent_id, limit=limit, similarity_threshold=0.0)
    
    async def clear_memories(self, agent_id: str = None):
        """清除记忆"""
        try:
            if CHROMADB_AVAILABLE and self.collection:
                if agent_id:
                    # 删除特定智能体的记忆
                    results = self.collection.get(where={"agent_id": agent_id})
                    if results["ids"]:
                        self.collection.delete(ids=results["ids"])
                else:
                    # 清除所有记忆
                    self.client.delete_collection(self.config["chromadb"]["collection_name"])
                    self.collection = self.client.create_collection(
                        self.config["chromadb"]["collection_name"]
                    )
            else:
                if agent_id:
                    self.memories = [
                        m for m in self.memories 
                        if m["metadata"].get("agent_id") != agent_id
                    ]
                else:
                    self.memories = []
            
            logger.info(f"清除记忆完成: {agent_id or '全部'}")
            
        except Exception as e:
            logger.error(f"清除记忆失败: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取记忆系统状态"""
        status = {
            "initialized": self.initialized,
            "chromadb_available": CHROMADB_AVAILABLE,
            "config": self.config
        }
        
        try:
            if CHROMADB_AVAILABLE and self.collection:
                count = self.collection.count()
                status["memory_count"] = count
            else:
                status["memory_count"] = len(self.memories) if hasattr(self, 'memories') else 0
        except:
            status["memory_count"] = 0
        
        return status
