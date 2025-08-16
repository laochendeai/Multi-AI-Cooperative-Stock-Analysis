#!/usr/bin/env python3
"""
修复app_enhanced.py中的模型配置解析问题
将所有 model_config.split(":", 1) 替换为 self._parse_model_config(model_config)
"""

import re

def fix_model_config_parsing():
    """修复模型配置解析"""
    
    # 读取文件
    with open('app_enhanced.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有需要替换的模式
    patterns = [
        # 匹配 provider, model = model_config.split(":", 1)
        (r'(\s+)provider, model = model_config\.split\(":", 1\)', r'\1provider, model = self._parse_model_config(model_config)'),
        # 匹配 provider, model_name = model.split(":", 1)
        (r'(\s+)provider, model_name = model\.split\(":", 1\)', r'\1provider, model_name = self._parse_model_config(model)'),
    ]
    
    # 执行替换
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # 写回文件
    with open('app_enhanced.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 模型配置解析修复完成")

if __name__ == "__main__":
    fix_model_config_parsing()
