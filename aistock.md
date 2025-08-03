## 项目概述

Multi-AI-Cooperative-Stock-Analysis 是一个基于多智能体大语言模型的金融交易框架，模拟真实交易公司的运作模式。通过部署专业化的LLM驱动的智能体（从基本面分析师、情感专家、技术分析师到交易员、风险管理团队），平台协作评估市场条件并做出交易决策。

## 项目架构

### 1. 核心架构组件

```

```

### 2. 智能体团队架构

#### 2.1 分析师团队 (Analyst Team)
- **市场分析师** (Market Analyst): 技术指标分析，价格走势预测
- **情感分析师** (Social Media Analyst): 社交媒体情感分析
- **新闻分析师** (News Analyst): 全球新闻和宏观经济指标监控
- **基本面分析师** (Fundamentals Analyst): 公司财务和业绩指标评估

#### 2.2 研究团队 (Research Team)
- **多头研究员** (Bull Researcher): 看涨观点和机会识别
- **空头研究员** (Bear Researcher): 看跌风险和威胁评估
- **研究经理** (Research Manager): 协调辩论，做出投资建议

#### 2.3 交易团队 (Trading Team)
- **交易员** (Trader): 基于分析制定交易计划

#### 2.4 风险管理团队 (Risk Management Team)
- **激进分析师** (Risky Debator): 高风险高回报策略倡导
- **保守分析师** (Conservative Debator): 风险控制和稳健策略
- **中性分析师** (Neutral Debator): 平衡观点和中庸策略

#### 2.5 投资组合管理 (Portfolio Management)
- **风险经理** (Risk Manager): 最终决策和风险评估

## 大模型使用分析

### 1. 大模型配置

#### 1.1 支持的大模型提供商
- **阿里云百炼**: qwen系列模型
- **DEEPSEEK**: DEEPSEEK系列模型
- **Google**: Gemini 2.0 Flash, Gemini 2.5 Flash, Gemini 2.5 Pro等
- **MOONSHOT**: KIMI K2等开源模型
- **Ollama**: 本地部署模型(llama3.1, qwen3等)

#### 1.2 双层思维模型架构
- **深度思考模型** (deep_think_llm): 用于复杂推理和决策
- **快速思考模型** (quick_think_llm): 用于快速响应和简单任务

### 2. 大模型调用位置和作用

#### 2.1 核心图结构 (tradingagents/graph/trading_graph.py)
**位置**: 第61-71行
**作用**: 
- 初始化深度思考和快速思考LLM
- 根据配置选择不同的模型提供商
- 为整个框架提供LLM服务

**代码示例**:
```python
if self.config["llm_provider"].lower() == "openai":
    self.deep_thinking_llm = ChatOpenAI(model=self.config["deep_think_llm"])
    self.quick_thinking_llm = ChatOpenAI(model=self.config["quick_think_llm"])
```

#### 2.2 分析师智能体

**2.2.1 市场分析师** (tradingagents/agents/analysts/market_analyst.py)
- **LLM作用**: 分析技术指标，生成市场报告
- **调用方式**: `chain = prompt | llm.bind_tools(tools)`(这里改成**gradio**架构)
- **输出**: 市场分析报告

**2.2.2 情感分析师** (tradingagents/agents/analysts/social_media_analyst.py)
- **LLM作用**: 分析社交媒体情感，评估市场情绪
- **调用方式**: `result = chain.invoke(state["messages"])`(这里改成gradio架构)
- **输出**: 情感分析报告

**2.2.3 新闻分析师** (tradingagents/agents/analysts/news_analyst.py)
- **LLM作用**: 分析全球新闻和宏观经济事件影响
- **调用方式**: `result = chain.invoke(state["messages"])`(这里改成gradio架构)
- **输出**: 新闻分析报告

**2.2.4 基本面分析师** (tradingagents/agents/analysts/fundamentals_analyst.py)
- **LLM作用**: 分析公司财务数据和基本面指标
- **调用方式**: `result = chain.invoke(state["messages"])`(这里改成gradio架构)
- **输出**: 基本面分析报告

#### 2.3 研究团队智能体

**2.3.1 多头研究员** (tradingagents/agents/researchers/bull_researcher.py)
- **LLM作用**: 提供看涨论据，参与投资辩论
- **调用方式**: `response = llm.invoke(prompt)`(这里改成gradio架构)
- **特色**: 集成记忆系统，从过往经验学习

**2.3.2 空头研究员** (tradingagents/agents/researchers/bear_researcher.py)
- **LLM作用**: 提供看跌论据，识别投资风险
- **调用方式**: `response = llm.invoke(prompt)`(这里改成gradio架构)
- **特色**: 集成记忆系统，风险识别能力

**2.3.3 研究经理** (tradingagents/agents/managers/research_manager.py)
- **LLM作用**: 协调多空辩论，做出最终投资建议
- **调用方式**: `response = llm.invoke(prompt)`(这里改成gradio架构)
- **输出**: 综合投资计划

#### 2.4 交易智能体

**交易员** (tradingagents/agents/trader/trader.py)
- **LLM作用**: 基于研究团队建议制定具体交易策略
- **调用方式**: `result = llm.invoke(messages)`(这里改成gradio架构)
- **特色**: 利用历史交易记忆优化决策
- **输出**: 交易投资计划

#### 2.5 风险管理智能体

**2.5.1 激进分析师** (tradingagents/agents/risk_mgmt/aggresive_debator.py)
- **LLM作用**: 倡导高风险高回报策略
- **调用方式**: `response = llm.invoke(prompt)`(这里改成gradio架构)

**2.5.2 保守分析师** (tradingagents/agents/risk_mgmt/conservative_debator.py)
- **LLM作用**: 强调风险控制和稳健策略
- **调用方式**: `response = llm.invoke(prompt)`(这里改成gradio架构)

**2.5.3 中性分析师** (tradingagents/agents/risk_mgmt/neutral_debator.py)
- **LLM作用**: 提供平衡观点和中庸策略
- **调用方式**: `response = llm.invoke(prompt)`(这里改成gradio架构)

**2.5.4 风险经理** (tradingagents/agents/managers/risk_manager.py)
- **LLM作用**: 评估风险辩论，做出最终交易决策
- **调用方式**: `response = llm.invoke(prompt)`(这里改成gradio架构)
- **输出**: 最终交易决策 (BUY/SELL/HOLD)

#### 2.6 辅助功能中的LLM使用

**2.6.1 信号处理** (tradingagents/graph/signal_processing.py)
- **LLM作用**: 从复杂交易信号中提取核心决策
- **调用方式**: `self.quick_thinking_llm.invoke(messages).content`(这里改成gradio架构)
- **输出**: 简化的交易决策 (BUY/SELL/HOLD)

**2.6.2 反思机制** (tradingagents/graph/reflection.py)
- **LLM作用**: 基于交易结果反思和学习
- **调用方式**: `self.quick_thinking_llm.invoke(messages).content`(这里改成gradio架构)
- **输出**: 经验总结和改进建议

#### 2.7 在线数据获取中的LLM使用

**数据接口** (tradingagents/dataflows/interface.py)
- **get_stock_news_openai**: 使用LLM搜索股票相关社交媒体信息
- **get_global_news_openai**: 使用LLM搜索全球宏观经济新闻
- **get_fundamentals_openai**: 使用LLM搜索公司基本面信息
- **调用方式**: `client.responses.create(model=config["quick_think_llm"])`

### 3. 记忆系统

**记忆管理** (tradingagents/agents/utils/memory.py)
- **作用**: 存储和检索历史交易经验
- **技术**: 使用千问嵌入模型和ChromaDB向量数据库，本地数据库
- **功能**: 为各智能体提供历史经验参考

## 程序运行流程

### 1. 初始化阶段
1. 加载配置文件 (default_config.py)
2. 初始化LLM模型 (深度思考 + 快速思考)
3. 创建智能体工具包 (Toolkit)
4. 初始化记忆系统
5. 构建gradio工作流图

### 2. 数据收集阶段（建立本地数据库，依据查询股票增量更新）
1. **市场分析师**: 获取技术指标数据 (akshare接口)
2. **情感分析师**: 收集社交媒体情感数据 (akshare接口)
3. **新闻分析师**: 获取新闻和宏观经济数据 (akshare接口)
4. **基本面分析师**: 收集财务数据 (aishare接口)

### 3. 分析和辩论阶段
1. **研究团队辩论**: 多头vs空头研究员进行结构化辩论
2. **研究经理决策**: 基于辩论结果制定投资计划
3. **交易员规划**: 将投资计划转化为具体交易策略

### 4. 风险评估阶段
1. **风险团队辩论**: 激进、保守、中性分析师评估交易风险
2. **风险经理决策**: 综合风险评估，做出最终交易决策

### 5. 输出和学习阶段
1. 生成最终交易决策 (BUY/SELL/HOLD)
2. 记录决策过程和理由
3. 基于交易结果进行反思和学习
4. 更新各智能体的记忆系统

## 数据源和工具

### 在线数据源
- **akshare**: 股价数据
- **FinnHub**: 新闻、内部交易数据
- **LLM模型获取的**: 当前股票的全球新闻
- **LLM模型获取的**: 社交媒体情感
- **LLM模型获取的**: 实时信息检索

### 离线数据源
- **缓存数据**: 本地存储的历史数据
- **SimFin**: 财务报表数据
- **StockStats**: 技术指标计算

### 技术栈
- **gradio**: 工作流编排
- **gradio**: LLM集成框架
- **ChromaDB**: 向量数据库
- **Rich**: CLI界面美化
- **Pandas**: 数据处理

## 配置和部署

### 环境要求
- Python 3.13+
- OpenAI API Key (或其他LLM提供商API)
- FinnHub API Key

### 运行方式
1. 
2. **编程模式**: 
3. **调试模式**: 支持详细的执行跟踪

## 大模型使用统计

### 1. LLM调用总览

| 智能体类型 | 智能体数量 | LLM调用次数 | 主要模型类型 | 调用目的 |
|-----------|-----------|------------|-------------|----------|
| 分析师团队 | 4个 | 4-8次 | quick_think_llm | 数据分析和报告生成 |
| 研究团队 | 3个 | 3-6次 | deep_think_llm | 投资辩论和决策 |
| 交易团队 | 1个 | 1次 | deep_think_llm | 交易策略制定 |
| 风险管理团队 | 4个 | 4-8次 | deep_think_llm | 风险评估和最终决策 |
| 辅助功能 | 3个 | 1-3次 | quick_think_llm | 信号处理和反思 |
| 在线数据获取 | 3个 | 0-3次 | quick_think_llm | 实时数据搜索 |

**总计**: 约15-29次LLM调用（取决于辩论轮数和在线工具使用）

### 2. 详细LLM使用映射

#### 2.1 核心智能体LLM使用
```
Multi-AI-Cooperative-Stock-Analysis (主控制器)
├── deep_thinking_llm (复杂推理)
│   ├── Bull Researcher (多头研究员)
│   ├── Bear Researcher (空头研究员)
│   ├── Research Manager (研究经理)
│   ├── Trader (交易员)
│   ├── Risky Debator (激进分析师)
│   ├── Conservative Debator (保守分析师)
│   ├── Neutral Debator (中性分析师)
│   └── Risk Manager (风险经理)
│
└── quick_thinking_llm (快速响应)
    ├── Market Analyst (市场分析师)
    ├── Social Media Analyst (情感分析师)
    ├── News Analyst (新闻分析师)
    ├── Fundamentals Analyst (基本面分析师)
    ├── Signal Processor (信号处理器)
    ├── Reflector (反思机制)
    └── Online Data Tools (在线数据工具)
```

#### 2.2 LLM调用模式分析

**高频调用场景**:
- 辩论轮次: 每轮辩论涉及2-3个智能体，可配置1-10轮
- 数据分析: 每个分析师至少1次LLM调用
- 决策制定: 每个决策节点1次LLM调用

**调用优化策略**:
- 使用快速模型处理简单任务
- 使用深度模型处理复杂推理
- 支持本地模型降低成本
- 缓存机制减少重复调用

### 3. 成本估算

基于默认配置 (deepseek + qwen-max):
- 单次完整分析: 约15-25次LLM调用
- 预估成本:
- 日均分析成本: 

## 项目特色和创新点

### 1. 多智能体协作架构
- **专业化分工**: 每个智能体专注特定领域
- **结构化辩论**: 多空观点充分交锋
- **层次化决策**: 从分析到决策的完整链条

### 2. 记忆和学习机制
- **经验积累**: 基于历史交易结果学习
- **错误纠正**: 反思机制持续改进
- **知识传承**: 向量数据库存储经验

### 3. 灵活的模型配置
- **多提供商支持**: DEEPSEEK、qen-max、Google、moonshot等可以自主添加
- **双层思维**: 快速响应 + 深度思考
- **本地部署**: 支持Ollama本地模型

### 4. 丰富的数据源
- **实时数据**: 在线API获取最新信息
- **历史数据**: 缓存数据支持回测
- **多维分析**: 技术、基本面、情感、新闻

## 使用

### 1. 模型选择
- **测试环境**: 使用qen3、kimi k2、deepseek降低成本
- **生产环境**: 使用qen3-max或其他可选模型提高质量
- **本地部署**: 使用Ollama + Llama3.1+qwen3:0.6b节省成本

### 2. 配置优化
- **辩论轮数**: 1-2轮适合快速决策，3-5轮适合深度分析
- **在线工具**: 实验时开启，回测时关闭
- **记忆系统**: 长期使用后效果更佳

### 3. 风险提示
- **仅供研究**: 不构成投资建议
- **模型依赖**: 决策质量受LLM能力限制
- **数据质量**: 依赖外部数据源的准确性

### 最终的左侧控制台结构

  

```

🎛️ 系统控制台

├── 📊 数据源管理 (只保留有用的API配置)

│   ├── 📡 AkShare (7个API接口)

│   │   ├── ✅ 启用 AkShare

│   │   └── 可用API接口:

│   │       • stock_basic: stock_info_a_code_name

│   │       • stock_daily: stock_zh_a_hist

│   │       • stock_indicators: stock_zh_a_hist_min_em

│   │       • stock_hot: stock_hot_rank_wc

│   │       • stock_sentiment: stock_comment_em

│   │       • stock_news: stock_news_em

│   │       • stock_financial: stock_financial_em

│   ├── 📡 Yahoo Finance (2个API接口)

│   │   ├── ⚠️ Yahoo Finance 已禁用

│   │   └── 可用API接口:

│   │       • stock_daily: download

│   │       • stock_info: info

│   └── 🌐 网络请求控制

│       ├── 请求超时: 5秒

│       └── 最大重试次数: 2次

├── 👥 分析师团队 (已补充完整)

│   ├── **请选择您的分析师团队（可多选）：**

│   ├── ☑ 市场分析师（技术指标）

│   ├── ☐ 社交媒体分析师（情感分析）

│   ├── ☐ 新闻分析师（宏观事件）

│   ├── ☐ 基本面分析师（财务数据）

│   ├── ---

│   ├── ✅ 已选择 X 个分析师团队

│   ├── • 选中的分析师列表

│   └── ---

└── 🔍 研究深度 (已补充完整)

    ├── **选择研究深度：**

    ├── [Radio按钮选择界面]

    ├──

    ├── ● 浅层 - 快速响应（1轮辩论）

    ├── ○ 中等 - 平衡分析（3轮辩论）

    ├── ○ 全面 - 深度研究（5轮辩论+策略回溯）

    ├── ---

    └── 📊 配置详情显示

        ├── 辩论轮数: 1/3/5

        ├── 最大Token: 500/1000/2000

        └── 策略回溯: ❌/❌/✅

```

