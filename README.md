# 🤖 TradingAgents - 多智能体协作股票分析系统

基于15个专业AI智能体协作的股票分析系统，提供全面、专业的投资分析服务。

## ✨ 核心特性

- 🤖 **15个专业智能体**: 分析师、研究员、风险管理、交易员团队协作
- 🔧 **灵活LLM配置**: 支持OpenAI、DeepSeek、Google、Moonshot、阿里百炼等多个提供商
- 📊 **智能报告生成**: 多种专业报告模板，支持Markdown格式导出
- 🧠 **智能文档精简**: 自动提取关键信息，避免信息过载
- 💾 **向量记忆系统**: 基于ChromaDB的智能记忆和上下文理解
- 🎨 **现代化界面**: 直观的Web界面，支持移动端访问

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动系统
```bash
python final_ui.py
```

### 3. 访问界面
在浏览器中打开: `http://localhost:7860`

### 4. 配置LLM
- 点击"LLM模型配置"标签页
- 输入您的API密钥
- 测试连接确保配置正确

### 5. 开始分析
- 输入股票代码（如：600519、000001）
- 选择分析深度（1-4轮）
- 点击"开始智能分析"

## 📋 系统要求

- Python 3.8+
- 4GB+ 内存
- 稳定的网络连接

## 🏗️ 智能体架构

### 📈 分析师团队
- **市场分析师**: 技术指标分析和价格走势预测
- **情感分析师**: 社交媒体情绪和市场情感分析
- **新闻分析师**: 新闻事件和宏观经济影响分析
- **基本面分析师**: 财务数据和基本面指标分析

### 🔬 研究团队
- **多头研究员**: 寻找投资机会和看涨理由
- **空头研究员**: 识别投资风险和看跌因素
- **研究经理**: 协调多空辩论并综合投资建议

### ⚠️ 风险管理团队
- **激进辩论者**: 提出大胆的投资观点
- **保守辩论者**: 强调风险控制和稳健投资
- **中性辩论者**: 提供平衡的观点和分析
- **风险经理**: 最终的风险评估和决策

### 💼 交易团队
- **交易员**: 制定具体的交易策略和执行计划

## 🔧 支持的LLM提供商

- **OpenAI**: GPT-4, GPT-3.5-turbo
- **DeepSeek**: deepseek-chat, deepseek-coder
- **Google**: Gemini Pro, Gemini Pro Vision
- **Moonshot**: Kimi K2 (moonshot-v1-8k/32k/128k)
- **阿里百炼**: 通义千问 (qwen-turbo/plus/max)
- **自定义提供商**: 支持添加其他OpenAI兼容的API

## 📊 报告模板

- **标准模板**: 完整的分析报告，适合大多数用户
- **详细模板**: 包含详细分析矩阵和图表
- **高管模板**: 简洁的决策摘要，适合高管阅读
- **技术模板**: 专注于技术分析的报告
- **研究模板**: 深度研究报告，适合专业投资者

## 📁 项目结构

```
TradingAgents/
├── final_ui.py                 # 主启动文件
├── app_tradingagents_upgraded.py  # 备用启动文件
├── app_enhanced.py             # 增强功能模块
├── core/                       # 核心功能模块
│   ├── enhanced_llm_manager.py     # LLM配置管理
│   ├── agent_model_manager.py      # 智能体模型管理
│   ├── enhanced_report_generator.py # 报告生成
│   └── intelligent_summarizer.py   # 智能文档精简
├── tradingagents/              # 智能体框架
│   ├── agents/                     # 智能体实现
│   ├── graph/                      # 工作流图
│   └── dataflows/                  # 数据流
├── config/                     # 配置文件
├── docs/                       # 文档
└── reports/                    # 报告输出
```

## 📖 使用指南

详细的使用说明请参考：
- [用户使用指南](docs/USER_GUIDE.md)
- [技术架构文档](docs/TECHNICAL_ARCHITECTURE.md)
- [启动指南](STARTUP_GUIDE.md)

## 🧪 测试

运行集成测试验证系统功能：
```bash
python test_system_integration.py
```

## ⚠️ 免责声明

本系统提供的分析结果仅供参考，不构成投资建议。投资有风险，决策需谨慎。

## 📄 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件

---

**版本**: TradingAgents v2.0
**最后更新**: 2025-08-11
