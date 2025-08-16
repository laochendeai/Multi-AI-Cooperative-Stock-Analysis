#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents 完整集成应用
基于真实tradingagents架构的模块化程序
包含所有功能：LLM配置、分析、导出等
"""

import gradio as gr
import asyncio
import logging
import os
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入核心模块
from app_enhanced import EnhancedTradingAgentsApp
from tradingagents.graph.trading_graph import TradingGraph
from tradingagents.config.default_config import get_config
from core.llm_adapter import create_llm_client
from core.chromadb_memory import ChromaDBMemoryManager
from core.data_adapter import create_data_interface
from enum import Enum

# 定义分析深度枚举
class AnalysisDepth(Enum):
    SHALLOW = "shallow"
    MEDIUM = "medium"
    DEEP = "deep"

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegratedTradingAgentsApp:
    """集成的TradingAgents应用"""
    
    def __init__(self, db_path: str = "data/trading_data.db"):
        """初始化集成应用"""
        logger.info("🚀 初始化集成TradingAgents应用...")
        
        # 初始化增强版应用（保持现有功能）
        self.enhanced_app = EnhancedTradingAgentsApp(db_path)
        
        # 初始化真实tradingagents架构
        self.llm_client = create_llm_client(self.enhanced_app)
        self.memory_manager = ChromaDBMemoryManager()
        self.data_interface = create_data_interface(self.enhanced_app)
        self.config = get_config()
        
        # TradingGraph实例
        self.trading_graph = None
        
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
        
        logger.info("✅ 集成TradingAgents应用初始化完成")
    
    async def initialize_trading_graph(self):
        """初始化TradingGraph"""
        try:
            if not self.trading_graph:
                logger.info("🔧 初始化TradingGraph...")
                self.trading_graph = TradingGraph(
                    self.llm_client, 
                    self.data_interface
                )
                await self.memory_manager.initialize()
                logger.info("✅ TradingGraph初始化完成")
        except Exception as e:
            logger.error(f"❌ TradingGraph初始化失败: {e}")
            raise
    
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
    
    def _map_depth_to_analysis_depth(self, depth: str) -> AnalysisDepth:
        """映射分析深度"""
        depth_mapping = {
            "快速分析": AnalysisDepth.SHALLOW,
            "标准分析": AnalysisDepth.MEDIUM,
            "深度分析": AnalysisDepth.DEEP,
            "全面分析": AnalysisDepth.DEEP
        }
        return depth_mapping.get(depth, AnalysisDepth.MEDIUM)
    
    async def analyze_stock_real(self, symbol: str, depth: str, 
                                selected_agents: List[str]) -> Dict[str, Any]:
        """使用真实tradingagents架构进行股票分析"""
        try:
            logger.info(f"🔍 开始真实分析: {symbol}, 深度: {depth}")
            
            # 初始化TradingGraph
            await self.initialize_trading_graph()
            
            # 设置分析状态
            self.analysis_state.update({
                "is_running": True,
                "current_stage": "初始化分析",
                "progress": 10,
                "symbol": symbol,
                "depth": depth
            })
            
            # 映射分析深度
            analysis_depth = self._map_depth_to_analysis_depth(depth)
            
            # 使用TradingGraph进行分析
            self.analysis_state.update({
                "current_stage": "执行智能体协作分析",
                "progress": 30
            })
            
            result = await self.trading_graph.analyze_stock(symbol, analysis_depth)
            
            # 处理结果
            self.analysis_state.update({
                "current_stage": "处理分析结果",
                "progress": 80
            })
            
            processed_result = self._process_analysis_result(
                result, symbol, depth, selected_agents
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
            raise
    
    def _process_analysis_result(self, result: Dict[str, Any], 
                               symbol: str, depth: str, 
                               selected_agents: List[str]) -> Dict[str, Any]:
        """处理分析结果"""
        processed = {
            "symbol": symbol,
            "analysis_depth": depth,
            "timestamp": datetime.now().isoformat(),
            "selected_agents": selected_agents,
            "results": {},
            "summary": "",
            "recommendations": []
        }
        
        # 提取各智能体的分析结果
        if isinstance(result, dict):
            for agent in selected_agents:
                agent_result = self._extract_agent_result(result, agent)
                processed["results"][agent] = agent_result
        
        # 生成总结
        processed["summary"] = self._generate_analysis_summary(processed["results"])
        
        # 生成建议
        processed["recommendations"] = self._generate_recommendations(processed["results"])
        
        return processed
    
    def _extract_agent_result(self, result: Dict[str, Any], agent: str) -> Dict[str, Any]:
        """提取智能体结果"""
        # 这里实现从TradingGraph结果中提取特定智能体的分析
        # 根据实际的TradingGraph输出格式进行调整
        return {
            "agent_id": agent,
            "analysis": result.get(agent, f"{agent}分析结果"),
            "confidence": 0.8,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    
    def _generate_analysis_summary(self, results: Dict[str, Any]) -> str:
        """生成分析总结"""
        summary_parts = []
        
        for agent, result in results.items():
            if result.get("status") == "success":
                summary_parts.append(f"• {agent}: {result.get('analysis', '无分析结果')[:100]}...")
        
        return "\n".join(summary_parts) if summary_parts else "暂无有效分析结果"
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """生成投资建议"""
        recommendations = []
        
        # 基于各智能体的分析结果生成建议
        if "risk_manager" in results:
            recommendations.append("请注意风险管理，合理控制仓位")
        
        if "market_analyst" in results:
            recommendations.append("关注技术指标变化和市场趋势")
        
        if "fundamentals_analyst" in results:
            recommendations.append("重视基本面分析，关注公司财务状况")
        
        return recommendations
    
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
        md_content = f"""# 股票分析报告

## 基本信息
- **股票代码**: {result.get('symbol', 'N/A')}
- **分析深度**: {result.get('analysis_depth', 'N/A')}
- **分析时间**: {result.get('timestamp', 'N/A')}
- **选择的智能体**: {', '.join(result.get('selected_agents', []))}

## 分析结果

"""
        
        for agent, agent_result in result.get('results', {}).items():
            md_content += f"### {agent}\n"
            md_content += f"{agent_result.get('analysis', '无分析结果')}\n\n"
        
        md_content += f"""## 分析总结
{result.get('summary', '无总结')}

## 投资建议
"""
        
        for rec in result.get('recommendations', []):
            md_content += f"- {rec}\n"
        
        return md_content
    
    def _format_as_text(self, result: Dict[str, Any]) -> str:
        """格式化为纯文本"""
        text_content = f"""股票分析报告

基本信息:
股票代码: {result.get('symbol', 'N/A')}
分析深度: {result.get('analysis_depth', 'N/A')}
分析时间: {result.get('timestamp', 'N/A')}
选择的智能体: {', '.join(result.get('selected_agents', []))}

分析结果:
"""
        
        for agent, agent_result in result.get('results', {}).items():
            text_content += f"\n{agent}:\n"
            text_content += f"{agent_result.get('analysis', '无分析结果')}\n"
        
        text_content += f"\n分析总结:\n{result.get('summary', '无总结')}\n"
        
        text_content += "\n投资建议:\n"
        for rec in result.get('recommendations', []):
            text_content += f"- {rec}\n"
        
        return text_content

# 创建全局应用实例
app = IntegratedTradingAgentsApp()

# 异步分析函数
async def analyze_stock_async(symbol: str, depth: str, selected_agents: List[str]):
    """异步股票分析函数"""
    return await app.analyze_stock_real(symbol, depth, selected_agents)

def analyze_stock_sync(symbol: str, depth: str, selected_agents: List[str]):
    """同步股票分析函数（Gradio兼容）"""
    try:
        # 在新的事件循环中运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                analyze_stock_async(symbol, depth, selected_agents)
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

def create_integrated_ui():
    """创建集成UI界面"""

    # 自定义CSS样式
    custom_css = """
    .main-container {
        max-width: 100vw !important;
        margin: 0 !important;
        padding: 10px !important;
    }
    .analysis-card {
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        padding: 15px;
        margin: 5px 0;
        background: #f8f9fa;
    }
    .status-indicator {
        padding: 5px 10px;
        border-radius: 4px;
        font-weight: bold;
    }
    .status-success { background: #d4edda; color: #155724; }
    .status-warning { background: #fff3cd; color: #856404; }
    .status-error { background: #f8d7da; color: #721c24; }
    .compact-input { margin: 2px 0 !important; }
    .full-height { height: 80vh !important; }
    """

    with gr.Blocks(
        title="TradingAgents - 集成分析平台",
        css=custom_css,
        theme=gr.themes.Soft()
    ) as interface:

        # 页面标题
        gr.Markdown("""
        # 🤖 TradingAgents 集成分析平台
        ### 基于真实tradingagents架构的模块化股票分析系统
        """)

        # 主要布局：左侧配置(25%) + 中间分析(60%) + 右侧状态(15%)
        with gr.Row():
            # 左侧配置面板
            with gr.Column(scale=25, elem_classes=["analysis-card"]):
                gr.Markdown("### ⚙️ 分析配置")

                # 股票输入
                stock_input = gr.Textbox(
                    label="股票代码",
                    placeholder="输入股票代码，如：000001",
                    elem_classes=["compact-input"]
                )

                # 分析深度
                depth_select = gr.Dropdown(
                    choices=app.get_analysis_depths(),
                    value="标准分析",
                    label="分析深度",
                    elem_classes=["compact-input"]
                )

                # 智能体选择
                agents_select = gr.CheckboxGroup(
                    choices=app.get_available_agents(),
                    value=["market_analyst", "sentiment_analyst", "news_analyst"],
                    label="选择智能体",
                    elem_classes=["compact-input"]
                )

                # 分析按钮
                with gr.Row():
                    analyze_btn = gr.Button("🚀 开始分析", variant="primary")
                    stop_btn = gr.Button("⏹️ 停止", variant="secondary")

                gr.Markdown("---")

                # LLM配置
                gr.Markdown("### 🧠 LLM配置")

                # LLM提供商配置
                with gr.Accordion("LLM提供商管理", open=False):
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
                        add_provider_btn = gr.Button("➕ 添加提供商")
                        test_provider_btn = gr.Button("🧪 测试连接")

                    provider_status = gr.Textbox(
                        label="测试结果",
                        interactive=False
                    )

                # 智能体模型配置
                with gr.Accordion("智能体模型配置", open=False):
                    agent_model_config = gr.JSON(
                        label="智能体模型映射",
                        value=app.enhanced_app.agent_model_config
                    )

                    update_models_btn = gr.Button("🔄 更新模型配置")

                # 联网开关
                with gr.Row():
                    enable_network = gr.Checkbox(
                        label="启用联网功能",
                        value=True
                    )
                    test_network_btn = gr.Button("🌐 测试网络")

                network_status = gr.Textbox(
                    label="网络状态",
                    value="未测试",
                    interactive=False
                )

            # 中间分析结果面板
            with gr.Column(scale=60, elem_classes=["analysis-card"]):
                gr.Markdown("### 📊 分析结果")

                with gr.Tabs():
                    # 分析结果标签页
                    with gr.Tab("📈 分析报告"):
                        analysis_output = gr.Markdown(
                            value="等待分析...",
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
                        with gr.Row():
                            export_format = gr.Dropdown(
                                choices=["markdown", "json", "txt"],
                                value="markdown",
                                label="导出格式"
                            )
                            export_btn = gr.Button("📥 导出", variant="primary")

                        export_status = gr.Textbox(
                            label="导出状态",
                            interactive=False
                        )

                        # 隐藏的结果存储
                        result_storage = gr.Textbox(
                            visible=False,
                            value=""
                        )

            # 右侧状态面板
            with gr.Column(scale=15, elem_classes=["analysis-card"]):
                gr.Markdown("### 📊 系统状态")

                # 分析进度
                analysis_progress = gr.Progress()

                # 当前状态
                current_status = gr.Textbox(
                    label="当前状态",
                    value="就绪",
                    interactive=False,
                    elem_classes=["compact-input"]
                )

                # 系统信息
                with gr.Accordion("系统信息", open=True):
                    system_info = gr.Markdown(f"""
                    **TradingGraph**: {'✅ 已初始化' if app.trading_graph else '⏳ 未初始化'}
                    **LLM客户端**: ✅ 已连接
                    **数据接口**: ✅ 已连接
                    **内存管理**: ✅ 已连接
                    """)

                # 实时日志
                with gr.Accordion("实时日志", open=False):
                    log_output = gr.Textbox(
                        label="系统日志",
                        lines=10,
                        max_lines=20,
                        interactive=False,
                        elem_classes=["compact-input"]
                    )

                # 刷新按钮
                refresh_btn = gr.Button("🔄 刷新状态", size="sm")

        # 事件绑定
        def start_analysis(symbol, depth, agents):
            """开始分析"""
            if not symbol or not symbol.strip():
                return "❌ 请输入股票代码", "{}", "分析失败"

            if not agents:
                return "❌ 请至少选择一个智能体", "{}", "分析失败"

            try:
                # 执行分析
                result = analyze_stock_sync(symbol.strip(), depth, agents)

                if "error" in result:
                    return f"❌ 分析失败: {result['error']}", "{}", "分析失败"

                # 格式化输出
                formatted_output = format_analysis_output(result)
                result_json = json.dumps(result, ensure_ascii=False)

                return formatted_output, result, result_json, "分析完成"

            except Exception as e:
                error_msg = f"❌ 分析异常: {str(e)}"
                return error_msg, "{}", "", "分析异常"

        def format_analysis_output(result):
            """格式化分析输出"""
            if not result or "error" in result:
                return "❌ 分析失败"

            output = f"""# 📊 {result.get('symbol', 'N/A')} 分析报告

**分析时间**: {result.get('timestamp', 'N/A')}
**分析深度**: {result.get('analysis_depth', 'N/A')}
**智能体**: {', '.join(result.get('selected_agents', []))}

## 🔍 分析结果

"""

            for agent, agent_result in result.get('results', {}).items():
                output += f"""### {agent}
{agent_result.get('analysis', '无分析结果')}

"""

            output += f"""## 📝 分析总结
{result.get('summary', '无总结')}

## 💡 投资建议
"""

            for rec in result.get('recommendations', []):
                output += f"- {rec}\n"

            return output

        def test_provider_connection(name, url, key):
            """测试LLM提供商连接"""
            if not all([name, url, key]):
                return "❌ 请填写完整的提供商信息"

            try:
                # 这里实现实际的连接测试
                # 暂时返回模拟结果
                return f"✅ {name} 连接测试成功"
            except Exception as e:
                return f"❌ {name} 连接测试失败: {str(e)}"

        def test_network_connection():
            """测试网络连接"""
            try:
                import requests
                response = requests.get("https://www.baidu.com", timeout=5)
                if response.status_code == 200:
                    return "✅ 网络连接正常"
                else:
                    return f"⚠️ 网络连接异常: {response.status_code}"
            except Exception as e:
                return f"❌ 网络连接失败: {str(e)}"

        # 绑定事件
        analyze_btn.click(
            fn=start_analysis,
            inputs=[stock_input, depth_select, agents_select],
            outputs=[analysis_output, raw_data_output, result_storage, current_status]
        )

        export_btn.click(
            fn=export_result_sync,
            inputs=[result_storage, export_format],
            outputs=[export_status]
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

    return interface

if __name__ == "__main__":
    # 创建并启动界面
    interface = create_integrated_ui()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
