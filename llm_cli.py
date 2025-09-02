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

from llm_dynamic.analyzer import DynamicLLMAnalyzer
from llm_dynamic.database import get_all_products, get_products_by_keyword


async def main():
    """主程序入口"""
    if len(sys.argv) < 2:
        print("🤖 LLM动态商品分析工具")
        print("\n使用方法：")
        print("  python llm_cli.py '你的分析需求' [关键词] [--model 模型名]")
        print("\n示例：")
        print("  python llm_cli.py '找出性价比最高的iPhone'")
        print("  python llm_cli.py '分析这些商品的共同特点' iPhone")
        print("  python llm_cli.py '给购买建议' MacBook --model qwen2.5:7b")
        print("  python llm_cli.py '按价格排序' --keyword iPhone --limit 15")
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
    print(f"📊 分析数量：{limit}")
    print("=" * 50)

    try:
        # 初始化分析器
        analyzer = DynamicLLMAnalyzer(model=model)

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
        print(f"❌ 分析失败：{str(e)}")
        print("\n💡 可能的解决方案：")
        print("1. 确保Ollama服务已启动：ollama serve")
        print("2. 检查模型是否已安装：ollama list")
        print("3. 安装默认模型：ollama pull llama3.2")
        print("4. 检查数据库文件是否存在")


async def interactive_mode():
    """交互模式"""
    print("🤖 进入LLM动态分析交互模式")
    print("输入 'quit' 或 'exit' 退出")
    print("=" * 50)

    analyzer = DynamicLLMAnalyzer()

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
            print(f"❌ 错误：{str(e)}")


if __name__ == "__main__":
    # 检查是否是交互模式
    if len(sys.argv) == 2 and sys.argv[1] in ["--interactive", "-i"]:
        asyncio.run(interactive_mode())
    else:
        asyncio.run(main())
