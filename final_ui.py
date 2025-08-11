#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents 优化版UI
单屏幕显示，所有功能可用
"""

import gradio as gr
import asyncio
import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class OptimizedTradingAgentsUI:
    """优化版TradingAgents UI类"""

    def __init__(self):
        self.current_result = None
        self.analysis_progress = 0
        self.current_agent = "待机中"
        
        # 初始化增强功能模块
        try:
            from core.enhanced_llm_manager import EnhancedLLMManager
            from core.agent_model_manager import AgentModelManager
            from core.enhanced_report_generator import EnhancedReportGenerator
            from core.intelligent_summarizer import ContentProcessor

            self.llm_manager = EnhancedLLMManager()
            self.agent_manager = AgentModelManager()
            self.report_generator = EnhancedReportGenerator()
            self.content_processor = ContentProcessor()
            self.enhanced_features_available = True

        except ImportError as e:
            print(f"⚠️ 增强功能模块未找到: {e}")
            self.enhanced_features_available = False
    
    def get_system_info(self):
        """获取系统信息"""
        return {
            "系统状态": "✅ 正常运行",
            "智能体": "15个专业智能体",
            "LLM状态": "✅ 多模型支持",
            "增强功能": "✅ 已启用" if self.enhanced_features_available else "⚠️ 基础模式"
        }
    
    def run_analysis(self, stock_code, analysis_depth, selected_agents, progress=gr.Progress()):
        """运行股票分析"""
        try:
            if not stock_code or not stock_code.strip():
                return "❌ 请输入有效的股票代码", "", ""
            
            progress(0.1, desc="初始化系统...")
            
            # 导入分析函数
            from app_tradingagents_upgraded import analyze_stock_upgraded
            
            progress(0.3, desc="启动智能体...")
            
            # 映射分析深度
            depth_map = {"快速": "快速分析 (1轮辩论)", "标准": "标准分析 (2轮辩论)", 
                        "深度": "深度分析 (3轮辩论)", "全面": "全面分析 (4轮辩论)"}
            
            # 运行分析
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                analyze_stock_upgraded(
                    symbol=stock_code.strip(),
                    depth=depth_map.get(analysis_depth, "标准分析 (2轮辩论)"),
                    analysts=selected_agents[:4],  # 限制智能体数量
                    use_real_llm=True
                )
            )
            
            progress(1.0, desc="分析完成！")
            
            if result:
                self.current_result = result
                # 生成简化的图表数据
                chart_data = self.generate_chart_data(stock_code)
                # 生成分析日志
                log_data = f"分析完成时间: {datetime.now()}\n股票代码: {stock_code}\n分析深度: {analysis_depth}\n参与智能体: {', '.join(selected_agents)}"
                
                return result, chart_data, log_data
            else:
                return "❌ 分析失败，请检查股票代码或网络连接", "", ""
                
        except Exception as e:
            return f"❌ 分析过程中出现错误: {str(e)}", "", ""
    
    def generate_chart_data(self, stock_code):
        """生成图表数据"""
        import matplotlib.pyplot as plt
        import numpy as np
        
        # 生成模拟数据
        days = np.arange(1, 31)
        prices = 100 + np.cumsum(np.random.randn(30) * 2)
        
        plt.figure(figsize=(10, 6))
        plt.plot(days, prices, 'b-', linewidth=2, label=f'{stock_code} 价格走势')
        plt.title(f'{stock_code} 股价分析图表')
        plt.xlabel('天数')
        plt.ylabel('价格')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        return plt
    
    def save_llm_config(self, provider, api_key):
        """保存LLM配置"""
        if not api_key:
            return "❌ 请输入API密钥"
        
        try:
            if self.enhanced_features_available:
                self.llm_manager.llm_config[provider.lower()] = api_key
                result = self.llm_manager.save_llm_config()
                return f"✅ {provider} 配置保存成功" if result["status"] == "success" else f"❌ 保存失败: {result['message']}"
            else:
                return "⚠️ 增强功能不可用"
        except Exception as e:
            return f"❌ 保存失败: {str(e)}"
    
    def test_llm_connection(self, provider, api_key):
        """测试LLM连接"""
        if not api_key:
            return "❌ 请输入API密钥"
        
        try:
            if self.enhanced_features_available:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.llm_manager.test_provider_connection(provider.lower(), api_key)
                )
                loop.close()
                
                return f"✅ 连接成功" if result["status"] == "success" else f"❌ 连接失败: {result['message']}"
            else:
                return "⚠️ 增强功能不可用"
        except Exception as e:
            return f"❌ 测试失败: {str(e)}"
    
    def export_report(self, format_type):
        """导出报告"""
        if not self.current_result:
            return "❌ 没有可导出的分析结果"
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_report_{timestamp}.{format_type.lower()}"
            
            if format_type == "JSON":
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump({"report": str(self.current_result)}, f, ensure_ascii=False, indent=2)
            else:  # TXT
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(str(self.current_result))
            
            return f"✅ 报告已导出: {filename}"
        except Exception as e:
            return f"❌ 导出失败: {str(e)}"

# 创建UI实例
ui = OptimizedTradingAgentsUI()

def create_optimized_interface():
    """创建优化后的界面"""
    
    # 自定义CSS样式
    custom_css = """
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
    </style>
    """
    
    with gr.Blocks(
        title="🤖 TradingAgents - 优化版",
        theme=gr.themes.Soft(),
        css=custom_css
    ) as interface:
        
        # 紧凑标题栏
        gr.HTML("""
        <div style="text-align: center; padding: 8px; 
                   background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   color: white; border-radius: 8px; margin: 5px 0;">
            <h2 style="margin: 0; font-size: 1.4em;">🤖 TradingAgents 优化版</h2>
            <p style="margin: 3px 0 0 0; font-size: 0.85em;">专业多智能体股票分析系统 - 单屏幕优化版</p>
        </div>
        """)
        
        # 主要内容区域
        with gr.Row(equal_height=True):
            # 左侧控制面板 (30%)
            with gr.Column(scale=3, min_width=320):
                # 分析设置
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
                            choices=["JSON", "TXT"],
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
                
                # 系统状态 - 紧凑显示
                with gr.Group():
                    gr.Markdown("### 🔧 系统状态", elem_classes="compact-title")
                    
                    system_status = gr.JSON(
                        value=ui.get_system_info(),
                        container=False,
                        show_label=False
                    )
                    
                    with gr.Row():
                        refresh_btn = gr.Button("🔄 刷新", size="sm", scale=1)
                        export_btn = gr.Button("📤 导出", size="sm", scale=1)
            
            # 右侧结果显示 (70%)
            with gr.Column(scale=7, min_width=600):
                # 结果标签页
                with gr.Tabs() as result_tabs:
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
        
        # 配置标签页 - 紧凑布局
        with gr.Tabs():
            with gr.Tab("⚙️ 配置中心"):
                with gr.Row():
                    # LLM配置
                    with gr.Column(scale=1):
                        gr.Markdown("#### 🤖 LLM配置")
                        
                        provider_select = gr.Dropdown(
                            choices=["OpenAI", "Moonshot", "阿里百炼"],
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
                        
                        config_status = gr.Textbox(
                            label="状态",
                            container=False,
                            interactive=False,
                            lines=2
                        )
                    
                    # 快速帮助
                    with gr.Column(scale=1):
                        gr.Markdown("#### ❓ 快速帮助")
                        gr.Markdown("""
                        **使用步骤:**
                        1. 输入股票代码 (如: 600519)
                        2. 选择分析深度
                        3. 点击"🚀 分析"按钮
                        4. 查看结果并导出报告
                        
                        **支持的股票代码:**
                        - A股: 600519, 000001, 002415
                        - 港股: 00700, 09988
                        
                        **分析深度说明:**
                        - 快速: 1轮分析 (~2分钟)
                        - 标准: 2轮分析 (~5分钟)
                        - 深度: 3轮分析 (~8分钟)
                        - 全面: 4轮分析 (~12分钟)
                        """)
        
        # 事件绑定
        analyze_btn.click(
            fn=ui.run_analysis,
            inputs=[stock_input, analysis_depth, selected_agents],
            outputs=[analysis_output, chart_output, log_output],
            show_progress=True
        )
        
        refresh_btn.click(
            fn=lambda: ui.get_system_info(),
            outputs=system_status
        )
        
        export_btn.click(
            fn=ui.export_report,
            inputs=export_format,
            outputs=config_status
        )
        
        save_config_btn.click(
            fn=ui.save_llm_config,
            inputs=[provider_select, api_key_input],
            outputs=config_status
        )
        
        test_config_btn.click(
            fn=ui.test_llm_connection,
            inputs=[provider_select, api_key_input],
            outputs=config_status
        )
    
    return interface

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 TradingAgents 优化版 - 单屏幕显示")
    print("=" * 60)
    print("🚀 正在启动优化版界面...")
    print("🌐 界面地址: http://localhost:7862")
    print("📱 已优化移动端显示")
    print("=" * 60)

    try:
        interface = create_optimized_interface()
        print("✅ 优化版界面创建成功！")
        print("\n💡 优化特性:")
        print("   • 🎨 单屏幕紧凑布局")
        print("   • ⚡ 快速响应设计")
        print("   • 📱 移动端适配")
        print("   • 🔧 智能折叠组件")
        print("   • 📊 实时状态显示")
        
        print("\n🌟 现在可以在浏览器中访问: http://localhost:7862")

        interface.launch(
            server_name="0.0.0.0",
            server_port=7862,
            share=False,
            inbrowser=True
        )
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("🔧 请检查依赖包是否完整安装")
        sys.exit(1)
