<p align="center">
    BProxyPool
</p>
<p align="center">
  <a href="https://github.com/python">
    <img src="https://img.shields.io/badge/Python-3.7.4-brightgreen.svg" alt="Python">
  </a>
  <a href="https://github.com/littlebai3618/bproxypool/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/mashape/apistatus.svg" alt="license">
  </a>
</p>

简介
========

BProxyPool 是一个纯python实现、RESTful风格的基于Redis的代理池服务框架，有别于传统的代理池服务本框架引入了`virtual_pool`的概念，
在一个实际的代理池上抽象出逻辑上相互独立的代理池。这样在抓取项目过多的时候可以根据抓取不同的网站使用不同的代理池来提高代理池中代理的利用率

特色
========
* virtual_pool 可以抽象出多个逻辑代理池
* RESTful风格接口，规范
* 采用协程、线程的架构资源占用少
* 部署简单，自带一些免费代理`这些免费代理的抽取逻辑是从项目`[proxy_pool](https://github.com/jhao104/proxy_pool)[@jhao104](https://github.com/jhao104)`中收集整理得来`

前置依赖
============
* Python 3.7+
* redis

安装
=======

快速安装:

    # 克隆项目到安装目录
    cd bproxypool
    pip install -r requirements.txt
    vim config/frame_settings.py 修改配置文件
    vim config/gunicorn.py 修改gunicorn的配置
    sh start.sh scheduler # 启动调度器抓取代理
    sh start.sh service # 启动API服务


## 文档
* Api [返回状态码](./code.md)

| uri | method | Desc | arg|
| ----| ---- | ---- | ----|
| /proxy/ | GET | 随机得到一个IP | None |
| /proxy/ | DELETE | 从代理池中真正删除一个IP | proxy: 代理，source: 获取代理时返回的source|
| /proxy/\<string:virtual_pool> | GET | 从虚拟代理池中随机得到一个IP`第一次出现的virtual_pool会自动创建一个新的虚拟代理池` |None|
| /proxy/\<string:virtual_pool> | DELETE | 从代理池中真正删除一个IP |proxy: 代理，source: 获取代理时返回的source|
| /proxy/\<string:virtual_pool> | PATCH | 将一个虚拟代理池中的代理进行冷却(一段时间不会获取此代理)  |proxy: 代理 expire: 单位秒 冷却时间默认1800秒|
| /status/ | GET | 返回代理池的状态->代理总量、代理构成、虚拟代理池 | None |
| /vpool/\<string:virtual_pool>/ | DELETE | 删除一个虚拟代理池 | None |
* 新增代理源
```shell script
cd proxy # 进入bproxypool项目此目录
vim ${source_name}_getter.py # 新建一个xxxx_getter.py的文件
```
- demo
```python
from bproxypool.core import BaseProxyGetter
from bproxypool.http import Request
from proxy import log

# 类名会作为api中的 source 参数返回
class DemoProxySource(BaseProxyGetter):
    # 多久从代理源中获取一次代理 单位s
    get_rate = 20
    
    # 这里使用异步操作提速
    async def get_proxy(self) -> list:
        """
        :return 返回一个内容为 127.0.0.1:80 的数组
            demo: ['127.0.0.1:80', '127.0.0.1:8080']
        这里可以不去重，框架会去重
        """
        url = ''
        resp = await self._request(Request(url, headers=self.header))
        # log会输出到 log/scheduler.log中
        log.info(f'{resp.status} {resp.text}')
        if resp is not None and resp.status == 200:
            return resp.text.strip().split('\n')
        else:
            log.warning(f'{self.__class__.__name__} get proxy error: {url}')
        # 如果没有获取到，返回一个空数组即可
        return list()
```
```shell script
# 进入项目根目录
sh restart.sh scheduler # 重启调度模块
```

===============

## 使用示例 `接口调用结果以实际调取接口返回为准`
```python
# 获取一个代理 sync
import requests
def get_proxy():
    url='http://host:port/proxy/<virtual_pool>',
    # url='http://host:port/proxy/ # 不使用vpool
    resp = requests.get(url).json()
    # 返回下载结果 {"proxy": "127.0.0.1:80", "source": "BProxyPool"}
    return resp['data']
```
```python
# 获取一个代理 async
import aiohttp
import json
async def get_proxy(timeout) -> dict:
    temp_timeout = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession() as session:
        async with session.request(
                method='GET',
                url='http://host:port/proxy/<virtual_pool>',
                # url='http://host:port/proxy/ # 不使用vpool
                timeout=temp_timeout
        ) as resp:
            # 返回下载结果 {"proxy": "127.0.0.1:80", "source": "BProxyPool"}
            return json.loads(await resp.text())['data']
```


