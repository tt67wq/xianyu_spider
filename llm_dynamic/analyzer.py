"""
LLM动态分析器核心实现
支持完全动态的需求分析，用户说什么就分析什么
"""

import os
from typing import Dict, List, Optional

import ollama


class DynamicLLMAnalyzer:
    """动态LLM分析器 - 核心15行实现"""

    def __init__(self, model: Optional[str] = None):
        """初始化分析器，支持模型配置"""
        self.model = model or os.getenv("LLM_MODEL", "qwen3:0.6b")
        self.client = ollama.Client()

    async def analyze_with_prompt(
        self, products: List[Dict], prompt: str
    ) -> str:
        """
        核心函数：用户说啥，LLM做啥
        完全动态分析，无预设模板
        """
        # 构建完整上下文，让LLM自由理解

        try:
            # 调用LLM进行分析
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": f"商品数据：{products}\n\n用户需求：{prompt}\n\n请根据用户需求自由分析这些商品，输出格式不限。",
                    }
                ],
            )

            return response["message"]["content"]  # LLM完全自由输出

        except Exception as e:
            return f"分析过程中出现错误：{str(e)}\n请检查Ollama服务是否正常运行，或尝试更换模型。"

    def set_model(self, model_name: str):
        """动态切换模型"""
        self.model = model_name

    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        try:
            models = self.client.list()
            return [model["name"] for model in models["models"]]
        except:
            return ["无法获取模型列表，请检查Ollama服务"]
