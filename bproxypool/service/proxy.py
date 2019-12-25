"""
black_list 改为 使用string实现
"""

from bproxypool.core import BaseService, Conflict, NotFound, PatchSuccess, DeleteSuccess, \
    GetSuccess
from bproxypool.utils.logger import LoggerPool

log = LoggerPool().get_logger('proxypool', fn='api')


class ProxyService(BaseService):

    def get_proxy_with_virtual_pool(self, virtual_pool: str):
        for i in range(100):
            proxy = self.redis_handler.srandmember('bproxypool')
            if proxy is None:
                log.warning(f'{virtual_pool}\'s proxy pool is empty!')
                return NotFound(msg=f'{virtual_pool}\'s proxy pool is empty!', errno=101)
            proxy, source = proxy.split(',')
            if not self.redis_handler.exists(f'{virtual_pool}:{proxy}'):
                log.info(f'{virtual_pool} success get a proxy:{proxy}')
                return GetSuccess(data={'proxy': proxy, 'source': source})
        log.error(f'can\'t get proxy by {virtual_pool}, maybe black list is too many')
        return Conflict(data=f'can\'t get proxy by {virtual_pool}, maybe black list is too many', errno=102)

    def get_proxy(self):
        proxy = self.redis_handler.srandmember('bproxypool')
        if proxy is None:
            log.warning(f'proxy pool is empty!')
            return NotFound(msg=f'proxy pool is empty!', errno=101)
        proxy, source = proxy.split(',')
        log.info(f'success get a proxy:{proxy}')
        return GetSuccess(data={'proxy': proxy, 'source': source})

    def delete_proxy(self, proxy: str, source: str, virtual_pool: str = None):
        if self.redis_handler.srem('bproxypool', f'{proxy},{source}'):
            log.info(f'success delete a proxy:{proxy} source: {source}')
            return DeleteSuccess()
        if virtual_pool:
            return Conflict(data=f'delete proxy failed', errno=103)
        else:
            return Conflict(data=f'delete proxy from {virtual_pool} failed', errno=103)

    def cool_down_proxy(self, virtual_pool: str, proxy: str, expire: int = 1800):
        self.redis_handler.expire(f'{virtual_pool}:{proxy}', expire)
        self.redis_handler.sadd('virtual_pool', virtual_pool)
        log.info(f'success cool down proxy:{proxy}')
        return PatchSuccess(msg=f'success cool down proxy:{proxy}')


class VirtualPoolService(BaseService):

    def delete_virtual_pool(self, virtual_pool: str):
        for key in self.redis_handler.keys(f'{virtual_pool}:*'):
            self.redis_handler.delete(key)

        if self.redis_handler.srem('virtual_pool', virtual_pool):
            log.info(f'success delete a virtual_pool:{virtual_pool}')
            return DeleteSuccess()
        else:
            log.error(f'virtual_pool is not exist')
            return NotFound(msg='virtual_pool is not exist', errno=201)


class StatusService(BaseService):

    def get_pool_status(self):
        all_proxy = list(self.redis_handler.smembers('bproxypool'))
        pools = {
            'total': len(all_proxy)
        }

        for ps in all_proxy:
            proxy, source = ps.split(',')
            if source in pools:
                pools[source] += 1
            else:
                pools[source] = 1


        result = {
            'virtual_pools': list(self.redis_handler.smembers('virtual_pool')),
            'pool': pools
        }
        log.info(f'success get pool status:{result}')
        return GetSuccess(data=result)
