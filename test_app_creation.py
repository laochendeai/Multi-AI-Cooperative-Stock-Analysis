"""
测试应用创建
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_app_creation():
    """测试应用创建"""
    print("🧪 测试应用创建")
    print("="*50)
    
    try:
        from app_enhanced import EnhancedTradingAgentsApp
        print("✅ 成功导入 EnhancedTradingAgentsApp")
        
        print("🔄 创建应用实例...")
        app = EnhancedTradingAgentsApp()
        print("✅ 应用实例创建成功")
        
        # 检查关键属性
        attributes = [
            'data_collector',
            'config_file', 
            'config_dir',
            'analysis_sessions',
            'llm_config',
            'custom_llm_providers',
            'chromadb_available',
            'agent_model_config',
            'communication_logs',
            'last_analysis_result',
            'reports_dir',
            'retry_config',
            'analysis_state'
        ]
        
        print("\n📊 检查关键属性:")
        missing_attrs = []
        
        for attr in attributes:
            if hasattr(app, attr):
                value = getattr(app, attr)
                print(f"  ✅ {attr}: {type(value).__name__}")
            else:
                print(f"  ❌ {attr}: 缺失")
                missing_attrs.append(attr)
        
        if missing_attrs:
            print(f"\n⚠️ 缺失属性: {missing_attrs}")
            return False
        
        # 测试关键方法
        methods = [
            'get_system_status',
            'check_chromadb',
            'load_saved_config',
            'get_analysis_history',
            'load_analysis_report'
        ]
        
        print("\n📊 检查关键方法:")
        missing_methods = []
        
        for method in methods:
            if hasattr(app, method):
                print(f"  ✅ {method}: 存在")
            else:
                print(f"  ❌ {method}: 缺失")
                missing_methods.append(method)
        
        if missing_methods:
            print(f"\n⚠️ 缺失方法: {missing_methods}")
            return False
        
        # 测试系统状态
        print("\n📊 测试系统状态:")
        try:
            status = app.get_system_status()
            print("  ✅ get_system_status() 调用成功")
            for key, value in status.items():
                print(f"    {key}: {value}")
        except Exception as e:
            print(f"  ❌ get_system_status() 失败: {e}")
            return False
        
        print("\n🎉 应用创建测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 应用创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🎯 应用创建测试")
    print("="*80)
    
    success = test_app_creation()
    
    print("\n" + "="*80)
    print("📊 测试结果")
    print("="*80)
    
    if success:
        print("✅ 应用创建测试通过")
        print("\n💡 应用已正确初始化，包含所有必要的属性和方法")
        print("🚀 可以继续启动完整的界面")
    else:
        print("❌ 应用创建测试失败")
        print("需要检查和修复初始化问题")

if __name__ == "__main__":
    main()
