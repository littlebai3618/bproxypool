from bproxypool.utils.redis_handler import RedisHandler
from .config import FrameSettings


class BaseService(object):
    frame_settings = FrameSettings()

    def __init__(self):
        self.redis_handler = RedisHandler(**self.frame_settings['REDIS_CONFIG'])
