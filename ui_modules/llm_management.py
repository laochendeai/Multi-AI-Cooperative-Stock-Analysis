import gradio as gr

def create_llm_management_ui(app):
    """Creates the UI for managing LLM providers."""
    gr.Markdown("### 🧠 LLM提供商管理")

    # Accordion for configured providers
    with gr.Accordion("📋 已配置的LLM提供商", open=True):
        gr.Markdown("**当前系统中已配置的AI模型提供商:**")
        provider_overview = gr.Markdown(
            value=app._format_provider_overview(),
            elem_classes=["provider-overview"]
        )
        configured_llm_display = gr.JSON(
            label="详细配置信息",
            value=app.get_configured_llm_providers()
        )
        with gr.Row():
            refresh_llm_btn = gr.Button("🔄 刷新配置", size="sm")
            test_all_btn = gr.Button("🧪 测试所有提供商", size="sm", variant="secondary")

    # Accordion for status monitoring
    with gr.Accordion("📊 实时状态监控", open=False):
        gr.Markdown("**各提供商的实时连接状态和响应速度:**")
        provider_status_display = gr.Markdown(
            value="点击'测试所有提供商'按钮获取实时状态",
            elem_classes=["status-display"]
        )
        status_update_time = gr.Textbox(
            label="最后更新时间",
            value="未更新",
            interactive=False
        )

    # Accordion for model details
    with gr.Accordion("🤖 模型能力详情", open=False):
        gr.Markdown("**各提供商的模型列表和特殊能力:**")
        models_by_provider = gr.Markdown(
            value=app._format_models_by_provider(),
            elem_classes=["models-display"]
        )

    # Accordion for single model test
    with gr.Accordion("🧪 单个模型测试", open=False):
        model_test_select = gr.Dropdown(
            choices=app.get_all_available_models_list(),
            label="选择要测试的模型"
        )
        test_model_btn = gr.Button("🌐 测试模型连接")
        model_test_status = gr.Textbox(
            label="模型测试结果",
            interactive=False,
            lines=6
        )

    # Accordion for custom provider
    with gr.Accordion("➕ 添加自定义提供商", open=False):
        provider_name = gr.Textbox(label="提供商名称", placeholder="如：custom_openai")
        provider_url = gr.Textbox(label="API地址", placeholder="https://api.example.com/v1")
        provider_key = gr.Textbox(label="API密钥", type="password")
        with gr.Row():
            add_provider_btn = gr.Button("➕ 添加")
            test_provider_btn = gr.Button("🧪 测试")
        provider_status = gr.Textbox(label="操作结果", interactive=False, lines=3)

    # Accordion for network settings
    with gr.Accordion("🌐 网络设置", open=False):
        enable_network = gr.Checkbox(
            label="启用联网功能",
            value=True
        )
        test_network_btn = gr.Button("🌐 测试网络连接")
        network_status = gr.Textbox(
            label="网络状态",
            value="未测试",
            interactive=False,
            lines=4
        )

    # Return all components that need to be accessed later for event handling
    return {
        "provider_overview": provider_overview,
        "configured_llm_display": configured_llm_display,
        "refresh_llm_btn": refresh_llm_btn,
        "test_all_btn": test_all_btn,
        "provider_status_display": provider_status_display,
        "status_update_time": status_update_time,
        "models_by_provider": models_by_provider,
        "model_test_select": model_test_select,
        "test_model_btn": test_model_btn,
        "model_test_status": model_test_status,
        "provider_name": provider_name,
        "provider_url": provider_url,
        "provider_key": provider_key,
        "add_provider_btn": add_provider_btn,
        "test_provider_btn": test_provider_btn,
        "provider_status": provider_status,
        "enable_network": enable_network,
        "test_network_btn": test_network_btn,
        "network_status": network_status
    }

