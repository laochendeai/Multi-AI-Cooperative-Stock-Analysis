#!/bin/bash
# TradingAgents 索引更新脚本 (Linux/macOS)
# 提供索引管理、诊断、修复等功能

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo
    echo "========================================"
    print_message $CYAN "🤖 TradingAgents 索引更新工具"
    echo "========================================"
    echo
}

# 检查Python环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        if ! command -v python &> /dev/null; then
            print_message $RED "❌ 错误: 未找到Python环境"
            print_message $YELLOW "💡 请先安装Python 3.8+"
            exit 1
        else
            PYTHON_CMD="python"
        fi
    else
        PYTHON_CMD="python3"
    fi
    
    # 检查Python版本
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    print_message $GREEN "✅ Python版本: $PYTHON_VERSION"
}

# 显示菜单
show_menu() {
    echo
    print_message $BLUE "📋 请选择操作:"
    echo
    echo "1. 🔍 诊断索引状态"
    echo "2. 📦 创建备份"
    echo "3. 🔧 修复索引问题"
    echo "4. 🚀 完整更新流程"
    echo "5. 📊 查看系统状态"
    echo "6. 🧪 运行测试"
    echo "7. 📖 查看帮助"
    echo "0. 🚪 退出"
    echo
}

# 诊断索引状态
diagnose_indexes() {
    echo
    print_message $CYAN "🔍 开始诊断索引状态..."
    echo
    $PYTHON_CMD scripts/index_update_tool.py diagnose
    echo
    print_message $GREEN "📋 诊断完成"
}

# 创建备份
create_backup() {
    echo
    print_message $CYAN "📦 创建系统备份..."
    echo
    $PYTHON_CMD scripts/index_update_tool.py backup
    echo
    print_message $GREEN "📋 备份完成"
}

# 修复索引问题
repair_indexes() {
    echo
    print_message $CYAN "🔧 开始修复索引问题..."
    echo
    $PYTHON_CMD scripts/index_update_tool.py repair
    echo
    print_message $GREEN "📋 修复完成"
}

# 完整更新流程
full_update() {
    echo
    print_message $CYAN "🚀 执行完整更新流程..."
    echo
    
    print_message $BLUE "📋 步骤1: 创建备份"
    $PYTHON_CMD scripts/index_update_tool.py backup
    echo
    
    print_message $BLUE "📋 步骤2: 诊断问题"
    $PYTHON_CMD scripts/index_update_tool.py diagnose
    echo
    
    print_message $BLUE "📋 步骤3: 修复问题"
    $PYTHON_CMD scripts/index_update_tool.py repair
    echo
    
    print_message $BLUE "📋 步骤4: 更新依赖"
    pip install -r requirements.txt --upgrade
    echo
    
    print_message $BLUE "📋 步骤5: 验证系统"
    $PYTHON_CMD -c "
from final_ui import FinalTradingAgentsUI
ui = FinalTradingAgentsUI()
status = '正常' if ui.enhanced_features_available else '基础模式'
print(f'✅ 系统状态: {status}')
"
    echo
    print_message $GREEN "🎉 完整更新流程执行完毕！"
}

# 查看系统状态
show_status() {
    echo
    print_message $CYAN "📊 查看系统状态..."
    echo
    
    print_message $BLUE "📋 Python版本:"
    $PYTHON_CMD --version
    echo
    
    print_message $BLUE "📋 项目目录:"
    echo "$PROJECT_ROOT"
    echo
    
    print_message $BLUE "📋 关键文件检查:"
    
    files=("final_ui.py" "core/enhanced_llm_manager.py" "config/llm_config.template.json")
    for file in "${files[@]}"; do
        if [[ -f "$file" ]]; then
            print_message $GREEN "✅ $file - 存在"
        else
            print_message $RED "❌ $file - 缺失"
        fi
    done
    
    if [[ -d "tradingagents/agents" ]]; then
        print_message $GREEN "✅ agents目录 - 存在"
    else
        print_message $RED "❌ agents目录 - 缺失"
    fi
    
    echo
    print_message $BLUE "📋 依赖包检查:"
    $PYTHON_CMD -c "
import sys
packages = ['gradio', 'pandas', 'asyncio']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg} - 已安装')
    except ImportError:
        print(f'❌ {pkg} - 未安装')
"
}

# 运行测试
run_tests() {
    echo
    print_message $CYAN "🧪 运行系统测试..."
    echo
    
    print_message $BLUE "📋 测试1: UI组件导入"
    $PYTHON_CMD -c "
try:
    from final_ui import FinalTradingAgentsUI
    print('✅ UI组件导入成功')
except Exception as e:
    print(f'❌ UI组件导入失败: {e}')
"
    echo
    
    print_message $BLUE "📋 测试2: 核心模块导入"
    $PYTHON_CMD -c "
try:
    from core.enhanced_llm_manager import EnhancedLLMManager
    print('✅ LLM管理器导入成功')
except Exception as e:
    print(f'❌ LLM管理器导入失败: {e}')
"
    echo
    
    print_message $BLUE "📋 测试3: 智能体管理器"
    $PYTHON_CMD -c "
try:
    from core.agent_model_manager import AgentModelManager
    print('✅ 智能体管理器导入成功')
except Exception as e:
    print(f'❌ 智能体管理器导入失败: {e}')
"
    echo
    
    print_message $BLUE "📋 测试4: 系统集成测试"
    if [[ -f "test_system_integration.py" ]]; then
        print_message $YELLOW "🔄 运行集成测试..."
        $PYTHON_CMD test_system_integration.py
    else
        print_message $YELLOW "⚠️ 集成测试文件不存在"
    fi
    
    echo
    print_message $GREEN "📋 测试完成"
}

# 显示帮助
show_help() {
    echo
    print_message $CYAN "📖 TradingAgents 索引更新工具帮助"
    echo
    print_message $BLUE "🎯 功能说明:"
    echo "  • 诊断: 检查系统索引状态，发现潜在问题"
    echo "  • 备份: 创建系统文件备份，确保安全更新"
    echo "  • 修复: 自动修复发现的索引问题"
    echo "  • 完整更新: 执行备份→诊断→修复→验证的完整流程"
    echo "  • 状态查看: 显示系统当前状态和配置信息"
    echo "  • 测试: 运行各种测试验证系统功能"
    echo
    print_message $BLUE "🔧 常见问题:"
    echo "  • 如果出现导入错误，请运行\"修复索引问题\""
    echo "  • 如果缺少依赖包，请运行: pip install -r requirements.txt"
    echo "  • 如果UI无法启动，请先运行\"诊断索引状态\""
    echo
    print_message $BLUE "📁 相关文件:"
    echo "  • docs/INDEX_CODE_UPDATE_GUIDE.md - 详细文档"
    echo "  • scripts/index_update_tool.py - Python工具脚本"
    echo "  • config/ - 配置文件目录"
    echo "  • core/ - 核心模块目录"
    echo
    print_message $BLUE "🔗 使用方法:"
    echo "  ./scripts/update_indexes.sh          # 交互式菜单"
    echo "  ./scripts/update_indexes.sh diagnose # 直接诊断"
    echo "  ./scripts/update_indexes.sh backup   # 直接备份"
    echo "  ./scripts/update_indexes.sh repair   # 直接修复"
    echo "  ./scripts/update_indexes.sh full     # 完整流程"
}

# 主函数
main() {
    print_header
    check_python
    
    # 如果有命令行参数，直接执行对应功能
    if [[ $# -gt 0 ]]; then
        case $1 in
            "diagnose")
                diagnose_indexes
                ;;
            "backup")
                create_backup
                ;;
            "repair")
                repair_indexes
                ;;
            "full")
                full_update
                ;;
            "status")
                show_status
                ;;
            "test")
                run_tests
                ;;
            "help")
                show_help
                ;;
            *)
                print_message $RED "❌ 未知参数: $1"
                show_help
                exit 1
                ;;
        esac
        exit 0
    fi
    
    # 交互式菜单
    while true; do
        show_menu
        read -p "请输入选项 (0-7): " choice
        
        case $choice in
            1)
                diagnose_indexes
                ;;
            2)
                create_backup
                ;;
            3)
                repair_indexes
                ;;
            4)
                full_update
                ;;
            5)
                show_status
                ;;
            6)
                run_tests
                ;;
            7)
                show_help
                ;;
            0)
                echo
                print_message $GREEN "👋 感谢使用 TradingAgents 索引更新工具！"
                echo
                exit 0
                ;;
            *)
                print_message $RED "❌ 无效选项，请重新选择"
                ;;
        esac
        
        echo
        read -p "按回车键继续..."
    done
}

# 执行主函数
main "$@"
