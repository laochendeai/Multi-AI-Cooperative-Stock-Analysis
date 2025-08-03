"""
风险经理 - 最终决策和风险评估
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)

class RiskManager(BaseAgent):
    """风险经理 - 最终交易决策制定者"""
    
    def __init__(self, llm_client=None, memory_manager=None):
        super().__init__(
            agent_id="risk_manager",
            agent_type="风险经理",
            llm_client=llm_client,
            memory_manager=memory_manager
        )
        self.final_decisions = []
    
    async def analyze(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        做出最终交易决策
        
        Args:
            input_data: 包含所有团队的分析结果
            context: 上下文信息
            
        Returns:
            最终决策结果
        """
        try:
            symbol = input_data.get("symbol", "")
            trading_strategy = input_data.get("trading_strategy", {})
            aggressive_analysis = input_data.get("aggressive_analysis", {})
            conservative_analysis = input_data.get("conservative_analysis", {})
            neutral_analysis = input_data.get("neutral_analysis", {})
            research_recommendation = input_data.get("research_recommendation", {})
            
            # 构建最终决策提示
            decision_prompt = self._build_decision_prompt(
                symbol, trading_strategy, aggressive_analysis, 
                conservative_analysis, neutral_analysis, research_recommendation
            )
            
            # 获取LLM分析
            llm_response = await self.get_llm_response(decision_prompt, context)
            
            # 解析和结构化结果
            decision_result = self._parse_decision_result(llm_response, symbol)
            
            # 记录最终决策
            self.final_decisions.append({
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "final_decision": decision_result.get("final_decision", ""),
                "confidence": decision_result.get("decision_confidence", 0.5),
                "rationale": decision_result.get("decision_rationale", "")
            })
            
            return {
                "status": "success",
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "analysis_type": "final_decision",
                "symbol": symbol,
                "content": decision_result,
                "raw_response": llm_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"风险经理决策失败: {e}")
            return {
                "status": "error",
                "agent_id": self.agent_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_decision_prompt(self, symbol: str, trading_strategy: Dict, 
                              aggressive_analysis: Dict, conservative_analysis: Dict, 
                              neutral_analysis: Dict, research_recommendation: Dict) -> str:
        """构建最终决策提示"""
        prompt = f"""
作为风险经理，你需要综合所有团队的分析结果，对股票 {symbol} 做出最终的交易决策。

研究团队建议:
- 投资评级: {research_recommendation.get('investment_recommendation', 'N/A')}
- 信心水平: {research_recommendation.get('confidence_level', 'N/A')}
- 建议仓位: {research_recommendation.get('position_size', 'N/A')}
- 决策理由: {research_recommendation.get('decision_rationale', 'N/A')}

交易员策略:
- 交易行动: {trading_strategy.get('trading_action', 'N/A')}
- 建议仓位: {trading_strategy.get('position_size', 'N/A')}
- 预期收益: {trading_strategy.get('expected_return', 'N/A')}
- 最大风险: {trading_strategy.get('max_risk', 'N/A')}

激进分析师观点:
- 机会评估: {aggressive_analysis.get('opportunity_assessment', 'N/A')}
- 仓位建议: {aggressive_analysis.get('position_recommendation', 'N/A')}
- 激进程度: {aggressive_analysis.get('aggressiveness_score', 'N/A')}

保守分析师观点:
- 风险控制: {conservative_analysis.get('risk_control_assessment', 'N/A')}
- 仓位建议: {conservative_analysis.get('recommended_position', 'N/A')}
- 保守程度: {conservative_analysis.get('conservatism_score', 'N/A')}

中性分析师观点:
- 平衡评估: {neutral_analysis.get('balance_assessment', 'N/A')}
- 仓位建议: {neutral_analysis.get('balanced_position', 'N/A')}
- 综合评估: {neutral_analysis.get('comprehensive_evaluation', 'N/A')}

作为风险经理，请综合考虑以下因素做出最终决策:

1. **团队观点整合**
   - 各团队观点的权重分配
   - 分歧点的识别和处理
   - 共识点的确认和强化

2. **风险收益综合评估**
   - 最终的风险收益比评估
   - 不同情景下的表现预期
   - 风险承受能力匹配度

3. **决策一致性检查**
   - 与公司投资政策的一致性
   - 与投资组合整体策略的协调
   - 与风险管理框架的匹配

4. **执行可行性评估**
   - 市场流动性考虑
   - 执行时机选择
   - 操作复杂度评估

5. **最终交易决策**
   - 明确的交易指令 (BUY/SELL/HOLD)
   - 具体的仓位大小
   - 详细的风险控制措施
   - 执行时间安排

6. **监控和调整机制**
   - 关键监控指标设定
   - 调整触发条件
   - 退出策略制定

请做出明确、可执行的最终决策，并提供充分的理由支撑。
"""
        
        return prompt
    
    def _parse_decision_result(self, llm_response: str, symbol: str) -> Dict[str, Any]:
        """解析最终决策结果"""
        try:
            result = {
                "symbol": symbol,
                "decision_summary": llm_response,
                "final_decision": self._extract_final_decision(llm_response),
                "final_position": self._extract_final_position(llm_response),
                "decision_confidence": self._extract_decision_confidence(llm_response),
                "risk_assessment": self._extract_final_risk_assessment(llm_response),
                "execution_plan": self._extract_final_execution_plan(llm_response),
                "monitoring_framework": self._extract_monitoring_framework(llm_response),
                "exit_strategy": self._extract_exit_strategy(llm_response),
                "decision_rationale": self._extract_decision_rationale(llm_response),
                "team_consensus": self._extract_team_consensus(llm_response),
                "contingency_measures": self._extract_contingency_measures(llm_response)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"解析最终决策结果失败: {e}")
            return {
                "symbol": symbol,
                "decision_summary": llm_response,
                "final_decision": "HOLD",
                "decision_confidence": 0.5
            }
    
    def _extract_final_decision(self, text: str) -> str:
        """提取最终决策"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["强烈买入", "strong buy", "强买"]):
            return "STRONG_BUY"
        elif any(word in text_lower for word in ["买入", "buy", "建仓"]):
            return "BUY"
        elif any(word in text_lower for word in ["强烈卖出", "strong sell", "强卖"]):
            return "STRONG_SELL"
        elif any(word in text_lower for word in ["卖出", "sell", "平仓"]):
            return "SELL"
        elif any(word in text_lower for word in ["持有", "hold", "维持"]):
            return "HOLD"
        else:
            return "HOLD"
    
    def _extract_final_position(self, text: str) -> str:
        """提取最终仓位"""
        import re
        
        # 查找最终仓位
        position_patterns = [
            r'最终仓位[：:]\s*(\d+\.?\d*)%',
            r'决定仓位[：:]\s*(\d+\.?\d*)%',
            r'仓位[：:]\s*(\d+\.?\d*)%'
        ]
        
        for pattern in position_patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)}%"
        
        # 根据决策推断仓位
        decision = self._extract_final_decision(text)
        if decision == "STRONG_BUY":
            return "25-30%"
        elif decision == "BUY":
            return "15-20%"
        elif decision == "SELL":
            return "减仓50%"
        elif decision == "STRONG_SELL":
            return "清仓"
        else:
            return "维持当前"
    
    def _extract_decision_confidence(self, text: str) -> float:
        """提取决策信心度"""
        text_lower = text.lower()
        
        high_confidence = ["高度确信", "非常确定", "强烈信心", "十分确定"]
        medium_confidence = ["较为确信", "相对确定", "适度信心", "比较确定"]
        low_confidence = ["不太确定", "信心有限", "谨慎判断", "存在疑虑"]
        
        if any(word in text_lower for word in high_confidence):
            return 0.85
        elif any(word in text_lower for word in low_confidence):
            return 0.35
        elif any(word in text_lower for word in medium_confidence):
            return 0.65
        else:
            return 0.5
    
    def _extract_final_risk_assessment(self, text: str) -> Dict[str, str]:
        """提取最终风险评估"""
        text_lower = text.lower()
        
        # 风险等级
        if any(word in text_lower for word in ["高风险", "风险较高", "风险很大"]):
            risk_level = "高"
        elif any(word in text_lower for word in ["低风险", "风险较低", "风险很小"]):
            risk_level = "低"
        else:
            risk_level = "中等"
        
        # 风险可控性
        if any(word in text_lower for word in ["风险可控", "可以控制", "在控制范围"]):
            controllability = "可控"
        elif any(word in text_lower for word in ["风险难控", "难以控制", "控制困难"]):
            controllability = "难控"
        else:
            controllability = "一般"
        
        return {
            "risk_level": risk_level,
            "controllability": controllability
        }
    
    def _extract_final_execution_plan(self, text: str) -> Dict[str, str]:
        """提取最终执行计划"""
        plan = {}
        
        # 执行时机
        if "立即" in text.lower():
            plan["timing"] = "立即执行"
        elif "分批" in text.lower():
            plan["timing"] = "分批执行"
        elif "择机" in text.lower():
            plan["timing"] = "择机执行"
        else:
            plan["timing"] = "正常执行"
        
        # 执行方式
        if "市价" in text.lower():
            plan["method"] = "市价执行"
        elif "限价" in text.lower():
            plan["method"] = "限价执行"
        else:
            plan["method"] = "智能执行"
        
        return plan
    
    def _extract_monitoring_framework(self, text: str) -> List[str]:
        """提取监控框架"""
        framework = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["监控", "跟踪", "观察", "关注"]):
                item = line.strip()
                if item and len(item) > 10:
                    framework.append(item)
        
        return framework[:5]  # 最多返回5个监控项
    
    def _extract_exit_strategy(self, text: str) -> Dict[str, str]:
        """提取退出策略"""
        strategy = {}
        
        # 止损
        import re
        stop_loss_match = re.search(r'止损[：:]\s*(\d+\.?\d*)%?', text)
        if stop_loss_match:
            strategy["stop_loss"] = stop_loss_match.group(1)
        else:
            strategy["stop_loss"] = "技术位"
        
        # 止盈
        take_profit_match = re.search(r'止盈[：:]\s*(\d+\.?\d*)%?', text)
        if take_profit_match:
            strategy["take_profit"] = take_profit_match.group(1)
        else:
            strategy["take_profit"] = "分批止盈"
        
        return strategy
    
    def _extract_decision_rationale(self, text: str) -> str:
        """提取决策理由"""
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["理由", "原因", "基于", "考虑", "因为"]):
                if len(line.strip()) > 20:
                    return line.strip()
        
        # 如果没有明确理由，提取前几句
        sentences = text.split('。')
        if sentences and len(sentences[0]) > 30:
            return sentences[0][:200] + "..." if len(sentences[0]) > 200 else sentences[0]
        
        return "基于全面风险评估的综合决策"
    
    def _extract_team_consensus(self, text: str) -> str:
        """提取团队共识度"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["高度一致", "完全一致", "强烈共识"]):
            return "高度共识"
        elif any(word in text_lower for word in ["基本一致", "大体一致", "较好共识"]):
            return "基本共识"
        elif any(word in text_lower for word in ["分歧较大", "意见不一", "缺乏共识"]):
            return "分歧较大"
        else:
            return "部分共识"
    
    def _extract_contingency_measures(self, text: str) -> List[str]:
        """提取应急措施"""
        measures = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["应急", "预案", "备选", "替代"]):
                measure = line.strip()
                if measure and len(measure) > 10:
                    measures.append(measure)
        
        return measures[:3]  # 最多返回3个应急措施
