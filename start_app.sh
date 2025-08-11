#!/bin/bash
# Multi-AI-Cooperative-Stock-Analysis 启动脚本
# 适用于Linux/macOS系统

echo "========================================"
echo " Multi-AI-Cooperative-Stock-Analysis"
echo " 多智能体协作股票分析系统"
echo "========================================"

# 检查虚拟环境是否存在
if [ -d "aistock" ]; then
    echo "正在激活虚拟环境 aistock..."
    source aistock/bin/activate
else
    echo "警告: 虚拟环境 'aistock' 未找到，将使用全局Python环境"
    echo "建议创建虚拟环境: python3 -m venv aistock"
    echo ""
fi

# 检查Python是否可用
if ! command -v python &> /dev/null; then
    echo "错误: Python未安装或未添加到PATH"
    read -p "按任意键退出..."
    exit 1
fi

# 检查依赖是否安装
echo "检查依赖..."
python -c "import gradio" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "正在安装依赖..."
    pip install -r requirements.txt
fi

# 启动主程序
echo "正在启动主程序..."
echo "访问 http://localhost:7860 查看应用"
echo "按 Ctrl+C 停止程序"
echo "========================================"
python app_enhanced.py

read -p "按任意键退出..."
