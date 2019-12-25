import hashlib

import redis

from bproxypool.utils import singleton


@singleton
class RedisPoolFactory(object):
    """Redis Connection Pool"""
    def __init__(self):
        self.__pools = dict()

    @staticmethod
    def __make_hash(config):
        hashstr = ','.join([f'{k}:{v}' for k, v in config.items()])
        hashcode = hashlib.md5(hashstr.encode('utf8')).hexdigest()
        return hashcode

    def get_pool(self, redis_config: dict, max_connections: int) -> redis.Redis:
        """
        针对不同的redis配置缓存不同的连接池
        :param redis_config:
        host: ip or url
        port: int
        db: int
        password: None or str
        :max_connections: int default 5
        :return: conn pool
        """
        hashcode = self.__make_hash(redis_config)
        if hashcode in self.__pools:
            return redis.Redis(connection_pool=self.__pools[hashcode])
        else:
            self.__pools[hashcode] = redis.ConnectionPool(
                host=redis_config['host'],
                port=redis_config['port'],
                db=redis_config.get('db', 0),
                password=redis_config.get('password', None),
                decode_responses=True,
                max_connections=max_connections
            )
            return redis.Redis(connection_pool=self.__pools[hashcode])


def RedisHandler(max_connections: int = 5, **redis_config) -> redis.Redis:
    """
    返回redis的连接句柄
    :param redis_config:
        host: ip or url
        port: int
        db: int
        password: None or str
        max_connections: int default 5
    :return: redis handler
    """
    return RedisPoolFactory().get_pool(redis_config, max_connections)
