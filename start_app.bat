@echo off
REM Multi-AI-Cooperative-Stock-Analysis 启动脚本
REM 适用于Windows系统

echo ========================================
echo  Multi-AI-Cooperative-Stock-Analysis
echo  多智能体协作股票分析系统
echo ========================================
echo.

REM 检查虚拟环境是否存在
if exist "aistock\Scripts\activate.bat" (
    echo 正在激活虚拟环境 aistock...
    call aistock\Scripts\activate.bat
) else (
    echo 警告: 虚拟环境 'aistock' 未找到，将使用全局Python环境
    echo 建议创建虚拟环境: python -m venv aistock
    echo.
)

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Python未安装或未添加到PATH
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo 检查依赖...
python -c "import gradio" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements.txt
)

REM 启动主程序
echo 正在启动主程序...
echo 访问 http://localhost:7860 查看应用
echo 按 Ctrl+C 停止程序
echo ========================================
python app_enhanced.py

pause
