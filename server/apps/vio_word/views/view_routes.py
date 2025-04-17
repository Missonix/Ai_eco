from robyn import Robyn, Request
from apps.vio_word.views.views import vio_check

def vio_word_view_routes(app):
    """
    违规词检测 路由 
    路由层 应该专注于 处理请求 并 返回响应
    """
    
    app.add_route(route_type="POST", endpoint="/vio_word/check", handler=vio_check) # 违规词检测路由