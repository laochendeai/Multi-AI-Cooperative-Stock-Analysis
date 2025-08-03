"""
安装真实数据获取所需的依赖包
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

def main():
    print("🚀 开始安装真实数据获取所需的依赖包...")
    print("="*60)
    
    # 需要安装的包列表
    packages = [
        "akshare",      # 股票数据获取
        "pandas",       # 数据处理
        "numpy",        # 数值计算
        "httpx",        # HTTP客户端
        "sqlite3"       # 数据库（通常内置）
    ]
    
    success_count = 0
    total_count = len(packages)
    
    for package in packages:
        print(f"\n📦 正在安装 {package}...")
        if install_package(package):
            success_count += 1
        else:
            print(f"⚠️ {package} 安装失败，请手动安装")
    
    print("\n" + "="*60)
    print("📊 安装结果总结:")
    print(f"✅ 成功安装: {success_count}/{total_count}")
    print(f"❌ 安装失败: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n🎉 所有依赖包安装成功！")
        print("\n💡 现在可以使用真实数据功能:")
        print("1. 重新启动 TradingAgents 系统")
        print("2. 勾选 '🤖 使用真实LLM智能体协作'")
        print("3. 系统将自动获取真实的股票数据")
        print("4. 配置支持联网的LLM模型以获取新闻和社交媒体数据")
    else:
        print("\n⚠️ 部分依赖包安装失败")
        print("请手动安装失败的包，或检查网络连接")
        print("\n🔧 手动安装命令:")
        for package in packages:
            print(f"pip install {package}")
    
    print("\n📚 支持联网搜索的LLM模型推荐:")
    print("- OpenAI GPT-4 / GPT-4 Turbo")
    print("- Google Gemini Pro")
    print("- Perplexity 在线模型")
    print("- 其他支持联网功能的模型")

if __name__ == "__main__":
    main()
