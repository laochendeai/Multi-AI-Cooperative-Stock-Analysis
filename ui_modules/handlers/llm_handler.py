#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents LLM配置处理模块
负责LLM配置和连接测试
"""

import sys
import os
import asyncio

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class LLMHandler:
    """LLM配置处理器"""
    
    def __init__(self, ui_instance):
        """初始化LLM处理器"""
        self.ui = ui_instance
        self.supported_providers = [
            "OpenAI", "Moonshot", "阿里百炼", "Google", 
            "DeepSeek", "OpenRouter", "Groq"
        ]
    
    def save_llm_config(self, provider, api_key):
        """保存LLM配置"""
        if not api_key:
            return "❌ 请输入API密钥"
        
        if provider not in self.supported_providers:
            return f"❌ 不支持的提供商: {provider}"
        
        try:
            if self.ui.enhanced_features_available:
                # 保存到LLM管理器
                self.ui.llm_manager.llm_config[provider.lower()] = api_key
                result = self.ui.llm_manager.save_llm_config()
                
                if result.get("status") == "success":
                    return f"✅ {provider} 配置保存成功"
                else:
                    return f"❌ 保存失败: {result.get('message', '未知错误')}"
            else:
                return "⚠️ 增强功能不可用，无法保存配置"
                
        except Exception as e:
            return f"❌ 保存失败: {str(e)}"
    
    def test_llm_connection(self, provider, api_key):
        """测试LLM连接"""
        if not api_key:
            return "❌ 请输入API密钥"
        
        if provider not in self.supported_providers:
            return f"❌ 不支持的提供商: {provider}"
        
        try:
            if self.ui.enhanced_features_available:
                # 创建新的事件循环进行测试
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    result = loop.run_until_complete(
                        self.ui.llm_manager.test_provider_connection(
                            provider.lower(), api_key
                        )
                    )
                    
                    if result.get("status") == "success":
                        return f"✅ {provider} 连接测试成功"
                    else:
                        return f"❌ 连接失败: {result.get('message', '未知错误')}"
                        
                finally:
                    loop.close()
            else:
                return "⚠️ 增强功能不可用，无法测试连接"
                
        except Exception as e:
            return f"❌ 测试失败: {str(e)}"
    
    def get_provider_status(self):
        """获取所有提供商状态"""
        if not self.ui.enhanced_features_available:
            return {"error": "增强功能不可用"}
        
        try:
            status = {}
            for provider in self.supported_providers:
                provider_key = provider.lower()
                has_key = bool(self.ui.llm_manager.llm_config.get(provider_key))
                status[provider] = {
                    "configured": has_key,
                    "status": "已配置" if has_key else "未配置"
                }
            return status
            
        except Exception as e:
            return {"error": f"获取状态失败: {str(e)}"}
    
    def clear_provider_config(self, provider):
        """清除提供商配置"""
        if provider not in self.supported_providers:
            return f"❌ 不支持的提供商: {provider}"
        
        try:
            if self.ui.enhanced_features_available:
                provider_key = provider.lower()
                if provider_key in self.ui.llm_manager.llm_config:
                    del self.ui.llm_manager.llm_config[provider_key]
                    result = self.ui.llm_manager.save_llm_config()
                    
                    if result.get("status") == "success":
                        return f"✅ {provider} 配置已清除"
                    else:
                        return f"❌ 清除失败: {result.get('message', '未知错误')}"
                else:
                    return f"⚠️ {provider} 未配置"
            else:
                return "⚠️ 增强功能不可用"
                
        except Exception as e:
            return f"❌ 清除失败: {str(e)}"
    
    def get_available_models(self, provider):
        """获取提供商可用模型"""
        model_map = {
            "OpenAI": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
            "Moonshot": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
            "阿里百炼": ["qwen-turbo", "qwen-plus", "qwen-max"],
            "Google": ["gemini-pro", "gemini-pro-vision"],
            "DeepSeek": ["deepseek-chat", "deepseek-coder"],
            "OpenRouter": ["auto", "openai/gpt-4", "anthropic/claude-3"],
            "Groq": ["llama2-70b-4096", "mixtral-8x7b-32768"]
        }
        
        return model_map.get(provider, [])
    
    def batch_test_connections(self):
        """批量测试所有已配置的连接"""
        if not self.ui.enhanced_features_available:
            return {"error": "增强功能不可用"}
        
        results = {}
        for provider in self.supported_providers:
            provider_key = provider.lower()
            api_key = self.ui.llm_manager.llm_config.get(provider_key)
            
            if api_key:
                result = self.test_llm_connection(provider, api_key)
                results[provider] = result
            else:
                results[provider] = "⚠️ 未配置"
        
        return results

def create_llm_handler(ui_instance):
    """创建LLM处理器"""
    return LLMHandler(ui_instance)
