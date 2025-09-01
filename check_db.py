#!/usr/bin/env python3
"""
简单的数据库检查脚本
"""

import asyncio
import os

from dotenv import load_dotenv
from tortoise import Tortoise

from models import XianyuProduct

load_dotenv()

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/xianyu_spider.db")

DATABASE_CONFIG = {
    "connections": {
        "default": f"sqlite://{os.path.join(PROJECT_ROOT, DATABASE_PATH)}"
    },
    "apps": {
        "models": {
            "models": ["models"],
            "default_connection": "default",
        }
    },
}


async def main():
    await Tortoise.init(config=DATABASE_CONFIG)
    count = await XianyuProduct.all().count()
    print(f"数据库中现有 {count} 条记录")

    if count > 0:
        latest = await XianyuProduct.all().order_by("-id").first()
        print(f"最新记录: {latest.title[:50]}...")

    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
