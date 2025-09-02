#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# 测试 API 连接
import asyncio

from analyzer_api import DynamicLLMAnalyzerAPI


async def test_api():
    analyzer = DynamicLLMAnalyzerAPI()
    result = await analyzer.test_connection()
    print("连接测试结果:", result)

    # 测试简单的分析请求
    test_products = [{"title": "测试商品", "price": "100元"}]
    try:
        response = await analyzer.analyze_with_prompt(
            test_products, "简单分析这个商品"
        )
        print("测试成功:", response[:100])
    except Exception as e:
        print("测试失败:", str(e))


def main():
    asyncio.run(test_api())


if __name__ == "__main__":
    main()
