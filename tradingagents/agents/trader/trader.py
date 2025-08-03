"""
交易员 - 基于研究建议制定具体交易策略
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)

class Trader(BaseAgent):
    """专业交易员"""
    
    def __init__(self, llm_client=None, memory_manager=None):
        super().__init__(
            agent_id="trader",
            agent_type="交易员",
            llm_client=llm_client,
            memory_manager=memory_manager
        )
        self.trading_history = []
    
    async def analyze(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        制定交易策略
        
        Args:
            input_data: 包含研究建议、市场数据等
            context: 上下文信息
            
        Returns:
            交易策略结果
        """
        try:
            symbol = input_data.get("symbol", "")
            research_recommendation = input_data.get("research_recommendation", {})
            market_data = input_data.get("market_data", {})
            portfolio_context = input_data.get("portfolio_context", {})
            
            # 构建交易策略提示
            strategy_prompt = self._build_trading_prompt(symbol, research_recommendation, market_data, portfolio_context)
            
            # 获取LLM分析
            llm_response = await self.get_llm_response(strategy_prompt, context)
            
            # 解析和结构化结果
            strategy_result = self._parse_trading_result(llm_response, symbol)
            
            # 记录交易决策
            self.trading_history.append({
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "action": strategy_result.get("trading_action", ""),
                "reasoning": strategy_result.get("strategy_rationale", "")
            })
            
            return {
                "status": "success",
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "analysis_type": "trading_strategy",
                "symbol": symbol,
                "content": strategy_result,
                "raw_response": llm_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"交易策略制定失败: {e}")
            return {
                "status": "error",
                "agent_id": self.agent_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_trading_prompt(self, symbol: str, research_rec: Dict, market_data: Dict, portfolio_context: Dict) -> str:
        """构建交易策略提示"""
        prompt = f"""
作为专业交易员，你需要基于研究团队的投资建议，为股票 {symbol} 制定具体的交易策略。

研究团队建议:
- 投资评级: {research_rec.get('investment_recommendation', 'N/A')}
- 信心水平: {research_rec.get('confidence_level', 'N/A')}
- 建议仓位: {research_rec.get('position_size', 'N/A')}
- 投资时间: {research_rec.get('time_horizon', 'N/A')}
- 决策理由: {research_rec.get('decision_rationale', 'N/A')}

当前市场数据:
- 股票价格: {market_data.get('current_price', 'N/A')}
- 日内波动: {market_data.get('daily_change', 'N/A')}%
- 成交量: {market_data.get('volume', 'N/A')}
- 流动性: {market_data.get('liquidity', 'N/A')}
- 市场情绪: {market_data.get('market_sentiment', 'N/A')}

投资组合情况:
- 可用资金: {portfolio_context.get('available_cash', 'N/A')}
- 当前持仓: {portfolio_context.get('current_positions', 'N/A')}
- 风险敞口: {portfolio_context.get('risk_exposure', 'N/A')}
- 集中度: {portfolio_context.get('concentration', 'N/A')}

请制定详细的交易策略，包括:

1. **交易决策**
   - 明确的交易行动 (买入/卖出/持有/观望)
   - 交易数量和仓位比例
   - 交易优先级评估

2. **入场策略**
   - 最佳入场时机选择
   - 入场价位设定
   - 分批建仓计划
   - 市价vs限价选择

3. **风险管理**
   - 止损位设置 (具体价位)
   - 止盈位设置 (具体价位)
   - 最大亏损容忍度
   - 仓位调整机制

4. **执行计划**
   - 交易时间安排
   - 订单类型选择
   - 执行节奏控制
   - 滑点控制措施

5. **监控要点**
   - 关键技术位监控
   - 基本面变化跟踪
   - 市场情绪变化
   - 流动性状况

6. **应急预案**
   - 突发事件应对
   - 止损触发后的行动
   - 市场异常情况处理

请提供可执行的具体交易策略，确保风险可控且符合投资组合管理要求。
"""
        
        return prompt
    
    def _parse_trading_result(self, llm_response: str, symbol: str) -> Dict[str, Any]:
        """解析交易策略结果"""
        try:
            result = {
                "symbol": symbol,
                "trading_summary": llm_response,
                "trading_action": self._extract_trading_action(llm_response),
                "position_size": self._extract_position_size(llm_response),
                "entry_strategy": self._extract_entry_strategy(llm_response),
                "exit_strategy": self._extract_exit_strategy(llm_response),
                "risk_management": self._extract_risk_management(llm_response),
                "execution_plan": self._extract_execution_plan(llm_response),
                "monitoring_points": self._extract_monitoring_points(llm_response),
                "contingency_plan": self._extract_contingency_plan(llm_response),
                "strategy_rationale": self._extract_strategy_rationale(llm_response),
                "expected_return": self._extract_expected_return(llm_response),
                "max_risk": self._extract_max_risk(llm_response)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"解析交易策略结果失败: {e}")
            return {
                "symbol": symbol,
                "trading_summary": llm_response,
                "trading_action": "观望",
                "position_size": "0%"
            }
    
    def _extract_trading_action(self, text: str) -> str:
        """提取交易行动"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["买入", "建仓", "加仓", "购买"]):
            return "买入"
        elif any(word in text_lower for word in ["卖出", "平仓", "减仓", "出售"]):
            return "卖出"
        elif any(word in text_lower for word in ["持有", "维持", "不变"]):
            return "持有"
        else:
            return "观望"
    
    def _extract_position_size(self, text: str) -> str:
        """提取仓位大小"""
        import re
        
        # 查找仓位相关的数字
        position_patterns = [
            r'仓位[：:]\s*(\d+\.?\d*)%',
            r'建仓[：:]\s*(\d+\.?\d*)%',
            r'买入[：:]\s*(\d+\.?\d*)%',
            r'(\d+\.?\d*)%\s*仓位'
        ]
        
        for pattern in position_patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)}%"
        
        return "待定"
    
    def _extract_entry_strategy(self, text: str) -> Dict[str, str]:
        """提取入场策略"""
        strategy = {}
        
        # 入场方式
        if "分批" in text.lower():
            strategy["method"] = "分批建仓"
        elif "一次性" in text.lower():
            strategy["method"] = "一次性建仓"
        else:
            strategy["method"] = "灵活建仓"
        
        # 订单类型
        if "市价" in text.lower():
            strategy["order_type"] = "市价单"
        elif "限价" in text.lower():
            strategy["order_type"] = "限价单"
        else:
            strategy["order_type"] = "智能单"
        
        # 入场时机
        import re
        timing_match = re.search(r'时机[：:]([^。\n]+)', text)
        if timing_match:
            strategy["timing"] = timing_match.group(1).strip()
        else:
            strategy["timing"] = "择机而入"
        
        return strategy
    
    def _extract_exit_strategy(self, text: str) -> Dict[str, str]:
        """提取出场策略"""
        strategy = {}
        
        # 止损位
        import re
        stop_loss_patterns = [
            r'止损[：:]\s*(\d+\.?\d*)',
            r'止损位[：:]\s*(\d+\.?\d*)',
            r'止损价[：:]\s*(\d+\.?\d*)'
        ]
        
        for pattern in stop_loss_patterns:
            match = re.search(pattern, text)
            if match:
                strategy["stop_loss"] = match.group(1)
                break
        else:
            strategy["stop_loss"] = "技术位"
        
        # 止盈位
        take_profit_patterns = [
            r'止盈[：:]\s*(\d+\.?\d*)',
            r'止盈位[：:]\s*(\d+\.?\d*)',
            r'目标价[：:]\s*(\d+\.?\d*)'
        ]
        
        for pattern in take_profit_patterns:
            match = re.search(pattern, text)
            if match:
                strategy["take_profit"] = match.group(1)
                break
        else:
            strategy["take_profit"] = "分批止盈"
        
        return strategy
    
    def _extract_risk_management(self, text: str) -> Dict[str, str]:
        """提取风险管理措施"""
        risk_mgmt = {}
        
        # 最大亏损
        import re
        max_loss_match = re.search(r'最大亏损[：:]\s*(\d+\.?\d*)%', text)
        if max_loss_match:
            risk_mgmt["max_loss"] = f"{max_loss_match.group(1)}%"
        else:
            risk_mgmt["max_loss"] = "5%"
        
        # 风险控制方式
        if "动态调整" in text.lower():
            risk_mgmt["control_method"] = "动态调整"
        elif "固定止损" in text.lower():
            risk_mgmt["control_method"] = "固定止损"
        else:
            risk_mgmt["control_method"] = "灵活控制"
        
        return risk_mgmt
    
    def _extract_execution_plan(self, text: str) -> Dict[str, str]:
        """提取执行计划"""
        plan = {}
        
        # 执行时间
        if "开盘" in text.lower():
            plan["timing"] = "开盘时段"
        elif "收盘" in text.lower():
            plan["timing"] = "收盘时段"
        elif "盘中" in text.lower():
            plan["timing"] = "盘中择机"
        else:
            plan["timing"] = "全天候"
        
        # 执行节奏
        if "快速" in text.lower():
            plan["pace"] = "快速执行"
        elif "缓慢" in text.lower():
            plan["pace"] = "缓慢执行"
        else:
            plan["pace"] = "正常节奏"
        
        return plan
    
    def _extract_monitoring_points(self, text: str) -> List[str]:
        """提取监控要点"""
        points = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["监控", "关注", "跟踪", "观察"]):
                point = line.strip()
                if point and len(point) > 10:
                    points.append(point)
        
        return points[:5]  # 最多返回5个监控要点
    
    def _extract_contingency_plan(self, text: str) -> List[str]:
        """提取应急预案"""
        plans = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["应急", "预案", "突发", "异常"]):
                plan = line.strip()
                if plan and len(plan) > 10:
                    plans.append(plan)
        
        return plans[:3]  # 最多返回3个应急预案
    
    def _extract_strategy_rationale(self, text: str) -> str:
        """提取策略理由"""
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["理由", "原因", "基于", "考虑"]):
                if len(line.strip()) > 20:
                    return line.strip()
        
        # 如果没有明确的理由，返回前几句
        sentences = text.split('。')
        if sentences:
            return sentences[0][:150] + "..." if len(sentences[0]) > 150 else sentences[0]
        
        return "基于研究建议的交易策略"
    
    def _extract_expected_return(self, text: str) -> str:
        """提取预期收益"""
        import re
        
        return_patterns = [
            r'预期收益[：:]\s*(\d+\.?\d*)%',
            r'目标收益[：:]\s*(\d+\.?\d*)%',
            r'收益预期[：:]\s*(\d+\.?\d*)%'
        ]
        
        for pattern in return_patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)}%"
        
        return "待评估"
    
    def _extract_max_risk(self, text: str) -> str:
        """提取最大风险"""
        import re
        
        risk_patterns = [
            r'最大风险[：:]\s*(\d+\.?\d*)%',
            r'风险上限[：:]\s*(\d+\.?\d*)%',
            r'最大亏损[：:]\s*(\d+\.?\d*)%'
        ]
        
        for pattern in risk_patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)}%"
        
        return "5%"
