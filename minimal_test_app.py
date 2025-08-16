#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最小化测试应用
测试Gradio界面是否能正常启动
"""

import gradio as gr
import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_analysis(symbol, depth, agents):
    """测试分析函数"""
    if not symbol:
        return "❌ 请输入股票代码", "{}"
    
    # 模拟分析结果
    result = {
        "symbol": symbol,
        "depth": depth,
        "agents": agents,
        "result": f"这是 {symbol} 的模拟分析结果"
    }
    
    formatted = f"""# 📊 {symbol} 分析报告

**分析深度**: {depth}
**选择的智能体**: {', '.join(agents) if agents else '无'}

## 分析结果
这是一个模拟的分析结果，用于测试界面功能。

## 投资建议
- 请谨慎投资
- 注意风险控制
"""
    
    return formatted, result

def create_minimal_ui():
    """创建最小化UI"""
    
    with gr.Blocks(title="TradingAgents - 测试版") as interface:
        
        gr.Markdown("# 🤖 TradingAgents 测试版")
        
        with gr.Row():
            # 左侧输入
            with gr.Column(scale=1):
                gr.Markdown("### 输入配置")
                
                stock_input = gr.Textbox(
                    label="股票代码",
                    placeholder="如：000001"
                )
                
                depth_select = gr.Dropdown(
                    choices=["快速分析", "标准分析", "深度分析"],
                    value="标准分析",
                    label="分析深度"
                )
                
                agents_select = gr.CheckboxGroup(
                    choices=["market_analyst", "sentiment_analyst", "news_analyst"],
                    value=["market_analyst"],
                    label="选择智能体"
                )
                
                analyze_btn = gr.Button("开始分析", variant="primary")
            
            # 右侧输出
            with gr.Column(scale=2):
                gr.Markdown("### 分析结果")
                
                with gr.Tabs():
                    with gr.Tab("分析报告"):
                        analysis_output = gr.Markdown("等待分析...")
                    
                    with gr.Tab("原始数据"):
                        raw_output = gr.JSON()
        
        # 绑定事件
        analyze_btn.click(
            fn=test_analysis,
            inputs=[stock_input, depth_select, agents_select],
            outputs=[analysis_output, raw_output]
        )
    
    return interface

if __name__ == "__main__":
    print("🚀 启动最小化测试应用...")
    interface = create_minimal_ui()
    print("🌐 正在启动服务器...")
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
