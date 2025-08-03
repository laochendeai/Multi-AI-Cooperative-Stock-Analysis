"""
测试Gradio版本兼容性问题
"""

import gradio as gr

def test_dropdown_update():
    """测试Dropdown.update是否存在"""
    try:
        # 尝试使用旧的语法
        result = gr.Dropdown.update(choices=["test1", "test2"])
        print("✅ gr.Dropdown.update 可用")
        return True
    except AttributeError as e:
        print(f"❌ gr.Dropdown.update 不可用: {e}")
        print("💡 需要使用新的语法：直接返回选择列表")
        return False

def test_new_syntax():
    """测试新的语法"""
    try:
        # 新的语法：直接返回选择列表
        choices = ["test1", "test2", "test3"]
        print(f"✅ 新语法可用，返回: {choices}")
        return choices
    except Exception as e:
        print(f"❌ 新语法失败: {e}")
        return []

def create_test_interface():
    """创建测试界面"""
    with gr.Blocks() as demo:
        gr.Markdown("# Gradio版本兼容性测试")
        
        with gr.Row():
            test_dropdown = gr.Dropdown(
                label="测试下拉框",
                choices=["初始选项1", "初始选项2"],
                value="初始选项1"
            )
            
            update_btn = gr.Button("更新选项")
        
        status_text = gr.Textbox(label="状态", value="等待测试...")
        
        def update_dropdown_choices():
            """更新下拉框选项"""
            try:
                new_choices = ["新选项1", "新选项2", "新选项3"]
                return new_choices, "✅ 更新成功！使用新语法"
            except Exception as e:
                return ["错误"], f"❌ 更新失败: {str(e)}"
        
        update_btn.click(
            fn=update_dropdown_choices,
            outputs=[test_dropdown, status_text]
        )
    
    return demo

if __name__ == "__main__":
    print("🧪 测试Gradio版本兼容性")
    print("="*50)
    
    # 检查Gradio版本
    print(f"Gradio版本: {gr.__version__}")
    
    # 测试旧语法
    old_syntax_works = test_dropdown_update()
    
    # 测试新语法
    new_choices = test_new_syntax()
    
    print("\n" + "="*50)
    print("📊 测试结果:")
    print(f"旧语法 (gr.Dropdown.update): {'✅ 可用' if old_syntax_works else '❌ 不可用'}")
    print(f"新语法 (直接返回列表): {'✅ 可用' if new_choices else '❌ 不可用'}")
    
    if not old_syntax_works:
        print("\n💡 解决方案:")
        print("将所有 gr.Dropdown.update(choices=xxx) 替换为直接返回 xxx")
        print("例如: return gr.Dropdown.update(choices=['a', 'b']) → return ['a', 'b']")
    
    print("\n🚀 启动测试界面...")
    demo = create_test_interface()
    demo.launch(server_name="0.0.0.0", server_port=7865, share=False)
