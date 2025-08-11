#!/bin/bash

# TradingAgents 安全推送脚本
# 确保不会推送敏感信息到仓库

echo "🔐 TradingAgents 安全推送脚本"
echo "================================"

# 检查是否在正确的目录
if [ ! -f "final_ui.py" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查敏感文件是否存在
echo "🔍 检查敏感文件..."

SENSITIVE_FILES=(
    "config/llm_config.json"
    "config/agent_model_config.json"
    ".env"
    "*.log"
    "data/trading_data.db"
)

FOUND_SENSITIVE=false

for pattern in "${SENSITIVE_FILES[@]}"; do
    if ls $pattern 1> /dev/null 2>&1; then
        echo "⚠️  发现敏感文件: $pattern"
        FOUND_SENSITIVE=true
    fi
done

if [ "$FOUND_SENSITIVE" = true ]; then
    echo ""
    echo "❌ 发现敏感文件！"
    echo "请确保以下文件已添加到 .gitignore 或已删除:"
    for pattern in "${SENSITIVE_FILES[@]}"; do
        if ls $pattern 1> /dev/null 2>&1; then
            echo "   - $pattern"
        fi
    done
    echo ""
    echo "建议操作:"
    echo "1. 检查 .gitignore 文件"
    echo "2. 删除或移动敏感文件"
    echo "3. 重新运行此脚本"
    exit 1
fi

echo "✅ 未发现敏感文件"

# 检查配置模板是否存在
echo ""
echo "🔍 检查配置模板..."

REQUIRED_TEMPLATES=(
    "config/llm_config.template.json"
    "config/agent_model_config.template.json"
    "config/README.md"
)

for template in "${REQUIRED_TEMPLATES[@]}"; do
    if [ ! -f "$template" ]; then
        echo "❌ 缺少配置模板: $template"
        exit 1
    fi
done

echo "✅ 配置模板完整"

# 检查 .gitignore 文件
echo ""
echo "🔍 检查 .gitignore 文件..."

if [ ! -f ".gitignore" ]; then
    echo "❌ 缺少 .gitignore 文件"
    exit 1
fi

# 检查关键忽略规则
REQUIRED_IGNORES=(
    "config/llm_config.json"
    "config/agent_model_config.json"
    "*.log"
    "*.db"
    ".env"
)

for ignore_rule in "${REQUIRED_IGNORES[@]}"; do
    if ! grep -q "$ignore_rule" .gitignore; then
        echo "⚠️  .gitignore 中缺少规则: $ignore_rule"
    fi
done

echo "✅ .gitignore 文件检查完成"

# 显示将要提交的文件
echo ""
echo "📋 将要提交的文件:"
git status --porcelain

echo ""
echo "🔍 检查暂存区..."
git diff --cached --name-only

# 确认推送
echo ""
read -p "🚀 确认推送到远程仓库? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 推送已取消"
    exit 1
fi

# 执行Git操作
echo ""
echo "📦 准备推送..."

# 添加所有文件（.gitignore会自动排除敏感文件）
git add .

# 提交
echo ""
echo "💾 提交更改..."
git commit -m "🚀 TradingAgents v2.0 发布版本

✨ 新增功能:
- 动态LLM配置管理
- 智能体模型选择系统  
- 增强报告生成 (多模板支持)
- 智能文档精简系统
- 完整的配置安全机制

🔒 安全更新:
- 移除所有敏感配置信息
- 添加配置模板和设置指南
- 完善 .gitignore 规则

📚 文档更新:
- 更新 README.md
- 添加用户使用指南
- 添加技术架构文档
- 添加启动指南

🧹 项目清理:
- 删除100+个无用文件
- 优化项目结构
- 准备发布版本

向后兼容: 完全兼容 v1.0
启动方式: python final_ui.py"

# 推送到远程仓库
echo ""
echo "🌐 推送到远程仓库..."

# 检查是否有远程仓库
if git remote | grep -q origin; then
    git push origin main
    echo "✅ 推送完成!"
else
    echo "⚠️  未找到远程仓库 'origin'"
    echo "请先添加远程仓库:"
    echo "git remote add origin <your-repository-url>"
    echo "然后运行: git push -u origin main"
fi

echo ""
echo "🎉 安全推送完成!"
echo ""
echo "📋 后续步骤:"
echo "1. 在新环境中克隆仓库"
echo "2. 复制配置模板: cp config/*.template.json config/"
echo "3. 编辑配置文件并填入API密钥"
echo "4. 启动系统: python final_ui.py"
echo ""
echo "📖 详细说明请查看: config/README.md"
