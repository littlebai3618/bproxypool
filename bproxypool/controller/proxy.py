"""
1. GET /proxy/<string:vhost> 得到一个代理
2. DELETE /proxy/<string:proxy_ip:proxy_port> 删除一个代理
3. DELETE /proxy/<string:vhost>/<string:proxy_ip:proxy_port> 针对某个vhost 将ip进行冷却
"""
from flask import Blueprint

from bproxypool.controller.form import DeleteProxyForm, CoolDownProxyForm
from bproxypool.service.proxy import ProxyService

proxy = Blueprint('proxy_bp', __name__)
proxy_service = ProxyService()


@proxy.route('/<string:virtual_pool>', methods=['GET'])
def get_proxy_with_virtual_pool(virtual_pool):
    """
    根据virtual_pool 获取一个代理
    :param virtual_pool: vhost名称 baidu.com
    :return GetSuccess
    """
    return proxy_service.get_proxy_with_virtual_pool(virtual_pool)


@proxy.route('/', methods=['GET'])
def get_proxy():
    """
    从代理池中返回一个代理
    :return GetSuccess
    """
    return proxy_service.get_proxy()


@proxy.route('/', methods=['DELETE'])
def delete_proxy():
    """
    从代理池中删除一个代理
    :return DeleteSuccess
    """
    return proxy_service.delete_proxy(**DeleteProxyForm().to_dict())

@proxy.route('/<string:virtual_pool>', methods=['DELETE'])
def delete_proxy_with_virtual_pool(virtual_pool):
    """
    从代理池中删除一个代理
    :return DeleteSuccess
    """
    return proxy_service.delete_proxy(virtual_pool=virtual_pool, **DeleteProxyForm().to_dict())


@proxy.route('/<string:virtual_pool>', methods=['PATCH'])
def cool_down_proxy(virtual_pool):
    """
    将virtual_pool 中的一个代理进行冷却
    :param virtual_pool: vhost名称 baidu.com
    :return
    """
    return proxy_service.cool_down_proxy(virtual_pool, **CoolDownProxyForm().to_dict())
