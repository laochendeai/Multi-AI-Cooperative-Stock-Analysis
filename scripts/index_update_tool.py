#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents 索引更新工具
提供索引管理、诊断、修复等功能
"""

import os
import sys
import json
import shutil
import argparse
import importlib
import importlib.util
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class IndexUpdateTool:
    """索引更新工具主类"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backup_dir = self.project_root / "backups"
        self.config_dir = self.project_root / "config"
        self.core_dir = self.project_root / "core"
        
        # 确保目录存在
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self):
        """创建备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        # 备份关键文件
        files_to_backup = [
            "final_ui.py",
            "app_tradingagents_upgraded.py",
            "app_enhanced.py"
        ]
        
        dirs_to_backup = [
            "core",
            "config",
            "tradingagents"
        ]
        
        print(f"📦 创建备份到: {backup_path}")
        
        # 备份文件
        for file_name in files_to_backup:
            src = self.project_root / file_name
            if src.exists():
                shutil.copy2(src, backup_path / file_name)
                print(f"✅ 备份文件: {file_name}")
        
        # 备份目录
        for dir_name in dirs_to_backup:
            src = self.project_root / dir_name
            if src.exists():
                shutil.copytree(src, backup_path / dir_name)
                print(f"✅ 备份目录: {dir_name}")
        
        print(f"🎉 备份完成: {backup_path}")
        return backup_path
    
    def diagnose_indexes(self):
        """诊断索引状态"""
        print("🔍 开始索引诊断...")
        
        results = {
            "ui_components": self._check_ui_components(),
            "agent_registry": self._check_agent_registry(),
            "llm_providers": self._check_llm_providers(),
            "config_files": self._check_config_files(),
            "dependencies": self._check_dependencies()
        }
        
        # 输出诊断结果
        print("\n📊 诊断结果:")
        print("=" * 50)
        
        all_passed = True
        for check_name, result in results.items():
            status_icon = "✅" if result["status"] == "pass" else "❌"
            print(f"{status_icon} {check_name}: {result['message']}")
            
            if result["status"] != "pass":
                all_passed = False
                if "details" in result:
                    for detail in result["details"]:
                        print(f"   • {detail}")
        
        if all_passed:
            print("\n🎉 所有检查通过！")
        else:
            print("\n⚠️ 发现问题，建议运行修复命令")
        
        return results
    
    def _check_ui_components(self):
        """检查UI组件"""
        try:
            # 检查final_ui.py是否存在
            ui_file = self.project_root / "final_ui.py"
            if not ui_file.exists():
                return {
                    "status": "fail",
                    "message": "final_ui.py文件不存在",
                    "details": ["请确认文件路径正确"]
                }
            
            # 尝试导入UI类
            spec = importlib.util.spec_from_file_location("final_ui", ui_file)
            final_ui = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(final_ui)
            
            # 检查关键类是否存在
            if not hasattr(final_ui, 'FinalTradingAgentsUI'):
                return {
                    "status": "fail",
                    "message": "FinalTradingAgentsUI类不存在",
                    "details": ["检查类定义是否正确"]
                }
            
            return {
                "status": "pass",
                "message": "UI组件正常"
            }
            
        except Exception as e:
            return {
                "status": "fail",
                "message": f"UI组件检查失败: {str(e)}",
                "details": [str(e)]
            }
    
    def _check_agent_registry(self):
        """检查智能体注册表"""
        try:
            # 检查智能体目录
            agents_dir = self.project_root / "tradingagents" / "agents"
            if not agents_dir.exists():
                return {
                    "status": "fail",
                    "message": "智能体目录不存在",
                    "details": ["tradingagents/agents目录缺失"]
                }
            
            # 检查智能体子目录
            required_subdirs = ["analysts", "researchers", "risk_mgmt", "trader"]
            missing_dirs = []
            
            for subdir in required_subdirs:
                if not (agents_dir / subdir).exists():
                    missing_dirs.append(subdir)
            
            if missing_dirs:
                return {
                    "status": "fail",
                    "message": f"缺少智能体子目录: {', '.join(missing_dirs)}",
                    "details": missing_dirs
                }
            
            return {
                "status": "pass",
                "message": "智能体注册表正常"
            }
            
        except Exception as e:
            return {
                "status": "fail",
                "message": f"智能体注册表检查失败: {str(e)}",
                "details": [str(e)]
            }
    
    def _check_llm_providers(self):
        """检查LLM提供商配置"""
        try:
            # 检查配置文件
            llm_config_file = self.config_dir / "llm_config.json"
            template_file = self.config_dir / "llm_config.template.json"
            
            if not template_file.exists():
                return {
                    "status": "fail",
                    "message": "LLM配置模板文件不存在",
                    "details": ["config/llm_config.template.json缺失"]
                }
            
            # 如果配置文件不存在，从模板创建
            if not llm_config_file.exists():
                shutil.copy2(template_file, llm_config_file)
                print("📝 从模板创建LLM配置文件")
            
            # 验证配置文件格式
            with open(llm_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            required_keys = ["llm_config", "custom_llm_providers", "version"]
            missing_keys = [key for key in required_keys if key not in config]
            
            if missing_keys:
                return {
                    "status": "fail",
                    "message": f"LLM配置文件缺少必需字段: {', '.join(missing_keys)}",
                    "details": missing_keys
                }
            
            return {
                "status": "pass",
                "message": "LLM提供商配置正常"
            }
            
        except Exception as e:
            return {
                "status": "fail",
                "message": f"LLM提供商检查失败: {str(e)}",
                "details": [str(e)]
            }
    
    def _check_config_files(self):
        """检查配置文件"""
        try:
            required_configs = [
                "llm_config.template.json",
                "agent_model_config.template.json"
            ]
            
            missing_configs = []
            for config_file in required_configs:
                if not (self.config_dir / config_file).exists():
                    missing_configs.append(config_file)
            
            if missing_configs:
                return {
                    "status": "fail",
                    "message": f"缺少配置文件: {', '.join(missing_configs)}",
                    "details": missing_configs
                }
            
            return {
                "status": "pass",
                "message": "配置文件完整"
            }
            
        except Exception as e:
            return {
                "status": "fail",
                "message": f"配置文件检查失败: {str(e)}",
                "details": [str(e)]
            }
    
    def _check_dependencies(self):
        """检查依赖包"""
        try:
            required_packages = [
                "gradio",
                "pandas", 
                "asyncio",
                "json"
            ]
            
            missing_packages = []
            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    missing_packages.append(package)
            
            if missing_packages:
                return {
                    "status": "fail",
                    "message": f"缺少依赖包: {', '.join(missing_packages)}",
                    "details": [f"运行: pip install {' '.join(missing_packages)}"]
                }
            
            return {
                "status": "pass",
                "message": "依赖包完整"
            }
            
        except Exception as e:
            return {
                "status": "fail",
                "message": f"依赖检查失败: {str(e)}",
                "details": [str(e)]
            }
    
    def repair_indexes(self):
        """修复索引问题"""
        print("🔧 开始索引修复...")
        
        # 先运行诊断
        diagnosis = self.diagnose_indexes()
        
        repair_actions = []
        
        # 根据诊断结果确定修复动作
        for check_name, result in diagnosis.items():
            if result["status"] != "pass":
                if check_name == "config_files":
                    repair_actions.append(self._repair_config_files)
                elif check_name == "llm_providers":
                    repair_actions.append(self._repair_llm_config)
                elif check_name == "dependencies":
                    repair_actions.append(self._repair_dependencies)
        
        # 执行修复动作
        if repair_actions:
            print(f"\n🛠️ 执行{len(repair_actions)}个修复动作...")
            
            for action in repair_actions:
                try:
                    action()
                except Exception as e:
                    print(f"❌ 修复动作失败: {e}")
        else:
            print("✅ 无需修复")
        
        print("🎉 修复完成")
    
    def _repair_config_files(self):
        """修复配置文件"""
        print("📝 修复配置文件...")
        
        # 创建默认LLM配置
        llm_config_template = {
            "llm_config": {},
            "custom_llm_providers": {},
            "version": "1.0"
        }
        
        template_path = self.config_dir / "llm_config.template.json"
        if not template_path.exists():
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(llm_config_template, f, indent=2, ensure_ascii=False)
            print("✅ 创建LLM配置模板")
        
        # 创建默认智能体配置
        agent_config_template = {
            "market_analyst": "moonshot:moonshot-v1-8k",
            "sentiment_analyst": "阿里百炼:qwen-turbo",
            "news_analyst": "阿里百炼:qwen-turbo",
            "fundamentals_analyst": "阿里百炼:qwen-turbo"
        }
        
        agent_template_path = self.config_dir / "agent_model_config.template.json"
        if not agent_template_path.exists():
            with open(agent_template_path, 'w', encoding='utf-8') as f:
                json.dump(agent_config_template, f, indent=2, ensure_ascii=False)
            print("✅ 创建智能体配置模板")
    
    def _repair_llm_config(self):
        """修复LLM配置"""
        print("🔧 修复LLM配置...")
        
        config_file = self.config_dir / "llm_config.json"
        template_file = self.config_dir / "llm_config.template.json"
        
        if template_file.exists() and not config_file.exists():
            shutil.copy2(template_file, config_file)
            print("✅ 从模板恢复LLM配置")
    
    def _repair_dependencies(self):
        """修复依赖问题"""
        print("📦 修复依赖问题...")
        print("💡 请手动运行: pip install -r requirements.txt")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="TradingAgents索引更新工具")
    parser.add_argument("action", choices=["backup", "diagnose", "repair", "all"],
                       help="执行的操作")
    
    args = parser.parse_args()
    
    tool = IndexUpdateTool()
    
    if args.action == "backup":
        tool.create_backup()
    elif args.action == "diagnose":
        tool.diagnose_indexes()
    elif args.action == "repair":
        tool.repair_indexes()
    elif args.action == "all":
        print("🚀 执行完整索引更新流程...")
        tool.create_backup()
        tool.diagnose_indexes()
        tool.repair_indexes()
        print("🎉 完整流程执行完毕")

if __name__ == "__main__":
    main()
