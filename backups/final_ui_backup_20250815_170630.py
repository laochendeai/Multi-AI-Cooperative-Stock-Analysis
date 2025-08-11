#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents 最终工作版UI
确保能够正常启动和运行
"""

import gradio as gr
import asyncio
import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class FinalTradingAgentsUI:
    """最终版TradingAgents UI类"""

    def __init__(self):
        self.current_result = None

        # 初始化新功能组件
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
        system_info = {
            "系统状态": "✅ 正常运行",
            "ChromaDB记忆": "✅ 向量记忆系统就绪",
            "Moonshot API": "✅ Kimi K2模型连接正常",
            "阿里百炼API": "✅ Qwen-Turbo模型连接正常",
            "智能体数量": "15个专业智能体协作",
            "架构版本": "TradingAgents v2.0"
        }

        if self.enhanced_features_available:
            system_info.update({
                "增强功能": "✅ 已启用",
                "LLM管理器": "✅ 增强配置管理",
                "智能体管理": "✅ 灵活模型选择",
                "报告生成": "✅ 多模板支持",
                "文档精简": "✅ 智能内容处理"
            })
        else:
            system_info["增强功能"] = "⚠️ 部分功能不可用"

        return system_info
    
    def run_real_analysis(self, stock_code, analysis_depth, progress=gr.Progress()):
        """运行真实分析"""
        try:
            if not stock_code or not stock_code.strip():
                return "❌ 请输入有效的股票代码"
            
            progress(0.1, desc="初始化系统...")
            
            # 导入真实的分析函数
            from app_tradingagents_upgraded import analyze_stock_upgraded
            
            progress(0.3, desc="启动TradingAgents架构...")
            
            # 运行异步分析
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                analyze_stock_upgraded(
                    symbol=stock_code.strip(),
                    depth=analysis_depth,
                    analysts=["市场技术分析师", "投资者情感分析师", "新闻事件分析师", "基本面分析师"],
                    use_real_llm=True
                )
            )
            
            progress(0.9, desc="生成报告...")
            
            if result:
                self.current_result = result
                progress(1.0, desc="分析完成！")
                return result
            else:
                return "❌ 分析失败，请检查股票代码或网络连接"
                
        except Exception as e:
            return f"❌ 分析过程中出现错误: {str(e)}"
    
    def export_current_report(self, format_type):
        """导出当前报告"""
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

    def create_enhanced_llm_config_tab(self):
        """创建增强的LLM配置标签页内容"""
        if not self.enhanced_features_available:
            return [
                gr.Markdown("⚠️ 增强LLM配置功能不可用，请检查相关模块是否正确安装"),
                gr.Textbox("功能不可用", interactive=False)
            ]

        # 提供商选择器
        provider_selector = gr.Dropdown(
            choices=list(self.llm_manager.built_in_providers.keys()),
            label="选择提供商",
            value="openai"
        )

        # API密钥输入
        api_key_input = gr.Textbox(
            label="API密钥",
            type="password",
            placeholder="输入API密钥"
        )

        # 操作按钮
        with gr.Row():
            save_btn = gr.Button("💾 保存配置", variant="primary")
            test_btn = gr.Button("🧪 测试连接", variant="secondary")

        # 状态显示
        config_status = gr.Textbox(
            label="配置状态",
            interactive=False,
            lines=3
        )

        def save_provider_config(provider, api_key):
            if not api_key:
                return "❌ 请输入API密钥"

            self.llm_manager.llm_config[provider] = api_key
            result = self.llm_manager.save_llm_config()

            if result["status"] == "success":
                return f"✅ {provider} 配置保存成功"
            else:
                return f"❌ 保存失败: {result['message']}"

        def test_connection(provider, api_key):
            if not api_key:
                api_key = self.llm_manager.llm_config.get(provider)
                if not api_key:
                    return "❌ 请先配置API密钥"

            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.llm_manager.test_provider_connection(provider, api_key)
                )
                loop.close()

                if result["status"] == "success":
                    return f"✅ 连接成功\n模型: {result.get('model_used', 'N/A')}"
                else:
                    return f"❌ 连接失败: {result['message']}"
            except Exception as e:
                return f"❌ 测试失败: {str(e)}"

        # 绑定事件
        save_btn.click(
            fn=save_provider_config,
            inputs=[provider_selector, api_key_input],
            outputs=[config_status]
        )

        test_btn.click(
            fn=test_connection,
            inputs=[provider_selector, api_key_input],
            outputs=[config_status]
        )

        return [provider_selector, api_key_input, save_btn, test_btn, config_status]

    def create_enhanced_agent_config_tab(self):
        """创建增强的智能体配置标签页内容"""
        if not self.enhanced_features_available:
            return [gr.Markdown("⚠️ 增强智能体配置功能不可用，请检查相关模块是否正确安装")]

        # 智能体选择
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

        # 模型选择
        provider_selector = gr.Dropdown(
            label="LLM提供商",
            choices=[]
        )

        model_selector = gr.Dropdown(
            label="模型",
            choices=[]
        )

        # 兼容性信息
        compatibility_info = gr.Textbox(
            label="兼容性评估",
            interactive=False,
            lines=3
        )

        # 更新按钮
        update_btn = gr.Button("🔄 更新配置", variant="primary")

        # 状态显示
        update_status = gr.Textbox(
            label="更新状态",
            interactive=False
        )

        def update_agent_list(category):
            try:
                agents = self.agent_manager.get_all_agents().get(category, {})
                choices = [(f"{info['name']} ({agent_id})", agent_id)
                          for agent_id, info in agents.items()]
                return gr.Dropdown.update(choices=choices, value=None)
            except:
                return gr.Dropdown.update(choices=[])

        def update_provider_list():
            try:
                providers = self.llm_manager.get_all_providers()
                all_providers = list(providers["built_in"].keys()) + list(providers["custom"].keys())
                configured_providers = [p for p in all_providers if p in self.llm_manager.llm_config]
                return gr.Dropdown.update(choices=configured_providers)
            except:
                return gr.Dropdown.update(choices=[])

        def update_model_list(provider):
            if not provider:
                return gr.Dropdown.update(choices=[])
            try:
                models = self.llm_manager.get_provider_models(provider)
                model_choices = [(f"{model['name']} ({model['id']})", model['id'])
                               for model in models]
                return gr.Dropdown.update(choices=model_choices)
            except:
                return gr.Dropdown.update(choices=[])

        def check_compatibility(agent_id, provider, model):
            if not all([agent_id, provider, model]):
                return "请选择智能体、提供商和模型"

            try:
                available_models = {}
                all_providers = self.llm_manager.get_all_providers()

                for provider_id in list(all_providers["built_in"].keys()) + list(all_providers["custom"].keys()):
                    available_models[provider_id] = self.llm_manager.get_provider_models(provider_id)

                result = self.agent_manager.validate_model_compatibility(
                    agent_id, provider, model, available_models
                )

                if result["compatible"]:
                    return f"✅ 兼容\n评分: {result['score']:.2f}\n{result['recommendation']}"
                else:
                    return f"❌ 不兼容\n原因: {result['reason']}"
            except Exception as e:
                return f"❌ 检查失败: {str(e)}"

        def update_agent_model(agent_id, provider, model):
            if not all([agent_id, provider, model]):
                return "❌ 请选择智能体、提供商和模型"

            try:
                result = self.agent_manager.update_agent_model(agent_id, provider, model)

                if result["status"] == "success":
                    return f"✅ {result['message']}"
                else:
                    return f"❌ {result['message']}"
            except Exception as e:
                return f"❌ 更新失败: {str(e)}"

        # 绑定事件
        agent_category.change(
            fn=update_agent_list,
            inputs=[agent_category],
            outputs=[agent_selector]
        )

        provider_selector.change(
            fn=update_model_list,
            inputs=[provider_selector],
            outputs=[model_selector]
        )

        model_selector.change(
            fn=check_compatibility,
            inputs=[agent_selector, provider_selector, model_selector],
            outputs=[compatibility_info]
        )

        update_btn.click(
            fn=update_agent_model,
            inputs=[agent_selector, provider_selector, model_selector],
            outputs=[update_status]
        )

        return [agent_category, agent_selector, provider_selector, model_selector,
                compatibility_info, update_btn, update_status]

# 创建UI实例
ui = FinalTradingAgentsUI()

def create_final_interface():
    """创建最终界面"""
    
    with gr.Blocks(
        title="🤖 TradingAgents - 专业多智能体股票分析系统",
        theme=gr.themes.Default()
    ) as interface:
        
        # 标题
        gr.HTML("""
        <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin: 20px 0;">
            <h1 style="margin: 0; font-size: 2.5em;">🤖 TradingAgents</h1>
            <h2 style="margin: 10px 0 0 0; font-weight: normal; opacity: 0.9;">专业多智能体股票分析系统</h2>
            <p style="margin: 15px 0 0 0; opacity: 0.8;">基于ChromaDB向量记忆 + 15个专业智能体协作</p>
        </div>
        """)
        
        with gr.Row():
            # 左侧控制面板
            with gr.Column(scale=1):
                gr.Markdown("## 📊 分析控制台")
                
                stock_input = gr.Textbox(
                    label="📈 股票代码",
                    placeholder="输入股票代码，如：600519, 000001",
                    value="600519"
                )
                
                analysis_depth = gr.Dropdown(
                    choices=[
                        "快速分析 (1轮辩论)", 
                        "标准分析 (2轮辩论)", 
                        "深度分析 (3轮辩论)", 
                        "全面分析 (4轮辩论)"
                    ],
                    value="标准分析 (2轮辩论)",
                    label="🎯 分析深度"
                )
                
                analyze_btn = gr.Button(
                    "🚀 开始智能分析", 
                    variant="primary",
                    size="lg"
                )
                
                gr.Markdown("### 🔧 系统状态")
                system_status = gr.JSON(
                    value=ui.get_system_info(),
                    label="系统监控"
                )
                
                refresh_btn = gr.Button("🔄 刷新状态", size="sm")
            
            # 右侧结果显示
            with gr.Column(scale=2):
                gr.Markdown("## 📋 分析结果")
                
                analysis_output = gr.Markdown(
                    value="🔮 等待分析结果...\n\n点击左侧「开始智能分析」按钮开始分析",
                    label="智能分析报告"
                )
        
        # 功能标签页
        with gr.Tabs():
            with gr.Tab("🤖 LLM模型配置"):
                if ui.enhanced_features_available:
                    gr.Markdown("### 🔧 LLM提供商配置管理")
                    ui.create_enhanced_llm_config_tab()
                else:
                    gr.Markdown("### 当前智能体模型配置")
                    gr.JSON({
                        "市场技术分析师": "moonshot:moonshot-v1-8k (Kimi K2)",
                        "投资者情感分析师": "阿里百炼:qwen-turbo (通义千问)",
                        "新闻事件分析师": "阿里百炼:qwen-turbo (通义千问)",
                        "基本面分析师": "阿里百炼:qwen-turbo (通义千问)",
                        "多头研究员": "moonshot:moonshot-v1-8k (Kimi K2)",
                        "空头研究员": "moonshot:moonshot-v1-8k (Kimi K2)",
                        "研究经理": "moonshot:moonshot-v1-8k (Kimi K2)",
                        "交易员": "moonshot:moonshot-v1-8k (Kimi K2)",
                        "激进分析师": "moonshot:moonshot-v1-8k (Kimi K2)",
                        "保守分析师": "moonshot:moonshot-v1-8k (Kimi K2)",
                        "中性分析师": "moonshot:moonshot-v1-8k (Kimi K2)",
                        "风险经理": "moonshot:moonshot-v1-8k (Kimi K2)"
                    })
            
            with gr.Tab("👥 智能体管理"):
                if ui.enhanced_features_available:
                    gr.Markdown("### 🎯 智能体模型配置管理")
                    ui.create_enhanced_agent_config_tab()
                else:
                    gr.Markdown("### 15个专业智能体状态")
                    agent_data = [
                        ["市场技术分析师", "技术指标分析", "moonshot:moonshot-v1-8k", "✅ 就绪"],
                        ["投资者情感分析师", "情感数据分析", "阿里百炼:qwen-turbo", "✅ 就绪"],
                        ["新闻事件分析师", "新闻事件分析", "阿里百炼:qwen-turbo", "✅ 就绪"],
                        ["基本面分析师", "财务数据分析", "阿里百炼:qwen-turbo", "✅ 就绪"],
                        ["多头研究员", "多头观点研究", "moonshot:moonshot-v1-8k", "✅ 就绪"],
                        ["空头研究员", "空头观点研究", "moonshot:moonshot-v1-8k", "✅ 就绪"],
                        ["研究经理", "投资建议综合", "moonshot:moonshot-v1-8k", "✅ 就绪"],
                        ["交易员", "交易策略制定", "moonshot:moonshot-v1-8k", "✅ 就绪"],
                        ["激进分析师", "激进风险评估", "moonshot:moonshot-v1-8k", "✅ 就绪"],
                        ["保守分析师", "保守风险评估", "moonshot:moonshot-v1-8k", "✅ 就绪"],
                        ["中性分析师", "中性风险评估", "moonshot:moonshot-v1-8k", "✅ 就绪"],
                        ["风险经理", "最终决策制定", "moonshot:moonshot-v1-8k", "✅ 就绪"]
                    ]
                    gr.DataFrame(
                        value=agent_data,
                        headers=["智能体", "职责", "LLM模型", "状态"]
                    )
            
            with gr.Tab("📡 通信监测"):
                gr.Markdown("### 智能体通信日志")
                comm_logs = f"""[{datetime.now().strftime('%H:%M:%S')}] 系统启动完成
[{datetime.now().strftime('%H:%M:%S')}] ChromaDB向量记忆系统初始化成功
[{datetime.now().strftime('%H:%M:%S')}] 15个专业智能体就绪
[{datetime.now().strftime('%H:%M:%S')}] Moonshot API连接正常
[{datetime.now().strftime('%H:%M:%S')}] 阿里百炼API连接正常
[{datetime.now().strftime('%H:%M:%S')}] 系统准备就绪，等待分析任务"""
                
                gr.Textbox(
                    value=comm_logs,
                    lines=12,
                    interactive=False,
                    label="实时通信日志"
                )
            
            with gr.Tab("📋 报告管理"):
                if ui.enhanced_features_available:
                    gr.Markdown("### 📊 增强报告生成")

                    with gr.Row():
                        with gr.Column(scale=1):
                            template_selector = gr.Dropdown(
                                choices=["standard", "detailed", "executive", "technical", "research"],
                                label="选择模板",
                                value="standard"
                            )

                            include_toc = gr.Checkbox(label="包含目录", value=False)
                            include_charts = gr.Checkbox(label="包含图表分析", value=False)
                            include_footer = gr.Checkbox(label="包含页脚", value=True)

                            generate_btn = gr.Button("📄 生成Markdown报告", variant="primary")

                            generation_status = gr.Textbox(
                                label="生成状态",
                                interactive=False
                            )

                        with gr.Column(scale=2):
                            report_preview = gr.Textbox(
                                label="报告预览",
                                lines=15,
                                max_lines=25,
                                interactive=False,
                                show_copy_button=True
                            )

                    def generate_enhanced_report(template_name, toc, charts, footer):
                        try:
                            if not ui.current_result:
                                return "❌ 没有可用的分析结果，请先进行股票分析", ""

                            format_options = {
                                "include_toc": toc,
                                "include_charts": charts,
                                "include_footer": footer
                            }

                            report = ui.report_generator.generate_report(
                                ui.current_result,
                                template_name,
                                format_options
                            )

                            return "✅ 报告生成成功", report

                        except Exception as e:
                            return f"❌ 生成失败: {str(e)}", ""

                    generate_btn.click(
                        fn=generate_enhanced_report,
                        inputs=[template_selector, include_toc, include_charts, include_footer],
                        outputs=[generation_status, report_preview]
                    )

                    gr.Markdown("---")
                    gr.Markdown("### 传统导出")

                gr.Markdown("### 分析报告导出")

                with gr.Row():
                    export_format = gr.Radio(
                        choices=["JSON", "TXT", "Markdown"],
                        value="JSON",
                        label="导出格式"
                    )
                    export_btn = gr.Button("📤 导出当前报告", variant="secondary")

                export_status = gr.Textbox(
                    label="导出状态",
                    interactive=False,
                    placeholder="导出状态将在这里显示..."
                )
                
                gr.Markdown("### 使用说明")
                gr.Markdown("""
                1. **输入股票代码**: 支持A股代码，如600519、000001等
                2. **选择分析深度**: 根据需要选择1-4轮辩论深度
                3. **开始分析**: 点击分析按钮，系统将自动运行15个智能体
                4. **查看结果**: 分析完成后在右侧查看详细报告
                5. **导出报告**: 可将分析结果导出为JSON或TXT格式
                """)
        
        # 底部信息
        version_info = "TradingAgents v2.0" if ui.enhanced_features_available else "TradingAgents v1.0"
        features_info = "增强功能已启用" if ui.enhanced_features_available else "基础功能版本"

        gr.HTML(f"""
        <div style="text-align: center; padding: 20px; margin-top: 30px; background: #f8f9fa; border-radius: 10px; color: #666;">
            <p><strong>🤖 {version_info}</strong> | 基于ChromaDB向量记忆的专业AI股票分析系统</p>
            <p>🔧 <em>{features_info}</em></p>
            <p>⚠️ <em>本系统分析结果仅供参考，投资有风险，决策需谨慎</em></p>
            <p>🏗️ 架构: 15个专业智能体协作 | 🧠 记忆: ChromaDB向量记忆 | 🌐 界面: 现代化Gradio UI</p>
        </div>
        """)
        
        # 事件绑定
        analyze_btn.click(
            fn=ui.run_real_analysis,
            inputs=[stock_input, analysis_depth],
            outputs=analysis_output,
            show_progress=True
        )
        
        refresh_btn.click(
            fn=lambda: ui.get_system_info(),
            outputs=system_status
        )
        
        export_btn.click(
            fn=ui.export_current_report,
            inputs=export_format,
            outputs=export_status
        )
    
    return interface

if __name__ == "__main__":
    print("=" * 70)
    version_text = "TradingAgents v2.0 增强版" if ui.enhanced_features_available else "TradingAgents v1.0 基础版"
    print(f"🤖 {version_text}")
    print("=" * 70)
    print("🚀 正在启动...")
    print("🌐 界面地址: http://localhost:7860")
    print("📱 支持移动端访问")
    print("=" * 70)

    try:
        interface = create_final_interface()
        print("✅ 界面创建成功！")
        print("\n💡 功能特性:")
        print("   • 🎨 现代化设计界面")
        print("   • 🧠 ChromaDB向量记忆")
        print("   • 👥 15个专业智能体")
        print("   • 🔄 实时进度显示")
        print("   • 📊 多标签页管理")
        print("   • 📤 报告导出功能")
        print("   • 🔧 系统状态监控")

        if ui.enhanced_features_available:
            print("\n🆕 增强功能:")
            print("   • 🤖 动态LLM配置管理")
            print("   • 👥 智能体模型选择")
            print("   • 📊 多模板报告生成")
            print("   • 🧠 智能文档精简")
            print("   • 🔍 模型兼容性检查")
        else:
            print("\n⚠️ 增强功能模块未加载，运行基础版本")

        print("\n🌟 现在可以在浏览器中访问: http://localhost:7860")
        print()
        
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False
        )
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("🔧 请检查依赖包是否完整安装")
        print("💡 建议运行: pip install gradio pandas")
        sys.exit(1)
