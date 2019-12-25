# 这里着重参考了 https://github.com/jhao104/proxy_pool/的代理来源和解析方法
import re
import time

from bproxypool.core.base_proxy_getter import BaseProxyGetter
from bproxypool.http import Request
from proxy import log


class Data5uFree(BaseProxyGetter):

    async def get_proxy(self) -> list:
        url_list = [
            'http://www.data5u.com/',
            # 'http://www.data5u.com/free/gngn/index.shtml',
            # 'http://www.data5u.com/free/gnpt/index.shtml'
        ]
        key = 'ABCDEFGHIZ'
        result = list()
        for url in url_list:
            resp = await self._request(Request(url, headers=self.header))
            if resp is not None and resp.status == 200:
                ul_list = resp.xpath_selector.xpath('//ul[@class="l2"]')
                for ul in ul_list:
                    try:
                        ip = ul.xpath('./span[1]/li/text()')[0]
                        classnames = ul.xpath('./span[2]/li/attribute::class')[0]
                        classname = classnames.split(' ')[1]
                        port_sum = 0
                        for c in classname:
                            port_sum *= 10
                            port_sum += key.index(c)
                        port = port_sum >> 3
                        result.append('{}:{}'.format(ip, port))
                    except Exception:
                        pass
            else:
                log.warning(f'{self.__class__.__name__} get proxy error: {url}')
        return result


class XiCiDaiLiFree(BaseProxyGetter):

    async def get_proxy(self) -> list:

        url_list = [
            'http://www.xicidaili.com/nn/',  # 高匿
            # 'http://www.xicidaili.com/nt/',  # 透明
        ]
        result = list()
        for each_url in url_list:
            for i in range(1, 2):
                resp = await self._request(Request(each_url + str(i), headers=self.header))
                if resp is not None and resp.status == 200:
                    proxy_list = resp.xpath_selector.xpath('.//table[@id="ip_list"]//tr[position()>1]')
                    for proxy in proxy_list:
                        try:
                            result.append(':'.join(proxy.xpath('./td/text()')[0:2]))
                        except Exception:
                            pass
        return result


class GuoBanJiaFree(BaseProxyGetter):

    async def get_proxy(self):
        result = list()
        resp = await self._request(Request('http://www.goubanjia.com/', headers=self.header))
        if resp is None or resp.status != 200:
            log.info(f'{self.__class__.__name__} request failed {resp}')
            return

        proxy_list = resp.xpath_selector.xpath('//td[@class="ip"]')
        xpath_str = """.//*[not(contains(@style, 'display: none'))
                                                and not(contains(@style, 'display:none'))
                                                and not(contains(@class, 'port'))
                                                ]/text()
                                        """
        for each_proxy in proxy_list:
            try:
                # :符号裸放在td下，其他放在div span p中，先分割找出ip，再找port
                ip_addr = ''.join(each_proxy.xpath(xpath_str))

                # HTML中的port是随机数，真正的端口编码在class后面的字母中。
                # 比如这个：
                # <span class="port CFACE">9054</span>
                # CFACE解码后对应的是3128。
                port = 0
                for _ in each_proxy.xpath(".//span[contains(@class, 'port')]"
                                          "/attribute::class")[0]. \
                        replace("port ", ""):
                    port *= 10
                    port += (ord(_) - ord('A'))
                port /= 8

                result.append('{}:{}'.format(ip_addr, int(port)))
            except Exception:
                pass
        return result


class KuaiDaiLIFree(BaseProxyGetter):

    async def get_proxy(self) -> list:
        result = list()
        url_list = [
            'https://www.kuaidaili.com/free/inha/',
            'https://www.kuaidaili.com/free/intr/'
        ]
        for url in url_list:
            resp = await self._request(Request(url, headers=self.header))
            if resp is None or resp.status != 200:
                log.info(f'{self.__class__.__name__} request failed {resp}')
                continue

            proxy_list = resp.xpath_selector.xpath('.//table//tr')
            time.sleep(1)  # 必须sleep 不然第二条请求不到数据
            for tr in proxy_list[1:]:
                result.append(':'.join(tr.xpath('./td/text()')[0:2]))

        return result


class IP3366Free(BaseProxyGetter):

    async def get_proxy(self) -> list:
        result = list()

        urls = ['http://www.ip3366.net/free/?stype=1',
                "http://www.ip3366.net/free/?stype=2"]
        for url in urls:
            resp = await self._request(Request(url, headers=self.header))
            if resp is None or resp.status != 200:
                log.info(f'{self.__class__.__name__} request failed {resp}')
                continue

            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', resp.text)
            for proxy in proxies:
                result.append(":".join(proxy))

        return result


class IPHaiFree(BaseProxyGetter):

    async def get_proxy(self) -> list:
        result = list()

        urls = [
            'http://www.iphai.com/free/ng',
            'http://www.iphai.com/free/np',
            'http://www.iphai.com/free/wg',
            'http://www.iphai.com/free/wp'
        ]
        for url in urls:
            resp = await self._request(Request(url, headers=self.header))
            if resp is None or resp.status != 200:
                log.info(f'{self.__class__.__name__} request failed {resp}')
                continue

            proxies = re.findall(r'<td>\s*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*?</td>[\s\S]*?<td>\s*?(\d+)\s*?</td>',
                                 resp.text)
            for proxy in proxies:
                result.append(":".join(proxy))

        return result


class JiangXianLiFree(BaseProxyGetter):

    async def get_proxy(self) -> list:
        result = list()

        for i in range(1, 2):
            url = 'http://ip.jiangxianli.com/?country=中国&?page={}'.format(i)
            resp = await self._request(Request(url, headers=self.header))
            if resp is None or resp.status != 200:
                log.info(f'{self.__class__.__name__} request failed {resp}')
                continue

            for index, tr in enumerate(resp.xpath_selector.xpath("//table//tr")):
                if index == 0:
                    continue
                result.append(":".join(tr.xpath("./td/text()")[0:2]).strip())
        return result


class QYDaiLiFree(BaseProxyGetter):

    async def get_proxy(self) -> list:
        result = list()

        base_url = 'http://www.qydaili.com/free/?action=china&page='
        for page in range(1, 2):
            url = base_url + str(page)
            resp = await self._request(Request(url, headers=self.header))
            if resp is None or resp.status != 200:
                log.info(f'{self.__class__.__name__} request failed {resp}')
                continue

            proxies = re.findall(
                r'<td.*?>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td.*?>(\d+)</td>',
                resp.text)
            for proxy in proxies:
                result.append(':'.join(proxy))
        return result


class IP89Free(BaseProxyGetter):

    async def get_proxy(self) -> list:
        result = list()

        base_url = 'http://www.89ip.cn/index_{}.html'
        for page in range(1, 2):
            url = base_url.format(page)
            resp = await self._request(Request(url, headers=self.header))
            if resp is None or resp.status != 200:
                log.info(f'{self.__class__.__name__} request failed {resp}')
                continue
            proxies = re.findall(
                r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>',
                resp.text)
            for proxy in proxies:
                result.append(':'.join(proxy))
        return result


if __name__ == '__main__':
    # print(Data5uFree().debug())
    # print(IP66Free().debug())
    # XiCiDaiLiFree().debug()
    # GuoBanJiaFree().debug()
    # KuaiDaiLIFree().debug()
    # IP3366Free().debug()
    # IPHaiFree().debug()
    # JiangXianLiFree().debug()
    # QYDaiLiFree().debug()
    pass
