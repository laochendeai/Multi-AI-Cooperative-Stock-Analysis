# 🔐 TradingAgents 安全推送指南

## 🎯 概述

本指南帮助您安全地将TradingAgents项目推送到Git仓库，确保不会泄露API密钥和其他敏感信息。

## ⚠️ 重要提醒

**绝对不要将以下文件推送到公开仓库**：
- 包含真实API密钥的配置文件
- 数据库文件
- 日志文件
- 个人分析数据
- 任何包含敏感信息的文件

## 🚀 安全推送步骤

### 方法一：使用自动化脚本（推荐）

#### Linux/macOS
```bash
# 给脚本执行权限
chmod +x scripts/safe_push.sh

# 运行安全推送脚本
./scripts/safe_push.sh
```

#### Windows
```cmd
# 运行安全推送脚本
scripts\safe_push.bat
```

### 方法二：手动检查和推送

#### 1. 检查敏感文件
```bash
# 检查是否存在敏感文件
ls config/llm_config.json 2>/dev/null && echo "⚠️ 发现敏感配置文件"
ls config/agent_model_config.json 2>/dev/null && echo "⚠️ 发现敏感配置文件"
ls .env 2>/dev/null && echo "⚠️ 发现环境变量文件"
```

#### 2. 确保配置模板存在
```bash
# 检查配置模板
ls config/llm_config.template.json
ls config/agent_model_config.template.json
ls config/README.md
```

#### 3. 验证.gitignore
```bash
# 检查.gitignore是否包含敏感文件规则
grep -E "(llm_config\.json|agent_model_config\.json|\.env|\.log|\.db)" .gitignore
```

#### 4. 查看将要提交的文件
```bash
# 查看状态
git status

# 查看将要提交的具体内容
git diff --cached
```

#### 5. 安全提交和推送
```bash
# 添加文件（.gitignore会自动排除敏感文件）
git add .

# 提交
git commit -m "🚀 TradingAgents v2.0 安全发布版本"

# 推送
git push origin main
```

## 🧹 清理Git历史（如果之前推送了敏感信息）

如果您之前不小心推送了包含敏感信息的提交，需要清理Git历史：

### ⚠️ 重要警告
- 此操作会重写Git历史，不可逆
- 所有协作者需要重新克隆仓库
- 请先备份重要数据

### 执行清理
```bash
# 给脚本执行权限
chmod +x scripts/clean_git_history.sh

# 运行历史清理脚本
./scripts/clean_git_history.sh
```

### 手动清理特定文件
```bash
# 从整个Git历史中移除特定文件
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch config/llm_config.json' \
  --prune-empty --tag-name-filter cat -- --all

# 清理引用
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 强制推送
git push --force-with-lease origin main
```

## 📋 .gitignore 配置检查清单

确保您的 `.gitignore` 文件包含以下规则：

```gitignore
# 敏感配置文件
config/llm_config.json
config/agent_model_config.json

# 环境变量
.env
.env.*
*.env

# API密钥文件
**/api_keys.json
**/secrets.json
**/credentials.json
**/*_key.json
**/*_secret.json

# 数据库文件
*.db
*.sqlite
*.sqlite3
data/trading_data.db

# 日志文件
logs/
*.log
*.log.*

# 缓存和临时文件
data/memory/
data/cache/
__pycache__/
*.pyc

# 报告文件（可能包含敏感数据）
reports/*.json
reports/*.txt

# 测试和调试文件
debug_*.json
test_result_*.txt
trading_analysis_*.json
```

## 🔧 配置文件安全管理

### 使用配置模板
1. **创建模板文件**：包含配置结构但不包含真实密钥
2. **提供设置指南**：详细说明如何配置
3. **忽略实际配置**：确保真实配置文件在 `.gitignore` 中

### 环境变量方案
```bash
# 设置环境变量
export OPENAI_API_KEY="your-openai-key"
export DEEPSEEK_API_KEY="your-deepseek-key"

# 在代码中读取
import os
api_key = os.getenv('OPENAI_API_KEY')
```

### 配置文件加密
```python
# 使用简单的base64编码（示例）
import base64

def encrypt_key(key):
    return base64.b64encode(key.encode()).decode()

def decrypt_key(encrypted_key):
    return base64.b64decode(encrypted_key.encode()).decode()
```

## 🔍 安全检查工具

### 检查敏感信息
```bash
# 搜索可能的API密钥
grep -r "sk-" . --exclude-dir=.git
grep -r "AIza" . --exclude-dir=.git

# 检查配置文件
find . -name "*.json" -exec grep -l "api_key\|secret\|password" {} \;
```

### 验证.gitignore效果
```bash
# 检查被忽略的文件
git status --ignored

# 测试特定文件是否被忽略
git check-ignore config/llm_config.json
```

## 📚 最佳实践

### 开发环境
1. **本地配置**：在本地创建配置文件，不提交到版本控制
2. **环境隔离**：开发、测试、生产环境使用不同的API密钥
3. **权限最小化**：为API密钥设置最小必要权限

### 团队协作
1. **配置文档**：提供详细的配置设置文档
2. **模板文件**：提供配置模板供团队成员使用
3. **安全培训**：确保团队成员了解安全最佳实践

### 持续安全
1. **定期审查**：定期检查仓库中是否有敏感信息
2. **密钥轮换**：定期更换API密钥
3. **监控使用**：监控API密钥的使用情况

## 🚨 应急响应

### 如果意外推送了敏感信息

#### 立即行动
1. **撤销密钥**：立即在API提供商处撤销泄露的密钥
2. **生成新密钥**：创建新的API密钥
3. **清理历史**：使用历史清理脚本移除敏感信息
4. **通知团队**：告知团队成员重新克隆仓库

#### 长期措施
1. **加强检查**：实施更严格的推送前检查
2. **自动化工具**：使用自动化工具检测敏感信息
3. **流程改进**：改进开发和部署流程

## 📞 获取帮助

### 常见问题
- **Q**: 如何知道文件是否被.gitignore忽略？
- **A**: 使用 `git check-ignore <filename>` 命令

- **Q**: 如何查看Git历史中的敏感文件？
- **A**: 使用 `git log --all --full-history -- <filename>`

- **Q**: 强制推送后团队成员应该怎么做？
- **A**: 删除本地仓库，重新克隆，重新配置API密钥

### 技术支持
- 查看项目文档：`README.md`
- 配置指南：`config/README.md`
- 用户指南：`docs/USER_GUIDE.md`

---

**记住**：安全是一个持续的过程，不是一次性的任务。始终保持警惕，定期审查和更新安全措施。

**推送前检查清单**：
- [ ] 检查敏感文件是否存在
- [ ] 验证.gitignore规则
- [ ] 确认配置模板完整
- [ ] 查看将要提交的文件
- [ ] 运行安全推送脚本
