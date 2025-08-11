#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体模型选择管理器 - 管理智能体与LLM模型的映射关系
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class AgentModelManager:
    """智能体模型选择管理器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.agent_config_file = self.config_dir / "agent_model_config.json"
        self.agent_profiles_file = self.config_dir / "agent_profiles.json"
        
        # 智能体定义
        self.agent_definitions = {
            "analysts": {
                "market_analyst": {
                    "name": "市场分析师",
                    "description": "专业的市场技术分析师，擅长技术指标分析和价格走势预测",
                    "required_capabilities": ["text_analysis", "numerical_reasoning"],
                    "preferred_model_types": ["chat"],
                    "min_context_length": 4096,
                    "performance_priority": "accuracy"
                },
                "sentiment_analyst": {
                    "name": "情感分析师", 
                    "description": "专业的社交媒体情感分析师，擅长分析市场情绪和舆情",
                    "required_capabilities": ["text_analysis", "sentiment_analysis"],
                    "preferred_model_types": ["chat"],
                    "min_context_length": 2048,
                    "performance_priority": "speed"
                },
                "news_analyst": {
                    "name": "新闻分析师",
                    "description": "专业的新闻分析师，擅长分析全球新闻和宏观经济事件",
                    "required_capabilities": ["text_analysis", "reasoning"],
                    "preferred_model_types": ["chat"],
                    "min_context_length": 8192,
                    "performance_priority": "accuracy"
                },
                "fundamentals_analyst": {
                    "name": "基本面分析师",
                    "description": "专业的基本面分析师，擅长分析公司财务数据和基本面指标",
                    "required_capabilities": ["numerical_reasoning", "financial_analysis"],
                    "preferred_model_types": ["chat"],
                    "min_context_length": 4096,
                    "performance_priority": "accuracy"
                }
            },
            "researchers": {
                "bull_researcher": {
                    "name": "多头研究员",
                    "description": "多头研究员，专注于寻找投资机会和看涨理由",
                    "required_capabilities": ["reasoning", "research"],
                    "preferred_model_types": ["chat"],
                    "min_context_length": 8192,
                    "performance_priority": "depth"
                },
                "bear_researcher": {
                    "name": "空头研究员",
                    "description": "空头研究员，专注于识别投资风险和看跌因素",
                    "required_capabilities": ["reasoning", "risk_analysis"],
                    "preferred_model_types": ["chat"],
                    "min_context_length": 8192,
                    "performance_priority": "depth"
                },
                "research_manager": {
                    "name": "研究经理",
                    "description": "研究经理，负责协调多空辩论并做出投资建议",
                    "required_capabilities": ["reasoning", "synthesis", "decision_making"],
                    "preferred_model_types": ["chat"],
                    "min_context_length": 16384,
                    "performance_priority": "accuracy"
                }
            },
            "risk_management": {
                "aggressive_debator": {
                    "name": "激进辩论者",
                    "description": "激进的辩论者，提出大胆的投资观点",
                    "required_capabilities": ["reasoning", "argumentation"],
                    "preferred_model_types": ["chat"],
                    "min_context_length": 4096,
                    "performance_priority": "creativity"
                },
                "conservative_debator": {
                    "name": "保守辩论者",
                    "description": "保守的辩论者，强调风险控制和稳健投资",
                    "required_capabilities": ["reasoning", "risk_analysis"],
                    "preferred_model_types": ["chat"],
                    "min_context_length": 4096,
                    "performance_priority": "accuracy"
                },
                "neutral_debator": {
                    "name": "中性辩论者",
                    "description": "中性的辩论者，提供平衡的观点和分析",
                    "required_capabilities": ["reasoning", "balance"],
                    "preferred_model_types": ["chat"],
                    "min_context_length": 4096,
                    "performance_priority": "balance"
                },
                "risk_manager": {
                    "name": "风险经理",
                    "description": "风险经理，负责最终的风险评估和交易决策",
                    "required_capabilities": ["risk_analysis", "decision_making"],
                    "preferred_model_types": ["chat"],
                    "min_context_length": 8192,
                    "performance_priority": "accuracy"
                }
            },
            "trading": {
                "trader": {
                    "name": "交易员",
                    "description": "专业交易员，负责制定具体的交易策略和执行计划",
                    "required_capabilities": ["strategy_planning", "execution"],
                    "preferred_model_types": ["chat"],
                    "min_context_length": 4096,
                    "performance_priority": "precision"
                }
            }
        }
        
        # 当前智能体模型配置
        self.agent_model_config = {}
        self.load_agent_config()
    
    def load_agent_config(self):
        """加载智能体模型配置"""
        try:
            if self.agent_config_file.exists():
                with open(self.agent_config_file, 'r', encoding='utf-8') as f:
                    self.agent_model_config = json.load(f)
                logger.info(f"智能体模型配置已加载: {len(self.agent_model_config)}个智能体")
            else:
                # 使用默认配置
                self.agent_model_config = self._get_default_agent_config()
                self.save_agent_config()
                logger.info("使用默认智能体模型配置")
        except Exception as e:
            logger.error(f"加载智能体模型配置失败: {e}")
            self.agent_model_config = self._get_default_agent_config()
    
    def _get_default_agent_config(self) -> Dict[str, str]:
        """获取默认智能体模型配置"""
        default_config = {}
        
        for category, agents in self.agent_definitions.items():
            for agent_id, agent_info in agents.items():
                # 根据智能体特性选择默认模型
                if agent_info["performance_priority"] == "speed":
                    default_config[agent_id] = "deepseek:deepseek-chat"
                elif agent_info["performance_priority"] == "depth":
                    default_config[agent_id] = "moonshot:moonshot-v1-32k"
                elif agent_info["min_context_length"] > 8192:
                    default_config[agent_id] = "moonshot:moonshot-v1-32k"
                else:
                    default_config[agent_id] = "moonshot:moonshot-v1-8k"
        
        return default_config
    
    def save_agent_config(self):
        """保存智能体模型配置"""
        try:
            with open(self.agent_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.agent_model_config, f, indent=2, ensure_ascii=False)
            
            logger.info("智能体模型配置已保存")
            return {"status": "success", "message": "配置保存成功"}
        except Exception as e:
            logger.error(f"保存智能体模型配置失败: {e}")
            return {"status": "error", "message": f"保存失败: {str(e)}"}
    
    def get_all_agents(self) -> Dict[str, Any]:
        """获取所有智能体信息"""
        agents_info = {}
        
        for category, agents in self.agent_definitions.items():
            agents_info[category] = {}
            for agent_id, agent_info in agents.items():
                current_model = self.agent_model_config.get(agent_id, "未配置")
                agents_info[category][agent_id] = {
                    **agent_info,
                    "current_model": current_model,
                    "agent_id": agent_id,
                    "category": category
                }
        
        return agents_info
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取指定智能体信息"""
        for category, agents in self.agent_definitions.items():
            if agent_id in agents:
                agent_info = agents[agent_id].copy()
                agent_info["current_model"] = self.agent_model_config.get(agent_id, "未配置")
                agent_info["agent_id"] = agent_id
                agent_info["category"] = category
                return agent_info
        return None
    
    def update_agent_model(self, agent_id: str, provider: str, model: str) -> Dict[str, Any]:
        """更新智能体的模型配置"""
        try:
            # 验证智能体是否存在
            agent_info = self.get_agent_info(agent_id)
            if not agent_info:
                return {"status": "error", "message": f"智能体 {agent_id} 不存在"}
            
            # 更新配置
            model_config = f"{provider}:{model}"
            self.agent_model_config[agent_id] = model_config
            
            # 保存配置
            result = self.save_agent_config()
            if result["status"] == "success":
                logger.info(f"智能体 {agent_id} 模型已更新为: {model_config}")
                return {
                    "status": "success", 
                    "message": f"智能体 {agent_info['name']} 模型已更新为: {provider}/{model}"
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"更新智能体模型失败: {e}")
            return {"status": "error", "message": f"更新失败: {str(e)}"}
    
    def validate_model_compatibility(self, agent_id: str, provider: str, model: str, 
                                   available_models: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """验证模型与智能体的兼容性"""
        try:
            # 获取智能体信息
            agent_info = self.get_agent_info(agent_id)
            if not agent_info:
                return {"compatible": False, "reason": f"智能体 {agent_id} 不存在"}
            
            # 检查提供商是否存在
            if provider not in available_models:
                return {"compatible": False, "reason": f"提供商 {provider} 不可用"}
            
            # 查找模型信息
            model_info = None
            for model_data in available_models[provider]:
                if model_data["id"] == model:
                    model_info = model_data
                    break
            
            if not model_info:
                return {"compatible": False, "reason": f"模型 {model} 在提供商 {provider} 中不存在"}
            
            # 检查模型类型兼容性
            if model_info["type"] not in agent_info["preferred_model_types"]:
                return {
                    "compatible": False, 
                    "reason": f"模型类型 {model_info['type']} 不适合智能体 {agent_info['name']}"
                }
            
            # 检查上下文长度
            if model_info["context_length"] < agent_info["min_context_length"]:
                return {
                    "compatible": False,
                    "reason": f"模型上下文长度 {model_info['context_length']} 小于智能体最低要求 {agent_info['min_context_length']}"
                }
            
            # 计算兼容性评分
            compatibility_score = self._calculate_compatibility_score(agent_info, model_info)
            
            return {
                "compatible": True,
                "score": compatibility_score,
                "recommendation": self._get_compatibility_recommendation(compatibility_score),
                "model_info": model_info
            }
            
        except Exception as e:
            logger.error(f"验证模型兼容性失败: {e}")
            return {"compatible": False, "reason": f"验证失败: {str(e)}"}
    
    def _calculate_compatibility_score(self, agent_info: Dict[str, Any], model_info: Dict[str, Any]) -> float:
        """计算兼容性评分 (0-1)"""
        score = 0.0
        
        # 基础兼容性 (40%)
        if model_info["type"] in agent_info["preferred_model_types"]:
            score += 0.4
        
        # 上下文长度适配性 (30%)
        context_ratio = model_info["context_length"] / agent_info["min_context_length"]
        if context_ratio >= 2.0:
            score += 0.3
        elif context_ratio >= 1.5:
            score += 0.2
        elif context_ratio >= 1.0:
            score += 0.1
        
        # 性能优先级匹配 (30%)
        performance_priority = agent_info["performance_priority"]
        if performance_priority == "speed" and "turbo" in model_info["id"].lower():
            score += 0.3
        elif performance_priority == "accuracy" and any(keyword in model_info["id"].lower() 
                                                       for keyword in ["pro", "max", "plus"]):
            score += 0.3
        elif performance_priority == "depth" and model_info["context_length"] >= 16384:
            score += 0.3
        else:
            score += 0.1
        
        return min(score, 1.0)
    
    def _get_compatibility_recommendation(self, score: float) -> str:
        """根据兼容性评分获取推荐建议"""
        if score >= 0.8:
            return "强烈推荐 - 高度兼容"
        elif score >= 0.6:
            return "推荐 - 良好兼容"
        elif score >= 0.4:
            return "可用 - 基本兼容"
        else:
            return "不推荐 - 兼容性较差"
    
    def get_recommended_models(self, agent_id: str, available_models: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """获取智能体的推荐模型列表"""
        try:
            agent_info = self.get_agent_info(agent_id)
            if not agent_info:
                return []
            
            recommendations = []
            
            for provider, models in available_models.items():
                for model_info in models:
                    compatibility = self.validate_model_compatibility(
                        agent_id, provider, model_info["id"], available_models
                    )
                    
                    if compatibility["compatible"] and compatibility["score"] >= 0.4:
                        recommendations.append({
                            "provider": provider,
                            "model": model_info["id"],
                            "model_name": model_info["name"],
                            "score": compatibility["score"],
                            "recommendation": compatibility["recommendation"],
                            "model_info": model_info
                        })
            
            # 按评分排序
            recommendations.sort(key=lambda x: x["score"], reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"获取推荐模型失败: {e}")
            return []
    
    def batch_update_agents(self, updates: List[Dict[str, str]]) -> Dict[str, Any]:
        """批量更新智能体模型配置"""
        try:
            success_count = 0
            error_count = 0
            errors = []
            
            for update in updates:
                agent_id = update.get("agent_id")
                provider = update.get("provider")
                model = update.get("model")
                
                if not all([agent_id, provider, model]):
                    errors.append(f"更新项缺少必需字段: {update}")
                    error_count += 1
                    continue
                
                result = self.update_agent_model(agent_id, provider, model)
                if result["status"] == "success":
                    success_count += 1
                else:
                    errors.append(f"{agent_id}: {result['message']}")
                    error_count += 1
            
            return {
                "status": "success" if error_count == 0 else "partial",
                "message": f"成功更新 {success_count} 个智能体，失败 {error_count} 个",
                "success_count": success_count,
                "error_count": error_count,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"批量更新智能体失败: {e}")
            return {"status": "error", "message": f"批量更新失败: {str(e)}"}
    
    def reset_to_defaults(self) -> Dict[str, Any]:
        """重置所有智能体为默认模型配置"""
        try:
            self.agent_model_config = self._get_default_agent_config()
            result = self.save_agent_config()
            
            if result["status"] == "success":
                logger.info("智能体模型配置已重置为默认值")
                return {"status": "success", "message": "已重置为默认配置"}
            else:
                return result
                
        except Exception as e:
            logger.error(f"重置默认配置失败: {e}")
            return {"status": "error", "message": f"重置失败: {str(e)}"}
