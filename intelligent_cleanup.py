#!/usr/bin/env python3
"""
智能代码仓库清理工具
专业的代码仓库管理助手
"""

import os
import shutil
import subprocess
import json
from pathlib import Path
from datetime import datetime, timedelta
import re

class IntelligentRepoCleanup:
    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path)
        self.backup_dir = self.repo_path / "backup_temp"
        self.cleanup_log = []
        self.preserved_files = []
        self.cleaned_files = []
        
        # 核心文件模式
        self.core_patterns = {
            'source_dirs': ['src/', 'lib/', 'core/', 'tradingagents/', 'ui_modules/'],
            'config_files': ['package.json', 'requirements.txt', 'Dockerfile', '.env.example', 
                           'config/', 'pyproject.toml', 'setup.py', 'setup.cfg'],
            'docs': ['README.md', 'LICENSE', 'CHANGELOG.md', 'docs/', 'RELEASE_NOTES.md'],
            'git_meta': ['.gitignore', '.gitattributes', '.github/']
        }
        
        # 清理目标模式
        self.cleanup_patterns = {
            'test_files': ['tests/', '__test__/', '*test*.py', '*.spec.js', '*_test.py', 
                          'test_*.py', 'minimal_test_app.py', 'debug_app.py'],
            'ai_docs': ['*_REPORT.md', '*_SUMMARY.md', '*_GUIDE.md', '*_explanation.txt',
                       '*_FIX_*.md', '*_COMPLETION_*.md', '*_OPTIMIZATION_*.md'],
            'dev_cache': ['.vscode/', '.idea/', '__pycache__/', '*.pyc', '.pytest_cache/',
                         'node_modules/', '.cache/'],
            'build_artifacts': ['dist/', 'build/', '*.egg-info/', '.tox/', 'coverage/',
                              'htmlcov/', '.coverage'],
            'temp_files': ['*.tmp', '*.temp', '*.log', '*.bak', '*~', '.DS_Store'],
            'backup_files': ['backups/', '*_backup_*.py', '*_backup_*.txt']
        }
    
    def get_repo_size(self):
        """获取仓库大小"""
        try:
            result = subprocess.run(['du', '-sh', '.'], capture_output=True, text=True, cwd=self.repo_path)
            if result.returncode == 0:
                return result.stdout.split()[0]
        except:
            pass
        return "Unknown"
    
    def is_recently_modified(self, file_path, days=3):
        """检查文件是否在最近几天内修改过"""
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            return datetime.now() - mtime < timedelta(days=days)
        except:
            return False
    
    def should_preserve_file(self, file_path):
        """判断文件是否应该保留"""
        path_str = str(file_path)
        
        # 保留用户自定义文件
        if 'user_custom' in path_str.lower():
            return True, "用户自定义文件"
        
        # 保留核心源代码目录
        for pattern in self.core_patterns['source_dirs']:
            if path_str.startswith(pattern) or f"/{pattern}" in path_str:
                return True, "核心源代码"
        
        # 保留关键配置文件
        for pattern in self.core_patterns['config_files']:
            if pattern in path_str or file_path.name == pattern:
                return True, "关键配置文件"
        
        # 保留必要文档
        for pattern in self.core_patterns['docs']:
            if pattern in path_str or file_path.name == pattern:
                return True, "必要文档"
        
        # 保留git元数据
        for pattern in self.core_patterns['git_meta']:
            if pattern in path_str:
                return True, "Git元数据"
        
        # 保留主要应用文件
        if file_path.name in ['final_integrated_app.py', 'app_enhanced.py']:
            return True, "主要应用文件"
        
        return False, ""
    
    def should_cleanup_file(self, file_path):
        """判断文件是否应该清理"""
        path_str = str(file_path)
        
        # 检查各种清理模式
        for category, patterns in self.cleanup_patterns.items():
            for pattern in patterns:
                if self.match_pattern(path_str, pattern):
                    return True, category
        
        return False, ""
    
    def match_pattern(self, path_str, pattern):
        """匹配文件模式"""
        if pattern.endswith('/'):
            return pattern[:-1] in path_str.split('/')
        elif '*' in pattern:
            import fnmatch
            return fnmatch.fnmatch(os.path.basename(path_str), pattern)
        else:
            return pattern in path_str
    
    def backup_recent_files(self, file_path):
        """备份最近修改的文件"""
        if self.is_recently_modified(file_path):
            self.backup_dir.mkdir(exist_ok=True)
            backup_path = self.backup_dir / file_path.name
            try:
                if file_path.is_file():
                    shutil.copy2(file_path, backup_path)
                elif file_path.is_dir():
                    shutil.copytree(file_path, backup_path, dirs_exist_ok=True)
                return True
            except Exception as e:
                print(f"备份失败 {file_path}: {e}")
        return False
    
    def analyze_files(self):
        """分析文件并分类"""
        to_preserve = []
        to_cleanup = []
        
        for root, dirs, files in os.walk(self.repo_path):
            # 跳过.git目录
            if '.git' in dirs:
                dirs.remove('.git')
            
            root_path = Path(root)
            
            # 检查目录
            for dir_name in dirs[:]:  # 使用切片复制避免修改迭代中的列表
                dir_path = root_path / dir_name
                should_preserve, reason = self.should_preserve_file(dir_path)
                should_cleanup, cleanup_reason = self.should_cleanup_file(dir_path)
                
                if should_preserve:
                    to_preserve.append((dir_path, reason))
                elif should_cleanup:
                    to_cleanup.append((dir_path, cleanup_reason))
            
            # 检查文件
            for file_name in files:
                file_path = root_path / file_name
                should_preserve, reason = self.should_preserve_file(file_path)
                should_cleanup, cleanup_reason = self.should_cleanup_file(file_path)
                
                if should_preserve:
                    to_preserve.append((file_path, reason))
                elif should_cleanup:
                    to_cleanup.append((file_path, cleanup_reason))
        
        return to_preserve, to_cleanup
    
    def preview_cleanup(self):
        """预览清理操作"""
        print("🔍 分析项目文件结构...")
        to_preserve, to_cleanup = self.analyze_files()
        
        print(f"\n📊 分析结果:")
        print(f"  保留文件: {len(to_preserve)} 个")
        print(f"  清理文件: {len(to_cleanup)} 个")
        
        print(f"\n✅ 将保留的核心文件:")
        for file_path, reason in to_preserve[:10]:  # 只显示前10个
            print(f"  📁 {file_path} ({reason})")
        if len(to_preserve) > 10:
            print(f"  ... 还有 {len(to_preserve) - 10} 个文件")
        
        print(f"\n🗑️ 将清理的文件:")
        cleanup_by_category = {}
        for file_path, category in to_cleanup:
            if category not in cleanup_by_category:
                cleanup_by_category[category] = []
            cleanup_by_category[category].append(file_path)
        
        for category, files in cleanup_by_category.items():
            print(f"  📂 {category}: {len(files)} 个文件")
            for file_path in files[:3]:  # 只显示前3个
                print(f"    🗑️ {file_path}")
            if len(files) > 3:
                print(f"    ... 还有 {len(files) - 3} 个文件")
        
        return to_preserve, to_cleanup

    def execute_cleanup(self, to_cleanup, confirm=True):
        """执行清理操作"""
        if confirm:
            response = input(f"\n⚠️ 确认清理 {len(to_cleanup)} 个文件/目录? (y/N): ")
            if response.lower() != 'y':
                print("❌ 清理操作已取消")
                return False

        print("\n🔄 开始清理操作...")

        # 创建备份目录
        self.backup_dir.mkdir(exist_ok=True)

        cleaned_count = 0
        backed_up_count = 0

        for file_path, category in to_cleanup:
            try:
                # 备份最近修改的文件
                if self.backup_recent_files(file_path):
                    backed_up_count += 1
                    print(f"💾 已备份: {file_path}")

                # 使用git rm删除已跟踪的文件
                if file_path.exists():
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

                self.cleaned_files.append((file_path, category))
                cleaned_count += 1

            except Exception as e:
                print(f"❌ 处理失败 {file_path}: {e}")

        print(f"\n✅ 清理完成!")
        print(f"  🗑️ 已清理: {cleaned_count} 个文件/目录")
        print(f"  💾 已备份: {backed_up_count} 个最近修改的文件")

        return True

    def generate_cleanup_report(self):
        """生成清理报告"""
        report_path = self.repo_path / "cleaned_files.log"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# TradingAgents 仓库清理报告\n")
            f.write(f"清理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## 清理统计\n")
            f.write(f"总清理文件数: {len(self.cleaned_files)}\n\n")

            # 按类别统计
            category_stats = {}
            for _, category in self.cleaned_files:
                category_stats[category] = category_stats.get(category, 0) + 1

            f.write("## 按类别统计\n")
            for category, count in category_stats.items():
                f.write(f"- {category}: {count} 个文件\n")

            f.write("\n## 清理的文件列表\n")
            for file_path, category in self.cleaned_files:
                f.write(f"- [{category}] {file_path}\n")

        print(f"📋 清理报告已生成: {report_path}")
        return report_path

if __name__ == "__main__":
    cleanup = IntelligentRepoCleanup()

    print("🤖 TradingAgents 智能仓库清理工具")
    print("=" * 50)

    # 获取清理前大小
    initial_size = cleanup.get_repo_size()
    print(f"📊 清理前仓库大小: {initial_size}")

    # 预览清理
    to_preserve, to_cleanup = cleanup.preview_cleanup()

    # 执行清理
    if cleanup.execute_cleanup(to_cleanup):
        # 生成报告
        cleanup.generate_cleanup_report()

        # 获取清理后大小
        final_size = cleanup.get_repo_size()
        print(f"📊 清理后仓库大小: {final_size}")

        # 计算精简率
        try:
            initial_mb = float(initial_size.replace('M', ''))
            final_mb = float(final_size.replace('M', ''))
            reduction_rate = (initial_mb - final_mb) / initial_mb * 100
            print(f"📈 仓库精简率: {reduction_rate:.1f}%")
        except:
            print("📈 仓库精简率: 计算失败")

        print("\n🎉 清理完成! 可以继续进行git提交操作。")
