# OpenAI API 配置指南

本指南将帮助您配置 OpenAI API 密钥，以便在 xianyu_spider 项目中使用 LLM 功能。

## 📋 前提条件

- 拥有 OpenAI 账户
- 已安装项目依赖 (langchain, langchain-openai)

## 🔑 获取 OpenAI API 密钥

### 1. 注册 OpenAI 账户

1. 访问 [OpenAI 官网](https://platform.openai.com/)
2. 点击 "Sign up" 注册账户
3. 验证邮箱并完成账户设置

### 2. 获取 API 密钥

1. 登录 OpenAI 平台
2. 进入 [API Keys 页面](https://platform.openai.com/api-keys)
3. 点击 "Create new secret key"
4. 为密钥设置名称（如 "xianyu-spider-key"）
5. 复制生成的 API 密钥（以 `sk-` 开头）

⚠️ **重要提醒**：API 密钥只会显示一次，请立即复制并安全保存！

## ⚙️ 配置环境变量

### 1. 复制环境配置文件

```bash
cp env.example .env
```

### 2. 编辑 .env 文件

打开 `.env` 文件，找到 LLM 配置部分：

```env
# LLM配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
```

将 `your_openai_api_key_here` 替换为您的实际 API 密钥：

```env
# LLM配置
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
```

## 🌐 API 端点配置

### 官方 OpenAI API

```env
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 第三方 API 代理（可选）

如果您使用第三方 API 代理服务，可以修改基础 URL：

```env
# 示例：SiliconFlow API
OPENAI_BASE_URL=https://api.siliconflow.cn/v1
OPENAI_MODEL=Qwen/Qwen2.5-7B-Instruct

# 示例：其他代理服务
OPENAI_BASE_URL=https://your-proxy-service.com/v1
```

⚠️ **注意**：使用第三方 API 时，模型名称可能与 OpenAI 官方不同，请查看服务提供商的文档。

## 🎯 模型选择

### 推荐模型配置

#### OpenAI 官方模型

| 模型 | 用途 | 成本 | 性能 |
|------|------|------|------|
| `gpt-3.5-turbo` | 日常分析 | 💰 低 | ⚡ 快 |
| `gpt-4` | 复杂分析 | 💰💰💰 高 | 🎯 精确 |
| `gpt-4-turbo` | 平衡选择 | 💰💰 中 | ⚡🎯 快且精确 |

#### 第三方 API 模型（示例）

| 服务商 | 模型名称 | 特点 |
|-------|---------|------|
| SiliconFlow | `Qwen/Qwen2.5-7B-Instruct` | 中文优化 |
| SiliconFlow | `meta-llama/Meta-Llama-3.1-8B-Instruct` | 通用性能 |
| 其他服务商 | 请参考各服务商文档 | - |

### 配置示例

```env
# OpenAI 官方模型
OPENAI_MODEL=gpt-3.5-turbo        # 经济实用型
OPENAI_MODEL=gpt-4                # 高精度型
OPENAI_MODEL=gpt-4-turbo          # 平衡型

# 第三方 API 模型（示例）
OPENAI_MODEL=Qwen/Qwen2.5-7B-Instruct           # SiliconFlow 中文模型
OPENAI_MODEL=meta-llama/Meta-Llama-3.1-8B-Instruct  # SiliconFlow 通用模型
```

## 🧪 测试配置

### 1. 验证 API 连接

运行测试脚本验证配置：

```bash
python check_llm_env.py
```

### 2. 基本功能测试

```bash
python test_llm_basic.py
```

预期输出示例：
```
✅ API 连接成功
✅ 模型响应正常
✅ LLM 配置验证完成
```

## 💡 使用提示

### 成本控制

1. **选择合适的模型**：
   - 简单任务使用 `gpt-3.5-turbo`
   - 复杂分析使用 `gpt-4`

2. **优化提示词**：
   - 保持提示词简洁明确
   - 避免重复和冗余信息

3. **设置使用限制**：
   - 在 OpenAI 控制台设置月度使用限额
   - 监控 API 使用量

### 安全最佳实践

1. **保护 API 密钥**：
   - 不要将 `.env` 文件提交到版本控制
   - 定期轮换 API 密钥
   - 使用环境变量管理敏感信息

2. **访问控制**：
   - 限制 API 密钥的使用权限
   - 设置 IP 白名单（如果支持）

## 🔧 故障排除

### 常见错误及解决方案

#### 1. 401 Unauthorized

**问题**：API 密钥无效或已过期

**解决方案**：
- 检查 API 密钥格式（应以 `sk-` 开头）
- 验证密钥是否正确复制
- 确认账户状态正常

#### 2. 429 Rate Limit Exceeded

**问题**：请求频率超过限制

**解决方案**：
- 减少请求频率
- 升级 API 计划
- 实现请求重试机制

#### 3. Model Not Found (400错误)

**问题**：模型不存在或名称错误

**解决方案**：
- 检查模型名称是否正确
- 确认使用的 API 服务支持该模型
- 第三方 API 的模型名称可能与 OpenAI 不同

#### 4. Connection Error

**问题**：网络连接问题

**解决方案**：
- 检查网络连接
- 验证 `OPENAI_BASE_URL` 配置
- 考虑使用代理服务

### 调试命令

```bash
# 检查环境变量
echo $OPENAI_API_KEY
echo $OPENAI_BASE_URL
echo $OPENAI_MODEL

# 测试 API 连接（OpenAI 官方）
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# 测试第三方 API 连接（以 SiliconFlow 为例）
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.siliconflow.cn/v1/models

# 查看项目日志
tail -f logs/llm.log
```

## 📞 获取帮助

如果您在配置过程中遇到问题：

1. 查看 [OpenAI API 文档](https://platform.openai.com/docs)
2. 检查项目 [FAQ 文档](FAQ.md)
3. 提交 [GitHub Issue](https://github.com/your-repo/issues)

## 🔄 配置更新

当需要更新配置时：

1. 停止正在运行的服务
2. 修改 `.env` 文件
3. 重新启动服务
4. 运行测试验证新配置

---

**注意**：请确保遵守 OpenAI 的使用条款和政策，合理使用 API 服务。
