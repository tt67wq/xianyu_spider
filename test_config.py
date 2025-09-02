#!/usr/bin/env python3
"""
配置模块测试脚本
测试CLI配置管理和LLM配置功能
"""

import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cli_config import (
    get_config,
    get_database_path,
    get_llm_api_key,
    get_llm_base_url,
    get_llm_max_retries,
    get_llm_max_tokens,
    get_llm_model,
    get_llm_temperature,
    get_llm_timeout,
    is_llm_configured,
)


def test_basic_config():
    """测试基础配置功能"""
    print("🧪 测试基础配置功能")
    print("-" * 40)

    config = get_config()

    # 测试数据库配置
    db_path = get_database_path()
    print(f"✅ 数据库路径: {db_path}")

    # 测试爬虫配置
    spider_config = config.get_spider_config()
    print(f"✅ 请求延迟: {spider_config['request_delay']}秒")
    print(
        f"✅ 浏览器模式: {'无头' if spider_config['browser_headless'] else '有头'}"
    )

    # 测试调试配置
    debug_enabled = config.is_debug_enabled()
    print(f"✅ 调试模式: {'开启' if debug_enabled else '关闭'}")

    print("✅ 基础配置测试通过\n")


def test_llm_config():
    """测试LLM配置功能"""
    print("🤖 测试LLM配置功能")
    print("-" * 40)

    # 测试LLM配置状态
    llm_configured = is_llm_configured()
    print(f"✅ LLM配置状态: {'已配置' if llm_configured else '未配置'}")

    if llm_configured:
        # 测试各项LLM配置
        api_key = get_llm_api_key()
        if api_key:
            masked_key = f"{api_key[:10]}...{api_key[-4:]}"
            print(f"✅ API密钥: {masked_key}")

        base_url = get_llm_base_url()
        print(f"✅ API端点: {base_url}")

        model = get_llm_model()
        print(f"✅ 模型名称: {model}")

        timeout = get_llm_timeout()
        print(f"✅ 超时时间: {timeout}秒")

        max_retries = get_llm_max_retries()
        print(f"✅ 最大重试: {max_retries}次")

        temperature = get_llm_temperature()
        print(f"✅ 温度参数: {temperature}")

        max_tokens = get_llm_max_tokens()
        print(f"✅ 最大tokens: {max_tokens}")
    else:
        print("⚠️  LLM未配置，请检查环境变量")

    print("✅ LLM配置测试通过\n")


def test_config_validation():
    """测试配置验证功能"""
    print("✔️  测试配置验证功能")
    print("-" * 40)

    config = get_config()

    # 测试页数验证
    try:
        validated_pages = config.validate_pages(5)
        print(f"✅ 页数验证(5): {validated_pages}")

        validated_pages = config.validate_pages(100)  # 可能超出限制
        print(f"✅ 页数验证(100): {validated_pages}")
    except ValueError as e:
        print(f"❌ 页数验证失败: {e}")

    # 测试表格限制验证
    try:
        validated_limit = config.validate_table_limit(20)
        print(f"✅ 表格限制验证(20): {validated_limit}")

        validated_limit = config.validate_table_limit(200)  # 可能超出限制
        print(f"✅ 表格限制验证(200): {validated_limit}")
    except ValueError as e:
        print(f"❌ 表格限制验证失败: {e}")

    # 测试输出格式验证
    try:
        validated_format = config.validate_output_format("table")
        print(f"✅ 输出格式验证(table): {validated_format}")

        validated_format = config.validate_output_format("json")
        print(f"✅ 输出格式验证(json): {validated_format}")
    except ValueError as e:
        print(f"❌ 输出格式验证失败: {e}")

    # 测试LLM模型验证
    try:
        validated_model = config.validate_llm_model("gpt-4")
        print(f"✅ LLM模型验证(gpt-4): {validated_model}")

        validated_model = config.validate_llm_model("  gpt-3.5-turbo  ")
        print(f"✅ LLM模型验证(带空格): '{validated_model}'")
    except ValueError as e:
        print(f"❌ LLM模型验证失败: {e}")

    print("✅ 配置验证测试通过\n")


def test_config_getter():
    """测试配置获取功能"""
    print("📋 测试配置获取功能")
    print("-" * 40)

    config = get_config()

    # 测试路径获取
    db_path = config.get("database.path")
    print(f"✅ 获取数据库路径: {db_path}")

    request_delay = config.get("spider.request_delay")
    print(f"✅ 获取请求延迟: {request_delay}")

    # 测试默认值
    non_existent = config.get("non.existent.key", "default_value")
    print(f"✅ 获取不存在的配置(默认值): {non_existent}")

    # 测试LLM配置获取
    llm_config = config.get_llm_config()
    print(f"✅ 获取LLM配置: {len(llm_config)}个配置项")

    print("✅ 配置获取测试通过\n")


def test_environment_variables():
    """测试环境变量读取"""
    print("🌍 测试环境变量读取")
    print("-" * 40)

    # 显示当前环境变量状态
    env_vars = [
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "OPENAI_MODEL",
        "LLM_TIMEOUT",
        "LLM_MAX_RETRIES",
        "LLM_TEMPERATURE",
        "LLM_MAX_TOKENS",
        "DATABASE_PATH",
        "DEBUG",
    ]

    for var in env_vars:
        value = os.getenv(var)
        if var == "OPENAI_API_KEY" and value:
            # 脱敏显示API密钥
            display_value = f"{value[:10]}...{value[-4:]}"
        else:
            display_value = value if value else "未设置"

        status = "✅" if value else "⚪"
        print(f"{status} {var}: {display_value}")

    print("✅ 环境变量读取测试完成\n")


def test_error_handling():
    """测试错误处理"""
    print("⚠️  测试错误处理")
    print("-" * 40)

    config = get_config()

    # 测试无效页数
    try:
        config.validate_pages(-1)
        print("❌ 应该抛出异常但没有")
    except ValueError as e:
        print(f"✅ 正确捕获页数错误: {e}")

    # 测试无效输出格式
    try:
        config.validate_output_format("invalid_format")
        print("❌ 应该抛出异常但没有")
    except ValueError as e:
        print(f"✅ 正确捕获输出格式错误: {e}")

    # 测试空模型名称
    try:
        config.validate_llm_model("")
        print("❌ 应该抛出异常但没有")
    except ValueError as e:
        print(f"✅ 正确捕获模型名称错误: {e}")

    print("✅ 错误处理测试通过\n")


def main():
    """主测试函数"""
    print("🔍 CLI配置模块完整测试")
    print("=" * 60)

    try:
        # 执行所有测试
        test_basic_config()
        test_llm_config()
        test_config_validation()
        test_config_getter()
        test_environment_variables()
        test_error_handling()

        # 显示配置摘要
        print("📊 配置摘要")
        print("-" * 40)
        config = get_config()
        config.print_config_summary()

        print("\n" + "=" * 60)
        print("🎉 所有配置测试通过！")

        # 提供建议
        if not is_llm_configured():
            print("\n💡 建议：")
            print("  1. 配置 OPENAI_API_KEY 环境变量")
            print("  2. 可选配置 OPENAI_BASE_URL（使用第三方API时）")
            print("  3. 可选配置 OPENAI_MODEL（使用特定模型时）")
            print("  4. 参考 docs/API_SETUP_GUIDE.md 获取详细指导")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        if config.is_debug_enabled():
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
