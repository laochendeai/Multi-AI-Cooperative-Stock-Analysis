#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents 智能体结果提取修复脚本
修复智能体结果提取和数据解析问题
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analyze_agent_result_structure():
    """分析智能体结果结构"""
    print("🔍 分析智能体结果结构...")
    
    # 模拟智能体返回的数据结构
    sample_agent_results = {
        "social_media_analyst": {
            "status": "success",
            "agent_id": "social_media_analyst",
            "agent_type": "情感分析师",
            "analysis_type": "sentiment_analysis",
            "symbol": "000001",
            "content": {
                "sentiment_score": 0.65,
                "market_mood": "乐观",
                "discussion_volume": "高",
                "key_topics": ["业绩增长", "市场前景", "政策利好"],
                "analysis_summary": "基于社交媒体数据分析，投资者对该股票整体情绪偏向乐观..."
            },
            "raw_response": "详细的LLM分析响应...",
            "timestamp": "2025-08-15T18:39:30.795480"
        },
        "market_analyst": {
            "status": "success",
            "agent_id": "market_analyst",
            "content": "技术分析结果：该股票当前处于上升趋势...",
            "confidence": 0.8,
            "timestamp": "2025-08-15T18:39:30.795480"
        }
    }
    
    print("📊 智能体结果结构分析:")
    for agent_id, result in sample_agent_results.items():
        print(f"\n🤖 {agent_id}:")
        print(f"   数据类型: {type(result)}")
        print(f"   可用键: {list(result.keys())}")
        
        # 分析content字段
        content = result.get("content")
        if content:
            print(f"   content类型: {type(content)}")
            if isinstance(content, dict):
                print(f"   content键: {list(content.keys())}")
            elif isinstance(content, str):
                print(f"   content长度: {len(content)}")
    
    return sample_agent_results

def create_enhanced_extraction_function():
    """创建增强的结果提取函数"""
    print("\n🔧 创建增强的结果提取函数...")
    
    enhanced_extraction_code = '''
def extract_agent_result_enhanced(agent_data, agent_key):
    """
    增强版智能体结果提取函数
    
    Args:
        agent_data: 智能体返回的数据
        agent_key: 智能体标识符
        
    Returns:
        标准化的智能体结果
    """
    import logging
    from datetime import datetime
    
    logger = logging.getLogger(__name__)
    
    if not agent_data:
        return {
            "agent_id": agent_key,
            "analysis": "智能体数据为空",
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat(),
            "status": "no_data"
        }
    
    analysis_content = ""
    confidence = 0.5
    timestamp = datetime.now().isoformat()
    status = "success"
    
    try:
        # 处理不同的数据结构
        if isinstance(agent_data, dict):
            # 优先级1: 直接从content字段提取
            content = agent_data.get("content")
            if content:
                if isinstance(content, str) and len(content.strip()) > 10:
                    analysis_content = content.strip()
                elif isinstance(content, dict):
                    # 从content字典中提取分析内容
                    analysis_parts = []
                    
                    # 查找分析摘要
                    for key in ["analysis_summary", "summary", "analysis", "result"]:
                        if key in content and isinstance(content[key], str):
                            analysis_parts.append(content[key])
                    
                    # 查找其他有用信息
                    for key, value in content.items():
                        if key not in ["analysis_summary", "summary", "analysis", "result"]:
                            if isinstance(value, str) and len(value.strip()) > 5:
                                analysis_parts.append(f"{key}: {value}")
                            elif isinstance(value, (int, float)):
                                analysis_parts.append(f"{key}: {value}")
                            elif isinstance(value, list) and value:
                                analysis_parts.append(f"{key}: {', '.join(map(str, value))}")
                    
                    if analysis_parts:
                        analysis_content = "\\n".join(analysis_parts)
            
            # 优先级2: 从raw_response提取
            if not analysis_content:
                raw_response = agent_data.get("raw_response", "")
                if isinstance(raw_response, str) and len(raw_response.strip()) > 10:
                    analysis_content = raw_response.strip()
            
            # 优先级3: 从其他字段提取
            if not analysis_content:
                for key in ["analysis", "result", "output", "response"]:
                    value = agent_data.get(key)
                    if isinstance(value, str) and len(value.strip()) > 10:
                        analysis_content = value.strip()
                        break
            
            # 提取元数据
            confidence = agent_data.get("confidence", 0.5)
            timestamp = agent_data.get("timestamp", datetime.now().isoformat())
            
            # 检查状态
            agent_status = agent_data.get("status", "unknown")
            if agent_status == "error":
                status = "error"
                error_msg = agent_data.get("error", "未知错误")
                analysis_content = f"分析失败: {error_msg}"
            elif agent_status == "success" and analysis_content:
                status = "success"
            else:
                status = "no_content"
        
        elif isinstance(agent_data, str):
            # 直接是字符串结果
            if len(agent_data.strip()) > 10:
                analysis_content = agent_data.strip()
                status = "success"
        
        # 如果仍然没有内容，记录详细信息
        if not analysis_content:
            logger.warning(f"无法从{agent_key}提取有效内容")
            logger.warning(f"数据类型: {type(agent_data)}")
            
            if isinstance(agent_data, dict):
                logger.warning(f"可用键: {list(agent_data.keys())}")
                for k, v in agent_data.items():
                    if isinstance(v, str):
                        logger.warning(f"  {k}: str({len(v)}) = '{v[:50]}...'")
                    else:
                        logger.warning(f"  {k}: {type(v)} = {str(v)[:50]}")
            
            analysis_content = "分析结果不可用"
            status = "no_content"
        
        return {
            "agent_id": agent_key,
            "analysis": analysis_content,
            "confidence": float(confidence) if isinstance(confidence, (int, float)) else 0.5,
            "timestamp": timestamp,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"提取{agent_key}结果时发生错误: {e}")
        return {
            "agent_id": agent_key,
            "analysis": f"结果提取失败: {str(e)}",
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat(),
            "status": "error"
        }
'''
    
    print("✅ 增强版结果提取函数创建完成")
    return enhanced_extraction_code

def test_extraction_function():
    """测试结果提取函数"""
    print("\n🧪 测试结果提取函数...")
    
    # 创建测试数据
    test_cases = [
        {
            "name": "正常的字典结构（带content字典）",
            "data": {
                "status": "success",
                "agent_id": "social_media_analyst",
                "content": {
                    "analysis_summary": "基于社交媒体数据分析，投资者情绪偏向乐观",
                    "sentiment_score": 0.65,
                    "market_mood": "乐观"
                },
                "confidence": 0.8,
                "timestamp": "2025-08-15T18:39:30.795480"
            }
        },
        {
            "name": "简单字符串content",
            "data": {
                "status": "success",
                "content": "这是一个详细的技术分析结果，包含多项指标分析...",
                "confidence": 0.7
            }
        },
        {
            "name": "错误状态",
            "data": {
                "status": "error",
                "error": "网络连接失败",
                "agent_id": "news_analyst"
            }
        },
        {
            "name": "空内容",
            "data": {
                "status": "success",
                "content": "",
                "agent_id": "market_analyst"
            }
        },
        {
            "name": "只有raw_response",
            "data": {
                "raw_response": "这是LLM返回的原始分析结果，包含详细的市场分析...",
                "status": "success"
            }
        }
    ]
    
    # 执行测试（这里只是模拟，实际需要导入函数）
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   测试{i}: {test_case['name']}")
        data = test_case['data']
        
        # 模拟提取逻辑
        if isinstance(data, dict):
            content = data.get("content")
            if content:
                if isinstance(content, str) and len(content.strip()) > 10:
                    result = "✅ 成功提取字符串内容"
                elif isinstance(content, dict):
                    analysis_parts = []
                    for key in ["analysis_summary", "summary", "analysis"]:
                        if key in content:
                            analysis_parts.append(content[key])
                    result = "✅ 成功提取字典内容" if analysis_parts else "⚠️ 字典内容为空"
                else:
                    result = "⚠️ content为空"
            elif data.get("raw_response"):
                result = "✅ 从raw_response提取内容"
            elif data.get("status") == "error":
                result = "✅ 正确处理错误状态"
            else:
                result = "❌ 无法提取有效内容"
        else:
            result = "❌ 数据格式不正确"
        
        print(f"      结果: {result}")
    
    print("\n✅ 结果提取函数测试完成")

def create_fix_patch():
    """创建修复补丁"""
    print("\n🔧 创建修复补丁...")
    
    patch_content = '''
# 修复app_tradingagents_upgraded.py中的_extract_agent_result方法

def _extract_agent_result_fixed(self, agent_data, agent_key):
    """
    修复版智能体结果提取方法
    """
    if not agent_data:
        return {
            "agent_id": agent_key,
            "analysis": "智能体数据为空",
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat(),
            "status": "no_data"
        }
    
    analysis_content = ""
    confidence = 0.5
    timestamp = datetime.now().isoformat()
    status = "success"
    
    try:
        if isinstance(agent_data, dict):
            # 优先级1: 从content字段提取
            content = agent_data.get("content")
            if content:
                if isinstance(content, str) and len(content.strip()) > 10:
                    analysis_content = content.strip()
                elif isinstance(content, dict):
                    # 从content字典中提取分析内容
                    analysis_parts = []
                    
                    # 查找分析摘要
                    for key in ["analysis_summary", "summary", "analysis", "result"]:
                        if key in content and isinstance(content[key], str) and len(content[key].strip()) > 10:
                            analysis_parts.append(f"{key}: {content[key].strip()}")
                    
                    # 查找其他有用信息
                    for key, value in content.items():
                        if key not in ["analysis_summary", "summary", "analysis", "result"]:
                            if isinstance(value, str) and len(value.strip()) > 5:
                                analysis_parts.append(f"{key}: {value.strip()}")
                            elif isinstance(value, (int, float)):
                                analysis_parts.append(f"{key}: {value}")
                            elif isinstance(value, list) and value:
                                analysis_parts.append(f"{key}: {', '.join(map(str, value))}")
                    
                    if analysis_parts:
                        analysis_content = "\\n".join(analysis_parts)
            
            # 优先级2: 从raw_response提取
            if not analysis_content:
                raw_response = agent_data.get("raw_response", "")
                if isinstance(raw_response, str) and len(raw_response.strip()) > 10:
                    analysis_content = raw_response.strip()
            
            # 优先级3: 从其他字段提取
            if not analysis_content:
                for key in ["analysis", "result", "output", "response"]:
                    value = agent_data.get(key)
                    if isinstance(value, str) and len(value.strip()) > 10:
                        analysis_content = value.strip()
                        break
            
            # 提取元数据
            confidence = agent_data.get("confidence", 0.5)
            timestamp = agent_data.get("timestamp", datetime.now().isoformat())
            
            # 检查状态
            agent_status = agent_data.get("status", "unknown")
            if agent_status == "error":
                status = "error"
                error_msg = agent_data.get("error", "未知错误")
                analysis_content = f"分析失败: {error_msg}"
            elif agent_status == "success" and analysis_content:
                status = "success"
            else:
                status = "no_content"
        
        elif isinstance(agent_data, str) and len(agent_data.strip()) > 10:
            analysis_content = agent_data.strip()
            status = "success"
        
        # 如果仍然没有内容
        if not analysis_content:
            logger.warning(f"无法从{agent_key}提取有效内容")
            logger.warning(f"数据类型: {type(agent_data)}")
            
            if isinstance(agent_data, dict):
                logger.warning(f"可用键: {list(agent_data.keys())}")
                for k, v in agent_data.items():
                    if isinstance(v, str):
                        logger.warning(f"  {k}: str({len(v)}) = '{v[:50]}...'")
                    else:
                        logger.warning(f"  {k}: {type(v)} = {str(v)[:50]}")
            
            analysis_content = "分析结果不可用"
            status = "no_content"
        
        return {
            "agent_id": agent_key,
            "analysis": analysis_content,
            "confidence": float(confidence) if isinstance(confidence, (int, float)) else 0.5,
            "timestamp": timestamp,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"提取{agent_key}结果时发生错误: {e}")
        return {
            "agent_id": agent_key,
            "analysis": f"结果提取失败: {str(e)}",
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat(),
            "status": "error"
        }
'''
    
    print("✅ 修复补丁创建完成")
    return patch_content

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 TradingAgents 智能体结果提取修复")
    print("=" * 60)
    print(f"📅 修复时间: {datetime.now()}")
    print()
    
    # 分析问题
    print("🔍 问题分析:")
    print("   1. TradingGraph智能体状态不可用")
    print("   2. social_media_analyst返回内容为空")
    print("   3. 结果提取逻辑无法正确解析数据结构")
    print()
    
    # 执行修复步骤
    sample_results = analyze_agent_result_structure()
    enhanced_code = create_enhanced_extraction_function()
    test_extraction_function()
    patch_content = create_fix_patch()
    
    print("\n" + "=" * 60)
    print("📊 修复方案总结")
    print("=" * 60)
    
    print("✅ 修复要点:")
    print("   • 增强智能体结果提取逻辑")
    print("   • 支持多种数据结构格式")
    print("   • 改进content字典解析")
    print("   • 添加更好的错误处理")
    print("   • 提供详细的调试信息")
    
    print("\n💡 实施建议:")
    print("   1. 更新app_tradingagents_upgraded.py中的_extract_agent_result方法")
    print("   2. 测试各种智能体返回格式")
    print("   3. 监控智能体分析质量")
    print("   4. 优化智能体提示词")
    
    print("\n🔧 下一步操作:")
    print("   • 应用修复补丁到主代码")
    print("   • 测试修复效果")
    print("   • 监控智能体分析结果")

if __name__ == "__main__":
    main()
