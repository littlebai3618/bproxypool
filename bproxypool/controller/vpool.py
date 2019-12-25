from flask import Blueprint

from bproxypool.service.proxy import VirtualPoolService

vpool = Blueprint('virtual_pool_bp', __name__)
vpool_service = VirtualPoolService()


@vpool.route('/<string:virtual_pool>', methods=['DELETE'])
def delete_virtual_pool(virtual_pool):
    """
    从虚拟pool中
    :return: DeleteSuccess
    """
    return vpool_service.delete_virtual_pool(virtual_pool)