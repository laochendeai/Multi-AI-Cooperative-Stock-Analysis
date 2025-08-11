"""
保守分析师 - 强调风险控制和稳健策略
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ConservativeDebator(BaseAgent):
    """保守分析师 - 风险控制和稳健策略倡导者"""
    
    def __init__(self, llm_client=None, memory_manager=None):
        super().__init__(
            agent_id="conservative_debator",
            agent_type="保守分析师",
            llm_client=llm_client,
            memory_manager=memory_manager
        )
    
    async def analyze(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行保守风险分析
        
        Args:
            input_data: 包含交易策略、市场数据等
            context: 上下文信息
            
        Returns:
            保守分析结果
        """
        try:
            symbol = input_data.get("symbol", "")
            trading_strategy = input_data.get("trading_strategy", {})
            market_conditions = input_data.get("market_conditions", {})
            
            # 构建保守分析提示
            analysis_prompt = self._build_conservative_prompt(symbol, trading_strategy, market_conditions)
            
            # 获取LLM分析
            llm_response = await self.get_llm_response(analysis_prompt, context)
            
            # 解析和结构化结果
            analysis_result = self._parse_conservative_result(llm_response, symbol)
            
            return {
                "status": "success",
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "analysis_type": "conservative_risk_analysis",
                "symbol": symbol,
                "stance": "conservative",
                "content": analysis_result,
                "raw_response": llm_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"保守分析失败: {e}")
            return {
                "status": "error",
                "agent_id": self.agent_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_conservative_prompt(self, symbol: str, trading_strategy: Dict, market_conditions: Dict) -> str:
        """构建保守分析提示"""
        prompt = f"""
作为保守分析师，你强调风险控制和稳健投资策略。请对股票 {symbol} 的交易策略进行保守风险评估。

当前交易策略:
- 交易行动: {trading_strategy.get('trading_action', 'N/A')}
- 建议仓位: {trading_strategy.get('position_size', 'N/A')}
- 预期收益: {trading_strategy.get('expected_return', 'N/A')}
- 最大风险: {trading_strategy.get('max_risk', 'N/A')}
- 策略理由: {trading_strategy.get('strategy_rationale', 'N/A')}

市场环境:
- 市场趋势: {market_conditions.get('market_trend', 'N/A')}
- 波动率: {market_conditions.get('volatility', 'N/A')}
- 流动性: {market_conditions.get('liquidity', 'N/A')}
- 市场情绪: {market_conditions.get('sentiment', 'N/A')}

作为保守分析师，请从以下角度进行分析:

1. **风险识别**
   - 当前策略存在的主要风险点
   - 市场环境中的潜在威胁
   - 不确定性因素分析

2. **风险控制评估**
   - 当前风险控制措施是否充分
   - 止损设置是否合理
   - 仓位大小是否过于激进

3. **稳健性分析**
   - 策略在不利情况下的表现
   - 最坏情况下的损失评估
   - 策略的抗风险能力

4. **保守化建议**
   - 如何降低投资风险
   - 更稳健的仓位建议
   - 更严格的风险控制措施

5. **安全边际**
   - 当前安全边际是否足够
   - 如何增加安全缓冲
   - 防御性措施建议

6. **长期稳定性**
   - 策略的长期可持续性
   - 资本保护的重要性
   - 稳健收益vs高风险收益

请提供谨慎、稳健的风险评估，优先考虑资本保护。
"""
        
        return prompt
    
    def _parse_conservative_result(self, llm_response: str, symbol: str) -> Dict[str, Any]:
        """解析保守分析结果"""
        try:
            result = {
                "symbol": symbol,
                "conservative_summary": llm_response,
                "risk_identification": self._extract_risk_identification(llm_response),
                "risk_control_assessment": self._extract_risk_control_assessment(llm_response),
                "stability_analysis": self._extract_stability_analysis(llm_response),
                "conservative_recommendations": self._extract_conservative_recommendations(llm_response),
                "safety_margin": self._extract_safety_margin(llm_response),
                "capital_protection": self._extract_capital_protection(llm_response),
                "risk_warnings": self._extract_risk_warnings(llm_response),
                "conservatism_score": self._calculate_conservatism_score(llm_response),
                "recommended_position": self._extract_recommended_position(llm_response)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"解析保守分析结果失败: {e}")
            return {
                "symbol": symbol,
                "conservative_summary": llm_response,
                "conservatism_score": 0.8
            }
    
    def _extract_risk_identification(self, text: str) -> List[str]:
        """提取风险识别"""
        risks = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["风险", "威胁", "危险", "隐患"]):
                risk = line.strip()
                if risk and len(risk) > 10:
                    risks.append(risk)
        
        return risks[:5]  # 最多返回5个风险点
    
    def _extract_risk_control_assessment(self, text: str) -> str:
        """提取风险控制评估"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["不足", "不够", "需要加强", "有待改善"]):
            return "风险控制不足"
        elif any(word in text_lower for word in ["充分", "足够", "良好", "完善"]):
            return "风险控制充分"
        else:
            return "风险控制一般"
    
    def _extract_stability_analysis(self, text: str) -> str:
        """提取稳定性分析"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["稳定性强", "稳健", "可靠"]):
            return "稳定性良好"
        elif any(word in text_lower for word in ["稳定性差", "不稳定", "波动大"]):
            return "稳定性较差"
        else:
            return "稳定性一般"
    
    def _extract_conservative_recommendations(self, text: str) -> List[str]:
        """提取保守建议"""
        recommendations = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["建议", "应该", "需要", "可以"]):
                if any(conservative in line for conservative in ["降低", "减少", "控制", "谨慎"]):
                    recommendation = line.strip()
                    if recommendation and len(recommendation) > 10:
                        recommendations.append(recommendation)
        
        return recommendations[:4]  # 最多返回4个保守建议
    
    def _extract_safety_margin(self, text: str) -> str:
        """提取安全边际"""
        import re
        
        # 查找安全边际相关数字
        margin_patterns = [
            r'安全边际[：:]\s*(\d+\.?\d*)%',
            r'安全缓冲[：:]\s*(\d+\.?\d*)%',
            r'保护垫[：:]\s*(\d+\.?\d*)%'
        ]
        
        for pattern in margin_patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)}%"
        
        # 根据保守程度推断
        text_lower = text.lower()
        if any(word in text_lower for word in ["充足", "足够", "良好"]):
            return "充足"
        elif any(word in text_lower for word in ["不足", "需要", "应该"]):
            return "不足"
        else:
            return "一般"
    
    def _extract_capital_protection(self, text: str) -> List[str]:
        """提取资本保护措施"""
        protections = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["保护", "防护", "防御", "保全"]):
                protection = line.strip()
                if protection and len(protection) > 10:
                    protections.append(protection)
        
        return protections[:3]  # 最多返回3个保护措施
    
    def _extract_risk_warnings(self, text: str) -> List[str]:
        """提取风险警告"""
        warnings = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["警告", "注意", "小心", "提醒"]):
                warning = line.strip()
                if warning and len(warning) > 10:
                    warnings.append(warning)
        
        return warnings[:3]  # 最多返回3个风险警告
    
    def _calculate_conservatism_score(self, text: str) -> float:
        """计算保守程度分数"""
        text_lower = text.lower()
        
        # 保守指标
        conservative_words = ["保守", "谨慎", "稳健", "控制", "降低", "减少", "安全"]
        # 激进指标
        aggressive_words = ["激进", "大胆", "冒险", "高风险", "增加", "提高"]
        
        conservative_count = sum(1 for word in conservative_words if word in text_lower)
        aggressive_count = sum(1 for word in aggressive_words if word in text_lower)
        
        base_score = 0.8  # 保守分析师基础分数较高
        score_boost = conservative_count * 0.03
        score_penalty = aggressive_count * 0.05
        
        score = max(0.6, min(0.95, base_score + score_boost - score_penalty))
        return round(score, 2)
    
    def _extract_recommended_position(self, text: str) -> str:
        """提取推荐仓位"""
        import re
        
        # 查找仓位建议
        position_patterns = [
            r'建议仓位[：:]\s*(\d+\.?\d*)%',
            r'仓位[：:]\s*(\d+\.?\d*)%',
            r'降低到[：:]\s*(\d+\.?\d*)%'
        ]
        
        for pattern in position_patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)}%"
        
        # 根据文本内容推断
        text_lower = text.lower()
        if any(word in text_lower for word in ["轻仓", "小仓位", "降低仓位"]):
            return "5-10%"
        elif any(word in text_lower for word in ["适度", "中等仓位"]):
            return "10-15%"
        elif any(word in text_lower for word in ["观望", "暂停", "等待"]):
            return "0%"
        else:
            return "维持当前"
