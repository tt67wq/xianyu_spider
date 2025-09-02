"""
商品数据读取模块
动态获取商品数据供LLM分析使用
"""

import sys
from pathlib import Path
from typing import Dict, List

from tortoise import Tortoise

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))
from cli_config import get_database_path
from models import XianyuProduct


def get_database_url() -> str:
    """
    获取数据库连接URL，支持环境变量配置

    Returns:
        SQLite数据库连接字符串
    """
    # 使用现有配置管理获取路径
    db_path = get_database_path()

    # 路径处理和验证
    path = Path(db_path)
    if not path.is_absolute():
        # 相对路径，相对于项目根目录
        path = Path(__file__).parent.parent / path

    # 确保目录存在
    path.parent.mkdir(parents=True, exist_ok=True)

    # 返回SQLite连接字符串
    return f"sqlite://{path.absolute()}"


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
            db_url=get_database_url(), modules={"models": ["models"]}
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
            db_url=get_database_url(), modules={"models": ["models"]}
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
            db_url=get_database_url(), modules={"models": ["models"]}
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
