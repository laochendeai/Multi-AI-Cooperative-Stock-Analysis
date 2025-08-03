#!/usr/bin/env python3
"""
TradingAgents Gradio应用启动脚本
零知识迁移版本 - 安全启动器
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """配置日志系统"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )

def check_environment():
    """检查环境配置"""
    required_dirs = ['core']
    missing_dirs = []
    
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"❌ 缺少必要目录: {missing_dirs}")
        print("正在创建目录结构...")
        
        for dir_name in missing_dirs:
            os.makedirs(dir_name, exist_ok=True)
            # 创建__init__.py文件
            init_file = os.path.join(dir_name, '__init__.py')
            with open(init_file, 'w') as f:
                f.write('# Auto-generated __init__.py\n')
        
        print("✅ 目录结构创建完成")
    
    # 检查环境变量
    env_file = '.env'
    if not os.path.exists(env_file):
        print(f"⚠️  未找到 {env_file} 文件")
        print("正在创建示例环境文件...")
        
        with open(env_file, 'w') as f:
            f.write("""# SECURE_ZONE: LLM API密钥槽位
DEEPSEEK_API_KEY=your_deepseek_key_here
OPENAI_API_KEY=your_openai_key_here
GROQ_API_KEY=your_groq_key_here
GOOGLE_API_KEY=your_google_key_here
MOONSHOT_API_KEY=your_moonshot_key_here

# SECURE_ZONE: 数据源认证槽位
AKSHARE_API_KEY=your_akshare_key_here
NEWS_API_KEY=your_news_api_key_here
FINNHUB_API_KEY=your_finnhub_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here

# 应用配置
APP_ENV=development
LOG_LEVEL=INFO
MAX_CONCURRENT_REQUESTS=10
""")
        
        print(f"✅ 已创建 {env_file} 文件，请填入真实的API密钥")
        return False
    
    return True

def load_environment():
    """加载环境变量"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ 环境变量加载成功")
        return True
    except ImportError:
        print("⚠️  python-dotenv未安装，使用系统环境变量")
        return True
    except Exception as e:
        print(f"❌ 环境变量加载失败: {e}")
        return False

def check_dependencies():
    """检查依赖包"""
    required_packages = [
        'gradio',
        'openai', 
        'aiohttp',
        'asyncio'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {missing_packages}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包检查通过")
    return True

def main():
    """主启动函数"""
    print("🚀 TradingAgents Gradio应用启动中...")
    print("=" * 50)
    
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # 环境检查
    if not check_environment():
        print("❌ 环境检查失败，请配置API密钥后重新启动")
        return
    
    # 加载环境变量
    if not load_environment():
        print("❌ 环境变量加载失败")
        return
    
    # 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败")
        return
    
    try:
        # 导入并启动应用
        logger.info("正在启动TradingAgents应用...")
        
        from app import TradingAgentsGradioApp
        
        # 创建应用实例
        app = TradingAgentsGradioApp()
        interface = app.create_interface()
        
        print("✅ 应用初始化完成")
        print("🌐 启动Web服务器...")
        print("📱 访问地址: http://localhost:7860")
        print("🔒 安全模式: 已启用")
        print("=" * 50)
        
        # 启动Gradio应用
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=True,
            show_error=True,
            quiet=False,
            favicon_path=None,
            ssl_verify=False
        )
        
    except KeyboardInterrupt:
        print("\n🛑 用户中断，正在关闭应用...")
        logger.info("应用被用户中断")
    except Exception as e:
        print(f"❌ 应用启动失败: {e}")
        logger.error(f"应用启动失败: {e}", exc_info=True)
        
        # 提供故障排除建议
        print("\n🔧 故障排除建议:")
        print("1. 检查API密钥是否正确配置")
        print("2. 确认所有依赖包已安装")
        print("3. 检查端口7860是否被占用")
        print("4. 查看app.log文件获取详细错误信息")

if __name__ == "__main__":
    main()