#!/usr/bin/env python3
"""
CLI框架综合测试脚本
验证 1.3 CLI框架任务的完成情况
"""

import asyncio
import os
import sys
import tempfile
from unittest.mock import patch

# 添加项目路径到sys.path以便导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli_config import (
    CLIConfig,
    CLIError,
    ConfigError,
    DatabaseError,
    OutputError,
    SpiderError,
    get_config,
    handle_cli_error,
)
from cli_spider import create_parser, save_to_csv, save_to_json
from database import close_database, init_database


async def test_cli_config():
    """测试CLI配置管理"""
    print("🔍 测试CLI配置管理...")

    try:
        # 测试配置加载
        config = get_config()
        if not isinstance(config, CLIConfig):
            print("❌ 配置实例类型错误")
            return False

        # 测试配置访问
        test_keys = [
            "database.path",
            "spider.request_delay",
            "spider.browser_headless",
            "ui.table_max_rows_default",
            "output.default_format",
        ]

        for key in test_keys:
            value = config.get(key)
            if value is None:
                print(f"❌ 配置键 {key} 返回 None")
                return False

        print("✅ 配置键访问正常")

        # 测试配置验证方法
        try:
            config.validate_pages(5)
            config.validate_table_limit(20)
            config.validate_output_format("json")
            print("✅ 配置验证方法正常")
        except Exception as e:
            print(f"❌ 配置验证方法失败: {e}")
            return False

        # 测试配置边界值
        try:
            config.validate_pages(0)
            print("❌ 页数验证应该拒绝0")
            return False
        except ValueError:
            print("✅ 页数验证正确拒绝了无效值")

        try:
            config.validate_output_format("invalid")
            print("❌ 输出格式验证应该拒绝无效格式")
            return False
        except ValueError:
            print("✅ 输出格式验证正确拒绝了无效值")

        return True

    except Exception as e:
        print(f"❌ CLI配置测试失败: {e}")
        return False


async def test_cli_errors():
    """测试CLI错误处理"""
    print("\n🔍 测试CLI错误处理...")

    try:
        # 测试自定义异常类
        error_classes = [
            CLIError,
            ConfigError,
            DatabaseError,
            SpiderError,
            OutputError,
        ]

        for error_class in error_classes:
            try:
                raise error_class("测试错误")
            except error_class as e:
                if not isinstance(e, CLIError):
                    print(f"❌ {error_class.__name__} 不是 CLIError 的子类")
                    return False

        print("✅ 自定义异常类继承关系正确")

        # 测试错误处理函数
        with patch("builtins.print") as mock_print:
            exit_code = handle_cli_error(CLIError("测试错误"), debug=False)
            if exit_code != 1:
                print(f"❌ CLIError 处理返回了错误的退出码: {exit_code}")
                return False

            exit_code = handle_cli_error(KeyboardInterrupt(), debug=False)
            if exit_code != 130:
                print(
                    f"❌ KeyboardInterrupt 处理返回了错误的退出码: {exit_code}"
                )
                return False

        print("✅ 错误处理函数工作正常")

        return True

    except Exception as e:
        print(f"❌ CLI错误处理测试失败: {e}")
        return False


async def test_argparse_integration():
    """测试argparse集成"""
    print("\n🔍 测试argparse集成...")

    try:
        # 测试解析器创建
        parser = create_parser()
        if parser is None:
            print("❌ 解析器创建失败")
            return False

        print("✅ 解析器创建成功")

        # 测试帮助命令解析
        test_args = [
            ["--help"],
            ["search", "--help"],
            ["info", "--help"],
        ]

        for args in test_args:
            try:
                parser.parse_args(args)
                print(f"❌ 帮助命令 {args} 应该导致SystemExit")
                return False
            except SystemExit:
                # 这是预期的行为
                pass

        print("✅ 帮助命令解析正常")

        # 测试有效命令解析
        valid_commands = [
            ["search", "test"],
            ["search", "test", "-p", "2"],
            ["search", "test", "--format", "json"],
            ["search", "test", "--no-db"],
            ["info"],
        ]

        for cmd in valid_commands:
            try:
                args = parser.parse_args(cmd)
                if args.command not in ["search", "info"]:
                    print(f"❌ 命令解析错误: {cmd}")
                    return False
            except Exception as e:
                print(f"❌ 有效命令解析失败 {cmd}: {e}")
                return False

        print("✅ 有效命令解析正常")

        return True

    except Exception as e:
        print(f"❌ argparse集成测试失败: {e}")
        return False


async def test_output_functions():
    """测试输出功能"""
    print("\n🔍 测试输出功能...")

    try:
        # 准备测试数据
        test_data = [
            {
                "商品标题": "测试商品1",
                "当前售价": "¥100",
                "发货地区": "北京",
                "卖家昵称": "测试卖家1",
                "商品链接": "https://test1.com",
                "商品图片链接": "https://test1.com/image.jpg",
                "发布时间": "2024-12-19 10:00",
            },
            {
                "商品标题": "测试商品2",
                "当前售价": "¥200",
                "发货地区": "上海",
                "卖家昵称": "测试卖家2",
                "商品链接": "https://test2.com",
                "商品图片链接": "https://test2.com/image.jpg",
                "发布时间": "2024-12-19 11:00",
            },
        ]

        # 测试JSON保存
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json_file = f.name

        try:
            success = save_to_json(test_data, json_file)
            if not success:
                print("❌ JSON保存函数返回False")
                return False

            # 验证文件内容
            with open(json_file, "r", encoding="utf-8") as f:
                import json

                loaded_data = json.load(f)
                if len(loaded_data) != 2:
                    print("❌ JSON文件内容不正确")
                    return False

            print("✅ JSON保存功能正常")

        finally:
            os.unlink(json_file)

        # 测试CSV保存
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as f:
            csv_file = f.name

        try:
            success = save_to_csv(test_data, csv_file)
            if not success:
                print("❌ CSV保存函数返回False")
                return False

            # 验证文件内容
            with open(csv_file, "r", encoding="utf-8") as f:
                import csv

                reader = csv.DictReader(f)
                rows = list(reader)
                if len(rows) != 2:
                    print("❌ CSV文件内容不正确")
                    return False

            print("✅ CSV保存功能正常")

        finally:
            os.unlink(csv_file)

        # 测试错误处理
        try:
            save_to_json(test_data, "/invalid/path/file.json")
            print("❌ JSON保存应该抛出OutputError")
            return False
        except OutputError:
            print("✅ JSON保存错误处理正常")

        try:
            save_to_csv([], csv_file)
            print("❌ CSV保存空数据应该抛出OutputError")
            return False
        except OutputError:
            print("✅ CSV保存空数据错误处理正常")

        return True

    except Exception as e:
        print(f"❌ 输出功能测试失败: {e}")
        return False


async def test_database_integration():
    """测试数据库集成"""
    print("\n🔍 测试数据库集成...")

    try:
        # 测试数据库初始化
        success = await init_database()
        if not success:
            print("❌ 数据库初始化失败")
            return False

        print("✅ 数据库初始化成功")

        # 测试数据库关闭
        success = await close_database()
        if not success:
            print("❌ 数据库关闭失败")
            return False

        print("✅ 数据库关闭成功")

        return True

    except Exception as e:
        print(f"❌ 数据库集成测试失败: {e}")
        return False


async def test_cli_main_function():
    """测试CLI主函数集成"""
    print("\n🔍 测试CLI主函数集成...")

    try:
        # 由于主函数涉及sys.argv，我们测试关键组件的集成
        from cli_spider import create_parser

        # 测试解析器和配置的集成
        parser = create_parser()

        # 模拟命令行参数
        test_args = parser.parse_args(["info"])

        if test_args.command != "info":
            print("❌ 解析器集成测试失败")
            return False

        print("✅ CLI主函数组件集成正常")

        # 测试配置和解析器的默认值一致性
        config = get_config()
        spider_config = config.get_spider_config()
        ui_config = config.get_ui_config()

        search_args = parser.parse_args(["search", "test"])

        if search_args.pages != spider_config["max_pages_default"]:
            print("❌ 默认页数配置不一致")
            return False

        if search_args.limit != ui_config["table_max_rows_default"]:
            print("❌ 默认表格行数配置不一致")
            return False

        print("✅ 配置和解析器默认值一致")

        # 测试全局verbose参数
        try:
            verbose_args = parser.parse_args(["-v", "info"])
            if not hasattr(verbose_args, "verbose") or not verbose_args.verbose:
                print("❌ 全局verbose参数解析失败")
                return False
            print("✅ 全局verbose参数解析正常")
        except Exception as e:
            print(f"❌ 全局verbose参数测试失败: {e}")
            return False

        return True

    except Exception as e:
        print(f"❌ CLI主函数集成测试失败: {e}")
        return False


async def test_environment_variables():
    """测试环境变量处理"""
    print("\n🔍 测试环境变量处理...")

    try:
        config = get_config()

        # 测试必要的环境变量是否被正确读取
        required_vars = [
            ("DATABASE_PATH", "database.path"),
            ("REQUEST_DELAY", "spider.request_delay"),
            ("BROWSER_HEADLESS", "spider.browser_headless"),
            ("USER_AGENT", "spider.user_agent"),
            ("DEBUG", "debug.enabled"),
        ]

        for env_var, config_key in required_vars:
            config_value = config.get(config_key)
            if config_value is None:
                print(f"❌ 环境变量 {env_var} 对应的配置 {config_key} 为空")
                return False

        print("✅ 环境变量处理正常")

        # 测试类型转换
        if not isinstance(config.get("spider.request_delay"), float):
            print("❌ REQUEST_DELAY 类型转换失败")
            return False

        if not isinstance(config.get("spider.browser_headless"), bool):
            print("❌ BROWSER_HEADLESS 类型转换失败")
            return False

        print("✅ 环境变量类型转换正常")

        return True

    except Exception as e:
        print(f"❌ 环境变量处理测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("=" * 70)
    print("🚀 开始执行CLI框架综合测试")
    print("=" * 70)

    tests = [
        ("CLI配置管理测试", test_cli_config),
        ("CLI错误处理测试", test_cli_errors),
        ("argparse集成测试", test_argparse_integration),
        ("输出功能测试", test_output_functions),
        ("数据库集成测试", test_database_integration),
        ("CLI主函数集成测试", test_cli_main_function),
        ("环境变量处理测试", test_environment_variables),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{'=' * 50}")
        print(f"开始测试: {test_name}")
        print("=" * 50)

        result = await test_func()
        results.append((test_name, result))

        if result:
            print(f"✅ {test_name} - 通过")
        else:
            print(f"❌ {test_name} - 失败")

    # 确保清理数据库连接
    try:
        await close_database()
    except:
        pass

    print("\n" + "=" * 70)
    print("📊 测试结果汇总")
    print("=" * 70)

    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 所有测试通过！CLI框架功能正常。")
        print("✅ 1.3.1 创建 cli_spider.py - 完成")
        print("✅ 1.3.2 实现argparse参数解析 - 完成")
        print("✅ 1.3.3 设置默认配置和错误处理 - 完成")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")
    print("=" * 70)

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
