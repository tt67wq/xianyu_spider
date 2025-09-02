#!/usr/bin/env python3
"""
LLM动态分析模块基础测试脚本
测试模块导入、数据库连接和LLM基础功能
"""

import asyncio
import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tortoise import Tortoise

from llm_dynamic.analyzer import DynamicLLMAnalyzer
from llm_dynamic.database import get_all_products, get_products_by_keyword
from models import XianyuProduct


async def test_database_connection():
    """测试数据库连接"""
    print("🔗 测试数据库连接...")
    try:
        await Tortoise.init(
            db_url="sqlite://database.sqlite3", modules={"models": ["models"]}
        )

        # 生成数据库表
        await Tortoise.generate_schemas()

        print("✅ 数据库连接成功")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败：{str(e)}")
        return False
    finally:
        await Tortoise.close_connections()


async def create_test_data():
    """创建测试数据"""
    print("📝 创建测试数据...")
    try:
        await Tortoise.init(
            db_url="sqlite://database.sqlite3", modules={"models": ["models"]}
        )

        # 检查是否已有数据
        count = await XianyuProduct.all().count()
        if count > 0:
            print(f"✅ 数据库中已有 {count} 条数据")
            return True

        # 创建测试商品数据
        test_products = [
            {
                "title": "iPhone 13 128G 95新 无维修",
                "price": "3200",
                "price_cents": 320000,
                "area": "北京市朝阳区",
                "seller": "张三",
                "link": "https://test.url/1",
                "link_hash": "test_hash_1_" + "a" * 20,
                "image_url": "https://test.img/1.jpg",
            },
            {
                "title": "iPhone 12 64G 9成新 原装",
                "price": "2800",
                "price_cents": 280000,
                "area": "上海市浦东新区",
                "seller": "李四",
                "link": "https://test.url/2",
                "link_hash": "test_hash_2_" + "b" * 20,
                "image_url": "https://test.img/2.jpg",
            },
            {
                "title": "MacBook Air M1 256G 几乎全新",
                "price": "5500",
                "price_cents": 550000,
                "area": "深圳市南山区",
                "seller": "王五",
                "link": "https://test.url/3",
                "link_hash": "test_hash_3_" + "c" * 20,
                "image_url": "https://test.img/3.jpg",
            },
            {
                "title": "iPhone 11 Pro 128G 8成新",
                "price": "2200",
                "price_cents": 220000,
                "area": "广州市天河区",
                "seller": "赵六",
                "link": "https://test.url/4",
                "link_hash": "test_hash_4_" + "d" * 20,
                "image_url": "https://test.img/4.jpg",
            },
            {
                "title": "MacBook Pro 13 512G 9新",
                "price": "7800",
                "price_cents": 780000,
                "area": "杭州市西湖区",
                "seller": "钱七",
                "link": "https://test.url/5",
                "link_hash": "test_hash_5_" + "e" * 20,
                "image_url": "https://test.img/5.jpg",
            },
        ]

        for product_data in test_products:
            await XianyuProduct.create(**product_data)

        print(f"✅ 成功创建 {len(test_products)} 条测试数据")
        return True

    except Exception as e:
        print(f"❌ 创建测试数据失败：{str(e)}")
        return False
    finally:
        await Tortoise.close_connections()


async def test_data_query():
    """测试数据查询功能"""
    print("🔍 测试数据查询...")
    try:
        # 测试关键词查询
        iphone_products = await get_products_by_keyword("iPhone", limit=3)
        print(f"✅ iPhone查询结果：{len(iphone_products)} 条")

        # 测试全量查询
        all_products = await get_all_products(limit=5)
        print(f"✅ 全量查询结果：{len(all_products)} 条")

        if iphone_products:
            print("📱 示例iPhone商品：")
            product = iphone_products[0]
            price_display = product.get("price", "未知")
            if product.get("price_cents", -1) > 0:
                price_display = f"{product['price_cents'] / 100:.0f}元"
            print(f"   标题：{product.get('title')}")
            print(f"   价格：{price_display}")
            print(f"   地区：{product.get('area')}")

        return len(iphone_products) > 0 or len(all_products) > 0

    except Exception as e:
        print(f"❌ 数据查询失败：{str(e)}")
        return False


async def test_llm_analyzer():
    """测试LLM分析器"""
    print("🤖 测试LLM分析器...")
    try:
        # 初始化分析器
        analyzer = DynamicLLMAnalyzer()

        # 获取测试数据
        products = await get_products_by_keyword("iPhone", limit=2)
        if not products:
            products = await get_all_products(limit=2)

        if not products:
            print("❌ 没有可用的测试数据")
            return False

        print(f"📊 使用 {len(products)} 条商品进行测试分析")

        # 简单测试提示
        test_prompt = "总结这些商品的基本信息"

        print("🔄 执行LLM分析...")
        result = await analyzer.analyze_with_prompt(products, test_prompt)

        print("✅ LLM分析完成")
        print("📋 分析结果：")
        print("-" * 50)
        print(result)
        print("-" * 50)

        return True

    except Exception as e:
        print(f"❌ LLM分析失败：{str(e)}")
        if "Connection refused" in str(e) or "Failed to connect" in str(e):
            print("💡 提示：请确保Ollama服务正在运行（ollama serve）")
        elif "model" in str(e).lower():
            print("💡 提示：请检查模型是否已安装（ollama list）")
        return False


async def main():
    """主测试程序"""
    print("🧪 LLM动态分析模块基础测试")
    print("=" * 60)

    tests = [
        ("数据库连接", test_database_connection),
        ("创建测试数据", create_test_data),
        ("数据查询功能", test_data_query),
        ("LLM分析器", test_llm_analyzer),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🔧 [{test_name}]")
        success = await test_func()
        results.append((test_name, success))

        if not success:
            print(f"⚠️  {test_name} 测试失败，但继续其他测试...")

    print("\n" + "=" * 60)
    print("📊 测试结果汇总：")

    all_passed = True
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"   {test_name:<15} | {status}")
        if not success:
            all_passed = False

    print("-" * 60)

    if all_passed:
        print("🎉 所有测试通过！LLM动态分析模块可以正常使用")
        print("\n🚀 下一步可以尝试：")
        print("   python llm_cli.py '找出性价比最高的iPhone'")
        print("   python llm_cli.py --interactive")
    else:
        print("⚠️  部分测试失败，请检查相关配置")
        print("\n🔧 常见问题解决：")
        print("   1. 确保Ollama服务运行：ollama serve")
        print("   2. 检查可用模型：ollama list")
        print("   3. 安装推荐模型：ollama pull qwen2.5:0.6b")
        print("   4. 检查依赖安装：uv sync")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
