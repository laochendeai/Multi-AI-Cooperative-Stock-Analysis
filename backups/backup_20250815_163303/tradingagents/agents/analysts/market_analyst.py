"""
市场分析师 - 专业技术指标分析和价格走势预测
"""

import logging
from typing import Dict, Any
from datetime import datetime

from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)

class MarketAnalyst(BaseAgent):
    """市场技术分析师"""
    
    def __init__(self, llm_client=None, memory_manager=None):
        super().__init__(
            agent_id="market_analyst",
            agent_type="技术分析师",
            llm_client=llm_client,
            memory_manager=memory_manager
        )
    
    async def analyze(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行技术分析
        
        Args:
            input_data: 包含股票代码、价格数据等
            context: 上下文信息
            
        Returns:
            技术分析结果
        """
        try:
            symbol = input_data.get("symbol", "")
            price_data = input_data.get("price_data", {})
            technical_indicators = input_data.get("technical_indicators", {})
            
            # 构建分析提示
            analysis_prompt = self._build_analysis_prompt(symbol, price_data, technical_indicators)
            
            # 获取LLM分析
            llm_response = await self.get_llm_response(analysis_prompt, context)
            
            # 解析和结构化结果
            analysis_result = self._parse_analysis_result(llm_response, symbol)
            
            return {
                "status": "success",
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "analysis_type": "technical_analysis",
                "symbol": symbol,
                "content": analysis_result,
                "raw_response": llm_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"市场分析失败: {e}")
            return {
                "status": "error",
                "agent_id": self.agent_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_analysis_prompt(self, symbol: str, price_data: Dict, indicators: Dict) -> str:
        """构建技术分析提示"""
        prompt = f"""
作为专业的市场技术分析师，请对股票 {symbol} 进行全面的技术分析。

当前价格数据:
- 最新价格: {price_data.get('current_price', 'N/A')}
- 开盘价: {price_data.get('open', 'N/A')}
- 最高价: {price_data.get('high', 'N/A')}
- 最低价: {price_data.get('low', 'N/A')}
- 成交量: {price_data.get('volume', 'N/A')}
- 涨跌幅: {price_data.get('change_percent', 'N/A')}%

技术指标:
"""
        
        # 添加技术指标信息
        for indicator, value in indicators.items():
            prompt += f"- {indicator}: {value}\n"
        
        prompt += """
请从以下角度进行分析:

1. **价格走势分析**
   - 当前趋势方向（上涨/下跌/横盘）
   - 关键支撑位和阻力位
   - 价格形态识别

2. **技术指标分析**
   - 移动平均线信号
   - RSI超买超卖情况
   - MACD金叉死叉信号
   - 布林带位置分析

3. **成交量分析**
   - 量价关系
   - 成交量变化趋势

4. **短期预测**
   - 未来1-3个交易日可能走势
   - 关键价位预测
   - 风险提示

5. **交易建议**
   - 买入/卖出/持有建议
   - 建议仓位比例
   - 止损止盈位设置

请提供专业、客观的分析，避免过于绝对的判断。
"""
        
        return prompt
    
    def _parse_analysis_result(self, llm_response: str, symbol: str) -> Dict[str, Any]:
        """解析LLM分析结果"""
        try:
            # 提取关键信息
            result = {
                "symbol": symbol,
                "analysis_summary": llm_response,
                "trend_direction": self._extract_trend(llm_response),
                "support_resistance": self._extract_levels(llm_response),
                "trading_signal": self._extract_signal(llm_response),
                "risk_level": self._extract_risk_level(llm_response),
                "confidence_score": self._calculate_confidence(llm_response)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"解析分析结果失败: {e}")
            return {
                "symbol": symbol,
                "analysis_summary": llm_response,
                "trend_direction": "未知",
                "trading_signal": "观望",
                "risk_level": "中等",
                "confidence_score": 0.5
            }
    
    def _extract_trend(self, text: str) -> str:
        """提取趋势方向"""
        text_lower = text.lower()
        if any(word in text_lower for word in ["上涨", "看涨", "上升", "bullish"]):
            return "上涨"
        elif any(word in text_lower for word in ["下跌", "看跌", "下降", "bearish"]):
            return "下跌"
        elif any(word in text_lower for word in ["横盘", "震荡", "sideways"]):
            return "横盘"
        return "未明确"
    
    def _extract_levels(self, text: str) -> Dict[str, str]:
        """提取支撑阻力位"""
        # 简单的关键词提取，实际应用中可以使用更复杂的NLP技术
        support = "待确定"
        resistance = "待确定"
        
        lines = text.split('\n')
        for line in lines:
            if "支撑" in line:
                support = line.strip()
            elif "阻力" in line:
                resistance = line.strip()
        
        return {
            "support": support,
            "resistance": resistance
        }
    
    def _extract_signal(self, text: str) -> str:
        """提取交易信号"""
        text_lower = text.lower()
        if any(word in text_lower for word in ["买入", "建仓", "加仓", "buy"]):
            return "买入"
        elif any(word in text_lower for word in ["卖出", "减仓", "平仓", "sell"]):
            return "卖出"
        elif any(word in text_lower for word in ["持有", "观望", "hold"]):
            return "持有"
        return "观望"
    
    def _extract_risk_level(self, text: str) -> str:
        """提取风险等级"""
        text_lower = text.lower()
        if any(word in text_lower for word in ["高风险", "风险较高", "谨慎"]):
            return "高"
        elif any(word in text_lower for word in ["低风险", "风险较低", "稳健"]):
            return "低"
        return "中等"
    
    def _calculate_confidence(self, text: str) -> float:
        """计算置信度分数"""
        # 基于关键词的简单置信度计算
        confidence_keywords = ["确定", "明确", "强烈", "显著", "清晰"]
        uncertainty_keywords = ["可能", "或许", "不确定", "谨慎", "观察"]
        
        text_lower = text.lower()
        confidence_count = sum(1 for word in confidence_keywords if word in text_lower)
        uncertainty_count = sum(1 for word in uncertainty_keywords if word in text_lower)
        
        # 简单的置信度计算
        base_confidence = 0.5
        confidence_boost = confidence_count * 0.1
        confidence_penalty = uncertainty_count * 0.1
        
        confidence = max(0.1, min(0.9, base_confidence + confidence_boost - confidence_penalty))
        return round(confidence, 2)
