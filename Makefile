.PHONY: help install install-dev run dev test lint format clean playwright-install db-reset docker-build docker-run

# 默认目标
.DEFAULT_GOAL := help

# 项目配置
PYTHON := python
PIP := pip
UV := uv
PROJECT_NAME := xianyu-spider
HOST := 0.0.0.0
PORT := 8000

# 颜色输出
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help:  ## 显示可用命令
	@echo "$(GREEN)闲鱼爬虫项目 - 可用命令$(NC)"
	@echo "================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install:  ## 安装生产环境依赖
	@echo "$(GREEN)开始安装生产环境依赖...$(NC)"
	$(PIP) install -r requirements.txt

install-dev:  ## 安装开发环境依赖
	@echo "$(GREEN)开始安装开发环境依赖...$(NC)"
	$(PIP) install -e ".[dev]"
	$(MAKE) playwright-install

playwright-install:  ## 安装 Playwright 浏览器
	@echo "$(GREEN)安装 Playwright 浏览器...$(NC)"
	playwright install chromium

run:  ## 运行生产服务
	@echo "$(GREEN)启动生产环境服务...$(NC)"
	$(PYTHON) spider.py

dev:  ## 运行开发服务（带热重载）
	@echo "$(GREEN)启动开发环境服务...$(NC)"
	$(PYTHON) -m uvicorn spider:app --host $(HOST) --port $(PORT) --reload

test:  ## 运行测试
	@echo "$(GREEN)运行测试...$(NC)"
	$(PYTHON) -m pytest test.py -v

test-cov:  ## 运行测试并生成覆盖率报告
	@echo "$(GREEN)运行测试并生成覆盖率报告...$(NC)"
	$(PYTHON) -m pytest test.py --cov=./ --cov-report=html --cov-report=term

lint:  ## 代码检查（flake8和pylint）
	@echo "$(GREEN)执行代码检查...$(NC)"
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:  ## 格式化代码
	@echo "$(GREEN)格式化代码...$(NC)"
	black . --line-length=88
	isort . --profile black

format-check:  ## 检查代码格式
	@echo "$(GREEN)检查代码格式...$(NC)"
	black --check . --line-length=88
	isort --check-only . --profile black

clean:  ## 清理缓存和临时文件
	@echo "$(GREEN)清理项目...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

db-reset:  ## 重置数据库
	@echo "$(YELLOW)警告：这将删除所有数据！$(NC)"
	@read -p "确定要继续吗? (y/N): " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(GREEN)重置数据库...$(NC)"; \
		rm -f data/xianyu_spider.db; \
		echo "$(GREEN)数据库已重置！$(NC)"; \
	fi

db-stats:  ## 显示数据库统计信息
	@echo "$(GREEN)数据库统计信息：$(NC)"
	@if [ -f data/xianyu_spider.db ]; then \
		echo "数据库文件大小: $$(ls -lh data/xianyu_spider.db | awk '{print $$5}')"; \
		echo "商品记录数量: $$($(PYTHON) -c "import sqlite3; conn=sqlite3.connect('data/xianyu_spider.db'); print(conn.execute('SELECT COUNT(*) FROM xianyu_products').fetchone()[0]); conn.close()")"; \
	else \
		echo "数据库文件不存在"; \
	fi

docker-build:  ## 构建Docker镜像
	@echo "$(GREEN)构建Docker镜像...$(NC)"
	docker build -t $(PROJECT_NAME):latest .

docker-run:  ## 运行Docker容器
	@echo "$(GREEN)运行Docker容器...$(NC)"
	docker run -p $(PORT):$(PORT) --env-file .env $(PROJECT_NAME):latest

docker-stop:  ## 停止Docker容器
	@echo "$(GREEN)停止Docker容器...$(NC)"
	docker stop $(PROJECT_NAME) || true
	docker rm $(PROJECT_NAME) || true

deps-upgrade:  ## 升级所有依赖
	@echo "$(GREEN)升级项目依赖...$(NC)"
	$(PIP) list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 $(PIP) install -U

logs:  ## 查看应用日志
	@echo "$(GREEN)实时查看应用日志...$(NC)"
	tail -f data/*.log 2>/dev/null || echo "$(YELLOW)日志文件不存在$(NC)"

health:  ## 检查服务健康状态
	@echo "$(GREEN)检查服务健康状态...$(NC)"
	@curl -s http://$(HOST):$(PORT)/docs > /dev/null && echo "$(GREEN)服务运行正常$(NC)" || echo "$(RED)服务未运行$(NC)"

api-test:  ## API接口测试
	@echo "$(GREEN)测试API接口...$(NC)"
	@read -p "请输入搜索关键词: " keyword; \
	read -p "请输入最大页数(默认1): " max_pages; \
	max_pages=$${max_pages:-1}; \
	curl -X POST http://$(HOST):$(PORT)/search/ \
	-H "Content-Type: application/json" \
	-d "{\"keyword\":\"$$keyword\",\"max_pages\":$$max_pages}"

setup-env:  ## 设置环境变量模板
	@echo "$(GREEN)设置环境变量模板...$(NC)"
	@if [ ! -f .env ]; then \
		cp .env.example .env 2>/dev/null || \
		cat > .env << 'EOF'; \
# 数据库配置\n\
DATABASE_PATH=data/xianyu_spider.db\n\
\n\
# 服务器配置\n\
SERVER_HOST=0.0.0.0\n\
SERVER_PORT=8000\n\
\n\
# 爬虫配置\n\
REQUEST_DELAY=1\n\
BROWSER_HEADLESS=true\n\
DEBUG=false\n\
EOF; \
	echo "$(GREEN)环境文件已创建: .env$(NC)"; \
	else \
		echo "$(YELLOW)环境文件已存在: .env$(NC)"; \
	fi
