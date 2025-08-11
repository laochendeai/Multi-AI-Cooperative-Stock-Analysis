"""
社交媒体分析师 - 专业情感分析和市场情绪评估
"""

import logging
from typing import Dict, Any
from datetime import datetime

from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)

class SocialMediaAnalyst(BaseAgent):
    """社交媒体情感分析师"""
    
    def __init__(self, llm_client=None, memory_manager=None):
        super().__init__(
            agent_id="social_media_analyst",
            agent_type="情感分析师",
            llm_client=llm_client,
            memory_manager=memory_manager
        )
    
    async def analyze(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行社交媒体情感分析
        
        Args:
            input_data: 包含股票代码、社交媒体数据等
            context: 上下文信息
            
        Returns:
            情感分析结果
        """
        try:
            symbol = input_data.get("symbol", "")
            social_data = input_data.get("social_data", {})
            news_sentiment = input_data.get("news_sentiment", {})
            
            # 构建分析提示
            analysis_prompt = self._build_sentiment_prompt(symbol, social_data, news_sentiment)
            
            # 获取LLM分析
            llm_response = await self.get_llm_response(analysis_prompt, context)
            
            # 解析和结构化结果
            analysis_result = self._parse_sentiment_result(llm_response, symbol)
            
            return {
                "status": "success",
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "analysis_type": "sentiment_analysis",
                "symbol": symbol,
                "content": analysis_result,
                "raw_response": llm_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return {
                "status": "error",
                "agent_id": self.agent_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_sentiment_prompt(self, symbol: str, social_data: Dict, news_sentiment: Dict) -> str:
        """构建情感分析提示"""
        prompt = f"""
作为专业的社交媒体情感分析师，请对股票 {symbol} 的市场情绪进行全面分析。

社交媒体数据:
- 讨论热度: {social_data.get('discussion_volume', 'N/A')}
- 正面提及: {social_data.get('positive_mentions', 'N/A')}
- 负面提及: {social_data.get('negative_mentions', 'N/A')}
- 中性提及: {social_data.get('neutral_mentions', 'N/A')}
- 关键词热度: {social_data.get('trending_keywords', [])}

新闻情感数据:
- 新闻总数: {news_sentiment.get('total_news', 'N/A')}
- 正面新闻: {news_sentiment.get('positive_news', 'N/A')}
- 负面新闻: {news_sentiment.get('negative_news', 'N/A')}
- 情感得分: {news_sentiment.get('sentiment_score', 'N/A')}

请从以下角度进行分析:

1. **整体情感倾向**
   - 市场情绪是偏向乐观、悲观还是中性
   - 情感强度评估（强烈/中等/温和）
   - 情感变化趋势

2. **讨论热度分析**
   - 当前讨论热度水平
   - 与历史平均水平对比
   - 热度变化原因分析

3. **关键话题识别**
   - 主要讨论话题
   - 影响情感的关键事件
   - 市场关注焦点

4. **情感质量评估**
   - 讨论内容的专业性
   - 是否存在情绪化炒作
   - 理性分析vs情绪化反应

5. **投资影响预测**
   - 当前情感对股价的可能影响
   - 情感转变的可能性
   - 短期情感走势预测

6. **风险提示**
   - 情感极端化风险
   - 反向情感可能性
   - 需要关注的情感指标

请提供客观、专业的情感分析，避免被短期情绪波动误导。
"""
        
        return prompt
    
    def _parse_sentiment_result(self, llm_response: str, symbol: str) -> Dict[str, Any]:
        """解析情感分析结果"""
        try:
            result = {
                "symbol": symbol,
                "sentiment_summary": llm_response,
                "overall_sentiment": self._extract_overall_sentiment(llm_response),
                "sentiment_strength": self._extract_sentiment_strength(llm_response),
                "discussion_heat": self._extract_discussion_heat(llm_response),
                "key_topics": self._extract_key_topics(llm_response),
                "market_impact": self._extract_market_impact(llm_response),
                "sentiment_score": self._calculate_sentiment_score(llm_response),
                "confidence_level": self._calculate_confidence(llm_response)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"解析情感分析结果失败: {e}")
            return {
                "symbol": symbol,
                "sentiment_summary": llm_response,
                "overall_sentiment": "中性",
                "sentiment_strength": "中等",
                "sentiment_score": 0.5,
                "confidence_level": 0.5
            }
    
    def _extract_overall_sentiment(self, text: str) -> str:
        """提取整体情感倾向"""
        text_lower = text.lower()
        
        positive_words = ["乐观", "积极", "正面", "看好", "利好", "positive", "bullish"]
        negative_words = ["悲观", "消极", "负面", "看空", "利空", "negative", "bearish"]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "积极"
        elif negative_count > positive_count:
            return "消极"
        else:
            return "中性"
    
    def _extract_sentiment_strength(self, text: str) -> str:
        """提取情感强度"""
        text_lower = text.lower()
        
        strong_words = ["强烈", "极度", "非常", "显著", "剧烈"]
        mild_words = ["温和", "轻微", "适度", "一般"]
        
        if any(word in text_lower for word in strong_words):
            return "强烈"
        elif any(word in text_lower for word in mild_words):
            return "温和"
        else:
            return "中等"
    
    def _extract_discussion_heat(self, text: str) -> str:
        """提取讨论热度"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["热度很高", "讨论激烈", "关注度高"]):
            return "高"
        elif any(word in text_lower for word in ["热度较低", "讨论较少", "关注度低"]):
            return "低"
        else:
            return "中等"
    
    def _extract_key_topics(self, text: str) -> list:
        """提取关键话题"""
        # 简单的关键词提取
        topics = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["话题", "讨论", "关注", "焦点"]):
                # 提取该行作为话题
                topic = line.strip()
                if topic and len(topic) < 100:  # 避免过长的内容
                    topics.append(topic)
        
        return topics[:5]  # 最多返回5个话题
    
    def _extract_market_impact(self, text: str) -> str:
        """提取市场影响预测"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["推动上涨", "利好", "正面影响"]):
            return "正面"
        elif any(word in text_lower for word in ["推动下跌", "利空", "负面影响"]):
            return "负面"
        else:
            return "中性"
    
    def _calculate_sentiment_score(self, text: str) -> float:
        """计算情感得分 (-1到1之间)"""
        text_lower = text.lower()
        
        # 正面词汇
        positive_words = ["乐观", "积极", "正面", "看好", "利好", "上涨", "买入"]
        # 负面词汇
        negative_words = ["悲观", "消极", "负面", "看空", "利空", "下跌", "卖出"]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_count = positive_count + negative_count
        if total_count == 0:
            return 0.0
        
        score = (positive_count - negative_count) / total_count
        return round(max(-1.0, min(1.0, score)), 2)
    
    def _calculate_confidence(self, text: str) -> float:
        """计算分析置信度"""
        text_lower = text.lower()
        
        confidence_indicators = ["明确", "清晰", "显著", "确定", "强烈"]
        uncertainty_indicators = ["可能", "或许", "不确定", "模糊", "难以判断"]
        
        confidence_count = sum(1 for word in confidence_indicators if word in text_lower)
        uncertainty_count = sum(1 for word in uncertainty_indicators if word in text_lower)
        
        base_confidence = 0.6
        confidence_boost = confidence_count * 0.1
        confidence_penalty = uncertainty_count * 0.1
        
        confidence = max(0.2, min(0.9, base_confidence + confidence_boost - confidence_penalty))
        return round(confidence, 2)
