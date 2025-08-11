"""
基本面分析师 - 专业财务数据和基本面指标分析
"""

import logging
from typing import Dict, Any
from datetime import datetime

from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)

class FundamentalsAnalyst(BaseAgent):
    """基本面分析师"""
    
    def __init__(self, llm_client=None, memory_manager=None):
        super().__init__(
            agent_id="fundamentals_analyst",
            agent_type="基本面分析师",
            llm_client=llm_client,
            memory_manager=memory_manager
        )
    
    async def analyze(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行基本面分析
        
        Args:
            input_data: 包含股票代码、财务数据等
            context: 上下文信息
            
        Returns:
            基本面分析结果
        """
        try:
            symbol = input_data.get("symbol", "")
            financial_data = input_data.get("financial_data", {})
            company_info = input_data.get("company_info", {})
            industry_data = input_data.get("industry_data", {})
            
            # 构建分析提示
            analysis_prompt = self._build_fundamentals_prompt(symbol, financial_data, company_info, industry_data)
            
            # 获取LLM分析
            llm_response = await self.get_llm_response(analysis_prompt, context)
            
            # 解析和结构化结果
            analysis_result = self._parse_fundamentals_result(llm_response, symbol)
            
            return {
                "status": "success",
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "analysis_type": "fundamentals_analysis",
                "symbol": symbol,
                "content": analysis_result,
                "raw_response": llm_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"基本面分析失败: {e}")
            return {
                "status": "error",
                "agent_id": self.agent_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_fundamentals_prompt(self, symbol: str, financial_data: Dict, company_info: Dict, industry_data: Dict) -> str:
        """构建基本面分析提示"""
        prompt = f"""
作为专业的基本面分析师，请对股票 {symbol} 进行全面的基本面分析。

公司基本信息:
- 公司名称: {company_info.get('company_name', 'N/A')}
- 所属行业: {company_info.get('industry', 'N/A')}
- 市值: {company_info.get('market_cap', 'N/A')}
- 员工数: {company_info.get('employees', 'N/A')}
- 成立时间: {company_info.get('founded', 'N/A')}

财务数据:
- 总收入: {financial_data.get('revenue', 'N/A')}
- 净利润: {financial_data.get('net_income', 'N/A')}
- 总资产: {financial_data.get('total_assets', 'N/A')}
- 总负债: {financial_data.get('total_debt', 'N/A')}
- 股东权益: {financial_data.get('shareholders_equity', 'N/A')}
- 现金流: {financial_data.get('cash_flow', 'N/A')}

关键财务比率:
- PE比率: {financial_data.get('pe_ratio', 'N/A')}
- PB比率: {financial_data.get('pb_ratio', 'N/A')}
- ROE: {financial_data.get('roe', 'N/A')}%
- ROA: {financial_data.get('roa', 'N/A')}%
- 毛利率: {financial_data.get('gross_margin', 'N/A')}%
- 净利率: {financial_data.get('net_margin', 'N/A')}%
- 负债率: {financial_data.get('debt_ratio', 'N/A')}%

行业对比数据:
- 行业平均PE: {industry_data.get('industry_pe', 'N/A')}
- 行业平均PB: {industry_data.get('industry_pb', 'N/A')}
- 行业平均ROE: {industry_data.get('industry_roe', 'N/A')}%
- 行业增长率: {industry_data.get('industry_growth', 'N/A')}%

请从以下角度进行分析:

1. **盈利能力分析**
   - 收入增长趋势和质量
   - 利润率水平和变化
   - 盈利能力的可持续性
   - 与行业平均水平对比

2. **财务健康状况**
   - 资产负债结构分析
   - 现金流状况评估
   - 偿债能力分析
   - 财务风险评估

3. **估值分析**
   - 当前估值水平评估
   - 与历史估值对比
   - 与同行业公司对比
   - 合理估值区间预测

4. **成长性分析**
   - 历史成长表现
   - 未来成长潜力
   - 成长驱动因素
   - 成长可持续性

5. **竞争优势分析**
   - 核心竞争力识别
   - 护城河评估
   - 市场地位分析
   - 竞争风险评估

6. **投资建议**
   - 基于基本面的投资评级
   - 目标价位预测
   - 投资风险提示
   - 关键监控指标

请提供专业、客观的基本面分析，重点关注长期投资价值。
"""
        
        return prompt
    
    def _parse_fundamentals_result(self, llm_response: str, symbol: str) -> Dict[str, Any]:
        """解析基本面分析结果"""
        try:
            result = {
                "symbol": symbol,
                "fundamentals_summary": llm_response,
                "profitability_rating": self._extract_profitability_rating(llm_response),
                "financial_health": self._extract_financial_health(llm_response),
                "valuation_level": self._extract_valuation_level(llm_response),
                "growth_potential": self._extract_growth_potential(llm_response),
                "competitive_advantage": self._extract_competitive_advantage(llm_response),
                "investment_rating": self._extract_investment_rating(llm_response),
                "target_price": self._extract_target_price(llm_response),
                "key_risks": self._extract_key_risks(llm_response),
                "overall_score": self._calculate_overall_score(llm_response)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"解析基本面分析结果失败: {e}")
            return {
                "symbol": symbol,
                "fundamentals_summary": llm_response,
                "investment_rating": "中性",
                "overall_score": 0.5
            }
    
    def _extract_profitability_rating(self, text: str) -> str:
        """提取盈利能力评级"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["盈利能力强", "盈利优秀", "利润率高"]):
            return "优秀"
        elif any(word in text_lower for word in ["盈利能力弱", "盈利较差", "利润率低"]):
            return "较差"
        else:
            return "一般"
    
    def _extract_financial_health(self, text: str) -> str:
        """提取财务健康状况"""
        text_lower = text.lower()
        
        healthy_indicators = ["财务健康", "资产质量好", "现金流充足", "负债合理"]
        unhealthy_indicators = ["财务风险", "资产质量差", "现金流紧张", "负债过高"]
        
        healthy_count = sum(1 for word in healthy_indicators if word in text_lower)
        unhealthy_count = sum(1 for word in unhealthy_indicators if word in text_lower)
        
        if healthy_count > unhealthy_count:
            return "健康"
        elif unhealthy_count > healthy_count:
            return "风险"
        else:
            return "一般"
    
    def _extract_valuation_level(self, text: str) -> str:
        """提取估值水平"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["低估", "估值偏低", "价值被低估"]):
            return "低估"
        elif any(word in text_lower for word in ["高估", "估值偏高", "价格过高"]):
            return "高估"
        else:
            return "合理"
    
    def _extract_growth_potential(self, text: str) -> str:
        """提取成长潜力"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["成长性强", "增长潜力大", "发展前景好"]):
            return "高"
        elif any(word in text_lower for word in ["成长性弱", "增长有限", "发展受限"]):
            return "低"
        else:
            return "中等"
    
    def _extract_competitive_advantage(self, text: str) -> str:
        """提取竞争优势"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["竞争优势明显", "护城河深", "市场地位强"]):
            return "强"
        elif any(word in text_lower for word in ["竞争优势弱", "护城河浅", "竞争激烈"]):
            return "弱"
        else:
            return "一般"
    
    def _extract_investment_rating(self, text: str) -> str:
        """提取投资评级"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["强烈推荐", "买入", "增持"]):
            return "买入"
        elif any(word in text_lower for word in ["卖出", "减持", "回避"]):
            return "卖出"
        elif any(word in text_lower for word in ["持有", "中性"]):
            return "持有"
        else:
            return "中性"
    
    def _extract_target_price(self, text: str) -> str:
        """提取目标价位"""
        import re
        
        # 查找价格相关的数字
        price_patterns = [
            r'目标价[：:]\s*(\d+\.?\d*)',
            r'合理价位[：:]\s*(\d+\.?\d*)',
            r'目标价位[：:]\s*(\d+\.?\d*)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return "待确定"
    
    def _extract_key_risks(self, text: str) -> list:
        """提取关键风险"""
        risks = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["风险", "威胁", "挑战", "不确定"]):
                risk = line.strip()
                if risk and len(risk) < 100:
                    risks.append(risk)
        
        return risks[:3]  # 最多返回3个关键风险
    
    def _calculate_overall_score(self, text: str) -> float:
        """计算综合评分"""
        text_lower = text.lower()

        # 正面指标
        positive_indicators = ["优秀", "强", "好", "高", "健康", "低估", "推荐"]
        # 负面指标
        negative_indicators = ["差", "弱", "低", "风险", "高估", "回避", "卖出"]

        positive_count = sum(1 for word in positive_indicators if word in text_lower)
        negative_count = sum(1 for word in negative_indicators if word in text_lower)

        total_count = positive_count + negative_count
        if total_count == 0:
            return 0.5

        score = 0.3 + (positive_count / total_count) * 0.7  # 基础分0.3，最高1.0
        return round(max(0.1, min(1.0, score)), 2)
