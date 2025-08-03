import gradio as gr
import asyncio
import json
import re
import time
from typing import Dict, Any, List
from core.llm_orchestrator import GradioLLMOrchestrator
from core.secure_data_manager import DataSourceAuthManager

class TradingAgentsGradioApp:
    def __init__(self):
        self.orchestrator = GradioLLMOrchestrator()
        self.data_manager = DataSourceAuthManager()
        self.app_state = {}
    
    async def process_user_input(self, message: str, history: List, context_state: Dict) -> tuple:
        """处理用户输入的主函数"""
        try:
            # 更新上下文
            context_state.update({
                'user_message': message,
                'timestamp': time.time(),
                'session_id': context_state.get('session_id', 'default')
            })
            
            # 并行处理LLM协作
            llm_results = await self.orchestrator.process_parallel(message, context_state)
            
            # 如果需要数据，获取股票数据
            if self._requires_stock_data(message):
                stock_symbol = self._extract_stock_symbol(message)
                stock_data = await self.data_manager.get_data_with_fallback(
                    'akshare', 
                    {'symbol': stock_symbol}
                )
                llm_results['stock_data'] = stock_data
            
            # 格式化响应
            response = self._format_response(llm_results)
            
            # 更新历史记录
            history.append([message, response])
            
            # 更新上下文状态
            context_state['last_response'] = llm_results
            context_state['conversation_count'] = context_state.get('conversation_count', 0) + 1
            
            return history, context_state, ""
            
        except Exception as e:
            error_response = f"处理请求时发生错误: {str(e)}"
            history.append([message, error_response])
            return history, context_state, ""

    def process_user_input_sync(self, message: str, history: List, context_state: Dict) -> tuple:
        """同步包装器用于Gradio调用"""
        try:
            # 创建新的事件循环或使用现有的
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            return loop.run_until_complete(
                self.process_user_input(message, history, context_state)
            )
        except Exception as e:
            error_response = f"处理请求时发生错误: {str(e)}"
            history.append([message, error_response])
            return history, context_state, ""

    def _requires_stock_data(self, message: str) -> bool:
        """判断是否需要股票数据"""
        stock_keywords = ['股票', '股价', '行情', 'stock', 'price', '分析']
        return any(keyword in message.lower() for keyword in stock_keywords)
    
    def _extract_stock_symbol(self, message: str) -> str:
        """从消息中提取股票代码"""
        # 简单的股票代码提取逻辑
        pattern = r'[A-Z]{2,5}|[0-9]{6}'
        matches = re.findall(pattern, message.upper())
        return matches[0] if matches else 'AAPL'
    
    def _format_response(self, results: Dict) -> str:
        """格式化响应结果"""
        if results.get('status') == 'error':
            return f"❌ 分析失败: {results.get('error', '未知错误')}"
        
        response_parts = []
        
        # 添加摘要
        if results.get('summary'):
            response_parts.append(f"📊 **综合分析摘要**\n{results['summary']}\n")
        
        # 添加各个AI引擎的结果
        for i, result in enumerate(results.get('results', []), 1):
            if result.get('status') == 'success':
                provider = result.get('provider', f'AI引擎{i}')
                content = result.get('content', '')
                response_parts.append(f"🤖 **{provider}分析**\n{content}\n")
        
        # 添加股票数据
        if 'stock_data' in results:
            stock_info = results['stock_data']
            if stock_info.get('status') == 'success':
                data = stock_info['data']
                response_parts.append(
                    f"📈 **实时数据** (来源: {stock_info.get('source', 'unknown')})\n"
                    f"代码: {data.get('symbol', 'N/A')}\n"
                    f"价格: ${data.get('price', 'N/A')}\n"
                    f"涨跌: {data.get('change', 'N/A')}%\n"
                )
        
        return "\n".join(response_parts) if response_parts else "🤔 暂无分析结果"
    
    def create_interface(self):
        """创建Gradio界面"""
        with gr.Blocks(
            title="🔐 TradingAgents - 多AI协作股票分析系统",
            theme=gr.themes.Soft(),
            css="""
            .gradio-container {
                max-width: 1200px !important;
            }
            .chat-message {
                border-radius: 10px;
                padding: 10px;
                margin: 5px 0;
            }
            """
        ) as interface:
            
            # 状态管理
            context_state = gr.State({
                'session_id': 'default',
                'conversation_count': 0,
                'initialized': False
            })
            
            # 标题和说明
            gr.Markdown("""
            # 🔐 TradingAgents - 多AI协作股票分析系统
            
            **零知识迁移版本** | 基于Gradio的安全多LLM协作平台
            
            ✨ **功能特色**:
            - 🤖 5个AI引擎并行协作分析
            - 📊 实时股票数据获取
            - 🔒 企业级安全架构
            - ⚡ 异步高性能处理
            """)
            
            with gr.Row():
                with gr.Column(scale=3):
                    # 主聊天界面
                    chatbot = gr.Chatbot(
                        label="AI分析助手",
                        height=500,
                        show_label=True,
                        container=True,
                        bubble_full_width=False
                    )
                    
                    # 输入区域
                    with gr.Row():
                        msg_input = gr.Textbox(
                            label="输入您的分析需求",
                            placeholder="例如: 分析AAPL股票的投资价值...",
                            lines=2,
                            scale=4
                        )
                        send_btn = gr.Button("🚀 发送", scale=1, variant="primary")
                
                with gr.Column(scale=1):
                    # 系统状态面板
                    gr.Markdown("### 📊 系统状态")
                    
                    system_status = gr.JSON(
                        label="实时状态",
                        value={
                            "🤖 AI引擎": "就绪",
                            "📡 数据源": "连接中",
                            "🔒 安全状态": "正常",
                            "⚡ 响应时间": "< 2s"
                        }
                    )
                    
                    # 快捷操作
                    gr.Markdown("### ⚡ 快捷分析")
                    
                    quick_analysis_btn = gr.Button("📈 市场概览", size="sm")
                    tech_analysis_btn = gr.Button("🔍 技术分析", size="sm") 
                    news_analysis_btn = gr.Button("📰 新闻情感", size="sm")
                    
                    # 设置面板
                    with gr.Accordion("⚙️ 高级设置", open=False):
                        llm_selection = gr.CheckboxGroup(
                            choices=["主分析引擎", "情感分析", "代码生成", "多模态", "轻量级"],
                            value=["主分析引擎", "情感分析"],
                            label="启用的AI引擎"
                        )
                        
                        data_sources = gr.CheckboxGroup(
                            choices=["AKShare", "Finnhub", "Alpha Vantage"],
                            value=["AKShare", "Finnhub"],
                            label="数据源"
                        )
            
            # 事件绑定
            def handle_message(message, history, context):
                return self.process_user_input_sync(message, history, context)

            # 发送按钮事件
            send_btn.click(
                fn=handle_message,
                inputs=[msg_input, chatbot, context_state],
                outputs=[chatbot, context_state, msg_input],
                show_progress=True
            )

            # 回车发送
            msg_input.submit(
                fn=handle_message,
                inputs=[msg_input, chatbot, context_state],
                outputs=[chatbot, context_state, msg_input],
                show_progress=True
            )
            
            # 快捷按钮事件
            def quick_market_overview():
                return "请分析当前市场整体走势和热点板块"
            
            def quick_tech_analysis():
                return "请对主要指数进行技术分析，包括支撑阻力位"
            
            def quick_news_sentiment():
                return "请分析最新财经新闻的市场情感倾向"
            
            quick_analysis_btn.click(
                fn=quick_market_overview,
                outputs=msg_input
            )
            
            tech_analysis_btn.click(
                fn=quick_tech_analysis,
                outputs=msg_input
            )
            
            news_analysis_btn.click(
                fn=quick_news_sentiment,
                outputs=msg_input
            )
        
        return interface

# 应用启动
def main():
    app = TradingAgentsGradioApp()
    interface = app.create_interface()
    
    # 启动应用
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True,
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    main()