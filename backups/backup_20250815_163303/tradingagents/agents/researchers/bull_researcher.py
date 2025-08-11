"""
多头研究员 - 专注于寻找投资机会和看涨理由
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)

class BullResearcher(BaseAgent):
    """多头研究员 - 看涨观点和机会识别"""
    
    def __init__(self, llm_client=None, memory_manager=None):
        super().__init__(
            agent_id="bull_researcher",
            agent_type="多头研究员",
            llm_client=llm_client,
            memory_manager=memory_manager
        )
        self.debate_history = []
    
    async def analyze(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行多头研究分析
        
        Args:
            input_data: 包含分析师报告、市场数据等
            context: 上下文信息
            
        Returns:
            多头研究结果
        """
        try:
            symbol = input_data.get("symbol", "")
            analyst_reports = input_data.get("analyst_reports", [])
            market_data = input_data.get("market_data", {})
            debate_context = context.get("debate_context", {})
            
            # 构建多头分析提示
            analysis_prompt = self._build_bull_prompt(symbol, analyst_reports, market_data, debate_context)
            
            # 获取LLM分析
            llm_response = await self.get_llm_response(analysis_prompt, context)
            
            # 解析和结构化结果
            analysis_result = self._parse_bull_result(llm_response, symbol)
            
            # 保存辩论历史
            self.debate_history.append({
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "position": "bull",
                "arguments": analysis_result.get("key_arguments", [])
            })
            
            return {
                "status": "success",
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "analysis_type": "bull_research",
                "symbol": symbol,
                "position": "bull",
                "content": analysis_result,
                "raw_response": llm_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"多头研究分析失败: {e}")
            return {
                "status": "error",
                "agent_id": self.agent_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_bull_prompt(self, symbol: str, analyst_reports: List, market_data: Dict, debate_context: Dict) -> str:
        """构建多头分析提示"""
        prompt = f"""
作为专业的多头研究员，你的任务是为股票 {symbol} 寻找投资机会和看涨理由。

分析师报告摘要:
"""
        
        # 添加分析师报告
        for i, report in enumerate(analyst_reports[:4], 1):
            prompt += f"""
报告 {i} ({report.get('analyst_type', 'N/A')}):
- 结论: {report.get('conclusion', 'N/A')}
- 关键发现: {report.get('key_findings', 'N/A')}
- 风险提示: {report.get('risks', 'N/A')}
"""
        
        prompt += f"""
市场数据:
- 当前价格: {market_data.get('current_price', 'N/A')}
- 52周高点: {market_data.get('week_52_high', 'N/A')}
- 52周低点: {market_data.get('week_52_low', 'N/A')}
- 市盈率: {market_data.get('pe_ratio', 'N/A')}
- 市净率: {market_data.get('pb_ratio', 'N/A')}
"""
        
        # 添加辩论上下文
        if debate_context.get("bear_arguments"):
            prompt += f"""
空头观点 (需要反驳):
{debate_context['bear_arguments']}
"""
        
        prompt += """
作为多头研究员，请从以下角度构建看涨论据:

1. **价值发现**
   - 被低估的价值点
   - 市场未充分认识的优势
   - 估值修复的可能性

2. **成长机会**
   - 业务增长驱动因素
   - 新的收入来源
   - 市场扩张机会

3. **竞争优势**
   - 护城河和壁垒
   - 技术或品牌优势
   - 市场地位强化

4. **催化剂识别**
   - 短期催化事件
   - 政策利好因素
   - 行业趋势支撑

5. **风险缓解**
   - 对空头观点的反驳
   - 风险可控性分析
   - 下行保护因素

6. **投资时机**
   - 当前买入时机分析
   - 预期收益评估
   - 持有期建议

请提供有说服力的多头论据，但保持客观和理性。重点关注可量化的投资机会。
"""
        
        return prompt
    
    def _parse_bull_result(self, llm_response: str, symbol: str) -> Dict[str, Any]:
        """解析多头研究结果"""
        try:
            result = {
                "symbol": symbol,
                "bull_summary": llm_response,
                "investment_thesis": self._extract_investment_thesis(llm_response),
                "key_arguments": self._extract_key_arguments(llm_response),
                "catalysts": self._extract_catalysts(llm_response),
                "value_proposition": self._extract_value_proposition(llm_response),
                "growth_drivers": self._extract_growth_drivers(llm_response),
                "risk_mitigation": self._extract_risk_mitigation(llm_response),
                "target_return": self._extract_target_return(llm_response),
                "conviction_level": self._calculate_conviction(llm_response),
                "time_horizon": self._extract_time_horizon(llm_response)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"解析多头研究结果失败: {e}")
            return {
                "symbol": symbol,
                "bull_summary": llm_response,
                "investment_thesis": "看涨",
                "conviction_level": 0.6
            }
    
    def _extract_investment_thesis(self, text: str) -> str:
        """提取投资主题"""
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line for keyword in ["投资主题", "核心逻辑", "投资理由"]):
                return line.strip()
        
        # 如果没有明确的投资主题，提取第一段作为主题
        paragraphs = text.split('\n\n')
        if paragraphs:
            return paragraphs[0][:200] + "..." if len(paragraphs[0]) > 200 else paragraphs[0]
        
        return "基于基本面和技术面的综合看涨判断"
    
    def _extract_key_arguments(self, text: str) -> List[str]:
        """提取关键论据"""
        arguments = []
        lines = text.split('\n')
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 识别论据相关的段落
            if any(keyword in line for keyword in ["论据", "理由", "优势", "机会", "催化"]):
                current_section = "argument"
            elif line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•')):
                if current_section == "argument":
                    arguments.append(line)
            elif current_section == "argument" and len(line) > 20:
                arguments.append(line)
        
        return arguments[:5]  # 最多返回5个关键论据
    
    def _extract_catalysts(self, text: str) -> List[str]:
        """提取催化剂"""
        catalysts = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["催化", "驱动", "利好", "推动"]):
                catalyst = line.strip()
                if catalyst and len(catalyst) > 10:
                    catalysts.append(catalyst)
        
        return catalysts[:3]  # 最多返回3个催化剂
    
    def _extract_value_proposition(self, text: str) -> str:
        """提取价值主张"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["低估", "价值被低估", "估值偏低"]):
            return "价值低估"
        elif any(word in text_lower for word in ["成长", "增长潜力", "发展前景"]):
            return "成长价值"
        elif any(word in text_lower for word in ["分红", "股息", "现金流"]):
            return "收益价值"
        else:
            return "综合价值"
    
    def _extract_growth_drivers(self, text: str) -> List[str]:
        """提取增长驱动因素"""
        drivers = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["增长", "成长", "扩张", "发展"]):
                driver = line.strip()
                if driver and len(driver) > 10:
                    drivers.append(driver)
        
        return drivers[:3]  # 最多返回3个增长驱动因素
    
    def _extract_risk_mitigation(self, text: str) -> List[str]:
        """提取风险缓解措施"""
        mitigations = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["缓解", "控制", "应对", "反驳"]):
                mitigation = line.strip()
                if mitigation and len(mitigation) > 10:
                    mitigations.append(mitigation)
        
        return mitigations[:3]  # 最多返回3个风险缓解措施
    
    def _extract_target_return(self, text: str) -> str:
        """提取目标收益"""
        import re
        
        # 查找收益相关的数字
        return_patterns = [
            r'目标收益[：:]\s*(\d+\.?\d*)%',
            r'预期收益[：:]\s*(\d+\.?\d*)%',
            r'收益率[：:]\s*(\d+\.?\d*)%'
        ]
        
        for pattern in return_patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)}%"
        
        return "待评估"
    
    def _calculate_conviction(self, text: str) -> float:
        """计算投资信念强度"""
        text_lower = text.lower()
        
        # 强信念指标
        strong_conviction = ["强烈推荐", "确信", "明确", "显著", "强劲"]
        # 弱信念指标
        weak_conviction = ["谨慎", "可能", "或许", "不确定", "有限"]
        
        strong_count = sum(1 for word in strong_conviction if word in text_lower)
        weak_count = sum(1 for word in weak_conviction if word in text_lower)
        
        base_conviction = 0.6  # 多头研究员基础信念较高
        conviction_boost = strong_count * 0.1
        conviction_penalty = weak_count * 0.1
        
        conviction = max(0.3, min(0.9, base_conviction + conviction_boost - conviction_penalty))
        return round(conviction, 2)
    
    def _extract_time_horizon(self, text: str) -> str:
        """提取投资时间范围"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["长期", "长线", "战略", "持有"]):
            return "长期"
        elif any(word in text_lower for word in ["短期", "短线", "快速", "即时"]):
            return "短期"
        else:
            return "中期"
    
    async def participate_debate(self, debate_round: int, bear_arguments: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """参与辩论"""
        try:
            symbol = context.get("symbol", "")
            
            debate_prompt = f"""
这是第 {debate_round} 轮投资辩论，针对股票 {symbol}。

空头研究员的论据:
"""
            for i, arg in enumerate(bear_arguments, 1):
                debate_prompt += f"{i}. {arg}\n"
            
            debate_prompt += """
作为多头研究员，请针对空头论据进行反驳，并强化你的看涨观点:

1. **直接反驳**
   - 针对空头论据的具体反驳
   - 提供相反的证据和数据

2. **论据强化**
   - 强化你的核心看涨论据
   - 提供新的支撑证据

3. **风险重新评估**
   - 重新评估空头提到的风险
   - 说明风险的可控性

请保持专业和客观，避免情绪化的争论。
"""
            
            llm_response = await self.get_llm_response(debate_prompt, context)
            
            return {
                "status": "success",
                "agent_id": self.agent_id,
                "debate_round": debate_round,
                "position": "bull",
                "response": llm_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"多头辩论参与失败: {e}")
            return {
                "status": "error",
                "agent_id": self.agent_id,
                "error": str(e)
            }
