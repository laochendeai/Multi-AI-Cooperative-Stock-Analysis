#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动带赞赏码的TradingAgents界面
2:7:1布局，右侧显示赞赏码，单屏幕显示优化
"""

from ui_modules.main_interface import create_modular_interface

def main():
    """启动主程序"""
    print("=" * 60)
    print("🤖 TradingAgents - 赞赏码版本")
    print("=" * 60)
    print("🚀 正在启动界面...")
    print("💝 右侧栏显示赞赏码")
    print("📱 单屏幕显示优化")
    print("🎨 2:7:1 三栏布局")
    print("=" * 60)
    
    try:
        # 创建界面
        interface = create_modular_interface()
        
        print("✅ 界面创建成功！")
        print("\n💡 布局特性:")
        print("   • 🎯 左侧控制面板: 20% (股票输入、分析设置)")
        print("   • 📊 中间主要内容: 70% (分析结果、图表、报告)")
        print("   • 💝 右侧赞赏码: 10% (支持项目 + 系统状态)")
        print("\n🌟 现在可以在浏览器中访问: http://localhost:7860")
        
        # 启动界面
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True,
            quiet=False
        )
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
