#!/usr/bin/env python3
"""
CLI配置管理模块
提供默认配置、环境变量处理和配置验证功能
"""

import os
import sys
from typing import Any, Dict

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class CLIConfig:
    """CLI配置管理器"""

    def __init__(self):
        self.config = self._load_config()
        self._validate_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置信息"""
        return {
            # 数据库配置
            "database": {
                "path": os.getenv("DATABASE_PATH", "data/xianyu_spider.db"),
                "auto_create_dir": True,
            },
            # 爬虫配置
            "spider": {
                "request_delay": float(os.getenv("REQUEST_DELAY", "1")),
                "browser_headless": os.getenv(
                    "BROWSER_HEADLESS", "true"
                ).lower()
                == "true",
                "user_agent": os.getenv(
                    "USER_AGENT",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                ),
                "max_pages_default": 1,
                "max_pages_limit": 50,
                "timeout": 30,
            },
            # CLI界面配置
            "ui": {
                "table_max_rows_default": 10,
                "table_max_rows_limit": 100,
                "title_max_length": 40,
                "price_max_length": 12,
                "area_max_length": 15,
                "seller_max_length": 20,
            },
            # 输出配置
            "output": {
                "default_format": "table",
                "supported_formats": ["table", "json", "csv"],
                "json_indent": 2,
                "csv_encoding": "utf-8",
            },
            # 调试配置
            "debug": {
                "enabled": os.getenv("DEBUG", "false").lower() == "true",
                "verbose_default": False,
                "quiet_default": False,
            },
            # 网络配置
            "network": {
                "retry_attempts": 3,
                "retry_delay": 2,
                "connection_timeout": 10,
            },
        }

    def _validate_config(self):
        """验证配置参数"""
        errors = []

        # 验证爬虫配置
        spider_config = self.config["spider"]
        if spider_config["request_delay"] < 0:
            errors.append("REQUEST_DELAY 不能为负数")

        if spider_config["max_pages_limit"] < 1:
            errors.append("最大页数限制必须大于0")

        # 验证UI配置
        ui_config = self.config["ui"]
        if ui_config["table_max_rows_limit"] < 1:
            errors.append("表格最大行数限制必须大于0")

        # 验证网络配置
        network_config = self.config["network"]
        if network_config["retry_attempts"] < 0:
            errors.append("重试次数不能为负数")

        if errors:
            print("❌ 配置验证失败:")
            for error in errors:
                print(f"   - {error}")
            sys.exit(1)

    def get(self, key_path: str, default=None):
        """
        获取配置值

        Args:
            key_path: 配置键路径，如 'spider.request_delay'
            default: 默认值

        Returns:
            配置值
        """
        keys = key_path.split(".")
        value = self.config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return self.config["database"]

    def get_spider_config(self) -> Dict[str, Any]:
        """获取爬虫配置"""
        return self.config["spider"]

    def get_ui_config(self) -> Dict[str, Any]:
        """获取UI配置"""
        return self.config["ui"]

    def get_output_config(self) -> Dict[str, Any]:
        """获取输出配置"""
        return self.config["output"]

    def get_debug_config(self) -> Dict[str, Any]:
        """获取调试配置"""
        return self.config["debug"]

    def get_network_config(self) -> Dict[str, Any]:
        """获取网络配置"""
        return self.config["network"]

    def is_debug_enabled(self) -> bool:
        """检查是否启用调试模式"""
        return self.config["debug"]["enabled"]

    def validate_pages(self, pages: int) -> int:
        """验证页数参数"""
        spider_config = self.get_spider_config()
        max_limit = spider_config["max_pages_limit"]

        if pages < 1:
            raise ValueError("页数必须大于0")

        if pages > max_limit:
            print(f"⚠️  页数 {pages} 超过限制 {max_limit}，将使用限制值")
            return max_limit

        return pages

    def validate_table_limit(self, limit: int) -> int:
        """验证表格行数限制"""
        ui_config = self.get_ui_config()
        max_limit = ui_config["table_max_rows_limit"]

        if limit < 1:
            raise ValueError("表格行数限制必须大于0")

        if limit > max_limit:
            print(f"⚠️  表格行数 {limit} 超过限制 {max_limit}，将使用限制值")
            return max_limit

        return limit

    def validate_output_format(self, format_name: str) -> str:
        """验证输出格式"""
        output_config = self.get_output_config()
        supported = output_config["supported_formats"]

        if format_name not in supported:
            raise ValueError(
                f"不支持的输出格式: {format_name}，支持的格式: {', '.join(supported)}"
            )

        return format_name

    def print_config_summary(self):
        """打印配置摘要"""
        print("⚙️  当前配置:")
        print(f"   数据库路径: {self.get('database.path')}")
        print(f"   请求延迟: {self.get('spider.request_delay')}秒")
        print(
            f"   浏览器模式: {'无头' if self.get('spider.browser_headless') else '有头'}"
        )
        print(f"   默认页数: {self.get('spider.max_pages_default')}")
        print(f"   调试模式: {'开启' if self.is_debug_enabled() else '关闭'}")
        print(f"   默认输出格式: {self.get('output.default_format')}")


class CLIError(Exception):
    """CLI程序基础异常类"""

    def __init__(self, message: str, exit_code: int = 1):
        self.message = message
        self.exit_code = exit_code
        super().__init__(self.message)


class ConfigError(CLIError):
    """配置错误"""

    pass


class DatabaseError(CLIError):
    """数据库错误"""

    pass


class SpiderError(CLIError):
    """爬虫错误"""

    pass


class OutputError(CLIError):
    """输出错误"""

    pass


def handle_cli_error(error: Exception, debug: bool = False):
    """
    统一的CLI错误处理函数

    Args:
        error: 异常对象
        debug: 是否显示调试信息
    """
    if isinstance(error, CLIError):
        print(f"❌ {error.message}")
        if debug:
            import traceback

            traceback.print_exc()
        return error.exit_code

    elif isinstance(error, KeyboardInterrupt):
        print("\n\n⚠️  操作被用户中断")
        return 130  # 标准的键盘中断退出码

    elif isinstance(error, FileNotFoundError):
        print(f"❌ 文件未找到: {error}")
        if debug:
            import traceback

            traceback.print_exc()
        return 2

    elif isinstance(error, PermissionError):
        print(f"❌ 权限错误: {error}")
        if debug:
            import traceback

            traceback.print_exc()
        return 3

    else:
        print(f"❌ 未知错误: {error}")
        if debug:
            import traceback

            traceback.print_exc()
        return 1


# 全局配置实例
cli_config = CLIConfig()


def get_config() -> CLIConfig:
    """获取全局配置实例"""
    return cli_config


# 便捷函数
def get_database_path() -> str:
    """获取数据库路径"""
    return cli_config.get("database.path")


def get_request_delay() -> float:
    """获取请求延迟"""
    return cli_config.get("spider.request_delay")


def is_headless() -> bool:
    """检查是否使用无头浏览器"""
    return cli_config.get("spider.browser_headless")


def get_user_agent() -> str:
    """获取用户代理字符串"""
    return cli_config.get("spider.user_agent")


def is_debug() -> bool:
    """检查是否启用调试模式"""
    return cli_config.is_debug_enabled()
