# BProxyPool - 基于Redis的代理池服务框架

<p align="center">
  <a href="https://github.com/python">
    <img src="https://img.shields.io/badge/Python-3.7+-brightgreen.svg" alt="Python">
  </a>
  <a href="https://github.com/littlebai3618/bproxypool/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/mashape/apistatus.svg" alt="license">
  </a>
</p>

## 项目简介

BProxyPool 是一个用纯Python实现的、采用RESTful风格设计的基于Redis的代理池服务框架。该框架的核心特色是引入了 `virtual_pool`（虚拟代理池）概念，能够在一个实际的代理池基础上抽象出多个逻辑上相互独立的代理池。这样的设计使得在需要处理多个抓取项目时，可以根据不同网站使用不同的代理池，从而显著提高代理的利用率。

## 核心特色

- **🎯 虚拟代理池（Virtual Pool）**: 支持在一个物理代理池上创建多个逻辑独立的代理池
- **🌐 RESTful API**: 提供标准化的REST接口，易于集成和使用
- **⚡ 高性能架构**: 采用协程和多线程架构，资源占用少，性能优异
- **🚀 简单部署**: 开箱即用，内置多个免费代理源（代理获取逻辑参考自 [proxy_pool](https://github.com/jhao104/proxy_pool) 项目）
- **🔄 自动调度**: 内置调度器自动获取和验证代理可用性
- **📊 状态监控**: 提供完整的代理池状态监控接口

## 系统要求

- **Python**: 3.7 或更高版本
- **Redis**: 用于代理数据存储和管理
- **操作系统**: Linux/macOS/Windows

## 快速开始

### 1. 安装部署

```bash
# 克隆项目
git clone https://github.com/your-repo/bproxypool.git
cd bproxypool

# 安装依赖
pip install -r requirements.txt

# 配置Redis连接
vim config/frame_settings.py

# 配置Gunicorn服务器
vim config/gunicorn.py
```

### 2. 启动服务

```bash
# 启动调度器（负责抓取和验证代理）
sh start.sh scheduler

# 启动API服务
sh start.sh service
```

### 3. 服务管理

```bash
# 重启调度器
sh restart.sh scheduler

# 停止服务
sh stop.sh
```

## API接口文档

### 代理获取接口

| 接口路径 | 方法 | 功能描述 | 参数说明 |
|---------|------|----------|----------|
| `/proxy/` | GET | 从默认代理池随机获取一个代理 | 无 |
| `/proxy/<virtual_pool>` | GET | 从指定虚拟代理池随机获取一个代理<br/>*首次访问会自动创建虚拟池* | 无 |

**返回格式示例**:
```json
{
  "code": 200,
  "data": {
    "proxy": "127.0.0.1:8080",
    "source": "ProxySource"
  }
}
```

### 代理管理接口

| 接口路径 | 方法 | 功能描述 | 参数说明 |
|---------|------|----------|----------|
| `/proxy/` | DELETE | 从代理池中删除指定代理 | `proxy`: 代理地址<br/>`source`: 代理来源 |
| `/proxy/<virtual_pool>` | DELETE | 从虚拟代理池中删除指定代理 | `proxy`: 代理地址<br/>`source`: 代理来源 |
| `/proxy/<virtual_pool>` | PATCH | 将代理设置为冷却状态 | `proxy`: 代理地址<br/>`expire`: 冷却时间（秒，默认1800） |

### 状态监控接口

| 接口路径 | 方法 | 功能描述 | 参数说明 |
|---------|------|----------|----------|
| `/status/` | GET | 获取代理池状态信息<br/>包括代理总量、构成、虚拟池信息 | 无 |
| `/vpool/<virtual_pool>/` | DELETE | 删除指定的虚拟代理池 | 无 |

## 使用示例

### 同步方式获取代理

```python
import requests

def get_proxy():
    url = 'http://localhost:5000/proxy/my_pool'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['data']
    return None

# 使用代理
proxy_info = get_proxy()
if proxy_info:
    proxy = proxy_info['proxy']
    print(f"获取到代理: {proxy}")
```

### 异步方式获取代理

```python
import aiohttp
import asyncio

async def get_proxy_async():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:5000/proxy/my_pool') as response:
            if response.status == 200:
                data = await response.json()
                return data['data']
    return None

# 使用示例
async def main():
    proxy_info = await get_proxy_async()
    if proxy_info:
        print(f"获取到代理: {proxy_info['proxy']}")

asyncio.run(main())
```

## 自定义代理源

### 1. 创建代理获取器

在 `proxy/` 目录下创建新的代理获取器文件：

```python
# proxy/custom_proxy_getter.py
from bproxypool.core import BaseProxyGetter
from bproxypool.http import Request
from proxy import log

class CustomProxySource(BaseProxyGetter):
    # 获取频率（秒）
    get_rate = 300
    
    async def get_proxy(self) -> list:
        """
        获取代理列表
        :return: 代理地址列表，格式为 ['ip:port', 'ip:port', ...]
        """
        try:
            url = 'http://your-proxy-source.com/api/proxies'
            response = await self._request(Request(url, headers=self.header))
            
            if response and response.status == 200:
                # 解析响应，返回代理列表
                proxies = self.parse_proxies(response.text)
                log.info(f'{self.__class__.__name__} 获取到 {len(proxies)} 个代理')
                return proxies
            else:
                log.warning(f'{self.__class__.__name__} 获取代理失败: {url}')
        except Exception as e:
            log.error(f'{self.__class__.__name__} 异常: {str(e)}')
        
        return []
    
    def parse_proxies(self, text):
        """解析代理响应数据"""
        # 根据实际API响应格式进行解析
        return text.strip().split('\n')
```

### 2. 重启调度器

```bash
sh restart.sh scheduler
```

## 配置说明

### Redis配置 (`config/frame_settings.py`)

```python
# Redis连接配置
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'password': None,
    'decode_responses': True
}

# 代理验证配置
PROXY_CHECK_URL = 'http://httpbin.org/ip'
PROXY_CHECK_TIMEOUT = 10
```

### Gunicorn配置 (`config/gunicorn.py`)

```python
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
timeout = 30
keepalive = 2
```

## 监控与日志

- **调度器日志**: `log/scheduler.log`
- **API服务日志**: `log/server.log`
- **状态监控**: 通过 `/status/` 接口获取实时状态

## 技术架构

```
├── bproxypool/           # 核心代码目录
│   ├── controller/       # API控制器
│   ├── core/            # 核心组件
│   ├── http/            # HTTP客户端
│   ├── service/         # 业务逻辑层
│   ├── utils/           # 工具类
│   ├── scheduler.py     # 调度器
│   └── server.py        # Web服务器
├── proxy/               # 代理获取器
├── config/              # 配置文件
├── log/                 # 日志目录
└── requirements.txt     # 依赖列表
```

## 性能优化建议

1. **Redis优化**: 根据代理数量调整Redis内存配置
2. **并发控制**: 根据服务器性能调整Gunicorn worker数量
3. **代理验证**: 合理设置代理验证频率和超时时间
4. **虚拟池管理**: 避免创建过多不必要的虚拟代理池

## 常见问题

### Q: 如何查看代理池状态？
A: 访问 `/status/` 接口可以获取完整的代理池状态信息。

### Q: 代理获取失败怎么办？
A: 检查Redis连接、代理源可用性和网络连接，查看日志获取详细错误信息。

### Q: 如何提高代理获取成功率？
A: 增加多个代理源、调整获取频率、优化代理验证逻辑。

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目！

---

**注意**: 使用代理服务时请遵守相关法律法规和网站服务条款。