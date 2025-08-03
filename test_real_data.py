"""
测试真实数据获取功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app_enhanced import RealDataCollector

async def test_real_data_collection():
    """测试真实数据收集功能"""
    print("🧪 测试真实数据收集功能")
    print("="*60)
    
    # 创建数据收集器
    collector = RealDataCollector()
    
    # 测试股票代码
    test_symbols = ["600519", "000001", "000002"]
    
    for symbol in test_symbols:
        print(f"\n📊 测试股票: {symbol}")
        print("-"*40)
        
        try:
            # 获取真实数据
            data = await collector.get_real_stock_data(symbol)
            
            if "error" in data:
                print(f"❌ 获取失败: {data['error']}")
                continue
            
            print(f"✅ 获取成功!")
            print(f"股票名称: {data.get('name', '未知')}")
            print(f"当前价格: {data['price_data']['current_price']}")
            print(f"涨跌幅: {data['price_data']['change_percent']}%")
            print(f"成交量: {data['price_data']['volume']}")
            
            print(f"\n📈 技术指标:")
            tech = data['technical_indicators']
            print(f"RSI: {tech['rsi']:.2f}")
            print(f"MACD: {tech['macd']:.2f}")
            print(f"MA5: {tech['ma5']:.2f}")
            print(f"MA20: {tech['ma20']:.2f}")
            print(f"布林带上轨: {tech['bollinger_upper']:.2f}")
            print(f"布林带下轨: {tech['bollinger_lower']:.2f}")
            
            print(f"\n💰 市场数据:")
            market = data['market_data']
            print(f"市盈率: {market['pe_ratio']}")
            print(f"市净率: {market['pb_ratio']}")
            
            print(f"数据来源: {data['data_source']}")
            print(f"更新时间: {data['update_time']}")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    return True

async def test_database_functionality():
    """测试数据库功能"""
    print("\n" + "="*60)
    print("🗄️ 测试数据库功能")
    print("="*60)
    
    collector = RealDataCollector()
    
    # 检查数据库文件
    db_path = collector.db_path
    print(f"数据库路径: {db_path}")
    print(f"数据库存在: {db_path.exists()}")
    
    if db_path.exists():
        print(f"数据库大小: {db_path.stat().st_size} 字节")
    
    # 测试数据库连接
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询表结构
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"数据库表: {[table[0] for table in tables]}")
        
        # 查询数据记录数
        for table_name in ['stock_data', 'technical_indicators', 'news_data']:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"{table_name} 记录数: {count}")
            except:
                print(f"{table_name} 表不存在或查询失败")
        
        conn.close()
        print("✅ 数据库功能正常")
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
    
    return True

async def test_akshare_availability():
    """测试akshare可用性"""
    print("\n" + "="*60)
    print("📦 测试akshare可用性")
    print("="*60)
    
    try:
        import akshare as ak
        print("✅ akshare 导入成功")
        
        # 测试获取股票列表
        try:
            stock_list = ak.stock_zh_a_spot_em()
            print(f"✅ 获取股票列表成功，共 {len(stock_list)} 只股票")
            
            # 显示前5只股票
            print("前5只股票:")
            for i in range(min(5, len(stock_list))):
                stock = stock_list.iloc[i]
                print(f"  {stock['代码']} - {stock['名称']} - {stock['最新价']}")
            
        except Exception as e:
            print(f"❌ 获取股票列表失败: {e}")
        
        # 测试获取历史数据
        try:
            from datetime import datetime, timedelta
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            
            hist_data = ak.stock_zh_a_hist(symbol="600519", period="daily", 
                                         start_date=start_date, end_date=end_date, adjust="")
            print(f"✅ 获取历史数据成功，共 {len(hist_data)} 条记录")
            
        except Exception as e:
            print(f"❌ 获取历史数据失败: {e}")
        
        return True
        
    except ImportError:
        print("❌ akshare 未安装")
        print("请运行: pip install akshare")
        return False
    except Exception as e:
        print(f"❌ akshare 测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🎯 TradingAgents 真实数据获取功能测试")
    print("="*80)
    
    # 测试1: akshare可用性
    akshare_test = await test_akshare_availability()
    
    # 测试2: 数据库功能
    db_test = await test_database_functionality()
    
    # 测试3: 真实数据收集
    if akshare_test:
        data_test = await test_real_data_collection()
    else:
        print("\n⚠️ 跳过真实数据收集测试（akshare不可用）")
        data_test = False
    
    # 总结
    print("\n" + "="*80)
    print("📊 测试结果总结")
    print("="*80)
    print(f"akshare可用性: {'✅ 通过' if akshare_test else '❌ 失败'}")
    print(f"数据库功能: {'✅ 通过' if db_test else '❌ 失败'}")
    print(f"真实数据收集: {'✅ 通过' if data_test else '❌ 失败'}")
    
    if akshare_test and data_test:
        print("\n🎉 恭喜！真实数据获取功能正常工作！")
        print("\n💡 使用建议:")
        print("1. 重新启动 TradingAgents 系统")
        print("2. 勾选 '🤖 使用真实LLM智能体协作'")
        print("3. 系统将自动获取真实的股票技术指标数据")
        print("4. 配置支持联网的LLM模型以获取新闻和社交媒体数据")
        print("5. 在 '📡 通信监控' 页面查看真实的数据获取过程")
    else:
        print("\n❌ 真实数据功能测试失败")
        print("\n🔧 排查建议:")
        if not akshare_test:
            print("1. 安装akshare: pip install akshare")
            print("2. 检查网络连接")
        print("3. 查看错误日志了解具体问题")
        print("4. 确认Python环境配置正确")

if __name__ == "__main__":
    asyncio.run(main())
