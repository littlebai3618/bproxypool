from flask import Blueprint

from bproxypool.service.proxy import StatusService

status = Blueprint('status_bp', __name__)
status_service = StatusService()


@status.route('/', methods=['GET'])
def get_pool_status():
    """
    获取代理池当前状态
    :return: GetSuccess
    """
    return status_service.get_pool_status()