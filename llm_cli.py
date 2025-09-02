#!/usr/bin/env python3
"""
LLM动态需求分析 - CLI工具
用户说什么，LLM就分析什么的命令行接口
"""

import asyncio
import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cli_config
from llm_dynamic.analyzer_api import DynamicLLMAnalyzerAPI
from llm_dynamic.database import get_all_products, get_products_by_keyword


async def main():
    """主程序入口"""
    if len(sys.argv) < 2:
        print("🤖 LLM动态商品分析工具")
        print("\n使用方法：")
        print("  python llm_cli.py '你的分析需求' [关键词] [选项]")
        print("\n基本选项：")
        print("  --model 模型名       指定模型（默认：gpt-3.5-turbo）")
        print("  --keyword 关键词     搜索关键词")
        print("  --limit 数量         分析商品数量（默认：10）")
        print("  --interactive, -i    交互模式")
        print("\n使用示例：")
        print("  python llm_cli.py '找出性价比最高的iPhone'")
        print("  python llm_cli.py '分析这些商品' iPhone --model gpt-4")
        print("  python llm_cli.py '给购买建议' --keyword MacBook")
        print("  python llm_cli.py '按价格排序' --keyword iPhone --limit 15")
        print("\n配置检查：")
        print("  python check_llm_env.py")
        print("\n配置指南：")
        print("  docs/API_SETUP_GUIDE.md")
        return

    # 解析命令行参数
    prompt = sys.argv[1]
    keyword = None
    model = None
    limit = 10

    # 简单参数解析
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--model" and i + 1 < len(sys.argv):
            model = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--keyword" and i + 1 < len(sys.argv):
            keyword = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--limit" and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])
            i += 2
        elif not keyword and not sys.argv[i].startswith("--"):
            keyword = sys.argv[i]
            i += 1
        else:
            i += 1

    print(f"🎯 分析需求：{prompt}")
    if keyword:
        print(f"🔍 关键词：{keyword}")
    if model:
        print(f"🤖 使用模型：{model}")
    else:
        print(f"🤖 默认模型：{cli_config.get_llm_model()}")

    print(f"📊 分析数量：{limit}")
    print("=" * 50)

    try:
        # 验证API密钥
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OpenAI API 密钥未配置")
            print("\n💡 配置方法：")
            print("1. 复制环境配置：cp env.example .env")
            print("2. 编辑 .env 文件，设置 OPENAI_API_KEY")
            print("3. 详细指南：docs/API_SETUP_GUIDE.md")
            return

        # 初始化分析器
        analyzer = DynamicLLMAnalyzerAPI(model=model)
        print("🔗 正在验证API连接...")

        # 测试连接
        connection_test = await analyzer.test_connection()
        if connection_test["status"] == "error":
            print(f"❌ API连接失败：{connection_test['message']}")
            print("\n💡 建议解决方案：")
            for suggestion in connection_test.get("suggestions", []):
                print(f"  • {suggestion}")
            return
        else:
            print(f"✅ API连接成功：{connection_test['message']}")

        # 获取商品数据
        if keyword:
            products = await get_products_by_keyword(keyword, limit)
            print(f"📦 找到 {len(products)} 个相关商品")
        else:
            products = await get_all_products(limit)
            print(f"📦 获取最新 {len(products)} 个商品")

        if not products:
            print("❌ 没有找到相关商品数据")
            return

        print("🤔 LLM分析中...")
        print("-" * 50)

        # 执行动态分析
        result = await analyzer.analyze_with_prompt(products, prompt)

        print("🎉 分析结果：")
        print(result)

    except Exception as e:
        error_msg = str(e)
        print(f"❌ 分析失败：{error_msg}")
        print("\n💡 可能的解决方案：")

        if "api_key" in error_msg.lower():
            print("1. 检查 OPENAI_API_KEY 是否正确配置")
            print("2. 验证API密钥格式（以sk-开头）")
        elif "rate_limit" in error_msg.lower():
            print("1. API请求频率超限，请稍后重试")
            print("2. 考虑升级API计划")
        elif "model" in error_msg.lower():
            print("1. 检查模型名称是否正确")
            print("2. 验证账户是否有模型访问权限")
        else:
            print("1. 检查网络连接")
            print("2. 验证API服务状态")
            print("3. 查看详细配置指南：docs/API_SETUP_GUIDE.md")

        print("4. 检查数据库文件是否存在")
        print("5. 运行环境检查：python check_llm_env.py")


async def interactive_mode():
    """交互模式"""
    print("🤖 进入LLM动态分析交互模式")
    print("输入 'quit' 或 'exit' 退出")
    print("=" * 50)

    try:
        # 验证API密钥
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OpenAI API 密钥未配置，请先配置后再使用交互模式")
            print("\n💡 配置方法：")
            print("1. 复制环境配置：cp env.example .env")
            print("2. 编辑 .env 文件，设置 OPENAI_API_KEY")
            print("3. 详细指南：docs/API_SETUP_GUIDE.md")
            return

        analyzer = DynamicLLMAnalyzerAPI()

        # 测试连接
        print("🔗 正在验证API连接...")
        connection_test = await analyzer.test_connection()
        if connection_test["status"] == "error":
            print(f"❌ API连接失败：{connection_test['message']}")
            return
        else:
            print(f"✅ {connection_test['message']}")
    except Exception as e:
        print(f"❌ 初始化分析器失败：{str(e)}")
        return

    while True:
        try:
            prompt = input("\n💭 你想分析什么？> ").strip()

            if prompt.lower() in ["quit", "exit", "退出"]:
                print("👋 再见！")
                break

            if not prompt:
                continue

            # 简单的关键词提取（用户可以输入：分析iPhone或iPhone分析）
            keyword = None
            for word in prompt.split():
                if any(
                    brand in word.lower()
                    for brand in ["iphone", "ipad", "macbook", "apple", "苹果"]
                ):
                    keyword = word
                    break

            # 获取数据
            if keyword:
                products = await get_products_by_keyword(keyword, 10)
                print(f"📦 找到 {len(products)} 个相关商品")
            else:
                products = await get_all_products(10)
                print(f"📦 获取最新 {len(products)} 个商品")

            if not products:
                print("❌ 没有找到相关商品数据")
                continue

            print("🤔 分析中...")
            result = await analyzer.analyze_with_prompt(products, prompt)
            print(f"\n🎉 分析结果：\n{result}")

        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 错误：{error_msg}")

            if "rate_limit" in error_msg.lower():
                print("💡 API请求频率超限，请稍等片刻再试")
            elif "api_key" in error_msg.lower():
                print("💡 API密钥问题，请检查配置")


if __name__ == "__main__":
    # 检查是否是交互模式
    if len(sys.argv) >= 2 and sys.argv[-1] in ["--interactive", "-i"]:
        asyncio.run(interactive_mode())
    else:
        asyncio.run(main())
