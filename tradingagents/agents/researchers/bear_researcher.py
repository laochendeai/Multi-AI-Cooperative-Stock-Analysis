"""
空头研究员 - 专注于识别投资风险和看跌因素
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)

class BearResearcher(BaseAgent):
    """空头研究员 - 看跌风险和威胁评估"""
    
    def __init__(self, llm_client=None, memory_manager=None):
        super().__init__(
            agent_id="bear_researcher",
            agent_type="空头研究员",
            llm_client=llm_client,
            memory_manager=memory_manager
        )
        self.debate_history = []
    
    async def analyze(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行空头研究分析
        
        Args:
            input_data: 包含分析师报告、市场数据等
            context: 上下文信息
            
        Returns:
            空头研究结果
        """
        try:
            symbol = input_data.get("symbol", "")
            analyst_reports = input_data.get("analyst_reports", [])
            market_data = input_data.get("market_data", {})
            debate_context = context.get("debate_context", {})
            
            # 构建空头分析提示
            analysis_prompt = self._build_bear_prompt(symbol, analyst_reports, market_data, debate_context)
            
            # 获取LLM分析
            llm_response = await self.get_llm_response(analysis_prompt, context)
            
            # 解析和结构化结果
            analysis_result = self._parse_bear_result(llm_response, symbol)
            
            # 保存辩论历史
            self.debate_history.append({
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "position": "bear",
                "arguments": analysis_result.get("key_risks", [])
            })
            
            return {
                "status": "success",
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "analysis_type": "bear_research",
                "symbol": symbol,
                "position": "bear",
                "content": analysis_result,
                "raw_response": llm_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"空头研究分析失败: {e}")
            return {
                "status": "error",
                "agent_id": self.agent_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_bear_prompt(self, symbol: str, analyst_reports: List, market_data: Dict, debate_context: Dict) -> str:
        """构建空头分析提示"""
        prompt = f"""
作为专业的空头研究员，你的任务是为股票 {symbol} 识别投资风险和看跌因素。

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
        if debate_context.get("bull_arguments"):
            prompt += f"""
多头观点 (需要质疑):
{debate_context['bull_arguments']}
"""
        
        prompt += """
作为空头研究员，请从以下角度识别风险和看跌因素:

1. **估值风险**
   - 估值过高的证据
   - 泡沫化风险
   - 估值回归压力

2. **基本面恶化**
   - 业绩下滑风险
   - 财务状况恶化
   - 竞争地位削弱

3. **行业和宏观风险**
   - 行业周期下行
   - 政策不利因素
   - 宏观环境恶化

4. **技术面风险**
   - 技术指标恶化
   - 趋势反转信号
   - 支撑位破位风险

5. **流动性和情绪风险**
   - 市场情绪转变
   - 资金流出压力
   - 投资者信心下降

6. **特定风险因素**
   - 公司治理问题
   - 监管风险
   - 黑天鹅事件

请提供有说服力的空头论据，重点关注可能导致股价下跌的具体风险。
"""
        
        return prompt
    
    def _parse_bear_result(self, llm_response: str, symbol: str) -> Dict[str, Any]:
        """解析空头研究结果"""
        try:
            result = {
                "symbol": symbol,
                "bear_summary": llm_response,
                "risk_thesis": self._extract_risk_thesis(llm_response),
                "key_risks": self._extract_key_risks(llm_response),
                "valuation_concerns": self._extract_valuation_concerns(llm_response),
                "fundamental_weaknesses": self._extract_fundamental_weaknesses(llm_response),
                "technical_warnings": self._extract_technical_warnings(llm_response),
                "downside_catalysts": self._extract_downside_catalysts(llm_response),
                "target_downside": self._extract_target_downside(llm_response),
                "risk_severity": self._calculate_risk_severity(llm_response),
                "probability_assessment": self._assess_probability(llm_response)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"解析空头研究结果失败: {e}")
            return {
                "symbol": symbol,
                "bear_summary": llm_response,
                "risk_thesis": "看跌",
                "risk_severity": 0.6
            }
    
    def _extract_risk_thesis(self, text: str) -> str:
        """提取风险主题"""
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line for keyword in ["风险主题", "核心风险", "主要担忧"]):
                return line.strip()
        
        # 如果没有明确的风险主题，提取第一段作为主题
        paragraphs = text.split('\n\n')
        if paragraphs:
            return paragraphs[0][:200] + "..." if len(paragraphs[0]) > 200 else paragraphs[0]
        
        return "基于多重风险因素的看跌判断"
    
    def _extract_key_risks(self, text: str) -> List[str]:
        """提取关键风险"""
        risks = []
        lines = text.split('\n')
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 识别风险相关的段落
            if any(keyword in line for keyword in ["风险", "威胁", "担忧", "问题", "隐患"]):
                current_section = "risk"
            elif line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•')):
                if current_section == "risk":
                    risks.append(line)
            elif current_section == "risk" and len(line) > 20:
                risks.append(line)
        
        return risks[:5]  # 最多返回5个关键风险
    
    def _extract_valuation_concerns(self, text: str) -> List[str]:
        """提取估值担忧"""
        concerns = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["估值", "高估", "泡沫", "价格过高"]):
                concern = line.strip()
                if concern and len(concern) > 10:
                    concerns.append(concern)
        
        return concerns[:3]  # 最多返回3个估值担忧
    
    def _extract_fundamental_weaknesses(self, text: str) -> List[str]:
        """提取基本面弱点"""
        weaknesses = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["基本面", "财务", "业绩", "盈利", "收入"]):
                if any(negative in line for negative in ["下滑", "恶化", "减少", "亏损", "问题"]):
                    weakness = line.strip()
                    if weakness and len(weakness) > 10:
                        weaknesses.append(weakness)
        
        return weaknesses[:3]  # 最多返回3个基本面弱点
    
    def _extract_technical_warnings(self, text: str) -> List[str]:
        """提取技术面警告"""
        warnings = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["技术", "图表", "趋势", "支撑", "阻力"]):
                if any(negative in line for negative in ["破位", "下跌", "恶化", "转向", "信号"]):
                    warning = line.strip()
                    if warning and len(warning) > 10:
                        warnings.append(warning)
        
        return warnings[:3]  # 最多返回3个技术面警告
    
    def _extract_downside_catalysts(self, text: str) -> List[str]:
        """提取下跌催化剂"""
        catalysts = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["催化", "触发", "导致", "引发"]):
                if any(negative in line for negative in ["下跌", "下降", "恶化", "危机"]):
                    catalyst = line.strip()
                    if catalyst and len(catalyst) > 10:
                        catalysts.append(catalyst)
        
        return catalysts[:3]  # 最多返回3个下跌催化剂
    
    def _extract_target_downside(self, text: str) -> str:
        """提取目标下跌幅度"""
        import re
        
        # 查找下跌相关的数字
        downside_patterns = [
            r'下跌[：:]\s*(\d+\.?\d*)%',
            r'跌幅[：:]\s*(\d+\.?\d*)%',
            r'目标下跌[：:]\s*(\d+\.?\d*)%'
        ]
        
        for pattern in downside_patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)}%"
        
        return "待评估"
    
    def _calculate_risk_severity(self, text: str) -> float:
        """计算风险严重程度"""
        text_lower = text.lower()
        
        # 高风险指标
        high_risk = ["严重", "重大", "危险", "崩盘", "暴跌", "危机"]
        # 低风险指标
        low_risk = ["轻微", "有限", "可控", "温和", "小幅"]
        
        high_count = sum(1 for word in high_risk if word in text_lower)
        low_count = sum(1 for word in low_risk if word in text_lower)
        
        base_severity = 0.6  # 空头研究员基础风险评估较高
        severity_boost = high_count * 0.1
        severity_penalty = low_count * 0.1
        
        severity = max(0.3, min(0.9, base_severity + severity_boost - severity_penalty))
        return round(severity, 2)
    
    def _assess_probability(self, text: str) -> float:
        """评估风险发生概率"""
        text_lower = text.lower()
        
        # 高概率指标
        high_prob = ["很可能", "极有可能", "必然", "确定", "明确"]
        # 低概率指标
        low_prob = ["不太可能", "可能性较小", "不确定", "或许", "也许"]
        
        high_count = sum(1 for word in high_prob if word in text_lower)
        low_count = sum(1 for word in low_prob if word in text_lower)
        
        base_probability = 0.5
        prob_boost = high_count * 0.1
        prob_penalty = low_count * 0.1
        
        probability = max(0.2, min(0.8, base_probability + prob_boost - prob_penalty))
        return round(probability, 2)
    
    async def participate_debate(self, debate_round: int, bull_arguments: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """参与辩论"""
        try:
            symbol = context.get("symbol", "")
            
            debate_prompt = f"""
这是第 {debate_round} 轮投资辩论，针对股票 {symbol}。

多头研究员的论据:
"""
            for i, arg in enumerate(bull_arguments, 1):
                debate_prompt += f"{i}. {arg}\n"
            
            debate_prompt += """
作为空头研究员，请针对多头论据进行质疑，并强化你的看跌观点:

1. **论据质疑**
   - 质疑多头论据的合理性
   - 指出论据中的漏洞和风险

2. **风险强化**
   - 强化你识别的关键风险
   - 提供新的风险证据

3. **反向论证**
   - 从相反角度解读多头提到的利好
   - 说明利好因素的局限性

请保持专业和客观，重点关注风险识别和防范。
"""
            
            llm_response = await self.get_llm_response(debate_prompt, context)
            
            return {
                "status": "success",
                "agent_id": self.agent_id,
                "debate_round": debate_round,
                "position": "bear",
                "response": llm_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"空头辩论参与失败: {e}")
            return {
                "status": "error",
                "agent_id": self.agent_id,
                "error": str(e)
            }
