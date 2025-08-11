#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强报告生成器 - 支持多种Markdown模板和格式化选项
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class EnhancedReportGenerator:
    """增强的报告生成器"""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        
        # 内置模板
        self.built_in_templates = {
            "standard": self._get_standard_template(),
            "detailed": self._get_detailed_template(),
            "executive": self._get_executive_template(),
            "technical": self._get_technical_template(),
            "research": self._get_research_template()
        }
        
        # 加载自定义模板
        self.custom_templates = self._load_custom_templates()
    
    def _get_standard_template(self) -> str:
        """标准模板"""
        return """# 📊 {stock_name} ({symbol}) 投资分析报告

## 📋 基本信息
- **股票代码**: {symbol}
- **股票名称**: {stock_name}
- **分析时间**: {analysis_time}
- **分析深度**: {analysis_depth}
- **报告生成**: TradingAgents 多智能体协作系统

---

## 🎯 投资建议摘要

{executive_summary}

---

## 📈 综合分析

{comprehensive_report}

---

## 📊 专业分析团队报告

### 📈 市场技术分析
{market_analysis}

### 💭 市场情感分析  
{sentiment_analysis}

### 📰 新闻事件分析
{news_analysis}

### 📊 基本面分析
{fundamentals_analysis}

---

## 🔬 多空辩论

### 🐂 多头观点
{bull_arguments}

### 🐻 空头观点
{bear_arguments}

### 👨‍💼 研究经理综合意见
{investment_recommendation}

---

## 💼 交易策略建议

{trading_strategy}

---

## ⚠️ 风险评估

{risk_assessment}

---

## 🎯 最终投资决策

{final_decision}

---

## 📈 分析统计

- **参与智能体**: {agent_count} 个专业智能体
- **分析轮次**: {analysis_rounds} 轮
- **数据来源**: {data_sources}
- **置信度**: {confidence_level}

---

*本报告由TradingAgents多智能体系统生成，仅供参考，不构成投资建议。投资有风险，入市需谨慎。*

**免责声明**: 本分析报告基于公开信息和AI模型分析，不保证信息的准确性和完整性。投资者应当根据自身情况做出独立判断。
"""
    
    def _get_detailed_template(self) -> str:
        """详细模板"""
        return """# 📊 {stock_name} ({symbol}) 详细投资分析报告

<div align="center">

**TradingAgents 多智能体协作分析系统**

*专业 • 全面 • 智能*

</div>

---

## 📋 报告概览

| 项目 | 详情 |
|------|------|
| 股票代码 | {symbol} |
| 股票名称 | {stock_name} |
| 分析时间 | {analysis_time} |
| 分析深度 | {analysis_depth} |
| 参与智能体 | {agent_count} 个 |
| 分析轮次 | {analysis_rounds} 轮 |

---

## 🎯 执行摘要

> **投资建议**: {investment_recommendation_summary}
> 
> **风险等级**: {risk_level}
> 
> **置信度**: {confidence_level}

{executive_summary}

---

## 📈 市场分析矩阵

### 技术面分析
```
技术指标评分: {technical_score}
趋势方向: {trend_direction}
支撑位: {support_level}
阻力位: {resistance_level}
```

{market_analysis}

### 基本面分析
```
估值水平: {valuation_level}
财务健康度: {financial_health}
成长性: {growth_potential}
盈利能力: {profitability}
```

{fundamentals_analysis}

### 情感面分析
```
市场情绪: {market_sentiment}
新闻影响: {news_impact}
社交媒体热度: {social_media_buzz}
```

{sentiment_analysis}

---

## 📰 重要信息汇总

{news_analysis}

---

## 🔬 深度研究分析

### 🐂 多头研究报告
{bull_arguments}

### 🐻 空头研究报告  
{bear_arguments}

### 👨‍💼 研究经理综合评估
{investment_recommendation}

---

## 💼 交易策略制定

### 策略概述
{trading_strategy_overview}

### 具体建议
{trading_strategy}

### 风险控制
{risk_management_strategy}

---

## ⚠️ 全面风险评估

{risk_assessment}

---

## 🎯 最终投资决策

{final_decision}

---

## 📊 附录：分析方法说明

### 智能体协作流程
1. **数据收集**: 多源数据实时获取
2. **专业分析**: 4个专业分析师并行分析
3. **深度研究**: 多空研究员对比研究
4. **综合评估**: 研究经理整合观点
5. **风险辩论**: 多轮辩论深化分析
6. **最终决策**: 风险经理和交易员制定策略

### 数据来源
{data_sources_detail}

---

*报告生成时间: {report_generation_time}*

**版权声明**: 本报告版权归TradingAgents系统所有，未经授权不得转载。
"""
    
    def _get_executive_template(self) -> str:
        """高管摘要模板"""
        return """# 📊 {stock_name} ({symbol}) 投资决策报告

## 🎯 核心结论

**投资建议**: {investment_recommendation_summary}

**目标价位**: {target_price}

**风险等级**: {risk_level}

---

## 📈 关键指标

| 指标 | 数值 | 评级 |
|------|------|------|
| 技术面评分 | {technical_score} | {technical_rating} |
| 基本面评分 | {fundamental_score} | {fundamental_rating} |
| 情感面评分 | {sentiment_score} | {sentiment_rating} |
| 综合评分 | {overall_score} | {overall_rating} |

---

## 💡 投资亮点

{investment_highlights}

---

## ⚠️ 主要风险

{key_risks}

---

## 💼 操作建议

{trading_recommendations}

---

*本报告为高管决策版本，详细分析请参考完整报告*
"""
    
    def _get_technical_template(self) -> str:
        """技术分析模板"""
        return """# 📊 {stock_name} ({symbol}) 技术分析报告

## 📈 技术指标分析

{market_analysis}

## 📊 图表分析

{chart_analysis}

## 🔍 量价分析

{volume_price_analysis}

## 📈 趋势分析

{trend_analysis}

## 🎯 技术面结论

{technical_conclusion}
"""
    
    def _get_research_template(self) -> str:
        """研究报告模板"""
        return """# 📊 {stock_name} ({symbol}) 深度研究报告

## 🔬 研究方法

本报告采用TradingAgents多智能体协作分析框架，通过15个专业智能体的协作完成全面分析。

## 📊 基本面深度分析

{fundamentals_analysis}

## 📰 行业与宏观分析

{industry_analysis}

## 🔬 多空辩论详情

### 🐂 多头论据
{bull_arguments}

### 🐻 空头论据
{bear_arguments}

## 👨‍💼 研究结论

{research_conclusion}

## 📈 估值分析

{valuation_analysis}

## 🎯 投资建议

{investment_recommendation}
"""
    
    def _load_custom_templates(self) -> Dict[str, str]:
        """加载自定义模板"""
        custom_templates = {}
        try:
            for template_file in self.templates_dir.glob("*.md"):
                template_name = template_file.stem
                with open(template_file, 'r', encoding='utf-8') as f:
                    custom_templates[template_name] = f.read()
            logger.info(f"加载了 {len(custom_templates)} 个自定义模板")
        except Exception as e:
            logger.error(f"加载自定义模板失败: {e}")
        return custom_templates
    
    def get_available_templates(self) -> Dict[str, str]:
        """获取所有可用模板"""
        templates = {}
        templates.update(self.built_in_templates)
        templates.update(self.custom_templates)
        return templates
    
    def generate_report(self, result: Dict[str, Any], template_name: str = "standard", 
                       format_options: Dict[str, Any] = None) -> str:
        """生成报告"""
        try:
            # 获取模板
            templates = self.get_available_templates()
            if template_name not in templates:
                logger.warning(f"模板 {template_name} 不存在，使用标准模板")
                template_name = "standard"
            
            template = templates[template_name]
            
            # 准备数据
            report_data = self._prepare_report_data(result, format_options or {})
            
            # 格式化模板
            formatted_report = self._format_template(template, report_data)
            
            # 后处理
            final_report = self._post_process_report(formatted_report, format_options or {})
            
            return final_report
            
        except Exception as e:
            logger.error(f"生成报告失败: {e}")
            return f"❌ 报告生成失败: {str(e)}"
    
    def _prepare_report_data(self, result: Dict[str, Any], format_options: Dict[str, Any]) -> Dict[str, Any]:
        """准备报告数据"""
        # 基础数据
        data = {
            "symbol": result.get("symbol", "未知"),
            "stock_name": result.get("stock_name", "未知"),
            "analysis_time": result.get("analysis_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "analysis_depth": result.get("analysis_depth", "标准"),
            "report_generation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            
            # 分析内容
            "comprehensive_report": self._format_content(result.get("comprehensive_report", "暂无数据")),
            "market_analysis": self._format_content(result.get("market_analysis", "暂无数据")),
            "sentiment_analysis": self._format_content(result.get("sentiment_analysis", "暂无数据")),
            "news_analysis": self._format_content(result.get("news_analysis", "暂无数据")),
            "fundamentals_analysis": self._format_content(result.get("fundamentals_analysis", "暂无数据")),
            "bull_arguments": self._format_content(result.get("bull_arguments", "暂无数据")),
            "bear_arguments": self._format_content(result.get("bear_arguments", "暂无数据")),
            "investment_recommendation": self._format_content(result.get("investment_recommendation", "暂无数据")),
            "trading_strategy": self._format_content(result.get("trading_strategy", "暂无数据")),
            "risk_assessment": self._format_content(result.get("risk_assessment", "暂无数据")),
            "final_decision": self._format_content(result.get("final_decision", "暂无数据")),
            
            # 统计信息
            "agent_count": result.get("agent_count", 15),
            "analysis_rounds": result.get("analysis_rounds", 1),
            "data_sources": result.get("data_sources", "AkShare, 实时数据"),
            "confidence_level": result.get("confidence_level", "中等"),
            
            # 摘要信息
            "executive_summary": self._generate_executive_summary(result),
            "investment_recommendation_summary": self._extract_investment_summary(result),
            "risk_level": self._assess_risk_level(result),
        }
        
        # 添加评分信息
        data.update(self._generate_scores(result))
        
        # 添加格式化选项
        if format_options.get("include_charts", False):
            data["chart_analysis"] = self._generate_chart_analysis(result)
        
        return data
    
    def _format_content(self, content: str) -> str:
        """格式化内容"""
        if not content or content == "暂无数据":
            return "> 📝 暂无相关分析数据"
        
        # 清理内容
        content = str(content).strip()
        
        # 移除多余的换行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 确保内容不为空
        if not content:
            return "> 📝 暂无相关分析数据"
        
        return content
    
    def _generate_executive_summary(self, result: Dict[str, Any]) -> str:
        """生成执行摘要"""
        try:
            summary_parts = []
            
            # 从各部分提取关键信息
            if result.get("investment_recommendation"):
                summary_parts.append(f"**投资建议**: {self._extract_key_sentence(result['investment_recommendation'])}")
            
            if result.get("risk_assessment"):
                summary_parts.append(f"**风险评估**: {self._extract_key_sentence(result['risk_assessment'])}")
            
            if result.get("final_decision"):
                summary_parts.append(f"**最终决策**: {self._extract_key_sentence(result['final_decision'])}")
            
            return "\n\n".join(summary_parts) if summary_parts else "基于多智能体协作分析的综合投资建议。"
            
        except Exception as e:
            logger.error(f"生成执行摘要失败: {e}")
            return "基于多智能体协作分析的综合投资建议。"
    
    def _extract_key_sentence(self, content: str) -> str:
        """提取关键句子"""
        if not content:
            return "暂无信息"
        
        # 简单提取第一句话
        sentences = content.split('。')
        if sentences:
            return sentences[0].strip() + "。"
        return content[:100] + "..." if len(content) > 100 else content
    
    def _extract_investment_summary(self, result: Dict[str, Any]) -> str:
        """提取投资建议摘要"""
        recommendation = result.get("investment_recommendation", "")
        if "买入" in recommendation or "建议购买" in recommendation:
            return "买入"
        elif "卖出" in recommendation or "建议卖出" in recommendation:
            return "卖出"
        elif "持有" in recommendation or "建议持有" in recommendation:
            return "持有"
        else:
            return "观望"
    
    def _assess_risk_level(self, result: Dict[str, Any]) -> str:
        """评估风险等级"""
        risk_content = result.get("risk_assessment", "").lower()
        if "高风险" in risk_content or "风险较高" in risk_content:
            return "高风险"
        elif "低风险" in risk_content or "风险较低" in risk_content:
            return "低风险"
        else:
            return "中等风险"
    
    def _generate_scores(self, result: Dict[str, Any]) -> Dict[str, str]:
        """生成评分信息"""
        # 这里可以根据实际分析结果计算评分
        # 目前使用模拟数据
        return {
            "technical_score": "7.5/10",
            "fundamental_score": "8.0/10", 
            "sentiment_score": "6.5/10",
            "overall_score": "7.3/10",
            "technical_rating": "良好",
            "fundamental_rating": "优秀",
            "sentiment_rating": "一般",
            "overall_rating": "良好"
        }
    
    def _generate_chart_analysis(self, result: Dict[str, Any]) -> str:
        """生成图表分析"""
        return "📊 图表分析功能开发中，敬请期待。"
    
    def _format_template(self, template: str, data: Dict[str, Any]) -> str:
        """格式化模板"""
        try:
            return template.format(**data)
        except KeyError as e:
            logger.warning(f"模板变量缺失: {e}")
            # 替换缺失的变量为默认值
            for key in re.findall(r'\{(\w+)\}', template):
                if key not in data:
                    data[key] = f"[{key}数据缺失]"
            return template.format(**data)
    
    def _post_process_report(self, report: str, format_options: Dict[str, Any]) -> str:
        """后处理报告"""
        # 移除多余的空行
        report = re.sub(r'\n{4,}', '\n\n\n', report)
        
        # 添加目录（如果需要）
        if format_options.get("include_toc", False):
            toc = self._generate_toc(report)
            report = toc + "\n\n" + report
        
        # 添加页脚
        if format_options.get("include_footer", True):
            footer = f"\n\n---\n\n*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n*Powered by TradingAgents*"
            report += footer
        
        return report
    
    def _generate_toc(self, report: str) -> str:
        """生成目录"""
        toc_lines = ["## 📑 目录\n"]
        
        # 提取标题
        headers = re.findall(r'^(#{1,3})\s+(.+)$', report, re.MULTILINE)
        
        for level, title in headers:
            indent = "  " * (len(level) - 1)
            # 生成锚点链接
            anchor = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '-').lower()
            toc_lines.append(f"{indent}- [{title}](#{anchor})")
        
        return "\n".join(toc_lines)
    
    def save_template(self, template_name: str, template_content: str) -> Dict[str, Any]:
        """保存自定义模板"""
        try:
            template_file = self.templates_dir / f"{template_name}.md"
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            # 重新加载自定义模板
            self.custom_templates = self._load_custom_templates()
            
            logger.info(f"模板 {template_name} 保存成功")
            return {"status": "success", "message": f"模板 {template_name} 保存成功"}
            
        except Exception as e:
            logger.error(f"保存模板失败: {e}")
            return {"status": "error", "message": f"保存失败: {str(e)}"}
    
    def delete_template(self, template_name: str) -> Dict[str, Any]:
        """删除自定义模板"""
        try:
            if template_name in self.built_in_templates:
                return {"status": "error", "message": "不能删除内置模板"}
            
            template_file = self.templates_dir / f"{template_name}.md"
            if template_file.exists():
                template_file.unlink()
                
                # 重新加载自定义模板
                self.custom_templates = self._load_custom_templates()
                
                logger.info(f"模板 {template_name} 删除成功")
                return {"status": "success", "message": f"模板 {template_name} 删除成功"}
            else:
                return {"status": "error", "message": f"模板 {template_name} 不存在"}
                
        except Exception as e:
            logger.error(f"删除模板失败: {e}")
            return {"status": "error", "message": f"删除失败: {str(e)}"}


class ReportManagerUI:
    """报告管理界面"""

    def __init__(self, enhanced_app=None):
        self.enhanced_app = enhanced_app
        self.report_generator = EnhancedReportGenerator()

    def create_report_management_interface(self):
        """创建报告管理界面"""
        import gradio as gr

        with gr.Blocks(title="报告管理") as interface:
            gr.Markdown("# 📊 报告管理系统")

            with gr.Tabs():
                # Tab 1: 报告生成
                with gr.TabItem("📄 报告生成"):
                    self._create_report_generation_tab()

                # Tab 2: 模板管理
                with gr.TabItem("📝 模板管理"):
                    self._create_template_management_tab()

                # Tab 3: 报告历史
                with gr.TabItem("📚 报告历史"):
                    self._create_report_history_tab()

        return interface

    def _create_report_generation_tab(self):
        """创建报告生成标签页"""
        import gradio as gr

        gr.Markdown("## 生成分析报告")

        with gr.Row():
            with gr.Column(scale=1):
                template_selector = gr.Dropdown(
                    choices=list(self.report_generator.get_available_templates().keys()),
                    label="选择模板",
                    value="standard"
                )

                include_toc = gr.Checkbox(label="包含目录", value=False)
                include_charts = gr.Checkbox(label="包含图表分析", value=False)
                include_footer = gr.Checkbox(label="包含页脚", value=True)

                generate_btn = gr.Button("📄 生成报告", variant="primary")

                download_btn = gr.DownloadButton("💾 下载报告", variant="secondary")

            with gr.Column(scale=2):
                report_preview = gr.Textbox(
                    label="报告预览",
                    lines=20,
                    max_lines=30,
                    interactive=False,
                    show_copy_button=True
                )

                generation_status = gr.Textbox(
                    label="生成状态",
                    interactive=False
                )

        def generate_report(template_name, toc, charts, footer):
            try:
                if not self.enhanced_app or not self.enhanced_app.last_analysis_result:
                    return "❌ 没有可用的分析结果，请先进行股票分析", ""

                format_options = {
                    "include_toc": toc,
                    "include_charts": charts,
                    "include_footer": footer
                }

                report = self.report_generator.generate_report(
                    self.enhanced_app.last_analysis_result,
                    template_name,
                    format_options
                )

                return "✅ 报告生成成功", report

            except Exception as e:
                return f"❌ 生成失败: {str(e)}", ""

        generate_btn.click(
            fn=generate_report,
            inputs=[template_selector, include_toc, include_charts, include_footer],
            outputs=[generation_status, report_preview]
        )

    def _create_template_management_tab(self):
        """创建模板管理标签页"""
        import gradio as gr

        gr.Markdown("## 模板管理")

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 模板列表")

                template_list = gr.Dropdown(
                    choices=list(self.report_generator.get_available_templates().keys()),
                    label="选择模板",
                    value="standard"
                )

                with gr.Row():
                    load_template_btn = gr.Button("📋 加载模板")
                    delete_template_btn = gr.Button("🗑️ 删除模板", variant="stop")

                template_status = gr.Textbox(
                    label="操作状态",
                    interactive=False
                )

            with gr.Column(scale=2):
                gr.Markdown("### 模板编辑")

                template_name_input = gr.Textbox(
                    label="模板名称",
                    placeholder="输入新模板名称"
                )

                template_content = gr.Textbox(
                    label="模板内容",
                    lines=15,
                    placeholder="输入模板内容，使用 {变量名} 格式插入变量"
                )

                save_template_btn = gr.Button("💾 保存模板", variant="primary")

        def load_template(template_name):
            try:
                templates = self.report_generator.get_available_templates()
                if template_name in templates:
                    return template_name, templates[template_name], f"✅ 模板 {template_name} 加载成功"
                else:
                    return "", "", f"❌ 模板 {template_name} 不存在"
            except Exception as e:
                return "", "", f"❌ 加载失败: {str(e)}"

        def save_template(name, content):
            try:
                if not name or not content:
                    return "❌ 请输入模板名称和内容"

                result = self.report_generator.save_template(name, content)

                if result["status"] == "success":
                    # 更新模板列表
                    new_choices = list(self.report_generator.get_available_templates().keys())
                    return f"✅ {result['message']}"
                else:
                    return f"❌ {result['message']}"

            except Exception as e:
                return f"❌ 保存失败: {str(e)}"

        def delete_template(template_name):
            try:
                result = self.report_generator.delete_template(template_name)

                if result["status"] == "success":
                    return f"✅ {result['message']}"
                else:
                    return f"❌ {result['message']}"

            except Exception as e:
                return f"❌ 删除失败: {str(e)}"

        load_template_btn.click(
            fn=load_template,
            inputs=[template_list],
            outputs=[template_name_input, template_content, template_status]
        )

        save_template_btn.click(
            fn=save_template,
            inputs=[template_name_input, template_content],
            outputs=[template_status]
        )

        delete_template_btn.click(
            fn=delete_template,
            inputs=[template_list],
            outputs=[template_status]
        )

    def _create_report_history_tab(self):
        """创建报告历史标签页"""
        import gradio as gr

        gr.Markdown("## 报告历史")

        with gr.Row():
            with gr.Column(scale=1):
                history_list = gr.Dropdown(
                    label="历史报告",
                    choices=[]
                )

                with gr.Row():
                    refresh_history_btn = gr.Button("🔄 刷新列表")
                    delete_report_btn = gr.Button("🗑️ 删除报告", variant="stop")

                history_status = gr.Textbox(
                    label="操作状态",
                    interactive=False
                )

            with gr.Column(scale=2):
                report_content = gr.Textbox(
                    label="报告内容",
                    lines=20,
                    interactive=False,
                    show_copy_button=True
                )

        def refresh_history():
            try:
                if self.enhanced_app:
                    history = self.enhanced_app.get_report_history()
                    choices = [(item["display_name"], item["file_path"]) for item in history]
                    return gr.Dropdown.update(choices=choices)
                else:
                    return gr.Dropdown.update(choices=[])
            except Exception as e:
                return gr.Dropdown.update(choices=[])

        def load_report(file_path):
            try:
                if not file_path:
                    return ""

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                return content

            except Exception as e:
                return f"❌ 加载报告失败: {str(e)}"

        refresh_history_btn.click(
            fn=refresh_history,
            outputs=[history_list]
        )

        history_list.change(
            fn=load_report,
            inputs=[history_list],
            outputs=[report_content]
        )
