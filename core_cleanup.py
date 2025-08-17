#!/usr/bin/env python3
"""
TradingAgents 核心清理工具
专门清理与 final_integrated_app.py 启动无关的所有文件
"""

import os
import shutil
import subprocess
import json
from pathlib import Path
from datetime import datetime

class CoreCleanup:
    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path)
        self.cleaned_files = []
        
        # 核心启动必需文件
        self.essential_files = {
            # 主启动文件
            "final_integrated_app.py",
            
            # 核心依赖
            "app_enhanced.py",
            
            # 配置文件
            "requirements.txt",
            "config/llm_config.json",
            "config/agent_model_config.json", 
            "config/README.md",
            
            # 核心模块目录
            "core/",
            "tradingagents/",
            "ui_modules/",
            
            # 数据和资源
            "data/",
            "assets/",
            "exports/",
            
            # 项目文档
            "README.md",
            "RELEASE_NOTES.md",
            "RELEASE_NOTES_v3.0.md",
            
            # Git配置
            ".gitignore",
            ".gitattributes",
            ".env.example"
        }
        
        # 需要清理的文件模式
        self.cleanup_patterns = [
            # 所有测试文件
            "test_*.py",
            "*_test.py", 
            "debug_*.py",
            "minimal_*.py",
            
            # 所有报告文档
            "*_REPORT.md",
            "*_SUMMARY.md", 
            "*_GUIDE.md",
            "*_COMPLETION*.md",
            "*_FIX*.md",
            "*_OPTIMIZATION*.md",
            
            # 备用和临时文件
            "*_backup*.py",
            "*_upgraded.py",
            "*_optimized.py",
            "working_*.py",
            "simplified_*.py",
            "integrated_*.py",
            
            # 工具和脚本
            "fix_*.py",
            "start_*.py",
            "tools/",
            "scripts/",
            
            # 启动脚本
            "*.bat",
            "*.sh",
            
            # 缓存和临时
            "__pycache__/",
            "*.pyc",
            ".vscode/",
            "backup_temp/",
            
            # 分析结果
            "analysis_report_*.json",
            "analysis_report_*.txt",
            "model_cache_backup_*.txt",
            
            # 其他UI文件
            "final_ui*.py",
            "start_donation_ui.py",
            
            # 清理工具本身
            "intelligent_cleanup.py",
            "cleaned_files.log",
            
            # 中文目录
            "阿里百炼qwen-turbo"
        ]
    
    def is_essential_file(self, file_path):
        """检查文件是否为核心必需文件"""
        path_str = str(file_path)
        
        # 检查精确匹配
        if file_path.name in self.essential_files:
            return True
            
        # 检查目录匹配
        for essential in self.essential_files:
            if essential.endswith('/'):
                if essential[:-1] in path_str.split('/') or essential[:-1] in path_str.split('\\'):
                    return True
            elif path_str.endswith(essential):
                return True
        
        return False
    
    def should_cleanup(self, file_path):
        """检查文件是否应该被清理"""
        import fnmatch
        
        path_str = str(file_path)
        file_name = file_path.name
        
        for pattern in self.cleanup_patterns:
            if pattern.endswith('/'):
                # 目录模式
                if pattern[:-1] in path_str.split('/') or pattern[:-1] in path_str.split('\\'):
                    return True
            elif '*' in pattern:
                # 通配符模式
                if fnmatch.fnmatch(file_name, pattern):
                    return True
            else:
                # 精确匹配
                if pattern == file_name or pattern in path_str:
                    return True
        
        return False
    
    def analyze_files(self):
        """分析文件并分类"""
        to_keep = []
        to_cleanup = []
        
        for root, dirs, files in os.walk(self.repo_path):
            # 跳过.git目录
            if '.git' in dirs:
                dirs.remove('.git')
            
            root_path = Path(root)
            
            # 检查目录
            for dir_name in dirs[:]:
                dir_path = root_path / dir_name
                if self.is_essential_file(dir_path):
                    to_keep.append(dir_path)
                elif self.should_cleanup(dir_path):
                    to_cleanup.append(dir_path)
            
            # 检查文件
            for file_name in files:
                file_path = root_path / file_name
                if self.is_essential_file(file_path):
                    to_keep.append(file_path)
                elif self.should_cleanup(file_path):
                    to_cleanup.append(file_path)
        
        return to_keep, to_cleanup
    
    def preview_cleanup(self):
        """预览清理操作"""
        print("🎯 TradingAgents 核心清理工具")
        print("=" * 50)
        print("🎯 目标: 只保留 final_integrated_app.py 启动所需的核心文件")
        print()
        
        to_keep, to_cleanup = self.analyze_files()
        
        print(f"📊 分析结果:")
        print(f"  保留核心文件: {len(to_keep)} 个")
        print(f"  清理多余文件: {len(to_cleanup)} 个")
        print()
        
        print("✅ 保留的核心文件 (前10个):")
        for file_path in to_keep[:10]:
            print(f"  📁 {file_path}")
        if len(to_keep) > 10:
            print(f"  ... 还有 {len(to_keep) - 10} 个核心文件")
        print()
        
        print("🗑️ 将清理的多余文件:")
        for file_path in to_cleanup[:20]:
            print(f"  ❌ {file_path}")
        if len(to_cleanup) > 20:
            print(f"  ... 还有 {len(to_cleanup) - 20} 个文件")
        
        return to_keep, to_cleanup
    
    def execute_cleanup(self, to_cleanup, confirm=True):
        """执行清理操作"""
        if confirm:
            response = input(f"\n⚠️ 确认清理 {len(to_cleanup)} 个多余文件? (y/N): ")
            if response.lower() != 'y':
                print("❌ 清理操作已取消")
                return False
        
        print("\n🔄 开始核心清理...")
        
        cleaned_count = 0
        for file_path in to_cleanup:
            try:
                if file_path.exists():
                    # 使用git rm删除已跟踪的文件
                    try:
                        result = subprocess.run(['git', 'rm', '-rf', str(file_path)], 
                                              capture_output=True, text=True, cwd=self.repo_path)
                        if result.returncode == 0:
                            print(f"🗑️ Git删除: {file_path}")
                        else:
                            # 如果git rm失败，使用系统删除
                            if file_path.is_file():
                                file_path.unlink()
                            elif file_path.is_dir():
                                shutil.rmtree(file_path)
                            print(f"🗑️ 系统删除: {file_path}")
                    except Exception as e:
                        print(f"❌ 删除失败 {file_path}: {e}")
                        continue
                
                self.cleaned_files.append(file_path)
                cleaned_count += 1
                
            except Exception as e:
                print(f"❌ 处理失败 {file_path}: {e}")
        
        print(f"\n✅ 核心清理完成!")
        print(f"  🗑️ 已清理: {cleaned_count} 个多余文件")
        
        return True
    
    def generate_report(self):
        """生成清理报告"""
        report_path = self.repo_path / "CORE_CLEANUP_REPORT.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# TradingAgents 核心清理报告\n\n")
            f.write(f"清理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"清理目标: 只保留 final_integrated_app.py 启动所需的核心文件\n\n")
            
            f.write(f"## 清理统计\n")
            f.write(f"总清理文件数: {len(self.cleaned_files)}\n\n")
            
            f.write("## 清理的文件列表\n")
            for file_path in self.cleaned_files:
                f.write(f"- {file_path}\n")
        
        print(f"📋 清理报告已生成: {report_path}")
        return report_path

if __name__ == "__main__":
    cleanup = CoreCleanup()
    
    # 预览清理
    to_keep, to_cleanup = cleanup.preview_cleanup()
    
    # 执行清理
    if cleanup.execute_cleanup(to_cleanup):
        # 生成报告
        cleanup.generate_report()
        print("\n🎉 核心清理完成! 现在项目只包含启动所需的核心文件。")
