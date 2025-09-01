"""
价格解析工具模块

用于将各种格式的价格字符串解析为整数（分），支持数值计算和排序。
"""

import re


def parse_price_to_cents(price_str: str) -> int:
    """
    将价格字符串转换为分(整数)

    Args:
        price_str: 价格字符串，如"¥1200", "1.2万", "价格异常", "¥2,500", "1200"

    Returns:
        int: 价格(分)，异常时返回-1

    Examples:
        >>> parse_price_to_cents("¥1200")
        120000
        >>> parse_price_to_cents("1.2万")
        1200000
        >>> parse_price_to_cents("¥2,500")
        250000
        >>> parse_price_to_cents("价格异常")
        -1
        >>> parse_price_to_cents("")
        -1
        >>> parse_price_to_cents("1200")  # 无¥符号
        120000
    """
    if not isinstance(price_str, str) or not price_str.strip():
        return -1

    price_str = price_str.strip()

    # 如果是异常价格标识
    if any(
        keyword in price_str
        for keyword in ["异常", "暂无", "待定", "免费", "面议"]
    ):
        return -1

    # 移除非数字字符，保留小数点和万
    cleaned_str = re.sub(r"[^\d.,\u4e07万]", "", price_str)
    if not cleaned_str:
        return -1

    try:
        # 处理"万"单位
        if "万" in cleaned_str or "\u4e07" in cleaned_str:
            # 移除"万"字，保留数字部分
            num_str = re.sub(r"[万\u4e07]", "", cleaned_str)
            if not num_str:
                return -1

            # 转换为浮点型，然后乘以万倍
            price_value = float(num_str) * 10000
        else:
            # 处理普通数字，移除逗号分隔符
            num_str = re.sub(r",", "", cleaned_str)
            if not num_str:
                return -1
            price_value = float(num_str)

        # 转换为分（整数）
        price_cents = int(round(price_value * 100))

        # 确保价格非负
        return max(-1, price_cents)

    except (ValueError, TypeError):
        return -1


def format_cents_to_display(price_cents: int) -> str:
    """
    将分格式价格转换为显示格式

    Args:
        price_cents: 价格(分)

    Returns:
        str: 格式化显示字符串
    """
    if price_cents < 0:
        return "价格异常"

    yuan_value = price_cents / 100

    if yuan_value >= 10000:
        return f"¥{yuan_value / 10000:.1f}万"
    else:
        return f"¥{yuan_value:.0f}"


def test_price_parser():
    """测试价格解析功能"""
    test_cases = [
        ("¥1200", 120000),
        ("¥1200.00", 120000),
        ("¥1,200", 120000),
        ("¥2,500.50", 250050),
        ("1.2万", 1200000),
        ("¥1.2万", 1200000),
        ("12000", 1200000),
        ("价格异常", -1),
        ("", -1),
        ("¥", -1),
        ("暂无价格", -1),
        ("面议", -1),
        ("免费", -1),
    ]

    print("开始测试价格解析功能...")
    all_passed = True

    for price_str, expected in test_cases:
        result = parse_price_to_cents(price_str)
        status = "✓" if result == expected else "✗"
        if result != expected:
            all_passed = False
        print(f"{status} {price_str} -> {result} (期望: {expected})")

    if all_passed:
        print("🎉 所有测试用例通过！")
    else:
        print("❌ 部分测试用例失败")


if __name__ == "__main__":
    # 命令行测试时可直接运行
    test_price_parser()
