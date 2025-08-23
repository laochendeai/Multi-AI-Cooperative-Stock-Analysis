import gradio as gr
import logging

logger = logging.getLogger(__name__)

def create_agent_config_ui(app):
    """Creates the UI for configuring and selecting agents."""
    agent_configs = {}
    available_agents = app.get_available_agents()
    models_with_features = app.get_models_with_features()

    model_choices = []
    for model, info in models_with_features.items():
        choice_text = f"{model} - {info['description']}"
        model_choices.append((choice_text, model))

    with gr.Accordion("🤖 智能体配置", open=False):
        gr.Markdown("**选择参与分析的智能体并为每个智能体配置专用模型:**")
        with gr.Column():
            for agent in available_agents:
                saved_config = app.agent_model_memory.get(agent, "")
                current_model = saved_config.split(":", 1)[1] if ":" in saved_config else saved_config

                if current_model not in models_with_features:
                    current_model = list(models_with_features.keys())[0] if models_with_features else ""

                logger.info(f"🤖 初始化智能体 {agent} 配置: {saved_config} -> {current_model}")

                with gr.Row():
                    agent_enabled = gr.Checkbox(
                        label=f"🤖 {agent}",
                        value=agent in ["market_analyst", "sentiment_analyst", "news_analyst"],
                        scale=2
                    )
                    agent_model = gr.Dropdown(
                        choices=model_choices,
                        value=current_model,
                        label="选择模型",
                        interactive=True,
                        scale=4
                    )
                    model_features_display = gr.Textbox(
                        value=models_with_features.get(current_model, {}).get("best_for", ""),
                        label="适用场景",
                        interactive=False,
                        scale=2
                    )

                agent_configs[agent] = {
                    "enabled": agent_enabled,
                    "model": agent_model,
                    "features": model_features_display
                }

            with gr.Row():
                save_agent_config_btn = gr.Button("💾 保存智能体配置", variant="secondary")
                agent_config_status = gr.Textbox(
                    label="配置状态",
                    interactive=False,
                    lines=2
                )

    return agent_configs, save_agent_config_btn, agent_config_status

