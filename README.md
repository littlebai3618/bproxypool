# BProxyPool - 基于Redis的代理池服务框架

<p align="center">
  <a href="https://github.com/python">
    <img src="https://img.shields.io/badge/Python-3.7+-brightgreen.svg" alt="Python">
  </a>
  <a href="https://github.com/littlebai3618/bproxypool/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/mashape/apistatus.svg" alt="license">
  </a>
</p>

## 📖 项目简介

BProxyPool 是一个纯Python实现的、RESTful风格的基于Redis的代理池服务框架。区别于传统代理池服务，本框架引入了**虚拟代理池(virtual_pool)**的创新概念，在一个实际的代理池基础上抽象出逻辑上相互独立的多个代理池。这种设计在多项目抓取场景下，可以根据不同网站分配不同的代理池，显著提高代理资源的利用率。

## ✨ 核心特色

- 🎯 **虚拟代理池** - 支持在单一物理代理池上创建多个逻辑独立的虚拟代理池
- 🌐 **RESTful API** - 规范的REST风格接口设计，易于集成和使用
- ⚡ **高性能架构** - 采用协程+线程架构，资源占用少，并发性能强
- 🚀 **部署简单** - 自带免费代理源，开箱即用
- 🔧 **易于扩展** - 支持自定义代理源，满足特殊需求

## 🏗️ 系统架构

```
bproxypool/
├── controller/          # 控制器层，处理HTTP请求
├── core/               # 核心模块，基础类和配置
├── http/               # HTTP客户端封装
├── service/            # 业务逻辑层
├── utils/              # 工具模块
├── scheduler.py        # 调度器，负责代理获取和验证
└── server.py          # Web服务器
```

## 📋 前置依赖

- **Python**: 3.7+
- **Redis**: 任意版本
- **系统**: Linux/macOS/Windows

## 🚀 快速开始

### 1. 安装部署

```bash
# 克隆项目
git clone <repository-url>
cd bproxypool

# 安装依赖
pip install -r requirements.txt

# 配置修改
vim config/frame_settings.py    # 修改配置文件
vim config/gunicorn.py          # 修改gunicorn配置
```

### 2. 启动服务

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

## 📚 API文档

### 基础接口

| 接口路径 | 请求方法 | 功能描述 | 参数说明 |
|---------|---------|----------|----------|
| `/proxy/` | GET | 随机获取一个代理 | 无 |
| `/proxy/` | DELETE | 从代理池中删除指定代理 | proxy: 代理地址, source: 代理来源 |
| `/status/` | GET | 查看代理池状态信息 | 无 |

### 虚拟代理池接口

| 接口路径 | 请求方法 | 功能描述 | 参数说明 |
|---------|---------|----------|----------|
| `/proxy/<virtual_pool>` | GET | 从虚拟代理池获取代理 | 首次访问会自动创建虚拟池 |
| `/proxy/<virtual_pool>` | DELETE | 从虚拟代理池删除代理 | proxy: 代理地址, source: 代理来源 |
| `/proxy/<virtual_pool>` | PATCH | 冷却虚拟池中的代理 | proxy: 代理地址, expire: 冷却时间(秒) |
| `/vpool/<virtual_pool>/` | DELETE | 删除整个虚拟代理池 | 无 |

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

## 🔧 自定义代理源

### 1. 创建代理源文件

```bash
# 进入代理源目录
cd proxy

# 创建新的代理源文件
vim custom_proxy_getter.py
```

### 2. 实现代理源类

```python
from bproxypool.core import BaseProxyGetter
from bproxypool.http import Request
from proxy import log

class CustomProxySource(BaseProxyGetter):
    """自定义代理源示例"""
    
    # 获取频率：每20秒获取一次
    get_rate = 20
    
    async def get_proxy(self) -> list:
        """
        获取代理列表
        :return: 代理列表，格式为 ['127.0.0.1:8080', '192.168.1.1:3128']
        """
        url = 'https://your-proxy-source.com/api'
        
        try:
            resp = await self._request(Request(url, headers=self.header))
            log.info(f'获取代理响应: {resp.status}')
            
            if resp and resp.status == 200:
                # 解析响应数据，返回代理列表
                return self._parse_proxies(resp.text)
            else:
                log.warning(f'获取代理失败: {url}, 状态码: {resp.status}')
                
        except Exception as e:
            log.error(f'获取代理异常: {e}')
            
        return []
    
    def _parse_proxies(self, text: str) -> list:
        """解析代理数据"""
        # 根据实际API响应格式进行解析
        return text.strip().split('\n')
```

### 3. 重启调度器

```bash
# 重启调度器以加载新的代理源
sh restart.sh scheduler
```

## 💻 使用示例

### 同步调用

```python
import requests

def get_proxy(virtual_pool='default'):
    """获取代理"""
    url = f'http://localhost:8080/proxy/{virtual_pool}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data['data']
    return None

# 使用示例
proxy_info = get_proxy('crawl_pool_1')
if proxy_info:
    proxy = proxy_info['proxy']
    print(f"获取到代理: {proxy}")
```

### 异步调用

```python
import aiohttp
import asyncio

async def get_proxy_async(virtual_pool='default', timeout=10):
    """异步获取代理"""
    url = f'http://localhost:8080/proxy/{virtual_pool}'
    
    timeout_config = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(timeout=timeout_config) as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['data']
        except asyncio.TimeoutError:
            print("请求超时")
        except Exception as e:
            print(f"请求异常: {e}")
    
    return None

# 使用示例
async def main():
    proxy_info = await get_proxy_async('crawl_pool_2')
    if proxy_info:
        proxy = proxy_info['proxy']
        print(f"获取到代理: {proxy}")

# 运行
asyncio.run(main())
```

### 代理管理

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
5. 打开 Pull Request

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

本项目中的免费代理获取逻辑参考了 [proxy_pool](https://github.com/jhao104/proxy_pool) 项目，感谢 [@jhao104](https://github.com/jhao104) 的贡献。

## 📞 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 提交 Issue
- 发起 Pull Request
- 发送邮件至项目维护者

---

⭐ 如果这个项目对你有帮助，欢迎给个星标支持！