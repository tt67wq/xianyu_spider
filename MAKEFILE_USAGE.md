# Makefile 使用指南

## 简介

这份指南详细介绍了如何使用为闲鱼爬虫项目创建的Makefile，它包含了开发、测试、部署的常用命令。

## 快速开始

### 1. 首次设置

```bash
# 复制环境变量文件
cp env.example .env

# 编辑配置文件（根据需要修改）
nano .env

# 安装开发环境依赖
make install-dev
```

### 2. 启动服务

```bash
# 开发模式（带热重载）
make dev

# 生产模式
make run
```

## 常用命令详解

### 🔧 开发命令

| 命令 | 描述 |
|------|------|
| `make install` | 仅安装生产环境依赖 |
| `make install-dev` | 安装完整的开发环境，包括测试工具、格式化工具等 |
| `make dev` | 启动开发服务器，支持热重载（修改代码自动重启） |
| `make run` | 启动生产服务器 |

### 🧪 测试命令

```bash
# 运行基础测试
make test

# 运行测试并生成覆盖率报告（htmlcov/目录）
make test-cov

# 检查代码质量
make lint
```

### 🎨 代码格式化

```bash
# 格式化代码（自动修复）
make format

# 仅检查格式（不修改）
make format-check
```

### 🗄️ 数据库管理

```bash
# 显示数据库统计信息
make db-stats

# 重置数据库（警告：会删除所有数据）
make db-reset
```

### 🐳 容器化部署

```bash
# 构建Docker镜像
make docker-build

# 运行Docker容器
make docker-run

# 停止正在运行的容器
make docker-stop
```

### 🛠️ 系统维护

```bash
# 升级所有依赖到最新版本
make deps-upgrade

# 清理缓存和临时文件
make clean

# 创建环境变量模板
make setup-env
```

## 实际使用示例

### 场景1：新项目设置

```bash
git clone <repository>
cd xianyu_spider

# 一步到位设置环境
make setup-env
# 编辑 .env 文件配置
make install-dev

# 首次测试
make health    # 确认服务能正常启动
make api-test  # 测试API接口
```

### 场景2：日常开发流程

```bash
# 每天早上更新依赖
make deps-upgrade

# 开始开发前检查
make format-check
make lint
make test

# 修复格式问题
make format

# 启动开发服务
make dev
```

### 场景3：部署到生产环境

```bash
# 清理环境
make clean

# 基础安装
make install

# 容器化部署
make docker-build
make docker-run
```

## 故障排除

### Q: 浏览器安装失败
```bash
make playwright-install
```

### Q: 环境配置问题
```bash
# 重新设置环境
make setup-env
# 检查当前环境
cat .env
```

### Q: 服务启动失败
```bash
# 查看端口是否被占用
lsof -i :8000

# 清理并重试
make clean
make setup-env
make install-dev
make dev
```

### Q: 想要测试API
```bash
# 使用内置测试命令
make api-test
# 按提示输入关键词和页数
```

## 监控和日志

### 检查服务状态
```bash
make health
```

### 查看实时日志
```
make logs
```

### 数据库统计
```bash
make db-stats
```

## 环境变量说明

编辑 `.env` 文件可以配置以下设置：

- **数据库**: 支持 SQLite/MySQL/PostgreSQL
- **服务器**: HOST 和 PORT 配置
- **爬虫**: 延迟时间、无头模式开关
- **浏览器**: 自定义 User-Agent
- **代理**: 配置代理服务器

## 最佳实践

### 开发阶段
1. 保持 `make format && make lint && make test` 流程
2. 修改代码后及时格式化
3. 使用 `make dev` 进行开发，避免直接运行脚本

### 部署阶段
1. 清理开发文件：`make clean`
2. 使用容器化部署：`make docker-build && make docker-run`
3. 定期检查安全更新：`make deps-upgrade`

### 协作规范
- 提交前运行 `make test` 确保测试通过
- 保持代码格式统一：`make format`
- 更新依赖记录到 `requirements.txt`

## 进阶命令

### 自定义配置文件
```bash
# 使用自定义端口启动
SERVER_PORT=3000 make dev

# 修改主机绑定
SERVER_HOST=localhost make dev
```

### 调试模式
```bash
# 设置调试模式
DEBUG=true make dev
```

### 代理配置示例
```bash
# 在 .env 文件中添加：
# HTTP_PROXY=http://127.0.0.1:8080
# HTTPS_PROXY=http://127.0.0.1:8080
```

## 常见问题解决方案

这个Makefile旨在简化开发流程，如果遇到问题可以运行 `make help` 查看可用命令，或参考项目README.md获取更多信息。