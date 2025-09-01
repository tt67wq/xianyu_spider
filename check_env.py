#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境配置验证脚本
用于检查SQLite数据库配置和环境变量是否正确设置
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Tuple


def print_header(title: str):
    """打印格式化的标题"""
    print(f"\n{'=' * 50}")
    print(f" {title}")
    print("=" * 50)


def print_check(item: str, status: bool, details: str = ""):
    """打印检查结果"""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {item}")
    if details:
        print(f"   {details}")


def check_python_version() -> bool:
    """检查Python版本"""
    version = sys.version_info
    required = (3, 8)

    if version >= required:
        print_check(
            f"Python版本: {version.major}.{version.minor}.{version.micro}", True
        )
        return True
    else:
        print_check(
            f"Python版本: {version.major}.{version.minor}.{version.micro}",
            False,
            f"需要Python {required[0]}.{required[1]}+",
        )
        return False


def check_required_packages() -> bool:
    """检查必需的Python包"""
    required_packages = [
        ("fastapi", "fastapi"),
        ("tortoise", "tortoise"),
        ("aiosqlite", "aiosqlite"),
        ("playwright", "playwright"),
        ("uvicorn", "uvicorn"),
        ("python-dotenv", "dotenv"),
    ]

    missing_packages = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print_check(f"包 {package_name}", True)
        except ImportError:
            print_check(f"包 {package_name}", False, "未安装")
            missing_packages.append(package_name)

    if missing_packages:
        print(f"\n缺失的包: {', '.join(missing_packages)}")
        print("请运行: pip install " + " ".join(missing_packages))
        return False

    return True


def check_project_structure() -> bool:
    """检查项目目录结构"""
    project_root = Path(__file__).parent
    required_files = ["spider.py", ".env.example"]
    required_dirs = ["data"]

    all_good = True

    for file in required_files:
        file_path = project_root / file
        exists = file_path.exists()
        print_check(f"文件 {file}", exists)
        if not exists:
            all_good = False

    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        exists = dir_path.exists()
        print_check(f"目录 {dir_name}/", exists)
        if not exists:
            all_good = False
            print(f"   创建目录: mkdir {dir_name}")

    return all_good


def check_env_file() -> Tuple[bool, Dict[str, str]]:
    """检查环境变量文件"""
    from dotenv import load_dotenv

    project_root = Path(__file__).parent
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"

    if not env_file.exists():
        print_check(".env文件", False, "不存在")
        if env_example.exists():
            print("   建议: cp .env.example .env")
        return False, {}

    print_check(".env文件", True)

    # 加载环境变量
    load_dotenv(env_file)

    # 检查关键环境变量
    env_vars = {
        "DATABASE_PATH": os.getenv("DATABASE_PATH", ""),
        "SERVER_HOST": os.getenv("SERVER_HOST", ""),
        "SERVER_PORT": os.getenv("SERVER_PORT", ""),
        "DEBUG": os.getenv("DEBUG", ""),
        "REQUEST_DELAY": os.getenv("REQUEST_DELAY", ""),
    }

    for key, value in env_vars.items():
        has_value = bool(value.strip())
        print_check(f"  {key}", has_value, value if has_value else "未设置")

    return True, env_vars


async def check_database_connection(env_vars: Dict[str, str]) -> bool:
    """检查数据库连接"""
    try:
        from tortoise import Tortoise

        # 构建数据库路径
        project_root = Path(__file__).parent
        db_path = env_vars.get("DATABASE_PATH", "data/xianyu_spider.db")
        full_db_path = project_root / db_path

        # 确保数据目录存在
        full_db_path.parent.mkdir(exist_ok=True)

        # 数据库配置
        db_url = f"sqlite://{full_db_path.absolute()}"
        config = {
            "connections": {"default": db_url},
            "apps": {
                "models": {
                    "models": ["spider"],
                    "default_connection": "default",
                }
            },
        }

        print_check(f"数据库路径: {full_db_path}", True)

        # 测试连接
        await Tortoise.init(config=config)
        print_check("数据库连接", True)

        # 生成表结构
        await Tortoise.generate_schemas()
        print_check("表结构创建", True)

        # 检查数据库文件
        if full_db_path.exists():
            size = full_db_path.stat().st_size
            print_check(f"数据库文件大小: {size} bytes", True)

        await Tortoise.close_connections()
        print_check("数据库连接关闭", True)

        return True

    except Exception as e:
        print_check("数据库连接", False, str(e))
        return False


async def check_playwright_browser() -> bool:
    """检查Playwright浏览器"""
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            # 检查Chromium是否安装
            try:
                browser = await p.chromium.launch(headless=True)
                print_check("Playwright Chromium", True)
                await browser.close()
                return True
            except Exception as e:
                print_check("Playwright Chromium", False, str(e))
                print("   建议运行: playwright install chromium")
                return False

    except ImportError:
        print_check("Playwright", False, "未安装")
        return False


def check_port_availability(host: str, port: int) -> bool:
    """检查端口是否可用"""
    import socket

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            if result == 0:
                print_check(f"端口 {host}:{port}", False, "端口被占用")
                return False
            else:
                print_check(f"端口 {host}:{port}", True, "可用")
                return True
    except Exception as e:
        print_check(f"端口 {host}:{port}", False, str(e))
        return False


async def main():
    """主检查函数"""
    print("🔍 闲鱼爬虫项目环境配置检查")

    # 检查列表
    checks = []

    # 1. Python版本检查
    print_header("Python环境检查")
    checks.append(check_python_version())

    # 2. 包依赖检查
    print_header("依赖包检查")
    checks.append(check_required_packages())

    # 3. 项目结构检查
    print_header("项目结构检查")
    checks.append(check_project_structure())

    # 4. 环境变量检查
    print_header("环境变量检查")
    env_ok, env_vars = check_env_file()
    checks.append(env_ok)

    # 5. 数据库连接检查
    print_header("数据库连接检查")
    if env_ok:
        db_ok = await check_database_connection(env_vars)
        checks.append(db_ok)
    else:
        print_check("跳过数据库检查", False, "环境变量未正确配置")
        checks.append(False)

    # 6. Playwright浏览器检查
    print_header("浏览器环境检查")
    checks.append(await check_playwright_browser())

    # 7. 端口可用性检查
    print_header("网络端口检查")
    if env_vars.get("SERVER_HOST") and env_vars.get("SERVER_PORT"):
        try:
            port = int(env_vars["SERVER_PORT"])
            host = env_vars["SERVER_HOST"]
            if host == "0.0.0.0":
                host = "127.0.0.1"  # 测试本地端口
            checks.append(check_port_availability(host, port))
        except ValueError:
            print_check("端口配置", False, "SERVER_PORT不是有效数字")
            checks.append(False)
    else:
        print_check("跳过端口检查", False, "端口配置未设置")
        checks.append(False)

    # 总结
    print_header("检查结果总结")
    passed = sum(checks)
    total = len(checks)

    if passed == total:
        print("🎉 恭喜！所有检查都通过了！")
        print("✅ 您的环境配置完全正确，可以启动项目了")
        print("\n启动命令:")
        print("  python spider.py")
    else:
        failed = total - passed
        print(f"⚠️  有 {failed} 项检查未通过，请根据上述提示进行修复")
        print(f"📊 通过率: {passed}/{total} ({passed / total * 100:.1f}%)")

        print("\n常见解决方案:")
        print("1. 安装缺失的包: pip install -r requirements.txt")
        print("2. 安装浏览器: playwright install chromium")
        print("3. 复制环境变量: cp .env.example .env")
        print("4. 创建数据目录: mkdir -p data")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n检查被用户中断")
    except Exception as e:
        print(f"\n\n检查过程中出现错误: {e}")
        sys.exit(1)
