def singleton(cls):
    """
    单例类
    :param cls:
    :param args:
    :param kw:
    :return:
    """
    instances = {}
    def _singleton(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return _singleton