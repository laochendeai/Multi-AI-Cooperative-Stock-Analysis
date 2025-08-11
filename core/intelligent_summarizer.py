#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能文档精简系统 - 替换简单截取，支持关键信息提取和内容摘要生成
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class IntelligentSummarizer:
    """智能文档精简器"""
    
    def __init__(self, max_length: int = 1000):
        self.max_length = max_length
        
        # 关键词权重配置
        self.keyword_weights = {
            # 投资相关高权重词
            "investment": 3.0, "投资": 3.0, "建议": 3.0, "推荐": 3.0,
            "buy": 2.5, "sell": 2.5, "hold": 2.5, "买入": 2.5, "卖出": 2.5, "持有": 2.5,
            "risk": 2.5, "风险": 2.5, "机会": 2.5, "opportunity": 2.5,
            
            # 分析相关中权重词
            "analysis": 2.0, "分析": 2.0, "评估": 2.0, "assessment": 2.0,
            "trend": 2.0, "趋势": 2.0, "预测": 2.0, "forecast": 2.0,
            "performance": 2.0, "表现": 2.0, "业绩": 2.0,
            
            # 财务相关词
            "revenue": 1.8, "营收": 1.8, "profit": 1.8, "利润": 1.8,
            "growth": 1.8, "增长": 1.8, "valuation": 1.8, "估值": 1.8,
            "earnings": 1.8, "收益": 1.8, "财务": 1.8, "financial": 1.8,
            
            # 市场相关词
            "market": 1.5, "市场": 1.5, "price": 1.5, "价格": 1.5,
            "volume": 1.5, "成交量": 1.5, "sentiment": 1.5, "情绪": 1.5,
            
            # 技术分析词
            "technical": 1.5, "技术": 1.5, "indicator": 1.5, "指标": 1.5,
            "support": 1.5, "支撑": 1.5, "resistance": 1.5, "阻力": 1.5,
            
            # 新闻事件词
            "news": 1.3, "新闻": 1.3, "event": 1.3, "事件": 1.3,
            "announcement": 1.3, "公告": 1.3, "policy": 1.3, "政策": 1.3
        }
        
        # 句子重要性标识符
        self.importance_markers = {
            "结论": 3.0, "conclusion": 3.0, "总结": 3.0, "summary": 3.0,
            "建议": 2.8, "recommendation": 2.8, "推荐": 2.8,
            "重要": 2.5, "important": 2.5, "关键": 2.5, "key": 2.5,
            "核心": 2.3, "core": 2.3, "主要": 2.3, "main": 2.3,
            "显著": 2.0, "significant": 2.0, "明显": 2.0, "obvious": 2.0
        }
    
    def summarize_content(self, content: str, context: str = "", 
                         preserve_structure: bool = True) -> str:
        """智能精简内容"""
        try:
            if not content or len(content.strip()) <= self.max_length:
                return content.strip()
            
            # 预处理内容
            cleaned_content = self._preprocess_content(content)
            
            # 如果清理后的内容仍然过长，进行智能精简
            if len(cleaned_content) > self.max_length:
                if preserve_structure:
                    summarized = self._structure_aware_summarize(cleaned_content, context)
                else:
                    summarized = self._sentence_based_summarize(cleaned_content, context)
                
                # 添加精简标识
                if len(summarized) < len(cleaned_content):
                    summarized += f"\n\n💡 *内容已智能精简，原文长度: {len(content)}字符*"
                
                return summarized
            else:
                return cleaned_content
                
        except Exception as e:
            logger.error(f"内容精简失败: {e}")
            # 回退到简单截取
            return content[:self.max_length] + "...\n\n[内容过长，已截断显示]"
    
    def _preprocess_content(self, content: str) -> str:
        """预处理内容"""
        # 移除多余的空白字符
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # 移除重复的标点符号
        content = re.sub(r'[。！？]{2,}', '。', content)
        content = re.sub(r'[，、；：]{2,}', '，', content)
        
        # 移除格式化字符
        content = content.replace("**", "").replace("*", "")
        content = content.replace("###", "").replace("##", "").replace("#", "")
        content = content.replace("```", "").replace("`", "")
        
        # 移除多余的引号和括号
        content = re.sub(r'["""]{2,}', '"', content)
        content = re.sub(r'[（）()]{2,}', '', content)
        
        return content.strip()
    
    def _structure_aware_summarize(self, content: str, context: str = "") -> str:
        """结构感知的精简"""
        # 分析内容结构
        sections = self._identify_sections(content)
        
        if sections:
            # 按重要性排序段落
            ranked_sections = self._rank_sections(sections, context)
            
            # 选择最重要的段落
            selected_content = []
            current_length = 0
            
            for section, score in ranked_sections:
                if current_length + len(section) <= self.max_length * 0.9:  # 留10%空间给标识
                    selected_content.append(section)
                    current_length += len(section)
                else:
                    # 如果段落太长，进行句子级精简
                    remaining_space = self.max_length * 0.9 - current_length
                    if remaining_space > 100:  # 至少要有100字符空间
                        summarized_section = self._sentence_based_summarize(
                            section, context, int(remaining_space)
                        )
                        selected_content.append(summarized_section)
                    break
            
            return "\n\n".join(selected_content)
        else:
            # 如果无法识别结构，使用句子级精简
            return self._sentence_based_summarize(content, context)
    
    def _identify_sections(self, content: str) -> List[str]:
        """识别内容段落"""
        # 按双换行分割段落
        sections = [section.strip() for section in content.split('\n\n') if section.strip()]
        
        # 如果段落太少，按单换行分割
        if len(sections) < 3:
            sections = [section.strip() for section in content.split('\n') if section.strip()]
        
        # 过滤掉太短的段落
        sections = [section for section in sections if len(section) > 20]
        
        return sections
    
    def _rank_sections(self, sections: List[str], context: str = "") -> List[Tuple[str, float]]:
        """对段落按重要性排序"""
        ranked = []
        
        for section in sections:
            score = self._calculate_section_importance(section, context)
            ranked.append((section, score))
        
        # 按分数降序排序
        ranked.sort(key=lambda x: x[1], reverse=True)
        
        return ranked
    
    def _calculate_section_importance(self, section: str, context: str = "") -> float:
        """计算段落重要性分数"""
        score = 0.0
        section_lower = section.lower()
        
        # 1. 关键词权重
        for keyword, weight in self.keyword_weights.items():
            count = section_lower.count(keyword.lower())
            score += count * weight
        
        # 2. 重要性标识符
        for marker, weight in self.importance_markers.items():
            if marker.lower() in section_lower:
                score += weight
        
        # 3. 数字和百分比（通常包含重要信息）
        number_count = len(re.findall(r'\d+\.?\d*%?', section))
        score += number_count * 0.5
        
        # 4. 长度惩罚（避免选择过长的段落）
        length_penalty = len(section) / 1000  # 每1000字符减0.1分
        score -= length_penalty * 0.1
        
        # 5. 位置权重（开头和结尾的段落通常更重要）
        # 这个需要在调用时传入位置信息，暂时跳过
        
        # 6. 上下文相关性
        if context:
            context_keywords = self._extract_keywords(context)
            for keyword in context_keywords:
                if keyword.lower() in section_lower:
                    score += 1.0
        
        return score
    
    def _sentence_based_summarize(self, content: str, context: str = "", 
                                max_length: Optional[int] = None) -> str:
        """基于句子的精简"""
        if max_length is None:
            max_length = self.max_length
        
        # 分割句子
        sentences = self._split_sentences(content)
        
        if not sentences:
            return content[:max_length] + "..."
        
        # 计算每个句子的重要性
        sentence_scores = []
        for sentence in sentences:
            score = self._calculate_sentence_importance(sentence, context)
            sentence_scores.append((sentence, score))
        
        # 按重要性排序
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 选择最重要的句子
        selected_sentences = []
        current_length = 0
        
        for sentence, score in sentence_scores:
            if current_length + len(sentence) <= max_length * 0.9:
                selected_sentences.append(sentence)
                current_length += len(sentence)
            else:
                break
        
        # 按原始顺序重新排列
        original_order = []
        for sentence in sentences:
            if sentence in selected_sentences:
                original_order.append(sentence)
        
        return "。".join(original_order) + "。" if original_order else content[:max_length] + "..."
    
    def _split_sentences(self, content: str) -> List[str]:
        """分割句子"""
        # 使用中英文句号分割
        sentences = re.split(r'[。！？.!?]+', content)
        
        # 清理和过滤
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        return sentences
    
    def _calculate_sentence_importance(self, sentence: str, context: str = "") -> float:
        """计算句子重要性"""
        score = 0.0
        sentence_lower = sentence.lower()
        
        # 1. 关键词权重
        for keyword, weight in self.keyword_weights.items():
            if keyword.lower() in sentence_lower:
                score += weight
        
        # 2. 重要性标识符
        for marker, weight in self.importance_markers.items():
            if marker.lower() in sentence_lower:
                score += weight
        
        # 3. 数字和百分比
        number_count = len(re.findall(r'\d+\.?\d*%?', sentence))
        score += number_count * 0.8
        
        # 4. 句子长度（适中长度的句子通常包含更多信息）
        length = len(sentence)
        if 50 <= length <= 200:
            score += 1.0
        elif length < 20:
            score -= 1.0
        elif length > 300:
            score -= 0.5
        
        # 5. 上下文相关性
        if context:
            context_keywords = self._extract_keywords(context)
            for keyword in context_keywords:
                if keyword.lower() in sentence_lower:
                    score += 1.5
        
        return score
    
    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 简单的关键词提取
        words = re.findall(r'\b\w+\b', text.lower())
        
        # 过滤停用词和短词
        stop_words = {'的', '了', '在', '是', '和', '与', '或', '但', '而', '因为', '所以', 
                     'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        # 返回出现频率较高的词
        from collections import Counter
        word_counts = Counter(keywords)
        
        return [word for word, count in word_counts.most_common(10)]
    
    def extract_key_points(self, content: str, max_points: int = 5) -> List[str]:
        """提取关键要点"""
        try:
            sentences = self._split_sentences(content)
            
            if not sentences:
                return []
            
            # 计算句子重要性
            sentence_scores = []
            for sentence in sentences:
                score = self._calculate_sentence_importance(sentence)
                sentence_scores.append((sentence, score))
            
            # 选择最重要的句子作为要点
            sentence_scores.sort(key=lambda x: x[1], reverse=True)
            
            key_points = []
            for sentence, score in sentence_scores[:max_points]:
                # 简化句子
                simplified = self._simplify_sentence(sentence)
                if simplified:
                    key_points.append(simplified)
            
            return key_points
            
        except Exception as e:
            logger.error(f"提取关键要点失败: {e}")
            return []
    
    def _simplify_sentence(self, sentence: str) -> str:
        """简化句子"""
        # 移除修饰词
        sentence = re.sub(r'(非常|很|比较|相当|十分|极其)', '', sentence)
        
        # 移除冗余表达
        sentence = re.sub(r'(我认为|我觉得|据我所知|根据分析)', '', sentence)
        
        # 保留核心信息
        sentence = sentence.strip()
        
        return sentence if len(sentence) > 10 else ""
    
    def create_executive_summary(self, content: str, max_length: int = 200) -> str:
        """创建执行摘要"""
        try:
            # 提取关键要点
            key_points = self.extract_key_points(content, max_points=3)
            
            if not key_points:
                # 如果无法提取要点，使用句子级精简
                return self._sentence_based_summarize(content, max_length=max_length)
            
            # 组合关键要点
            summary = "。".join(key_points) + "。"
            
            # 如果摘要仍然过长，进一步精简
            if len(summary) > max_length:
                summary = self._sentence_based_summarize(summary, max_length=max_length)
            
            return summary
            
        except Exception as e:
            logger.error(f"创建执行摘要失败: {e}")
            return content[:max_length] + "..."


class ContentProcessor:
    """内容处理器 - 集成智能精简功能"""
    
    def __init__(self, max_length: int = 1000):
        self.summarizer = IntelligentSummarizer(max_length)
    
    def process_analysis_content(self, content: Any, agent_type: str = "", 
                               context: str = "") -> str:
        """处理分析内容"""
        try:
            # 转换为字符串
            if isinstance(content, dict):
                content_str = self._extract_from_dict(content)
            elif isinstance(content, list):
                content_str = "\n".join([str(item) for item in content])
            else:
                content_str = str(content)
            
            # 如果内容为空或太短，直接返回
            if not content_str or len(content_str.strip()) < 20:
                return "暂无分析数据"
            
            # 智能精简
            processed = self.summarizer.summarize_content(
                content_str, 
                context=f"{agent_type} {context}",
                preserve_structure=True
            )
            
            return processed if processed else "分析结果处理失败"
            
        except Exception as e:
            logger.error(f"处理分析内容失败: {e}")
            return f"内容处理失败: {str(e)}"
    
    def _extract_from_dict(self, data: Dict[str, Any]) -> str:
        """从字典中提取内容"""
        # 优先字段
        priority_fields = [
            "content", "analysis", "summary", "conclusion", 
            "recommendation", "result", "output", "response"
        ]
        
        # 尝试从优先字段提取
        for field in priority_fields:
            if field in data and data[field]:
                return str(data[field])
        
        # 如果没有优先字段，组合所有有意义的字段
        excluded_fields = {
            "agent_id", "timestamp", "status", "confidence", 
            "model_used", "type", "metadata"
        }
        
        content_parts = []
        for key, value in data.items():
            if key not in excluded_fields and value:
                if isinstance(value, (str, int, float)):
                    content_parts.append(f"{key}: {value}")
                elif isinstance(value, dict):
                    nested_content = self._extract_from_dict(value)
                    if nested_content:
                        content_parts.append(f"{key}: {nested_content}")
        
        return "\n".join(content_parts)
    
    def create_summary_report(self, analysis_results: Dict[str, Any]) -> Dict[str, str]:
        """创建摘要报告"""
        try:
            summary_report = {}
            
            # 处理各个分析部分
            analysis_sections = [
                ("market_analysis", "市场分析"),
                ("sentiment_analysis", "情感分析"),
                ("news_analysis", "新闻分析"),
                ("fundamentals_analysis", "基本面分析"),
                ("bull_arguments", "多头观点"),
                ("bear_arguments", "空头观点"),
                ("investment_recommendation", "投资建议"),
                ("trading_strategy", "交易策略"),
                ("risk_assessment", "风险评估"),
                ("final_decision", "最终决策")
            ]
            
            for key, name in analysis_sections:
                if key in analysis_results:
                    content = analysis_results[key]
                    processed = self.process_analysis_content(
                        content, 
                        agent_type=name,
                        context="投资分析"
                    )
                    summary_report[key] = processed
            
            return summary_report
            
        except Exception as e:
            logger.error(f"创建摘要报告失败: {e}")
            return {}
    
    def extract_key_insights(self, analysis_results: Dict[str, Any]) -> List[str]:
        """提取关键洞察"""
        try:
            all_content = []
            
            # 收集所有分析内容
            for key, value in analysis_results.items():
                if isinstance(value, str) and len(value) > 50:
                    all_content.append(value)
            
            combined_content = "\n\n".join(all_content)
            
            # 提取关键要点
            key_points = self.summarizer.extract_key_points(
                combined_content, 
                max_points=8
            )
            
            return key_points
            
        except Exception as e:
            logger.error(f"提取关键洞察失败: {e}")
            return []
