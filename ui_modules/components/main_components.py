#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents 主要UI组件模块
负责创建主要的Gradio界面组件
"""

import gradio as gr
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def create_header_component():
    """创建页面头部组件"""
    return gr.HTML("""
    <div style="text-align: center; padding: 8px; 
               background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
               color: white; border-radius: 8px; margin: 5px 0;">
        <h2 style="margin: 0; font-size: 1.4em;">🤖 TradingAgents 模块化版</h2>
        <p style="margin: 3px 0 0 0; font-size: 0.85em;">专业多智能体股票分析系统 - 模块化架构</p>
    </div>
    """)

def create_analysis_input_components():
    """创建分析输入组件"""
    with gr.Group():
        gr.Markdown("### 📊 分析设置", elem_classes="compact-title")
        
        with gr.Row():
            stock_input = gr.Textbox(
                label="股票代码",
                placeholder="600519",
                scale=2,
                container=False
            )
            analyze_btn = gr.Button(
                "🚀 分析", 
                variant="primary",
                scale=1,
                size="sm"
            )
        
        # 快速设置
        with gr.Row():
            analysis_depth = gr.Dropdown(
                choices=["快速", "标准", "深度", "全面"],
                value="标准",
                label="深度",
                scale=1,
                container=False
            )
            
            export_format = gr.Dropdown(
                choices=["JSON", "TXT", "HTML", "MD"],
                value="JSON",
                label="导出",
                scale=1,
                container=False
            )
        
        # 智能体选择 - 折叠式
        with gr.Accordion("👥 智能体选择", open=False):
            selected_agents = gr.CheckboxGroup(
                choices=[
                    "市场分析师", "情感分析师", "新闻分析师", "基本面分析师",
                    "多头研究员", "空头研究员", "风险经理", "交易员"
                ],
                value=["市场分析师", "情感分析师", "基本面分析师"],
                container=False
            )
    
    return stock_input, analyze_btn, analysis_depth, export_format, selected_agents

def create_system_status_components(ui_instance):
    """创建系统状态组件"""
    with gr.Group():
        gr.Markdown("### 🔧 系统状态", elem_classes="compact-title")
        
        system_status = gr.JSON(
            value=ui_instance.get_system_info(),
            container=False,
            show_label=False
        )
        
        with gr.Row():
            refresh_btn = gr.Button("🔄 刷新", size="sm", scale=1)
            export_btn = gr.Button("📤 导出", size="sm", scale=1)
            reset_btn = gr.Button("🗑️ 重置", size="sm", scale=1)
    
    return system_status, refresh_btn, export_btn, reset_btn

def create_results_components():
    """创建结果显示组件"""
    # 结果标签页
    with gr.Tabs():
        with gr.Tab("📈 分析结果"):
            analysis_output = gr.Markdown(
                value="🔮 等待分析结果...",
                container=False,
                elem_classes="result-area"
            )
        
        with gr.Tab("📊 数据图表"):
            chart_output = gr.Plot(
                container=False
            )
        
        with gr.Tab("🔍 分析日志"):
            log_output = gr.Textbox(
                lines=12,
                container=False,
                show_copy_button=True
            )
        
        with gr.Tab("📋 报告管理"):
            with gr.Row():
                with gr.Column(scale=1):
                    report_list = gr.Dataframe(
                        headers=["文件名", "大小", "创建时间", "格式"],
                        datatype=["str", "str", "str", "str"],
                        label="历史报告"
                    )
                
                with gr.Column(scale=1):
                    report_content = gr.Textbox(
                        label="报告内容预览",
                        lines=10,
                        container=False,
                        show_copy_button=True
                    )
            
            with gr.Row():
                refresh_reports_btn = gr.Button("🔄 刷新列表", size="sm")
                delete_report_btn = gr.Button("🗑️ 删除选中", size="sm")
                view_report_btn = gr.Button("👁️ 查看内容", size="sm")
    
    return (analysis_output, chart_output, log_output, 
            report_list, report_content, refresh_reports_btn, 
            delete_report_btn, view_report_btn)

def create_config_components():
    """创建配置组件"""
    with gr.Row():
        # LLM配置
        with gr.Column(scale=1):
            gr.Markdown("#### 🤖 LLM配置")
            
            provider_select = gr.Dropdown(
                choices=["OpenAI", "Moonshot", "阿里百炼", "Google", 
                        "DeepSeek", "OpenRouter", "Groq"],
                value="OpenAI",
                label="提供商",
                container=False
            )
            
            api_key_input = gr.Textbox(
                label="API密钥",
                type="password",
                container=False
            )
            
            with gr.Row():
                save_config_btn = gr.Button("💾 保存", size="sm")
                test_config_btn = gr.Button("🧪 测试", size="sm")
                clear_config_btn = gr.Button("🗑️ 清除", size="sm")
            
            config_status = gr.Textbox(
                label="状态",
                container=False,
                interactive=False,
                lines=3
            )
            
            # 提供商状态
            provider_status = gr.JSON(
                label="提供商状态",
                container=False
            )
        
        # 系统配置和帮助
        with gr.Column(scale=1):
            gr.Markdown("#### ⚙️ 系统配置")
            
            with gr.Accordion("🔧 高级设置", open=False):
                max_agents = gr.Slider(
                    minimum=1,
                    maximum=8,
                    value=4,
                    step=1,
                    label="最大智能体数量"
                )
                
                timeout_setting = gr.Slider(
                    minimum=30,
                    maximum=300,
                    value=120,
                    step=30,
                    label="分析超时时间(秒)"
                )
                
                enable_cache = gr.Checkbox(
                    label="启用结果缓存",
                    value=True
                )
            
            gr.Markdown("#### ❓ 快速帮助")
            gr.Markdown("""
            **模块化特性:**
            - 🧩 组件化架构，易于维护
            - 🔄 热插拔模块支持
            - 📊 独立的处理器模块
            - 🎨 可定制UI组件
            
            **使用步骤:**
            1. 配置LLM提供商API密钥
            2. 输入股票代码进行分析
            3. 查看结果并导出报告
            4. 管理历史分析记录
            
            **支持格式:**
            - JSON: 结构化数据
            - TXT: 纯文本报告
            - HTML: 网页格式
            - MD: Markdown文档
            """)
    
    return (provider_select, api_key_input, save_config_btn, test_config_btn, 
            clear_config_btn, config_status, provider_status, max_agents, 
            timeout_setting, enable_cache)

def create_footer_component():
    """创建页面底部组件"""
    return gr.HTML("""
    <div style="text-align: center; padding: 10px; margin-top: 20px; 
               border-top: 1px solid #eee; color: #666; font-size: 0.9em;">
        <p>🤖 TradingAgents 模块化版本 | 
           📚 <a href="docs/UI_OPTIMIZATION_PLAN.md" target="_blank">技术文档</a> | 
           🔧 <a href="scripts/ui_optimizer.py" target="_blank">优化工具</a></p>
    </div>
    """)

def get_custom_css():
    """获取自定义CSS样式"""
    return """
    <style>
    .compact-header { margin-bottom: 10px !important; }
    .compact-title { margin: 8px 0 !important; font-size: 1.1em !important; }
    .result-area { max-height: 500px !important; overflow-y: auto !important; }
    .gradio-container .block { padding: 6px !important; margin: 3px 0 !important; }
    .status-indicator { background: #f0f8ff; padding: 8px; border-radius: 6px; margin: 5px 0; }
    @media (max-width: 1366px) {
        .gradio-container { max-width: 100% !important; padding: 8px !important; }
    }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 3px; }
    ::-webkit-scrollbar-thumb { background: #888; border-radius: 3px; }
    .module-info { 
        background: linear-gradient(45deg, #f0f8ff, #e6f3ff); 
        padding: 10px; 
        border-radius: 8px; 
        border-left: 4px solid #667eea; 
        margin: 10px 0; 
    }
    </style>
    """
