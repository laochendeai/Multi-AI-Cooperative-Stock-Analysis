"""
TradingAgents - 多智能体协作股票分析系统
基于15个专业化LLM智能体的金融交易框架
"""

import gradio as gr
import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from tradingagents.graph.trading_graph import TradingGraph, AnalysisDepth
from tradingagents.agents.utils.memory import MemoryManager
from tradingagents.dataflows.interface import DataInterface
from core.llm_orchestrator import GradioLLMOrchestrator
from core.security import SecurityManager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingAgentsApp:
    """TradingAgents主应用"""
    
    def __init__(self):
        self.llm_orchestrator = GradioLLMOrchestrator()
        self.security_manager = SecurityManager()
        self.trading_graph = None
        self.data_interface = DataInterface()
        self.memory_manager = MemoryManager()
        self.analysis_sessions = []
        self.current_session = None
        
    async def initialize(self):
        """初始化应用"""
        try:
            # 初始化记忆系统
            await self.memory_manager.initialize()
            
            # 初始化交易图
            self.trading_graph = TradingGraph(self.llm_orchestrator)
            
            logger.info("TradingAgents应用初始化完成")
            
        except Exception as e:
            logger.error(f"应用初始化失败: {e}")
            raise
    
    async def analyze_stock_comprehensive(self, symbol: str, depth: str, selected_analysts: List[str]) -> Dict[str, Any]:
        """执行全面的股票分析"""
        try:
            logger.info(f"开始全面分析股票: {symbol}, 深度: {depth}")
            
            if not self.trading_graph:
                await self.initialize()
            
            # 转换深度参数
            depth_mapping = {
                "浅层分析": AnalysisDepth.SHALLOW,
                "中等分析": AnalysisDepth.MEDIUM, 
                "深度分析": AnalysisDepth.DEEP
            }
            analysis_depth = depth_mapping.get(depth, AnalysisDepth.MEDIUM)
            
            # 执行分析
            analysis_result = await self.trading_graph.analyze_stock(symbol, analysis_depth)
            
            # 保存会话
            self.current_session = analysis_result
            self.analysis_sessions.append(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"股票分析失败: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """获取市场概览"""
        try:
            return await self.data_interface.get_market_overview()
        except Exception as e:
            logger.error(f"获取市场概览失败: {e}")
            return {"error": str(e)}
    
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """获取分析历史"""
        return self.analysis_sessions[-10:] if self.analysis_sessions else []
    
    def get_agent_status(self) -> Dict[str, Any]:
        """获取智能体状态"""
        if self.trading_graph:
            return self.trading_graph.get_analysis_status()
        return {"status": "未初始化"}

# 创建应用实例
app = TradingAgentsApp()

def create_interface():
    """创建新的Gradio界面"""
    
    with gr.Blocks(
        title="TradingAgents - 多智能体股票分析系统", 
        theme=gr.themes.Soft(),
        css="""
        .main-container { max-width: 1400px; margin: 0 auto; }
        .control-panel { background: #f8f9fa; padding: 20px; border-radius: 10px; }
        .result-panel { background: #ffffff; padding: 20px; border-radius: 10px; }
        .status-good { color: #28a745; }
        .status-warning { color: #ffc107; }
        .status-error { color: #dc3545; }
        """
    ) as interface:
        
        # 主标题
        gr.Markdown("""
        # 🤖 TradingAgents - 多智能体协作股票分析系统
        
        **基于15个专业化智能体的金融交易分析框架** | 提供全方位的股票投资决策支持
        
        ---
        """)
        
        with gr.Row():
            # 左侧控制台
            with gr.Column(scale=1, elem_classes=["control-panel"]):
                gr.Markdown("## 📊 分析控制台")
                
                # 股票输入区域
                with gr.Group():
                    gr.Markdown("### 🎯 目标股票")
                    stock_input = gr.Textbox(
                        label="股票代码",
                        placeholder="输入股票代码，如：000001、600036",
                        value="",
                        info="支持A股股票代码"
                    )
                    
                    search_btn = gr.Button("🔍 搜索股票", size="sm")
                    stock_info_display = gr.JSON(
                        label="股票信息",
                        value={},
                        visible=False
                    )
                
                # 分析配置区域
                with gr.Group():
                    gr.Markdown("### ⚙️ 分析配置")
                    
                    analysis_depth = gr.Dropdown(
                        label="研究深度",
                        choices=["浅层分析", "中等分析", "深度分析"],
                        value="中等分析",
                        info="深度分析包含更多轮辩论和策略回溯"
                    )
                    
                    # 分析师选择
                    gr.Markdown("#### 👥 分析师团队选择")
                    
                    analyst_market = gr.Checkbox(label="📈 市场分析师", value=True)
                    analyst_sentiment = gr.Checkbox(label="💭 情感分析师", value=True)
                    analyst_news = gr.Checkbox(label="📰 新闻分析师", value=True)
                    analyst_fundamentals = gr.Checkbox(label="📊 基本面分析师", value=True)
                    
                    # 研究团队配置
                    gr.Markdown("#### 🔬 研究团队配置")
                    
                    enable_debate = gr.Checkbox(label="🥊 启用多空辩论", value=True)
                    debate_rounds = gr.Slider(
                        label="辩论轮次",
                        minimum=1,
                        maximum=5,
                        value=3,
                        step=1,
                        visible=True
                    )
                    
                    # 风险管理配置
                    gr.Markdown("#### ⚠️ 风险管理配置")
                    
                    risk_tolerance = gr.Dropdown(
                        label="风险偏好",
                        choices=["保守", "平衡", "激进"],
                        value="平衡"
                    )
                
                # 执行按钮
                with gr.Group():
                    analyze_btn = gr.Button(
                        "🚀 开始全面分析", 
                        variant="primary", 
                        size="lg",
                        elem_classes=["analyze-button"]
                    )
                    
                    stop_btn = gr.Button(
                        "⏹️ 停止分析", 
                        variant="stop", 
                        size="sm",
                        visible=False
                    )
                
                # 状态监控
                with gr.Group():
                    gr.Markdown("### 📡 系统状态")
                    
                    status_display = gr.Textbox(
                        label="分析状态",
                        value="🟢 系统就绪",
                        interactive=False,
                        lines=2
                    )
                    
                    agent_status_btn = gr.Button("🔍 查看智能体状态", size="sm")
                    
                    agent_status_display = gr.JSON(
                        label="智能体状态",
                        value={},
                        visible=False
                    )
            
            # 右侧结果展示区域
            with gr.Column(scale=2, elem_classes=["result-panel"]):
                gr.Markdown("## 📈 分析结果")
                
                # 结果标签页
                with gr.Tabs():
                    # 综合报告
                    with gr.TabItem("📋 综合报告"):
                        comprehensive_report = gr.Markdown(
                            value="等待分析结果...",
                            elem_classes=["report-content"]
                        )
                    
                    # 分析师报告
                    with gr.TabItem("👥 分析师报告"):
                        with gr.Accordion("📈 市场技术分析", open=True):
                            market_analysis_output = gr.Markdown(value="暂无数据")
                        
                        with gr.Accordion("💭 社交情感分析", open=False):
                            sentiment_analysis_output = gr.Markdown(value="暂无数据")
                        
                        with gr.Accordion("📰 新闻事件分析", open=False):
                            news_analysis_output = gr.Markdown(value="暂无数据")
                        
                        with gr.Accordion("📊 基本面分析", open=False):
                            fundamentals_analysis_output = gr.Markdown(value="暂无数据")
                    
                    # 研究辩论
                    with gr.TabItem("🥊 多空辩论"):
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown("### 🐂 多头观点")
                                bull_arguments = gr.Markdown(value="暂无数据")
                            
                            with gr.Column():
                                gr.Markdown("### 🐻 空头观点")
                                bear_arguments = gr.Markdown(value="暂无数据")
                        
                        gr.Markdown("### 🎯 投资建议")
                        investment_recommendation = gr.Markdown(value="暂无数据")
                    
                    # 交易策略
                    with gr.TabItem("💼 交易策略"):
                        trading_strategy_output = gr.Markdown(value="暂无数据")
                    
                    # 风险评估
                    with gr.TabItem("⚠️ 风险评估"):
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown("#### 🔴 激进观点")
                                aggressive_view = gr.Markdown(value="暂无数据")
                            
                            with gr.Column():
                                gr.Markdown("#### 🟡 中性观点")
                                neutral_view = gr.Markdown(value="暂无数据")
                            
                            with gr.Column():
                                gr.Markdown("#### 🔵 保守观点")
                                conservative_view = gr.Markdown(value="暂无数据")
                        
                        gr.Markdown("### 🎯 最终决策")
                        final_decision_output = gr.Markdown(value="暂无数据")
                    
                    # 数据详情
                    with gr.TabItem("📊 原始数据"):
                        raw_data_output = gr.JSON(
                            label="完整分析数据",
                            value={}
                        )
        
        # 底部功能区域
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 📚 分析历史")
                
                with gr.Row():
                    refresh_history_btn = gr.Button("🔄 刷新历史", size="sm")
                    clear_history_btn = gr.Button("🗑️清空历史", size="sm")
                
                history_display = gr.Dataframe(
                    headers=["时间", "股票", "深度", "状态", "决策"],
                    datatype=["str", "str", "str", "str", "str"],
                    value=[],
                    interactive=False
                )
            
            with gr.Column():
                gr.Markdown("## 🌐 市场概览")
                
                market_overview_btn = gr.Button("📊 获取市场概览", size="sm")
                market_overview_display = gr.JSON(
                    label="市场概览数据",
                    value={}
                )
        
        # 底部信息
        gr.Markdown("""
        ---
        
        ### 💡 使用说明
        
        1. **股票代码**: 输入A股股票代码（如：000001、600036、300750）
        2. **研究深度**: 
           - 浅层分析：1轮辩论，快速分析
           - 中等分析：3轮辩论，平衡分析
           - 深度分析：5轮辩论，包含策略回溯
        3. **分析师团队**: 可选择参与分析的专业智能体
        4. **风险管理**: 三种风险偏好对应不同的投资策略
        
        ### ⚠️ 免责声明
        
        本系统提供的分析结果仅供参考，不构成投资建议。投资有风险，决策需谨慎。
        
        ---
        
        **TradingAgents v1.0** | Powered by Multi-Agent LLM Framework
        """)
        
        # 事件处理函数
        async def run_comprehensive_analysis(symbol, depth, market_checked, sentiment_checked,
                                           news_checked, fundamentals_checked, progress=gr.Progress()):
            """运行全面分析"""
            if not symbol:
                return "❌ 请输入股票代码", {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}

            try:
                # 准备分析师列表
                selected_analysts = []
                if market_checked:
                    selected_analysts.append("market_analyst")
                if sentiment_checked:
                    selected_analysts.append("sentiment_analyst")
                if news_checked:
                    selected_analysts.append("news_analyst")
                if fundamentals_checked:
                    selected_analysts.append("fundamentals_analyst")

                if not selected_analysts:
                    return "❌ 请至少选择一个分析师", {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}

                # 更新状态
                progress(0.1, desc="🔄 初始化分析系统...")

                # 执行分析
                result = await app.analyze_stock_comprehensive(symbol, depth, selected_analysts)

                if result.get("status") == "failed":
                    return f"❌ 分析失败: {result.get('error', '未知错误')}", {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}

                progress(1.0, desc="✅ 分析完成")

                # 解析结果
                return parse_analysis_results(result)

            except Exception as e:
                logger.error(f"分析执行失败: {e}")
                return f"❌ 系统错误: {str(e)}", {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}

        def parse_analysis_results(result):
            """解析分析结果"""
            try:
                # 提取各部分结果
                results = result.get("results", {})

                # 综合报告
                comprehensive = generate_comprehensive_report(result)

                # 分析师报告
                analyst_reports = results.get("analyst_reports", {})
                market_report = format_analyst_report(analyst_reports.get("market_analysis", {}))
                sentiment_report = format_analyst_report(analyst_reports.get("sentiment_analysis", {}))
                news_report = format_analyst_report(analyst_reports.get("news_analysis", {}))
                fundamentals_report = format_analyst_report(analyst_reports.get("fundamentals_analysis", {}))

                # 研究辩论
                research_results = results.get("research_results", {})
                bull_args = format_research_report(research_results.get("bull_research", {}))
                bear_args = format_research_report(research_results.get("bear_research", {}))
                investment_rec = format_investment_recommendation(research_results.get("investment_recommendation", {}))

                # 交易策略
                trading_strategy = format_trading_strategy(results.get("trading_strategy", {}))

                # 风险评估
                final_decision = results.get("final_decision", {})
                aggressive_analysis = format_risk_analysis(final_decision.get("aggressive_analysis", {}))
                neutral_analysis = format_risk_analysis(final_decision.get("neutral_analysis", {}))
                conservative_analysis = format_risk_analysis(final_decision.get("conservative_analysis", {}))
                final_dec = format_final_decision(final_decision.get("final_decision", {}))

                # 原始数据
                raw_data = result

                return (
                    "✅ 分析完成",
                    comprehensive,
                    market_report,
                    sentiment_report,
                    news_report,
                    fundamentals_report,
                    bull_args,
                    bear_args,
                    investment_rec,
                    trading_strategy,
                    aggressive_analysis,
                    neutral_analysis,
                    conservative_analysis,
                    final_dec,
                    raw_data
                )

            except Exception as e:
                logger.error(f"解析结果失败: {e}")
                return f"❌ 结果解析失败: {str(e)}", {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}

        # 格式化函数
        def generate_comprehensive_report(result):
            """生成综合报告"""
            symbol = result.get("symbol", "")
            status = result.get("status", "")

            if status != "completed":
                return f"## 📊 {symbol} 综合分析报告\n\n❌ 分析未完成"

            # 提取关键信息
            results = result.get("results", {})
            final_decision = results.get("final_decision", {}).get("final_decision", {}).get("content", {})

            decision = final_decision.get("final_decision", "HOLD")
            confidence = final_decision.get("decision_confidence", 0.5)
            position = final_decision.get("final_position", "待定")

            report = f"""
## 📊 {symbol} 综合分析报告

### 🎯 最终决策
- **投资决策**: {decision}
- **建议仓位**: {position}
- **信心水平**: {confidence:.1%}

### 📈 分析概览
- **分析时间**: {result.get('start_time', '')}
- **分析深度**: {result.get('depth', '')}
- **分析状态**: ✅ 已完成

### 💡 关键洞察
{final_decision.get('decision_rationale', '暂无详细说明')}

---
*本报告由15个专业智能体协作生成，仅供参考*
"""
            return report

        def format_analyst_report(report_data):
            """格式化分析师报告"""
            if not report_data or report_data.get("status") != "success":
                return "❌ 分析失败或数据不可用"

            content = report_data.get("content", {})
            agent_type = report_data.get("agent_type", "分析师")

            return f"""
### {agent_type}报告

**分析摘要**: {content.get('analysis_summary', '暂无摘要')[:200]}...

**关键发现**: {content.get('key_findings', '暂无')}

**置信度**: {content.get('confidence_score', 0.5):.1%}
"""

        def format_research_report(research_data):
            """格式化研究报告"""
            if not research_data or research_data.get("status") != "success":
                return "❌ 研究数据不可用"

            content = research_data.get("content", {})

            return f"""
### 研究观点

**投资主题**: {content.get('investment_thesis', '暂无')}

**关键论据**:
{format_list(content.get('key_arguments', []))}

**信念强度**: {content.get('conviction_level', 0.5):.1%}
"""

        def format_investment_recommendation(rec_data):
            """格式化投资建议"""
            if not rec_data or rec_data.get("status") != "success":
                return "❌ 投资建议不可用"

            content = rec_data.get("content", {})

            return f"""
### 投资建议

**评级**: {content.get('investment_recommendation', '中性')}
**建议仓位**: {content.get('position_size', '待定')}
**投资时间**: {content.get('time_horizon', '待定')}
**信心水平**: {content.get('confidence_level', 0.5):.1%}

**决策理由**: {content.get('decision_rationale', '暂无详细说明')}
"""

        def format_trading_strategy(strategy_data):
            """格式化交易策略"""
            if not strategy_data or strategy_data.get("status") != "success":
                return "❌ 交易策略不可用"

            content = strategy_data.get("content", {})

            return f"""
### 交易策略

**交易行动**: {content.get('trading_action', '观望')}
**建议仓位**: {content.get('position_size', '待定')}
**预期收益**: {content.get('expected_return', '待评估')}
**最大风险**: {content.get('max_risk', '5%')}

**入场策略**: {content.get('entry_strategy', {}).get('method', '灵活建仓')}
**风险控制**: {content.get('risk_management', {}).get('max_loss', '5%')}

**策略理由**: {content.get('strategy_rationale', '暂无详细说明')}
"""

        def format_risk_analysis(risk_data):
            """格式化风险分析"""
            if not risk_data or risk_data.get("status") != "success":
                return "❌ 风险分析不可用"

            content = risk_data.get("content", {})
            stance = risk_data.get("stance", "中性")

            return f"""
### {stance.upper()}观点

**风险评估**: {content.get('risk_assessment', '中等风险')}
**仓位建议**: {content.get('position_recommendation', '待定')}

**主要观点**: {content.get('summary', '暂无详细说明')[:200]}...
"""

        def format_final_decision(decision_data):
            """格式化最终决策"""
            if not decision_data or decision_data.get("status") != "success":
                return "❌ 最终决策不可用"

            content = decision_data.get("content", {})

            return f"""
### 🎯 最终投资决策

**决策**: {content.get('final_decision', 'HOLD')}
**仓位**: {content.get('final_position', '待定')}
**信心度**: {content.get('decision_confidence', 0.5):.1%}

**风险评估**: {content.get('risk_assessment', {}).get('risk_level', '中等')}风险
**团队共识**: {content.get('team_consensus', '部分共识')}

**决策理由**: {content.get('decision_rationale', '暂无详细说明')}

**执行计划**: {content.get('execution_plan', {}).get('timing', '正常执行')}
"""

        def format_list(items):
            """格式化列表"""
            if not items:
                return "暂无数据"
            return "\n".join([f"- {item}" for item in items[:5]])

        # 其他事件处理函数
        def search_stock(symbol):
            """搜索股票信息"""
            if not symbol:
                return {}, False

            # 这里可以调用数据接口获取股票基本信息
            stock_info = {
                "symbol": symbol,
                "name": f"{symbol}股票",
                "market": "A股",
                "status": "正常交易"
            }
            return stock_info, True

        def get_agent_status():
            """获取智能体状态"""
            status = app.get_agent_status()
            return status, True

        def refresh_history():
            """刷新历史记录"""
            history = app.get_analysis_history()

            # 转换为表格格式
            table_data = []
            for session in history:
                table_data.append([
                    session.get("start_time", "")[:19],
                    session.get("symbol", ""),
                    session.get("depth", ""),
                    session.get("status", ""),
                    session.get("results", {}).get("final_decision", {}).get("final_decision", {}).get("content", {}).get("final_decision", "")
                ])

            return table_data

        async def get_market_overview():
            """获取市场概览"""
            try:
                overview = await app.get_market_overview()
                return overview
            except Exception as e:
                return {"error": str(e)}

        # 绑定事件
        analyze_btn.click(
            fn=run_comprehensive_analysis,
            inputs=[
                stock_input, analysis_depth, analyst_market, analyst_sentiment,
                analyst_news, analyst_fundamentals
            ],
            outputs=[
                status_display, comprehensive_report, market_analysis_output,
                sentiment_analysis_output, news_analysis_output, fundamentals_analysis_output,
                bull_arguments, bear_arguments, investment_recommendation,
                trading_strategy_output, aggressive_view, neutral_view,
                conservative_view, final_decision_output, raw_data_output
            ]
        )

        search_btn.click(
            fn=search_stock,
            inputs=[stock_input],
            outputs=[stock_info_display]
        )

        agent_status_btn.click(
            fn=get_agent_status,
            outputs=[agent_status_display]
        )

        refresh_history_btn.click(
            fn=refresh_history,
            outputs=[history_display]
        )

        market_overview_btn.click(
            fn=get_market_overview,
            outputs=[market_overview_display]
        )

    return interface

if __name__ == "__main__":
    # 创建并启动界面
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7861,  # 使用不同端口避免冲突
        share=False,
        debug=True
    )
