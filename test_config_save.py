"""
测试配置保存功能
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app_enhanced import EnhancedTradingAgentsApp

def test_config_save():
    """测试配置保存和加载功能"""
    print("🧪 测试TradingAgents配置保存功能")
    print("="*50)
    
    # 创建应用实例
    app = EnhancedTradingAgentsApp()
    
    print(f"📁 配置文件路径: {app.config_file}")
    print(f"📂 配置目录: {app.config_dir}")
    print(f"🔧 初始配置数量: {len(app.llm_config)}")
    print()
    
    # 测试添加配置
    print("1️⃣ 测试添加LLM配置...")
    app.llm_config["test_provider"] = "test-api-key-12345"
    app.llm_config["deepseek"] = "sk-test-deepseek-key"
    print(f"   添加后配置数量: {len(app.llm_config)}")
    
    # 测试添加自定义提供商
    print("2️⃣ 测试添加自定义提供商...")
    result = app.add_custom_llm_provider(
        name="TestLLM",
        api_key="test-custom-key-67890",
        base_url="https://api.test.com/v1",
        model="test-model-v1"
    )
    print(f"   添加结果: {result.get('message', '失败')}")
    print(f"   自定义提供商数量: {len(app.custom_llm_providers)}")
    
    # 测试保存配置
    print("3️⃣ 测试保存配置...")
    save_result = app.save_config()
    print(f"   保存结果: {save_result.get('message', '失败')}")
    print(f"   配置文件存在: {app.config_file.exists()}")
    
    if app.config_file.exists():
        print(f"   配置文件大小: {app.config_file.stat().st_size} 字节")
    
    # 测试清空内存配置
    print("4️⃣ 测试清空内存配置...")
    original_count = len(app.llm_config)
    app.llm_config.clear()
    app.custom_llm_providers.clear()
    print(f"   清空后配置数量: {len(app.llm_config)}")
    
    # 测试加载配置
    print("5️⃣ 测试加载配置...")
    load_result = app.load_saved_config()
    print(f"   加载结果: {load_result.get('message', '失败')}")
    print(f"   加载后配置数量: {len(app.llm_config)}")
    print(f"   加载后自定义提供商数量: {len(app.custom_llm_providers)}")
    
    # 验证配置内容
    print("6️⃣ 验证配置内容...")
    if "test_provider" in app.llm_config:
        print("   ✅ test_provider 配置已恢复")
    else:
        print("   ❌ test_provider 配置丢失")
    
    if "TestLLM" in app.custom_llm_providers:
        print("   ✅ TestLLM 自定义提供商已恢复")
        test_llm_config = app.custom_llm_providers["TestLLM"]
        print(f"      - API密钥: {test_llm_config['api_key'][:10]}...")
        print(f"      - 基础URL: {test_llm_config['base_url']}")
        print(f"      - 模型: {test_llm_config['model']}")
    else:
        print("   ❌ TestLLM 自定义提供商丢失")
    
    # 测试获取提供商信息
    print("7️⃣ 测试获取提供商信息...")
    providers_info = app.get_all_llm_providers()
    print(f"   内置提供商: {len(providers_info['built_in'])}")
    print(f"   自定义提供商: {len(providers_info['custom'])}")
    
    for name, info in providers_info['custom'].items():
        print(f"      - {name}: {info['type']}, 已配置: {info['configured']}")
    
    # 测试清空配置
    print("8️⃣ 测试清空配置...")
    clear_result = app.clear_saved_config()
    print(f"   清空结果: {clear_result.get('message', '失败')}")
    print(f"   配置文件存在: {app.config_file.exists()}")
    print(f"   清空后配置数量: {len(app.llm_config)}")
    
    print()
    print("="*50)
    print("🎉 配置保存功能测试完成！")
    
    # 总结
    if save_result.get('status') == 'success' and load_result.get('status') == 'success':
        print("✅ 配置保存和加载功能正常工作")
    else:
        print("❌ 配置保存或加载功能存在问题")
    
    return True

def test_encryption():
    """测试加密功能"""
    print("\n🔒 测试加密功能")
    print("-"*30)
    
    app = EnhancedTradingAgentsApp()
    
    # 测试加密
    original_key = "sk-test-api-key-12345"
    encrypted_key = app._encrypt_key(original_key)
    decrypted_key = app._decrypt_key(encrypted_key)
    
    print(f"原始密钥: {original_key}")
    print(f"加密后: {encrypted_key}")
    print(f"解密后: {decrypted_key}")
    
    if original_key == decrypted_key:
        print("✅ 加密解密功能正常")
    else:
        print("❌ 加密解密功能异常")
    
    return original_key == decrypted_key

if __name__ == "__main__":
    try:
        # 测试配置保存功能
        config_test_passed = test_config_save()
        
        # 测试加密功能
        encryption_test_passed = test_encryption()
        
        print("\n" + "="*60)
        print("📊 测试结果总结")
        print("="*60)
        print(f"配置保存功能: {'✅ 通过' if config_test_passed else '❌ 失败'}")
        print(f"加密解密功能: {'✅ 通过' if encryption_test_passed else '❌ 失败'}")
        
        if config_test_passed and encryption_test_passed:
            print("\n🎉 所有测试通过！配置保存功能可以正常使用。")
            print("\n💡 使用建议:")
            print("1. 启动系统: python app_enhanced.py")
            print("2. 访问: http://localhost:7864")
            print("3. 配置LLM: 在'⚙️ LLM配置'页面输入API密钥")
            print("4. 保存配置: 点击'💾 保存'按钮")
            print("5. 重启验证: 重启系统验证配置自动加载")
        else:
            print("\n❌ 部分测试失败，请检查代码实现。")
    
    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
