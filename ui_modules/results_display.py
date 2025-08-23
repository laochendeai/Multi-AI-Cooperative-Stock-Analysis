import gradio as gr

def create_results_display_ui():
    """Creates the UI for displaying analysis results, raw data, and export options."""
    with gr.Tabs():
        with gr.Tab("📈 分析报告"):
            analysis_output = gr.Markdown(
                value="🔄 等待分析...\n\n请在左侧配置面板中:\n1. 输入股票代码\n2. 选择分析深度\n3. 选择智能体\n4. 点击开始分析",
                elem_classes=["full-height"]
            )

        with gr.Tab("🔍 原始数据"):
            raw_data_output = gr.JSON(
                label="原始分析数据",
                elem_classes=["full-height"]
            )

        with gr.Tab("📤 导出结果"):
            gr.Markdown("#### 📥 导出分析结果")
            with gr.Row():
                export_format = gr.Dropdown(
                    choices=["markdown", "json", "txt"],
                    value="markdown",
                    label="导出格式"
                )
                export_btn = gr.Button("📥 导出", variant="primary")
            export_status = gr.Textbox(
                label="导出状态",
                interactive=False,
                lines=2
            )
            gr.Markdown("""
            **导出格式说明:**
            - **Markdown**: 适合文档查看和分享
            - **JSON**: 适合程序处理和数据分析
            - **TXT**: 适合简单文本查看
            """)
            result_storage = gr.Textbox(
                visible=False,
                value=""
            )

    return {
        "analysis_output": analysis_output,
        "raw_data_output": raw_data_output,
        "export_format": export_format,
        "export_btn": export_btn,
        "export_status": export_status,
        "result_storage": result_storage
    }

