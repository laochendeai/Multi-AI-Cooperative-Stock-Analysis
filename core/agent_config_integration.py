#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体配置集成模块 - 将新的智能体管理功能集成到现有应用中
"""

import gradio as gr
import logging
from typing import Dict, Any, List, Optional, Tuple
from .enhanced_llm_manager import EnhancedLLMManager
from .agent_model_manager import AgentModelManager

logger = logging.getLogger(__name__)

class AgentConfigIntegration:
    """智能体配置集成器"""
    
    def __init__(self, enhanced_app=None):
        self.enhanced_app = enhanced_app
        self.llm_manager = EnhancedLLMManager()
        self.agent_manager = AgentModelManager()
        
        # 如果有现有应用，同步配置
        if enhanced_app:
            self.sync_with_existing_app()
    
    def sync_with_existing_app(self):
        """与现有应用同步配置"""
        try:
            # 同步LLM配置
            for provider, api_key in self.enhanced_app.llm_config.items():
                self.llm_manager.llm_config[provider] = api_key
            
            # 同步自定义提供商
            for provider, config in self.enhanced_app.custom_llm_providers.items():
                if provider not in self.llm_manager.custom_providers:
                    self.llm_manager.custom_providers[provider] = {
                        "name": config.get("name", provider),
                        "base_url": config.get("base_url", ""),
                        "api_key_header": "Authorization",
                        "api_key_prefix": "Bearer ",
                        "models": [{"id": config.get("model", "default"), "name": config.get("model", "default"), "type": "chat", "context_length": 4096}],
                        "request_format": "openai_compatible"
                    }
            
            # 同步智能体模型配置
            for agent_id, model_config in self.enhanced_app.agent_model_config.items():
                self.agent_manager.agent_model_config[agent_id] = model_config
            
            logger.info("配置同步完成")
        except Exception as e:
            logger.error(f"配置同步失败: {e}")
    
    def create_agent_selection_interface(self) -> Tuple[gr.Dropdown, gr.Dropdown, gr.Dropdown, gr.Button, gr.Textbox]:
        """创建智能体选择界面组件"""
        with gr.Row():
            with gr.Column(scale=1):
                agent_category = gr.Dropdown(
                    choices=[
                        ("分析师团队", "analysts"),
                        ("研究团队", "researchers"), 
                        ("风险管理", "risk_management"),
                        ("交易团队", "trading")
                    ],
                    label="智能体类别",
                    value="analysts"
                )
                
                agent_selector = gr.Dropdown(
                    label="选择智能体",
                    choices=[]
                )
            
            with gr.Column(scale=1):
                provider_selector = gr.Dropdown(
                    label="LLM提供商",
                    choices=[]
                )
                
                model_selector = gr.Dropdown(
                    label="模型",
                    choices=[]
                )
            
            with gr.Column(scale=1):
                update_btn = gr.Button("🔄 更新配置", variant="primary")
                
                status_display = gr.Textbox(
                    label="状态",
                    interactive=False,
                    lines=3
                )
        
        return agent_category, agent_selector, provider_selector, model_selector, update_btn, status_display
    
    def create_batch_config_interface(self) -> Tuple[gr.Dataframe, gr.Button, gr.Button, gr.Textbox]:
        """创建批量配置界面"""
        with gr.Column():
            gr.Markdown("### 批量智能体配置")
            
            config_table = gr.Dataframe(
                headers=["智能体", "当前提供商", "当前模型", "新提供商", "新模型"],
                label="智能体配置表",
                interactive=True,
                wrap=True
            )
            
            with gr.Row():
                load_current_btn = gr.Button("📋 加载当前配置", variant="secondary")
                batch_update_btn = gr.Button("🔄 批量更新", variant="primary")
            
            batch_status = gr.Textbox(
                label="批量操作状态",
                interactive=False,
                lines=5
            )
        
        return config_table, load_current_btn, batch_update_btn, batch_status
    
    def create_compatibility_checker(self) -> Tuple[gr.Dropdown, gr.Dropdown, gr.Dropdown, gr.Button, gr.JSON]:
        """创建兼容性检查器"""
        with gr.Column():
            gr.Markdown("### 模型兼容性检查")
            
            with gr.Row():
                check_agent = gr.Dropdown(
                    label="智能体",
                    choices=[]
                )
                
                check_provider = gr.Dropdown(
                    label="提供商",
                    choices=[]
                )
                
                check_model = gr.Dropdown(
                    label="模型",
                    choices=[]
                )
                
                check_btn = gr.Button("🔍 检查兼容性", variant="secondary")
            
            compatibility_result = gr.JSON(
                label="兼容性检查结果",
                value={}
            )
        
        return check_agent, check_provider, check_model, check_btn, compatibility_result
    
    def get_agent_choices(self, category: str) -> List[Tuple[str, str]]:
        """获取指定类别的智能体选择列表"""
        try:
            agents = self.agent_manager.get_all_agents().get(category, {})
            return [(f"{info['name']} ({agent_id})", agent_id) for agent_id, info in agents.items()]
        except Exception as e:
            logger.error(f"获取智能体选择列表失败: {e}")
            return []
    
    def get_provider_choices(self) -> List[str]:
        """获取提供商选择列表"""
        try:
            providers = self.llm_manager.get_all_providers()
            configured_providers = []
            
            # 内置提供商
            for provider_id, info in providers["built_in"].items():
                if info["configured"]:
                    configured_providers.append(provider_id)
            
            # 自定义提供商
            for provider_id, info in providers["custom"].items():
                if info["configured"]:
                    configured_providers.append(provider_id)
            
            return configured_providers
        except Exception as e:
            logger.error(f"获取提供商选择列表失败: {e}")
            return []
    
    def get_model_choices(self, provider: str) -> List[Tuple[str, str]]:
        """获取指定提供商的模型选择列表"""
        try:
            models = self.llm_manager.get_provider_models(provider)
            return [(f"{model['name']} ({model['id']})", model['id']) for model in models]
        except Exception as e:
            logger.error(f"获取模型选择列表失败: {e}")
            return []
    
    def update_agent_model(self, agent_id: str, provider: str, model: str) -> str:
        """更新智能体模型配置"""
        try:
            result = self.agent_manager.update_agent_model(agent_id, provider, model)
            
            # 同步到现有应用
            if self.enhanced_app and result["status"] == "success":
                self.enhanced_app.agent_model_config[agent_id] = f"{provider}:{model}"
                self.enhanced_app.save_agent_model_config()
            
            if result["status"] == "success":
                return f"✅ {result['message']}"
            else:
                return f"❌ {result['message']}"
        except Exception as e:
            logger.error(f"更新智能体模型失败: {e}")
            return f"❌ 更新失败: {str(e)}"
    
    def load_current_config_table(self) -> List[List[str]]:
        """加载当前配置到表格"""
        try:
            agents = self.agent_manager.get_all_agents()
            table_data = []
            
            for category, category_agents in agents.items():
                for agent_id, agent_info in category_agents.items():
                    current_model = agent_info.get("current_model", "未配置")
                    if ":" in current_model:
                        current_provider, current_model_id = current_model.split(":", 1)
                    else:
                        current_provider, current_model_id = "未配置", "未配置"
                    
                    table_data.append([
                        f"{agent_info['name']} ({agent_id})",
                        current_provider,
                        current_model_id,
                        "",  # 新提供商
                        ""   # 新模型
                    ])
            
            return table_data
        except Exception as e:
            logger.error(f"加载当前配置失败: {e}")
            return []
    
    def batch_update_agents(self, table_data: List[List[str]]) -> str:
        """批量更新智能体配置"""
        try:
            updates = []
            
            for row in table_data:
                if len(row) >= 5:
                    agent_display = row[0]
                    new_provider = row[3]
                    new_model = row[4]
                    
                    # 提取智能体ID
                    if "(" in agent_display and ")" in agent_display:
                        agent_id = agent_display.split("(")[-1].split(")")[0]
                    else:
                        continue
                    
                    # 如果有新配置，添加到更新列表
                    if new_provider and new_model:
                        updates.append({
                            "agent_id": agent_id,
                            "provider": new_provider,
                            "model": new_model
                        })
            
            if not updates:
                return "❌ 没有找到需要更新的配置"
            
            result = self.agent_manager.batch_update_agents(updates)
            
            # 同步到现有应用
            if self.enhanced_app and result["status"] in ["success", "partial"]:
                for update in updates:
                    agent_id = update["agent_id"]
                    provider = update["provider"]
                    model = update["model"]
                    self.enhanced_app.agent_model_config[agent_id] = f"{provider}:{model}"
                
                self.enhanced_app.save_agent_model_config()
            
            if result["status"] == "success":
                return f"✅ 批量更新成功: {result['message']}"
            elif result["status"] == "partial":
                error_details = "\n".join(result.get("errors", []))
                return f"⚠️ 部分更新成功: {result['message']}\n错误详情:\n{error_details}"
            else:
                return f"❌ 批量更新失败: {result['message']}"
                
        except Exception as e:
            logger.error(f"批量更新失败: {e}")
            return f"❌ 批量更新失败: {str(e)}"
    
    def check_model_compatibility(self, agent_id: str, provider: str, model: str) -> Dict[str, Any]:
        """检查模型兼容性"""
        try:
            if not all([agent_id, provider, model]):
                return {"error": "请选择智能体、提供商和模型"}
            
            # 获取所有可用模型的详细信息
            available_models = {}
            all_providers = self.llm_manager.get_all_providers()
            
            for provider_id in list(all_providers["built_in"].keys()) + list(all_providers["custom"].keys()):
                available_models[provider_id] = self.llm_manager.get_provider_models(provider_id)
            
            result = self.agent_manager.validate_model_compatibility(agent_id, provider, model, available_models)
            
            if result["compatible"]:
                return {
                    "compatible": True,
                    "score": result["score"],
                    "recommendation": result["recommendation"],
                    "model_info": result["model_info"],
                    "agent_info": self.agent_manager.get_agent_info(agent_id)
                }
            else:
                return {
                    "compatible": False,
                    "reason": result["reason"]
                }
                
        except Exception as e:
            logger.error(f"兼容性检查失败: {e}")
            return {"error": f"检查失败: {str(e)}"}
    
    def get_agent_recommendations(self, agent_id: str) -> List[Dict[str, Any]]:
        """获取智能体的推荐模型"""
        try:
            if not agent_id:
                return []
            
            # 获取所有可用模型的详细信息
            available_models = {}
            all_providers = self.llm_manager.get_all_providers()
            
            for provider_id in list(all_providers["built_in"].keys()) + list(all_providers["custom"].keys()):
                available_models[provider_id] = self.llm_manager.get_provider_models(provider_id)
            
            return self.agent_manager.get_recommended_models(agent_id, available_models)
            
        except Exception as e:
            logger.error(f"获取推荐模型失败: {e}")
            return []
    
    def create_recommendations_display(self, agent_id: str) -> List[List[str]]:
        """创建推荐模型显示数据"""
        try:
            recommendations = self.get_agent_recommendations(agent_id)
            
            data = []
            for rec in recommendations[:10]:  # 显示前10个推荐
                data.append([
                    rec["provider"],
                    rec["model_name"],
                    f"{rec['score']:.2f}",
                    rec["recommendation"]
                ])
            
            return data
        except Exception as e:
            logger.error(f"创建推荐显示失败: {e}")
            return []
