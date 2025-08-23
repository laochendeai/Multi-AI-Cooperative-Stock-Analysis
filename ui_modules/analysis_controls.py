import gradio as gr

def create_analysis_controls_ui(app):
    """Creates the primary analysis input controls."""
    gr.Markdown("### ⚙️ 分析配置")

    stock_input = gr.Textbox(
        label="📈 股票代码",
        placeholder="输入股票代码，如：000001, 600519",
        elem_classes=["compact-input"]
    )

    depth_select = gr.Dropdown(
        choices=app.get_analysis_depths(),
        value="标准分析",
        label="🔍 分析深度",
        elem_classes=["compact-input"]
    )

    with gr.Row():
        analyze_btn = gr.Button("🚀 开始分析", variant="primary")
        stop_btn = gr.Button("⏹️ 停止", variant="secondary")

    return {
        "stock_input": stock_input,
        "depth_select": depth_select,
        "analyze_btn": analyze_btn,
        "stop_btn": stop_btn
    }

