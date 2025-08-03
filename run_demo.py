"""
TradingAgents 演示启动脚本
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def check_dependencies():
    """检查依赖项"""
    required_packages = [
        'gradio',
        'asyncio',
        'datetime',
        'typing'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"缺少依赖包: {missing_packages}")
        logger.info("请运行: pip install gradio")
        return False
    
    return True

def create_demo_config():
    """创建演示配置"""
    config_dir = project_root / "config"
    config_dir.mkdir(exist_ok=True)
    
    # 创建基本配置文件
    demo_config = {
        "llm": {
            "provider": "demo",
            "model": "demo-model",
            "api_key": "demo-key"
        },
        "data": {
            "sources": ["demo"],
            "cache_enabled": True
        },
        "agents": {
            "enabled": True,
            "debug_mode": True
        }
    }
    
    return demo_config

def run_simple_demo():
    """运行简单演示"""
    import gradio as gr
    
    def demo_analysis(symbol, analysis_type):
        """演示分析函数"""
        if not symbol:
            return "请输入股票代码"
        
        # 模拟分析结果
        demo_result = f"""
# 📊 {symbol} 股票分析报告 (演示模式)

## 🎯 分析概览
- **股票代码**: {symbol}
- **分析类型**: {analysis_type}
- **分析时间**: 2024-01-01 10:00:00
- **系统状态**: 演示模式

## 📈 技术分析
- **当前价格**: ¥50.00 (模拟数据)
- **涨跌幅**: +2.5%
- **成交量**: 1,000,000股
- **技术指标**: RSI: 55, MACD: 正向

## 📊 基本面分析
- **市盈率**: 25.5
- **市净率**: 3.2
- **ROE**: 15%
- **财务状况**: 良好

## 💭 市场情绪
- **投资者情绪**: 乐观
- **新闻情感**: 正面
- **社交媒体**: 积极讨论

## 🎯 投资建议
- **评级**: 买入
- **目标价**: ¥55.00
- **风险等级**: 中等
- **投资时间**: 3-6个月

## ⚠️ 风险提示
本分析结果为演示数据，仅供系统功能展示使用。
实际投资请基于真实数据和专业分析。

---
*TradingAgents 演示系统 v1.0*
"""
        return demo_result
    
    # 创建简单界面
    with gr.Blocks(title="TradingAgents 演示系统", theme=gr.themes.Soft()) as demo:
        
        gr.Markdown("""
        # 🤖 TradingAgents 演示系统
        
        **多智能体协作股票分析框架演示版本**
        
        ⚠️ **注意**: 这是演示版本，使用模拟数据，不提供真实的投资建议。
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## 📊 分析控制台")
                
                stock_input = gr.Textbox(
                    label="股票代码",
                    placeholder="输入股票代码，如：000001",
                    value="000001"
                )
                
                analysis_type = gr.Dropdown(
                    label="分析类型",
                    choices=["综合分析", "技术分析", "基本面分析", "情绪分析"],
                    value="综合分析"
                )
                
                analyze_btn = gr.Button("🚀 开始分析", variant="primary")
                
                gr.Markdown("""
                ### 📋 系统状态
                - 🟢 演示模式运行中
                - 📊 使用模拟数据
                - 🤖 智能体系统: 就绪
                """)
            
            with gr.Column(scale=2):
                gr.Markdown("## 📈 分析结果")
                
                analysis_output = gr.Markdown(
                    value="点击'开始分析'查看演示结果...",
                    elem_classes=["analysis-output"]
                )
        
        gr.Markdown("""
        ---
        
        ### 💡 演示说明
        
        1. **功能展示**: 本演示展示了TradingAgents系统的界面和基本功能
        2. **模拟数据**: 所有分析结果均为模拟数据，不代表真实市场情况
        3. **完整版本**: 完整版本包含15个专业智能体和真实数据源
        4. **技术架构**: 基于多智能体协作、LLM驱动的金融分析框架
        
        ### 🔧 技术特性
        
        - **多智能体协作**: 15个专业化智能体分工协作
        - **实时数据**: 支持多种金融数据源
        - **深度分析**: 包含技术面、基本面、情绪面分析
        - **风险管理**: 多层次风险评估和控制
        - **可扩展性**: 模块化设计，易于扩展
        
        ---
        
        **TradingAgents Demo v1.0** | Powered by Multi-Agent LLM Framework
        """)
        
        # 绑定事件
        analyze_btn.click(
            fn=demo_analysis,
            inputs=[stock_input, analysis_type],
            outputs=[analysis_output]
        )
    
    return demo

def main():
    """主函数"""
    logger.info("启动 TradingAgents 演示系统...")
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 创建演示配置
    config = create_demo_config()
    logger.info("演示配置已创建")
    
    # 运行演示
    try:
        demo = run_simple_demo()
        logger.info("启动演示界面...")
        
        demo.launch(
            server_name="0.0.0.0",
            server_port=7862,
            share=False,
            debug=True,
            show_error=True
        )
        
    except Exception as e:
        logger.error(f"演示启动失败: {e}")
        logger.info("请检查依赖项和配置")

if __name__ == "__main__":
    main()
