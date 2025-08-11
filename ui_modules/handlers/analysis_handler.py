#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents 分析处理模块
负责股票分析的核心逻辑
"""

import sys
import os
import asyncio
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class AnalysisHandler:
    """分析处理器"""
    
    def __init__(self, ui_instance):
        """初始化分析处理器"""
        self.ui = ui_instance
        self.is_analyzing = False
    
    def run_analysis(self, stock_code, analysis_depth, selected_agents, progress=None):
        """运行股票分析"""
        try:
            if not stock_code or not stock_code.strip():
                from ui_modules.utils.chart_utils import safe_generate_chart
                error_chart = safe_generate_chart("error", "请输入股票代码")
                return "❌ 请输入有效的股票代码", error_chart, "未输入股票代码"
            
            if self.is_analyzing:
                from ui_modules.utils.chart_utils import safe_generate_chart
                error_chart = safe_generate_chart("error", "分析正在进行中")
                return "⚠️ 分析正在进行中，请稍候...", error_chart, "分析正在进行中"
            
            self.is_analyzing = True
            
            if progress:
                progress(0.1, desc="初始化系统...")
            
            # 导入分析函数
            try:
                from app_tradingagents_upgraded import analyze_stock_upgraded
            except ImportError as e:
                self.is_analyzing = False
                error_chart = self._generate_error_chart(f"导入失败: {str(e)}")
                return f"❌ 无法导入分析模块: {e}", error_chart, f"导入错误: {str(e)}"
            
            if progress:
                progress(0.3, desc="启动智能体...")
            
            # 映射分析深度
            depth_map = {
                "快速": "快速分析 (1轮辩论)", 
                "标准": "标准分析 (2轮辩论)", 
                "深度": "深度分析 (3轮辩论)", 
                "全面": "全面分析 (4轮辩论)"
            }
            
            # 运行分析
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    analyze_stock_upgraded(
                        symbol=stock_code.strip(),
                        depth=depth_map.get(analysis_depth, "标准分析 (2轮辩论)"),
                        analysts=selected_agents[:4],  # 限制智能体数量
                        use_real_llm=True
                    )
                )
                
                if progress:
                    progress(1.0, desc="分析完成！")
                
                if result:
                    self.ui.current_result = result
                    # 使用安全的图表生成
                    from ui_modules.utils.chart_utils import safe_generate_chart
                    chart_data = safe_generate_chart("stock", stock_code)
                    # 生成分析日志
                    log_data = self._generate_log_data(stock_code, analysis_depth, selected_agents)

                    self.is_analyzing = False
                    return result, chart_data, log_data
                else:
                    self.is_analyzing = False
                    error_chart = self._generate_error_chart("分析失败")
                    return "❌ 分析失败，请检查股票代码或网络连接", error_chart, "分析失败，未生成日志"
                    
            finally:
                loop.close()
                
        except Exception as e:
            self.is_analyzing = False
            error_chart = self._generate_error_chart(f"错误: {str(e)}")
            return f"❌ 分析过程中出现错误: {str(e)}", error_chart, f"错误日志: {str(e)}"
    
    def _generate_chart_data(self, stock_code):
        """生成图表数据"""
        try:
            import matplotlib.pyplot as plt
            import numpy as np

            # 生成模拟数据
            days = np.arange(1, 31)
            prices = 100 + np.cumsum(np.random.randn(30) * 2)

            plt.figure(figsize=(10, 6))
            plt.plot(days, prices, 'b-', linewidth=2, label=f'{stock_code} 价格走势')
            plt.title(f'{stock_code} 股价分析图表')
            plt.xlabel('天数')
            plt.ylabel('价格')
            plt.legend()
            plt.grid(True, alpha=0.3)

            return plt

        except Exception as e:
            print(f"⚠️ 图表生成失败: {e}")
            return self._generate_error_chart(f"图表生成失败: {str(e)}")

    def _generate_error_chart(self, error_message):
        """生成错误图表"""
        try:
            import matplotlib.pyplot as plt

            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, f'❌ {error_message}',
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=plt.gca().transAxes,
                    fontsize=16,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral", alpha=0.7))
            plt.title('图表生成错误')
            plt.axis('off')

            return plt
        except Exception:
            # 如果连错误图表都无法生成，返回None
            return None
    
    def _generate_log_data(self, stock_code, analysis_depth, selected_agents):
        """生成分析日志"""
        log_entries = [
            f"分析完成时间: {datetime.now()}",
            f"股票代码: {stock_code}",
            f"分析深度: {analysis_depth}",
            f"参与智能体: {', '.join(selected_agents)}",
            f"系统状态: {'增强模式' if self.ui.enhanced_features_available else '基础模式'}",
            f"分析结果长度: {len(str(self.ui.current_result)) if self.ui.current_result else 0} 字符"
        ]
        
        return "\n".join(log_entries)
    
    def get_analysis_status(self):
        """获取分析状态"""
        return {
            "is_analyzing": self.is_analyzing,
            "progress": self.ui.analysis_progress,
            "current_agent": self.ui.current_agent,
            "has_result": bool(self.ui.current_result)
        }
    
    def cancel_analysis(self):
        """取消分析"""
        if self.is_analyzing:
            self.is_analyzing = False
            self.ui.current_agent = "分析已取消"
            return "✅ 分析已取消"
        return "⚠️ 没有正在进行的分析"

def create_analysis_handler(ui_instance):
    """创建分析处理器"""
    return AnalysisHandler(ui_instance)
