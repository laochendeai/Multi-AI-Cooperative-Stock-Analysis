@echo off
REM 设置二维码文件权限脚本 (Windows版本)
REM Setup QR Code File Permissions Script (Windows Version)

echo 🔒 设置二维码文件安全权限...

REM 检查文件是否存在
if not exist "assets\donation_qrcode.png" (
    echo ❌ 错误: 二维码文件不存在 assets\donation_qrcode.png
    pause
    exit /b 1
)

if not exist "assets\donation_qrcode.sha256" (
    echo ❌ 错误: 校验和文件不存在 assets\donation_qrcode.sha256
    pause
    exit /b 1
)

REM 设置文件为只读权限
echo 📝 设置文件权限为只读...
attrib +R "assets\donation_qrcode.png"
attrib +R "assets\donation_qrcode.sha256"

REM 验证权限设置
echo 🔍 验证文件权限...
dir "assets\donation_qrcode.png"
dir "assets\donation_qrcode.sha256"

REM 运行安全校验
echo 🛡️  运行安全校验...
python -c "import sys; sys.path.append('.'); from core.qrcode_security import QRCodeSecurityManager; manager = QRCodeSecurityManager(); print('✅ 二维码安全校验通过' if manager.verify_qrcode() else '❌ 二维码安全校验失败'); sys.exit(0 if manager.verify_qrcode() else 1)"

if %errorlevel% neq 0 (
    echo ❌ 安全校验失败
    pause
    exit /b 1
)

echo 🎉 二维码安全设置完成！
echo.
echo 📋 安全设置摘要:
echo    - 文件权限: 只读
echo    - SHA-256校验: 通过
echo    - 安全状态: ✅ 安全
echo.
echo ⚠️  注意: 文件现在为只读状态，如需修改请先更改权限

pause
