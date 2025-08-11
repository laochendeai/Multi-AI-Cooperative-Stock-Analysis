#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM配置界面组件 - 提供完整的LLM和智能体配置界面
"""

import gradio as gr
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from .enhanced_llm_manager import EnhancedLLMManager
from .agent_model_manager import AgentModelManager

logger = logging.getLogger(__name__)

class LLMConfigUI:
    """LLM配置界面管理器"""
    
    def __init__(self):
        self.llm_manager = EnhancedLLMManager()
        self.agent_manager = AgentModelManager()
    
    def create_llm_config_interface(self) -> gr.Blocks:
        """创建LLM配置界面"""
        with gr.Blocks(title="LLM配置管理") as interface:
            gr.Markdown("# 🤖 LLM配置管理")
            
            with gr.Tabs():
                # Tab 1: 内置提供商配置
                with gr.TabItem("🏢 内置提供商"):
                    self._create_builtin_providers_tab()
                
                # Tab 2: 自定义提供商
                with gr.TabItem("➕ 自定义提供商"):
                    self._create_custom_providers_tab()
                
                # Tab 3: 智能体模型配置
                with gr.TabItem("🤖 智能体配置"):
                    self._create_agent_config_tab()
                
                # Tab 4: 模型测试
                with gr.TabItem("🧪 连接测试"):
                    self._create_test_tab()
        
        return interface
    
    def _create_builtin_providers_tab(self):
        """创建内置提供商配置标签页"""
        gr.Markdown("## 配置内置LLM提供商")
        
        with gr.Row():
            with gr.Column(scale=1):
                provider_selector = gr.Dropdown(
                    choices=list(self.llm_manager.built_in_providers.keys()),
                    label="选择提供商",
                    value="openai"
                )
                
                api_key_input = gr.Textbox(
                    label="API密钥",
                    type="password",
                    placeholder="输入API密钥"
                )
                
                with gr.Row():
                    save_btn = gr.Button("💾 保存配置", variant="primary")
                    test_btn = gr.Button("🧪 测试连接", variant="secondary")
                
                status_output = gr.Textbox(
                    label="状态",
                    interactive=False,
                    lines=3
                )
            
            with gr.Column(scale=1):
                provider_info = gr.JSON(
                    label="提供商信息",
                    value={}
                )
                
                models_display = gr.Dataframe(
                    headers=["模型ID", "模型名称", "类型", "上下文长度"],
                    label="可用模型",
                    interactive=False
                )
        
        # 事件绑定
        def update_provider_info(provider):
            if provider in self.llm_manager.built_in_providers:
                config = self.llm_manager.built_in_providers[provider]
                models_data = [
                    [model["id"], model["name"], model["type"], model["context_length"]]
                    for model in config["models"]
                ]
                return config, models_data
            return {}, []
        
        def save_provider_config(provider, api_key):
            if not api_key:
                return "❌ 请输入API密钥"
            
            self.llm_manager.llm_config[provider] = api_key
            result = self.llm_manager.save_llm_config()
            
            if result["status"] == "success":
                return f"✅ {provider} 配置保存成功"
            else:
                return f"❌ 保存失败: {result['message']}"
        
        def test_provider_connection(provider, api_key):
            if not api_key:
                api_key = self.llm_manager.llm_config.get(provider)
                if not api_key:
                    return "❌ 请先配置API密钥"
            
            # 异步测试连接
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.llm_manager.test_provider_connection(provider, api_key)
                )
                loop.close()
                
                if result["status"] == "success":
                    return f"✅ 连接成功\n模型: {result.get('model_used', 'N/A')}\n响应预览: {result.get('response_preview', 'N/A')}"
                else:
                    return f"❌ 连接失败: {result['message']}"
            except Exception as e:
                return f"❌ 测试失败: {str(e)}"
        
        provider_selector.change(
            fn=update_provider_info,
            inputs=[provider_selector],
            outputs=[provider_info, models_display]
        )
        
        save_btn.click(
            fn=save_provider_config,
            inputs=[provider_selector, api_key_input],
            outputs=[status_output]
        )
        
        test_btn.click(
            fn=test_provider_connection,
            inputs=[provider_selector, api_key_input],
            outputs=[status_output]
        )
    
    def _create_custom_providers_tab(self):
        """创建自定义提供商标签页"""
        gr.Markdown("## 添加自定义LLM提供商")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 添加新提供商")
                
                provider_name = gr.Textbox(label="提供商名称", placeholder="例如: Claude")
                provider_id = gr.Textbox(label="提供商ID", placeholder="例如: claude")
                base_url = gr.Textbox(label="API基础URL", placeholder="https://api.example.com/v1")
                api_key = gr.Textbox(label="API密钥", type="password")
                
                with gr.Accordion("高级设置", open=False):
                    api_key_header = gr.Textbox(
                        label="API密钥头部",
                        value="Authorization",
                        placeholder="Authorization"
                    )
                    api_key_prefix = gr.Textbox(
                        label="API密钥前缀",
                        value="Bearer ",
                        placeholder="Bearer "
                    )
                    request_format = gr.Dropdown(
                        choices=["openai_compatible", "google_gemini", "dashscope", "custom"],
                        label="请求格式",
                        value="openai_compatible"
                    )
                
                with gr.Row():
                    add_provider_btn = gr.Button("➕ 添加提供商", variant="primary")
                    clear_form_btn = gr.Button("🗑️ 清空表单", variant="secondary")
                
                add_status = gr.Textbox(label="添加状态", interactive=False)
            
            with gr.Column(scale=1):
                gr.Markdown("### 已添加的自定义提供商")
                
                custom_providers_list = gr.Dataframe(
                    headers=["提供商ID", "名称", "基础URL", "添加时间"],
                    label="自定义提供商列表",
                    interactive=False
                )
                
                with gr.Row():
                    refresh_list_btn = gr.Button("🔄 刷新列表")
                    remove_provider_btn = gr.Button("🗑️ 删除选中", variant="stop")
                
                remove_provider_id = gr.Textbox(
                    label="要删除的提供商ID",
                    placeholder="输入要删除的提供商ID"
                )
                
                remove_status = gr.Textbox(label="删除状态", interactive=False)
        
        # 事件绑定
        def add_custom_provider(name, provider_id, base_url, api_key, header, prefix, format_type):
            if not all([name, provider_id, base_url, api_key]):
                return "❌ 请填写所有必需字段"
            
            provider_config = {
                "name": name,
                "provider_id": provider_id,
                "base_url": base_url,
                "api_key": api_key,
                "api_key_header": header,
                "api_key_prefix": prefix,
                "request_format": format_type
            }
            
            result = self.llm_manager.add_custom_provider(provider_config)
            
            if result["status"] == "success":
                return f"✅ {result['message']}"
            else:
                return f"❌ {result['message']}"
        
        def refresh_custom_providers():
            providers = self.llm_manager.get_all_providers()["custom"]
            data = [
                [pid, config["name"], config["base_url"], config.get("added_time", "")]
                for pid, config in providers.items()
            ]
            return data
        
        def remove_custom_provider(provider_id):
            if not provider_id:
                return "❌ 请输入要删除的提供商ID"
            
            result = self.llm_manager.remove_custom_provider(provider_id)
            
            if result["status"] == "success":
                return f"✅ {result['message']}"
            else:
                return f"❌ {result['message']}"
        
        def clear_form():
            return "", "", "", "", "Authorization", "Bearer ", "openai_compatible"
        
        add_provider_btn.click(
            fn=add_custom_provider,
            inputs=[provider_name, provider_id, base_url, api_key, 
                   api_key_header, api_key_prefix, request_format],
            outputs=[add_status]
        )
        
        clear_form_btn.click(
            fn=clear_form,
            outputs=[provider_name, provider_id, base_url, api_key,
                    api_key_header, api_key_prefix, request_format]
        )
        
        refresh_list_btn.click(
            fn=refresh_custom_providers,
            outputs=[custom_providers_list]
        )
        
        remove_provider_btn.click(
            fn=remove_custom_provider,
            inputs=[remove_provider_id],
            outputs=[remove_status]
        )
    
    def _create_agent_config_tab(self):
        """创建智能体配置标签页"""
        gr.Markdown("## 智能体模型配置")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 选择智能体")
                
                agent_category = gr.Dropdown(
                    choices=["analysts", "researchers", "risk_management", "trading"],
                    label="智能体类别",
                    value="analysts"
                )
                
                agent_selector = gr.Dropdown(
                    label="选择智能体",
                    choices=[]
                )
                
                agent_info_display = gr.JSON(
                    label="智能体信息",
                    value={}
                )
            
            with gr.Column(scale=1):
                gr.Markdown("### 模型配置")
                
                provider_dropdown = gr.Dropdown(
                    label="LLM提供商",
                    choices=[]
                )
                
                model_dropdown = gr.Dropdown(
                    label="模型",
                    choices=[]
                )
                
                compatibility_info = gr.Textbox(
                    label="兼容性评估",
                    interactive=False,
                    lines=3
                )
                
                with gr.Row():
                    update_agent_btn = gr.Button("🔄 更新配置", variant="primary")
                    get_recommendations_btn = gr.Button("💡 获取推荐", variant="secondary")
                
                update_status = gr.Textbox(label="更新状态", interactive=False)
        
        with gr.Row():
            gr.Markdown("### 推荐模型")
            recommendations_display = gr.Dataframe(
                headers=["提供商", "模型", "评分", "推荐等级"],
                label="推荐模型列表",
                interactive=False
            )
        
        # 事件绑定
        def update_agent_list(category):
            agents = self.agent_manager.get_all_agents().get(category, {})
            choices = [(f"{info['name']} ({agent_id})", agent_id) 
                      for agent_id, info in agents.items()]
            return gr.Dropdown.update(choices=choices, value=None)
        
        def update_agent_info(agent_id):
            if not agent_id:
                return {}
            
            agent_info = self.agent_manager.get_agent_info(agent_id)
            return agent_info if agent_info else {}
        
        def update_provider_list():
            providers = self.llm_manager.get_all_providers()
            all_providers = list(providers["built_in"].keys()) + list(providers["custom"].keys())
            configured_providers = [p for p in all_providers if p in self.llm_manager.llm_config]
            return gr.Dropdown.update(choices=configured_providers)
        
        def update_model_list(provider):
            if not provider:
                return gr.Dropdown.update(choices=[])
            
            models = self.llm_manager.get_provider_models(provider)
            model_choices = [(f"{model['name']} ({model['id']})", model['id']) 
                           for model in models]
            return gr.Dropdown.update(choices=model_choices)
        
        def check_compatibility(agent_id, provider, model):
            if not all([agent_id, provider, model]):
                return "请选择智能体、提供商和模型"
            
            available_models = {}
            for p in self.llm_manager.get_all_providers()["built_in"]:
                available_models[p] = self.llm_manager.get_provider_models(p)
            for p in self.llm_manager.get_all_providers()["custom"]:
                available_models[p] = self.llm_manager.get_provider_models(p)
            
            result = self.agent_manager.validate_model_compatibility(
                agent_id, provider, model, available_models
            )
            
            if result["compatible"]:
                return f"✅ 兼容\n评分: {result['score']:.2f}\n{result['recommendation']}"
            else:
                return f"❌ 不兼容\n原因: {result['reason']}"
        
        def update_agent_model(agent_id, provider, model):
            if not all([agent_id, provider, model]):
                return "❌ 请选择智能体、提供商和模型"
            
            result = self.agent_manager.update_agent_model(agent_id, provider, model)
            
            if result["status"] == "success":
                return f"✅ {result['message']}"
            else:
                return f"❌ {result['message']}"
        
        def get_agent_recommendations(agent_id):
            if not agent_id:
                return []
            
            available_models = {}
            for p in self.llm_manager.get_all_providers()["built_in"]:
                available_models[p] = self.llm_manager.get_provider_models(p)
            for p in self.llm_manager.get_all_providers()["custom"]:
                available_models[p] = self.llm_manager.get_provider_models(p)
            
            recommendations = self.agent_manager.get_recommended_models(agent_id, available_models)
            
            data = [
                [rec["provider"], rec["model_name"], f"{rec['score']:.2f}", rec["recommendation"]]
                for rec in recommendations[:10]  # 显示前10个推荐
            ]
            
            return data
        
        # 绑定事件
        agent_category.change(
            fn=update_agent_list,
            inputs=[agent_category],
            outputs=[agent_selector]
        )
        
        agent_selector.change(
            fn=update_agent_info,
            inputs=[agent_selector],
            outputs=[agent_info_display]
        )
        
        # 页面加载时更新提供商列表
        interface.load(
            fn=update_provider_list,
            outputs=[provider_dropdown]
        )
        
        provider_dropdown.change(
            fn=update_model_list,
            inputs=[provider_dropdown],
            outputs=[model_dropdown]
        )
        
        model_dropdown.change(
            fn=check_compatibility,
            inputs=[agent_selector, provider_dropdown, model_dropdown],
            outputs=[compatibility_info]
        )
        
        update_agent_btn.click(
            fn=update_agent_model,
            inputs=[agent_selector, provider_dropdown, model_dropdown],
            outputs=[update_status]
        )
        
        get_recommendations_btn.click(
            fn=get_agent_recommendations,
            inputs=[agent_selector],
            outputs=[recommendations_display]
        )
    
    def _create_test_tab(self):
        """创建测试标签页"""
        gr.Markdown("## 连接测试")
        
        with gr.Row():
            test_provider = gr.Dropdown(
                label="选择提供商",
                choices=[]
            )
            
            test_btn = gr.Button("🧪 测试连接", variant="primary")
        
        test_results = gr.Textbox(
            label="测试结果",
            interactive=False,
            lines=10
        )
        
        def update_test_providers():
            providers = self.llm_manager.get_all_providers()
            all_providers = list(providers["built_in"].keys()) + list(providers["custom"].keys())
            configured_providers = [p for p in all_providers if p in self.llm_manager.llm_config]
            return gr.Dropdown.update(choices=configured_providers)
        
        def test_connection(provider):
            if not provider:
                return "❌ 请选择提供商"
            
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.llm_manager.test_provider_connection(provider)
                )
                loop.close()
                
                if result["status"] == "success":
                    return f"✅ {provider} 连接成功\n模型: {result.get('model_used', 'N/A')}\n响应预览: {result.get('response_preview', 'N/A')}"
                else:
                    return f"❌ {provider} 连接失败: {result['message']}"
            except Exception as e:
                return f"❌ 测试失败: {str(e)}"
        
        # 页面加载时更新提供商列表
        interface.load(
            fn=update_test_providers,
            outputs=[test_provider]
        )
        
        test_btn.click(
            fn=test_connection,
            inputs=[test_provider],
            outputs=[test_results]
        )
