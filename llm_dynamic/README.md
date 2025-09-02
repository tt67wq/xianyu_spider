# LLM动态需求分析模块

## 🎯 设计理念

**用户说什么，LLM就分析什么** - 完全动态需求驱动的商品分析系统，无预设模板，无固定规则。

## ✨ 核心特点

- 🔄 **完全动态**: 支持任意自然语言分析需求
- 🤖 **多模型**: 支持切换不同LLM模型（llama3.2、qwen2.5等）
- 🚀 **零配置**: 15行核心代码，开箱即用
- 💬 **对话式**: 像聊天一样分析商品数据
- 📊 **自由输出**: LLM决定输出格式，无格式限制

## 🛠️ 快速开始

### 1. 环境检查
```bash
# 检查环境是否就绪
python check_llm_env.py
```

### 2. 基础使用
```bash
# 基本分析
python llm_cli.py "找出性价比最高的iPhone"

# 指定关键词
python llm_cli.py "分析这些商品的共同特点" iPhone

# 使用特定模型
python llm_cli.py "给购买建议" MacBook --model qwen2.5:7b

# 控制分析数量
python llm_cli.py "按价格排序" --keyword iPhone --limit 15
```

### 3. 交互模式
```bash
# 启动交互式对话
python llm_cli.py --interactive

# 示例对话
> 分析性价比最高的商品
> 这些iPhone哪个最值得买？
> 帮我找3000元以下的MacBook
> 退出
```

## 📝 使用示例

### 价格分析
```bash
python llm_cli.py "分析价格是否合理，给出市场建议"
```

### 性价比评估
```bash
python llm_cli.py "按性价比排序，推荐最值得买的3个"
```

### 风险识别
```bash
python llm_cli.py "这些商品有什么风险？注意哪些问题？"
```

### 购买建议
```bash
python llm_cli.py "我是学生，预算3000，给购买建议" iPhone
```

### 趋势分析
```bash
python llm_cli.py "分析价格趋势，现在是否适合入手"
```

## 🔧 环境要求

### 系统要求
- Python >= 3.8
- 内存 >= 4GB（推荐8GB）
- 磁盘空间 >= 2GB（用于模型）

### 软件依赖
```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 启动Ollama服务
ollama serve

# 安装Python依赖
uv sync
```

### 推荐模型
```bash
# 轻量级（适合低配置）
ollama pull llama3.2        # 3B参数

# 中文优化（推荐）
ollama pull qwen2.5:7b       # 7B参数，中文表现好

# 推理能力强
ollama pull mistral:7b       # 7B参数，逻辑推理强

# 多用途
ollama pull stablelm2        # 平衡性能
```

## 🏗️ 架构设计

### 核心组件
```
llm_dynamic/
├── __init__.py          # 模块入口
├── analyzer.py          # LLM分析器（15行核心代码）
├── database.py          # 数据读取接口
└── README.md           # 本文档

根目录/
├── llm_cli.py          # 命令行工具
├── check_llm_env.py    # 环境检查
└── requirements.txt    # 依赖清单
```

### 数据流程
```
用户需求 → 数据库查询 → LLM分析 → 自由输出
```

## 🎨 自定义使用

### 编程接口
```python
from llm_dynamic import DynamicLLMAnalyzer, get_products_by_keyword

# 初始化分析器
analyzer = DynamicLLMAnalyzer(model="qwen2.5:7b")

# 获取商品数据
products = await get_products_by_keyword("iPhone", limit=10)

# 执行动态分析
result = await analyzer.analyze_with_prompt(
    products, 
    "帮我找出最值得买的，并说明理由"
)

print(result)
```

### 模型切换
```python
# 运行时切换模型
analyzer.set_model("mistral:7b")

# 查看可用模型
models = analyzer.get_available_models()
print(models)
```

### 环境变量配置
```bash
# 设置默认模型
export LLM_MODEL=qwen2.5:7b

# 使用环境变量
python llm_cli.py "分析商品"
```

## 🔍 实际应用场景

### 消费决策
- "3000元预算，iPhone还是安卓？"
- "这个价格值得入手吗？"
- "现在买还是等降价？"

### 市场分析
- "分析这类商品的价格区间"
- "总结卖家的常见套路"
- "识别可能的风险点"

### 个性化推荐
- "适合学生的性价比选择"
- "商务人士推荐配置"
- "老年人易用产品筛选"

## ⚠️ 注意事项

### 模型选择建议
- **内存4GB**: 使用llama3.2（3B）
- **内存8GB**: 使用qwen2.5:7b（推荐）
- **内存16GB+**: 任意模型

### 性能优化
- 控制商品数量（--limit参数）
- 使用具体关键词缩小范围
- 选择合适的模型大小

### 常见问题
1. **Ollama连接失败**: 确保`ollama serve`已启动
2. **模型未找到**: 使用`ollama pull`安装模型
3. **分析速度慢**: 减少商品数量或换用小模型
4. **中文效果差**: 推荐使用qwen2.5系列模型

## 🚀 后续规划

- [ ] 支持图片分析（VLM模型）
- [ ] 会话历史记录
- [ ] 分析结果导出
- [ ] Web界面支持
- [ ] 多轮对话优化
- [ ] 批量分析功能

## 📧 技术支持

如有问题，请检查：
1. 环境是否满足要求（运行`check_llm_env.py`）
2. Ollama服务是否正常
3. 模型是否已下载
4. 数据库文件是否存在

---

**核心理念**: 让AI理解你的真实需求，提供个性化的商品分析。