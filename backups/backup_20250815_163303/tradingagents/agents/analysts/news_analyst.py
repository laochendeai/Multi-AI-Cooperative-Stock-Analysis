"""
新闻分析师 - 专业新闻分析和宏观经济事件监控
"""

import logging
from typing import Dict, Any
from datetime import datetime

from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)

class NewsAnalyst(BaseAgent):
    """新闻分析师"""
    
    def __init__(self, llm_client=None, memory_manager=None):
        super().__init__(
            agent_id="news_analyst",
            agent_type="新闻分析师",
            llm_client=llm_client,
            memory_manager=memory_manager
        )
    
    async def analyze(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行新闻分析
        
        Args:
            input_data: 包含股票代码、新闻数据等
            context: 上下文信息
            
        Returns:
            新闻分析结果
        """
        try:
            symbol = input_data.get("symbol", "")
            news_data = input_data.get("news_data", [])
            macro_events = input_data.get("macro_events", [])
            
            # 构建分析提示
            analysis_prompt = self._build_news_prompt(symbol, news_data, macro_events)
            
            # 获取LLM分析
            llm_response = await self.get_llm_response(analysis_prompt, context)
            
            # 解析和结构化结果
            analysis_result = self._parse_news_result(llm_response, symbol)
            
            return {
                "status": "success",
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "analysis_type": "news_analysis",
                "symbol": symbol,
                "content": analysis_result,
                "raw_response": llm_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"新闻分析失败: {e}")
            return {
                "status": "error",
                "agent_id": self.agent_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_news_prompt(self, symbol: str, news_data: list, macro_events: list) -> str:
        """构建新闻分析提示"""
        prompt = f"""
作为专业的新闻分析师，请对股票 {symbol} 相关的新闻和宏观经济事件进行全面分析。

相关新闻:
"""
        
        # 添加新闻数据
        for i, news in enumerate(news_data[:5], 1):  # 最多分析5条新闻
            prompt += f"""
新闻 {i}:
- 标题: {news.get('title', 'N/A')}
- 来源: {news.get('source', 'N/A')}
- 时间: {news.get('publish_time', 'N/A')}
- 摘要: {news.get('summary', 'N/A')}
"""
        
        prompt += "\n宏观经济事件:\n"
        
        # 添加宏观事件
        for i, event in enumerate(macro_events[:3], 1):  # 最多分析3个事件
            prompt += f"""
事件 {i}:
- 事件: {event.get('event', 'N/A')}
- 时间: {event.get('date', 'N/A')}
- 重要性: {event.get('importance', 'N/A')}
- 影响: {event.get('impact', 'N/A')}
"""
        
        prompt += """
请从以下角度进行分析:

1. **新闻影响评估**
   - 各条新闻对股价的潜在影响（正面/负面/中性）
   - 新闻的可信度和重要性评级
   - 市场已反应程度评估

2. **宏观环境分析**
   - 当前宏观经济环境对该股票的影响
   - 政策变化的潜在影响
   - 行业趋势分析

3. **事件关联性分析**
   - 新闻事件之间的关联性
   - 与历史类似事件的对比
   - 事件发展的可能路径

4. **时效性分析**
   - 新闻的时效性和持续影响力
   - 短期vs长期影响评估
   - 关键时间节点预测

5. **市场反应预测**
   - 市场对新闻的可能反应
   - 投资者情绪变化预测
   - 交易量和波动性预期

6. **风险与机会**
   - 新闻带来的投资机会
   - 潜在风险点识别
   - 需要关注的后续发展

请提供客观、专业的新闻分析，重点关注对投资决策的实际指导意义。
"""
        
        return prompt
    
    def _parse_news_result(self, llm_response: str, symbol: str) -> Dict[str, Any]:
        """解析新闻分析结果"""
        try:
            result = {
                "symbol": symbol,
                "news_summary": llm_response,
                "overall_impact": self._extract_overall_impact(llm_response),
                "impact_strength": self._extract_impact_strength(llm_response),
                "time_horizon": self._extract_time_horizon(llm_response),
                "key_events": self._extract_key_events(llm_response),
                "market_reaction": self._extract_market_reaction(llm_response),
                "risk_opportunities": self._extract_risk_opportunities(llm_response),
                "credibility_score": self._calculate_credibility(llm_response),
                "urgency_level": self._extract_urgency_level(llm_response)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"解析新闻分析结果失败: {e}")
            return {
                "symbol": symbol,
                "news_summary": llm_response,
                "overall_impact": "中性",
                "impact_strength": "中等",
                "credibility_score": 0.5
            }
    
    def _extract_overall_impact(self, text: str) -> str:
        """提取整体影响"""
        text_lower = text.lower()
        
        positive_indicators = ["正面", "利好", "积极", "推动", "支撑", "提升"]
        negative_indicators = ["负面", "利空", "消极", "打压", "拖累", "下降"]
        
        positive_count = sum(1 for word in positive_indicators if word in text_lower)
        negative_count = sum(1 for word in negative_indicators if word in text_lower)
        
        if positive_count > negative_count:
            return "正面"
        elif negative_count > positive_count:
            return "负面"
        else:
            return "中性"
    
    def _extract_impact_strength(self, text: str) -> str:
        """提取影响强度"""
        text_lower = text.lower()
        
        strong_indicators = ["重大", "显著", "强烈", "巨大", "深远"]
        weak_indicators = ["轻微", "有限", "温和", "较小"]
        
        if any(word in text_lower for word in strong_indicators):
            return "强"
        elif any(word in text_lower for word in weak_indicators):
            return "弱"
        else:
            return "中等"
    
    def _extract_time_horizon(self, text: str) -> str:
        """提取影响时间范围"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["长期", "持续", "长远", "战略"]):
            return "长期"
        elif any(word in text_lower for word in ["短期", "即时", "临时", "短暂"]):
            return "短期"
        else:
            return "中期"
    
    def _extract_key_events(self, text: str) -> list:
        """提取关键事件"""
        events = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["事件", "新闻", "发布", "公告"]):
                event = line.strip()
                if event and len(event) < 150:
                    events.append(event)
        
        return events[:3]  # 最多返回3个关键事件
    
    def _extract_market_reaction(self, text: str) -> str:
        """提取市场反应预测"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["上涨", "买入", "看涨", "积极反应"]):
            return "积极"
        elif any(word in text_lower for word in ["下跌", "卖出", "看跌", "消极反应"]):
            return "消极"
        else:
            return "平淡"
    
    def _extract_risk_opportunities(self, text: str) -> Dict[str, list]:
        """提取风险和机会"""
        risks = []
        opportunities = []
        
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line_lower = line.lower()
            if "风险" in line_lower:
                current_section = "risk"
            elif "机会" in line_lower or "机遇" in line_lower:
                current_section = "opportunity"
            elif line.strip() and current_section:
                if current_section == "risk":
                    risks.append(line.strip())
                elif current_section == "opportunity":
                    opportunities.append(line.strip())
        
        return {
            "risks": risks[:3],
            "opportunities": opportunities[:3]
        }
    
    def _calculate_credibility(self, text: str) -> float:
        """计算新闻可信度分数"""
        text_lower = text.lower()
        
        credible_indicators = ["官方", "权威", "确认", "证实", "公告"]
        uncertain_indicators = ["传言", "据说", "可能", "疑似", "未证实"]
        
        credible_count = sum(1 for word in credible_indicators if word in text_lower)
        uncertain_count = sum(1 for word in uncertain_indicators if word in text_lower)
        
        base_credibility = 0.6
        credibility_boost = credible_count * 0.1
        credibility_penalty = uncertain_count * 0.15
        
        credibility = max(0.2, min(0.95, base_credibility + credibility_boost - credibility_penalty))
        return round(credibility, 2)
    
    def _extract_urgency_level(self, text: str) -> str:
        """提取紧急程度"""
        text_lower = text.lower()
        
        urgent_indicators = ["紧急", "立即", "马上", "重大", "突发"]
        routine_indicators = ["常规", "例行", "定期", "预期"]
        
        if any(word in text_lower for word in urgent_indicators):
            return "高"
        elif any(word in text_lower for word in routine_indicators):
            return "低"
        else:
            return "中等"
