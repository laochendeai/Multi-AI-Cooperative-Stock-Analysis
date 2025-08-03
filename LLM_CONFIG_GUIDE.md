# 🤖 TradingAgents LLM配置指南

## 📋 概述

TradingAgents增强版系统现在支持灵活的LLM配置管理，包括内置提供商和自定义提供商的添加、测试和管理。

## 🌐 访问系统

**系统地址**: http://localhost:7864

## ⚙️ LLM配置功能

### 1. **内置提供商配置**

系统预置了4个主流LLM提供商：

#### 🔥 DeepSeek
- **API密钥格式**: `sk-xxxxxxxxxxxxxxxx`
- **官网**: https://platform.deepseek.com/
- **特点**: 高性价比，中文支持优秀

#### 🧠 OpenAI
- **API密钥格式**: `sk-xxxxxxxxxxxxxxxx`
- **官网**: https://platform.openai.com/
- **特点**: 业界标杆，功能强大

#### 🌐 Google
- **API密钥格式**: `AIzaxxxxxxxxxxxxxxxx`
- **官网**: https://ai.google.dev/
- **特点**: Gemini模型，多模态支持

#### 🌙 Moonshot
- **API密钥格式**: `sk-xxxxxxxxxxxxxxxx`
- **官网**: https://platform.moonshot.cn/
- **特点**: 国产优秀模型，长文本处理

### 2. **自定义提供商添加** ⭐

现在您可以添加任何自定义的LLM提供商！

#### 📝 添加步骤

1. **访问"⚙️ LLM配置"标签页**
2. **点击"⚙️ 自定义提供商"子标签**
3. **填写提供商信息**：
   - **提供商名称**: 为您的LLM起一个名称（如：Claude、通义千问、文心一言）
   - **API密钥**: 您的LLM服务API密钥
   - **API基础URL** (可选): 自部署或特殊端点的完整URL
   - **模型名称** (可选): 指定要使用的具体模型

4. **点击"➕ 添加提供商"**
5. **点击"🔍 测试连接"验证配置**

#### 🎯 支持的自定义提供商示例

**Claude (Anthropic)**:
```
提供商名称: Claude
API密钥: sk-ant-xxxxxxxxxxxxxxxx
API基础URL: https://api.anthropic.com/v1
模型名称: claude-3-sonnet-20240229
```

**通义千问 (阿里云)**:
```
提供商名称: 通义千问
API密钥: sk-xxxxxxxxxxxxxxxx
API基础URL: https://dashscope.aliyuncs.com/api/v1
模型名称: qwen-turbo
```

**文心一言 (百度)**:
```
提供商名称: 文心一言
API密钥: your-access-token
API基础URL: https://aip.baidubce.com/rpc/2.0
模型名称: ernie-bot-turbo
```

**本地部署模型**:
```
提供商名称: 本地Llama
API密钥: local-key
API基础URL: http://localhost:8000/v1
模型名称: llama-2-7b-chat
```

### 3. **提供商管理**

#### 📊 查看已配置提供商
- 在"已配置的提供商"表格中查看所有提供商状态
- 显示提供商类型（内置/自定义）和配置状态

#### 🗑️ 删除自定义提供商
1. 在下拉列表中选择要删除的自定义提供商
2. 点击"🗑️ 删除"按钮
3. 确认删除操作

#### 🔄 刷新提供商列表
- 点击"🔄 刷新列表"更新提供商状态

## 🔧 环境变量配置

### 创建 .env 文件

在项目根目录创建 `.env` 文件：

```bash
# DeepSeek
DEEPSEEK_API_KEY=sk-your-deepseek-key

# OpenAI
OPENAI_API_KEY=sk-your-openai-key

# Google
GOOGLE_API_KEY=AIza-your-google-key

# Moonshot
MOONSHOT_API_KEY=sk-your-moonshot-key

# 自定义提供商也可以通过环境变量配置
CUSTOM_LLM_API_KEY=your-custom-key
```

### 环境变量优先级

1. **界面配置** > **环境变量**
2. 系统启动时自动加载环境变量中的API密钥
3. 界面中的配置会覆盖环境变量

## 🧪 连接测试

### 测试功能
- 每个提供商都有独立的"测试连接"按钮
- 测试会验证API密钥格式和连通性
- 显示详细的测试结果和错误信息

### 测试结果说明
- ✅ **连接成功**: API密钥有效，可以正常使用
- ❌ **连接失败**: 检查API密钥格式或网络连接
- ⚠️ **格式错误**: API密钥格式不正确

## 📊 系统信息

### ChromaDB状态
- ✅ **已安装**: 向量记忆系统可用
- ❌ **未安装**: 需要安装ChromaDB

### 系统配置监控
- 已配置提供商数量
- 自定义提供商数量
- 分析历史记录数量
- 系统运行状态

## 🚀 使用流程

### 完整使用流程

1. **配置LLM提供商**
   - 添加内置或自定义提供商
   - 测试连接确保可用

2. **进行股票分析**
   - 切换到"📊 股票分析"标签页
   - 输入股票代码（如：600519）
   - 选择分析深度和智能体团队
   - ✅ **勾选"使用真实LLM"**（重要！）
   - 点击"🚀 开始全面分析"

3. **查看分析结果**
   - 在多个标签页查看详细分析
   - 对比不同智能体的观点
   - 获取最终投资建议

4. **管理分析历史**
   - 在"📚 分析历史"查看历史记录
   - 跟踪分析效果和决策质量

## ⚠️ 注意事项

### API密钥安全
- 🔒 API密钥在界面中加密显示
- 🚫 不要在公共场所暴露API密钥
- 🔄 定期更换API密钥确保安全

### 使用限制
- 📊 不同提供商有不同的调用限制
- 💰 注意API调用费用
- ⏱️ 深度分析需要更多时间和调用次数

### 最佳实践
- 🧪 添加新提供商后先测试连接
- 📈 根据分析需求选择合适的模型
- 💾 定期备份重要的分析结果
- 🔍 对比不同LLM的分析质量

## 🆘 故障排除

### 常见问题

**Q: API密钥测试失败？**
A: 检查密钥格式、网络连接和账户余额

**Q: 自定义提供商无法添加？**
A: 确保名称唯一且API密钥格式正确

**Q: ChromaDB不可用？**
A: 运行 `pip install chromadb sentence-transformers`

**Q: 分析结果为空？**
A: 确保勾选"使用真实LLM"且API密钥有效

### 技术支持
- 📖 查看详细文档：`README_TRADINGAGENTS.md`
- 🔧 运行系统测试：`python test_basic.py`
- 📊 查看系统状态：访问"📊 系统信息"标签页

---

**🎉 现在您可以灵活配置任何LLM提供商，享受真正的多智能体协作分析！**

*TradingAgents Enhanced v1.0 | 支持无限扩展的LLM生态系统*
