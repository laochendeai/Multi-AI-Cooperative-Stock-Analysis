# 🔧 TradingAgents 配置指南

## 📋 配置文件说明

本目录包含TradingAgents系统的配置文件模板。为了保护您的API密钥安全，实际的配置文件不会包含在版本控制中。

## 🚀 快速设置

### 1. 复制配置模板

```bash
# 复制LLM配置模板
cp config/llm_config.template.json config/llm_config.json

# 复制智能体配置模板
cp config/agent_model_config.template.json config/agent_model_config.json
```

### 2. 配置LLM API密钥

编辑 `config/llm_config.json` 文件，填入您的API密钥：

```json
{
  "llm_config": {
    "openai": "your-openai-api-key",
    "deepseek": "your-deepseek-api-key",
    "google": "your-google-api-key",
    "moonshot": "your-moonshot-api-key",
    "阿里百炼": "your-alibaba-api-key"
  }
}
```

### 3. 配置智能体模型

编辑 `config/agent_model_config.json` 文件，选择每个智能体使用的模型：

```json
{
  "market_analyst": "moonshot:moonshot-v1-8k",
  "sentiment_analyst": "阿里百炼:qwen-turbo",
  "news_analyst": "阿里百炼:qwen-turbo"
}
```

## 🔑 支持的LLM提供商

### OpenAI
- **模型**: GPT-4, GPT-3.5-turbo, GPT-4o
- **获取密钥**: https://platform.openai.com/api-keys
- **格式**: `sk-...`

### DeepSeek
- **模型**: deepseek-chat, deepseek-coder
- **获取密钥**: https://platform.deepseek.com/api_keys
- **格式**: `sk-...`

### Google Gemini
- **模型**: gemini-pro, gemini-pro-vision
- **获取密钥**: https://makersuite.google.com/app/apikey
- **格式**: `AIza...`

### Moonshot AI
- **模型**: moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k
- **获取密钥**: https://platform.moonshot.cn/console/api-keys
- **格式**: `sk-...`

### 阿里百炼
- **模型**: qwen-turbo, qwen-plus, qwen-max
- **获取密钥**: https://bailian.console.aliyun.com/
- **格式**: `sk-...`

## 🛡️ 安全注意事项

### ⚠️ 重要提醒
- **绝不要**将包含真实API密钥的配置文件提交到版本控制系统
- **绝不要**在公开场合分享您的API密钥
- **定期轮换**您的API密钥以确保安全

### 🔒 安全最佳实践
1. **使用环境变量**: 考虑使用环境变量存储API密钥
2. **限制权限**: 为API密钥设置最小必要权限
3. **监控使用**: 定期检查API密钥的使用情况
4. **备份配置**: 安全地备份您的配置文件

## 📁 配置文件结构

```
config/
├── README.md                          # 本文件
├── llm_config.template.json          # LLM配置模板
├── agent_model_config.template.json  # 智能体配置模板
├── llm_config.json                   # 实际LLM配置（不在版本控制中）
└── agent_model_config.json           # 实际智能体配置（不在版本控制中）
```

## 🔧 高级配置

### 自定义LLM提供商

您可以在界面中添加自定义LLM提供商，或直接编辑配置文件：

```json
{
  "llm_config": {
    "custom_provider": "your-api-key"
  },
  "custom_llm_providers": {
    "custom_provider": {
      "name": "自定义提供商",
      "base_url": "https://api.example.com/v1",
      "api_key_header": "Authorization",
      "api_key_prefix": "Bearer ",
      "models": [
        {
          "id": "custom-model",
          "name": "自定义模型",
          "type": "chat",
          "context_length": 4096
        }
      ]
    }
  }
}
```

### 智能体模型优化

根据不同任务特性选择合适的模型：

- **速度优先**: 选择 turbo 类型模型
- **质量优先**: 选择 pro/max 类型模型
- **成本优化**: 选择较小的模型
- **上下文需求**: 根据分析深度选择合适的上下文长度

## 🚨 故障排除

### 常见问题

**Q: API密钥无效**
A: 检查密钥格式是否正确，确认密钥未过期

**Q: 连接测试失败**
A: 检查网络连接，确认API服务可用

**Q: 配置文件丢失**
A: 从模板文件重新创建配置文件

**Q: 模型不兼容**
A: 使用界面中的兼容性检查功能

### 获取帮助

- 查看主文档: `README.md`
- 用户指南: `docs/USER_GUIDE.md`
- 启动指南: `STARTUP_GUIDE.md`

---

**配置完成后，使用以下命令启动系统**:
```bash
python final_ui.py
```

**访问地址**: http://localhost:7860
