"""
安装阿里百炼DashScope依赖包
"""

import subprocess
import sys
import os

def install_package(package):
    """安装Python包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ 成功安装 {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装 {package} 失败: {e}")
        return False

def test_dashscope_import():
    """测试dashscope导入"""
    try:
        import dashscope
        print("✅ dashscope 导入成功")
        print(f"版本: {getattr(dashscope, '__version__', '未知')}")
        return True
    except ImportError as e:
        print(f"❌ dashscope 导入失败: {e}")
        return False

def main():
    print("🚀 安装阿里百炼DashScope依赖包")
    print("="*60)
    
    # 安装dashscope
    print("📦 正在安装 dashscope...")
    success = install_package("dashscope")
    
    if success:
        print("\n🧪 测试导入...")
        import_success = test_dashscope_import()
        
        if import_success:
            print("\n🎉 阿里百炼DashScope安装成功！")
            print("\n💡 使用说明:")
            print("1. 在TradingAgents界面中选择 '阿里百炼' 提供商")
            print("2. 配置您的DASHSCOPE_API_KEY")
            print("3. 选择支持联网的模型如 qwen-plus-2025-04-28")
            print("4. 情感分析师、新闻分析师、基本面分析师将自动启用联网搜索")
            
            print("\n🔑 API密钥获取:")
            print("1. 访问 https://dashscope.aliyun.com/")
            print("2. 注册/登录阿里云账号")
            print("3. 创建API密钥")
            print("4. 在系统中配置 DASHSCOPE_API_KEY 环境变量")
            
            print("\n📊 支持的模型:")
            print("- qwen-turbo (快速模型)")
            print("- qwen-plus (平衡模型)")
            print("- qwen-max (最强模型)")
            print("- qwen-plus-2025-04-28 (支持联网搜索)")
            
        else:
            print("\n❌ 导入测试失败，请检查安装")
    else:
        print("\n❌ 安装失败")
        print("\n🔧 手动安装命令:")
        print("pip install dashscope")

if __name__ == "__main__":
    main()
