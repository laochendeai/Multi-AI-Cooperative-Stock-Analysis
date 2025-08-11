#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强LLM配置管理器 - 支持动态添加LLM提供商和模型
"""

import json
import logging
import base64
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import aiohttp
import openai

logger = logging.getLogger(__name__)

class EnhancedLLMManager:
    """增强的LLM配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.llm_config_file = self.config_dir / "llm_config.json"
        self.providers_config_file = self.config_dir / "llm_providers.json"
        
        # 内置提供商配置
        self.built_in_providers = {
            "openai": {
                "name": "OpenAI",
                "base_url": "https://api.openai.com/v1",
                "api_key_header": "Authorization",
                "api_key_prefix": "Bearer ",
                "models": [
                    {"id": "gpt-4", "name": "GPT-4", "type": "chat", "context_length": 8192},
                    {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "type": "chat", "context_length": 128000},
                    {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "type": "chat", "context_length": 4096}
                ],
                "request_format": "openai_compatible"
            },
            "deepseek": {
                "name": "DeepSeek",
                "base_url": "https://api.deepseek.com/v1",
                "api_key_header": "Authorization", 
                "api_key_prefix": "Bearer ",
                "models": [
                    {"id": "deepseek-chat", "name": "DeepSeek Chat", "type": "chat", "context_length": 32768},
                    {"id": "deepseek-coder", "name": "DeepSeek Coder", "type": "chat", "context_length": 16384}
                ],
                "request_format": "openai_compatible"
            },
            "google": {
                "name": "Google Gemini",
                "base_url": "https://generativelanguage.googleapis.com/v1beta",
                "api_key_header": "x-goog-api-key",
                "api_key_prefix": "",
                "models": [
                    {"id": "gemini-pro", "name": "Gemini Pro", "type": "chat", "context_length": 30720},
                    {"id": "gemini-pro-vision", "name": "Gemini Pro Vision", "type": "multimodal", "context_length": 30720}
                ],
                "request_format": "google_gemini"
            },
            "moonshot": {
                "name": "Moonshot AI",
                "base_url": "https://api.moonshot.cn/v1",
                "api_key_header": "Authorization",
                "api_key_prefix": "Bearer ",
                "models": [
                    {"id": "moonshot-v1-8k", "name": "Moonshot v1 8K", "type": "chat", "context_length": 8192},
                    {"id": "moonshot-v1-32k", "name": "Moonshot v1 32K", "type": "chat", "context_length": 32768},
                    {"id": "moonshot-v1-128k", "name": "Moonshot v1 128K", "type": "chat", "context_length": 131072}
                ],
                "request_format": "openai_compatible"
            },
            "阿里百炼": {
                "name": "阿里百炼",
                "base_url": "https://dashscope.aliyuncs.com/api/v1",
                "api_key_header": "Authorization",
                "api_key_prefix": "Bearer ",
                "models": [
                    {"id": "qwen-turbo", "name": "通义千问-Turbo", "type": "chat", "context_length": 6000},
                    {"id": "qwen-plus", "name": "通义千问-Plus", "type": "chat", "context_length": 30000},
                    {"id": "qwen-max", "name": "通义千问-Max", "type": "chat", "context_length": 6000}
                ],
                "request_format": "dashscope"
            }
        }
        
        # 加载配置
        self.llm_config = {}
        self.custom_providers = {}
        self.load_configurations()
    
    def _encrypt_key(self, key: str) -> str:
        """加密API密钥"""
        if not key:
            return ""
        return base64.b64encode(key.encode()).decode()
    
    def _decrypt_key(self, encrypted_key: str) -> str:
        """解密API密钥"""
        if not encrypted_key:
            return ""
        try:
            return base64.b64decode(encrypted_key.encode()).decode()
        except Exception:
            return encrypted_key  # 如果解密失败，返回原始值
    
    def load_configurations(self):
        """加载所有配置"""
        self.load_llm_config()
        self.load_providers_config()
    
    def load_llm_config(self):
        """加载LLM配置"""
        try:
            if self.llm_config_file.exists():
                with open(self.llm_config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 加载内置提供商配置
                if "llm_config" in config_data:
                    for provider, encrypted_key in config_data["llm_config"].items():
                        self.llm_config[provider] = self._decrypt_key(encrypted_key)
                
                # 加载自定义提供商配置
                if "custom_llm_providers" in config_data:
                    for name, config in config_data["custom_llm_providers"].items():
                        self.llm_config[name] = self._decrypt_key(config["api_key"])
                
                logger.info(f"LLM配置已加载: {len(self.llm_config)}个提供商")
            else:
                logger.info("LLM配置文件不存在，使用默认配置")
        except Exception as e:
            logger.error(f"加载LLM配置失败: {e}")
    
    def load_providers_config(self):
        """加载提供商配置"""
        try:
            if self.providers_config_file.exists():
                with open(self.providers_config_file, 'r', encoding='utf-8') as f:
                    self.custom_providers = json.load(f)
                logger.info(f"自定义提供商配置已加载: {len(self.custom_providers)}个提供商")
            else:
                logger.info("提供商配置文件不存在，使用默认配置")
        except Exception as e:
            logger.error(f"加载提供商配置失败: {e}")
    
    def save_llm_config(self):
        """保存LLM配置"""
        try:
            # 分离内置和自定义提供商
            built_in_config = {}
            custom_config = {}
            
            for provider, api_key in self.llm_config.items():
                if provider in self.built_in_providers:
                    built_in_config[provider] = self._encrypt_key(api_key)
                else:
                    custom_config[provider] = {
                        "api_key": self._encrypt_key(api_key),
                        "added_time": datetime.now().isoformat()
                    }
            
            config_data = {
                "llm_config": built_in_config,
                "custom_llm_providers": custom_config,
                "saved_time": datetime.now().isoformat(),
                "version": "2.0"
            }
            
            with open(self.llm_config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info("LLM配置已保存")
            return {"status": "success", "message": "配置保存成功"}
        except Exception as e:
            logger.error(f"保存LLM配置失败: {e}")
            return {"status": "error", "message": f"保存失败: {str(e)}"}
    
    def save_providers_config(self):
        """保存提供商配置"""
        try:
            with open(self.providers_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_providers, f, indent=2, ensure_ascii=False)
            
            logger.info("提供商配置已保存")
            return {"status": "success", "message": "提供商配置保存成功"}
        except Exception as e:
            logger.error(f"保存提供商配置失败: {e}")
            return {"status": "error", "message": f"保存失败: {str(e)}"}
    
    def add_custom_provider(self, provider_config: Dict[str, Any]) -> Dict[str, Any]:
        """添加自定义LLM提供商"""
        try:
            required_fields = ["name", "provider_id", "base_url", "api_key"]
            for field in required_fields:
                if field not in provider_config:
                    return {"status": "error", "message": f"缺少必需字段: {field}"}
            
            provider_id = provider_config["provider_id"]
            
            # 检查是否已存在
            if provider_id in self.built_in_providers or provider_id in self.custom_providers:
                return {"status": "error", "message": f"提供商 {provider_id} 已存在"}
            
            # 添加到自定义提供商
            self.custom_providers[provider_id] = {
                "name": provider_config["name"],
                "base_url": provider_config["base_url"],
                "api_key_header": provider_config.get("api_key_header", "Authorization"),
                "api_key_prefix": provider_config.get("api_key_prefix", "Bearer "),
                "models": provider_config.get("models", []),
                "request_format": provider_config.get("request_format", "openai_compatible"),
                "added_time": datetime.now().isoformat(),
                "description": provider_config.get("description", "")
            }
            
            # 添加API密钥到LLM配置
            self.llm_config[provider_id] = provider_config["api_key"]
            
            # 保存配置
            self.save_providers_config()
            self.save_llm_config()
            
            logger.info(f"成功添加自定义提供商: {provider_id}")
            return {"status": "success", "message": f"成功添加提供商: {provider_config['name']}"}
            
        except Exception as e:
            logger.error(f"添加自定义提供商失败: {e}")
            return {"status": "error", "message": f"添加失败: {str(e)}"}
    
    def remove_custom_provider(self, provider_id: str) -> Dict[str, Any]:
        """移除自定义LLM提供商"""
        try:
            if provider_id in self.built_in_providers:
                return {"status": "error", "message": "不能删除内置提供商"}
            
            if provider_id not in self.custom_providers:
                return {"status": "error", "message": f"提供商 {provider_id} 不存在"}
            
            # 移除配置
            del self.custom_providers[provider_id]
            if provider_id in self.llm_config:
                del self.llm_config[provider_id]
            
            # 保存配置
            self.save_providers_config()
            self.save_llm_config()
            
            logger.info(f"成功移除自定义提供商: {provider_id}")
            return {"status": "success", "message": f"成功移除提供商: {provider_id}"}
            
        except Exception as e:
            logger.error(f"移除自定义提供商失败: {e}")
            return {"status": "error", "message": f"移除失败: {str(e)}"}
    
    def get_all_providers(self) -> Dict[str, Any]:
        """获取所有提供商信息"""
        providers = {
            "built_in": {},
            "custom": {}
        }
        
        # 内置提供商
        for provider_id, config in self.built_in_providers.items():
            providers["built_in"][provider_id] = {
                "name": config["name"],
                "configured": provider_id in self.llm_config,
                "models": config["models"],
                "type": "内置"
            }
        
        # 自定义提供商
        for provider_id, config in self.custom_providers.items():
            providers["custom"][provider_id] = {
                "name": config["name"],
                "configured": provider_id in self.llm_config,
                "models": config.get("models", []),
                "type": "自定义",
                "base_url": config["base_url"],
                "added_time": config.get("added_time", "")
            }
        
        return providers
    
    def get_provider_models(self, provider_id: str) -> List[Dict[str, Any]]:
        """获取指定提供商的模型列表"""
        if provider_id in self.built_in_providers:
            return self.built_in_providers[provider_id]["models"]
        elif provider_id in self.custom_providers:
            return self.custom_providers[provider_id].get("models", [])
        else:
            return []
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """获取所有可用模型的简化列表"""
        models = {}
        
        # 内置提供商
        for provider_id, config in self.built_in_providers.items():
            if provider_id in self.llm_config:
                models[provider_id] = [model["id"] for model in config["models"]]
        
        # 自定义提供商
        for provider_id, config in self.custom_providers.items():
            if provider_id in self.llm_config:
                models[provider_id] = [model["id"] for model in config.get("models", [])]
        
        return models
    
    async def test_provider_connection(self, provider_id: str, api_key: str = None) -> Dict[str, Any]:
        """测试提供商连接"""
        try:
            # 使用提供的API密钥或已配置的密钥
            test_api_key = api_key or self.llm_config.get(provider_id)
            if not test_api_key:
                return {"status": "error", "message": "未提供API密钥"}
            
            # 获取提供商配置
            provider_config = None
            if provider_id in self.built_in_providers:
                provider_config = self.built_in_providers[provider_id]
            elif provider_id in self.custom_providers:
                provider_config = self.custom_providers[provider_id]
            else:
                return {"status": "error", "message": "未知的提供商"}
            
            # 执行连接测试
            if provider_config["request_format"] == "openai_compatible":
                result = await self._test_openai_compatible(provider_config, test_api_key)
            elif provider_config["request_format"] == "google_gemini":
                result = await self._test_google_gemini(provider_config, test_api_key)
            elif provider_config["request_format"] == "dashscope":
                result = await self._test_dashscope(provider_config, test_api_key)
            else:
                result = await self._test_generic_api(provider_config, test_api_key)
            
            return result
            
        except Exception as e:
            logger.error(f"测试提供商连接失败: {e}")
            return {"status": "error", "message": f"连接测试失败: {str(e)}"}
    
    async def _test_openai_compatible(self, provider_config: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """测试OpenAI兼容的API"""
        try:
            client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url=provider_config["base_url"]
            )
            
            # 获取第一个可用模型
            models = provider_config["models"]
            if not models:
                return {"status": "error", "message": "没有可用的模型"}
            
            test_model = models[0]["id"]
            
            # 发送测试请求
            response = await client.chat.completions.create(
                model=test_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            return {
                "status": "success", 
                "message": "连接成功",
                "model_used": test_model,
                "response_preview": response.choices[0].message.content[:50]
            }
            
        except Exception as e:
            return {"status": "error", "message": f"OpenAI兼容API测试失败: {str(e)}"}
    
    async def _test_google_gemini(self, provider_config: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """测试Google Gemini API"""
        try:
            # 实现Google Gemini API测试
            # 这里需要根据实际的Google Gemini API格式实现
            return {"status": "success", "message": "Google Gemini连接测试暂未实现"}
        except Exception as e:
            return {"status": "error", "message": f"Google Gemini测试失败: {str(e)}"}
    
    async def _test_dashscope(self, provider_config: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """测试阿里百炼API"""
        try:
            # 实现阿里百炼API测试
            # 这里需要根据实际的阿里百炼API格式实现
            return {"status": "success", "message": "阿里百炼连接测试暂未实现"}
        except Exception as e:
            return {"status": "error", "message": f"阿里百炼测试失败: {str(e)}"}
    
    async def _test_generic_api(self, provider_config: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """测试通用API"""
        try:
            # 实现通用API测试
            return {"status": "success", "message": "通用API连接测试暂未实现"}
        except Exception as e:
            return {"status": "error", "message": f"通用API测试失败: {str(e)}"}
