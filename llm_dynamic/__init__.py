"""
LLM动态需求分析模块

完全动态需求驱动的商品分析系统
用户说什么，LLM就分析什么，不设任何预设模板
"""

try:
    from .analyzer import DynamicLLMAnalyzer
except ImportError:
    # ollama依赖不可用时跳过本地分析器
    DynamicLLMAnalyzer = None

from .analyzer_api import DynamicLLMAnalyzerAPI
from .database import get_products_by_keyword

__version__ = "1.0.0"
__author__ = "Xianyu Spider Team"

# 动态构建导出列表，排除不可用的组件
__all__ = [
    "DynamicLLMAnalyzerAPI",
    "get_products_by_keyword",
]

if DynamicLLMAnalyzer is not None:
    __all__.append("DynamicLLMAnalyzer")
