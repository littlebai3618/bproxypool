# BProxyPool - 智能代理池服务框架

<p align="center">
  <a href="https://github.com/python">
    <img src="https://img.shields.io/badge/Python-3.7+-brightgreen.svg" alt="Python">
  </a>
  <a href="https://github.com/littlebai3618/bproxypool/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/mashape/apistatus.svg" alt="license">
  </a>
</p>

## 🚀 项目简介

BProxyPool 是一个基于 Python 开发的高性能代理池服务框架，采用 RESTful API 设计和 Redis 存储。本项目的核心亮点是引入了**虚拟代理池（virtual_pool）**概念，能够在单个物理代理池基础上抽象出多个逻辑独立的代理池，显著提升代理资源的利用效率。

## ✨ 核心特性

- **🔄 虚拟代理池** - 支持创建多个逻辑隔离的代理池，提高资源利用率
- **📡 RESTful API** - 标准化的接口设计，易于集成和使用
- **⚡ 高性能架构** - 基于协程和多线程，资源占用低，响应速度快
- **🎯 智能调度** - 自动化代理获取和验证机制
- **📦 开箱即用** - 内置多个免费代理源，快速部署
- **🔧 易于扩展** - 支持自定义代理源，灵活配置

## 🛠️ 技术栈

- **语言**: Python 3.7+
- **框架**: Flask + aiohttp
- **数据库**: Redis
- **调度器**: APScheduler
- **部署**: Gunicorn

## 📋 系统要求

- Python 3.7+
- Redis 服务器
- 8GB+ 内存推荐

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd bproxypool

# 安装Python依赖
pip install -r requirements.txt
```

### 2. 配置系统

```bash
# 修改框架配置
vim config/frame_settings.py

# 配置Gunicorn
vim config/gunicorn.py
```

### 3. 启动服务

```bash
# 启动调度器（负责抓取和验证代理）
sh start.sh scheduler

# 启动API服务
sh start.sh service
```

### 3. 验证服务

```bash
# 检查服务状态
curl http://localhost:8080/status/

# 获取一个代理
curl http://localhost:8080/proxy/
```

## 📚 API 接口文档

### 基础代理操作

| 接口 | 方法 | 功能描述 | 参数 |
|------|------|----------|------|
| `/proxy/` | GET | 随机获取一个代理 | 无 |
| `/proxy/` | DELETE | 删除指定代理 | proxy, source |
| `/status/` | GET | 获取代理池状态 | 无 |

### 虚拟代理池操作

| 接口 | 方法 | 功能描述 | 参数 |
|------|------|----------|------|
| `/proxy/<virtual_pool>` | GET | 从虚拟池获取代理 | 无 |
| `/proxy/<virtual_pool>` | DELETE | 从虚拟池删除代理 | proxy, source |
| `/proxy/<virtual_pool>` | PATCH | 冷却代理（暂时不可用） | proxy, expire |
| `/vpool/<virtual_pool>/` | DELETE | 删除虚拟代理池 | 无 |

### 返回数据格式

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "proxy": "127.0.0.1:8080",
    "source": "ProxySource"
  }
}
```

详细状态码说明请参考：[API状态码文档](./code.md)

## 💻 使用示例

### 同步方式获取代理

```python
import requests

def get_proxy():
    url = 'http://host:port/proxy/my_pool'
    response = requests.get(url).json()
    return response['data']

# 返回格式: {"proxy": "127.0.0.1:8080", "source": "ProxySource"}
```

### 异步方式获取代理

```python
import aiohttp
import json

async def get_proxy(timeout=10):
    timeout_config = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession() as session:
        async with session.get(
            'http://host:port/proxy/my_pool',
            timeout=timeout_config
        ) as response:
            result = json.loads(await response.text())
            return result['data']
```

## 🔧 扩展开发

### 添加自定义代理源

1. 在 `proxy/` 目录下创建新的获取器文件：

```python
# proxy/custom_proxy_getter.py
from bproxypool.core import BaseProxyGetter
from bproxypool.http import Request
from proxy import log

class CustomProxySource(BaseProxyGetter):
    # 获取频率（秒）
    get_rate = 30
    
    async def get_proxy(self) -> list:
        """
        返回代理列表，格式: ['ip:port', 'ip:port', ...]
        """
        url = 'your-proxy-source-url'
        response = await self._request(Request(url, headers=self.header))
        
        if response and response.status == 200:
            # 解析响应数据，返回代理列表
            proxies = self.parse_response(response.text)
            log.info(f'获取到 {len(proxies)} 个代理')
            return proxies
        else:
            log.warning(f'{self.__class__.__name__} 获取代理失败')
            return []
    
    def parse_response(self, text):
        # 实现你的解析逻辑
        return text.strip().split('\n')
```

2. 重启调度服务：

```bash
sh restart.sh scheduler
```

## 📂 项目结构

```
bproxypool/
├── bproxypool/          # 核心框架代码
│   ├── controller/      # API控制器
│   ├── core/           # 核心组件
│   ├── http/           # HTTP客户端
│   ├── service/        # 业务逻辑
│   └── utils/          # 工具类
├── config/             # 配置文件
├── proxy/              # 代理获取器
├── log/                # 日志目录
└── requirements.txt    # 依赖清单
```

## 🔄 运维管理

```bash
# 启动服务
sh start.sh scheduler   # 启动调度器
sh start.sh service     # 启动API服务

# 重启服务
sh restart.sh scheduler # 重启调度器
sh restart.sh service   # 重启API服务

# 停止服务
sh stop.sh              # 停止所有服务
```

## 📖 相关文档

- [API 状态码说明](./code.md)
- [配置文件详解](./config/)

## 代理管理示例

```python
import requests

def manage_proxy():
    """代理管理示例"""
    base_url = 'http://localhost:8080'
    
    # 1. 获取代理池状态
    status = requests.get(f'{base_url}/status/').json()
    print("代理池状态:", status['data'])
    
    # 2. 获取代理
    proxy_resp = requests.get(f'{base_url}/proxy/test_pool').json()
    proxy_info = proxy_resp['data']
    
    # 3. 冷却代理（暂时不使用该代理）
    cool_data = {
        'proxy': proxy_info['proxy'],
        'expire': 1800  # 冷却30分钟
    }
    requests.patch(f'{base_url}/proxy/test_pool', json=cool_data)
    
    # 4. 删除无效代理
    delete_data = {
        'proxy': proxy_info['proxy'],
        'source': proxy_info['source']
    }
    requests.delete(f'{base_url}/proxy/test_pool', json=delete_data)
```

## 🔧 配置说明

### 主配置文件 (`config/frame_settings.py`)

```python
# Redis配置
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None

# 代理验证配置
PROXY_TIMEOUT = 10
PROXY_RETRY = 3

# 调度器配置
SCHEDULER_INTERVAL = 300  # 调度间隔（秒）
```

### Web服务配置 (`config/gunicorn.py`)

```python
# 服务器配置
bind = "0.0.0.0:8080"
workers = 4
worker_class = "sync"
timeout = 30
```

## 📊 监控和日志

### 日志文件

- `log/scheduler.log` - 调度器日志
- `log/service.log` - API服务日志

### 监控指标

通过 `/status/` 接口可以获取：
- 代理总数
- 各来源代理分布
- 虚拟代理池状态
- 系统运行状态

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 开源协议

本项目采用 MIT 协议，详情请参阅 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- 免费代理源的抓取逻辑参考了 [proxy_pool](https://github.com/jhao104/proxy_pool) 项目
- 感谢所有为本项目做出贡献的开发者

## 📞 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 提交 Issue
- 发起 Pull Request
- 发送邮件至项目维护者

---

⭐ 如果这个项目对你有帮助，欢迎给个星标支持！