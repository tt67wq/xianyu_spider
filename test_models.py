#!/usr/bin/env python3
"""
测试脚本：验证模型和数据库连接兼容性
用于验证 1.1 数据模型分离任务的完成情况
"""

import asyncio
import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from tortoise import Tortoise

# 加载环境变量
load_dotenv()

# 导入独立的模型
from models import XianyuProduct

# 项目根目录路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 环境变量配置
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/xianyu_spider.db")

# 数据库配置
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


async def test_database_connection():
    """测试数据库连接"""
    print("🔍 正在测试数据库连接...")

    try:
        # 初始化 Tortoise ORM
        await Tortoise.init(config=DATABASE_CONFIG)
        await Tortoise.generate_schemas(safe=True)
        print("✅ 数据库连接成功")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


async def test_model_operations():
    """测试模型基本操作"""
    print("\n🔍 正在测试模型基本操作...")

    try:
        # 测试创建记录
        test_product = await XianyuProduct.create(
            title="测试商品",
            price="¥100",
            area="北京",
            seller="测试卖家",
            link="https://test.example.com/item/123",
            link_hash="test_hash_" + str(int(datetime.now().timestamp())),
            image_url="https://test.example.com/image.jpg",
            publish_time=datetime.now(),
        )
        print(f"✅ 创建测试记录成功: {test_product}")

        # 测试查询记录
        found_product = await XianyuProduct.get(id=test_product.id)
        print(f"✅ 查询记录成功: {found_product}")

        # 测试更新记录
        found_product.price = "¥120"
        await found_product.save()
        print("✅ 更新记录成功")

        # 测试删除记录
        await found_product.delete()
        print("✅ 删除测试记录成功")

        return True
    except Exception as e:
        print(f"❌ 模型操作失败: {e}")
        return False


async def test_existing_data_compatibility():
    """测试现有数据兼容性"""
    print("\n🔍 正在测试现有数据兼容性...")

    try:
        # 检查现有数据
        total_count = await XianyuProduct.all().count()
        print(f"✅ 读取现有数据成功，共 {total_count} 条记录")

        if total_count > 0:
            # 获取最新的一条记录
            latest_product = await XianyuProduct.all().order_by("-id").first()
            print(f"✅ 最新记录: {latest_product}")

        return True
    except Exception as e:
        print(f"❌ 现有数据兼容性测试失败: {e}")
        return False


async def test_environment_variables():
    """测试环境变量配置"""
    print("\n🔍 正在测试环境变量配置...")

    try:
        required_vars = [
            "DATABASE_PATH",
            "REQUEST_DELAY",
            "BROWSER_HEADLESS",
            "USER_AGENT",
        ]

        for var in required_vars:
            value = os.getenv(var)
            if value is not None:
                print(f"✅ {var}: {value}")
            else:
                print(f"⚠️  {var}: 未设置，将使用默认值")

        return True
    except Exception as e:
        print(f"❌ 环境变量测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("=" * 60)
    print("🚀 开始执行数据模型分离兼容性测试")
    print("=" * 60)

    tests = [
        ("数据库连接测试", test_database_connection),
        ("环境变量配置测试", test_environment_variables),
        ("现有数据兼容性测试", test_existing_data_compatibility),
        ("模型操作测试", test_model_operations),
    ]

    results = []

    for test_name, test_func in tests:
        result = await test_func()
        results.append((test_name, result))

    # 清理数据库连接
    await Tortoise.close_connections()

    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)

    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！数据模型分离任务完成。")
        print("✅ 1.1.1 创建 models.py - 完成")
        print("✅ 1.1.2 验证模型导入兼容性 - 完成")
        print("✅ 1.1.3 检查环境变量配置一致性 - 完成")
    else:
        print("⚠️  部分测试失败，请检查相关配置。")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试执行异常: {e}")
        sys.exit(1)
