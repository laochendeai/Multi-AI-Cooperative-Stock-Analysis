"""
中性分析师 - 提供平衡观点和中庸策略
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)

class NeutralDebator(BaseAgent):
    """中性分析师 - 平衡观点和中庸策略倡导者"""
    
    def __init__(self, llm_client=None, memory_manager=None):
        super().__init__(
            agent_id="neutral_debator",
            agent_type="中性分析师",
            llm_client=llm_client,
            memory_manager=memory_manager
        )
    
    async def analyze(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行中性风险分析
        
        Args:
            input_data: 包含交易策略、激进和保守观点等
            context: 上下文信息
            
        Returns:
            中性分析结果
        """
        try:
            symbol = input_data.get("symbol", "")
            trading_strategy = input_data.get("trading_strategy", {})
            aggressive_view = input_data.get("aggressive_view", {})
            conservative_view = input_data.get("conservative_view", {})
            
            # 构建中性分析提示
            analysis_prompt = self._build_neutral_prompt(symbol, trading_strategy, aggressive_view, conservative_view)
            
            # 获取LLM分析
            llm_response = await self.get_llm_response(analysis_prompt, context)
            
            # 解析和结构化结果
            analysis_result = self._parse_neutral_result(llm_response, symbol)
            
            return {
                "status": "success",
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "analysis_type": "neutral_risk_analysis",
                "symbol": symbol,
                "stance": "neutral",
                "content": analysis_result,
                "raw_response": llm_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"中性分析失败: {e}")
            return {
                "status": "error",
                "agent_id": self.agent_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_neutral_prompt(self, symbol: str, trading_strategy: Dict, aggressive_view: Dict, conservative_view: Dict) -> str:
        """构建中性分析提示"""
        prompt = f"""
作为中性分析师，你需要在激进和保守观点之间寻找平衡，为股票 {symbol} 提供客观、中庸的风险评估。

当前交易策略:
- 交易行动: {trading_strategy.get('trading_action', 'N/A')}
- 建议仓位: {trading_strategy.get('position_size', 'N/A')}
- 预期收益: {trading_strategy.get('expected_return', 'N/A')}
- 最大风险: {trading_strategy.get('max_risk', 'N/A')}

激进分析师观点:
- 机会评估: {aggressive_view.get('opportunity_assessment', 'N/A')}
- 仓位建议: {aggressive_view.get('position_recommendation', 'N/A')}
- 激进程度: {aggressive_view.get('aggressiveness_score', 'N/A')}
- 主要论据: {aggressive_view.get('competitive_edge', [])}

保守分析师观点:
- 风险识别: {conservative_view.get('risk_identification', [])}
- 仓位建议: {conservative_view.get('recommended_position', 'N/A')}
- 保守程度: {conservative_view.get('conservatism_score', 'N/A')}
- 主要担忧: {conservative_view.get('risk_warnings', [])}

作为中性分析师，请从以下角度进行平衡分析:

1. **观点平衡**
   - 激进和保守观点的合理性评估
   - 两种观点的优缺点分析
   - 寻找中间立场的可能性

2. **风险收益平衡**
   - 在风险和收益之间找到最佳平衡点
   - 评估当前策略的风险收益比
   - 提出平衡的调整建议

3. **情景分析**
   - 不同市场情景下的策略表现
   - 牛市、熊市、震荡市的应对策略
   - 策略的适应性评估

4. **中庸策略建议**
   - 既不过于激进也不过于保守的策略
   - 适度的仓位和风险控制建议
   - 灵活调整的机制设计

5. **综合评估**
   - 对当前策略的客观评价
   - 策略优化的具体建议
   - 执行中的注意事项

6. **决策支持**
   - 为最终决策提供平衡的参考
   - 关键决策点的权衡分析
   - 实用的执行指导

请提供客观、平衡的分析，避免极端观点，寻求最优的中庸之道。
"""
        
        return prompt
    
    def _parse_neutral_result(self, llm_response: str, symbol: str) -> Dict[str, Any]:
        """解析中性分析结果"""
        try:
            result = {
                "symbol": symbol,
                "neutral_summary": llm_response,
                "balance_assessment": self._extract_balance_assessment(llm_response),
                "risk_reward_balance": self._extract_risk_reward_balance(llm_response),
                "scenario_analysis": self._extract_scenario_analysis(llm_response),
                "moderate_recommendations": self._extract_moderate_recommendations(llm_response),
                "comprehensive_evaluation": self._extract_comprehensive_evaluation(llm_response),
                "decision_support": self._extract_decision_support(llm_response),
                "balanced_position": self._extract_balanced_position(llm_response),
                "neutrality_score": self._calculate_neutrality_score(llm_response),
                "flexibility_rating": self._extract_flexibility_rating(llm_response)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"解析中性分析结果失败: {e}")
            return {
                "symbol": symbol,
                "neutral_summary": llm_response,
                "neutrality_score": 0.5
            }
    
    def _extract_balance_assessment(self, text: str) -> str:
        """提取平衡评估"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["平衡良好", "观点均衡", "合理平衡"]):
            return "观点平衡"
        elif any(word in text_lower for word in ["偏向激进", "过于乐观"]):
            return "偏向激进"
        elif any(word in text_lower for word in ["偏向保守", "过于谨慎"]):
            return "偏向保守"
        else:
            return "需要平衡"
    
    def _extract_risk_reward_balance(self, text: str) -> str:
        """提取风险收益平衡"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["风险收益平衡", "比例合理", "平衡良好"]):
            return "平衡合理"
        elif any(word in text_lower for word in ["风险过高", "收益不足"]):
            return "风险偏高"
        elif any(word in text_lower for word in ["风险过低", "收益有限"]):
            return "过于保守"
        else:
            return "需要调整"
    
    def _extract_scenario_analysis(self, text: str) -> Dict[str, str]:
        """提取情景分析"""
        scenarios = {}
        
        # 牛市情景
        if "牛市" in text.lower():
            if any(word in text.lower() for word in ["表现良好", "适合", "有利"]):
                scenarios["bull_market"] = "表现良好"
            else:
                scenarios["bull_market"] = "表现一般"
        
        # 熊市情景
        if "熊市" in text.lower():
            if any(word in text.lower() for word in ["抗跌", "防御", "稳健"]):
                scenarios["bear_market"] = "抗跌能力强"
            else:
                scenarios["bear_market"] = "需要防御"
        
        # 震荡市情景
        if "震荡" in text.lower():
            if any(word in text.lower() for word in ["适应", "灵活", "稳定"]):
                scenarios["sideways_market"] = "适应性强"
            else:
                scenarios["sideways_market"] = "需要调整"
        
        return scenarios
    
    def _extract_moderate_recommendations(self, text: str) -> List[str]:
        """提取中庸建议"""
        recommendations = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["建议", "可以", "应该", "考虑"]):
                if any(moderate in line for moderate in ["适度", "平衡", "中等", "合理"]):
                    recommendation = line.strip()
                    if recommendation and len(recommendation) > 10:
                        recommendations.append(recommendation)
        
        return recommendations[:4]  # 最多返回4个中庸建议
    
    def _extract_comprehensive_evaluation(self, text: str) -> str:
        """提取综合评估"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["策略合理", "整体良好", "可以接受"]):
            return "策略合理"
        elif any(word in text_lower for word in ["需要调整", "有待改进", "可以优化"]):
            return "需要优化"
        elif any(word in text_lower for word in ["风险较大", "不够稳健", "过于激进"]):
            return "风险偏高"
        else:
            return "中性评价"
    
    def _extract_decision_support(self, text: str) -> List[str]:
        """提取决策支持"""
        supports = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["决策", "选择", "权衡", "考虑"]):
                support = line.strip()
                if support and len(support) > 15:
                    supports.append(support)
        
        return supports[:3]  # 最多返回3个决策支持
    
    def _extract_balanced_position(self, text: str) -> str:
        """提取平衡仓位建议"""
        import re
        
        # 查找仓位建议
        position_patterns = [
            r'平衡仓位[：:]\s*(\d+\.?\d*)%',
            r'建议仓位[：:]\s*(\d+\.?\d*)%',
            r'中等仓位[：:]\s*(\d+\.?\d*)%'
        ]
        
        for pattern in position_patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)}%"
        
        # 根据文本内容推断
        text_lower = text.lower()
        if any(word in text_lower for word in ["中等仓位", "适度仓位", "平衡仓位"]):
            return "15-20%"
        elif any(word in text_lower for word in ["轻仓", "小仓位"]):
            return "10-15%"
        elif any(word in text_lower for word in ["标准仓位", "正常仓位"]):
            return "20-25%"
        else:
            return "根据情况调整"
    
    def _calculate_neutrality_score(self, text: str) -> float:
        """计算中性程度分数"""
        text_lower = text.lower()
        
        # 中性指标
        neutral_words = ["平衡", "中性", "中庸", "适度", "合理", "客观"]
        # 极端指标
        extreme_words = ["激进", "保守", "极端", "过度", "过于"]
        
        neutral_count = sum(1 for word in neutral_words if word in text_lower)
        extreme_count = sum(1 for word in extreme_words if word in text_lower)
        
        base_score = 0.5  # 中性分析师基础分数
        score_boost = neutral_count * 0.05
        score_penalty = extreme_count * 0.03
        
        score = max(0.3, min(0.7, base_score + score_boost - score_penalty))
        return round(score, 2)
    
    def _extract_flexibility_rating(self, text: str) -> str:
        """提取灵活性评级"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["高度灵活", "非常灵活", "灵活性强"]):
            return "高灵活性"
        elif any(word in text_lower for word in ["适度灵活", "一般灵活"]):
            return "中等灵活性"
        elif any(word in text_lower for word in ["灵活性差", "不够灵活", "僵化"]):
            return "低灵活性"
        else:
            return "灵活性一般"
