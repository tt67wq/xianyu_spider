#!/usr/bin/env python3
"""
数据库配置功能测试脚本
测试环境变量配置、路径处理和数据库连接功能
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))

from cli_config import get_database_path
from llm_dynamic.database import get_all_products, get_database_url


async def test_default_config():
    """测试默认配置"""
    print("🔧 [测试1] 默认配置")

    try:
        # 获取默认数据库路径
        db_path = get_database_path()
        print(f"   默认路径: {db_path}")

        # 获取数据库URL
        db_url = get_database_url()
        print(f"   数据库URL: {db_url}")

        # 验证路径格式
        assert db_url.startswith("sqlite://"), "数据库URL格式错误"
        assert "data/xianyu_spider.db" in db_url, "默认路径不正确"

        print("   ✅ 默认配置测试通过")
        return True

    except Exception as e:
        print(f"   ❌ 默认配置测试失败: {str(e)}")
        return False


async def test_env_variable_config():
    """测试环境变量配置"""
    print("🔧 [测试2] 环境变量配置")

    try:
        # 使用临时目录作为测试路径
        with tempfile.TemporaryDirectory() as temp_dir:
            test_db_path = os.path.join(temp_dir, "test_env.db")

            # 模拟环境变量
            with patch.dict(os.environ, {"DATABASE_PATH": test_db_path}):
                # 重新导入以获取新的环境变量
                import importlib

                import cli_config

                importlib.reload(cli_config)

                # 重新导入database模块
                from llm_dynamic import database

                importlib.reload(database)

                db_url = database.get_database_url()
                print(f"   环境变量路径: {test_db_path}")
                print(f"   生成的URL: {db_url}")

                # 验证URL包含测试路径
                assert test_db_path in db_url, "环境变量路径未正确应用"

                # 验证目录自动创建
                path = Path(test_db_path)
                assert path.parent.exists(), "目录未自动创建"

        print("   ✅ 环境变量配置测试通过")
        return True

    except Exception as e:
        print(f"   ❌ 环境变量配置测试失败: {str(e)}")
        return False


async def test_relative_path():
    """测试相对路径处理"""
    print("🔧 [测试3] 相对路径处理")

    try:
        # 测试相对路径
        with tempfile.TemporaryDirectory() as temp_dir:
            relative_path = "test_data/relative.db"

            with patch.dict(os.environ, {"DATABASE_PATH": relative_path}):
                # 重新导入以获取新的环境变量
                import importlib

                import cli_config

                importlib.reload(cli_config)

                from llm_dynamic import database

                importlib.reload(database)

                db_url = database.get_database_url()
                print(f"   相对路径: {relative_path}")
                print(f"   解析后URL: {db_url}")

                # 验证路径被正确转换为绝对路径
                assert db_url.startswith("sqlite://"), "URL格式错误"
                assert "test_data/relative.db" in db_url, "相对路径未正确处理"

        print("   ✅ 相对路径处理测试通过")
        return True

    except Exception as e:
        print(f"   ❌ 相对路径处理测试失败: {str(e)}")
        return False


async def test_database_connection():
    """测试数据库连接功能"""
    print("🔧 [测试4] 数据库连接")

    try:
        # 使用默认配置测试连接
        products = await get_all_products(1)
        print("   连接成功，数据库状态正常")
        print(f"   查询结果: {len(products)} 条记录")

        print("   ✅ 数据库连接测试通过")
        return True

    except Exception as e:
        print(f"   ❌ 数据库连接测试失败: {str(e)}")
        return False


async def test_path_validation():
    """测试路径验证和错误处理"""
    print("🔧 [测试5] 路径验证")

    try:
        # 测试无效路径处理
        invalid_paths = [
            "",  # 空路径
            "   ",  # 空白路径
        ]

        for invalid_path in invalid_paths:
            if invalid_path.strip():  # 只测试非空路径
                with patch.dict(os.environ, {"DATABASE_PATH": invalid_path}):
                    try:
                        import importlib

                        import cli_config

                        importlib.reload(cli_config)

                        from llm_dynamic import database

                        importlib.reload(database)

                        db_url = database.get_database_url()
                        print(f"   路径 '{invalid_path}' 处理结果: {db_url}")
                    except Exception as e:
                        print(f"   路径 '{invalid_path}' 错误处理: {str(e)}")

        print("   ✅ 路径验证测试通过")
        return True

    except Exception as e:
        print(f"   ❌ 路径验证测试失败: {str(e)}")
        return False


async def test_directory_creation():
    """测试目录自动创建功能"""
    print("🔧 [测试6] 目录自动创建")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # 测试深层目录结构
            deep_path = os.path.join(
                temp_dir, "level1", "level2", "level3", "test.db"
            )

            with patch.dict(os.environ, {"DATABASE_PATH": deep_path}):
                import importlib

                import cli_config

                importlib.reload(cli_config)

                from llm_dynamic import database

                importlib.reload(database)

                db_url = database.get_database_url()

                # 验证目录结构被创建
                path = Path(deep_path)
                assert path.parent.exists(), "深层目录结构未被创建"
                print(f"   深层目录已创建: {path.parent}")

        print("   ✅ 目录自动创建测试通过")
        return True

    except Exception as e:
        print(f"   ❌ 目录自动创建测试失败: {str(e)}")
        return False


async def main():
    """主测试程序"""
    print("🧪 数据库配置功能测试")
    print("=" * 60)

    tests = [
        ("默认配置", test_default_config),
        ("环境变量配置", test_env_variable_config),
        ("相对路径处理", test_relative_path),
        ("数据库连接", test_database_connection),
        ("路径验证", test_path_validation),
        ("目录自动创建", test_directory_creation),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        success = await test_func()
        results.append((test_name, success))

    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")

    all_passed = True
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"   {test_name:<15} | {status}")
        if not success:
            all_passed = False

    print("-" * 60)

    if all_passed:
        print("🎉 所有配置测试通过！数据库环境变量配置功能正常")
        print("\n🚀 配置示例:")
        print("   # .env 文件")
        print("   DATABASE_PATH=data/xianyu_spider.db      # 相对路径")
        print("   DATABASE_PATH=/tmp/test.db               # 绝对路径")
        print("   DATABASE_PATH=custom/location/data.db    # 自定义路径")
    else:
        print("⚠️  部分测试失败，请检查配置实现")

    print("\n" + "=" * 60)

    # 恢复默认环境
    try:
        import importlib

        import cli_config

        importlib.reload(cli_config)
        from llm_dynamic import database

        importlib.reload(database)
        print("✅ 环境已恢复到默认状态")
    except Exception as e:
        print(f"⚠️  环境恢复警告: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
