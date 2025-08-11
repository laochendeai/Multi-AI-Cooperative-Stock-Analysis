"""
安全管理器 - 处理API密钥和安全相关功能
"""

import os
import logging
from typing import Dict, Any, Optional
import hashlib
import time

logger = logging.getLogger(__name__)

class SecurityManager:
    """安全管理器"""
    
    def __init__(self):
        self.api_keys = {}
        self.rate_limits = {}
        self.last_requests = {}
        
    def set_api_key(self, provider: str, api_key: str):
        """设置API密钥"""
        try:
            # 简单的密钥验证
            if not api_key or len(api_key) < 10:
                logger.warning(f"API密钥格式可能不正确: {provider}")
            
            self.api_keys[provider] = api_key
            logger.info(f"已设置 {provider} API密钥")
            
        except Exception as e:
            logger.error(f"设置API密钥失败: {e}")
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """获取API密钥"""
        return self.api_keys.get(provider)
    
    def check_rate_limit(self, provider: str, limit_per_minute: int = 60) -> bool:
        """检查速率限制"""
        try:
            current_time = time.time()
            
            if provider not in self.last_requests:
                self.last_requests[provider] = []
            
            # 清理超过1分钟的请求记录
            self.last_requests[provider] = [
                req_time for req_time in self.last_requests[provider]
                if current_time - req_time < 60
            ]
            
            # 检查是否超过限制
            if len(self.last_requests[provider]) >= limit_per_minute:
                logger.warning(f"速率限制: {provider} 超过 {limit_per_minute}/分钟")
                return False
            
            # 记录当前请求
            self.last_requests[provider].append(current_time)
            return True
            
        except Exception as e:
            logger.error(f"速率限制检查失败: {e}")
            return True  # 出错时允许请求
    
    def validate_input(self, input_data: Any) -> bool:
        """验证输入数据"""
        try:
            # 基本的输入验证
            if isinstance(input_data, str):
                # 检查长度
                if len(input_data) > 10000:
                    logger.warning("输入数据过长")
                    return False
                
                # 检查恶意内容
                dangerous_patterns = ['<script>', 'javascript:', 'eval(', 'exec(']
                for pattern in dangerous_patterns:
                    if pattern.lower() in input_data.lower():
                        logger.warning(f"检测到潜在恶意内容: {pattern}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"输入验证失败: {e}")
            return False
    
    def hash_sensitive_data(self, data: str) -> str:
        """对敏感数据进行哈希处理"""
        try:
            return hashlib.sha256(data.encode()).hexdigest()
        except Exception as e:
            logger.error(f"数据哈希失败: {e}")
            return ""
    
    def load_env_keys(self):
        """从环境变量加载API密钥"""
        try:
            # 常见的API密钥环境变量
            env_keys = {
                "deepseek": "DEEPSEEK_API_KEY",
                "openai": "OPENAI_API_KEY", 
                "google": "GOOGLE_API_KEY",
                "moonshot": "MOONSHOT_API_KEY"
            }
            
            for provider, env_var in env_keys.items():
                api_key = os.getenv(env_var)
                if api_key:
                    self.set_api_key(provider, api_key)
                    logger.info(f"从环境变量加载 {provider} API密钥")
            
        except Exception as e:
            logger.error(f"加载环境变量失败: {e}")
    
    def get_security_status(self) -> Dict[str, Any]:
        """获取安全状态"""
        return {
            "api_keys_configured": len(self.api_keys),
            "providers": list(self.api_keys.keys()),
            "rate_limits_active": len(self.rate_limits),
            "total_requests": sum(len(reqs) for reqs in self.last_requests.values())
        }
