"""
修复Gradio兼容性问题的脚本
"""

import re

def fix_gradio_update_syntax(file_path):
    """修复文件中的Gradio update语法"""
    
    print(f"🔧 修复文件: {file_path}")
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 记录原始内容长度
    original_length = len(content)
    
    # 查找所有可能的问题模式
    patterns_to_fix = [
        # gr.Dropdown.update(choices=xxx)
        (r'gr\.Dropdown\.update\(choices=([^)]+)\)', r'\1'),
        # gr.Dropdown.update(choices=xxx, value=yyy)
        (r'gr\.Dropdown\.update\(choices=([^,]+),\s*value=[^)]+\)', r'\1'),
        # 其他可能的update模式
        (r'gr\.Dropdown\.update\([^)]*choices=([^,)]+)[^)]*\)', r'\1'),
    ]
    
    fixes_made = 0
    
    for pattern, replacement in patterns_to_fix:
        matches = re.findall(pattern, content)
        if matches:
            print(f"  🔍 找到 {len(matches)} 个匹配: {pattern}")
            content = re.sub(pattern, replacement, content)
            fixes_made += len(matches)
    
    # 检查是否还有其他update调用
    remaining_updates = re.findall(r'gr\.\w+\.update\([^)]*\)', content)
    if remaining_updates:
        print(f"  ⚠️  还有其他update调用需要手动检查:")
        for update in remaining_updates[:5]:  # 只显示前5个
            print(f"    - {update}")
    
    # 写回文件
    if fixes_made > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ 修复了 {fixes_made} 个问题")
    else:
        print(f"  ℹ️  没有发现需要修复的问题")
    
    return fixes_made

def check_file_for_issues(file_path):
    """检查文件中的潜在问题"""
    
    print(f"🔍 检查文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    issues = []
    
    for i, line in enumerate(lines, 1):
        # 检查是否有update调用
        if 'update(' in line and 'gr.' in line:
            issues.append((i, line.strip()))
    
    if issues:
        print(f"  ⚠️  发现 {len(issues)} 个潜在问题:")
        for line_num, line_content in issues:
            print(f"    行 {line_num}: {line_content}")
    else:
        print(f"  ✅ 没有发现问题")
    
    return issues

if __name__ == "__main__":
    file_to_fix = "app_enhanced.py"
    
    print("🚀 Gradio兼容性修复工具")
    print("="*50)
    
    # 首先检查问题
    issues = check_file_for_issues(file_to_fix)
    
    if issues:
        print(f"\n🔧 开始修复...")
        fixes = fix_gradio_update_syntax(file_to_fix)
        
        print(f"\n📊 修复结果:")
        print(f"  - 发现问题: {len(issues)} 个")
        print(f"  - 修复问题: {fixes} 个")
        
        if fixes > 0:
            print(f"\n✅ 修复完成！请重新运行程序测试。")
        else:
            print(f"\n❌ 没有进行任何修复，可能需要手动检查。")
    else:
        print(f"\n✅ 文件没有发现兼容性问题！")
    
    print("\n" + "="*50)
    print("🎯 修复说明:")
    print("- 将 gr.Dropdown.update(choices=xxx) 替换为直接返回 xxx")
    print("- 新版本Gradio不再支持 .update() 方法")
    print("- 直接返回新的选择列表即可更新组件")
