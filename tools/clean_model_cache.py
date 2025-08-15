#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents 模型缓存清理工具
清理损坏的sentence-transformers模型缓存
"""

import os
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path

def find_model_cache_directories():
    """查找所有可能的模型缓存目录"""
    cache_dirs = []
    
    # 常见的缓存目录位置
    possible_dirs = [
        "data/models",
        "models",
        ".cache/torch/sentence_transformers",
        os.path.expanduser("~/.cache/torch/sentence_transformers"),
        os.path.expanduser("~/.cache/huggingface/transformers"),
        "cache/models"
    ]
    
    for dir_path in possible_dirs:
        if os.path.exists(dir_path):
            cache_dirs.append(os.path.abspath(dir_path))
    
    return cache_dirs

def check_json_file_integrity(file_path):
    """检查JSON文件完整性"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, UnicodeDecodeError, FileNotFoundError):
        return False
    except Exception:
        return False

def scan_model_cache(cache_dir):
    """扫描模型缓存目录，查找损坏的文件"""
    print(f"🔍 扫描缓存目录: {cache_dir}")
    
    corrupted_models = []
    total_models = 0
    
    if not os.path.exists(cache_dir):
        print(f"   ⚠️ 目录不存在: {cache_dir}")
        return corrupted_models
    
    for item in os.listdir(cache_dir):
        item_path = os.path.join(cache_dir, item)
        
        if os.path.isdir(item_path):
            total_models += 1
            print(f"   📁 检查模型: {item}")
            
            # 检查关键文件
            critical_files = ['config.json', 'tokenizer.json', 'pytorch_model.bin']
            corrupted_files = []
            
            for file_name in critical_files:
                file_path = os.path.join(item_path, file_name)
                if os.path.exists(file_path):
                    if file_name.endswith('.json'):
                        if not check_json_file_integrity(file_path):
                            corrupted_files.append(file_name)
                            print(f"      ❌ 损坏文件: {file_name}")
                    else:
                        # 检查二进制文件大小
                        try:
                            size = os.path.getsize(file_path)
                            if size < 1024:  # 小于1KB可能是损坏的
                                corrupted_files.append(file_name)
                                print(f"      ❌ 可疑文件: {file_name} (大小: {size} bytes)")
                        except:
                            corrupted_files.append(file_name)
            
            if corrupted_files:
                corrupted_models.append({
                    'model_name': item,
                    'model_path': item_path,
                    'corrupted_files': corrupted_files
                })
                print(f"      🚨 模型损坏: {len(corrupted_files)}个文件")
            else:
                print(f"      ✅ 模型完整")
    
    print(f"   📊 扫描完成: {total_models}个模型，{len(corrupted_models)}个损坏")
    return corrupted_models

def clean_corrupted_models(corrupted_models, auto_confirm=False):
    """清理损坏的模型"""
    if not corrupted_models:
        print("✅ 没有发现损坏的模型缓存")
        return
    
    print(f"\n🧹 发现 {len(corrupted_models)} 个损坏的模型缓存:")
    
    for i, model_info in enumerate(corrupted_models, 1):
        print(f"\n{i}. 模型: {model_info['model_name']}")
        print(f"   路径: {model_info['model_path']}")
        print(f"   损坏文件: {', '.join(model_info['corrupted_files'])}")
        
        # 计算目录大小
        try:
            total_size = sum(
                os.path.getsize(os.path.join(dirpath, filename))
                for dirpath, dirnames, filenames in os.walk(model_info['model_path'])
                for filename in filenames
            )
            size_mb = total_size / (1024 * 1024)
            print(f"   大小: {size_mb:.1f} MB")
        except:
            print(f"   大小: 无法计算")
    
    if not auto_confirm:
        print(f"\n❓ 是否清理这些损坏的模型缓存？")
        print("   输入 'y' 或 'yes' 确认清理")
        print("   输入 'n' 或 'no' 取消操作")
        
        choice = input("请选择: ").lower().strip()
        if choice not in ['y', 'yes', '是', '确认']:
            print("❌ 操作已取消")
            return
    
    # 执行清理
    cleaned_count = 0
    total_size_freed = 0
    
    for model_info in corrupted_models:
        try:
            # 计算释放的空间
            try:
                model_size = sum(
                    os.path.getsize(os.path.join(dirpath, filename))
                    for dirpath, dirnames, filenames in os.walk(model_info['model_path'])
                    for filename in filenames
                )
                total_size_freed += model_size
            except:
                pass
            
            # 删除模型目录
            shutil.rmtree(model_info['model_path'])
            print(f"   ✅ 已清理: {model_info['model_name']}")
            cleaned_count += 1
            
        except Exception as e:
            print(f"   ❌ 清理失败: {model_info['model_name']} - {e}")
    
    size_freed_mb = total_size_freed / (1024 * 1024)
    print(f"\n🎉 清理完成!")
    print(f"   清理模型数: {cleaned_count}/{len(corrupted_models)}")
    print(f"   释放空间: {size_freed_mb:.1f} MB")

def backup_model_list(cache_dirs):
    """备份模型列表"""
    try:
        backup_file = f"model_cache_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(f"TradingAgents 模型缓存备份\n")
            f.write(f"备份时间: {datetime.now()}\n")
            f.write("=" * 50 + "\n\n")
            
            for cache_dir in cache_dirs:
                f.write(f"缓存目录: {cache_dir}\n")
                if os.path.exists(cache_dir):
                    for item in os.listdir(cache_dir):
                        item_path = os.path.join(cache_dir, item)
                        if os.path.isdir(item_path):
                            try:
                                size = sum(
                                    os.path.getsize(os.path.join(dirpath, filename))
                                    for dirpath, dirnames, filenames in os.walk(item_path)
                                    for filename in filenames
                                )
                                size_mb = size / (1024 * 1024)
                                f.write(f"  - {item} ({size_mb:.1f} MB)\n")
                            except:
                                f.write(f"  - {item} (大小未知)\n")
                f.write("\n")
        
        print(f"📋 模型列表已备份到: {backup_file}")
        return backup_file
        
    except Exception as e:
        print(f"⚠️ 备份失败: {e}")
        return None

def main():
    """主函数"""
    print("=" * 60)
    print("🧹 TradingAgents 模型缓存清理工具")
    print("=" * 60)
    print(f"🕒 运行时间: {datetime.now()}")
    print()
    
    # 查找缓存目录
    print("🔍 查找模型缓存目录...")
    cache_dirs = find_model_cache_directories()
    
    if not cache_dirs:
        print("❌ 未找到任何模型缓存目录")
        print("💡 可能的原因:")
        print("   • 还未下载过任何模型")
        print("   • 模型缓存在其他位置")
        print("   • 缓存目录已被手动删除")
        return
    
    print(f"✅ 找到 {len(cache_dirs)} 个缓存目录:")
    for cache_dir in cache_dirs:
        print(f"   📁 {cache_dir}")
    
    # 备份模型列表
    print(f"\n📋 备份当前模型列表...")
    backup_file = backup_model_list(cache_dirs)
    
    # 扫描损坏的模型
    print(f"\n🔍 扫描损坏的模型缓存...")
    all_corrupted_models = []
    
    for cache_dir in cache_dirs:
        corrupted_models = scan_model_cache(cache_dir)
        all_corrupted_models.extend(corrupted_models)
    
    # 清理损坏的模型
    if all_corrupted_models:
        clean_corrupted_models(all_corrupted_models)
    else:
        print("✅ 所有模型缓存都完整，无需清理")
    
    print(f"\n💡 使用建议:")
    print("   • 定期运行此工具清理损坏缓存")
    print("   • 确保网络连接稳定时下载模型")
    print("   • 如果经常出现损坏，考虑更换缓存目录")
    print("   • 备份文件可用于恢复模型列表")
    
    if backup_file:
        print(f"   • 备份文件: {backup_file}")

if __name__ == "__main__":
    # 检查命令行参数
    auto_confirm = "--auto" in sys.argv or "-y" in sys.argv
    
    if auto_confirm:
        print("🤖 自动模式：将自动清理损坏的缓存")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 操作被用户中断")
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()
