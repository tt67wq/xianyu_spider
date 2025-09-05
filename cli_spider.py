#!/usr/bin/env python3
"""
闲鱼商品搜索CLI工具
将FastAPI版本的爬虫功能改造为命令行工具
"""

import argparse
import asyncio
import csv
import hashlib
import json
import sys
import time
from datetime import datetime
from typing import Any, List

from playwright.async_api import async_playwright

from cli_config import (
    CLIError,
    DatabaseError,
    OutputError,
    SpiderError,
    get_config,
    handle_cli_error,
)
from database import close_database, get_database_info, init_database
from models import XianyuProduct
from utils.price_parser import parse_price_to_cents

# 获取配置实例
config = get_config()


def get_md5(text: str) -> str:
    """返回给定文本的MD5哈希值"""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def get_link_unique_key(link: str) -> str:
    """
    截取链接中前1个"&"之前的内容作为唯一标识依据。
    如果链接中的"&"少于1个，则返回整个链接。
    """
    parts = link.split("&", 1)
    if len(parts) >= 2:
        return "&".join(parts[:1])
    else:
        return link


async def safe_get(data: Any, *keys: Any, default: Any = "暂无") -> Any:
    """安全获取嵌套字典值"""
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError, IndexError):
            return default
    return data


async def save_to_db(
    data_list: List[dict], verbose: bool = False
) -> tuple[int, List[int]]:
    """
    逐条保存数据到数据库，若相同链接（按截取规则判断）的记录已存在则跳过，
    同时统计当前关键词下新增的记录数量，并返回新增记录的 id 列表
    """
    new_records = 0
    new_ids = []

    for i, item in enumerate(data_list, 1):
        try:
            link = item["商品链接"]
            # 先截取链接内容
            unique_part = get_link_unique_key(link)
            # 计算唯一标识的 MD5 哈希值
            link_hash = get_md5(unique_part)

            product, created = await XianyuProduct.get_or_create(
                link_hash=link_hash,
                defaults={
                    "title": item["商品标题"],
                    "price": item["当前售价"],
                    "price_cents": item.get("价格分", -1),
                    "area": item["发货地区"],
                    "seller": item["卖家昵称"],
                    "link": link,
                    "image_url": item["商品图片链接"],
                    "publish_time": datetime.strptime(
                        item["发布时间"], "%Y-%m-%d %H:%M"
                    )
                    if item["发布时间"] != "未知时间"
                    else None,
                },
            )

            if created:
                new_records += 1
                new_ids.append(product.id)
                if verbose:
                    print(
                        f"✅ 新增记录 {i}/{len(data_list)}: {item['商品标题'][:30]}..."
                    )
            else:
                if verbose:
                    print(
                        f"⏭️  跳过重复 {i}/{len(data_list)}: {item['商品标题'][:30]}..."
                    )

        except Exception as e:
            print(f"❌ 保存数据出错 {i}/{len(data_list)}: {str(e)}")

    return new_records, new_ids


async def scrape_xianyu(
    keyword: str, max_pages: int = 1, verbose: bool = False, quiet: bool = False
) -> List[dict]:
    """异步爬取闲鱼商品数据"""
    data_list = []
    spider_config = config.get_spider_config()

    if not quiet:
        print(f"🚀 开始搜索: '{keyword}' (最多 {max_pages} 页)")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=spider_config["browser_headless"]
        )
        context = await browser.new_context(
            user_agent=spider_config["user_agent"]
        )
        page = await context.new_page()

        async def on_response(response):
            """处理API响应，解析数据"""
            if (
                "h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search"
                in response.url
            ):
                try:
                    result_json = await response.json()
                    items = result_json.get("data", {}).get("resultList", [])

                    for item in items:
                        main_data = await safe_get(
                            item,
                            "data",
                            "item",
                            "main",
                            "exContent",
                            default={},
                        )
                        click_params = await safe_get(
                            item,
                            "data",
                            "item",
                            "main",
                            "clickParam",
                            "args",
                            default={},
                        )

                        # 解析商品信息
                        title = await safe_get(
                            main_data, "title", default="未知标题"
                        )

                        # 价格处理
                        price_parts = await safe_get(
                            main_data, "price", default=[]
                        )
                        price = "价格异常"
                        if isinstance(price_parts, list):
                            price = "".join(
                                [
                                    str(p.get("text", ""))
                                    for p in price_parts
                                    if isinstance(p, dict)
                                ]
                            )
                            price = price.replace("当前价", "").strip()
                            if "万" in price:
                                price = f"¥{float(price.replace('¥', '').replace('万', '')) * 10000:.0f}"

                        # 解析价格为整数(分)
                        price_cents = parse_price_to_cents(price)

                        # 其他字段解析
                        area = await safe_get(
                            main_data, "area", default="地区未知"
                        )
                        seller = await safe_get(
                            main_data, "userNickName", default="匿名卖家"
                        )
                        raw_link = await safe_get(
                            item,
                            "data",
                            "item",
                            "main",
                            "targetUrl",
                            default="",
                        )
                        image_url = await safe_get(
                            main_data, "picUrl", default=""
                        )

                        data_list.append(
                            {
                                "商品标题": title,
                                "当前售价": price,
                                "价格分": price_cents,
                                "发货地区": area,
                                "卖家昵称": seller,
                                "商品链接": raw_link.replace(
                                    "fleamarket://", "https://www.goofish.com/"
                                ),
                                "商品图片链接": f"https:{image_url}"
                                if image_url
                                and not image_url.startswith("http")
                                else image_url,
                                "发布时间": datetime.fromtimestamp(
                                    int(click_params.get("publishTime", 0))
                                    / 1000
                                ).strftime("%Y-%m-%d %H:%M")
                                if isinstance(
                                    click_params.get("publishTime"), str
                                )
                                and click_params.get(
                                    "publishTime", ""
                                ).isdigit()
                                else "未知时间",
                            }
                        )

                except Exception as e:
                    if verbose:
                        print(f"❌ 响应处理异常: {str(e)}")

        try:
            # 访问首页并操作页面
            if verbose:
                print("🌐 正在访问闲鱼首页...")
            await page.goto("https://www.goofish.com")
            await page.fill('input[class*="search-input"]', keyword)
            await page.click('button[type="submit"]')

            # 如果存在弹窗广告则关闭
            try:
                await page.wait_for_selector(
                    "div[class*='closeIconBg']", timeout=5000
                )
                await page.click("div[class*='closeIconBg']")
                if verbose:
                    print("✅ 关闭广告弹窗")
            except Exception:
                if verbose:
                    print("ℹ️  未发现广告弹窗")
                pass

            await page.click("text=新发布")
            await page.click("text=最新")

            # 注册响应监听
            page.on("response", on_response)

            # 分页处理
            current_page = 1
            while current_page <= max_pages:
                if not quiet:
                    print(f"📄 正在处理第 {current_page} 页...")
                await asyncio.sleep(
                    spider_config["request_delay"]
                )  # 等待数据加载

                if current_page < max_pages:
                    # 查找下一页按钮
                    next_btn = await page.query_selector(
                        "[class*='search-pagination-arrow-right']:not([disabled])"
                    )
                    if not next_btn:
                        if verbose:
                            print("ℹ️  已到达最后一页")
                        break
                    await next_btn.click()

                current_page += 1

        finally:
            await browser.close()

    return data_list


def print_results_table(data_list: List[dict], limit: int = 10):
    """以表格形式打印结果"""
    if not data_list:
        print("📝 没有找到商品数据")
        return

    ui_config = config.get_ui_config()
    title_len = ui_config["title_max_length"]
    price_len = ui_config["price_max_length"]
    area_len = ui_config["area_max_length"]
    seller_len = ui_config["seller_max_length"]

    print(f"\n📊 找到 {len(data_list)} 个商品:")
    print("=" * 120)
    print(
        f"{'序号':<4} {'标题':<{title_len}} {'价格':<{price_len}} {'地区':<{area_len}} {'卖家':<{seller_len}}"
    )
    print("=" * 120)

    for i, item in enumerate(data_list[:limit], 1):
        title = (
            item["商品标题"][: title_len - 2] + ".."
            if len(item["商品标题"]) > title_len
            else item["商品标题"]
        )
        price = (
            item["当前售价"][: price_len - 2] + ".."
            if len(item["当前售价"]) > price_len
            else item["当前售价"]
        )
        area = (
            item["发货地区"][: area_len - 2] + ".."
            if len(item["发货地区"]) > area_len
            else item["发货地区"]
        )
        seller = (
            item["卖家昵称"][: seller_len - 2] + ".."
            if len(item["卖家昵称"]) > seller_len
            else item["卖家昵称"]
        )

        print(
            f"{i:<4} {title:<{title_len}} {price:<{price_len}} {area:<{area_len}} {seller:<{seller_len}}"
        )

    if len(data_list) > limit:
        print(f"... 还有 {len(data_list) - limit} 个商品未显示")
    print("=" * 120)


def save_to_json(data_list: List[dict], filename: str) -> bool:
    """保存为JSON格式"""
    try:
        output_config = config.get_output_config()
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(
                data_list,
                f,
                ensure_ascii=False,
                indent=output_config["json_indent"],
            )
        return True
    except Exception as e:
        raise OutputError(f"保存JSON文件失败: {e}")


def save_to_csv(data_list: List[dict], filename: str) -> bool:
    """保存为CSV格式"""
    try:
        if not data_list:
            raise OutputError("没有数据可保存")

        output_config = config.get_output_config()
        with open(
            filename, "w", newline="", encoding=output_config["csv_encoding"]
        ) as f:
            writer = csv.DictWriter(f, fieldnames=data_list[0].keys())
            writer.writeheader()
            writer.writerows(data_list)
        return True
    except Exception as e:
        raise OutputError(f"保存CSV文件失败: {e}")


async def cli_search(args):
    """CLI搜索命令处理"""
    start_time = time.time()

    try:
        # 验证参数
        pages = config.validate_pages(args.pages)
        limit = config.validate_table_limit(args.limit)
        format_name = config.validate_output_format(args.format)

        # 初始化数据库
        if not args.no_db:
            if not await init_database():
                raise DatabaseError("数据库初始化失败")

            if args.verbose:
                db_info = await get_database_info()
                print(f"📦 数据库: {db_info['database_path']}")
                print(f"📊 现有记录: {db_info['record_count']} 条")

        # 执行搜索
        data_list = await scrape_xianyu(
            args.keyword, pages, args.verbose, args.quiet
        )

        if not data_list:
            if not args.quiet:
                print("😔 没有找到任何商品")
            return 0

        # 保存到数据库
        new_count = 0
        new_ids = []
        if not args.no_db:
            if not args.quiet:
                print("💾 正在保存到数据库...")
            new_count, new_ids = await save_to_db(data_list, args.verbose)

        # 输出结果
        elapsed_time = time.time() - start_time

        if not args.quiet:
            print(f"\n🎉 搜索完成! 用时: {elapsed_time:.2f}秒")
            print(f"📦 找到商品: {len(data_list)} 个")
            if not args.no_db:
                print(f"💾 新增记录: {new_count} 条")

        # 根据输出格式显示结果
        if format_name == "table":
            print_results_table(data_list, limit)
        elif format_name == "json":
            if args.output:
                save_to_json(data_list, args.output)
                print(f"✅ 结果已保存到: {args.output}")
            else:
                output_config = config.get_output_config()
                print(
                    json.dumps(
                        data_list,
                        ensure_ascii=False,
                        indent=output_config["json_indent"],
                    )
                )
        elif format_name == "csv":
            if args.output:
                save_to_csv(data_list, args.output)
                print(f"✅ 结果已保存到: {args.output}")
            else:
                raise OutputError("CSV格式需要指定输出文件 --output")

        return 0

    except (CLIError, ValueError) as e:
        return handle_cli_error(e, args.debug)

    except Exception as e:
        return handle_cli_error(SpiderError(f"搜索失败: {e}"), args.debug)

    finally:
        if not args.no_db:
            await close_database()


async def cli_info(args):
    """显示数据库信息"""
    try:
        if not await init_database():
            raise DatabaseError("数据库初始化失败")

        db_info = await get_database_info()

        print("📊 数据库信息:")
        print(f"   路径: {db_info['database_path']}")
        print(f"   文件存在: {'是' if db_info['database_exists'] else '否'}")
        print(f"   已初始化: {'是' if db_info['is_initialized'] else '否'}")
        print(f"   记录总数: {db_info['record_count']} 条")

        if args.verbose:
            config.print_config_summary()

            if db_info["record_count"] > 0:
                # 显示最新几条记录
                latest_products = (
                    await XianyuProduct.all().order_by("-id").limit(5)
                )
                print(f"\n📝 最新 {len(latest_products)} 条记录:")
                for i, product in enumerate(latest_products, 1):
                    print(f"   {i}. {product.title[:40]}... - {product.price}")

        return 0

    except CLIError as e:
        return handle_cli_error(e, args.debug)

    except Exception as e:
        return handle_cli_error(
            DatabaseError(f"获取数据库信息失败: {e}"), args.debug
        )

    finally:
        await close_database()


def create_parser():
    """创建命令行参数解析器"""
    spider_config = config.get_spider_config()
    ui_config = config.get_ui_config()
    output_config = config.get_output_config()

    parser = argparse.ArgumentParser(
        description="闲鱼商品搜索CLI工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s search "iPhone 14"                    # 搜索iPhone 14
  %(prog)s search "iPhone 14" -p 3               # 搜索3页
  %(prog)s search "iPhone 14" --format json      # JSON格式输出
  %(prog)s search "iPhone 14" -o results.csv     # 保存为CSV
  %(prog)s search "iPhone 14" --no-db            # 不保存到数据库
  %(prog)s info                                  # 显示数据库信息
  %(prog)s info -v                               # 显示详细数据库信息
        """,
    )

    # 全局选项
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    parser.add_argument("-q", "--quiet", action="store_true", help="静默模式")
    parser.add_argument("--debug", action="store_true", help="调试模式")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 搜索命令
    search_parser = subparsers.add_parser("search", help="搜索商品")
    search_parser.add_argument("keyword", help="搜索关键词")
    search_parser.add_argument(
        "-p",
        "--pages",
        type=int,
        default=spider_config["max_pages_default"],
        help=f"最大搜索页数 (默认: {spider_config['max_pages_default']}, 限制: {spider_config['max_pages_limit']})",
    )
    search_parser.add_argument(
        "--format",
        choices=output_config["supported_formats"],
        default=output_config["default_format"],
        help=f"输出格式 (默认: {output_config['default_format']})",
    )
    search_parser.add_argument(
        "-o", "--output", help="输出文件路径 (用于json/csv格式)"
    )
    search_parser.add_argument(
        "--no-db", action="store_true", help="不保存到数据库"
    )
    search_parser.add_argument(
        "--limit",
        type=int,
        default=ui_config["table_max_rows_default"],
        help=f"表格显示的最大行数 (默认: {ui_config['table_max_rows_default']}, 限制: {ui_config['table_max_rows_limit']})",
    )

    # 信息命令
    subparsers.add_parser("info", help="显示数据库信息")

    return parser


async def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()

    # 参数验证
    if (
        hasattr(args, "quiet")
        and hasattr(args, "verbose")
        and args.quiet
        and args.verbose
    ):
        print("❌ --quiet 和 --verbose 不能同时使用")
        return 1

    if not args.command:
        parser.print_help()
        return 1

    print("=" * 60)
    print("🕷️  闲鱼商品搜索CLI工具")
    print("=" * 60)

    try:
        if args.command == "search":
            return await cli_search(args)
        elif args.command == "info":
            return await cli_info(args)
        else:
            raise CLIError(f"未知命令: {args.command}")

    except Exception as e:
        return handle_cli_error(e, getattr(args, "debug", False))


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
