"""
激进分析师 - 倡导高风险高回报策略
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)

class AggressiveDebator(BaseAgent):
    """激进分析师 - 高风险高回报策略倡导者"""
    
    def __init__(self, llm_client=None, memory_manager=None):
        super().__init__(
            agent_id="aggressive_debator",
            agent_type="激进分析师",
            llm_client=llm_client,
            memory_manager=memory_manager
        )
    
    async def analyze(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行激进风险分析
        
        Args:
            input_data: 包含交易策略、市场数据等
            context: 上下文信息
            
        Returns:
            激进分析结果
        """
        try:
            symbol = input_data.get("symbol", "")
            trading_strategy = input_data.get("trading_strategy", {})
            market_conditions = input_data.get("market_conditions", {})
            
            # 构建激进分析提示
            analysis_prompt = self._build_aggressive_prompt(symbol, trading_strategy, market_conditions)
            
            # 获取LLM分析
            llm_response = await self.get_llm_response(analysis_prompt, context)
            
            # 解析和结构化结果
            analysis_result = self._parse_aggressive_result(llm_response, symbol)
            
            return {
                "status": "success",
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "analysis_type": "aggressive_risk_analysis",
                "symbol": symbol,
                "stance": "aggressive",
                "content": analysis_result,
                "raw_response": llm_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"激进分析失败: {e}")
            return {
                "status": "error",
                "agent_id": self.agent_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_aggressive_prompt(self, symbol: str, trading_strategy: Dict, market_conditions: Dict) -> str:
        """构建激进分析提示"""
        prompt = f"""
作为激进分析师，你倡导高风险高回报的投资策略。请对股票 {symbol} 的交易策略进行激进风险评估。

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

作为激进分析师，请从以下角度进行分析:

1. **机会最大化**
   - 当前策略是否充分利用了市场机会
   - 是否存在更激进的获利机会
   - 仓位是否过于保守

2. **风险承受能力**
   - 当前风险设定是否过于保守
   - 在可承受范围内是否可以承担更多风险
   - 风险收益比是否最优

3. **时机把握**
   - 当前是否是激进投资的好时机
   - 市场波动是否提供了更好的机会
   - 是否应该加大投资力度

4. **策略优化建议**
   - 如何提高仓位以获得更高收益
   - 如何利用杠杆或衍生品放大收益
   - 如何在风险可控下追求最大化收益

5. **竞争优势**
   - 激进策略相比保守策略的优势
   - 在当前市场环境下的胜率分析
   - 错过机会的机会成本

6. **执行建议**
   - 具体的激进操作建议
   - 风险控制的底线
   - 激进策略的执行要点

请提供有说服力的激进观点，但要确保风险在可控范围内。
"""
        
        return prompt
    
    def _parse_aggressive_result(self, llm_response: str, symbol: str) -> Dict[str, Any]:
        """解析激进分析结果"""
        try:
            result = {
                "symbol": symbol,
                "aggressive_summary": llm_response,
                "opportunity_assessment": self._extract_opportunity_assessment(llm_response),
                "risk_appetite": self._extract_risk_appetite(llm_response),
                "position_recommendation": self._extract_position_recommendation(llm_response),
                "leverage_suggestion": self._extract_leverage_suggestion(llm_response),
                "timing_advantage": self._extract_timing_advantage(llm_response),
                "competitive_edge": self._extract_competitive_edge(llm_response),
                "execution_tactics": self._extract_execution_tactics(llm_response),
                "aggressiveness_score": self._calculate_aggressiveness_score(llm_response),
                "risk_tolerance": self._extract_risk_tolerance(llm_response)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"解析激进分析结果失败: {e}")
            return {
                "symbol": symbol,
                "aggressive_summary": llm_response,
                "aggressiveness_score": 0.7
            }
    
    def _extract_opportunity_assessment(self, text: str) -> str:
        """提取机会评估"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["巨大机会", "绝佳时机", "千载难逢"]):
            return "极佳机会"
        elif any(word in text_lower for word in ["良好机会", "不错时机", "值得把握"]):
            return "良好机会"
        elif any(word in text_lower for word in ["一般机会", "普通时机"]):
            return "一般机会"
        else:
            return "机会有限"
    
    def _extract_risk_appetite(self, text: str) -> str:
        """提取风险偏好"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["高风险", "激进", "大胆", "冒险"]):
            return "高风险偏好"
        elif any(word in text_lower for word in ["中等风险", "适度", "平衡"]):
            return "中等风险偏好"
        else:
            return "相对保守"
    
    def _extract_position_recommendation(self, text: str) -> str:
        """提取仓位建议"""
        import re
        
        # 查找仓位建议
        position_patterns = [
            r'建议仓位[：:]\s*(\d+\.?\d*)%',
            r'仓位[：:]\s*(\d+\.?\d*)%',
            r'增加到[：:]\s*(\d+\.?\d*)%'
        ]
        
        for pattern in position_patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)}%"
        
        # 根据文本内容推断
        text_lower = text.lower()
        if any(word in text_lower for word in ["满仓", "重仓", "大仓位"]):
            return "30-50%"
        elif any(word in text_lower for word in ["加仓", "增仓", "提高仓位"]):
            return "20-30%"
        else:
            return "维持当前"
    
    def _extract_leverage_suggestion(self, text: str) -> str:
        """提取杠杆建议"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["杠杆", "融资", "放大"]):
            if any(word in text_lower for word in ["2倍", "双倍"]):
                return "2倍杠杆"
            elif any(word in text_lower for word in ["3倍", "三倍"]):
                return "3倍杠杆"
            else:
                return "适度杠杆"
        else:
            return "无杠杆"
    
    def _extract_timing_advantage(self, text: str) -> str:
        """提取时机优势"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["绝佳时机", "最佳时机", "完美时机"]):
            return "绝佳时机"
        elif any(word in text_lower for word in ["良好时机", "不错时机"]):
            return "良好时机"
        elif any(word in text_lower for word in ["一般时机", "普通时机"]):
            return "一般时机"
        else:
            return "时机不佳"
    
    def _extract_competitive_edge(self, text: str) -> List[str]:
        """提取竞争优势"""
        edges = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["优势", "胜率", "竞争力", "领先"]):
                edge = line.strip()
                if edge and len(edge) > 10:
                    edges.append(edge)
        
        return edges[:3]  # 最多返回3个竞争优势
    
    def _extract_execution_tactics(self, text: str) -> List[str]:
        """提取执行策略"""
        tactics = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["执行", "操作", "策略", "建议"]):
                tactic = line.strip()
                if tactic and len(tactic) > 15:
                    tactics.append(tactic)
        
        return tactics[:4]  # 最多返回4个执行策略
    
    def _calculate_aggressiveness_score(self, text: str) -> float:
        """计算激进程度分数"""
        text_lower = text.lower()
        
        # 激进指标
        aggressive_words = ["激进", "大胆", "冒险", "高风险", "满仓", "杠杆", "最大化"]
        # 保守指标
        conservative_words = ["保守", "谨慎", "稳健", "控制", "降低", "减少"]
        
        aggressive_count = sum(1 for word in aggressive_words if word in text_lower)
        conservative_count = sum(1 for word in conservative_words if word in text_lower)
        
        base_score = 0.7  # 激进分析师基础分数较高
        score_boost = aggressive_count * 0.05
        score_penalty = conservative_count * 0.05
        
        score = max(0.5, min(0.95, base_score + score_boost - score_penalty))
        return round(score, 2)
    
    def _extract_risk_tolerance(self, text: str) -> str:
        """提取风险容忍度"""
        import re
        
        # 查找风险容忍度数字
        tolerance_patterns = [
            r'风险容忍[：:]\s*(\d+\.?\d*)%',
            r'最大亏损[：:]\s*(\d+\.?\d*)%',
            r'风险上限[：:]\s*(\d+\.?\d*)%'
        ]
        
        for pattern in tolerance_patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)}%"
        
        # 根据激进程度推断
        text_lower = text.lower()
        if any(word in text_lower for word in ["高风险", "大胆", "激进"]):
            return "15-20%"
        elif any(word in text_lower for word in ["中等风险", "适度"]):
            return "10-15%"
        else:
            return "5-10%"
