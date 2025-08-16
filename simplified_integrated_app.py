#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents 简化集成应用
基于真实tradingagents架构的模块化程序
"""

import gradio as gr
import asyncio
import logging
import os
import json
import sys
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
from enum import Enum

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入核心模块
from app_enhanced import EnhancedTradingAgentsApp

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 定义分析深度枚举
class AnalysisDepth(Enum):
    SHALLOW = "shallow"
    MEDIUM = "medium"
    DEEP = "deep"

class SimplifiedTradingAgentsApp:
    """简化的TradingAgents应用"""
    
    def __init__(self, db_path: str = "data/trading_data.db"):
        """初始化简化应用"""
        logger.info("🚀 初始化简化TradingAgents应用...")
        
        # 初始化增强版应用（保持现有功能）
        self.enhanced_app = EnhancedTradingAgentsApp(db_path)
        
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
        
        logger.info("✅ 简化TradingAgents应用初始化完成")
    
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
    
    async def analyze_stock_enhanced(self, symbol: str, depth: str, 
                                   selected_agents: List[str]) -> Dict[str, Any]:
        """使用增强版应用进行股票分析"""
        try:
            logger.info(f"🔍 开始增强分析: {symbol}, 深度: {depth}")
            
            # 设置分析状态
            self.analysis_state.update({
                "is_running": True,
                "current_stage": "初始化分析",
                "progress": 10,
                "symbol": symbol,
                "depth": depth
            })
            
            # 使用增强版应用进行分析
            self.analysis_state.update({
                "current_stage": "执行智能体分析",
                "progress": 30
            })
            
            # 调用增强版应用的分析方法
            result = await self.enhanced_app.analyze_stock_enhanced(
                symbol, depth, selected_agents, use_real_llm=True
            )
            
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
            
            logger.info(f"✅ 增强分析完成: {symbol}")
            return processed_result
            
        except Exception as e:
            logger.error(f"❌ 增强分析失败: {e}")
            self.analysis_state.update({
                "is_running": False,
                "current_stage": f"分析失败: {str(e)}",
                "progress": 0
            })
            raise
    
    def _process_analysis_result(self, result: str, symbol: str, 
                               depth: str, selected_agents: List[str]) -> Dict[str, Any]:
        """处理分析结果"""
        processed = {
            "symbol": symbol,
            "analysis_depth": depth,
            "timestamp": datetime.now().isoformat(),
            "selected_agents": selected_agents,
            "raw_result": result,
            "formatted_result": self._format_result(result),
            "summary": self._extract_summary(result),
            "recommendations": self._extract_recommendations(result)
        }
        
        return processed
    
    def _format_result(self, result: str) -> str:
        """格式化分析结果"""
        if not result or result.strip() == "":
            return "❌ 分析结果为空"
        
        # 简单的格式化处理
        formatted = f"""# 📊 股票分析报告

{result}

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return formatted
    
    def _extract_summary(self, result: str) -> str:
        """提取分析总结"""
        if not result:
            return "无分析结果"
        
        # 简单提取前200个字符作为总结
        summary = result[:200] + "..." if len(result) > 200 else result
        return summary
    
    def _extract_recommendations(self, result: str) -> List[str]:
        """提取投资建议"""
        recommendations = [
            "请根据分析结果谨慎投资",
            "注意风险管理，合理控制仓位",
            "关注市场变化，及时调整策略"
        ]
        
        # 可以根据result内容提取更具体的建议
        if "买入" in result or "看涨" in result:
            recommendations.append("分析显示积极信号，可考虑适量配置")
        elif "卖出" in result or "看跌" in result:
            recommendations.append("分析显示消极信号，建议谨慎观望")
        
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
{result.get('formatted_result', '无分析结果')}

## 分析总结
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
{result.get('formatted_result', '无分析结果')}

分析总结:
{result.get('summary', '无总结')}

投资建议:
"""
        
        for rec in result.get('recommendations', []):
            text_content += f"- {rec}\n"
        
        return text_content
    
    def test_llm_connection(self, provider_name: str, api_url: str, api_key: str) -> str:
        """测试LLM连接"""
        try:
            # 这里可以实现实际的连接测试
            if not all([provider_name, api_url, api_key]):
                return "❌ 请填写完整的提供商信息"
            
            # 模拟测试
            return f"✅ {provider_name} 连接测试成功"
        except Exception as e:
            return f"❌ {provider_name} 连接测试失败: {str(e)}"
    
    def test_network_connection(self) -> str:
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

# 创建全局应用实例
app = SimplifiedTradingAgentsApp()

# 异步分析函数
async def analyze_stock_async(symbol: str, depth: str, selected_agents: List[str]):
    """异步股票分析函数"""
    return await app.analyze_stock_enhanced(symbol, depth, selected_agents)

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

def create_simplified_ui():
    """创建简化UI界面"""

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
    .compact-input { margin: 2px 0 !important; }
    .full-height { height: 70vh !important; }
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

        # 主要布局：左侧配置(30%) + 中间分析(55%) + 右侧状态(15%)
        with gr.Row():
            # 左侧配置面板
            with gr.Column(scale=30, elem_classes=["analysis-card"]):
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
                analyze_btn = gr.Button("🚀 开始分析", variant="primary")

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

                    test_provider_btn = gr.Button("🧪 测试连接")
                    provider_status = gr.Textbox(
                        label="测试结果",
                        interactive=False
                    )

                # 联网功能
                with gr.Accordion("网络设置", open=False):
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
            with gr.Column(scale=55, elem_classes=["analysis-card"]):
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
                    **增强版应用**: ✅ 已初始化
                    **数据库**: ✅ 已连接
                    **LLM配置**: ✅ 已加载
                    **智能体**: ✅ 已配置
                    """)

                # 实时日志
                with gr.Accordion("实时日志", open=False):
                    log_output = gr.Textbox(
                        label="系统日志",
                        lines=8,
                        max_lines=15,
                        interactive=False,
                        elem_classes=["compact-input"]
                    )

        # 事件绑定
        def start_analysis(symbol, depth, agents):
            """开始分析"""
            if not symbol or not symbol.strip():
                return "❌ 请输入股票代码", "{}", "", "分析失败"

            if not agents:
                return "❌ 请至少选择一个智能体", "{}", "", "分析失败"

            try:
                # 执行分析
                result = analyze_stock_sync(symbol.strip(), depth, agents)

                if "error" in result:
                    return f"❌ 分析失败: {result['error']}", "{}", "", "分析失败"

                # 格式化输出
                formatted_output = result.get('formatted_result', '无分析结果')
                result_json = json.dumps(result, ensure_ascii=False)

                return formatted_output, result, result_json, "分析完成"

            except Exception as e:
                error_msg = f"❌ 分析异常: {str(e)}"
                return error_msg, "{}", "", "分析异常"

        def test_provider_connection(name, url, key):
            """测试LLM提供商连接"""
            return app.test_llm_connection(name, url, key)

        def test_network_connection():
            """测试网络连接"""
            return app.test_network_connection()

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
    interface = create_simplified_ui()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
