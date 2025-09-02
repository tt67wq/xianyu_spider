#!/usr/bin/env python3
"""
LLM动态分析模块环境检查脚本
检查Python版本、内存、OpenAI API配置和连接状态
"""

import asyncio
import os
import sys
from typing import List, Tuple

import psutil


def check_python_version() -> Tuple[bool, str]:
    """检查Python版本（要求>=3.11）"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        return (
            True,
            f"✅ Python {version.major}.{version.minor}.{version.micro}",
        )
    else:
        return (
            False,
            f"❌ Python {version.major}.{version.minor}.{version.micro} (需要 >= 3.11)",
        )


def check_memory() -> Tuple[bool, str]:
    """检查系统内存（最少2GB/建议4GB）"""
    try:
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024**3)

        if total_gb >= 4:
            return True, f"✅ 系统内存: {total_gb:.1f}GB (充足)"
        elif total_gb >= 2:
            return True, f"⚠️  系统内存: {total_gb:.1f}GB (基本满足，建议4GB)"
        else:
            return False, f"❌ 系统内存: {total_gb:.1f}GB (不足，至少需要2GB)"
    except Exception as e:
        return False, f"❌ 无法检测内存: {str(e)}"


def check_api_key() -> Tuple[bool, str]:
    """检查OpenAI API密钥配置"""
    from cli_config import get_llm_api_key, is_llm_configured

    if not is_llm_configured():
        return False, "❌ OPENAI_API_KEY 环境变量未设置"

    api_key = get_llm_api_key()

    if not api_key.startswith("sk-"):
        return False, "❌ API密钥格式错误 (应以 'sk-' 开头)"

    if len(api_key) < 20:
        return False, "❌ API密钥长度异常 (过短)"

    # 脱敏显示
    masked_key = api_key[:10] + "..." + api_key[-4:]
    return True, f"✅ API密钥已配置: {masked_key}"


def check_env_file() -> Tuple[bool, str]:
    """检查.env文件是否存在"""
    env_path = ".env"

    if os.path.exists(env_path):
        return True, f"✅ 环境配置文件存在: {env_path}"
    else:
        return False, f"❌ 环境配置文件不存在: {env_path}"


async def check_api_connection() -> Tuple[bool, str]:
    """检查API连接状态"""
    try:
        from cli_config import is_llm_configured
        from llm_dynamic.analyzer_api import DynamicLLMAnalyzerAPI

        # 检查API密钥是否配置
        if not is_llm_configured():
            return False, "❌ API密钥未配置，无法测试连接"

        # 创建分析器并测试连接
        analyzer = DynamicLLMAnalyzerAPI()
        result = await analyzer.test_connection()

        if result["status"] == "success":
            return True, f"✅ API连接成功: {result['message']}"
        else:
            return False, f"❌ API连接失败: {result['message']}"

    except ImportError as e:
        return False, f"❌ 导入模块失败: {str(e)}"
    except Exception as e:
        return False, f"❌ API连接测试失败: {str(e)}"


def check_database_exists() -> Tuple[bool, str]:
    """检查数据库文件是否存在"""
    try:
        # 使用配置管理获取数据库路径
        from cli_config import get_database_path

        db_path = get_database_path()

        # 处理相对路径
        from pathlib import Path

        path = Path(db_path)
        if not path.is_absolute():
            path = Path(__file__).parent / path

        if path.exists():
            size = path.stat().st_size / 1024  # KB
            return True, f"✅ 数据库文件存在: {size:.1f}KB ({path})"
        else:
            return False, f"❌ 数据库文件不存在: {path}"
    except Exception as e:
        return False, f"❌ 数据库检查失败: {str(e)}"


def check_dependencies() -> Tuple[bool, str]:
    """检查Python依赖"""
    required_packages = [
        "langchain",
        "langchain_openai",
        "langchain_core",
        "tortoise",
        "models",
    ]
    missing = []

    for package in required_packages:
        try:
            if package == "langchain_openai":
                __import__("langchain_openai")
            elif package == "langchain_core":
                __import__("langchain_core")
            else:
                __import__(package)
        except ImportError:
            missing.append(package)

    if not missing:
        return True, "✅ 所有依赖已安装"
    else:
        return False, f"❌ 缺少依赖: {', '.join(missing)}"


def get_model_recommendations() -> List[str]:
    """推荐的模型列表"""
    return [
        "gpt-3.5-turbo (经济实用，速度快)",
        "gpt-4 (高精度，复杂分析)",
        "gpt-4-turbo (平衡选择)",
        "gpt-4o (最新模型)",
        "gpt-4o-mini (轻量级选择)",
    ]


def get_current_model_config() -> str:
    """获取当前模型配置"""
    from cli_config import get_llm_model

    return get_llm_model()


def print_setup_guide():
    """打印配置指南"""
    print("\n" + "=" * 60)
    print("🛠️  配置指南")
    print("=" * 60)

    print("\n1. 复制环境配置文件:")
    print("   cp env.example .env")

    print("\n2. 获取OpenAI API密钥:")
    print("   • 访问 https://platform.openai.com/api-keys")
    print("   • 注册/登录OpenAI账户")
    print("   • 创建新的API密钥")

    print("\n3. 配置环境变量 (.env文件):")
    print("   OPENAI_API_KEY=sk-your-api-key-here")
    print("   OPENAI_MODEL=gpt-3.5-turbo")
    print("   # OPENAI_BASE_URL=https://api.openai.com/v1  # 可选")

    print("\n4. 验证配置:")
    print("   python check_llm_env.py")

    print("\n5. 测试功能:")
    print("   python llm_cli.py '测试分析功能'")

    print("\n📋 详细配置指南:")
    print("   docs/API_SETUP_GUIDE.md")


async def main():
    """主检查程序"""
    print("🔍 LLM动态分析模块环境检查")
    print("=" * 60)

    # 同步检查项目
    sync_checks = [
        ("Python版本", check_python_version),
        ("系统内存", check_memory),
        ("环境配置文件", check_env_file),
        ("API密钥配置", check_api_key),
        ("数据库文件", check_database_exists),
        ("Python依赖", check_dependencies),
    ]

    all_passed = True

    for name, check_func in sync_checks:
        success, message = check_func()
        print(f"{name:12} | {message}")
        if not success:
            all_passed = False

    # 异步检查API连接
    print(f"{'API连接测试':12} | ", end="", flush=True)
    success, message = await check_api_connection()
    print(message)
    if not success:
        all_passed = False

    print("\n" + "-" * 60)

    # 显示当前配置
    print("📋 当前配置:")
    from cli_config import get_llm_base_url

    model = get_current_model_config()
    print(f"   🤖 模型: {model}")

    base_url = get_llm_base_url()
    print(f"   🌐 API端点: {base_url}")

    print("\n" + "-" * 60)

    if all_passed:
        print("🎉 环境检查通过！可以开始使用LLM动态分析功能")
        print("\n快速开始:")
        print("   python llm_cli.py '找出性价比最高的商品'")
        print("   python llm_cli.py '分析iPhone价格趋势' iPhone")
        print("   python llm_cli.py --interactive  # 交互模式")
    else:
        print("❌ 环境检查未通过，请参考配置指南")
        print_setup_guide()

    print("\n" + "=" * 60)
    print("💡 推荐模型:")
    for model in get_model_recommendations():
        print(f"   • {model}")

    print("\n💰 成本提示:")
    print("   • gpt-3.5-turbo: 约 $0.001/1K tokens")
    print("   • gpt-4: 约 $0.03/1K tokens")
    print("   • 建议从 gpt-3.5-turbo 开始使用")


if __name__ == "__main__":
    asyncio.run(main())
