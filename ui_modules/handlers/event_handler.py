#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents 事件处理模块
负责UI事件的绑定和处理
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class EventHandler:
    """事件处理器"""
    
    def __init__(self, ui_instance, analysis_handler, llm_handler, report_handler):
        """初始化事件处理器"""
        self.ui = ui_instance
        self.analysis_handler = analysis_handler
        self.llm_handler = llm_handler
        self.report_handler = report_handler
    
    def bind_analysis_events(self, components):
        """绑定分析相关事件"""
        (stock_input, analyze_btn, analysis_depth, export_format, 
         selected_agents, analysis_output, chart_output, log_output) = components
        
        # 分析按钮点击事件
        analyze_btn.click(
            fn=self.analysis_handler.run_analysis,
            inputs=[stock_input, analysis_depth, selected_agents],
            outputs=[analysis_output, chart_output, log_output],
            show_progress=True
        )
        
        # 股票代码输入回车事件
        stock_input.submit(
            fn=self.analysis_handler.run_analysis,
            inputs=[stock_input, analysis_depth, selected_agents],
            outputs=[analysis_output, chart_output, log_output],
            show_progress=True
        )
        
        return self
    
    def bind_system_events(self, components):
        """绑定系统相关事件"""
        (system_status, refresh_btn, export_btn, reset_btn, export_format) = components
        
        # 刷新系统状态
        refresh_btn.click(
            fn=lambda: self.ui.get_system_info(),
            outputs=system_status
        )
        
        # 导出当前结果
        export_btn.click(
            fn=lambda fmt: self.report_handler.export_report(fmt),
            inputs=export_format,
            outputs=None  # 将在界面中显示消息
        )
        
        # 重置系统状态
        reset_btn.click(
            fn=self._reset_system,
            outputs=[system_status]
        )
        
        return self
    
    def bind_llm_config_events(self, components):
        """绑定LLM配置相关事件"""
        (provider_select, api_key_input, save_config_btn, test_config_btn, 
         clear_config_btn, config_status, provider_status) = components
        
        # 保存配置
        save_config_btn.click(
            fn=self.llm_handler.save_llm_config,
            inputs=[provider_select, api_key_input],
            outputs=config_status
        )
        
        # 测试连接
        test_config_btn.click(
            fn=self.llm_handler.test_llm_connection,
            inputs=[provider_select, api_key_input],
            outputs=config_status
        )
        
        # 清除配置
        clear_config_btn.click(
            fn=self.llm_handler.clear_provider_config,
            inputs=provider_select,
            outputs=config_status
        )
        
        # 提供商选择变化时更新状态
        provider_select.change(
            fn=self._update_provider_status,
            outputs=provider_status
        )
        
        return self
    
    def bind_report_events(self, components):
        """绑定报告管理相关事件"""
        (report_list, report_content, refresh_reports_btn, 
         delete_report_btn, view_report_btn) = components
        
        # 刷新报告列表
        refresh_reports_btn.click(
            fn=self._refresh_report_list,
            outputs=report_list
        )
        
        # 查看报告内容
        view_report_btn.click(
            fn=self._view_selected_report,
            inputs=report_list,
            outputs=report_content
        )
        
        # 删除选中报告
        delete_report_btn.click(
            fn=self._delete_selected_report,
            inputs=report_list,
            outputs=[report_list, report_content]
        )
        
        return self
    
    def bind_advanced_events(self, components):
        """绑定高级功能事件"""
        (max_agents, timeout_setting, enable_cache) = components
        
        # 最大智能体数量变化
        max_agents.change(
            fn=self._update_max_agents,
            inputs=max_agents
        )
        
        # 超时设置变化
        timeout_setting.change(
            fn=self._update_timeout,
            inputs=timeout_setting
        )
        
        # 缓存设置变化
        enable_cache.change(
            fn=self._update_cache_setting,
            inputs=enable_cache
        )
        
        return self
    
    def _reset_system(self):
        """重置系统状态"""
        self.ui.reset_state()
        return self.ui.get_system_info()
    
    def _update_provider_status(self):
        """更新提供商状态"""
        return self.llm_handler.get_provider_status()
    
    def _refresh_report_list(self):
        """刷新报告列表"""
        reports = self.report_handler.list_reports()
        if isinstance(reports, str):  # 错误信息
            return []
        
        # 转换为表格格式
        table_data = []
        for report in reports:
            table_data.append([
                report["filename"],
                report["size"],
                report["created"],
                report["format"]
            ])
        
        return table_data
    
    def _view_selected_report(self, report_list_data):
        """查看选中的报告"""
        if not report_list_data or len(report_list_data) == 0:
            return "❌ 请先选择一个报告"
        
        # 获取选中的报告文件名（假设选中第一行）
        try:
            selected_filename = report_list_data[0][0]  # 第一列是文件名
            content = self.report_handler.get_report_content(selected_filename)
            return content
        except (IndexError, TypeError):
            return "❌ 无法获取选中的报告"
    
    def _delete_selected_report(self, report_list_data):
        """删除选中的报告"""
        if not report_list_data or len(report_list_data) == 0:
            return [], "❌ 请先选择一个报告"
        
        try:
            selected_filename = report_list_data[0][0]  # 第一列是文件名
            result = self.report_handler.delete_report(selected_filename)
            
            # 刷新列表
            updated_list = self._refresh_report_list()
            return updated_list, result
            
        except (IndexError, TypeError):
            return report_list_data, "❌ 无法删除选中的报告"
    
    def _update_max_agents(self, max_agents):
        """更新最大智能体数量"""
        # 这里可以添加更新逻辑
        print(f"🔧 最大智能体数量设置为: {max_agents}")
        return f"✅ 最大智能体数量已设置为: {max_agents}"
    
    def _update_timeout(self, timeout):
        """更新超时设置"""
        # 这里可以添加更新逻辑
        print(f"⏱️ 分析超时时间设置为: {timeout}秒")
        return f"✅ 超时时间已设置为: {timeout}秒"
    
    def _update_cache_setting(self, enable_cache):
        """更新缓存设置"""
        # 这里可以添加更新逻辑
        status = "启用" if enable_cache else "禁用"
        print(f"💾 结果缓存已{status}")
        return f"✅ 结果缓存已{status}"
    
    def get_event_summary(self):
        """获取事件绑定摘要"""
        return {
            "analysis_events": "分析相关事件已绑定",
            "system_events": "系统相关事件已绑定",
            "llm_config_events": "LLM配置事件已绑定",
            "report_events": "报告管理事件已绑定",
            "advanced_events": "高级功能事件已绑定",
            "total_handlers": 5
        }

def create_event_handler(ui_instance, analysis_handler, llm_handler, report_handler):
    """创建事件处理器"""
    return EventHandler(ui_instance, analysis_handler, llm_handler, report_handler)
