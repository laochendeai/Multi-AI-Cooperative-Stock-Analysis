@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🔐 TradingAgents 安全推送脚本
echo ================================

REM 检查是否在正确的目录
if not exist "final_ui.py" (
    echo ❌ 错误: 请在项目根目录运行此脚本
    pause
    exit /b 1
)

echo 🔍 检查敏感文件...

REM 检查敏感文件
set FOUND_SENSITIVE=false

if exist "config\llm_config.json" (
    echo ⚠️  发现敏感文件: config\llm_config.json
    set FOUND_SENSITIVE=true
)

if exist "config\agent_model_config.json" (
    echo ⚠️  发现敏感文件: config\agent_model_config.json
    set FOUND_SENSITIVE=true
)

if exist ".env" (
    echo ⚠️  发现敏感文件: .env
    set FOUND_SENSITIVE=true
)

if exist "*.log" (
    echo ⚠️  发现敏感文件: *.log
    set FOUND_SENSITIVE=true
)

if exist "data\trading_data.db" (
    echo ⚠️  发现敏感文件: data\trading_data.db
    set FOUND_SENSITIVE=true
)

if "!FOUND_SENSITIVE!"=="true" (
    echo.
    echo ❌ 发现敏感文件！
    echo 请确保以下文件已添加到 .gitignore 或已删除
    echo 建议操作:
    echo 1. 检查 .gitignore 文件
    echo 2. 删除或移动敏感文件
    echo 3. 重新运行此脚本
    pause
    exit /b 1
)

echo ✅ 未发现敏感文件

echo.
echo 🔍 检查配置模板...

REM 检查配置模板
if not exist "config\llm_config.template.json" (
    echo ❌ 缺少配置模板: config\llm_config.template.json
    pause
    exit /b 1
)

if not exist "config\agent_model_config.template.json" (
    echo ❌ 缺少配置模板: config\agent_model_config.template.json
    pause
    exit /b 1
)

if not exist "config\README.md" (
    echo ❌ 缺少配置说明: config\README.md
    pause
    exit /b 1
)

echo ✅ 配置模板完整

echo.
echo 🔍 检查 .gitignore 文件...

if not exist ".gitignore" (
    echo ❌ 缺少 .gitignore 文件
    pause
    exit /b 1
)

echo ✅ .gitignore 文件存在

REM 显示将要提交的文件
echo.
echo 📋 将要提交的文件:
git status --porcelain

echo.
echo 🔍 检查暂存区...
git diff --cached --name-only

REM 确认推送
echo.
set /p CONFIRM="🚀 确认推送到远程仓库? (y/N): "

if /i not "!CONFIRM!"=="y" (
    echo ❌ 推送已取消
    pause
    exit /b 1
)

REM 执行Git操作
echo.
echo 📦 准备推送...

REM 添加所有文件
git add .

REM 提交
echo.
echo 💾 提交更改...
git commit -m "🚀 TradingAgents v2.0 发布版本

✨ 新增功能:
- 动态LLM配置管理
- 智能体模型选择系统  
- 增强报告生成 (多模板支持)
- 智能文档精简系统
- 完整的配置安全机制

🔒 安全更新:
- 移除所有敏感配置信息
- 添加配置模板和设置指南
- 完善 .gitignore 规则

📚 文档更新:
- 更新 README.md
- 添加用户使用指南
- 添加技术架构文档
- 添加启动指南

🧹 项目清理:
- 删除100+个无用文件
- 优化项目结构
- 准备发布版本

向后兼容: 完全兼容 v1.0
启动方式: python final_ui.py"

REM 推送到远程仓库
echo.
echo 🌐 推送到远程仓库...

REM 检查是否有远程仓库
git remote | findstr "origin" >nul
if errorlevel 1 (
    echo ⚠️  未找到远程仓库 'origin'
    echo 请先添加远程仓库:
    echo git remote add origin ^<your-repository-url^>
    echo 然后运行: git push -u origin main
) else (
    git push origin main
    echo ✅ 推送完成!
)

echo.
echo 🎉 安全推送完成!
echo.
echo 📋 后续步骤:
echo 1. 在新环境中克隆仓库
echo 2. 复制配置模板: copy config\*.template.json config\
echo 3. 编辑配置文件并填入API密钥
echo 4. 启动系统: python final_ui.py
echo.
echo 📖 详细说明请查看: config\README.md

pause
