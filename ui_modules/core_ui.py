#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents 核心UI类模块
负责UI的核心逻辑和状态管理
"""

import sys
import os
import json
import asyncio
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class OptimizedTradingAgentsUI:
    """优化版TradingAgents UI核心类"""

    def __init__(self):
        """初始化UI核心组件"""
        self.current_result = None
        self.analysis_progress = 0
        self.current_agent = "待机中"
        
        # 初始化增强功能模块
        self._initialize_enhanced_modules()
    
    def _initialize_enhanced_modules(self):
        """初始化增强功能模块"""
        try:
            from core.enhanced_llm_manager import EnhancedLLMManager
            from core.agent_model_manager import AgentModelManager
            from core.enhanced_report_generator import EnhancedReportGenerator
            from core.intelligent_summarizer import ContentProcessor

            self.llm_manager = EnhancedLLMManager()
            self.agent_manager = AgentModelManager()
            self.report_generator = EnhancedReportGenerator()
            self.content_processor = ContentProcessor()
            self.enhanced_features_available = True

            print("✅ 增强功能模块初始化成功")

        except ImportError as e:
            print(f"⚠️ 增强功能模块未找到: {e}")
            self.enhanced_features_available = False
    
    def get_system_info(self):
        """获取系统信息"""
        return {
            "系统状态": "✅ 正常运行",
            "智能体": "15个专业智能体",
            "LLM状态": "✅ 多模型支持",
            "增强功能": "✅ 已启用" if self.enhanced_features_available else "⚠️ 基础模式"
        }
    
    def update_progress(self, progress, description=""):
        """更新分析进度"""
        self.analysis_progress = progress
        self.current_agent = description
        return progress, description
    
    def reset_state(self):
        """重置UI状态"""
        self.current_result = None
        self.analysis_progress = 0
        self.current_agent = "待机中"
        print("🔄 UI状态已重置")
    
    def get_status_summary(self):
        """获取状态摘要"""
        return {
            "current_result": bool(self.current_result),
            "analysis_progress": self.analysis_progress,
            "current_agent": self.current_agent,
            "enhanced_features": self.enhanced_features_available,
            "timestamp": datetime.now().isoformat()
        }

# 创建全局UI实例
ui_instance = OptimizedTradingAgentsUI()

def get_ui_instance():
    """获取UI实例"""
    return ui_instance

def reset_ui_instance():
    """重置UI实例"""
    global ui_instance
    ui_instance.reset_state()
    return ui_instance
