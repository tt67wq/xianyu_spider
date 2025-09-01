#!/usr/bin/env python3
"""
数据库连接管理模块
用于CLI版本的独立数据库配置和连接生命周期管理
"""

import os

from dotenv import load_dotenv
from tortoise import Tortoise

# 加载环境变量
load_dotenv()

# 项目根目录路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 环境变量配置
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/xianyu_spider.db")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


class DatabaseManager:
    """数据库连接管理器"""

    def __init__(self):
        self.is_initialized = False
        self.config = self._get_database_config()

    def _get_database_config(self) -> dict:
        """获取数据库配置"""
        return {
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

    async def init_database(self, safe_schema: bool = True) -> bool:
        """
        初始化数据库连接

        Args:
            safe_schema: 安全模式创建表结构，不会删除现有数据

        Returns:
            bool: 初始化是否成功
        """
        try:
            if self.is_initialized:
                if DEBUG:
                    print("⚠️  数据库已经初始化，跳过重复初始化")
                return True

            # 确保数据库目录存在
            db_dir = os.path.dirname(os.path.join(PROJECT_ROOT, DATABASE_PATH))
            if not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                if DEBUG:
                    print(f"📁 创建数据库目录: {db_dir}")

            # 初始化 Tortoise ORM
            await Tortoise.init(config=self.config)

            # 生成数据库表结构
            await Tortoise.generate_schemas(safe=safe_schema)

            self.is_initialized = True

            if DEBUG:
                print(
                    f"✅ 数据库初始化成功: {os.path.join(PROJECT_ROOT, DATABASE_PATH)}"
                )

            return True

        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            return False

    async def close_database(self) -> bool:
        """
        关闭数据库连接

        Returns:
            bool: 关闭是否成功
        """
        try:
            if not self.is_initialized:
                if DEBUG:
                    print("⚠️  数据库未初始化，无需关闭")
                return True

            await Tortoise.close_connections()
            self.is_initialized = False

            if DEBUG:
                print("✅ 数据库连接已关闭")

            return True

        except Exception as e:
            print(f"❌ 关闭数据库连接失败: {e}")
            return False

    async def reset_database(self) -> bool:
        """
        重置数据库（危险操作，慎用）

        Returns:
            bool: 重置是否成功
        """
        try:
            if self.is_initialized:
                await self.close_database()

            # 重新初始化，不使用安全模式
            await Tortoise.init(config=self.config)
            await Tortoise.generate_schemas(safe=False)

            self.is_initialized = True

            if DEBUG:
                print("✅ 数据库重置成功")

            return True

        except Exception as e:
            print(f"❌ 数据库重置失败: {e}")
            return False

    def get_database_path(self) -> str:
        """获取数据库文件路径"""
        return os.path.join(PROJECT_ROOT, DATABASE_PATH)

    def database_exists(self) -> bool:
        """检查数据库文件是否存在"""
        return os.path.exists(self.get_database_path())


# 全局数据库管理器实例
db_manager = DatabaseManager()


async def init_database(safe_schema: bool = True) -> bool:
    """
    便捷函数：初始化数据库连接

    Args:
        safe_schema: 安全模式创建表结构

    Returns:
        bool: 初始化是否成功
    """
    return await db_manager.init_database(safe_schema)


async def close_database() -> bool:
    """
    便捷函数：关闭数据库连接

    Returns:
        bool: 关闭是否成功
    """
    return await db_manager.close_database()


async def get_database_info() -> dict:
    """
    获取数据库信息

    Returns:
        dict: 数据库状态信息
    """
    from models import XianyuProduct

    info = {
        "database_path": db_manager.get_database_path(),
        "database_exists": db_manager.database_exists(),
        "is_initialized": db_manager.is_initialized,
        "record_count": 0,
    }

    if db_manager.is_initialized:
        try:
            info["record_count"] = await XianyuProduct.all().count()
        except Exception as e:
            info["error"] = str(e)

    return info


# 上下文管理器支持
class DatabaseContext:
    """数据库连接上下文管理器"""

    def __init__(self, safe_schema: bool = True):
        self.safe_schema = safe_schema

    async def __aenter__(self):
        """进入上下文时初始化数据库"""
        success = await init_database(self.safe_schema)
        if not success:
            raise RuntimeError("数据库初始化失败")
        return db_manager

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时关闭数据库连接"""
        await close_database()


def get_database_context(safe_schema: bool = True) -> DatabaseContext:
    """
    获取数据库上下文管理器

    Args:
        safe_schema: 安全模式创建表结构

    Returns:
        DatabaseContext: 数据库上下文管理器

    Usage:
        async with get_database_context() as db:
            # 数据库操作
            pass
    """
    return DatabaseContext(safe_schema)
