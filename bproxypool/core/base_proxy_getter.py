import aiohttp
from aiohttp import ClientResponse

from bproxypool.core import ProxyGetterError
from bproxypool.http import Response, Request


class BaseProxyGetter(object):

    # int 秒
    get_rate = 5 * 60

    header = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
    }

    async def get_proxy(self) -> str:
        """
        得到代理池的方法
        :return: 'proxy_ip:proxy_port'
        """
        raise ProxyGetterError('Please rebuild get_proxy() func')

    async def _request(self, req: Request):
        temp_timeout = aiohttp.ClientTimeout(total=req.timeout)
        async with aiohttp.ClientSession() as session:
            async with session.request(
                    method=req.method,
                    url=req.url,
                    headers=req.headers,
                    # post 参数，get时为 None
                    data=req.data,
                    cookies=req.cookies,
                    # 是否允许重定向
                    allow_redirects=req.allow_redirect,
                    timeout=temp_timeout,
                    proxy=None if not isinstance(req.proxy, dict) else 'http://{}'.format(req.proxy['proxy']),
                    # ssl验证
                    ssl=req.verify_ssl,
            ) as resp:
                # 挂起等待下载结果
                return await self.__assemble_response(resp, req)

    async def __assemble_response(self, response: ClientResponse, request: Request) -> Response:
        # 这里只处理 str 类型的数据
        text = await response.text(errors='ignore')
        return Response(
            url=str(response.url),
            status=response.status,
            headers=dict(response.headers),
            request=request,
            cookies={i.key: i.value for i in response.cookies.values()},
            text=text
        )

    async def check_ip(self, proxy) -> bool:

        if isinstance(proxy, bytes):
            proxy = proxy.decode("utf8")
        try:
            r = await self._request(Request(
                url='https://www.baidu.com/',
                proxy="http://{proxy}".format(proxy=proxy),
                timeout=10,
                verify_ssl=False
            ))
            if r.status == 200:
                return True
        except Exception:
            pass
        return False
