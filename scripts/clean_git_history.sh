#!/bin/bash

# Git历史清理脚本 - 移除敏感信息
# ⚠️ 警告: 此脚本会重写Git历史，请谨慎使用

echo "🧹 Git历史清理脚本"
echo "=================="
echo ""
echo "⚠️  警告: 此脚本将重写Git历史记录"
echo "这将移除所有历史提交中的敏感文件"
echo "操作不可逆，请确保已备份重要数据"
echo ""

# 确认操作
read -p "🚨 确认要清理Git历史吗? 这将删除所有历史记录! (yes/NO): " -r
echo

if [[ ! $REPLY == "yes" ]]; then
    echo "❌ 操作已取消"
    exit 1
fi

echo "🔍 检查当前仓库状态..."

# 检查是否有未提交的更改
if ! git diff-index --quiet HEAD --; then
    echo "❌ 发现未提交的更改，请先提交或暂存"
    git status
    exit 1
fi

echo "✅ 工作区干净"

# 备份当前分支
CURRENT_BRANCH=$(git branch --show-current)
echo "📦 当前分支: $CURRENT_BRANCH"

# 创建备份分支
BACKUP_BRANCH="backup-before-cleanup-$(date +%Y%m%d-%H%M%S)"
git branch $BACKUP_BRANCH
echo "✅ 已创建备份分支: $BACKUP_BRANCH"

echo ""
echo "🧹 开始清理敏感文件..."

# 定义要从历史中移除的敏感文件
SENSITIVE_FILES=(
    "config/llm_config.json"
    "config/agent_model_config.json"
    "*.log"
    "*.db"
    ".env"
    "*.env"
    "**/api_keys.json"
    "**/secrets.json"
    "**/credentials.json"
    "**/*_key.json"
    "**/*_secret.json"
    "data/trading_data.db"
    "data/memory/"
    "data/cache/"
    "logs/"
    "reports/*.json"
    "reports/*.txt"
    "trading_analysis_*.json"
    "analysis_result_*.json"
    "debug_*.json"
    "test_result_*.txt"
    "chroma_db/"
    "*.chroma"
)

# 使用git filter-branch移除敏感文件
echo "🔄 重写Git历史..."

for file_pattern in "${SENSITIVE_FILES[@]}"; do
    echo "   移除: $file_pattern"
    git filter-branch --force --index-filter \
        "git rm -rf --cached --ignore-unmatch $file_pattern" \
        --prune-empty --tag-name-filter cat -- --all
done

echo "✅ 敏感文件已从历史中移除"

# 清理引用
echo ""
echo "🧹 清理Git引用..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo "✅ Git引用已清理"

# 验证清理结果
echo ""
echo "🔍 验证清理结果..."

# 检查是否还有敏感文件在历史中
echo "检查历史中的敏感文件..."
for file_pattern in "${SENSITIVE_FILES[@]}"; do
    if git log --all --full-history -- "$file_pattern" | grep -q "commit"; then
        echo "⚠️  警告: $file_pattern 可能仍在历史中"
    fi
done

echo "✅ 历史清理验证完成"

# 显示仓库大小变化
echo ""
echo "📊 仓库大小信息:"
du -sh .git

echo ""
echo "🎉 Git历史清理完成!"
echo ""
echo "📋 重要提醒:"
echo "1. 备份分支: $BACKUP_BRANCH"
echo "2. 如需恢复，使用: git checkout $BACKUP_BRANCH"
echo "3. 强制推送到远程: git push --force-with-lease origin $CURRENT_BRANCH"
echo "4. 通知团队成员重新克隆仓库"
echo ""
echo "⚠️  注意事项:"
echo "- 所有协作者需要重新克隆仓库"
echo "- 现有的Pull Request可能需要重新创建"
echo "- 确保所有敏感信息已从新的提交中移除"
echo ""

# 询问是否立即推送
read -p "🚀 是否立即强制推送到远程仓库? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌐 强制推送到远程仓库..."
    
    # 检查远程仓库
    if git remote | grep -q origin; then
        git push --force-with-lease origin $CURRENT_BRANCH
        echo "✅ 强制推送完成"
        echo ""
        echo "🔔 请通知所有协作者:"
        echo "1. 删除本地仓库"
        echo "2. 重新克隆: git clone <repository-url>"
        echo "3. 重新配置API密钥"
    else
        echo "❌ 未找到远程仓库 'origin'"
    fi
else
    echo "⏸️  推送已跳过"
    echo "稍后可手动推送: git push --force-with-lease origin $CURRENT_BRANCH"
fi

echo ""
echo "✨ 清理脚本执行完成!"
