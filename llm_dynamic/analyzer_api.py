"""
基于 LangChain 的 LLM API 分析器实现
替代原有的 ollama 本地调用，使用 OpenAI API 进行商品分析
"""

import asyncio
import os
import sys
from typing import Dict, List, Optional

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_config import get_config


class DynamicLLMAnalyzerAPI:
    """基于 LangChain 的动态 LLM 分析器 - API 版本"""

    def __init__(self, model: Optional[str] = None):
        """
        初始化分析器，支持模型配置

        Args:
            model: 模型名称，默认从环境变量获取
        """
        # 获取配置
        config = get_config()
        llm_config = config.get_llm_config()

        self.model = model or llm_config["model"]
        self.api_key = llm_config["api_key"]
        self.base_url = llm_config["base_url"]
        self.timeout = llm_config["timeout"]
        self.max_retries = llm_config["max_retries"]
        self.temperature = llm_config["temperature"]
        self.max_tokens = llm_config["max_tokens"]

        # 验证必要的环境变量
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY 环境变量未设置。请在 .env 文件中配置您的 OpenAI API 密钥。"
            )

        # 初始化 LangChain ChatOpenAI 客户端
        try:
            self.client = ChatOpenAI(
                model=self.model,
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
                max_retries=self.max_retries,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        except Exception as e:
            raise ConnectionError(f"初始化 OpenAI 客户端失败: {str(e)}")

    async def analyze_with_prompt(
        self, products: List[Dict], prompt: str
    ) -> str:
        """
        核心函数：用户说啥，LLM做啥
        完全动态分析，无预设模板

        Args:
            products: 商品数据列表
            prompt: 用户分析需求

        Returns:
            str: LLM 分析结果
        """
        try:
            # 构建完整的分析请求
            analysis_content = f"""商品数据：{products}

用户需求：{prompt}

请根据用户需求自由分析这些商品，输出格式不限。请提供有价值的洞察和建议。"""

            # 创建消息
            message = HumanMessage(content=analysis_content)

            # 调用 LLM 进行分析（异步调用）
            response = await asyncio.to_thread(self.client.invoke, [message])

            return response.content

        except Exception as e:
            # 详细的错误处理
            error_msg = f"LLM 分析过程中出现错误：{str(e)}\n"

            if "api_key" in str(e).lower():
                error_msg += "请检查 OPENAI_API_KEY 是否正确配置。"
            elif "rate_limit" in str(e).lower():
                error_msg += "API 请求频率超限，请稍后重试。"
            elif "model" in str(e).lower():
                error_msg += (
                    f"模型 '{self.model}' 不可用，请检查模型名称或权限。"
                )
            elif "timeout" in str(e).lower():
                error_msg += "请求超时，请检查网络连接或尝试减少数据量。"
            else:
                error_msg += "请检查网络连接和 API 配置。"

            return error_msg

    def set_model(self, model_name: str):
        """
        动态切换模型

        Args:
            model_name: 新的模型名称
        """
        try:
            self.model = model_name
            # 重新初始化客户端
            self.client = ChatOpenAI(
                model=self.model,
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
                max_retries=self.max_retries,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        except Exception as e:
            raise ValueError(f"切换模型失败: {str(e)}")

    async def test_connection(self) -> Dict[str, any]:
        """
        测试 API 连接状态

        Returns:
            Dict: 连接测试结果
        """
        try:
            # 发送简单的测试请求
            test_message = HumanMessage(
                content="Hello, this is a connection test."
            )

            response = await asyncio.to_thread(
                self.client.invoke, [test_message]
            )

            return {
                "status": "success",
                "message": "API 连接正常",
                "model": self.model,
                "response_preview": response.content[:50] + "...",
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"API 连接失败: {str(e)}",
                "model": self.model,
                "suggestions": [
                    "检查 OPENAI_API_KEY 是否正确",
                    "验证网络连接状态",
                    "确认模型名称是否正确",
                    "检查 API 余额和权限",
                ],
            }

    def get_config_info(self) -> Dict[str, str]:
        """
        获取当前配置信息

        Returns:
            Dict: 配置信息
        """
        return {
            "model": self.model,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "api_key_configured": "是" if self.api_key else "否",
            "api_key_preview": f"{self.api_key[:10]}..."
            if self.api_key
            else "未配置",
        }
