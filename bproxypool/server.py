"""
RESTful 风格代理池服务
1. GET /proxy/<string:vhost> 得到一个代理
2. DELETE /proxy/<string:proxy_ip:proxy_port> 删除一个代理
3. DELETE /proxy/<string:vhost>/<string:proxy_ip:proxy_port> 针对某个vhost 将ip进行冷却
4. GET /status/<string:vhost> 得到vhost下代理池状态
5. GET /status 得到代理池总状态
"""
import sys
import traceback

from flask import Flask

from bproxypool.controller.proxy import proxy
from bproxypool.controller.status import status
from bproxypool.controller.vpool import vpool
from bproxypool.core import APIException, HTTPException
from bproxypool.utils.logger import LoggerPool

log = LoggerPool().get_logger('proxy_api', fn='api')


def create_app():
    app = Flask(__name__)
    # 用户管理模块
    app.register_blueprint(proxy, url_prefix="/proxy")
    # project管理模块
    app.register_blueprint(status, url_prefix="/status")
    # 节点管理模块
    app.register_blueprint(vpool, url_prefix="/vpool")

    @app.errorhandler(Exception)
    def framework_error(error):
        if isinstance(error, APIException):
            return error
        if isinstance(error, HTTPException):
            return APIException(error.code, error.description, -1)
        tp, msg, tb = sys.exc_info()
        e_msg = ''.join(traceback.format_exception(tp, msg, tb))
        log.error(e_msg)
        return APIException(msg=str(error))

    return app