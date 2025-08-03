"""
测试股票数据获取
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app_enhanced import EnhancedTradingAgentsApp

async def test_stock_data_fetch():
    """测试股票数据获取"""
    print("🧪 测试股票数据获取")
    print("="*60)
    
    app = EnhancedTradingAgentsApp()
    
    # 测试不同的股票代码
    test_symbols = [
        "600519",  # 贵州茅台（应该存在）
        "000001",  # 平安银行（应该存在）
        "600328",  # 天房发展（可能存在问题）
        "300750",  # 宁德时代（应该存在）
    ]
    
    for symbol in test_symbols:
        print(f"\n📊 测试股票: {symbol}")
        
        try:
            # 获取股票数据
            stock_data = await app.data_collector.get_stock_data(symbol)
            
            if "error" in stock_data:
                print(f"  ❌ 获取失败: {stock_data['error']}")
                continue
            
            print(f"  ✅ 获取成功")
            print(f"  📈 股票代码: {stock_data.get('symbol', '未知')}")
            print(f"  🏷️ 股票名称: '{stock_data.get('name', '未知')}'")
            print(f"  💰 当前价格: {stock_data.get('price_data', {}).get('current_price', '未知')}元")
            print(f"  📊 涨跌幅: {stock_data.get('price_data', {}).get('change_percent', '未知')}%")
            
            # 检查名称字段
            name = stock_data.get('name', '')
            if not name or name.strip() == '':
                print(f"  ⚠️ 警告: 股票名称为空")
            elif name == symbol:
                print(f"  ⚠️ 警告: 股票名称等于代码，可能获取失败")
            else:
                print(f"  ✅ 股票名称正常")
                
        except Exception as e:
            print(f"  ❌ 获取异常: {e}")

async def test_akshare_direct():
    """直接测试akshare数据获取"""
    print("\n🧪 直接测试akshare数据获取")
    print("="*60)
    
    try:
        import akshare as ak
        
        # 获取A股实时数据
        print("📊 获取A股实时数据...")
        real_time_data = ak.stock_zh_a_spot_em()
        
        print(f"  数据行数: {len(real_time_data)}")
        print(f"  数据列: {list(real_time_data.columns)}")
        
        # 测试特定股票
        test_symbols = ["600519", "600328", "000001"]
        
        for symbol in test_symbols:
            print(f"\n📈 查找股票: {symbol}")
            
            stock_info = real_time_data[real_time_data['代码'] == symbol]
            
            if stock_info.empty:
                print(f"  ❌ 未找到股票 {symbol}")
                continue
            
            stock_row = stock_info.iloc[0]
            
            print(f"  ✅ 找到股票")
            print(f"  代码: {stock_row['代码']}")
            print(f"  名称: '{stock_row['名称']}'")
            print(f"  最新价: {stock_row['最新价']}")
            print(f"  涨跌幅: {stock_row['涨跌幅']}")
            
            # 检查名称
            name = stock_row['名称']
            if pd.isna(name) or str(name).strip() == '':
                print(f"  ⚠️ 名称为空或NaN")
            elif str(name) == symbol:
                print(f"  ⚠️ 名称等于代码")
            else:
                print(f"  ✅ 名称正常")
                
    except Exception as e:
        print(f"❌ akshare测试失败: {e}")

async def test_stock_name_fallback():
    """测试股票名称回退机制"""
    print("\n🧪 测试股票名称回退机制")
    print("="*60)
    
    # 模拟不同的股票名称情况
    test_cases = [
        {"symbol": "600519", "name": "贵州茅台", "expected": "贵州茅台"},
        {"symbol": "600328", "name": "", "expected": "600328"},  # 空名称
        {"symbol": "600328", "name": None, "expected": "600328"},  # None名称
        {"symbol": "600328", "name": "600328", "expected": "600328"},  # 名称等于代码
    ]
    
    for case in test_cases:
        symbol = case["symbol"]
        name = case["name"]
        expected = case["expected"]
        
        print(f"\n📊 测试用例: {symbol}")
        print(f"  输入名称: '{name}'")
        
        # 名称处理逻辑
        if not name or str(name).strip() == '' or str(name) == symbol:
            processed_name = symbol  # 使用代码作为名称
        else:
            processed_name = str(name).strip()
        
        print(f"  处理后名称: '{processed_name}'")
        print(f"  期望名称: '{expected}'")
        
        if processed_name == expected:
            print(f"  ✅ 处理正确")
        else:
            print(f"  ❌ 处理错误")

def test_prompt_with_fallback():
    """测试带回退机制的提示生成"""
    print("\n🧪 测试带回退机制的提示生成")
    print("="*60)
    
    # 模拟股票数据
    test_cases = [
        {"symbol": "600519", "name": "贵州茅台"},
        {"symbol": "600328", "name": ""},  # 空名称
        {"symbol": "600328", "name": "600328"},  # 名称等于代码
    ]
    
    for case in test_cases:
        symbol = case["symbol"]
        raw_name = case["name"]
        
        print(f"\n📊 测试股票: {symbol}")
        print(f"  原始名称: '{raw_name}'")
        
        # 名称处理逻辑（改进版）
        if not raw_name or str(raw_name).strip() == '' or str(raw_name) == symbol:
            # 如果名称为空或等于代码，尝试从已知映射获取
            known_names = {
                "600519": "贵州茅台",
                "000001": "平安银行", 
                "600328": "天房发展",
                "300750": "宁德时代"
            }
            stock_name = known_names.get(symbol, f"股票{symbol}")
        else:
            stock_name = str(raw_name).strip()
        
        print(f"  处理后名称: '{stock_name}'")
        
        # 生成提示示例
        prompt_sample = f"请分析股票{symbol}（{stock_name}）的技术指标..."
        print(f"  提示示例: {prompt_sample}")
        
        # 检查是否还有问题
        if f"股票{symbol}（股票{symbol}）" in prompt_sample:
            print(f"  ❌ 仍有格式问题")
        else:
            print(f"  ✅ 格式正常")

async def main():
    """主测试函数"""
    print("🎯 股票数据获取问题诊断")
    print("="*80)
    
    # 执行各项测试
    await test_stock_data_fetch()
    
    # 需要pandas用于akshare测试
    try:
        import pandas as pd
        await test_akshare_direct()
    except ImportError:
        print("\n⚠️ 跳过akshare直接测试（需要pandas）")
    
    await test_stock_name_fallback()
    test_prompt_with_fallback()
    
    print("\n" + "="*80)
    print("📊 诊断总结")
    print("="*80)
    print("💡 可能的问题和解决方案:")
    print("1. 股票600328可能已停牌或退市")
    print("2. akshare数据中名称字段为空")
    print("3. 需要添加股票名称回退机制")
    print("4. 需要维护已知股票代码到名称的映射")
    
    print("\n🔧 建议的修复方案:")
    print("1. 添加股票名称验证和回退逻辑")
    print("2. 维护常用股票的名称映射表")
    print("3. 在提示中处理名称为空的情况")
    print("4. 添加数据获取失败的友好提示")

if __name__ == "__main__":
    asyncio.run(main())
