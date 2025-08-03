import asyncio
import logging
import time
from typing import Dict, Any, List
from core.secure_llm_manager import SecureLLMClient, LLMSlotConfig

logger = logging.getLogger(__name__)

class GradioLLMOrchestrator:
    def __init__(self):
        self.llm_slots = {
            'analyzer': LLMSlotConfig("<SLOT_A>", "deepseek", "主分析引擎"),
            'sentiment': LLMSlotConfig("<SLOT_B>", "openai", "情感分析引擎"),
            'coder': LLMSlotConfig("<SLOT_C>", "groq", "代码生成引擎"),
            'multimodal': LLMSlotConfig("<SLOT_D>", "google", "多模态引擎"),
            'lightweight': LLMSlotConfig("<SLOT_E>", "moonshot", "轻量级引擎")
        }
        self.clients = {}
        self.state_manager = CrossLLMStateManager()
    
    async def initialize_clients(self):
        """异步初始化所有LLM客户端"""
        for role, config in self.llm_slots.items():
            self.clients[role] = SecureLLMClient(config.slot_id, config.provider)
            await self.clients[role].initialize()
    
    async def process_parallel(self, input_data: str, context: Dict) -> Dict[str, Any]:
        """并行处理多LLM协作"""
        logger.info(f"Starting parallel LLM processing for input: {input_data[:100]}...")

        if not self.clients:
            logger.info("Initializing LLM clients...")
            await self.initialize_clients()

        tasks = []

        # 根据输入类型确定参与的LLM
        if self._requires_code_analysis(input_data):
            logger.debug("Adding code analysis task")
            tasks.append(self._analyze_code(input_data, context))

        if self._requires_sentiment_analysis(input_data):
            logger.debug("Adding sentiment analysis task")
            tasks.append(self._analyze_sentiment(input_data, context))

        # 主分析始终执行
        logger.debug("Adding main analysis task")
        tasks.append(self._main_analysis(input_data, context))

        logger.info(f"Executing {len(tasks)} parallel tasks")
        # 并行执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 整合结果
        integrated_result = await self._integrate_parallel_results(results, context)
        logger.info("Parallel processing completed")
        return integrated_result
    
    def _requires_code_analysis(self, input_data: str) -> bool:
        """判断是否需要代码分析"""
        code_keywords = ['代码', 'code', 'python', 'function', 'class', '函数']
        return any(keyword in input_data.lower() for keyword in code_keywords)
    
    def _requires_sentiment_analysis(self, input_data: str) -> bool:
        """判断是否需要情感分析"""
        sentiment_keywords = ['情感', '新闻', '舆情', 'sentiment', 'news']
        return any(keyword in input_data.lower() for keyword in sentiment_keywords)
    
    async def _analyze_code(self, input_data: str, context: Dict) -> Dict:
        """代码分析任务"""
        context_with_role = {**context, "system_prompt": "你是专业的代码分析师"}
        return await self.clients['coder'].process_async(input_data, context_with_role)
    
    async def _analyze_sentiment(self, input_data: str, context: Dict) -> Dict:
        """情感分析任务"""
        context_with_role = {**context, "system_prompt": "你是专业的情感分析师"}
        return await self.clients['sentiment'].process_async(input_data, context_with_role)
    
    async def _main_analysis(self, input_data: str, context: Dict) -> Dict:
        """主分析任务"""
        context_with_role = {**context, "system_prompt": "你是专业的股票分析师"}
        return await self.clients['analyzer'].process_async(input_data, context_with_role)
    
    async def _integrate_parallel_results(self, results: List, context: Dict) -> Dict:
        """整合并行处理结果"""
        integrated_result = {
            "timestamp": time.time(),
            "results": [],
            "summary": "",
            "context_updates": {}
        }
        
        for result in results:
            if isinstance(result, Exception):
                integrated_result["results"].append({
                    "status": "error",
                    "error": str(result)
                })
            else:
                integrated_result["results"].append(result)
        
        # 生成综合摘要
        successful_results = [r for r in integrated_result["results"] if r.get("status") == "success"]
        if successful_results:
            integrated_result["summary"] = self._generate_summary(successful_results)
        
        return integrated_result
    
    def _generate_summary(self, results: List[Dict]) -> str:
        """生成结果摘要"""
        contents = [r.get("content", "") for r in results if r.get("content")]
        return f"基于{len(contents)}个AI引擎的综合分析结果"

class CrossLLMStateManager:
    def __init__(self):
        self.shared_context = {}
        self.llm_specific_states = {}
        self.sync_locks = {}
    
    async def sync_context(self, llm_id: str, local_state: Dict) -> Dict:
        """同步LLM间的上下文状态"""
        if llm_id not in self.sync_locks:
            self.sync_locks[llm_id] = asyncio.Lock()
            
        async with self.sync_locks[llm_id]:
            # 更新共享上下文
            self.shared_context.update(local_state.get('shared', {}))
            
            # 保存LLM特定状态
            self.llm_specific_states[llm_id] = local_state.get('private', {})
            
            return {
                'shared': self.shared_context.copy(),
                'private': self.llm_specific_states.get(llm_id, {}),
                'global_state': self._compute_global_state()
            }
    
    def _compute_global_state(self) -> Dict:
        """计算全局状态摘要"""
        return {
            'active_llms': list(self.llm_specific_states.keys()),
            'context_version': hash(str(self.shared_context)),
            'last_sync': time.time()
        }

    async def process_async(self, prompt: str, context: dict = None) -> dict:
        """异步处理单个LLM请求"""
        try:
            if not self.clients:
                await self.initialize_clients()

            # 使用主分析引擎
            if 'analyzer' in self.clients:
                result = await self.clients['analyzer'].generate_async(prompt, context or {})
                return {
                    'status': 'success',
                    'content': result.get('content', ''),
                    'provider': 'analyzer'
                }
            else:
                # 模拟响应
                return {
                    'status': 'success',
                    'content': f"模拟LLM响应: {prompt[:100]}...",
                    'provider': 'mock'
                }

        except Exception as e:
            logger.error(f"异步LLM处理失败: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'content': f"LLM处理失败，使用模拟响应: {prompt[:50]}..."
            }