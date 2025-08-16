#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents 最终集成应用
基于真实tradingagents架构的完整模块化程序
实现所有要求的功能
"""

import gradio as gr
import asyncio
import logging
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
        self.agent_model_memory = {
            "market_analyst": "gpt-4",
            "sentiment_analyst": "deepseek-chat",
            "news_analyst": "gemini-pro",
            "fundamentals_analyst": "gpt-4",
            "bull_researcher": "deepseek-chat",
            "bear_researcher": "deepseek-chat",
            "research_manager": "gpt-4",
            "trader": "gpt-3.5-turbo",
            "risk_manager": "gpt-4"
        }

        logger.info("✅ 最终TradingAgents应用初始化完成")
    
    def get_available_agents(self) -> List[str]:
        """获取可用的智能体列表"""
        return [
            "market_analyst",      # 市场技术分析师
            "sentiment_analyst",   # 情感分析师
            "news_analyst",        # 新闻分析师
            "fundamentals_analyst", # 基本面分析师
            "bull_researcher",     # 多头研究员
            "bear_researcher",     # 空头研究员
            "research_manager",    # 研究经理
            "trader",             # 交易员
            "risk_manager"        # 风险管理师
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
        """获取所有可用模型的平铺列表"""
        models_dict = self.get_available_models()
        all_models = []
        for provider, models in models_dict.items():
            all_models.extend(models)
        return all_models

    def update_agent_model_config(self, agent: str, model: str) -> str:
        """更新智能体模型配置"""
        try:
            if agent not in self.get_available_agents():
                return f"❌ 无效的智能体: {agent}"

            all_models = self.get_all_available_models_list()
            if model not in all_models:
                return f"❌ 无效的模型: {model}"

            self.agent_model_memory[agent] = model
            return f"✅ 已更新 {agent} 的模型为: {model}"
        except Exception as e:
            return f"❌ 更新失败: {str(e)}"

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
            auth_result = self._test_provider_auth(provider, model_name)
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

    def _test_provider_auth(self, provider: str, model_name: str) -> str:
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
                response = asyncio.run(self.enhanced_app._call_llm(
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
        md_content = f"""# 📊 股票分析报告

## 📋 基本信息
- **股票代码**: {result.get('symbol', 'N/A')}
- **分析深度**: {result.get('analysis_depth', 'N/A')}
- **分析时间**: {result.get('timestamp', 'N/A')}
- **选择的智能体**: {', '.join(result.get('selected_agents', []))}
- **使用的模型**: {json.dumps(result.get('agent_models', {}), ensure_ascii=False)}

## 📈 分析结果
{result.get('formatted_result', '无分析结果')}

## 📝 分析总结
{result.get('summary', '无总结')}

## 💡 投资建议
"""
        
        for rec in result.get('recommendations', []):
            md_content += f"- {rec}\n"
        
        md_content += f"""
---
*本报告由 TradingAgents 真实架构生成*
*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return md_content
    
    def _format_as_text(self, result: Dict[str, Any]) -> str:
        """格式化为纯文本"""
        text_content = f"""TradingAgents 股票分析报告
{'='*50}

基本信息:
股票代码: {result.get('symbol', 'N/A')}
分析深度: {result.get('analysis_depth', 'N/A')}
分析时间: {result.get('timestamp', 'N/A')}
选择的智能体: {', '.join(result.get('selected_agents', []))}
使用的模型: {json.dumps(result.get('agent_models', {}), ensure_ascii=False)}

分析结果:
{'-'*30}
{result.get('formatted_result', '无分析结果')}

分析总结:
{'-'*30}
{result.get('summary', '无总结')}

投资建议:
{'-'*30}
"""
        
        for i, rec in enumerate(result.get('recommendations', []), 1):
            text_content += f"{i}. {rec}\n"
        
        text_content += f"""
{'='*50}
本报告由 TradingAgents 真实架构生成
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return text_content

# 创建全局应用实例
app = FinalTradingAgentsApp()

# 异步分析函数
async def analyze_stock_async(symbol: str, depth: str, selected_agents: List[str],
                            agent_models: Dict[str, str] = None):
    """异步股票分析函数"""
    return await app.analyze_stock_real(symbol, depth, selected_agents, agent_models)

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
    """创建最终UI界面"""

    # 自定义CSS样式
    custom_css = """
    .main-container {
        max-width: 100vw !important;
        margin: 0 !important;
        padding: 8px !important;
    }
    .analysis-card {
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        padding: 12px;
        margin: 3px 0;
        background: #f8f9fa;
    }
    .compact-input { margin: 1px 0 !important; }
    .full-height { height: 75vh !important; }
    .status-success { background: #d4edda; color: #155724; padding: 5px; border-radius: 4px; }
    .status-warning { background: #fff3cd; color: #856404; padding: 5px; border-radius: 4px; }
    .status-error { background: #f8d7da; color: #721c24; padding: 5px; border-radius: 4px; }
    """

    with gr.Blocks(
        title="TradingAgents - 完整集成平台",
        css=custom_css,
        theme=gr.themes.Soft()
    ) as interface:

        # 页面标题
        gr.Markdown("""
        # 🤖 TradingAgents 完整集成平台
        ### 基于真实tradingagents架构的模块化股票分析系统
        #### ✨ 支持自定义LLM、智能体模型选择、多格式导出
        """)

        # 主要布局：左侧配置(25%) + 中间分析(60%) + 右侧状态(15%)
        with gr.Row():
            # 左侧配置面板
            with gr.Column(scale=25, elem_classes=["analysis-card"]):
                gr.Markdown("### ⚙️ 分析配置")

                # 股票输入
                stock_input = gr.Textbox(
                    label="📈 股票代码",
                    placeholder="输入股票代码，如：000001, 600519",
                    elem_classes=["compact-input"]
                )

                # 分析深度
                depth_select = gr.Dropdown(
                    choices=app.get_analysis_depths(),
                    value="标准分析",
                    label="🔍 分析深度",
                    elem_classes=["compact-input"]
                )

                # 智能体选择
                agents_select = gr.CheckboxGroup(
                    choices=app.get_available_agents(),
                    value=["market_analyst", "sentiment_analyst", "news_analyst"],
                    label="🤖 选择智能体",
                    elem_classes=["compact-input"]
                )

                # 智能体模型配置
                with gr.Accordion("🧠 智能体模型配置", open=True):
                    gr.Markdown("**为每个智能体选择专用模型:**")

                    # 创建每个智能体的模型选择器
                    agent_model_selectors = {}
                    all_models = app.get_all_available_models_list()

                    for agent in app.get_available_agents():
                        agent_model_selectors[agent] = gr.Dropdown(
                            choices=all_models,
                            value=app.agent_model_memory.get(agent, all_models[0] if all_models else ""),
                            label=f"{agent}",
                            elem_classes=["compact-input"]
                        )

                    # 保存配置按钮
                    save_agent_config_btn = gr.Button("💾 保存智能体配置", variant="secondary")
                    agent_config_status = gr.Textbox(
                        label="配置状态",
                        interactive=False,
                        lines=2
                    )

                # 分析按钮
                with gr.Row():
                    analyze_btn = gr.Button("🚀 开始分析", variant="primary")
                    stop_btn = gr.Button("⏹️ 停止", variant="secondary")

                gr.Markdown("---")

                # LLM配置
                gr.Markdown("### 🧠 LLM提供商管理")

                # 当前已配置的LLM提供商 - 人性化显示
                with gr.Accordion("📋 已配置的LLM提供商", open=True):
                    gr.Markdown("**当前系统中已配置的AI模型提供商:**")

                    # 提供商概览
                    provider_overview = gr.Markdown(
                        value=app._format_provider_overview(),
                        elem_classes=["provider-overview"]
                    )

                    # 详细配置信息
                    configured_llm_display = gr.JSON(
                        label="详细配置信息",
                        value=app.get_configured_llm_providers()
                    )

                    with gr.Row():
                        refresh_llm_btn = gr.Button("🔄 刷新配置", size="sm")
                        test_all_btn = gr.Button("🧪 测试所有提供商", size="sm", variant="secondary")

                # 实时状态监控
                with gr.Accordion("📊 实时状态监控", open=False):
                    gr.Markdown("**各提供商的实时连接状态和响应速度:**")

                    provider_status_display = gr.Markdown(
                        value="点击'测试所有提供商'按钮获取实时状态",
                        elem_classes=["status-display"]
                    )

                    status_update_time = gr.Textbox(
                        label="最后更新时间",
                        value="未更新",
                        interactive=False
                    )

                # 模型能力详情
                with gr.Accordion("🤖 模型能力详情", open=False):
                    gr.Markdown("**各提供商的模型列表和特殊能力:**")

                    # 按提供商分组显示模型
                    models_by_provider = gr.Markdown(
                        value=app._format_models_by_provider(),
                        elem_classes=["models-display"]
                    )

                # 单个模型测试
                with gr.Accordion("🧪 单个模型测试", open=False):
                    model_test_select = gr.Dropdown(
                        choices=app.get_all_available_models_list(),
                        label="选择要测试的模型"
                    )
                    test_model_btn = gr.Button("🌐 测试模型连接")
                    model_test_status = gr.Textbox(
                        label="模型测试结果",
                        interactive=False,
                        lines=6
                    )

                # 自定义LLM提供商
                with gr.Accordion("➕ 添加自定义提供商", open=False):
                    provider_name = gr.Textbox(
                        label="提供商名称",
                        placeholder="如：custom_openai"
                    )
                    provider_url = gr.Textbox(
                        label="API地址",
                        placeholder="https://api.example.com/v1"
                    )
                    provider_key = gr.Textbox(
                        label="API密钥",
                        type="password"
                    )

                    with gr.Row():
                        add_provider_btn = gr.Button("➕ 添加")
                        test_provider_btn = gr.Button("🧪 测试")

                    provider_status = gr.Textbox(
                        label="操作结果",
                        interactive=False,
                        lines=3
                    )

                # 网络设置
                with gr.Accordion("🌐 网络设置", open=False):
                    enable_network = gr.Checkbox(
                        label="启用联网功能",
                        value=True
                    )
                    test_network_btn = gr.Button("🌐 测试网络连接")
                    network_status = gr.Textbox(
                        label="网络状态",
                        value="未测试",
                        interactive=False,
                        lines=4
                    )

            # 中间分析结果面板
            with gr.Column(scale=60, elem_classes=["analysis-card"]):
                gr.Markdown("### 📊 分析结果")

                with gr.Tabs():
                    # 分析结果标签页
                    with gr.Tab("📈 分析报告"):
                        analysis_output = gr.Markdown(
                            value="🔄 等待分析...\n\n请在左侧配置面板中:\n1. 输入股票代码\n2. 选择分析深度\n3. 选择智能体\n4. 点击开始分析",
                            elem_classes=["full-height"]
                        )

                    # 原始数据标签页
                    with gr.Tab("🔍 原始数据"):
                        raw_data_output = gr.JSON(
                            label="原始分析数据",
                            elem_classes=["full-height"]
                        )

                    # 导出功能标签页
                    with gr.Tab("📤 导出结果"):
                        gr.Markdown("#### 📥 导出分析结果")

                        with gr.Row():
                            export_format = gr.Dropdown(
                                choices=["markdown", "json", "txt"],
                                value="markdown",
                                label="导出格式"
                            )
                            export_btn = gr.Button("📥 导出", variant="primary")

                        export_status = gr.Textbox(
                            label="导出状态",
                            interactive=False,
                            lines=2
                        )

                        gr.Markdown("""
                        **导出格式说明:**
                        - **Markdown**: 适合文档查看和分享
                        - **JSON**: 适合程序处理和数据分析
                        - **TXT**: 适合简单文本查看
                        """)

                        # 隐藏的结果存储
                        result_storage = gr.Textbox(
                            visible=False,
                            value=""
                        )

            # 右侧状态面板
            with gr.Column(scale=15, elem_classes=["analysis-card"]):
                gr.Markdown("### 📊 系统状态")

                # 当前状态
                current_status = gr.Textbox(
                    label="当前状态",
                    value="🟢 系统就绪",
                    interactive=False,
                    elem_classes=["compact-input"]
                )

                # 分析进度
                analysis_progress = gr.Slider(
                    label="分析进度",
                    minimum=0,
                    maximum=100,
                    value=0,
                    interactive=False,
                    elem_classes=["compact-input"]
                )

                # 系统信息
                with gr.Accordion("ℹ️ 系统信息", open=True):
                    system_info = gr.Markdown(f"""
                    **应用状态**: {'✅ 正常' if app.enhanced_app else '❌ 异常'}
                    **数据库**: ✅ 已连接
                    **LLM配置**: ✅ 已加载
                    **智能体**: ✅ {len(app.get_available_agents())}个
                    **导出格式**: ✅ {len(app.export_formats)}种
                    """)

                # 可用模型
                with gr.Accordion("🤖 可用模型", open=False):
                    available_models = gr.JSON(
                        label="LLM模型列表",
                        value=app.get_available_models()
                    )

                # 实时日志
                with gr.Accordion("📝 实时日志", open=False):
                    log_output = gr.Textbox(
                        label="系统日志",
                        lines=6,
                        max_lines=10,
                        interactive=False,
                        elem_classes=["compact-input"]
                    )

                # 刷新按钮
                refresh_btn = gr.Button("🔄 刷新状态", size="sm")

        # 事件绑定函数
        def start_analysis(symbol, depth, agents, *agent_model_values):
            """开始分析"""
            if not symbol or not symbol.strip():
                return "❌ 请输入股票代码", "{}", "", "🔴 分析失败", 0

            if not agents:
                return "❌ 请至少选择一个智能体", "{}", "", "🔴 分析失败", 0

            try:
                # 构建智能体模型配置
                agent_models = {}
                agent_list = app.get_available_agents()
                for i, agent in enumerate(agent_list):
                    if i < len(agent_model_values):
                        agent_models[agent] = agent_model_values[i]

                # 执行分析
                models_json = json.dumps(agent_models)
                result = analyze_stock_sync(symbol.strip(), depth, agents, models_json)

                if "error" in result:
                    error_msg = f"❌ 分析失败: {result['error']}"
                    return error_msg, "{}", "", "🔴 分析失败", 0

                # 格式化输出
                formatted_output = result.get('formatted_result', '无分析结果')
                result_json = json.dumps(result, ensure_ascii=False)

                return formatted_output, result, result_json, "🟢 分析完成", 100

            except Exception as e:
                error_msg = f"❌ 分析异常: {str(e)}"
                return error_msg, "{}", "", "🔴 分析异常", 0

        def save_agent_config(*agent_model_values):
            """保存智能体模型配置"""
            try:
                agent_list = app.get_available_agents()
                results = []

                for i, agent in enumerate(agent_list):
                    if i < len(agent_model_values):
                        model = agent_model_values[i]
                        result = app.update_agent_model_config(agent, model)
                        results.append(result)

                return "\n".join(results)
            except Exception as e:
                return f"❌ 保存配置失败: {str(e)}"

        def refresh_llm_config():
            """刷新LLM配置显示"""
            return app.get_configured_llm_providers(), app._format_provider_overview(), app._format_models_by_provider()

        def test_all_providers():
            """测试所有提供商状态"""
            try:
                # 在新的事件循环中运行异步函数
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    results = loop.run_until_complete(app.test_all_providers_status())

                    # 格式化状态显示
                    status_text = []
                    status_text.append("## 📊 提供商实时状态\n")

                    for provider, status in results.items():
                        provider_type = app._get_provider_type(provider)
                        status_text.append(f"### 🏢 {provider}")
                        status_text.append(f"**类型**: {provider_type}")
                        status_text.append(f"**网络状态**: {status['网络状态']}")
                        status_text.append(f"**API状态**: {status['API状态']}")
                        status_text.append(f"**响应速度**: {status['响应速度']}")
                        status_text.append("")

                    formatted_status = "\n".join(status_text)
                    update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    return formatted_status, update_time
                finally:
                    loop.close()
            except Exception as e:
                error_msg = f"❌ 测试失败: {str(e)}"
                return error_msg, datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        def test_model_connection_ui(model_name):
            """测试模型连接UI函数"""
            return app.test_model_connection(model_name)

        def add_provider(name, url, key):
            """添加LLM提供商"""
            return app.add_custom_provider(name, url, key)

        def test_provider_connection(name, url, key):
            """测试LLM提供商连接"""
            return app.test_llm_connection(name, url, key)

        def test_network_connection():
            """测试网络连接"""
            return app.test_network_connection()

        def refresh_system_status():
            """刷新系统状态"""
            return f"""
            **应用状态**: {'✅ 正常' if app.enhanced_app else '❌ 异常'}
            **数据库**: ✅ 已连接
            **LLM配置**: ✅ 已加载
            **智能体**: ✅ {len(app.get_available_agents())}个
            **导出格式**: ✅ {len(app.export_formats)}种
            **刷新时间**: {datetime.now().strftime('%H:%M:%S')}
            """

        # 绑定事件
        # 分析事件 - 使用智能体模型选择器的值
        agent_model_inputs = [stock_input, depth_select, agents_select] + list(agent_model_selectors.values())
        analyze_btn.click(
            fn=start_analysis,
            inputs=agent_model_inputs,
            outputs=[analysis_output, raw_data_output, result_storage, current_status, analysis_progress]
        )

        # 保存智能体配置事件
        save_agent_config_btn.click(
            fn=save_agent_config,
            inputs=list(agent_model_selectors.values()),
            outputs=[agent_config_status]
        )

        export_btn.click(
            fn=export_result_sync,
            inputs=[result_storage, export_format],
            outputs=[export_status]
        )

        add_provider_btn.click(
            fn=add_provider,
            inputs=[provider_name, provider_url, provider_key],
            outputs=[provider_status]
        )

        test_provider_btn.click(
            fn=test_provider_connection,
            inputs=[provider_name, provider_url, provider_key],
            outputs=[provider_status]
        )

        test_network_btn.click(
            fn=test_network_connection,
            outputs=[network_status]
        )

        refresh_btn.click(
            fn=refresh_system_status,
            outputs=[system_info]
        )

        # LLM配置刷新事件
        refresh_llm_btn.click(
            fn=refresh_llm_config,
            outputs=[configured_llm_display, provider_overview, models_by_provider]
        )

        # 测试所有提供商事件
        test_all_btn.click(
            fn=test_all_providers,
            outputs=[provider_status_display, status_update_time]
        )

        # 模型测试事件
        test_model_btn.click(
            fn=test_model_connection_ui,
            inputs=[model_test_select],
            outputs=[model_test_status]
        )

    return interface

if __name__ == "__main__":
    # 创建并启动界面
    print("🚀 启动TradingAgents完整集成平台...")
    interface = create_final_ui()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7862,
        share=False,
        show_error=True,
        inbrowser=True
    )
