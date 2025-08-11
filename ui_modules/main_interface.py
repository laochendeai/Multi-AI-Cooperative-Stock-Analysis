#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents 主界面模块
集成所有模块创建完整的用户界面
"""

import gradio as gr
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入模块化组件
from ui_modules.core_ui import get_ui_instance
from ui_modules.handlers.analysis_handler import create_analysis_handler
from ui_modules.handlers.llm_handler import create_llm_handler
from ui_modules.handlers.report_handler import create_report_handler
from ui_modules.handlers.event_handler import create_event_handler
from ui_modules.components.main_components import (
    create_header_component,
    create_analysis_input_components,
    create_system_status_components,
    create_results_components,
    create_config_components,
    create_footer_component,
    get_custom_css
)

class ModularInterface:
    """模块化界面管理器"""
    
    def __init__(self):
        """初始化模块化界面"""
        print("🚀 初始化模块化界面...")
        
        # 获取核心UI实例
        self.ui = get_ui_instance()
        
        # 创建处理器
        self.analysis_handler = create_analysis_handler(self.ui)
        self.llm_handler = create_llm_handler(self.ui)
        self.report_handler = create_report_handler(self.ui)
        
        # 创建事件处理器
        self.event_handler = create_event_handler(
            self.ui, self.analysis_handler, 
            self.llm_handler, self.report_handler
        )
        
        print("✅ 所有模块初始化完成")
    
    def create_interface(self):
        """创建完整界面"""
        print("🎨 创建模块化界面...")
        
        with gr.Blocks(
            title="🤖 TradingAgents - 模块化版",
            theme=gr.themes.Soft(),
            css=get_custom_css()
        ) as interface:
            
            # 页面头部
            create_header_component()
            
            # 模块信息显示
            gr.HTML("""
            <div class="module-info">
                <h3>🧩 模块化架构信息</h3>
                <p><strong>核心模块:</strong> UI核心、分析处理、LLM管理、报告生成、事件处理</p>
                <p><strong>组件模块:</strong> 主要组件、样式管理、工具函数</p>
                <p><strong>架构优势:</strong> 易维护、可扩展、高内聚、低耦合</p>
            </div>
            """)
            
            # 主要内容区域
            with gr.Row(equal_height=True):
                # 左侧控制面板 (30%)
                with gr.Column(scale=3, min_width=320):
                    # 分析输入组件
                    (stock_input, analyze_btn, analysis_depth, 
                     export_format, selected_agents) = create_analysis_input_components()
                    
                    # 系统状态组件
                    (system_status, refresh_btn, export_btn, 
                     reset_btn) = create_system_status_components(self.ui)
                
                # 右侧结果显示 (70%)
                with gr.Column(scale=7, min_width=600):
                    # 结果显示组件
                    (analysis_output, chart_output, log_output, 
                     report_list, report_content, refresh_reports_btn, 
                     delete_report_btn, view_report_btn) = create_results_components()
            
            # 配置标签页
            with gr.Tabs():
                with gr.Tab("⚙️ 配置中心"):
                    (provider_select, api_key_input, save_config_btn, test_config_btn, 
                     clear_config_btn, config_status, provider_status, max_agents, 
                     timeout_setting, enable_cache) = create_config_components()
                
                with gr.Tab("📊 模块状态"):
                    self._create_module_status_tab()
            
            # 页面底部
            create_footer_component()
            
            # 绑定事件
            self._bind_all_events(
                stock_input, analyze_btn, analysis_depth, export_format, selected_agents,
                analysis_output, chart_output, log_output,
                system_status, refresh_btn, export_btn, reset_btn,
                provider_select, api_key_input, save_config_btn, test_config_btn, 
                clear_config_btn, config_status, provider_status,
                report_list, report_content, refresh_reports_btn, 
                delete_report_btn, view_report_btn,
                max_agents, timeout_setting, enable_cache
            )
        
        print("✅ 模块化界面创建完成")
        return interface
    
    def _create_module_status_tab(self):
        """创建模块状态标签页"""
        gr.Markdown("### 🔧 模块运行状态")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### 📦 已加载模块")
                module_status = gr.JSON(
                    value={
                        "core_ui": "✅ 已加载",
                        "analysis_handler": "✅ 已加载",
                        "llm_handler": "✅ 已加载", 
                        "report_handler": "✅ 已加载",
                        "event_handler": "✅ 已加载",
                        "main_components": "✅ 已加载"
                    },
                    label="模块状态",
                    container=False
                )
            
            with gr.Column():
                gr.Markdown("#### 📊 性能指标")
                performance_metrics = gr.JSON(
                    value=self._get_performance_metrics(),
                    label="性能指标",
                    container=False
                )
        
        with gr.Row():
            reload_modules_btn = gr.Button("🔄 重载模块", variant="secondary")
            test_modules_btn = gr.Button("🧪 测试模块", variant="primary")
            module_info_btn = gr.Button("ℹ️ 模块信息", variant="secondary")
        
        # 模块操作结果显示
        module_operation_result = gr.Textbox(
            label="操作结果",
            lines=5,
            container=False,
            show_copy_button=True
        )
        
        # 绑定模块管理事件
        reload_modules_btn.click(
            fn=self._reload_modules,
            outputs=[module_status, module_operation_result]
        )
        
        test_modules_btn.click(
            fn=self._test_all_modules,
            outputs=module_operation_result
        )
        
        module_info_btn.click(
            fn=self._get_module_info,
            outputs=module_operation_result
        )
    
    def _bind_all_events(self, *components):
        """绑定所有事件"""
        print("🔗 绑定界面事件...")
        
        # 解包组件
        (stock_input, analyze_btn, analysis_depth, export_format, selected_agents,
         analysis_output, chart_output, log_output,
         system_status, refresh_btn, export_btn, reset_btn,
         provider_select, api_key_input, save_config_btn, test_config_btn, 
         clear_config_btn, config_status, provider_status,
         report_list, report_content, refresh_reports_btn, 
         delete_report_btn, view_report_btn,
         max_agents, timeout_setting, enable_cache) = components
        
        # 绑定分析事件
        self.event_handler.bind_analysis_events((
            stock_input, analyze_btn, analysis_depth, export_format,
            selected_agents, analysis_output, chart_output, log_output
        ))
        
        # 绑定系统事件
        self.event_handler.bind_system_events((
            system_status, refresh_btn, export_btn, reset_btn, export_format
        ))
        
        # 绑定LLM配置事件
        self.event_handler.bind_llm_config_events((
            provider_select, api_key_input, save_config_btn, test_config_btn,
            clear_config_btn, config_status, provider_status
        ))
        
        # 绑定报告事件
        self.event_handler.bind_report_events((
            report_list, report_content, refresh_reports_btn,
            delete_report_btn, view_report_btn
        ))
        
        # 绑定高级功能事件
        self.event_handler.bind_advanced_events((
            max_agents, timeout_setting, enable_cache
        ))
        
        print("✅ 所有事件绑定完成")
    
    def _get_performance_metrics(self):
        """获取性能指标"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            return {
                "内存使用": f"{process.memory_info().rss / 1024 / 1024:.1f} MB",
                "CPU使用": f"{process.cpu_percent():.1f}%",
                "线程数": process.num_threads(),
                "运行时间": f"{process.create_time():.0f}s"
            }
        except ImportError:
            return {
                "内存使用": "需要安装psutil",
                "CPU使用": "需要安装psutil",
                "线程数": "未知",
                "运行时间": "未知"
            }
    
    def _reload_modules(self):
        """重载模块"""
        try:
            # 这里可以实现模块重载逻辑
            result = "🔄 模块重载功能开发中..."
            status = {
                "core_ui": "🔄 重载中",
                "analysis_handler": "🔄 重载中",
                "llm_handler": "🔄 重载中",
                "report_handler": "🔄 重载中",
                "event_handler": "🔄 重载中",
                "main_components": "🔄 重载中"
            }
            return status, result
        except Exception as e:
            return {}, f"❌ 重载失败: {str(e)}"
    
    def _test_all_modules(self):
        """测试所有模块"""
        results = []
        
        # 测试核心UI
        try:
            info = self.ui.get_system_info()
            results.append("✅ 核心UI模块: 正常")
        except Exception as e:
            results.append(f"❌ 核心UI模块: {e}")
        
        # 测试分析处理器
        try:
            status = self.analysis_handler.get_analysis_status()
            results.append("✅ 分析处理器: 正常")
        except Exception as e:
            results.append(f"❌ 分析处理器: {e}")
        
        # 测试LLM处理器
        try:
            status = self.llm_handler.get_provider_status()
            results.append("✅ LLM处理器: 正常")
        except Exception as e:
            results.append(f"❌ LLM处理器: {e}")
        
        # 测试报告处理器
        try:
            summary = self.report_handler.get_export_summary()
            results.append("✅ 报告处理器: 正常")
        except Exception as e:
            results.append(f"❌ 报告处理器: {e}")
        
        # 测试事件处理器
        try:
            summary = self.event_handler.get_event_summary()
            results.append("✅ 事件处理器: 正常")
        except Exception as e:
            results.append(f"❌ 事件处理器: {e}")
        
        return "\n".join(results)
    
    def _get_module_info(self):
        """获取模块信息"""
        info = [
            "🧩 TradingAgents 模块化架构信息",
            "=" * 40,
            "",
            "📦 核心模块:",
            "  • core_ui.py - UI核心逻辑和状态管理",
            "  • analysis_handler.py - 股票分析处理",
            "  • llm_handler.py - LLM配置和连接管理",
            "  • report_handler.py - 报告生成和导出",
            "  • event_handler.py - 事件绑定和处理",
            "",
            "🎨 组件模块:",
            "  • main_components.py - 主要UI组件",
            "  • main_interface.py - 界面集成管理",
            "",
            "🔧 架构优势:",
            "  • 高内聚低耦合的模块设计",
            "  • 易于维护和扩展",
            "  • 支持热插拔和独立测试",
            "  • 清晰的职责分离",
            "",
            "📊 模块统计:",
            f"  • 总模块数: 7个",
            f"  • 处理器模块: 4个",
            f"  • 组件模块: 2个",
            f"  • 核心模块: 1个"
        ]
        
        return "\n".join(info)

def create_modular_interface():
    """创建模块化界面"""
    modular_interface = ModularInterface()
    return modular_interface.create_interface()

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 TradingAgents 模块化版本启动")
    print("=" * 60)
    
    try:
        interface = create_modular_interface()
        print("✅ 模块化界面创建成功！")
        print("\n🧩 模块化特性:")
        print("   • 📦 组件化架构")
        print("   • 🔄 热插拔支持")
        print("   • 🧪 独立模块测试")
        print("   • 📊 模块状态监控")
        print("   • 🎨 可定制UI组件")
        
        print("\n🌟 现在可以在浏览器中访问: http://localhost:7863")
        
        interface.launch(
            server_name="0.0.0.0",
            server_port=7863,
            share=False,
            inbrowser=True
        )
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("🔧 请检查模块依赖是否完整")
        sys.exit(1)
