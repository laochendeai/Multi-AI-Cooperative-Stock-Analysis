"""
反思引擎 - 智能体学习和改进机制
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class ReflectionEngine:
    """反思引擎 - 负责智能体的学习和改进"""
    
    def __init__(self, memory_manager=None):
        self.memory_manager = memory_manager
        self.reflection_history = []
        self.performance_metrics = {}
        self.learning_insights = []
        self.improvement_suggestions = []
    
    async def reflect_on_analysis(self, analysis_session: Dict[str, Any]) -> Dict[str, Any]:
        """对分析会话进行反思"""
        try:
            logger.info(f"开始反思分析会话: {analysis_session.get('symbol', 'Unknown')}")
            
            # 提取关键信息
            symbol = analysis_session.get("symbol", "")
            results = analysis_session.get("results", {})
            
            # 分析各阶段表现
            stage_performance = await self._analyze_stage_performance(results)
            
            # 识别成功因素
            success_factors = await self._identify_success_factors(results)
            
            # 识别改进机会
            improvement_opportunities = await self._identify_improvement_opportunities(results)
            
            # 生成学习洞察
            learning_insights = await self._generate_learning_insights(results, stage_performance)
            
            # 创建反思记录
            reflection_record = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "stage_performance": stage_performance,
                "success_factors": success_factors,
                "improvement_opportunities": improvement_opportunities,
                "learning_insights": learning_insights,
                "overall_score": self._calculate_overall_score(stage_performance)
            }
            
            # 保存反思记录
            self.reflection_history.append(reflection_record)
            
            # 更新性能指标
            await self._update_performance_metrics(reflection_record)
            
            # 保存到记忆系统
            if self.memory_manager:
                await self._save_reflection_to_memory(reflection_record)
            
            logger.info(f"反思完成: {symbol}")
            return reflection_record
            
        except Exception as e:
            logger.error(f"反思分析失败: {e}")
            return {"error": str(e)}
    
    async def _analyze_stage_performance(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """分析各阶段表现"""
        try:
            stage_scores = {}
            
            # 数据收集阶段
            market_data = results.get("market_data", {})
            data_quality = market_data.get("comprehensive_data", {}).get("data_quality", {})
            stage_scores["data_collection"] = self._score_data_quality(data_quality)
            
            # 分析师阶段
            analyst_reports = results.get("analyst_reports", {})
            stage_scores["analyst_team"] = self._score_analyst_performance(analyst_reports)
            
            # 研究辩论阶段
            research_results = results.get("research_results", {})
            stage_scores["research_debate"] = self._score_research_performance(research_results)
            
            # 交易策略阶段
            trading_strategy = results.get("trading_strategy", {})
            stage_scores["trading_strategy"] = self._score_trading_strategy(trading_strategy)
            
            # 风险管理阶段
            final_decision = results.get("final_decision", {})
            stage_scores["risk_management"] = self._score_risk_management(final_decision)
            
            return stage_scores
            
        except Exception as e:
            logger.error(f"分析阶段表现失败: {e}")
            return {}
    
    def _score_data_quality(self, data_quality: Dict[str, Any]) -> float:
        """评分数据质量"""
        try:
            quality_score = data_quality.get("quality_score", 0.5)
            successful_sources = data_quality.get("successful_sources", 0)
            total_sources = data_quality.get("total_sources", 1)
            
            # 综合评分
            score = (quality_score * 0.7) + ((successful_sources / total_sources) * 0.3)
            return round(min(1.0, max(0.0, score)), 2)
            
        except Exception:
            return 0.5
    
    def _score_analyst_performance(self, analyst_reports: Dict[str, Any]) -> float:
        """评分分析师表现"""
        try:
            scores = []
            
            for analyst_type, report in analyst_reports.items():
                if isinstance(report, dict) and "status" in report:
                    if report["status"] == "success":
                        # 基于分析内容质量评分
                        content = report.get("content", {})
                        confidence = content.get("confidence_score", 0.5)
                        scores.append(confidence)
                    else:
                        scores.append(0.0)
            
            return round(sum(scores) / len(scores) if scores else 0.5, 2)
            
        except Exception:
            return 0.5
    
    def _score_research_performance(self, research_results: Dict[str, Any]) -> float:
        """评分研究表现"""
        try:
            # 评估辩论质量
            debate_rounds = len(research_results.get("debate_results", []))
            expected_rounds = research_results.get("debate_rounds", 1)
            
            # 评估投资建议质量
            recommendation = research_results.get("investment_recommendation", {})
            if recommendation.get("status") == "success":
                content = recommendation.get("content", {})
                confidence = content.get("confidence_level", 0.5)
                
                # 综合评分
                debate_score = min(1.0, debate_rounds / expected_rounds)
                recommendation_score = confidence
                
                return round((debate_score * 0.4) + (recommendation_score * 0.6), 2)
            
            return 0.3
            
        except Exception:
            return 0.5
    
    def _score_trading_strategy(self, trading_strategy: Dict[str, Any]) -> float:
        """评分交易策略"""
        try:
            if trading_strategy.get("status") == "success":
                content = trading_strategy.get("content", {})
                
                # 检查策略完整性
                required_fields = ["trading_action", "position_size", "risk_management", "execution_plan"]
                completeness = sum(1 for field in required_fields if field in content) / len(required_fields)
                
                # 检查风险收益比
                expected_return = content.get("expected_return", "0%")
                max_risk = content.get("max_risk", "100%")
                
                try:
                    return_val = float(expected_return.replace("%", ""))
                    risk_val = float(max_risk.replace("%", ""))
                    risk_reward_ratio = return_val / risk_val if risk_val > 0 else 0
                    risk_score = min(1.0, risk_reward_ratio / 2)  # 2:1比例为满分
                except:
                    risk_score = 0.5
                
                return round((completeness * 0.6) + (risk_score * 0.4), 2)
            
            return 0.3
            
        except Exception:
            return 0.5
    
    def _score_risk_management(self, final_decision: Dict[str, Any]) -> float:
        """评分风险管理"""
        try:
            if final_decision.get("status") == "success":
                content = final_decision.get("content", {})
                
                # 评估决策信心
                confidence = content.get("decision_confidence", 0.5)
                
                # 评估风险评估质量
                risk_assessment = content.get("risk_assessment", {})
                risk_score = 0.8 if risk_assessment.get("controllability") == "可控" else 0.5
                
                # 评估团队共识
                consensus = content.get("team_consensus", "")
                consensus_score = {"高度共识": 1.0, "基本共识": 0.8, "部分共识": 0.6, "分歧较大": 0.3}.get(consensus, 0.5)
                
                return round((confidence * 0.4) + (risk_score * 0.3) + (consensus_score * 0.3), 2)
            
            return 0.3
            
        except Exception:
            return 0.5
    
    async def _identify_success_factors(self, results: Dict[str, Any]) -> List[str]:
        """识别成功因素"""
        try:
            success_factors = []
            
            # 检查数据质量
            market_data = results.get("market_data", {})
            data_quality = market_data.get("comprehensive_data", {}).get("data_quality", {})
            if data_quality.get("quality_level") == "high":
                success_factors.append("高质量的数据收集")
            
            # 检查分析师一致性
            analyst_reports = results.get("analyst_reports", {})
            successful_analyses = sum(1 for report in analyst_reports.values() 
                                    if isinstance(report, dict) and report.get("status") == "success")
            if successful_analyses >= 3:
                success_factors.append("分析师团队表现优秀")
            
            # 检查辩论质量
            research_results = results.get("research_results", {})
            debate_rounds = len(research_results.get("debate_results", []))
            if debate_rounds >= 2:
                success_factors.append("充分的多空辩论")
            
            # 检查决策一致性
            final_decision = results.get("final_decision", {})
            if final_decision.get("status") == "success":
                content = final_decision.get("content", {})
                if content.get("team_consensus") in ["高度共识", "基本共识"]:
                    success_factors.append("团队决策共识度高")
            
            return success_factors
            
        except Exception as e:
            logger.error(f"识别成功因素失败: {e}")
            return []
    
    async def _identify_improvement_opportunities(self, results: Dict[str, Any]) -> List[str]:
        """识别改进机会"""
        try:
            opportunities = []
            
            # 检查数据质量问题
            market_data = results.get("market_data", {})
            data_quality = market_data.get("comprehensive_data", {}).get("data_quality", {})
            if data_quality.get("quality_level") == "low":
                opportunities.append("改进数据源质量和可靠性")
            
            # 检查分析师表现
            analyst_reports = results.get("analyst_reports", {})
            failed_analyses = [report_type for report_type, report in analyst_reports.items() 
                             if isinstance(report, dict) and report.get("status") != "success"]
            if failed_analyses:
                opportunities.append(f"改进{', '.join(failed_analyses)}的分析质量")
            
            # 检查辩论深度
            research_results = results.get("research_results", {})
            debate_rounds = len(research_results.get("debate_results", []))
            expected_rounds = research_results.get("debate_rounds", 1)
            if debate_rounds < expected_rounds:
                opportunities.append("增加辩论轮次以提高分析深度")
            
            # 检查决策信心
            final_decision = results.get("final_decision", {})
            if final_decision.get("status") == "success":
                content = final_decision.get("content", {})
                confidence = content.get("decision_confidence", 0.5)
                if confidence < 0.6:
                    opportunities.append("提高决策信心度和确定性")
            
            return opportunities
            
        except Exception as e:
            logger.error(f"识别改进机会失败: {e}")
            return []
    
    async def _generate_learning_insights(self, results: Dict[str, Any], stage_performance: Dict[str, Any]) -> List[str]:
        """生成学习洞察"""
        try:
            insights = []
            
            # 基于阶段表现生成洞察
            best_stage = max(stage_performance.items(), key=lambda x: x[1]) if stage_performance else ("", 0)
            worst_stage = min(stage_performance.items(), key=lambda x: x[1]) if stage_performance else ("", 0)
            
            if best_stage[1] > 0.8:
                insights.append(f"{best_stage[0]}阶段表现优秀，可作为其他阶段的参考标准")
            
            if worst_stage[1] < 0.5:
                insights.append(f"{worst_stage[0]}阶段需要重点改进和优化")
            
            # 基于决策结果生成洞察
            final_decision = results.get("final_decision", {})
            if final_decision.get("status") == "success":
                content = final_decision.get("content", {})
                decision = content.get("final_decision", "")
                if decision in ["STRONG_BUY", "STRONG_SELL"]:
                    insights.append("团队对强烈信号的识别能力较强")
                elif decision == "HOLD":
                    insights.append("团队在不确定情况下倾向于保守决策")
            
            return insights
            
        except Exception as e:
            logger.error(f"生成学习洞察失败: {e}")
            return []
    
    def _calculate_overall_score(self, stage_performance: Dict[str, Any]) -> float:
        """计算总体评分"""
        try:
            if not stage_performance:
                return 0.5
            
            scores = list(stage_performance.values())
            return round(sum(scores) / len(scores), 2)
            
        except Exception:
            return 0.5
    
    async def _update_performance_metrics(self, reflection_record: Dict[str, Any]):
        """更新性能指标"""
        try:
            symbol = reflection_record.get("symbol", "")
            overall_score = reflection_record.get("overall_score", 0.5)
            
            # 更新符号特定指标
            if symbol not in self.performance_metrics:
                self.performance_metrics[symbol] = {
                    "total_analyses": 0,
                    "average_score": 0.0,
                    "best_score": 0.0,
                    "worst_score": 1.0,
                    "improvement_trend": []
                }
            
            metrics = self.performance_metrics[symbol]
            metrics["total_analyses"] += 1
            
            # 更新平均分
            current_avg = metrics["average_score"]
            total = metrics["total_analyses"]
            metrics["average_score"] = round(((current_avg * (total - 1)) + overall_score) / total, 2)
            
            # 更新最佳和最差分数
            metrics["best_score"] = max(metrics["best_score"], overall_score)
            metrics["worst_score"] = min(metrics["worst_score"], overall_score)
            
            # 更新改进趋势
            metrics["improvement_trend"].append(overall_score)
            if len(metrics["improvement_trend"]) > 10:
                metrics["improvement_trend"] = metrics["improvement_trend"][-10:]
            
        except Exception as e:
            logger.error(f"更新性能指标失败: {e}")
    
    async def _save_reflection_to_memory(self, reflection_record: Dict[str, Any]):
        """保存反思到记忆系统"""
        try:
            if not self.memory_manager:
                return
            
            memory_content = f"反思记录: {reflection_record['symbol']} - 总分: {reflection_record['overall_score']}"
            
            await self.memory_manager.add_memory(
                content=memory_content,
                metadata={
                    "type": "reflection",
                    "symbol": reflection_record["symbol"],
                    "score": reflection_record["overall_score"],
                    "timestamp": reflection_record["timestamp"]
                }
            )
            
        except Exception as e:
            logger.error(f"保存反思到记忆失败: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        try:
            total_reflections = len(self.reflection_history)
            
            if total_reflections == 0:
                return {"total_reflections": 0, "message": "暂无反思记录"}
            
            # 计算总体统计
            recent_scores = [r["overall_score"] for r in self.reflection_history[-10:]]
            avg_recent_score = sum(recent_scores) / len(recent_scores) if recent_scores else 0
            
            # 获取改进趋势
            if len(recent_scores) >= 2:
                trend = "improving" if recent_scores[-1] > recent_scores[0] else "declining"
            else:
                trend = "stable"
            
            return {
                "total_reflections": total_reflections,
                "average_recent_score": round(avg_recent_score, 2),
                "performance_trend": trend,
                "symbols_analyzed": len(self.performance_metrics),
                "learning_insights_count": len(self.learning_insights)
            }
            
        except Exception as e:
            logger.error(f"获取性能摘要失败: {e}")
            return {"error": str(e)}
    
    def get_reflection_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取反思历史"""
        return self.reflection_history[-limit:] if self.reflection_history else []
