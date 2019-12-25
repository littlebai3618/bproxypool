# @Time    : 2019/7/11 3:41 PM
# @Author  : 白尚林
# @File    : __init__.py
# @Use     :
from .log_handler import LoggerPool


# ginicorn logger fix
try:
    from gunicorn.glogging import Logger
except:
    pass


class GLogger(Logger):

    log_from_work = f'[%(asctime)s %(filename)s:%(lineno)s] %(levelname)s: %(message)s'

    error_fmt = log_from_work
    datefmt = r"%Y-%m-%d %H:%M:%S.%f"
    access_fmt = log_from_work
    syslog_fmt = "[%(process)d] %(message)s"
