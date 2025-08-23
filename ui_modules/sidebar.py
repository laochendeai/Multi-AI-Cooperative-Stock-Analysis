import gradio as gr

def create_sidebar_ui(app):
    """Creates the right sidebar UI containing support and system status info."""
    # Support/Donation card
    gr.Markdown("### 💝 支持开发")
    gr.Markdown("""
    **🌟 感谢您使用 TradingAgents！**

    如果这个项目对您有帮助，欢迎支持开发者：
    """)
    gr.Image(
        value="./assets/donation_code.png",
        label="赞赏码",
        show_label=False,
        container=False,
        height=200,
        width=200
    )
    gr.Markdown("""
    **🎯 您的支持将用于：**
    - 🔧 功能改进和新特性开发
    - 🚀 性能优化和Bug修复
    - 📚 完成作者给妈妈尽点孝心的心愿

    **🤝 其他支持方式：**
    - ⭐ [GitHub Star](https://github.com/laochendeai/Multi-AI-Cooperative-Stock-Analysis)
    - ⭐ [Gitee Star](https://gitee.com/laochendeai/Multi-AI-Cooperative-Stock-Analysis)
    - 🐛 问题反馈和功能建议
    - 📢 推荐分享给朋友

    *💖 每一份支持都是对开源精神的鼓励！*
    """)

    gr.Markdown("---")

    # System Status section
    gr.Markdown("### 📊 系统状态")
    current_status = gr.Textbox(
        label="当前状态",
        value="🟢 系统就绪",
        interactive=False,
        elem_classes=["compact-input"]
    )
    analysis_progress = gr.Slider(
        label="分析进度",
        minimum=0,
        maximum=100,
        value=0,
        interactive=False,
        elem_classes=["compact-input"]
    )

    with gr.Accordion("ℹ️ 系统信息", open=True):
        system_info = gr.Markdown(f"""
        **应用状态**: {'✅ 正常' if app.enhanced_app else '❌ 异常'}
        **数据库**: ✅ 已连接
        **LLM配置**: ✅ 已加载
        **智能体**: ✅ {len(app.get_available_agents())}个
        **导出格式**: ✅ {len(app.export_formats)}种
        """)

    with gr.Accordion("🤖 可用模型", open=False):
        available_models = gr.JSON(
            label="LLM模型列表",
            value=app.get_available_models()
        )

    with gr.Accordion("📝 实时日志", open=False):
        log_output = gr.Textbox(
            label="系统日志",
            lines=6,
            max_lines=10,
            interactive=False,
            elem_classes=["compact-input"]
        )

    refresh_btn = gr.Button("🔄 刷新状态", size="sm")

    return {
        "current_status": current_status,
        "analysis_progress": analysis_progress,
        "system_info": system_info,
        "available_models": available_models,
        "log_output": log_output,
        "refresh_btn": refresh_btn
    }

