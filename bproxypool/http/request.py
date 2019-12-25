from .base_http import BaseHttp


class Request(BaseHttp):

    def __init__(self,
                 url,
                 method='GET',
                 headers=None,
                 data=None,
                 cookies=None,
                 meta=None,
                 priority: int = 3,
                 proxy=None,
                 allow_redirect: bool = False,
                 timeout: int = 10,
                 verify_ssl: bool = False):
        """
        :param url: 需要请求的链接
        :param method: 请求的方法
        :param callback: Extractor的回调方法
        :param headers: 请求头
        :param data: HTTP请求的body参数
        :param cookies: 需要携带的cookie
        :param meta: 元数据，不跟随request发送到服务端
        :param priority: request的优先级
        :param proxy: {'proxy': http:xxx, 'source': xxxxxx}
        :param allow_redirect: 是否重定向
        :param timeout: 超时时间
        :param verify_ssl: 是否校验证书
        :param errback: 解析异常时的回调函数
        :param sign: request唯一标识，用于下载状态回溯
        """
        self.url = self._set_url(url)
        self.headers = self._set_headers(headers)
        self.cookies = self._set_cookies(cookies)
        self.method = self._set_method(method)
        self.data = self._set_data(data)
        self.meta = self._set_meta(meta)
        self.priority = priority
        self.proxy = proxy  # 下载是否需要使用代理
        self.allow_redirect = allow_redirect  # 下载是否需要重定向
        self.timeout = timeout
        self.verify_ssl = verify_ssl

    @classmethod
    def loads(cls, param: dict):
        return cls(**param)

    def dumps(self):
        return self.__dict__

    def __str__(self):
        return "<Request:%s %s %s>" % (self.method, self.url, self.sign)

    __repr__ = __str__
