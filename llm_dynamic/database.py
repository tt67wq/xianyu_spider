"""
商品数据读取模块
动态获取商品数据供LLM分析使用
"""

from typing import Dict, List

from tortoise import Tortoise

from models import XianyuProduct


async def get_products_by_keyword(keyword: str, limit: int = 10) -> List[Dict]:
    """
    动态获取商品数据

    Args:
        keyword: 搜索关键词
        limit: 返回商品数量限制

    Returns:
        商品数据列表，包含标题、价格、地区、卖家等信息
    """
    try:
        # 初始化数据库连接
        await Tortoise.init(
            db_url="sqlite://database.sqlite3", modules={"models": ["models"]}
        )

        # 查询商品数据
        products = (
            await XianyuProduct.filter(title__icontains=keyword)
            .limit(limit)
            .values(
                "title",
                "price",
                "price_cents",
                "area",
                "seller",
                "link",
                "publish_time",
            )
        )

        # 转换为字典列表
        return [dict(p) for p in products]

    except Exception as e:
        print(f"数据库查询错误：{str(e)}")
        return []

    finally:
        # 关闭数据库连接
        await Tortoise.close_connections()


async def get_all_products(limit: int = 20) -> List[Dict]:
    """
    获取所有商品数据（用于全量分析）

    Args:
        limit: 返回商品数量限制

    Returns:
        商品数据列表
    """
    try:
        await Tortoise.init(
            db_url="sqlite://database.sqlite3", modules={"models": ["models"]}
        )

        products = (
            await XianyuProduct.all()
            .limit(limit)
            .values(
                "title",
                "price",
                "price_cents",
                "area",
                "seller",
                "link",
                "publish_time",
            )
        )

        return [dict(p) for p in products]

    except Exception as e:
        print(f"数据库查询错误：{str(e)}")
        return []

    finally:
        await Tortoise.close_connections()


async def get_products_by_price_range(
    min_price: float = 0, max_price: float = 999999, limit: int = 10
) -> List[Dict]:
    """
    按价格范围获取商品数据

    Args:
        min_price: 最低价格
        max_price: 最高价格
        limit: 返回商品数量限制

    Returns:
        符合价格条件的商品数据列表
    """
    try:
        await Tortoise.init(
            db_url="sqlite://database.sqlite3", modules={"models": ["models"]}
        )

        products = (
            await XianyuProduct.filter(
                price__gte=min_price, price__lte=max_price
            )
            .limit(limit)
            .values(
                "title",
                "price",
                "price_cents",
                "area",
                "seller",
                "link",
                "publish_time",
            )
        )

        return [dict(p) for p in products]

    except Exception as e:
        print(f"数据库查询错误：{str(e)}")
        return []

    finally:
        await Tortoise.close_connections()


def format_products_for_display(products: List[Dict]) -> str:
    """
    格式化商品数据用于展示

    Args:
        products: 商品数据列表

    Returns:
        格式化后的商品信息字符串
    """
    if not products:
        return "没有找到相关商品数据"

    formatted = "商品列表：\n"
    for i, product in enumerate(products, 1):
        # 格式化价格显示
        price_display = product.get("price", "未知")
        if product.get("price_cents", -1) > 0:
            price_display = f"{product['price_cents'] / 100:.0f}元"

        formatted += f"\n{i}. {product.get('title', '未知标题')}\n"
        formatted += f"   价格：{price_display}\n"
        formatted += f"   地区：{product.get('area', '未知')}\n"
        formatted += f"   卖家：{product.get('seller', '未知')}\n"
        formatted += f"   发布：{product.get('publish_time', '未知')}\n"
        formatted += "-" * 50

    return formatted
