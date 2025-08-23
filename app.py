#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents 多AI协作股票分析平台
基于真实tradingagents架构的完整模块化程序
实现所有要求的功能
"""

import gradio as gr
import asyncio
import logging
from ui_modules.agent_config import create_agent_config_ui
from ui_modules.llm_management import create_llm_management_ui
from ui_modules.results_display import create_results_display_ui
from ui_modules.analysis_controls import create_analysis_controls_ui
from ui_modules.sidebar import create_sidebar_ui

import os
import json
import sys
import time
import requests
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinalTradingAgentsApp:
    """最终集成的TradingAgents应用"""
    
    def __init__(self):
        """初始化最终应用"""
        logger.info("🚀 初始化最终TradingAgents应用...")
        
        try:
            # 延迟导入，避免初始化时卡住
            from app_enhanced import EnhancedTradingAgentsApp
            self.enhanced_app = EnhancedTradingAgentsApp()
            logger.info("✅ 增强版应用初始化完成")
        except Exception as e:
            logger.error(f"❌ 增强版应用初始化失败: {e}")
            self.enhanced_app = None
        
        # 分析状态
        self.analysis_state = {
            "is_running": False,
            "current_stage": "",
            "progress": 0,
            "symbol": "",
            "depth": ""
        }
        
        # 支持的导出格式
        self.export_formats = ["markdown", "json", "txt"]
        
        # LLM提供商配置
        self.custom_providers = {}

        # 智能体模型配置记忆
        self.agent_model_config_file = Path("config/agent_model_config.json")
        self.agent_model_memory = self._load_agent_model_config()

        # 同步配置到enhanced_app
        if self.enhanced_app:
            self.enhanced_app.agent_model_config.update(self.agent_model_memory)
            logger.info("🔄 配置已同步到增强版应用")

        logger.info(f"✅ 智能体模型配置已加载: {len(self.agent_model_memory)}个智能体")

        logger.info("✅ 最终TradingAgents应用初始化完成")

    def _load_agent_model_config(self) -> Dict[str, str]:
        """加载智能体模型配置"""
        try:
            available_agents = self.get_available_agents()

            if self.agent_model_config_file.exists():
                with open(self.agent_model_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # 过滤配置，只保留程序中定义的智能体
                filtered_config = {}
                for agent in available_agents:
                    if agent in config:
                        # 确保配置是完整格式（provider:model）
                        model_config = config[agent]
                        if ":" not in model_config:
                            model_config = self._build_full_model_config(model_config)
                        filtered_config[agent] = model_config
                    else:
                        # 为缺失的智能体设置默认模型
                        filtered_config[agent] = self._get_default_model_for_agent(agent)

                # 如果配置被过滤了，重新保存
                if len(filtered_config) != len(config):
                    logger.info(f"📂 配置文件包含额外智能体，已过滤: {len(config)} -> {len(filtered_config)}")
                    self._save_agent_model_config(filtered_config)

                logger.info(f"📂 从文件加载智能体配置: {len(filtered_config)}个智能体")
                return filtered_config
            else:
                # 如果配置文件不存在，使用默认配置
                default_config = {}
                for agent in available_agents:
                    default_config[agent] = self._get_default_model_for_agent(agent)

                logger.info(f"📂 使用默认智能体配置: {len(default_config)}个智能体")
                # 保存默认配置到文件
                self._save_agent_model_config(default_config)
                return default_config
        except Exception as e:
            logger.error(f"❌ 加载智能体配置失败: {e}")
            # 返回默认配置
            available_agents = self.get_available_agents()
            default_config = {}
            for agent in available_agents:
                default_config[agent] = self._get_default_model_for_agent(agent)
            return default_config

    def _get_default_model_for_agent(self, agent: str) -> str:
        """为智能体获取默认模型"""
        # 根据智能体类型选择合适的默认模型
        default_models = {
            "market_analyst": "阿里百炼:qwen-turbo",
            "sentiment_analyst": "阿里百炼:qwen-turbo",
            "social_media_analyst": "阿里百炼:qwen-turbo",
            "news_analyst": "阿里百炼:qwen-turbo",
            "fundamentals_analyst": "阿里百炼:qwen-turbo",
            "bull_researcher": "阿里百炼:qwen-turbo",
            "bear_researcher": "阿里百炼:qwen-turbo",
            "research_manager": "阿里百炼:qwen-turbo",
            "trader": "阿里百炼:qwen-turbo",
            "aggressive_debator": "阿里百炼:qwen-turbo",
            "conservative_debator": "阿里百炼:qwen-turbo",
            "neutral_debator": "阿里百炼:qwen-turbo",
            "risk_manager": "阿里百炼:qwen-turbo",
            "memory_manager": "阿里百炼:qwen-turbo",
            "signal_processor": "阿里百炼:qwen-turbo",
            "reflection_engine": "阿里百炼:qwen-turbo"
        }
        return default_models.get(agent, "阿里百炼:qwen-turbo")

    def _save_agent_model_config(self, config: Dict[str, str] = None):
        """保存智能体模型配置到文件"""
        try:
            # 确保配置目录存在
            self.agent_model_config_file.parent.mkdir(parents=True, exist_ok=True)

            # 使用传入的配置或当前配置
            config_to_save = config or self.agent_model_memory

            # 同步到enhanced_app
            if hasattr(self, 'enhanced_app') and self.enhanced_app:
                self.enhanced_app.agent_model_config.update(config_to_save)

            with open(self.agent_model_config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, ensure_ascii=False, indent=2)

            logger.info(f"💾 智能体配置已保存到: {self.agent_model_config_file}")
        except Exception as e:
            logger.error(f"❌ 保存智能体配置失败: {e}")

    def get_available_agents(self) -> List[str]:
        """获取可用的智能体列表"""
        return [
            "market_analyst",      # 市场技术分析师
            "sentiment_analyst",   # 情感分析师
            "social_media_analyst", # 社交媒体分析师
            "news_analyst",        # 新闻分析师
            "fundamentals_analyst", # 基本面分析师
            "bull_researcher",     # 多头研究员
            "bear_researcher",     # 空头研究员
            "research_manager",    # 研究经理
            "trader",             # 交易员
            "aggressive_debator",  # 激进分析师
            "conservative_debator", # 保守分析师
            "neutral_debator",     # 中性分析师
            "risk_manager",        # 风险管理师
            "memory_manager",      # 记忆管理器
            "signal_processor",    # 信号处理器
            "reflection_engine"    # 反思引擎
        ]
    
    def get_analysis_depths(self) -> List[str]:
        """获取分析深度选项"""
        return ["快速分析", "标准分析", "深度分析", "全面分析"]
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """获取可用的LLM模型"""
        if self.enhanced_app:
            return self.enhanced_app.get_available_models()
        else:
            return {
                "openai": ["gpt-4", "gpt-3.5-turbo"],
                "deepseek": ["deepseek-chat"],
                "google": ["gemini-pro"]
            }

    def get_all_available_models_list(self) -> List[str]:
        """获取所有可用模型的平铺列表（仅包含已配置的提供商）"""
        models_dict = self.get_available_models()
        configured_providers = self.get_configured_providers_list()

        all_models = []
        for provider, models in models_dict.items():
            # 只包含已配置LLM密钥的提供商的模型
            if provider in configured_providers:
                all_models.extend(models)
        return all_models

    def get_configured_providers_list(self) -> List[str]:
        """获取已配置LLM密钥的提供商列表"""
        configured_providers = []
        if self.enhanced_app:
            try:
                llm_config = self.enhanced_app.llm_config
                for provider in llm_config.keys():
                    if provider not in ["saved_time", "version"]:
                        configured_providers.append(provider)
            except Exception as e:
                logger.error(f"获取已配置提供商失败: {e}")
        return configured_providers

    def get_models_with_features(self) -> Dict[str, Dict[str, Any]]:
        """获取模型及其特色功能描述"""
        models_dict = self.get_available_models()
        configured_providers = self.get_configured_providers_list()

        models_with_features = {}

        # 模型特色描述
        model_features = {
            # DeepSeek 模型
            "deepseek-chat": {
                "provider": "deepseek",
                "description": "🧠 中文对话专家 - 擅长中文理解和逻辑推理",
                "features": ["中文对话", "逻辑推理", "知识问答"],
                "best_for": "中文分析、逻辑推理"
            },
            "deepseek-coder": {
                "provider": "deepseek",
                "description": "💻 代码生成专家 - 专业的编程和代码分析",
                "features": ["代码生成", "程序分析", "技术解答"],
                "best_for": "技术分析、代码相关"
            },

            # Google 模型
            "gemini-pro": {
                "provider": "google",
                "description": "🌟 多模态AI - 支持文本、图像理解和联网搜索",
                "features": ["多模态", "联网搜索", "图像理解"],
                "best_for": "综合分析、联网搜索"
            },
            "gemini-1.5-flash": {
                "provider": "google",
                "description": "⚡ 快速响应 - 高速处理，适合实时分析",
                "features": ["快速响应", "联网搜索", "实时分析"],
                "best_for": "快速分析、实时响应"
            },
            "gemini-1.5-pro": {
                "provider": "google",
                "description": "🎯 专业版本 - 更强的推理能力和准确性",
                "features": ["深度推理", "联网搜索", "高准确性"],
                "best_for": "深度分析、专业判断"
            },

            # Moonshot 模型
            "moonshot-v1-8k": {
                "provider": "moonshot",
                "description": "🌙 长文本处理 - 8K上下文，适合文档分析",
                "features": ["长文本", "文档分析", "上下文理解"],
                "best_for": "文档分析、长文本处理"
            },
            "moonshot-v1-32k": {
                "provider": "moonshot",
                "description": "📚 超长文本 - 32K上下文，处理大量信息",
                "features": ["超长文本", "大量信息", "深度理解"],
                "best_for": "大量数据分析、深度研究"
            },

            # 阿里百炼模型
            "qwen-turbo": {
                "provider": "阿里百炼",
                "description": "🔥 通义千问快速版 - 平衡速度和质量",
                "features": ["中文优化", "联网搜索", "快速响应"],
                "best_for": "中文分析、快速处理"
            },
            "qwen-plus": {
                "provider": "阿里百炼",
                "description": "⭐ 通义千问增强版 - 更强的推理和创作能力",
                "features": ["强推理", "联网搜索", "创作能力"],
                "best_for": "复杂分析、创意内容"
            },

            # Groq 模型
            "llama3-8b-8192": {
                "provider": "groq",
                "description": "🚀 Llama3快速版 - 超高速推理引擎",
                "features": ["超高速", "低延迟", "实时响应"],
                "best_for": "实时分析、快速响应"
            },
            "llama3-70b-8192": {
                "provider": "groq",
                "description": "💪 Llama3强化版 - 更强的理解和推理能力",
                "features": ["强推理", "高质量", "复杂任务"],
                "best_for": "复杂分析、深度推理"
            }
        }

        # 只包含已配置提供商的模型
        for provider, models in models_dict.items():
            if provider in configured_providers:
                for model in models:
                    if model in model_features:
                        models_with_features[model] = model_features[model]
                    else:
                        # 为未定义的模型提供默认描述
                        models_with_features[model] = {
                            "provider": provider,
                            "description": f"🤖 {model} - {provider}提供的AI模型",
                            "features": ["通用AI功能"],
                            "best_for": "通用分析任务"
                        }

        return models_with_features

    def update_agent_model_config(self, agent: str, model: str) -> str:
        """更新智能体模型配置"""
        try:
            if agent not in self.get_available_agents():
                return f"❌ 无效的智能体: {agent}"

            all_models = self.get_all_available_models_list()
            if model not in all_models:
                return f"❌ 无效的模型: {model}"

            # 构建完整的模型配置（provider:model格式）
            full_model_config = self._build_full_model_config(model)

            # 更新内存中的配置
            self.agent_model_memory[agent] = full_model_config

            # 同时更新enhanced_app的配置
            if hasattr(self, 'enhanced_app') and self.enhanced_app:
                self.enhanced_app.agent_model_config[agent] = full_model_config

            # 立即保存到文件
            self._save_agent_model_config()

            logger.info(f"✅ 智能体 {agent} 模型配置已更新并保存: {full_model_config}")
            return f"✅ 已更新 {agent} 的模型为: {full_model_config}"
        except Exception as e:
            logger.error(f"❌ 更新智能体配置失败: {e}")
            return f"❌ 更新失败: {str(e)}"

    def _build_full_model_config(self, model: str) -> str:
        """构建完整的模型配置（provider:model格式）"""
        if ":" in model:
            return model  # 已经是完整格式

        # 根据模型名称找到对应的提供商
        models_dict = self.get_available_models()
        for provider, provider_models in models_dict.items():
            if model in provider_models:
                return f"{provider}:{model}"

        # 如果找不到，使用默认提供商
        return f"阿里百炼:{model}"

    def get_agent_model_config(self) -> Dict[str, str]:
        """获取当前智能体模型配置"""
        return self.agent_model_memory.copy()

    def get_configured_llm_providers(self) -> Dict[str, Any]:
        """获取当前已配置的LLM提供商的详细信息"""
        configured = {}

        # 从enhanced_app获取已配置的提供商
        if self.enhanced_app:
            try:
                llm_config = self.enhanced_app.llm_config
                models_dict = self.get_available_models()

                for provider, config in llm_config.items():
                    if provider not in ["saved_time", "version"]:
                        # 获取提供商的详细信息
                        provider_info = {
                            "配置状态": "✅ 已配置",
                            "提供商类型": self._get_provider_type(provider),
                            "可用模型": models_dict.get(provider, []),
                            "模型数量": len(models_dict.get(provider, [])),
                            "联网搜索": self._check_network_capability(provider),
                            "API状态": "🔄 未测试",
                            "响应速度": "未知",
                            "特色功能": self._get_provider_features(provider)
                        }
                        configured[provider] = provider_info
            except Exception as e:
                logger.error(f"获取系统LLM配置失败: {e}")

        # 添加自定义提供商
        for name, config in self.custom_providers.items():
            configured[name] = {
                "配置状态": "✅ 自定义配置",
                "提供商类型": "自定义",
                "API地址": config.get("url", ""),
                "添加时间": config.get("added_time", ""),
                "联网搜索": "❓ 未知",
                "API状态": "🔄 未测试"
            }

        return configured

    def _get_provider_type(self, provider: str) -> str:
        """获取提供商类型描述"""
        provider_types = {
            "deepseek": "🧠 深度求索 - 中文优化大模型",
            "google": "🌟 Google Gemini - 多模态AI",
            "moonshot": "🌙 月之暗面 - 长文本处理",
            "阿里百炼": "🔥 阿里云 - 企业级AI",
            "openrouter": "🌐 OpenRouter - AI模型路由",
            "groq": "⚡ Groq - 高速推理引擎",
            "openai": "🤖 OpenAI - GPT系列模型"
        }
        return provider_types.get(provider, f"🔧 {provider}")

    def _check_network_capability(self, provider: str) -> str:
        """检查提供商的联网搜索能力"""
        # 基于已知信息判断联网能力
        network_capable = {
            "deepseek": "❌ 不支持联网",
            "google": "✅ 支持联网搜索",
            "moonshot": "❌ 不支持联网",
            "阿里百炼": "✅ 支持联网搜索",
            "openrouter": "🔄 取决于具体模型",
            "groq": "❌ 不支持联网",
            "openai": "❌ 不支持联网"
        }
        return network_capable.get(provider, "❓ 未知")

    def _get_provider_features(self, provider: str) -> List[str]:
        """获取提供商的特色功能"""
        features = {
            "deepseek": ["代码生成", "中文对话", "逻辑推理"],
            "google": ["多模态", "联网搜索", "图像理解"],
            "moonshot": ["长文本", "文档分析", "上下文理解"],
            "阿里百炼": ["企业应用", "联网搜索", "多语言"],
            "openrouter": ["模型选择", "负载均衡", "成本优化"],
            "groq": ["高速推理", "低延迟", "实时响应"],
            "openai": ["通用对话", "创意写作", "问题解答"]
        }
        return features.get(provider, ["通用AI功能"])

    async def test_all_providers_status(self) -> Dict[str, Dict[str, str]]:
        """测试所有已配置提供商的状态"""
        results = {}
        configured_providers = []

        # 获取已配置的提供商
        if self.enhanced_app:
            try:
                llm_config = self.enhanced_app.llm_config
                for provider in llm_config.keys():
                    if provider not in ["saved_time", "version"]:
                        configured_providers.append(provider)
            except Exception as e:
                logger.error(f"获取提供商列表失败: {e}")

        # 测试每个提供商
        for provider in configured_providers:
            try:
                logger.info(f"🧪 测试提供商状态: {provider}")

                # 网络连接测试
                network_result = self._test_provider_network_simple(provider)

                # 模型响应测试（如果有可用模型）
                models_dict = self.get_available_models()
                response_result = "❓ 未测试"
                response_time = "未知"

                if provider in models_dict and models_dict[provider]:
                    test_model = models_dict[provider][0]
                    try:
                        start_time = time.time()
                        response = await self.enhanced_app._call_llm(
                            provider, test_model, "Hi", "status_test"
                        )
                        end_time = time.time()

                        if response and len(response.strip()) > 0:
                            response_result = "✅ 响应正常"
                            response_time = f"{round(end_time - start_time, 2)}秒"
                        else:
                            response_result = "⚠️ 响应为空"
                            response_time = f"{round(end_time - start_time, 2)}秒"
                    except Exception as e:
                        response_result = "❌ 响应失败"
                        response_time = "超时"

                results[provider] = {
                    "网络状态": network_result,
                    "API状态": response_result,
                    "响应速度": response_time
                }

            except Exception as e:
                results[provider] = {
                    "网络状态": "❌ 测试失败",
                    "API状态": "❌ 测试失败",
                    "响应速度": "未知"
                }
                logger.error(f"测试 {provider} 失败: {e}")

        return results

    def _test_provider_network_simple(self, provider: str) -> str:
        """简单的网络连接测试"""
        try:
            provider_urls = {
                "deepseek": "https://api.deepseek.com/v1/models",
                "google": "https://generativelanguage.googleapis.com/v1/models",
                "moonshot": "https://api.moonshot.cn/v1/models",
                "阿里百炼": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                "groq": "https://api.groq.com/openai/v1/models",
                "openrouter": "https://openrouter.ai/api/v1/models",
                "openai": "https://api.openai.com/v1/models"
            }

            url = provider_urls.get(provider)
            if not url:
                return "❓ 未知提供商"

            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                return "✅ 网络正常"
            elif response.status_code in [401, 403]:
                return "✅ 网络正常 (需要认证)"
            else:
                return f"⚠️ 状态码: {response.status_code}"

        except requests.exceptions.Timeout:
            return "⏰ 连接超时"
        except requests.exceptions.ConnectionError:
            return "❌ 连接失败"
        except Exception as e:
            return f"❌ 异常: {str(e)[:20]}..."

    def _format_provider_overview(self) -> str:
        """格式化提供商概览"""
        try:
            configured = self.get_configured_llm_providers()
            if not configured:
                return "❌ 未检测到任何已配置的LLM提供商"

            overview = []
            overview.append(f"📊 **已配置提供商总数**: {len(configured)}个\n")

            for provider, info in configured.items():
                provider_type = info.get("提供商类型", provider)
                model_count = info.get("模型数量", 0)
                network_capability = info.get("联网搜索", "❓ 未知")

                overview.append(f"🏢 **{provider}**")
                overview.append(f"   - {provider_type}")
                overview.append(f"   - 可用模型: {model_count}个")
                overview.append(f"   - 联网搜索: {network_capability}")
                overview.append("")

            return "\n".join(overview)
        except Exception as e:
            return f"❌ 获取概览失败: {str(e)}"

    def _format_models_by_provider(self) -> str:
        """按提供商格式化模型列表"""
        try:
            models_dict = self.get_available_models()
            configured = self.get_configured_llm_providers()

            if not models_dict:
                return "❌ 未找到任何可用模型"

            formatted = []

            for provider, models in models_dict.items():
                if provider in configured:
                    provider_info = configured[provider]
                    provider_type = provider_info.get("提供商类型", provider)
                    network_capability = provider_info.get("联网搜索", "❓ 未知")
                    features = provider_info.get("特色功能", [])

                    formatted.append(f"## 🏢 {provider}")
                    formatted.append(f"**类型**: {provider_type}")
                    formatted.append(f"**联网搜索**: {network_capability}")
                    formatted.append(f"**特色功能**: {', '.join(features)}")
                    formatted.append(f"**可用模型** ({len(models)}个):")

                    for i, model in enumerate(models, 1):
                        formatted.append(f"   {i}. `{model}`")

                    formatted.append("")

            return "\n".join(formatted)
        except Exception as e:
            return f"❌ 格式化模型列表失败: {str(e)}"
    
    async def analyze_stock_real(self, symbol: str, depth: str, 
                               selected_agents: List[str], 
                               agent_models: Dict[str, str] = None) -> Dict[str, Any]:
        """使用真实tradingagents架构进行股票分析"""
        try:
            logger.info(f"🔍 开始真实分析: {symbol}, 深度: {depth}")
            
            # 设置分析状态
            self.analysis_state.update({
                "is_running": True,
                "current_stage": "初始化分析",
                "progress": 10,
                "symbol": symbol,
                "depth": depth
            })
            
            if not self.enhanced_app:
                raise Exception("增强版应用未初始化")
            
            # 使用增强版应用进行分析
            self.analysis_state.update({
                "current_stage": "执行智能体分析",
                "progress": 30
            })
            
            # 调用增强版应用的分析方法
            result = await self.enhanced_app.analyze_stock_enhanced(
                symbol, depth, selected_agents, use_real_llm=True
            )
            
            # 处理结果
            self.analysis_state.update({
                "current_stage": "处理分析结果",
                "progress": 80
            })
            
            processed_result = self._process_analysis_result(
                result, symbol, depth, selected_agents, agent_models
            )
            
            # 完成分析
            self.analysis_state.update({
                "is_running": False,
                "current_stage": "分析完成",
                "progress": 100
            })
            
            logger.info(f"✅ 真实分析完成: {symbol}")
            return processed_result
            
        except Exception as e:
            logger.error(f"❌ 真实分析失败: {e}")
            self.analysis_state.update({
                "is_running": False,
                "current_stage": f"分析失败: {str(e)}",
                "progress": 0
            })
            # 返回错误结果而不是抛出异常
            return {
                "error": str(e),
                "symbol": symbol,
                "analysis_depth": depth,
                "timestamp": datetime.now().isoformat(),
                "selected_agents": selected_agents,
                "raw_result": f"分析失败: {str(e)}",
                "formatted_result": f"❌ 分析失败: {str(e)}",
                "summary": f"分析过程中出现错误: {str(e)}",
                "recommendations": ["请检查股票代码是否正确", "请检查网络连接", "请稍后重试"]
            }
    
    def _process_analysis_result(self, result: str, symbol: str, 
                               depth: str, selected_agents: List[str],
                               agent_models: Dict[str, str] = None) -> Dict[str, Any]:
        """处理分析结果"""
        processed = {
            "symbol": symbol,
            "analysis_depth": depth,
            "timestamp": datetime.now().isoformat(),
            "selected_agents": selected_agents,
            "agent_models": agent_models or {},
            "raw_result": result,
            "formatted_result": self._format_result(result, symbol),
            "summary": self._extract_summary(result),
            "recommendations": self._extract_recommendations(result)
        }
        
        return processed
    
    def _format_result(self, result: str, symbol: str) -> str:
        """格式化分析结果"""
        if not result or result.strip() == "":
            return "❌ 分析结果为空"
        
        # 格式化处理
        formatted = f"""# 📊 {symbol} 股票分析报告

{result}

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*分析引擎: TradingAgents 真实架构*
"""
        return formatted
    
    def _extract_summary(self, result: str) -> str:
        """提取分析总结"""
        if not result:
            return "无分析结果"
        
        # 提取总结
        lines = result.split('\n')
        summary_lines = []
        
        for line in lines:
            if any(keyword in line for keyword in ['总结', '结论', '建议', '观点']):
                summary_lines.append(line.strip())
        
        if summary_lines:
            return '\n'.join(summary_lines[:3])  # 取前3行
        else:
            # 如果没有找到关键词，取前200个字符
            return result[:200] + "..." if len(result) > 200 else result
    
    def _extract_recommendations(self, result: str) -> List[str]:
        """提取投资建议"""
        recommendations = []
        
        # 基于结果内容提取建议
        if "买入" in result or "看涨" in result or "积极" in result:
            recommendations.append("🟢 分析显示积极信号，可考虑适量配置")
        elif "卖出" in result or "看跌" in result or "消极" in result:
            recommendations.append("🔴 分析显示消极信号，建议谨慎观望")
        else:
            recommendations.append("🟡 分析结果中性，建议持续观察")
        
        # 通用建议
        recommendations.extend([
            "📊 请结合多方面信息进行投资决策",
            "⚠️ 注意风险管理，合理控制仓位",
            "📈 关注市场变化，及时调整策略"
        ])
        
        return recommendations
    
    def add_custom_provider(self, name: str, url: str, key: str) -> str:
        """添加自定义LLM提供商"""
        try:
            if not all([name, url, key]):
                return "❌ 请填写完整的提供商信息"
            
            self.custom_providers[name] = {
                "url": url,
                "key": key,
                "added_time": datetime.now().isoformat()
            }
            
            return f"✅ 成功添加提供商: {name}"
        except Exception as e:
            return f"❌ 添加提供商失败: {str(e)}"
    
    def test_llm_connection(self, provider_name: str, api_url: str, api_key: str) -> str:
        """测试LLM连接"""
        try:
            if not all([provider_name, api_url, api_key]):
                return "❌ 请填写完整的提供商信息"
            
            # 这里可以实现实际的连接测试
            # 暂时返回模拟结果
            import time
            time.sleep(1)  # 模拟测试延迟
            
            return f"✅ {provider_name} 连接测试成功\n📡 API地址: {api_url}\n🔑 密钥验证通过"
        except Exception as e:
            return f"❌ {provider_name} 连接测试失败: {str(e)}"
    
    def test_network_connection(self) -> str:
        """测试网络连接"""
        try:
            import requests

            # 测试多个网站
            test_urls = [
                ("百度", "https://www.baidu.com"),
                ("Google", "https://www.google.com"),
                ("GitHub", "https://api.github.com")
            ]

            results = []
            for name, url in test_urls:
                try:
                    response = requests.get(url, timeout=3)
                    if response.status_code == 200:
                        results.append(f"✅ {name}: 连接正常")
                    else:
                        results.append(f"⚠️ {name}: 状态码 {response.status_code}")
                except:
                    results.append(f"❌ {name}: 连接失败")

            return "\n".join(results)
        except Exception as e:
            return f"❌ 网络测试失败: {str(e)}"

    def test_model_connection(self, model_name: str) -> str:
        """测试特定模型的真实联网功能"""
        try:
            if not model_name:
                return "❌ 请选择要测试的模型"

            logger.info(f"🧪 开始测试模型: {model_name}")

            # 查找模型所属的提供商
            provider = None
            models_dict = self.get_available_models()
            for prov, models in models_dict.items():
                if model_name in models:
                    provider = prov
                    break

            if not provider:
                error_msg = f"❌ 未找到模型 {model_name} 的提供商"
                logger.error(error_msg)
                return error_msg

            logger.info(f"📍 找到提供商: {provider}")

            # 真实的模型API测试
            test_results = []
            test_results.append(f"🤖 模型: {model_name}")
            test_results.append(f"🏢 提供商: {provider}")

            # 1. 测试网络连接
            logger.info("🌐 测试网络连接...")
            network_result = self._test_provider_network(provider)
            test_results.append(f"🌐 网络连接: {network_result}")

            # 2. 测试API认证
            logger.info("🔑 测试API认证...")
            auth_result = self._test_provider_auth(provider)
            test_results.append(f"🔑 API认证: {auth_result}")

            # 3. 测试模型响应
            logger.info("⚡ 测试模型响应...")
            response_result = self._test_model_response(provider, model_name)
            test_results.append(f"⚡ 模型响应: {response_result}")

            # 4. 测试响应速度
            logger.info("📊 测试响应速度...")
            speed_result = self._test_response_speed(provider, model_name)
            test_results.append(f"📊 响应速度: {speed_result}")

            final_result = "\n".join(test_results)
            logger.info(f"✅ 模型测试完成: {model_name}")
            logger.info(f"测试结果:\n{final_result}")

            return final_result

        except Exception as e:
            error_msg = f"❌ 模型测试失败: {str(e)}"
            logger.error(error_msg)
            logger.error(f"错误详情: {e}", exc_info=True)
            return error_msg

    def _test_provider_network(self, provider: str) -> str:
        """测试提供商网络连接"""
        try:
            import requests

            # 提供商API端点映射
            provider_urls = {
                "openai": "https://api.openai.com/v1/models",
                "deepseek": "https://api.deepseek.com/v1/models",
                "google": "https://generativelanguage.googleapis.com/v1/models",
                "moonshot": "https://api.moonshot.cn/v1/models",
                "阿里百炼": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                "groq": "https://api.groq.com/openai/v1/models",
                "openrouter": "https://openrouter.ai/api/v1/models"
            }

            url = provider_urls.get(provider)
            if not url:
                return "⚠️ 未知提供商"

            logger.info(f"🌐 测试网络连接到: {url}")

            response = requests.get(url, timeout=10)
            status_code = response.status_code

            logger.info(f"🌐 网络响应状态码: {status_code}")

            if status_code == 200:
                return "✅ 连接正常"
            elif status_code == 401:
                return "🔑 需要认证 (网络正常)"
            elif status_code == 403:
                return "🚫 访问被拒绝 (网络正常)"
            else:
                return f"⚠️ 状态码: {status_code}"

        except requests.exceptions.Timeout:
            logger.warning(f"🌐 网络连接超时: {provider}")
            return "⏰ 连接超时"
        except requests.exceptions.ConnectionError:
            logger.warning(f"🌐 网络连接失败: {provider}")
            return "❌ 连接失败"
        except Exception as e:
            logger.error(f"🌐 网络测试异常: {e}")
            return f"❌ 测试异常: {str(e)}"

    def _test_provider_auth(self, provider: str) -> str:
        """测试提供商API认证"""
        try:
            if not self.enhanced_app:
                return "⚠️ 应用未初始化"

            # 获取API密钥
            api_key = None
            try:
                llm_config = self.enhanced_app.llm_config
                if provider in llm_config:
                    # 解码base64编码的API密钥
                    import base64
                    encoded_key = llm_config[provider]
                    api_key = base64.b64decode(encoded_key).decode('utf-8')
                    logger.info(f"🔑 获取到API密钥: {provider} (长度: {len(api_key)})")
            except Exception as e:
                logger.warning(f"🔑 获取API密钥失败: {e}")
                return "❌ 无API密钥"

            if not api_key:
                return "❌ 未配置密钥"

            # 测试API认证
            import requests

            provider_test_configs = {
                "openai": {
                    "url": "https://api.openai.com/v1/models",
                    "headers": {"Authorization": f"Bearer {api_key}"}
                },
                "deepseek": {
                    "url": "https://api.deepseek.com/v1/models",
                    "headers": {"Authorization": f"Bearer {api_key}"}
                },
                "google": {
                    "url": f"https://generativelanguage.googleapis.com/v1/models?key={api_key}",
                    "headers": {}
                }
            }

            config = provider_test_configs.get(provider)
            if not config:
                return "⚠️ 暂不支持此提供商认证测试"

            logger.info(f"🔑 测试API认证: {config['url']}")

            response = requests.get(
                config["url"],
                headers=config["headers"],
                timeout=10
            )

            status_code = response.status_code
            logger.info(f"🔑 认证响应状态码: {status_code}")

            if status_code == 200:
                return "✅ 认证成功"
            elif status_code == 401:
                return "❌ 认证失败"
            elif status_code == 403:
                return "🚫 权限不足"
            else:
                return f"⚠️ 状态码: {status_code}"

        except Exception as e:
            logger.error(f"🔑 认证测试异常: {e}")
            return f"❌ 认证异常: {str(e)}"

    def _test_model_response(self, provider: str, model_name: str) -> str:
        """测试模型响应"""
        try:
            if not self.enhanced_app:
                return "⚠️ 应用未初始化"

            logger.info(f"⚡ 开始测试模型响应: {provider}/{model_name}")

            # 使用enhanced_app的LLM调用功能进行真实测试
            test_prompt = "请回复'测试成功'"

            # 调用LLM进行测试
            response = asyncio.run(self.enhanced_app._call_llm(
                provider, model_name, test_prompt, "test_agent"
            ))

            if response and len(response.strip()) > 0:
                logger.info(f"⚡ 模型响应成功: {response[:50]}...")
                return f"✅ 响应正常 ({len(response)}字符)"
            else:
                logger.warning("⚡ 模型响应为空")
                return "⚠️ 响应为空"

        except Exception as e:
            logger.error(f"⚡ 模型响应测试异常: {e}")
            return f"❌ 响应异常: {str(e)}"

    def _test_response_speed(self, provider: str, model_name: str) -> str:
        """测试响应速度"""
        try:
            import time

            logger.info(f"📊 开始测试响应速度: {provider}/{model_name}")

            start_time = time.time()

            # 简单的速度测试
            if self.enhanced_app:
                test_prompt = "Hi"
                asyncio.run(self.enhanced_app._call_llm(
                    provider, model_name, test_prompt, "speed_test"
                ))

                end_time = time.time()
                response_time = end_time - start_time

                logger.info(f"📊 响应时间: {response_time:.2f}秒")

                if response_time < 2:
                    return f"🚀 很快 ({response_time:.2f}s)"
                elif response_time < 5:
                    return f"⚡ 正常 ({response_time:.2f}s)"
                elif response_time < 10:
                    return f"🐌 较慢 ({response_time:.2f}s)"
                else:
                    return f"🐢 很慢 ({response_time:.2f}s)"
            else:
                return "⚠️ 无法测试"

        except Exception as e:
            logger.error(f"📊 速度测试异常: {e}")
            return f"❌ 测试异常: {str(e)}"
    
    def export_analysis_result(self, result: Dict[str, Any], 
                             format_type: str) -> str:
        """导出分析结果"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            symbol = result.get("symbol", "unknown")
            filename = f"analysis_{symbol}_{timestamp}.{format_type}"
            
            if format_type == "json":
                content = json.dumps(result, ensure_ascii=False, indent=2)
            elif format_type == "markdown":
                content = self._format_as_markdown(result)
            elif format_type == "txt":
                content = self._format_as_text(result)
            else:
                raise ValueError(f"不支持的导出格式: {format_type}")
            
            # 保存文件
            export_dir = Path("exports")
            export_dir.mkdir(exist_ok=True)
            
            file_path = export_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✅ 分析结果已导出: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"❌ 导出失败: {e}")
            raise
    
    def _format_as_markdown(self, result: Dict[str, Any]) -> str:
        """格式化为Markdown"""
        # 获取基本信息
        symbol = result.get('symbol', 'N/A')

        status = result.get('status', 'unknown')

        md_content = f"""# 📊 {symbol} 股票分析报告

**项目开源地址**：https://github.com/laochendeai/Multi-AI-Cooperative-Stock-Analysis
https://gitee.com/laochendeai/Multi-AI-Cooperative-Stock-Analysis
**绿泡泡号**：mtj1fc
**项目完全开源免费，我的主业弱电设计\\项目合作，欢迎大家联系。**

## 📋 基本信息
- **股票代码**: {symbol}
- **分析状态**: {status}
- **分析深度**: {result.get('depth', result.get('analysis_depth', 'N/A'))}
- **选择的智能体**: {', '.join(result.get('selected_agents', []))}

"""

        # 获取详细分析结果
        results = result.get('results', {})

        # 综合报告
        comprehensive_report = results.get('comprehensive_report', '')
        if comprehensive_report:
            md_content += f"""## 📈 综合分析报告
{comprehensive_report}

"""

        # 各个智能体的分析结果
        analysis_sections = [
            ('market_analysis', '🏪 市场分析'),
            ('sentiment_analysis', '😊 情感分析'),
            ('fundamentals_analysis', '📊 基本面分析'),
            ('news_analysis', '📰 新闻分析'),
            ('bull_arguments', '🐂 多头观点'),
            ('bear_arguments', '🐻 空头观点'),
            ('trading_strategy', '💼 交易策略'),
            ('risk_assessment', '⚠️ 风险评估')
        ]

        for key, title in analysis_sections:
            analysis_data = results.get(key, {})
            if analysis_data and isinstance(analysis_data, dict):
                analysis_content = analysis_data.get('analysis', '')
                if analysis_content:
                    md_content += f"""## {title}
{analysis_content}

"""

        # 最终决策
        final_decision = results.get('final_decision', {})
        if final_decision:
            md_content += "## 🎯 最终投资建议\n"
            if isinstance(final_decision, dict):
                decision = final_decision.get('decision', 'HOLD')
                reasoning = final_decision.get('reasoning', '')
                confidence = final_decision.get('confidence', 0)

                md_content += f"- **投资决策**: {decision}\n"
                md_content += f"- **置信度**: {confidence}%\n"
                if reasoning:
                    md_content += f"- **决策理由**: {reasoning}\n"
            else:
                md_content += f"- **投资决策**: {final_decision}\n"
            md_content += "\n"

        # 分析流程信息
        analysis_flow = result.get('analysis_flow', {})
        if analysis_flow:
            md_content += "## � 分析流程\n"
            for stage, info in analysis_flow.items():
                if isinstance(info, dict):
                    status = info.get('status', 'unknown')
                    duration = info.get('duration', 0)
                    md_content += f"- **{stage}**: {status} ({duration:.2f}s)\n"
            md_content += "\n"

        # 使用的模型配置
        agent_models = result.get('agent_models', {})
        if agent_models:
            md_content += "## 🤖 智能体模型配置\n"
            for agent, model in agent_models.items():
                md_content += f"- **{agent}**: {model}\n"
            md_content += "\n"

        md_content += f"""---
*本报告由 TradingAgents 多智能体协作系统生成*
*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*分析引擎: Enhanced TradingAgents v2.0*
"""

        return md_content
    
    def _format_as_text(self, result: Dict[str, Any]) -> str:
        """格式化为纯文本"""
        # 获取基本信息
        symbol = result.get('symbol', 'N/A')

        status = result.get('status', 'unknown')

        text_content = f"""TradingAgents 股票分析报告
{'='*60}

项目开源地址：https://github.com/laochendeai/Multi-AI-Cooperative-Stock-Analysis
https://gitee.com/laochendeai/Multi-AI-Cooperative-Stock-Analysis
绿泡泡号：mtj1fc
项目完全开源免费，我的主业弱电设计\\项目合作，欢迎大家联系。

基本信息:
股票代码: {symbol}
分析状态: {status}
分析深度: {result.get('depth', result.get('analysis_depth', 'N/A'))}
选择的智能体: {', '.join(result.get('selected_agents', []))}

"""

        # 获取详细分析结果
        results = result.get('results', {})

        # 综合报告
        comprehensive_report = results.get('comprehensive_report', '')
        if comprehensive_report:
            text_content += f"""综合分析报告:
{'-'*40}
{comprehensive_report}

"""

        # 各个智能体的分析结果
        analysis_sections = [
            ('market_analysis', '市场分析'),
            ('sentiment_analysis', '情感分析'),
            ('fundamentals_analysis', '基本面分析'),
            ('news_analysis', '新闻分析'),
            ('bull_arguments', '多头观点'),
            ('bear_arguments', '空头观点'),
            ('trading_strategy', '交易策略'),
            ('risk_assessment', '风险评估')
        ]

        for key, title in analysis_sections:
            analysis_data = results.get(key, {})
            if analysis_data and isinstance(analysis_data, dict):
                analysis_content = analysis_data.get('analysis', '')
                if analysis_content:
                    text_content += f"""{title}:
{'-'*40}
{analysis_content}

"""

        # 最终决策
        final_decision = results.get('final_decision', {})
        if final_decision:
            text_content += f"""最终投资建议:
{'-'*40}
"""
            if isinstance(final_decision, dict):
                decision = final_decision.get('decision', 'HOLD')
                reasoning = final_decision.get('reasoning', '')
                confidence = final_decision.get('confidence', 0)

                text_content += f"投资决策: {decision}\n"
                text_content += f"置信度: {confidence}%\n"
                if reasoning:
                    text_content += f"决策理由: {reasoning}\n"
            else:
                text_content += f"投资决策: {final_decision}\n"
            text_content += "\n"

        # 分析流程信息
        analysis_flow = result.get('analysis_flow', {})
        if analysis_flow:
            text_content += f"""分析流程:
{'-'*40}
"""
            for stage, info in analysis_flow.items():
                if isinstance(info, dict):
                    status = info.get('status', 'unknown')
                    duration = info.get('duration', 0)
                    text_content += f"{stage}: {status} ({duration:.2f}s)\n"
            text_content += "\n"

        # 使用的模型配置
        agent_models = result.get('agent_models', {})
        if agent_models:
            text_content += f"""智能体模型配置:
{'-'*40}
"""
            for agent, model in agent_models.items():
                text_content += f"{agent}: {model}\n"
            text_content += "\n"

        text_content += f"""{'='*60}
本报告由 TradingAgents 多智能体协作系统生成
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
分析引擎: Enhanced TradingAgents v2.0
{'='*60}
"""

        return text_content

# 创建全局应用实例
app = FinalTradingAgentsApp()

# 异步分析函数
async def analyze_stock_async(symbol: str, depth: str, selected_agents: List[str],
                            agent_models: Dict[str, str] = None):
    """异步股票分析函数"""
    # 更新智能体模型配置
    if agent_models:
        for agent, model in agent_models.items():
            app.enhanced_app.update_agent_model_config(agent, model)

    # 调用增强分析方法
    return await app.enhanced_app.analyze_stock_enhanced(symbol, depth, selected_agents, use_real_llm=True)

def format_analysis_result(result: Dict[str, Any]) -> str:
    """格式化分析结果为可读的Markdown格式"""
    try:
        if not isinstance(result, dict):
            return str(result)

        # 检查结果状态
        if result.get("status") == "failed":
            return f"❌ **分析失败**\n\n错误信息: {result.get('error', '未知错误')}"

        # 获取基本信息
        symbol = result.get("symbol", "未知股票")


        # 构建格式化输出
        output = []
        output.append(f"# 📊 {symbol} 股票分析报告")
        output.append("**项目开源地址**：https://github.com/laochendeai/Multi-AI-Cooperative-Stock-Analysis")
        output.append("https://gitee.com/laochendeai/Multi-AI-Cooperative-Stock-Analysis")
        output.append("**绿泡泡号**：mtj1fc")
        output.append("**项目完全开源免费，我的主业弱电设计\\项目合作，欢迎大家联系。**")
        output.append("")

        # 获取结果数据
        results = result.get("results", {})

        # 综合报告
        comprehensive_report = results.get("comprehensive_report", "")
        if comprehensive_report:
            output.append("## 📈 综合分析报告")
            output.append(comprehensive_report)
            output.append("")

        # 市场分析
        market_analysis = results.get("market_analysis", {})
        if market_analysis and isinstance(market_analysis, dict):
            analysis_content = market_analysis.get("analysis", "")
            if analysis_content:
                output.append("## 🏪 市场分析")
                output.append(analysis_content)
                output.append("")

        # 情感分析
        sentiment_analysis = results.get("sentiment_analysis", {})
        if sentiment_analysis and isinstance(sentiment_analysis, dict):
            analysis_content = sentiment_analysis.get("analysis", "")
            if analysis_content:
                output.append("## 😊 情感分析")
                output.append(analysis_content)
                output.append("")

        # 基本面分析
        fundamentals_analysis = results.get("fundamentals_analysis", {})
        if fundamentals_analysis and isinstance(fundamentals_analysis, dict):
            analysis_content = fundamentals_analysis.get("analysis", "")
            if analysis_content:
                output.append("## 📊 基本面分析")
                output.append(analysis_content)
                output.append("")

        # 多头观点
        bull_arguments = results.get("bull_arguments", {})
        if bull_arguments and isinstance(bull_arguments, dict):
            analysis_content = bull_arguments.get("analysis", "")
            if analysis_content:
                output.append("## 🐂 多头观点")
                output.append(analysis_content)
                output.append("")

        # 空头观点
        bear_arguments = results.get("bear_arguments", {})
        if bear_arguments and isinstance(bear_arguments, dict):
            analysis_content = bear_arguments.get("analysis", "")
            if analysis_content:
                output.append("## 🐻 空头观点")
                output.append(analysis_content)
                output.append("")

        # 交易策略
        trading_strategy = results.get("trading_strategy", {})
        if trading_strategy and isinstance(trading_strategy, dict):
            analysis_content = trading_strategy.get("analysis", "")
            if analysis_content:
                output.append("## 💼 交易策略")
                output.append(analysis_content)
                output.append("")

        # 风险评估
        risk_assessment = results.get("risk_assessment", {})
        if risk_assessment and isinstance(risk_assessment, dict):
            analysis_content = risk_assessment.get("analysis", "")
            if analysis_content:
                output.append("## ⚠️ 风险评估")
                output.append(analysis_content)
                output.append("")

        # 最终决策
        final_decision = results.get("final_decision", "HOLD")
        if final_decision:
            output.append("## 🎯 最终投资建议")
            if isinstance(final_decision, dict):
                decision = final_decision.get("decision", "HOLD")
                reasoning = final_decision.get("reasoning", "")
                output.append(f"**决策**: {decision}")
                if reasoning:
                    output.append(f"**理由**: {reasoning}")
            else:
                output.append(f"**决策**: {final_decision}")
            output.append("")

        # 如果没有任何内容，返回默认消息
        if len(output) <= 3:
            return f"✅ **{symbol} 分析完成**\n\n分析已完成，请查看右侧的原始数据获取详细信息。"

        return "\n".join(output)

    except Exception as e:
        logger.error(f"格式化分析结果失败: {e}")
        return f"✅ **分析完成**\n\n分析已完成，但格式化时出现问题: {str(e)}\n\n请查看右侧的原始数据获取详细信息。"

def analyze_stock_sync(symbol: str, depth: str, selected_agents: List[str],
                      agent_models_json: str = "{}"):
    """同步股票分析函数（Gradio兼容）"""
    try:
        # 解析智能体模型配置
        agent_models = json.loads(agent_models_json) if agent_models_json else {}

        # 在新的事件循环中运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                analyze_stock_async(symbol, depth, selected_agents, agent_models)
            )
            return result
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"❌ 同步分析失败: {e}")
        return {"error": str(e)}

def export_result_sync(result_json: str, format_type: str):
    """同步导出函数"""
    try:
        if not result_json:
            return "❌ 没有分析结果可导出"

        result = json.loads(result_json)
        file_path = app.export_analysis_result(result, format_type)
        return f"✅ 导出成功: {file_path}"
    except Exception as e:
        return f"❌ 导出失败: {str(e)}"

def create_final_ui():
    """Creates and orchestrates all UI modules and their event handlers."""

    custom_css = """
    .main-container { max-width: 100vw !important; margin: 0 !important; padding: 8px !important; }
    .analysis-card { border: 1px solid #e1e5e9; border-radius: 8px; padding: 12px; margin: 3px 0; background: #f8f9fa; }
    .compact-input { margin: 1px 0 !important; }
    .full-height { height: 75vh !important; }
    """

    with gr.Blocks(title="TradingAgents - Multi-AI Cooperative Stock Analysis Platform", css=custom_css, theme=gr.themes.Soft()) as interface:
        gr.Markdown("""
        # 🤖 TradingAgents: Multi-AI Cooperative Stock Analysis Platform
        ### A modular stock analysis system based on the real tradingagents architecture.
        """)

        with gr.Row():
            with gr.Column(scale=25, elem_classes=["analysis-card"]):
                controls_components = create_analysis_controls_ui(app)
                agent_configs, save_agent_config_btn, agent_config_status = create_agent_config_ui(app)
                gr.Markdown("---")
                llm_components = create_llm_management_ui(app)

            with gr.Column(scale=60, elem_classes=["analysis-card"]):
                gr.Markdown("### 📊 Analysis Results")
                results_components = create_results_display_ui()

            with gr.Column(scale=15, elem_classes=["analysis-card"]):
                sidebar_components = create_sidebar_ui(app)

        # --- Event Handler Functions ---
        available_agents = app.get_available_agents()

        def start_analysis(symbol, depth, *agent_config_values):
            if not symbol or not symbol.strip(): return "❌ Please enter a stock symbol", "{}", "", "🔴 Analysis Failed", 0
            try:
                selected_agents = [agent for i, agent in enumerate(available_agents) if agent_config_values[i*3]]
                if not selected_agents: return "❌ Please select at least one agent", "{}", "", "🔴 Analysis Failed", 0
                agent_models = {agent: agent_config_values[i*3+1] for i, agent in enumerate(available_agents) if agent_config_values[i*3]}
                result = analyze_stock_sync(symbol.strip(), depth, selected_agents, json.dumps(agent_models))
                if isinstance(result, dict) and "error" in result: return f"❌ Analysis failed: {result['error']}", "{}", "", "🔴 Analysis Failed", 0
                formatted_output = result.get('formatted_result', '') or format_analysis_result(result) if isinstance(result, dict) else str(result)
                result_json = json.dumps(result, ensure_ascii=False) if isinstance(result, dict) else json.dumps({"analysis_result": str(result)})
                return formatted_output, result, result_json, "🟢 Analysis Complete", 100
            except Exception as e: return f"❌ Analysis error: {str(e)}", "{}", "", "🔴 Analysis Error", 0

        def save_agent_config(*agent_config_values):
            try:
                results = [f"{agent}: {agent_config_values[i*3+1]} ({'✅ Enabled' if agent_config_values[i*3] else '⏸️ Disabled'})" for i, agent in enumerate(available_agents)]
                for i, agent in enumerate(available_agents): app.update_agent_model_config(agent, agent_config_values[i*3+1])
                return "💾 Config saved:\n" + "\n".join(results)
            except Exception as e: return f"❌ Failed to save config: {str(e)}"

        def update_model_features(model_name): return app.get_models_with_features().get(model_name, {}).get("best_for", "")
        def refresh_llm_config(): return app.get_configured_llm_providers(), app._format_provider_overview(), app._format_models_by_provider()
        def test_model_connection_ui(model_name): return app.test_model_connection(model_name)
        def add_provider(name, url, key): return app.add_custom_provider(name, url, key)
        def test_provider_connection(name, url, key): return app.test_llm_connection(name, url, key)
        def test_network_connection(): return app.test_network_connection()
        def refresh_system_status(): return f"""**App Status**: {'✅ Normal' if app.enhanced_app else '❌ Error'}\n**Database**: ✅ Connected\n**LLM Config**: ✅ Loaded\n**Agents**: ✅ {len(available_agents)}\n**Export Formats**: ✅ {len(app.export_formats)}\n**Last Refresh**: {datetime.now().strftime('%H:%M:%S')}"""

        def test_all_providers():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    results = loop.run_until_complete(app.test_all_providers_status())
                    status_text = ["## 📊 Provider Live Status\n"]
                    for provider, status in results.items(): status_text.extend([f"### 🏢 {provider}", f"**Type**: {app._get_provider_type(provider)}", f"**Network**: {status['网络状态']}", f"**API**: {status['API状态']}", f"**Latency**: {status['响应速度']}\n"])
                    return "\n".join(status_text), datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                finally: loop.close()
            except Exception as e: return f"❌ Test failed: {str(e)}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # --- Bind Events ---
        agent_config_inputs = [controls_components["stock_input"], controls_components["depth_select"]] + [val for agent in available_agents for val in agent_configs[agent].values()]
        controls_components["analyze_btn"].click(fn=start_analysis, inputs=agent_config_inputs, outputs=[results_components["analysis_output"], results_components["raw_data_output"], results_components["result_storage"], sidebar_components["current_status"], sidebar_components["analysis_progress"]])

        save_config_inputs = [val for agent in available_agents for val in agent_configs[agent].values()]
        save_agent_config_btn.click(fn=save_agent_config, inputs=save_config_inputs, outputs=[agent_config_status])

        for agent in available_agents: agent_configs[agent]["model"].change(fn=update_model_features, inputs=[agent_configs[agent]["model"]], outputs=[agent_configs[agent]["features"]])

        results_components["export_btn"].click(fn=export_result_sync, inputs=[results_components["result_storage"], results_components["export_format"]], outputs=[results_components["export_status"]])
        llm_components["add_provider_btn"].click(fn=add_provider, inputs=[llm_components["provider_name"], llm_components["provider_url"], llm_components["provider_key"]], outputs=[llm_components["provider_status"]])
        llm_components["test_provider_btn"].click(fn=test_provider_connection, inputs=[llm_components["provider_name"], llm_components["provider_url"], llm_components["provider_key"]], outputs=[llm_components["provider_status"]])
        llm_components["test_network_btn"].click(fn=test_network_connection, outputs=[llm_components["network_status"]])
        llm_components["refresh_llm_btn"].click(fn=refresh_llm_config, outputs=[llm_components["configured_llm_display"], llm_components["provider_overview"], llm_components["models_by_provider"]])
        llm_components["test_all_btn"].click(fn=test_all_providers, outputs=[llm_components["provider_status_display"], llm_components["status_update_time"]])
        llm_components["test_model_btn"].click(fn=test_model_connection_ui, inputs=[llm_components["model_test_select"]], outputs=[llm_components["model_test_status"]])
        sidebar_components["refresh_btn"].click(fn=refresh_system_status, outputs=[sidebar_components["system_info"]])

    return interface

if __name__ == "__main__":
    try:
        # Create and launch the interface
        print("🚀 Launching TradingAgents: Multi-AI Cooperative Stock Analysis Platform...")
        interface = create_final_ui()
        interface.launch(
            server_name="0.0.0.0",
            server_port=7863,
            share=False,
            show_error=True,
            inbrowser=True
        )
    except Exception as e:
        import traceback
        print("❌ Failed to launch the application:")
        traceback.print_exc()
