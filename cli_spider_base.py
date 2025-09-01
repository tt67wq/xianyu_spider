#!/usr/bin/env python3
"""
CLI版本爬虫基础框架
用于测试数据库连接管理功能
"""

import argparse
import asyncio
import sys
from datetime import datetime

from database import close_database, get_database_info, init_database
from models import XianyuProduct


async def test_database_connection():
    """测试数据库连接功能"""
    print("🔍 测试数据库连接管理...")

    # 初始化数据库
    success = await init_database()
    if not success:
        print("❌ 数据库初始化失败")
        return False

    print("✅ 数据库初始化成功")

    # 获取数据库信息
    info = await get_database_info()
    print("📊 数据库信息:")
    print(f"   路径: {info['database_path']}")
    print(f"   文件存在: {info['database_exists']}")
    print(f"   已初始化: {info['is_initialized']}")
    print(f"   记录数量: {info['record_count']}")

    # 测试基本数据库操作
    try:
        # 创建测试记录
        test_product = await XianyuProduct.create(
            title="CLI测试商品",
            price="¥88",
            area="上海",
            seller="CLI测试卖家",
            link="https://cli.test.com/item/456",
            link_hash=f"cli_test_{int(datetime.now().timestamp())}",
            image_url="https://cli.test.com/image.jpg",
            publish_time=datetime.now(),
        )
        print(f"✅ 创建测试记录成功: ID={test_product.id}")

        # 查询记录
        found = await XianyuProduct.get(id=test_product.id)
        print(f"✅ 查询记录成功: {found.title}")

        # 删除测试记录
        await found.delete()
        print("✅ 删除测试记录成功")

    except Exception as e:
        print(f"❌ 数据库操作测试失败: {e}")
        return False

    # 关闭数据库连接
    close_success = await close_database()
    if close_success:
        print("✅ 数据库连接关闭成功")
    else:
        print("❌ 数据库连接关闭失败")

    return success and close_success


async def cli_search(keyword: str, pages: int = 1):
    """CLI搜索功能（基础版本）"""
    print(f"🚀 开始搜索: '{keyword}' (最多 {pages} 页)")

    # 初始化数据库
    if not await init_database():
        print("❌ 数据库初始化失败")
        return 1

    try:
        # 这里将来会调用实际的爬虫功能
        # 目前只是模拟
        print("⏳ 正在搜索商品...")
        await asyncio.sleep(1)  # 模拟搜索时间

        # 获取当前数据库状态
        info = await get_database_info()
        print(f"📊 搜索完成，数据库中共有 {info['record_count']} 条记录")

        return 0

    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        return 1

    finally:
        # 确保关闭数据库连接
        await close_database()


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="闲鱼商品搜索CLI工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s test                     # 测试数据库连接
  %(prog)s search "iPhone 14"       # 搜索商品
  %(prog)s search "iPhone 14" -p 3  # 搜索3页
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 测试命令
    test_parser = subparsers.add_parser("test", help="测试数据库连接")

    # 搜索命令
    search_parser = subparsers.add_parser("search", help="搜索商品")
    search_parser.add_argument("keyword", help="搜索关键词")
    search_parser.add_argument(
        "-p", "--pages", type=int, default=1, help="最大搜索页数 (默认: 1)"
    )
    search_parser.add_argument(
        "-v", "--verbose", action="store_true", help="详细输出"
    )

    return parser


async def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    print("=" * 60)
    print("🐛 闲鱼商品搜索CLI工具 (测试版)")
    print("=" * 60)

    try:
        if args.command == "test":
            success = await test_database_connection()
            return 0 if success else 1

        elif args.command == "search":
            return await cli_search(args.keyword, args.pages)

        else:
            print(f"❌ 未知命令: {args.command}")
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\n\n⚠️  操作被用户中断")
        return 1

    except Exception as e:
        print(f"\n\n❌ 程序异常: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
