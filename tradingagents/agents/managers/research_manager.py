"""
研究经理 - 协调多空辩论并做出投资建议
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ResearchManager(BaseAgent):
    """研究经理 - 协调辩论，做出投资建议"""
    
    def __init__(self, llm_client=None, memory_manager=None):
        super().__init__(
            agent_id="research_manager",
            agent_type="研究经理",
            llm_client=llm_client,
            memory_manager=memory_manager
        )
        self.debate_sessions = []
    
    async def analyze(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        协调研究分析并做出投资建议
        
        Args:
            input_data: 包含多空研究结果
            context: 上下文信息
            
        Returns:
            投资建议结果
        """
        try:
            symbol = input_data.get("symbol", "")
            bull_research = input_data.get("bull_research", {})
            bear_research = input_data.get("bear_research", {})
            debate_results = input_data.get("debate_results", [])
            
            # 构建综合分析提示
            analysis_prompt = self._build_manager_prompt(symbol, bull_research, bear_research, debate_results)
            
            # 获取LLM分析
            llm_response = await self.get_llm_response(analysis_prompt, context)
            
            # 解析和结构化结果
            analysis_result = self._parse_manager_result(llm_response, symbol)
            
            # 记录决策会话
            self.debate_sessions.append({
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "bull_points": bull_research.get("key_arguments", []),
                "bear_points": bear_research.get("key_risks", []),
                "final_decision": analysis_result.get("investment_recommendation", "")
            })
            
            return {
                "status": "success",
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "analysis_type": "investment_recommendation",
                "symbol": symbol,
                "content": analysis_result,
                "raw_response": llm_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"研究经理分析失败: {e}")
            return {
                "status": "error",
                "agent_id": self.agent_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_manager_prompt(self, symbol: str, bull_research: Dict, bear_research: Dict, debate_results: List) -> str:
        """构建研究经理分析提示"""
        prompt = f"""
作为研究经理，你需要基于多空研究团队的辩论结果，对股票 {symbol} 做出最终的投资建议。

多头研究员观点:
投资主题: {bull_research.get('investment_thesis', 'N/A')}
关键论据:
"""
        
        # 添加多头论据
        for i, arg in enumerate(bull_research.get('key_arguments', []), 1):
            prompt += f"{i}. {arg}\n"
        
        prompt += f"""
催化剂: {bull_research.get('catalysts', [])}
信念强度: {bull_research.get('conviction_level', 'N/A')}

空头研究员观点:
风险主题: {bear_research.get('risk_thesis', 'N/A')}
关键风险:
"""
        
        # 添加空头风险
        for i, risk in enumerate(bear_research.get('key_risks', []), 1):
            prompt += f"{i}. {risk}\n"
        
        prompt += f"""
风险严重程度: {bear_research.get('risk_severity', 'N/A')}
发生概率: {bear_research.get('probability_assessment', 'N/A')}

辩论过程摘要:
"""
        
        # 添加辩论结果
        for i, debate in enumerate(debate_results, 1):
            prompt += f"""
第{i}轮辩论:
- 多头观点: {debate.get('bull_response', 'N/A')[:200]}...
- 空头观点: {debate.get('bear_response', 'N/A')[:200]}...
"""
        
        prompt += """
作为研究经理，请综合考虑以下因素做出投资建议:

1. **论据权衡**
   - 多空双方论据的说服力对比
   - 关键论据的可信度评估
   - 论据支撑证据的充分性

2. **风险收益评估**
   - 潜在收益vs潜在风险
   - 风险发生概率评估
   - 收益实现可能性

3. **时机分析**
   - 当前投资时机评估
   - 市场环境适宜性
   - 催化剂时间窗口

4. **不确定性管理**
   - 关键不确定因素识别
   - 情景分析和压力测试
   - 风险缓解措施

5. **投资建议**
   - 明确的投资评级 (强烈买入/买入/持有/卖出/强烈卖出)
   - 建议仓位比例
   - 投资时间范围
   - 关键监控指标

6. **执行策略**
   - 分批建仓策略
   - 止损止盈设置
   - 动态调整机制

请提供平衡、客观的投资建议，充分考虑多空双方的合理观点。
"""
        
        return prompt
    
    def _parse_manager_result(self, llm_response: str, symbol: str) -> Dict[str, Any]:
        """解析研究经理结果"""
        try:
            result = {
                "symbol": symbol,
                "investment_summary": llm_response,
                "investment_recommendation": self._extract_recommendation(llm_response),
                "confidence_level": self._extract_confidence_level(llm_response),
                "position_size": self._extract_position_size(llm_response),
                "time_horizon": self._extract_time_horizon(llm_response),
                "key_factors": self._extract_key_factors(llm_response),
                "risk_assessment": self._extract_risk_assessment(llm_response),
                "monitoring_indicators": self._extract_monitoring_indicators(llm_response),
                "execution_strategy": self._extract_execution_strategy(llm_response),
                "decision_rationale": self._extract_decision_rationale(llm_response)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"解析研究经理结果失败: {e}")
            return {
                "symbol": symbol,
                "investment_summary": llm_response,
                "investment_recommendation": "持有",
                "confidence_level": 0.5
            }
    
    def _extract_recommendation(self, text: str) -> str:
        """提取投资建议"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["强烈买入", "强买"]):
            return "强烈买入"
        elif any(word in text_lower for word in ["买入", "建仓", "增持"]):
            return "买入"
        elif any(word in text_lower for word in ["强烈卖出", "强卖"]):
            return "强烈卖出"
        elif any(word in text_lower for word in ["卖出", "减仓", "平仓"]):
            return "卖出"
        elif any(word in text_lower for word in ["持有", "维持"]):
            return "持有"
        else:
            return "中性"
    
    def _extract_confidence_level(self, text: str) -> float:
        """提取信心水平"""
        text_lower = text.lower()
        
        high_confidence = ["高度确信", "非常确定", "强烈信心", "明确"]
        medium_confidence = ["较为确信", "相对确定", "适度信心"]
        low_confidence = ["不太确定", "谨慎", "有限信心", "不确定"]
        
        if any(word in text_lower for word in high_confidence):
            return 0.8
        elif any(word in text_lower for word in low_confidence):
            return 0.3
        elif any(word in text_lower for word in medium_confidence):
            return 0.6
        else:
            return 0.5
    
    def _extract_position_size(self, text: str) -> str:
        """提取建议仓位"""
        import re
        
        # 查找仓位相关的数字
        position_patterns = [
            r'仓位[：:]\s*(\d+\.?\d*)%',
            r'建议仓位[：:]\s*(\d+\.?\d*)%',
            r'配置比例[：:]\s*(\d+\.?\d*)%'
        ]
        
        for pattern in position_patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)}%"
        
        # 根据投资建议推断仓位
        text_lower = text.lower()
        if any(word in text_lower for word in ["强烈买入", "重仓"]):
            return "20-30%"
        elif any(word in text_lower for word in ["买入", "标准"]):
            return "10-20%"
        elif any(word in text_lower for word in ["轻仓", "小仓位"]):
            return "5-10%"
        else:
            return "待定"
    
    def _extract_time_horizon(self, text: str) -> str:
        """提取投资时间范围"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["长期", "长线", "战略持有"]):
            return "长期(1年以上)"
        elif any(word in text_lower for word in ["短期", "短线", "快进快出"]):
            return "短期(1-3个月)"
        else:
            return "中期(3-12个月)"
    
    def _extract_key_factors(self, text: str) -> List[str]:
        """提取关键因素"""
        factors = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["关键", "重要", "核心", "主要"]):
                factor = line.strip()
                if factor and len(factor) > 10:
                    factors.append(factor)
        
        return factors[:5]  # 最多返回5个关键因素
    
    def _extract_risk_assessment(self, text: str) -> Dict[str, str]:
        """提取风险评估"""
        text_lower = text.lower()
        
        # 整体风险水平
        if any(word in text_lower for word in ["高风险", "风险较高"]):
            risk_level = "高"
        elif any(word in text_lower for word in ["低风险", "风险较低"]):
            risk_level = "低"
        else:
            risk_level = "中等"
        
        # 主要风险类型
        risk_types = []
        if "市场风险" in text_lower:
            risk_types.append("市场风险")
        if "流动性风险" in text_lower:
            risk_types.append("流动性风险")
        if "信用风险" in text_lower:
            risk_types.append("信用风险")
        if "操作风险" in text_lower:
            risk_types.append("操作风险")
        
        return {
            "risk_level": risk_level,
            "main_risks": risk_types[:3]
        }
    
    def _extract_monitoring_indicators(self, text: str) -> List[str]:
        """提取监控指标"""
        indicators = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["监控", "关注", "跟踪", "观察"]):
                indicator = line.strip()
                if indicator and len(indicator) > 10:
                    indicators.append(indicator)
        
        return indicators[:5]  # 最多返回5个监控指标
    
    def _extract_execution_strategy(self, text: str) -> Dict[str, str]:
        """提取执行策略"""
        strategy = {}
        
        # 建仓策略
        if "分批" in text.lower():
            strategy["entry"] = "分批建仓"
        elif "一次性" in text.lower():
            strategy["entry"] = "一次性建仓"
        else:
            strategy["entry"] = "灵活建仓"
        
        # 止损策略
        import re
        stop_loss_match = re.search(r'止损[：:]\s*(\d+\.?\d*)%', text)
        if stop_loss_match:
            strategy["stop_loss"] = f"{stop_loss_match.group(1)}%"
        else:
            strategy["stop_loss"] = "根据技术位设定"
        
        # 止盈策略
        take_profit_match = re.search(r'止盈[：:]\s*(\d+\.?\d*)%', text)
        if take_profit_match:
            strategy["take_profit"] = f"{take_profit_match.group(1)}%"
        else:
            strategy["take_profit"] = "分批止盈"
        
        return strategy
    
    def _extract_decision_rationale(self, text: str) -> str:
        """提取决策理由"""
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["理由", "原因", "基于", "考虑"]):
                if len(line.strip()) > 20:
                    return line.strip()
        
        # 如果没有明确的理由，返回前几句作为理由
        sentences = text.split('。')
        if sentences:
            return sentences[0][:150] + "..." if len(sentences[0]) > 150 else sentences[0]
        
        return "基于多空辩论的综合判断"
