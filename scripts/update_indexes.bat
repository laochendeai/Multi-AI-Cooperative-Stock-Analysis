@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: TradingAgents 索引更新批处理脚本
:: 提供Windows环境下的索引管理功能

echo.
echo ========================================
echo 🤖 TradingAgents 索引更新工具
echo ========================================
echo.

:: 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python环境
    echo 💡 请先安装Python 3.8+
    pause
    exit /b 1
)

:: 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

:: 切换到项目根目录
cd /d "%PROJECT_ROOT%"

:: 显示菜单
:menu
echo.
echo 📋 请选择操作:
echo.
echo 1. 🔍 诊断索引状态
echo 2. 📦 创建备份
echo 3. 🔧 修复索引问题
echo 4. 🚀 完整更新流程
echo 5. 📊 查看系统状态
echo 6. 🧪 运行测试
echo 7. 📖 查看帮助
echo 0. 🚪 退出
echo.
set /p choice="请输入选项 (0-7): "

if "%choice%"=="1" goto diagnose
if "%choice%"=="2" goto backup
if "%choice%"=="3" goto repair
if "%choice%"=="4" goto full_update
if "%choice%"=="5" goto status
if "%choice%"=="6" goto test
if "%choice%"=="7" goto help
if "%choice%"=="0" goto exit
echo ❌ 无效选项，请重新选择
goto menu

:diagnose
echo.
echo 🔍 开始诊断索引状态...
echo.
python scripts/index_update_tool.py diagnose
echo.
echo 📋 诊断完成，按任意键返回菜单...
pause >nul
goto menu

:backup
echo.
echo 📦 创建系统备份...
echo.
python scripts/index_update_tool.py backup
echo.
echo 📋 备份完成，按任意键返回菜单...
pause >nul
goto menu

:repair
echo.
echo 🔧 开始修复索引问题...
echo.
python scripts/index_update_tool.py repair
echo.
echo 📋 修复完成，按任意键返回菜单...
pause >nul
goto menu

:full_update
echo.
echo 🚀 执行完整更新流程...
echo.
echo 📋 步骤1: 创建备份
python scripts/index_update_tool.py backup
echo.
echo 📋 步骤2: 诊断问题
python scripts/index_update_tool.py diagnose
echo.
echo 📋 步骤3: 修复问题
python scripts/index_update_tool.py repair
echo.
echo 📋 步骤4: 更新依赖
pip install -r requirements.txt --upgrade
echo.
echo 📋 步骤5: 验证系统
python -c "from final_ui import FinalTradingAgentsUI; ui = FinalTradingAgentsUI(); print(f'✅ 系统状态: {\"正常\" if ui.enhanced_features_available else \"基础模式\"}')"
echo.
echo 🎉 完整更新流程执行完毕！
echo.
echo 📋 按任意键返回菜单...
pause >nul
goto menu

:status
echo.
echo 📊 查看系统状态...
echo.
echo 📋 Python版本:
python --version
echo.
echo 📋 项目目录:
echo %PROJECT_ROOT%
echo.
echo 📋 关键文件检查:
if exist "final_ui.py" (
    echo ✅ final_ui.py - 存在
) else (
    echo ❌ final_ui.py - 缺失
)

if exist "core\enhanced_llm_manager.py" (
    echo ✅ enhanced_llm_manager.py - 存在
) else (
    echo ❌ enhanced_llm_manager.py - 缺失
)

if exist "config\llm_config.template.json" (
    echo ✅ llm_config.template.json - 存在
) else (
    echo ❌ llm_config.template.json - 缺失
)

if exist "tradingagents\agents" (
    echo ✅ agents目录 - 存在
) else (
    echo ❌ agents目录 - 缺失
)

echo.
echo 📋 依赖包检查:
python -c "
import sys
packages = ['gradio', 'pandas', 'asyncio']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg} - 已安装')
    except ImportError:
        print(f'❌ {pkg} - 未安装')
"
echo.
echo 📋 按任意键返回菜单...
pause >nul
goto menu

:test
echo.
echo 🧪 运行系统测试...
echo.
echo 📋 测试1: UI组件导入
python -c "
try:
    from final_ui import FinalTradingAgentsUI
    print('✅ UI组件导入成功')
except Exception as e:
    print(f'❌ UI组件导入失败: {e}')
"
echo.
echo 📋 测试2: 核心模块导入
python -c "
try:
    from core.enhanced_llm_manager import EnhancedLLMManager
    print('✅ LLM管理器导入成功')
except Exception as e:
    print(f'❌ LLM管理器导入失败: {e}')
"
echo.
echo 📋 测试3: 智能体管理器
python -c "
try:
    from core.agent_model_manager import AgentModelManager
    print('✅ 智能体管理器导入成功')
except Exception as e:
    print(f'❌ 智能体管理器导入失败: {e}')
"
echo.
echo 📋 测试4: 系统集成测试
if exist "test_system_integration.py" (
    echo 🔄 运行集成测试...
    python test_system_integration.py
) else (
    echo ⚠️ 集成测试文件不存在
)
echo.
echo 📋 测试完成，按任意键返回菜单...
pause >nul
goto menu

:help
echo.
echo 📖 TradingAgents 索引更新工具帮助
echo.
echo 🎯 功能说明:
echo   • 诊断: 检查系统索引状态，发现潜在问题
echo   • 备份: 创建系统文件备份，确保安全更新
echo   • 修复: 自动修复发现的索引问题
echo   • 完整更新: 执行备份→诊断→修复→验证的完整流程
echo   • 状态查看: 显示系统当前状态和配置信息
echo   • 测试: 运行各种测试验证系统功能
echo.
echo 🔧 常见问题:
echo   • 如果出现导入错误，请运行"修复索引问题"
echo   • 如果缺少依赖包，请运行: pip install -r requirements.txt
echo   • 如果UI无法启动，请先运行"诊断索引状态"
echo.
echo 📁 相关文件:
echo   • docs/INDEX_CODE_UPDATE_GUIDE.md - 详细文档
echo   • scripts/index_update_tool.py - Python工具脚本
echo   • config/ - 配置文件目录
echo   • core/ - 核心模块目录
echo.
echo 📋 按任意键返回菜单...
pause >nul
goto menu

:exit
echo.
echo 👋 感谢使用 TradingAgents 索引更新工具！
echo.
exit /b 0

:: 错误处理
:error
echo.
echo ❌ 执行过程中出现错误
echo 💡 请检查错误信息并重试
echo.
pause
goto menu
