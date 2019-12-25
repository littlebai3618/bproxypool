# 定时获取代理并存入redis
# 自动寻找 BaseProxyGetter 方法
import asyncio
import inspect
import sys
import traceback

from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.blocking import BlockingScheduler

from bproxypool.core import BaseProxyGetter
from bproxypool.utils.importer import walk_modules
from bproxypool.utils.logger import LoggerPool
from bproxypool.utils.redis_handler import RedisHandler
from bproxypool.core.config import FrameSettings

log = LoggerPool().get_logger('scheduler', fn='scheduler')


class ProxyMaker(object):
    frame_settings = FrameSettings()

    def __init__(self, scheduler: BlockingScheduler):
        self.scheduler = scheduler
        self.redis_handler = RedisHandler(**self.frame_settings['REDIS_CONFIG'])
        self.local_proxy_class = dict()
        self.find_get_proxy()
        self.scheduler.add_job(
            self.find_get_proxy, 'interval',
            seconds=5,
            id='AutoFindProxyGetter',
            name='AutoFindProxyGetter'
        )

    def find_get_proxy(self):
        for mod in walk_modules(f'proxy'):
            for obj in vars(mod).values():
                if inspect.isclass(obj):
                    if issubclass(obj, BaseProxyGetter) and obj.__name__ != 'BaseProxyGetter':
                        self.local_proxy_class[obj.__name__] = obj(), obj.get_rate
                        if self.scheduler.get_job(str(obj.get_rate)) is None:
                            self.scheduler.add_job(self.run, 'interval',
                                                   args=(obj.get_rate,),
                                                   seconds=obj.get_rate,
                                                   id=str(obj.get_rate),
                                                   name=f'CrawlProxy-{obj.get_rate}')
        log.debug(f'total func(source) = {self.local_proxy_class}')

    def run(self, this_rate):
        tasks = list()
        loop = asyncio.new_event_loop()

        for source, obj_tuple in self.local_proxy_class.items():
            obj, rate = obj_tuple
            if this_rate == rate:
                tasks.append(asyncio.ensure_future(self.run_once(source, obj), loop=loop))

        if not tasks:
            # 如果没有任务就放弃
            try:
                self.scheduler.remove_job(str(this_rate))
            except JobLookupError:
                pass
            log.info(f'{this_rate} has no task')
            return

        log.info(f'{this_rate}/s run {len(tasks)}')

        loop.run_until_complete(asyncio.wait(tasks))

    async def run_once(self, source, obj):
        cur_proxy = set()
        try:
            for proxy in await obj.get_proxy():
                if await obj.check_ip(proxy):
                    cur_proxy.add(f'{proxy},{source}')
            log.info(f'{source} get {len(cur_proxy)} proxy')
        except Exception as e:
            log.error(f'{source} get proxy error: {e}')
            tp, msg, tb = sys.exc_info()
            e_msg = ''.join(traceback.format_exception(tp, msg, tb))
            log.error(f'get proxy exec:{e_msg}')

        if len(cur_proxy):
            self.redis_handler.sadd('bproxypool', *list(cur_proxy))
        log.info(f'{source} success insert {len(cur_proxy)} proxy to proxy pool')


class ProxyChecker(BaseProxyGetter):
    frame_settings = FrameSettings()

    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.redis_handler = RedisHandler(**self.frame_settings['REDIS_CONFIG'])
        self.scheduler.add_job(
            self.run, 'interval',
            seconds=30,
            id='AutoCheckProxy',
            name=f'AutoCheckProxy'
        )

    async def check_proxy(self, proxy, source) -> (bool, str, str):
        b = await self.check_ip(proxy)
        if not b:
            self.redis_handler.srem('bproxypool', f'{proxy},{source}')
        return b, source, proxy

    def run(self):
        invalid_ip = list()
        source_count = dict()
        tasks = list()
        loop = asyncio.new_event_loop()
        for sproxy in self.redis_handler.smembers('bproxypool'):
            proxy, source = sproxy.split(',')
            tasks.append(asyncio.ensure_future(self.check_proxy(proxy, source), loop=loop))

        log.info(f'proxy check need check {len(tasks)} proxy')
        loop.run_until_complete(asyncio.wait(tasks))

        for task in tasks:
            isvalid, source, proxy = task.result()
            if not isvalid:
                invalid_ip.append(f'{source},{proxy}')
                if source in source_count:
                    source_count[source] += 1
                else:
                    source_count[source] = 1
        log.info(f'success remove {len(invalid_ip)} proxy from proxy pool')
        log.info(f'valid detail {source_count}')


def run():
    scheduler = BlockingScheduler(logger=log)
    ProxyMaker(scheduler)
    ProxyChecker(scheduler)
    log.info('scheduler start!')
    scheduler.start()


if __name__ == '__main__':
    run()
