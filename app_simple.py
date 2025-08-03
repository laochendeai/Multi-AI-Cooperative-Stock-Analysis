"""
TradingAgents - 简化版多智能体股票分析系统
"""

import gradio as gr
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleTradingAgentsApp:
    """简化版TradingAgents应用"""
    
    def __init__(self):
        self.analysis_sessions = []
        
    async def analyze_stock_simple(self, symbol: str, depth: str, analysts: List[str]) -> Dict[str, Any]:
        """简化的股票分析"""
        try:
            logger.info(f"开始分析股票: {symbol}, 深度: {depth}")
            
            # 模拟分析过程
            await asyncio.sleep(1)  # 模拟分析时间
            
            # 生成模拟结果
            result = {
                "symbol": symbol,
                "status": "completed",
                "depth": depth,
                "start_time": datetime.now().isoformat(),
                "results": {
                    "market_analysis": f"{symbol} 技术分析显示当前处于上升趋势",
                    "sentiment_analysis": "市场情绪偏向乐观",
                    "news_analysis": "近期新闻整体正面",
                    "fundamentals_analysis": "基本面数据良好",
                    "bull_arguments": "多头观点：业绩增长稳定，行业前景良好",
                    "bear_arguments": "空头观点：估值偏高，存在回调风险",
                    "investment_recommendation": "建议：适度买入，目标价位上调10%",
                    "trading_strategy": "分批建仓，设置止损位",
                    "risk_assessment": "中等风险，适合稳健投资者",
                    "final_decision": f"对{symbol}给出买入评级，信心度75%"
                }
            }
            
            # 保存会话
            self.analysis_sessions.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"股票分析失败: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_analysis_history(self) -> List[List[str]]:
        """获取分析历史"""
        history = []
        for session in self.analysis_sessions[-10:]:
            history.append([
                session.get("start_time", "")[:19],
                session.get("symbol", ""),
                session.get("depth", ""),
                session.get("status", ""),
                session.get("results", {}).get("final_decision", "")[:50] + "..."
            ])
        return history

# 创建应用实例
app = SimpleTradingAgentsApp()

def create_simple_interface():
    """创建简化的Gradio界面"""
    
    with gr.Blocks(
        title="TradingAgents - 多智能体股票分析系统", 
        theme=gr.themes.Soft()
    ) as interface:
        
        # 主标题
        gr.Markdown("""
        # 🤖 TradingAgents - 多智能体协作股票分析系统
        
        **基于15个专业化智能体的金融交易分析框架** | 简化演示版本
        
        ---
        """)
        
        with gr.Row():
            # 左侧控制台
            with gr.Column(scale=1):
                gr.Markdown("## 📊 分析控制台")
                
                # 股票输入
                stock_input = gr.Textbox(
                    label="股票代码",
                    placeholder="输入股票代码，如：000001、600036",
                    value="000001"
                )
                
                # 分析深度
                analysis_depth = gr.Dropdown(
                    label="研究深度",
                    choices=["浅层分析", "中等分析", "深度分析"],
                    value="中等分析"
                )
                
                # 分析师选择
                gr.Markdown("### 👥 分析师团队")
                analyst_market = gr.Checkbox(label="📈 市场分析师", value=True)
                analyst_sentiment = gr.Checkbox(label="💭 情感分析师", value=True)
                analyst_news = gr.Checkbox(label="📰 新闻分析师", value=True)
                analyst_fundamentals = gr.Checkbox(label="📊 基本面分析师", value=True)
                
                # 执行按钮
                analyze_btn = gr.Button("🚀 开始全面分析", variant="primary", size="lg")
                
                # 状态显示
                status_display = gr.Textbox(
                    label="分析状态",
                    value="🟢 系统就绪",
                    interactive=False
                )
            
            # 右侧结果展示
            with gr.Column(scale=2):
                gr.Markdown("## 📈 分析结果")
                
                # 结果标签页
                with gr.Tabs():
                    # 综合报告
                    with gr.TabItem("📋 综合报告"):
                        comprehensive_report = gr.Markdown(value="等待分析结果...")
                    
                    # 分析师报告
                    with gr.TabItem("👥 分析师报告"):
                        market_analysis_output = gr.Markdown(value="暂无数据")
                        sentiment_analysis_output = gr.Markdown(value="暂无数据")
                        news_analysis_output = gr.Markdown(value="暂无数据")
                        fundamentals_analysis_output = gr.Markdown(value="暂无数据")
                    
                    # 多空辩论
                    with gr.TabItem("🥊 多空辩论"):
                        bull_arguments = gr.Markdown(value="暂无数据")
                        bear_arguments = gr.Markdown(value="暂无数据")
                        investment_recommendation = gr.Markdown(value="暂无数据")
                    
                    # 交易策略
                    with gr.TabItem("💼 交易策略"):
                        trading_strategy_output = gr.Markdown(value="暂无数据")
                    
                    # 风险评估
                    with gr.TabItem("⚠️ 风险评估"):
                        risk_assessment_output = gr.Markdown(value="暂无数据")
                        final_decision_output = gr.Markdown(value="暂无数据")
        
        # 底部历史记录
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 📚 分析历史")
                
                refresh_history_btn = gr.Button("🔄 刷新历史", size="sm")
                
                history_display = gr.Dataframe(
                    headers=["时间", "股票", "深度", "状态", "决策"],
                    datatype=["str", "str", "str", "str", "str"],
                    value=[]
                )
        
        # 底部信息
        gr.Markdown("""
        ---
        
        ### 💡 使用说明
        
        1. **股票代码**: 输入A股股票代码（如：000001、600036、300750）
        2. **研究深度**: 选择分析的详细程度
        3. **分析师团队**: 选择参与分析的专业智能体
        4. **查看结果**: 在不同标签页查看详细分析结果
        
        ### ⚠️ 免责声明
        
        本系统提供的分析结果仅供参考，不构成投资建议。投资有风险，决策需谨慎。
        
        ---
        
        **TradingAgents v1.0** | Powered by Multi-Agent LLM Framework
        """)
        
        # 事件处理函数
        def run_analysis(symbol, depth, market_checked, sentiment_checked, 
                        news_checked, fundamentals_checked):
            """运行分析"""
            if not symbol:
                return ("❌ 请输入股票代码", "暂无数据", "暂无数据", "暂无数据", 
                       "暂无数据", "暂无数据", "暂无数据", "暂无数据", "暂无数据", "暂无数据")
            
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
                    return ("❌ 请至少选择一个分析师", "暂无数据", "暂无数据", "暂无数据",
                           "暂无数据", "暂无数据", "暂无数据", "暂无数据", "暂无数据", "暂无数据")
                
                # 执行分析 (同步版本)
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                result = loop.run_until_complete(
                    app.analyze_stock_simple(symbol, depth, selected_analysts)
                )
                
                if result.get("status") == "failed":
                    return (f"❌ 分析失败: {result.get('error', '未知错误')}", 
                           "暂无数据", "暂无数据", "暂无数据", "暂无数据", 
                           "暂无数据", "暂无数据", "暂无数据", "暂无数据", "暂无数据")
                
                # 解析结果
                results = result.get("results", {})
                
                # 生成综合报告
                comprehensive = f"""
## 📊 {symbol} 综合分析报告

### 🎯 最终决策
{results.get('final_decision', '暂无决策')}

### 📈 分析概览
- **分析时间**: {result.get('start_time', '')}
- **分析深度**: {depth}
- **分析状态**: ✅ 已完成

### 💡 关键洞察
本次分析由{len(selected_analysts)}个专业智能体协作完成，提供全方位的投资决策支持。

---
*本报告由多智能体协作生成，仅供参考*
"""
                
                return (
                    "✅ 分析完成",
                    comprehensive,
                    f"### 📈 市场技术分析\n{results.get('market_analysis', '暂无数据')}",
                    f"### 💭 社交情感分析\n{results.get('sentiment_analysis', '暂无数据')}",
                    f"### 📰 新闻事件分析\n{results.get('news_analysis', '暂无数据')}",
                    f"### 📊 基本面分析\n{results.get('fundamentals_analysis', '暂无数据')}",
                    f"### 🐂 多头观点\n{results.get('bull_arguments', '暂无数据')}",
                    f"### 🐻 空头观点\n{results.get('bear_arguments', '暂无数据')}",
                    f"### 🎯 投资建议\n{results.get('investment_recommendation', '暂无数据')}",
                    f"### 💼 交易策略\n{results.get('trading_strategy', '暂无数据')}",
                    f"### ⚠️ 风险评估\n{results.get('risk_assessment', '暂无数据')}\n\n### 🎯 最终决策\n{results.get('final_decision', '暂无数据')}"
                )
                
            except Exception as e:
                logger.error(f"分析执行失败: {e}")
                return (f"❌ 系统错误: {str(e)}", "暂无数据", "暂无数据", "暂无数据",
                       "暂无数据", "暂无数据", "暂无数据", "暂无数据", "暂无数据", "暂无数据")
        
        def refresh_history():
            """刷新历史记录"""
            return app.get_analysis_history()
        
        # 绑定事件
        analyze_btn.click(
            fn=run_analysis,
            inputs=[
                stock_input, analysis_depth, analyst_market, analyst_sentiment,
                analyst_news, analyst_fundamentals
            ],
            outputs=[
                status_display, comprehensive_report, market_analysis_output,
                sentiment_analysis_output, news_analysis_output, fundamentals_analysis_output,
                bull_arguments, bear_arguments, investment_recommendation,
                trading_strategy_output, risk_assessment_output
            ]
        )
        
        refresh_history_btn.click(
            fn=refresh_history,
            outputs=[history_display]
        )
        
    return interface

if __name__ == "__main__":
    # 创建并启动界面
    interface = create_simple_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7863,  # 使用不同端口
        share=False,
        debug=True
    )
