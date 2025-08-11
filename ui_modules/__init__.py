#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents UI模块包
模块化UI架构的入口点
"""

__version__ = "2.0.0"
__author__ = "TradingAgents Team"
__description__ = "TradingAgents 模块化UI架构"

# 导入核心模块
from .core_ui import get_ui_instance, reset_ui_instance
from .main_interface import create_modular_interface, ModularInterface

# 导入处理器模块
from .handlers.analysis_handler import create_analysis_handler
from .handlers.llm_handler import create_llm_handler
from .handlers.report_handler import create_report_handler
from .handlers.event_handler import create_event_handler

# 导入组件模块
from .components.main_components import (
    create_header_component,
    create_analysis_input_components,
    create_system_status_components,
    create_results_components,
    create_config_components,
    create_footer_component,
    get_custom_css
)

# 模块信息
MODULE_INFO = {
    "name": "TradingAgents UI Modules",
    "version": __version__,
    "description": __description__,
    "modules": {
        "core": ["core_ui"],
        "handlers": ["analysis_handler", "llm_handler", "report_handler", "event_handler"],
        "components": ["main_components"],
        "interface": ["main_interface"]
    },
    "features": [
        "模块化架构",
        "高内聚低耦合",
        "易于维护扩展",
        "独立测试支持",
        "热插拔能力"
    ]
}

def get_module_info():
    """获取模块信息"""
    return MODULE_INFO

def initialize_modules():
    """初始化所有模块"""
    print(f"🚀 初始化TradingAgents UI模块 v{__version__}")
    
    try:
        # 初始化核心UI
        ui = get_ui_instance()
        print("✅ 核心UI模块初始化成功")
        
        # 初始化处理器
        analysis_handler = create_analysis_handler(ui)
        llm_handler = create_llm_handler(ui)
        report_handler = create_report_handler(ui)
        event_handler = create_event_handler(ui, analysis_handler, llm_handler, report_handler)
        print("✅ 处理器模块初始化成功")
        
        print("🎉 所有模块初始化完成")
        return True
        
    except Exception as e:
        print(f"❌ 模块初始化失败: {e}")
        return False

# 导出的公共接口
__all__ = [
    # 核心功能
    "get_ui_instance",
    "reset_ui_instance", 
    "create_modular_interface",
    "ModularInterface",
    
    # 处理器创建函数
    "create_analysis_handler",
    "create_llm_handler", 
    "create_report_handler",
    "create_event_handler",
    
    # 组件创建函数
    "create_header_component",
    "create_analysis_input_components",
    "create_system_status_components", 
    "create_results_components",
    "create_config_components",
    "create_footer_component",
    "get_custom_css",
    
    # 工具函数
    "get_module_info",
    "initialize_modules",
    
    # 常量
    "MODULE_INFO"
]
