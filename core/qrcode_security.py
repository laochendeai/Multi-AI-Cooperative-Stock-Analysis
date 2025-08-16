#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二维码安全校验模块
QR Code Security Verification Module

提供二维码完整性校验功能，确保收款码未被篡改
"""

import hashlib
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class QRCodeSecurityManager:
    """二维码安全管理器"""
    
    def __init__(self, qrcode_path="assets/donation_code.png",
                 checksum_path="assets/donation_code.sha256"):
        """
        初始化安全管理器
        
        Args:
            qrcode_path: 二维码图片路径
            checksum_path: 校验和文件路径
        """
        self.qrcode_path = Path(qrcode_path)
        self.checksum_path = Path(checksum_path)

        # 兼容性检查：按优先级查找二维码文件
        if not self.qrcode_path.exists():
            # 尝试其他文件名
            fallback_files = [
                ("assets/donation_qcode.png", "assets/donation_qcode.sha256"),
                ("assets/donation_qrcode.png", "assets/donation_qrcode.sha256")
            ]
            for qr_path, checksum_path in fallback_files:
                if Path(qr_path).exists():
                    self.qrcode_path = Path(qr_path)
                    self.checksum_path = Path(checksum_path)
                    break
        
    def calculate_sha256(self, file_path):
        """
        计算文件的SHA-256哈希值
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: SHA-256哈希值
        """
        try:
            with open(file_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"计算SHA-256失败: {e}")
            return None
    
    def load_expected_checksum(self):
        """
        加载预期的校验和
        
        Returns:
            str: 预期的SHA-256哈希值
        """
        try:
            with open(self.checksum_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"读取校验和文件失败: {e}")
            return None
    
    def verify_qrcode(self):
        """
        验证二维码完整性
        
        Returns:
            bool: 验证是否通过
        """
        if not self.qrcode_path.exists():
            logger.error(f"二维码文件不存在: {self.qrcode_path}")
            return False
            
        if not self.checksum_path.exists():
            logger.error(f"校验和文件不存在: {self.checksum_path}")
            return False
        
        # 计算当前文件的哈希值
        current_hash = self.calculate_sha256(self.qrcode_path)
        if not current_hash:
            return False
        
        # 加载预期的哈希值
        expected_hash = self.load_expected_checksum()
        if not expected_hash:
            return False
        
        # 比较哈希值
        is_valid = current_hash == expected_hash
        
        if is_valid:
            logger.info("✅ 二维码校验通过")
        else:
            logger.warning(f"❌ 二维码校验失败! 当前: {current_hash}, 预期: {expected_hash}")
            
        return is_valid
    
    def get_qrcode_info(self):
        """
        获取二维码信息
        
        Returns:
            dict: 二维码信息
        """
        info = {
            "path": str(self.qrcode_path),
            "exists": self.qrcode_path.exists(),
            "size": None,
            "hash": None,
            "verified": False
        }
        
        if info["exists"]:
            try:
                info["size"] = self.qrcode_path.stat().st_size
                info["hash"] = self.calculate_sha256(self.qrcode_path)
                info["verified"] = self.verify_qrcode()
            except Exception as e:
                logger.error(f"获取二维码信息失败: {e}")
        
        return info

def verify_qrcode():
    """
    快速验证二维码（兼容性函数）
    
    Returns:
        bool: 验证是否通过
    """
    manager = QRCodeSecurityManager()
    return manager.verify_qrcode()

def display_donation_info(exit_on_failure=False):
    """
    显示赞助信息

    Args:
        exit_on_failure: 如果为True，校验失败时退出程序
    """
    print("\n" + "="*60)
    print("💖 感谢您使用 TradingAgents 多智能体股票分析系统!")
    print("="*60)
    print("🙏 如果这个项目对您有帮助，请考虑赞助支持:")
    print("   ✅ 作者给妈妈尽点孝心的心愿")
    print("   ✅ 支持开发新功能")
    print("   ✅ 激励社区贡献")
    print("📱 扫描 assets/donation_code.png 中的二维码")
    print("⚖️  法律声明: 此为官方唯一收款码")
    print("="*60)

    # 验证二维码
    manager = QRCodeSecurityManager()
    if manager.verify_qrcode():
        print("✅ 二维码校验通过，可安全使用")
    else:
        print("❌ 二维码校验失败，请从官方仓库重新下载")
        if exit_on_failure:
            print("🚨 安全校验失败，程序即将退出...")
            print("请确保从官方仓库下载正确的二维码文件")
            print("="*60)
            import sys
            sys.exit(1)
    print("="*60 + "\n")

if __name__ == "__main__":
    # 测试功能
    manager = QRCodeSecurityManager()
    info = manager.get_qrcode_info()
    print("二维码信息:", info)
    
    display_donation_info()
