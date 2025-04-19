from robyn import Robyn, Request
from apps.users.views.views import (
    login,
    logout,
    register_check,
    get_current_user
)

def users_view_routes(app):
    """
    用户视图 路由 
    路由层 应该专注于 处理请求 并 返回响应
    """
    
    app.add_route(route_type="POST", endpoint="/users/login", handler=login) # 登录路由
    app.add_route(route_type="GET", endpoint="/users/logout", handler=logout) # 登出路由
    app.add_route(route_type="POST", endpoint="/users/register", handler=register_check) # 注册路由
    app.add_route(route_type="GET", endpoint="/user/info", handler=get_current_user) # 通过token获取用户
