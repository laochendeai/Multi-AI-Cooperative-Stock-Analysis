#!/bin/bash
# 设置二维码文件权限脚本
# Setup QR Code File Permissions Script

echo "🔒 设置二维码文件安全权限..."

# 检查文件是否存在
if [ ! -f "assets/donation_qrcode.png" ]; then
    echo "❌ 错误: 二维码文件不存在 assets/donation_qrcode.png"
    exit 1
fi

if [ ! -f "assets/donation_qrcode.sha256" ]; then
    echo "❌ 错误: 校验和文件不存在 assets/donation_qrcode.sha256"
    exit 1
fi

# 设置文件为只读权限 (444)
echo "📝 设置文件权限为只读..."
chmod 444 assets/donation_qrcode.png
chmod 444 assets/donation_qrcode.sha256

# 验证权限设置
echo "🔍 验证文件权限..."
ls -la assets/donation_qrcode.png
ls -la assets/donation_qrcode.sha256

# 检查权限是否正确设置
png_perms=$(stat -f "%A" assets/donation_qrcode.png 2>/dev/null || stat -c "%a" assets/donation_qrcode.png)
sha_perms=$(stat -f "%A" assets/donation_qrcode.sha256 2>/dev/null || stat -c "%a" assets/donation_qrcode.sha256)

if [ "$png_perms" = "444" ] && [ "$sha_perms" = "444" ]; then
    echo "✅ 文件权限设置成功 (只读: 444)"
else
    echo "❌ 文件权限设置失败"
    echo "   PNG权限: $png_perms (期望: 444)"
    echo "   SHA权限: $sha_perms (期望: 444)"
    exit 1
fi

# 运行安全校验
echo "🛡️  运行安全校验..."
python -c "
import sys
sys.path.append('.')
from core.qrcode_security import QRCodeSecurityManager

manager = QRCodeSecurityManager()
if manager.verify_qrcode():
    print('✅ 二维码安全校验通过')
else:
    print('❌ 二维码安全校验失败')
    sys.exit(1)
"

echo "🎉 二维码安全设置完成！"
echo ""
echo "📋 安全设置摘要:"
echo "   - 文件权限: 只读 (444)"
echo "   - SHA-256校验: 通过"
echo "   - 安全状态: ✅ 安全"
echo ""
echo "⚠️  注意: 文件现在为只读状态，如需修改请先更改权限"
