#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents 图表工具模块
专门处理图表生成和错误处理，确保返回正确的matplotlib对象
"""

import sys
import os
import platform

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 配置中文字体支持
def setup_chinese_font():
    """配置matplotlib中文字体支持"""
    try:
        import matplotlib.pyplot as plt
        import warnings

        # 抑制字体相关警告
        warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

        # 根据操作系统选择合适的中文字体
        system = platform.system()

        if system == "Windows":
            # Windows系统常用中文字体，优先使用支持更多字符的字体
            fonts = ['Microsoft YaHei', 'SimHei', 'SimSun', 'KaiTi', 'Arial Unicode MS']
        elif system == "Darwin":  # macOS
            # macOS系统中文字体
            fonts = ['PingFang SC', 'Hiragino Sans GB', 'STHeiti', 'Arial Unicode MS']
        else:  # Linux
            # Linux系统中文字体
            fonts = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'Source Han Sans SC', 'DejaVu Sans']

        # 设置中文字体
        plt.rcParams['font.sans-serif'] = fonts
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        plt.rcParams['font.size'] = 10  # 设置默认字体大小

        print(f"✅ 中文字体配置完成: {fonts[0]}")
        return True

    except Exception as e:
        print(f"⚠️ 字体配置失败: {e}")
        return False

# 初始化中文字体支持
setup_chinese_font()

class ChartGenerator:
    """图表生成器"""
    
    def __init__(self):
        """初始化图表生成器"""
        self.default_figsize = (10, 6)
        self.error_color = "lightcoral"
        self.success_color = "lightblue"
    
    def generate_stock_chart(self, stock_code, data=None):
        """生成股票图表"""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            # 清除之前的图表
            plt.clf()
            
            if data is None:
                # 生成模拟数据
                days = np.arange(1, 31)
                prices = 100 + np.cumsum(np.random.randn(30) * 2)
            else:
                days = data.get('days', np.arange(1, 31))
                prices = data.get('prices', 100 + np.cumsum(np.random.randn(30) * 2))
            
            fig, ax = plt.subplots(figsize=self.default_figsize)
            ax.plot(days, prices, 'b-', linewidth=2, label=f'{stock_code} 价格走势')
            ax.set_title(f'{stock_code} 股价分析图表', fontsize=14, fontweight='bold')
            ax.set_xlabel('天数')
            ax.set_ylabel('价格')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # 添加一些统计信息
            current_price = prices[-1]
            max_price = np.max(prices)
            min_price = np.min(prices)
            
            ax.text(0.02, 0.98, f'当前价格: {current_price:.2f}\n最高价: {max_price:.2f}\n最低价: {min_price:.2f}',
                   transform=ax.transAxes, verticalalignment='top',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor=self.success_color, alpha=0.7))
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            return self.generate_error_chart(f"股票图表生成失败: {str(e)}")
    
    def generate_error_chart(self, error_message):
        """生成错误图表"""
        try:
            import matplotlib.pyplot as plt
            
            # 清除之前的图表
            plt.clf()
            
            fig, ax = plt.subplots(figsize=self.default_figsize)
            
            # 创建错误显示
            ax.text(0.5, 0.5, f'❌ {error_message}', 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes,
                   fontsize=16,
                   fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.5", facecolor=self.error_color, alpha=0.8))
            
            ax.set_title('图表生成错误', fontsize=14, fontweight='bold', color='red')
            ax.axis('off')
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            # 如果连错误图表都无法生成，创建一个最基本的图表
            return self._create_minimal_error_chart(str(e))
    
    def _create_minimal_error_chart(self, error_message):
        """创建最小错误图表"""
        try:
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.text(0.5, 0.5, f'图表错误: {error_message}', 
                   ha='center', va='center', fontsize=12)
            ax.set_title('错误')
            ax.axis('off')
            return fig
        except:
            # 最后的备选方案
            return None
    
    def generate_empty_chart(self, message="等待数据..."):
        """生成空白图表"""
        try:
            import matplotlib.pyplot as plt
            
            plt.clf()
            
            fig, ax = plt.subplots(figsize=self.default_figsize)
            
            ax.text(0.5, 0.5, f'📊 {message}', 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes,
                   fontsize=18,
                   bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.5))
            
            ax.set_title('数据图表', fontsize=14)
            ax.axis('off')
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            return self.generate_error_chart(f"空白图表生成失败: {str(e)}")
    
    def generate_analysis_chart(self, analysis_data):
        """生成分析结果图表"""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            plt.clf()
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            # 上半部分：价格走势
            if 'price_data' in analysis_data:
                price_data = analysis_data['price_data']
                ax1.plot(price_data['dates'], price_data['prices'], 'b-', linewidth=2)
                ax1.set_title('价格走势分析')
                ax1.set_ylabel('价格')
                ax1.grid(True, alpha=0.3)
            else:
                # 模拟数据
                days = np.arange(1, 31)
                prices = 100 + np.cumsum(np.random.randn(30) * 2)
                ax1.plot(days, prices, 'b-', linewidth=2)
                ax1.set_title('价格走势分析（模拟数据）')
                ax1.set_ylabel('价格')
                ax1.grid(True, alpha=0.3)
            
            # 下半部分：分析指标
            if 'indicators' in analysis_data:
                indicators = analysis_data['indicators']
                labels = list(indicators.keys())
                values = list(indicators.values())
                
                ax2.bar(labels, values, color=['green' if v > 0 else 'red' for v in values])
                ax2.set_title('技术指标分析')
                ax2.set_ylabel('指标值')
            else:
                # 模拟指标
                labels = ['RSI', 'MACD', '布林带', 'KDJ']
                values = np.random.randn(4) * 10
                colors = ['green' if v > 0 else 'red' for v in values]
                
                ax2.bar(labels, values, color=colors)
                ax2.set_title('技术指标分析（模拟数据）')
                ax2.set_ylabel('指标值')
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            return self.generate_error_chart(f"分析图表生成失败: {str(e)}")
    
    def safe_chart_return(self, chart_result):
        """安全返回图表结果，确保不会返回字符串给Plot组件"""
        if chart_result is None:
            return self.generate_empty_chart("图表生成失败")

        # 检查是否是matplotlib图表对象
        try:
            import matplotlib.figure

            if isinstance(chart_result, matplotlib.figure.Figure):
                return chart_result
            elif hasattr(chart_result, 'gcf'):  # pyplot对象
                return chart_result.gcf()
            else:
                # 如果不是图表对象，生成错误图表
                return self.generate_error_chart("返回的不是有效的图表对象")

        except Exception as e:
            return self.generate_error_chart(f"图表验证失败: {str(e)}")

# 创建全局图表生成器实例
chart_generator = ChartGenerator()

def get_chart_generator():
    """获取图表生成器实例"""
    return chart_generator

def safe_generate_chart(chart_type, *args, **kwargs):
    """安全生成图表的便捷函数"""
    generator = get_chart_generator()
    
    try:
        if chart_type == "stock":
            result = generator.generate_stock_chart(*args, **kwargs)
        elif chart_type == "error":
            result = generator.generate_error_chart(*args, **kwargs)
        elif chart_type == "empty":
            result = generator.generate_empty_chart(*args, **kwargs)
        elif chart_type == "analysis":
            result = generator.generate_analysis_chart(*args, **kwargs)
        else:
            result = generator.generate_error_chart(f"未知图表类型: {chart_type}")
        
        return generator.safe_chart_return(result)
        
    except Exception as e:
        return generator.generate_error_chart(f"图表生成异常: {str(e)}")
