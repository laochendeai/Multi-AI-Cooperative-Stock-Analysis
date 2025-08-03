"""
信号处理器 - 处理智能体间的信号传递和协调
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)

class SignalType(Enum):
    """信号类型枚举"""
    ANALYSIS_COMPLETE = "analysis_complete"
    DEBATE_REQUEST = "debate_request"
    DECISION_REQUIRED = "decision_required"
    RISK_ALERT = "risk_alert"
    DATA_UPDATE = "data_update"
    WORKFLOW_CONTROL = "workflow_control"

class SignalPriority(Enum):
    """信号优先级枚举"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class Signal:
    """信号对象"""
    
    def __init__(self, signal_type: SignalType, sender: str, receiver: str = None, 
                 data: Dict[str, Any] = None, priority: SignalPriority = SignalPriority.MEDIUM):
        self.id = f"signal_{datetime.now().timestamp()}"
        self.signal_type = signal_type
        self.sender = sender
        self.receiver = receiver  # None表示广播
        self.data = data or {}
        self.priority = priority
        self.timestamp = datetime.now()
        self.processed = False
        self.response = None

class SignalProcessor:
    """信号处理器"""
    
    def __init__(self):
        self.signal_queue = asyncio.Queue()
        self.signal_handlers = {}
        self.signal_history = []
        self.active_signals = {}
        self.processing = False
        
        # 注册默认信号处理器
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """注册默认信号处理器"""
        self.signal_handlers[SignalType.ANALYSIS_COMPLETE] = self._handle_analysis_complete
        self.signal_handlers[SignalType.DEBATE_REQUEST] = self._handle_debate_request
        self.signal_handlers[SignalType.DECISION_REQUIRED] = self._handle_decision_required
        self.signal_handlers[SignalType.RISK_ALERT] = self._handle_risk_alert
        self.signal_handlers[SignalType.DATA_UPDATE] = self._handle_data_update
        self.signal_handlers[SignalType.WORKFLOW_CONTROL] = self._handle_workflow_control
    
    async def send_signal(self, signal: Signal) -> str:
        """发送信号"""
        try:
            # 添加到队列
            await self.signal_queue.put(signal)
            
            # 记录活跃信号
            self.active_signals[signal.id] = signal
            
            logger.debug(f"信号已发送: {signal.signal_type.value} from {signal.sender} to {signal.receiver}")
            return signal.id
            
        except Exception as e:
            logger.error(f"发送信号失败: {e}")
            return ""
    
    async def broadcast_signal(self, signal_type: SignalType, sender: str, 
                             data: Dict[str, Any] = None, priority: SignalPriority = SignalPriority.MEDIUM) -> str:
        """广播信号"""
        signal = Signal(signal_type, sender, None, data, priority)
        return await self.send_signal(signal)
    
    async def send_direct_signal(self, signal_type: SignalType, sender: str, receiver: str,
                                data: Dict[str, Any] = None, priority: SignalPriority = SignalPriority.MEDIUM) -> str:
        """发送直接信号"""
        signal = Signal(signal_type, sender, receiver, data, priority)
        return await self.send_signal(signal)
    
    async def start_processing(self):
        """开始处理信号"""
        if self.processing:
            logger.warning("信号处理器已在运行")
            return
        
        self.processing = True
        logger.info("信号处理器开始运行")
        
        try:
            while self.processing:
                try:
                    # 获取信号（带超时）
                    signal = await asyncio.wait_for(self.signal_queue.get(), timeout=1.0)
                    
                    # 处理信号
                    await self._process_signal(signal)
                    
                except asyncio.TimeoutError:
                    # 超时是正常的，继续循环
                    continue
                except Exception as e:
                    logger.error(f"处理信号时发生错误: {e}")
                    
        except Exception as e:
            logger.error(f"信号处理器运行失败: {e}")
        finally:
            self.processing = False
            logger.info("信号处理器已停止")
    
    async def stop_processing(self):
        """停止处理信号"""
        self.processing = False
        logger.info("信号处理器停止请求已发送")
    
    async def _process_signal(self, signal: Signal):
        """处理单个信号"""
        try:
            logger.debug(f"处理信号: {signal.signal_type.value} from {signal.sender}")
            
            # 获取处理器
            handler = self.signal_handlers.get(signal.signal_type)
            if handler:
                # 执行处理器
                response = await handler(signal)
                signal.response = response
            else:
                logger.warning(f"未找到信号处理器: {signal.signal_type.value}")
                signal.response = {"error": "No handler found"}
            
            # 标记为已处理
            signal.processed = True
            
            # 移除活跃信号
            if signal.id in self.active_signals:
                del self.active_signals[signal.id]
            
            # 添加到历史记录
            self.signal_history.append({
                "signal_id": signal.id,
                "signal_type": signal.signal_type.value,
                "sender": signal.sender,
                "receiver": signal.receiver,
                "timestamp": signal.timestamp.isoformat(),
                "processed": signal.processed,
                "response": signal.response
            })
            
            # 限制历史记录长度
            if len(self.signal_history) > 1000:
                self.signal_history = self.signal_history[-500:]
            
        except Exception as e:
            logger.error(f"处理信号失败: {e}")
            signal.response = {"error": str(e)}
            signal.processed = True
    
    async def _handle_analysis_complete(self, signal: Signal) -> Dict[str, Any]:
        """处理分析完成信号"""
        try:
            agent_id = signal.data.get("agent_id", "")
            analysis_result = signal.data.get("analysis_result", {})
            
            logger.info(f"智能体 {agent_id} 完成分析")
            
            # 可以在这里添加分析结果的后处理逻辑
            # 例如：通知其他智能体、更新状态等
            
            return {
                "status": "processed",
                "message": f"Analysis from {agent_id} processed successfully"
            }
            
        except Exception as e:
            logger.error(f"处理分析完成信号失败: {e}")
            return {"error": str(e)}
    
    async def _handle_debate_request(self, signal: Signal) -> Dict[str, Any]:
        """处理辩论请求信号"""
        try:
            requester = signal.data.get("requester", "")
            debate_topic = signal.data.get("topic", "")
            participants = signal.data.get("participants", [])
            
            logger.info(f"收到辩论请求: {debate_topic} from {requester}")
            
            # 可以在这里添加辩论协调逻辑
            # 例如：安排辩论时间、通知参与者等
            
            return {
                "status": "debate_scheduled",
                "topic": debate_topic,
                "participants": participants
            }
            
        except Exception as e:
            logger.error(f"处理辩论请求信号失败: {e}")
            return {"error": str(e)}
    
    async def _handle_decision_required(self, signal: Signal) -> Dict[str, Any]:
        """处理决策需求信号"""
        try:
            decision_type = signal.data.get("decision_type", "")
            context = signal.data.get("context", {})
            
            logger.info(f"收到决策需求: {decision_type}")
            
            # 可以在这里添加决策协调逻辑
            # 例如：收集相关信息、通知决策者等
            
            return {
                "status": "decision_pending",
                "decision_type": decision_type
            }
            
        except Exception as e:
            logger.error(f"处理决策需求信号失败: {e}")
            return {"error": str(e)}
    
    async def _handle_risk_alert(self, signal: Signal) -> Dict[str, Any]:
        """处理风险警报信号"""
        try:
            risk_level = signal.data.get("risk_level", "")
            risk_description = signal.data.get("description", "")
            
            logger.warning(f"收到风险警报: {risk_level} - {risk_description}")
            
            # 可以在这里添加风险处理逻辑
            # 例如：通知风险管理团队、暂停交易等
            
            return {
                "status": "risk_acknowledged",
                "risk_level": risk_level,
                "action_taken": "Risk management team notified"
            }
            
        except Exception as e:
            logger.error(f"处理风险警报信号失败: {e}")
            return {"error": str(e)}
    
    async def _handle_data_update(self, signal: Signal) -> Dict[str, Any]:
        """处理数据更新信号"""
        try:
            data_type = signal.data.get("data_type", "")
            update_info = signal.data.get("update_info", {})
            
            logger.info(f"收到数据更新: {data_type}")
            
            # 可以在这里添加数据更新处理逻辑
            # 例如：通知相关智能体、刷新缓存等
            
            return {
                "status": "data_updated",
                "data_type": data_type
            }
            
        except Exception as e:
            logger.error(f"处理数据更新信号失败: {e}")
            return {"error": str(e)}
    
    async def _handle_workflow_control(self, signal: Signal) -> Dict[str, Any]:
        """处理工作流控制信号"""
        try:
            control_action = signal.data.get("action", "")
            parameters = signal.data.get("parameters", {})
            
            logger.info(f"收到工作流控制: {control_action}")
            
            # 可以在这里添加工作流控制逻辑
            # 例如：暂停/恢复工作流、调整参数等
            
            return {
                "status": "workflow_controlled",
                "action": control_action
            }
            
        except Exception as e:
            logger.error(f"处理工作流控制信号失败: {e}")
            return {"error": str(e)}
    
    def register_handler(self, signal_type: SignalType, handler: Callable):
        """注册自定义信号处理器"""
        self.signal_handlers[signal_type] = handler
        logger.info(f"注册信号处理器: {signal_type.value}")
    
    def get_signal_status(self) -> Dict[str, Any]:
        """获取信号处理状态"""
        return {
            "processing": self.processing,
            "queue_size": self.signal_queue.qsize(),
            "active_signals": len(self.active_signals),
            "total_processed": len(self.signal_history),
            "handlers_registered": len(self.signal_handlers)
        }
    
    def get_signal_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取信号历史"""
        return self.signal_history[-limit:] if self.signal_history else []
    
    def get_active_signals(self) -> List[Dict[str, Any]]:
        """获取活跃信号"""
        active = []
        for signal in self.active_signals.values():
            active.append({
                "signal_id": signal.id,
                "signal_type": signal.signal_type.value,
                "sender": signal.sender,
                "receiver": signal.receiver,
                "priority": signal.priority.value,
                "timestamp": signal.timestamp.isoformat()
            })
        return active
    
    async def wait_for_signal_response(self, signal_id: str, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """等待信号响应"""
        try:
            start_time = datetime.now()
            
            while (datetime.now() - start_time).seconds < timeout:
                # 检查信号是否已处理
                if signal_id not in self.active_signals:
                    # 在历史记录中查找响应
                    for record in reversed(self.signal_history):
                        if record["signal_id"] == signal_id:
                            return record["response"]
                    break
                
                # 短暂等待
                await asyncio.sleep(0.1)
            
            logger.warning(f"等待信号响应超时: {signal_id}")
            return None
            
        except Exception as e:
            logger.error(f"等待信号响应失败: {e}")
            return None
