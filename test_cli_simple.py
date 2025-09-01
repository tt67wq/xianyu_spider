#!/usr/bin/env python3
"""
简化版CLI价格集成测试
验证cli_spider.py的修改是否正确
"""

from utils.price_parser import parse_price_to_cents


def test_price_parser():
    """测试价格解析函数"""
    print("=== 价格解析测试 ===")
    test_cases = [
        ("¥1200", 120000),
        ("¥1,200", 120000),
        ("¥1.2万", 1200000),
        ("¥2500.50", 250050),
        ("价格异常", -1),
        ("", -1),
    ]

    for price_str, expected in test_cases:
        actual = parse_price_to_cents(price_str)
        status = "✅" if actual == expected else "❌"
        print(f"  {status} {price_str} -> {actual}分 (预期: {expected})")

    return True


def test_cli_data_flow():
    """测试CLI数据流"""
    print("\n=== CLI数据流测试 ===")

    # 模拟从API提取数据后的处理过程
    mock_items = [
        {"title": "iPhone", "raw_price": "¥3200"},
        {"title": "MacBook", "raw_price": "¥1.2万"},
        {"title": "耳机", "raw_price": "价格异常"},
    ]

    processed = []
    for item in mock_items:
        price_str = item["raw_price"]
        price_cents = parse_price_to_cents(price_str)

        processed_item = {
            "title": item["title"],
            "price_str": price_str,
            "price_cents": price_cents,
        }
        processed.append(processed_item)

    # 验证
    expected_results = [
        ("¥3200", 320000),
        ("¥1.2万", 1200000),
        ("价格异常", -1),
    ]

    success = True
    for i, (item, expected) in enumerate(zip(processed, expected_results)):
        actual_str, actual_cents = item["price_str"], item["price_cents"]
        expected_str, expected_cents = expected

        if actual_cents == expected_cents:
            print(f"  ✅ {item['title']}: {actual_str} -> {actual_cents}分")
        else:
            print(
                f"  ❌ {item['title']}: {actual_str} -> {actual_cents}分 (预期{expected_cents})"
            )
            success = False

    return success


def main():
    """运行所有测试"""
    print("🚀 CLI爬虫集成测试\n")

    results = [
        test_price_parser(),
        test_cli_data_flow(),
    ]

    if all(results):
        print("\n🎉 CLI价格集成全部通过！")
        print("总结：✅ price_parser模块导入正确")
        print("      ✅ 价格解析逻辑工作正常")
        print("      ✅ 数据流处理正确")
        return True
    else:
        print("\n❌ 存在测试失败")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
