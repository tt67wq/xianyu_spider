# 闲鱼商品搜索API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)

基于 FastAPI 构建的闲鱼商品搜索接口，支持异步并发请求和自动化数据去重存储。

## 功能特性

- 🔍 关键词商品搜索（支持分页）
- ⚡ 异步高性能爬取（Playwright 无头浏览器）
- 🛡️ 智能数据去重（基于链接特征哈希值）
- 💾 数据持久化存储（关系数据库）
- 📊 返回新增记录统计信息

## 技术栈

| 组件           | 用途                     |
|----------------|--------------------------|
| FastAPI        | RESTful API框架          |
| Playwright     | 浏览器自动化爬取         |
| Tortoise ORM   | 异步数据库ORM            |
| SQLite         | 轻量级数据库存储         |
| aiosqlite      | 异步SQLite驱动           |
| Uvicorn        | ASGI服务器               |

## 快速开始

### 环境配置

1. 安装依赖
```bash
pip install -r requirements.txt
playwright install chromium
```

2. 环境变量配置
复制 `.env.example` 为 `.env` 并根据需要修改配置：
```bash
cp .env.example .env
```

主要环境变量说明：
```env
# 数据库配置
DATABASE_PATH=data/xianyu_spider.db

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# 爬虫配置
REQUEST_DELAY=1
BROWSER_HEADLESS=true
DEBUG=false
```

**SQLite数据库优势**：
- ✅ 无需额外安装数据库服务
- ✅ 零配置，开箱即用
- ✅ 文件存储，易于备份和迁移
- ✅ 适合单机部署和小团队开发

### 启动服务
```bash
python spider.py
```

数据库文件将自动创建在 `data/xianyu_spider.db`，首次运行会自动生成表结构。

## API 文档

访问 `http://localhost:8000/docs` 查看交互式文档

### 搜索接口
```
POST /search/
```

**请求参数示例**：
```json
{
  "keyword": "手机",
  "max_pages": 1
}
```

**响应示例**：
```json
{
  "status": "success",
  "keyword": "手机",
  "total_results": 30,
  "new_records": 5,
  "new_record_ids": [101,102,103,104,105]
}
```

## 使用示例
建议使用 Apifox 或者 Postman 进行测试

### cURL 请求
```bash
curl -X POST "http://localhost:8000/search/" \
-H "Content-Type: application/json" \
-d '{"keyword": "笔记本电脑", "max_pages": 2}'
```

### Python 客户端
```python
import requests

response = requests.post(
    "http://localhost:8000/search/",
    json={"keyword": "数码相机", "max_pages": 3}
)
print(response.json())
```

## 数据库管理

### SQLite特性
- **文件位置**: `data/xianyu_spider.db`
- **自动创建**: 首次运行自动生成
- **备份方式**: 直接复制db文件即可
- **查看数据**: 可使用SQLite Browser等工具

### 数据清理
```bash
# 删除数据库重新开始
rm data/xianyu_spider.db
```

### 性能监控
```bash
# 检查数据库大小
ls -lh data/xianyu_spider.db

# 统计记录数量
sqlite3 data/xianyu_spider.db "SELECT COUNT(*) FROM xianyu_products;"
```

## 注意事项

1. **法律合规**  
使用前请确保遵守《网络安全法》和闲鱼平台 Robots 协议，本代码仅用于学习研究

2. **反爬机制**  
建议配置代理 IP 池和随机请求间隔，默认配置可能触发反爬限制

3. **性能调优**  
- SQLite单进程写入，适合中小规模数据
- 大量并发写入建议考虑PostgreSQL或MySQL
- 定期清理历史数据避免文件过大

4. **数据安全**  
- 定期备份 `data` 目录
- `.env` 文件已加入 `.gitignore`，避免提交敏感配置
- 生产环境建议设置文件权限限制

## 版权声明

本项目采用 [MIT License](LICENSE)，请合理使用并注明出处。数据抓取结果不得用于商业用途。