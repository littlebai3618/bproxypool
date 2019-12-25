import os

import bproxypool
from bproxypool.utils import singleton
from bproxypool.utils.importer import import_module_by_path


@singleton
class FrameSettings(object):

    def __init__(self):
        """FrameSettings('${platform_name}.config.frame_settings')"""
        self.__settings = dict()
        # 优化错误处理
        module = import_module_by_path('frame_settings',
                                       os.path.join(bproxypool.__path__[0], '..', 'config', 'frame_settings.py'))
        for key in dir(module):
            if key.isupper():
                self.__settings[key] = getattr(module, key)

    def get(self, key, default=None):
        if default:
            return self.__settings.get(key, default)
        else:
            return self.__settings[key]

    def __getitem__(self, item):
        return self.__settings[item]