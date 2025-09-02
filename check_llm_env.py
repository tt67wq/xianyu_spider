#!/usr/bin/env python3
"""
LLM动态分析模块环境检查脚本
检查Python版本、内存、Ollama安装状态和可用模型
"""

import os
import subprocess
import sys
from typing import List, Tuple

import psutil


def check_python_version() -> Tuple[bool, str]:
    """检查Python版本（要求>=3.8）"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        return (
            True,
            f"✅ Python {version.major}.{version.minor}.{version.micro}",
        )
    else:
        return (
            False,
            f"❌ Python {version.major}.{version.minor}.{version.micro} (需要 >= 3.8)",
        )


def check_memory() -> Tuple[bool, str]:
    """检查系统内存（最少4GB/建议8GB）"""
    try:
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024**3)

        if total_gb >= 8:
            return True, f"✅ 系统内存: {total_gb:.1f}GB (充足)"
        elif total_gb >= 4:
            return True, f"⚠️  系统内存: {total_gb:.1f}GB (基本满足，建议8GB)"
        else:
            return False, f"❌ 系统内存: {total_gb:.1f}GB (不足，至少需要4GB)"
    except Exception as e:
        return False, f"❌ 无法检测内存: {str(e)}"


def check_ollama_installation() -> Tuple[bool, str]:
    """验证Ollama安装"""
    try:
        result = subprocess.run(
            ["ollama", "--version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            return True, f"✅ Ollama已安装: {version}"
        else:
            return False, f"❌ Ollama命令执行失败: {result.stderr}"
    except subprocess.TimeoutExpired:
        return False, "❌ Ollama命令超时"
    except FileNotFoundError:
        return False, "❌ Ollama未安装或不在PATH中"
    except Exception as e:
        return False, f"❌ Ollama检查失败: {str(e)}"


def check_ollama_service() -> Tuple[bool, str]:
    """检查Ollama服务状态"""
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            return True, "✅ Ollama服务运行正常"
        else:
            return False, f"❌ Ollama服务异常: {result.stderr}"
    except subprocess.TimeoutExpired:
        return False, "❌ Ollama服务响应超时"
    except Exception as e:
        return False, f"❌ Ollama服务检查失败: {str(e)}"


def get_available_models() -> Tuple[bool, List[str]]:
    """获取可用模型列表"""
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            models = []
            for line in lines[1:]:  # 跳过标题行
                if line.strip():
                    model_name = line.split()[0]
                    models.append(model_name)
            return True, models
        else:
            return False, []
    except Exception:
        return False, []


def check_database_exists() -> Tuple[bool, str]:
    """检查数据库文件是否存在"""
    db_path = "database.sqlite3"
    if os.path.exists(db_path):
        size = os.path.getsize(db_path) / 1024  # KB
        return True, f"✅ 数据库文件存在: {size:.1f}KB"
    else:
        return False, "❌ 数据库文件不存在"


def check_dependencies() -> Tuple[bool, str]:
    """检查Python依赖"""
    required_packages = ["ollama", "tortoise", "models"]
    missing = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if not missing:
        return True, "✅ 所有依赖已安装"
    else:
        return False, f"❌ 缺少依赖: {', '.join(missing)}"


def suggest_models() -> List[str]:
    """推荐的模型列表"""
    return [
        "llama3.2 (3B, 轻量级推荐)",
        "qwen2.5:7b (中文优化)",
        "mistral:7b (推理能力强)",
        "stablelm2 (多用途)",
    ]


def print_installation_guide():
    """打印安装指南"""
    print("\n" + "=" * 60)
    print("🛠️  安装指南")
    print("=" * 60)

    print("\n1. 安装Ollama:")
    print("   curl -fsSL https://ollama.ai/install.sh | sh")

    print("\n2. 启动Ollama服务:")
    print("   ollama serve")

    print("\n3. 安装推荐模型:")
    for model in suggest_models():
        model_name = model.split()[0]
        print(f"   ollama pull {model_name}")

    print("\n4. 安装Python依赖:")
    print("   uv sync")

    print("\n5. 测试安装:")
    print("   python llm_cli.py '测试功能'")


def main():
    """主检查程序"""
    print("🔍 LLM动态分析模块环境检查")
    print("=" * 60)

    checks = [
        ("Python版本", check_python_version),
        ("系统内存", check_memory),
        ("Ollama安装", check_ollama_installation),
        ("Ollama服务", check_ollama_service),
        ("数据库文件", check_database_exists),
        ("Python依赖", check_dependencies),
    ]

    all_passed = True

    for name, check_func in checks:
        success, message = check_func()
        print(f"{name:12} | {message}")
        if not success:
            all_passed = False

    print("\n" + "-" * 60)

    # 检查可用模型
    print("📋 可用模型:")
    success, models = get_available_models()
    if success and models:
        for model in models:
            print(f"   ✅ {model}")
    else:
        print("   ❌ 没有可用模型")
        all_passed = False

    print("\n" + "-" * 60)

    if all_passed:
        print("🎉 环境检查通过！可以开始使用LLM动态分析功能")
        print("\n快速开始:")
        print("   python llm_cli.py '找出性价比最高的商品'")
        print("   python llm_cli.py '分析iPhone价格趋势' iPhone")
        print("   python llm_cli.py --interactive  # 交互模式")
    else:
        print("❌ 环境检查未通过，请参考安装指南")
        print_installation_guide()

    print("\n" + "=" * 60)
    print("💡 推荐模型:")
    for model in suggest_models():
        print(f"   • {model}")


if __name__ == "__main__":
    main()
