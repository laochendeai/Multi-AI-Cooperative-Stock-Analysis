"""
缓存管理器 - 数据缓存和管理
"""

import logging
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import pickle

logger = logging.getLogger(__name__)

class CacheManager:
    """数据缓存管理器"""
    
    def __init__(self, cache_dir: str = "./data/cache"):
        self.cache_dir = cache_dir
        self.memory_cache = {}
        self.default_ttl = 300  # 5分钟默认TTL
        
        # 创建缓存目录
        os.makedirs(cache_dir, exist_ok=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取缓存数据"""
        try:
            # 首先检查内存缓存
            if key in self.memory_cache:
                cache_item = self.memory_cache[key]
                if self._is_valid(cache_item):
                    return cache_item["data"]
                else:
                    del self.memory_cache[key]
            
            # 检查磁盘缓存
            cache_file = self._get_cache_file(key)
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'rb') as f:
                        cache_item = pickle.load(f)
                    
                    if self._is_valid(cache_item):
                        # 加载到内存缓存
                        self.memory_cache[key] = cache_item
                        return cache_item["data"]
                    else:
                        # 删除过期的磁盘缓存
                        os.remove(cache_file)
                except Exception as e:
                    logger.error(f"读取磁盘缓存失败: {e}")
                    if os.path.exists(cache_file):
                        os.remove(cache_file)
            
            return default
            
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return default
    
    def set(self, key: str, data: Any, ttl: int = None) -> bool:
        """设置缓存数据"""
        try:
            ttl = ttl or self.default_ttl
            expire_time = datetime.now() + timedelta(seconds=ttl)
            
            cache_item = {
                "data": data,
                "expire_time": expire_time,
                "created_time": datetime.now()
            }
            
            # 保存到内存缓存
            self.memory_cache[key] = cache_item
            
            # 保存到磁盘缓存
            cache_file = self._get_cache_file(key)
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(cache_item, f)
            except Exception as e:
                logger.error(f"保存磁盘缓存失败: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存数据"""
        try:
            # 删除内存缓存
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            # 删除磁盘缓存
            cache_file = self._get_cache_file(key)
            if os.path.exists(cache_file):
                os.remove(cache_file)
            
            return True
            
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            return False
    
    def clear(self) -> bool:
        """清空所有缓存"""
        try:
            # 清空内存缓存
            self.memory_cache.clear()
            
            # 清空磁盘缓存
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    file_path = os.path.join(self.cache_dir, filename)
                    os.remove(file_path)
            
            return True
            
        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
            return False
    
    def cleanup_expired(self) -> int:
        """清理过期缓存"""
        try:
            cleaned_count = 0
            
            # 清理内存缓存
            expired_keys = []
            for key, cache_item in self.memory_cache.items():
                if not self._is_valid(cache_item):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.memory_cache[key]
                cleaned_count += 1
            
            # 清理磁盘缓存
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    file_path = os.path.join(self.cache_dir, filename)
                    try:
                        with open(file_path, 'rb') as f:
                            cache_item = pickle.load(f)
                        
                        if not self._is_valid(cache_item):
                            os.remove(file_path)
                            cleaned_count += 1
                    except Exception:
                        # 如果文件损坏，直接删除
                        os.remove(file_path)
                        cleaned_count += 1
            
            logger.info(f"清理了 {cleaned_count} 个过期缓存项")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"清理过期缓存失败: {e}")
            return 0
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        try:
            memory_count = len(self.memory_cache)
            
            disk_count = 0
            disk_size = 0
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    disk_count += 1
                    file_path = os.path.join(self.cache_dir, filename)
                    disk_size += os.path.getsize(file_path)
            
            return {
                "memory_cache_count": memory_count,
                "disk_cache_count": disk_count,
                "disk_cache_size_mb": round(disk_size / (1024 * 1024), 2),
                "cache_directory": self.cache_dir,
                "default_ttl": self.default_ttl
            }
            
        except Exception as e:
            logger.error(f"获取缓存信息失败: {e}")
            return {"error": str(e)}
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在且有效"""
        try:
            # 检查内存缓存
            if key in self.memory_cache:
                return self._is_valid(self.memory_cache[key])
            
            # 检查磁盘缓存
            cache_file = self._get_cache_file(key)
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'rb') as f:
                        cache_item = pickle.load(f)
                    return self._is_valid(cache_item)
                except Exception:
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"检查缓存存在性失败: {e}")
            return False
    
    def get_or_set(self, key: str, callback, ttl: int = None) -> Any:
        """获取缓存，如果不存在则通过回调函数设置"""
        try:
            # 尝试获取缓存
            cached_data = self.get(key)
            if cached_data is not None:
                return cached_data
            
            # 缓存不存在，通过回调函数获取数据
            data = callback()
            
            # 设置缓存
            self.set(key, data, ttl)
            
            return data
            
        except Exception as e:
            logger.error(f"获取或设置缓存失败: {e}")
            # 如果缓存操作失败，直接调用回调函数
            try:
                return callback()
            except Exception as callback_error:
                logger.error(f"回调函数执行失败: {callback_error}")
                return None
    
    def _is_valid(self, cache_item: Dict[str, Any]) -> bool:
        """检查缓存项是否有效"""
        try:
            expire_time = cache_item.get("expire_time")
            if expire_time is None:
                return False
            
            return datetime.now() < expire_time
            
        except Exception:
            return False
    
    def _get_cache_file(self, key: str) -> str:
        """获取缓存文件路径"""
        # 将key转换为安全的文件名
        safe_key = key.replace('/', '_').replace('\\', '_').replace(':', '_')
        return os.path.join(self.cache_dir, f"{safe_key}.cache")
    
    def set_default_ttl(self, ttl: int):
        """设置默认TTL"""
        self.default_ttl = ttl
    
    def get_keys(self, pattern: str = None) -> list:
        """获取所有缓存键"""
        try:
            keys = []
            
            # 内存缓存键
            for key in self.memory_cache.keys():
                if pattern is None or pattern in key:
                    keys.append(key)
            
            # 磁盘缓存键
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    key = filename[:-6]  # 移除.cache后缀
                    key = key.replace('_', '/')  # 恢复原始key格式
                    if pattern is None or pattern in key:
                        if key not in keys:  # 避免重复
                            keys.append(key)
            
            return keys
            
        except Exception as e:
            logger.error(f"获取缓存键失败: {e}")
            return []
