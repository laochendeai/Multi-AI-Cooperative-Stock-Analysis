"""
检查运行环境和依赖包
"""

import sys
import os
from pathlib import Path

def check_python_environment():
    """检查Python环境"""
    print("🐍 Python环境信息")
    print("="*50)
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    print(f"当前工作目录: {os.getcwd()}")
    print()

def check_required_packages():
    """检查必需的包"""
    print("📦 依赖包检查")
    print("="*50)
    
    required_packages = [
        "gradio",
        "asyncio", 
        "httpx",
        "pandas",
        "numpy",
        "sqlite3",
        "akshare",
        "dashscope"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == "sqlite3":
                import sqlite3
                print(f"✅ {package}: 内置模块")
            elif package == "asyncio":
                import asyncio
                print(f"✅ {package}: 内置模块")
            elif package == "dashscope":
                import dashscope
                print(f"✅ {package}: 已安装")
                # 测试基本功能
                try:
                    # 检查是否有Generation类
                    if hasattr(dashscope, 'Generation'):
                        print(f"   - Generation类: 可用")
                    else:
                        print(f"   - Generation类: 不可用")
                except Exception as e:
                    print(f"   - 功能测试失败: {e}")
            else:
                __import__(package)
                print(f"✅ {package}: 已安装")
        except ImportError as e:
            print(f"❌ {package}: 未安装 ({e})")
            missing_packages.append(package)
        except Exception as e:
            print(f"⚠️ {package}: 安装异常 ({e})")
    
    return missing_packages

def check_app_import():
    """检查应用导入"""
    print("\n🚀 应用导入检查")
    print("="*50)
    
    try:
        # 添加当前目录到路径
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        
        from app_enhanced import EnhancedTradingAgentsApp
        print("✅ EnhancedTradingAgentsApp 导入成功")
        
        # 创建应用实例
        app = EnhancedTradingAgentsApp()
        print("✅ 应用实例创建成功")
        
        # 检查dashscope调用方法
        if hasattr(app, '_call_dashscope'):
            print("✅ _call_dashscope 方法存在")
        else:
            print("❌ _call_dashscope 方法不存在")
        
        return True
        
    except ImportError as e:
        print(f"❌ 应用导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 应用创建失败: {e}")
        return False

def test_dashscope_direct():
    """直接测试dashscope功能"""
    print("\n🧪 DashScope直接测试")
    print("="*50)
    
    try:
        import dashscope
        print("✅ dashscope导入成功")
        
        # 检查主要类和方法
        if hasattr(dashscope, 'Generation'):
            print("✅ Generation类存在")
            
            # 检查call方法
            if hasattr(dashscope.Generation, 'call'):
                print("✅ Generation.call方法存在")
            else:
                print("❌ Generation.call方法不存在")
        else:
            print("❌ Generation类不存在")
        
        # 尝试设置API密钥（不会实际调用）
        try:
            dashscope.api_key = "test_key"
            print("✅ API密钥设置成功")
        except Exception as e:
            print(f"❌ API密钥设置失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ DashScope测试失败: {e}")
        return False

def main():
    """主检查函数"""
    print("🔍 TradingAgents 环境诊断")
    print("="*80)
    
    # 检查Python环境
    check_python_environment()
    
    # 检查依赖包
    missing_packages = check_required_packages()
    
    # 检查应用导入
    app_import_ok = check_app_import()
    
    # 测试dashscope
    dashscope_ok = test_dashscope_direct()
    
    # 总结
    print("\n" + "="*80)
    print("📊 诊断结果总结")
    print("="*80)
    
    if missing_packages:
        print(f"❌ 缺失依赖包: {missing_packages}")
        print("\n🔧 安装命令:")
        for package in missing_packages:
            print(f"pip install {package}")
    else:
        print("✅ 所有依赖包已安装")
    
    print(f"应用导入: {'✅ 正常' if app_import_ok else '❌ 失败'}")
    print(f"DashScope功能: {'✅ 正常' if dashscope_ok else '❌ 异常'}")
    
    if not missing_packages and app_import_ok and dashscope_ok:
        print("\n🎉 环境检查通过！")
        print("\n💡 如果仍然出现dashscope未安装的错误，可能的原因:")
        print("1. 主程序运行在不同的Python环境中")
        print("2. 需要重启主程序以重新加载模块")
        print("3. 虚拟环境配置问题")
        
        print("\n🔧 解决建议:")
        print("1. 确保使用相同的Python解释器运行主程序")
        print("2. 重新启动 python app_enhanced.py")
        print("3. 如果使用conda，确保激活正确的环境")
    else:
        print("\n❌ 环境存在问题，请根据上述信息修复")

if __name__ == "__main__":
    main()
