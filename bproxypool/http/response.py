"""
这里着重参考了scrapy 的response 对象
Response 对象要求实现domps 和 loads 方法来完成 obj <-> 消息之间的转换
"""
import copy
import json

from lxml import etree

from bproxypool.http import Request
from bproxypool.http.base_http import BaseHttp


class Response(BaseHttp):
    """
    自建response类型,仿照scrapy的response
    暂时只是存放一些属性
    """
    def __init__(self,
                 url,
                 status,
                 request,
                 headers=None,
                 cookies=None,
                 text=None):
        self.url = self._set_url(url)
        self.headers = self._set_headers(headers)
        self.status = status
        self.text = self._set_text(text)
        self.cookies = self._set_cookies(cookies)
        self.request = self.__set_request(request)
        self.meta = self.request.meta
        self.method = self.request.method

    def __set_request(self, request):
        if isinstance(request, dict):
            return Request.loads(request)
        elif isinstance(request, Request):
            return request
        else:
            raise TypeError("%s request must be dict or Request object. " % (type(self).__name__))


    def dumps(self):
        """解决序列化的嵌套问题"""
        resp = copy.copy(self.__dict__)
        if isinstance(resp['request'], Request):
            resp['request'] = resp['request'].dumps()
        return resp

    @classmethod
    def loads(cls, param: dict):
        return cls(**param)

    def json(self):
        return json.loads(self.text)

    @property
    def xpath_selector(self):
        """:return a xpath selector obj"""
        return etree.HTML(self.text)

    def __str__(self):
        return "<Response:%s %s %s>" % (self.method, self.status, self.url)

    __repr__ = __str__
