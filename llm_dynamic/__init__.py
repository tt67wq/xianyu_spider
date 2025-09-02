"""
LLM动态需求分析模块

完全动态需求驱动的商品分析系统
用户说什么，LLM就分析什么，不设任何预设模板
"""

from .analyzer import DynamicLLMAnalyzer
from .database import get_products_by_keyword

__version__ = "1.0.0"
__author__ = "Xianyu Spider Team"

__all__ = ["DynamicLLMAnalyzer", "get_products_by_keyword"]
