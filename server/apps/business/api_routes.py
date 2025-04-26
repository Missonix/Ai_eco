from robyn import Robyn, Request
from apps.business.api import (
    create_course_api,
    update_course_api,
    get_course_api,
    delete_course_api,
    get_all_courses_api,
    get_course_by_id_api,

    create_ai_product_api,
    update_ai_product_api,
    get_ai_product_by_id_api,
    get_all_ai_products_api,
    delete_ai_product_api,

    create_entitlement_rule_api,
    update_entitlement_rule_api,
    delete_entitlement_rule_api,
    get_all_entitlement_rules_api,
    get_entitlement_rule_by_id_api,
    get_entitlement_rules_by_filter_api,

    create_order_api,
    update_order_api,
    delete_order_api,
    get_all_orders_api,
    get_order_by_id_api,
    get_orders_by_filter_api,

    create_user_entitlement_api,
    update_user_entitlement_api,
    delete_user_entitlement_api,
    get_user_entitlement_by_id_api,
    get_all_user_entitlements,
    get_user_entitlements_by_filter_api,
    generate_user_entitlement_from_order_api,
    batch_generate_user_entitlements_api,

    delete_course_permanently_api,
    delete_ai_product_permanently_api,

    get_upload_error_orders_api,
    get_batch_generate_errors_api,

    get_course_count,
    get_ai_product_count,

    get_entitlement_rule_count,
    get_order_count,
    get_user_entitlement_count,

    search_courses_by_name_prefix_api,
    search_ai_products_by_name_prefix_api
)
from apps.business.views import upload_orders_excel

def business_api_routes(app):
    """
    业务视图 路由 
    路由层 应该专注于 处理请求 并 返回响应
    """
    
    app.add_route(route_type="POST", endpoint="/courses", handler=create_course_api) # 创建课程
    app.add_route(route_type="PATCH", endpoint="/courses/:course_id", handler=update_course_api) # 更新课程
    # app.add_route(route_type="POST", endpoint="/courses/search", handler=get_course_api) # 课程搜索
    app.add_route(route_type="DELETE", endpoint="/courses/:course_id", handler=delete_course_api) # 删除课程
    app.add_route(route_type="GET", endpoint="/courses", handler=get_all_courses_api) # 获取所有课程
    app.add_route(route_type="GET", endpoint="/courses/:course_id", handler=get_course_by_id_api) # 通过课程ID获取单个课程


    app.add_route(route_type="POST", endpoint="/ai_products", handler=create_ai_product_api) # 创建AI产品
    app.add_route(route_type="PATCH", endpoint="/ai_products/:ai_product_id", handler=update_ai_product_api) # 更新AI产品
    app.add_route(route_type="DELETE", endpoint="/ai_products/:ai_product_id", handler=delete_ai_product_api) # 删除AI产品
    app.add_route(route_type="GET", endpoint="/ai_products", handler=get_all_ai_products_api) # 获取所有AI产品
    app.add_route(route_type="GET", endpoint="/ai_products/:ai_product_id", handler=get_ai_product_by_id_api) # 通过AI产品ID获取单个AI产品


    app.add_route(route_type="POST", endpoint="/entitlement_rules", handler=create_entitlement_rule_api) # 创建权益规则
    app.add_route(route_type="PATCH", endpoint="/entitlement_rules/:rule_id", handler=update_entitlement_rule_api) # 更新权益规则
    app.add_route(route_type="DELETE", endpoint="/entitlement_rules/:rule_id", handler=delete_entitlement_rule_api) # 删除权益规则
    app.add_route(route_type="GET", endpoint="/entitlement_rules", handler=get_all_entitlement_rules_api) # 获取所有权益规则
    app.add_route(route_type="GET", endpoint="/entitlement_rules/:rule_id", handler=get_entitlement_rule_by_id_api) # 通过课程ID获取单个权益规则
    app.add_route(route_type="POST", endpoint="/entitlement_rules/search", handler=get_entitlement_rules_by_filter_api) # 通过条件查询单个权益规则


    app.add_route(route_type="POST", endpoint="/orders", handler=create_order_api) # 创建单个订单
    app.add_route(route_type="PATCH", endpoint="/orders/:order_id", handler=update_order_api) # 更新订单
    app.add_route(route_type="DELETE", endpoint="/orders/:order_id", handler=delete_order_api) # 删除订单
    app.add_route(route_type="GET", endpoint="/orders", handler=get_all_orders_api) # 获取所有订单
    app.add_route(route_type="GET", endpoint="/orders/:order_id", handler=get_order_by_id_api) # 通过订单ID获取单个订单
    app.add_route(route_type="POST", endpoint="/orders/search", handler=get_orders_by_filter_api) # 通过条件查询订单


    app.add_route(route_type="POST", endpoint="/user_entitlements", handler=create_user_entitlement_api) # 创建用户权益
    app.add_route(route_type="PATCH", endpoint="/user_entitlements/:entitlement_id", handler=update_user_entitlement_api) # 更新用户权益
    app.add_route(route_type="DELETE", endpoint="/user_entitlements/:entitlement_id", handler=delete_user_entitlement_api) # 删除用户权益
    app.add_route(route_type="GET", endpoint="/user_entitlements", handler=get_all_user_entitlements) # 获取所有用户权益
    app.add_route(route_type="GET", endpoint="/user_entitlements/:entitlement_id", handler=get_user_entitlement_by_id_api) # 通过用户权益ID获取单个用户权益
    app.add_route(route_type="POST", endpoint="/user_entitlements/search", handler=get_user_entitlements_by_filter_api) # 通过条件查询用户权益

    app.add_route(route_type="GET", endpoint="/user_entitlements/generate/:order_id", handler=generate_user_entitlement_from_order_api) # 根据订单生成用户权益
    app.add_route(route_type="GET", endpoint="/user_entitlements/batch_generate", handler=batch_generate_user_entitlements_api) # 批量根据订单生成用户权益

    app.add_route(route_type="POST", endpoint="/orders/upload", handler=upload_orders_excel) # 上传订单Excel文件

    app.add_route(route_type="DELETE", endpoint="/del_courses/:course_id", handler=delete_course_permanently_api) # 彻底删除课程
    app.add_route(route_type="DELETE", endpoint="/del_ai_products/:ai_product_id", handler=delete_ai_product_permanently_api) # 彻底删除AI产品

    app.add_route(route_type="GET", endpoint="/upload_error_orders", handler=get_upload_error_orders_api) # 获取上传错误订单
    app.add_route(route_type="GET", endpoint="/batch_generate_errors", handler=get_batch_generate_errors_api) # 获取批量生成权益错误
    
    app.add_route(route_type="GET", endpoint="/courses/count", handler=get_course_count) # 获取课程总数
    app.add_route(route_type="GET", endpoint="/ai_products/count", handler=get_ai_product_count) # 获取AI产品总数

    app.add_route(route_type="GET", endpoint="/entitlement_rules/count", handler=get_entitlement_rule_count) # 获取权益规则总数
    app.add_route(route_type="GET", endpoint="/orders/count", handler=get_order_count) # 获取订单总数
    app.add_route(route_type="GET", endpoint="/user_entitlements/count", handler=get_user_entitlement_count) # 获取用户权益总数

    app.add_route(route_type="POST", endpoint="/courses/search", handler=search_courses_by_name_prefix_api) # 根据课程名称开头搜索课程
    app.add_route(route_type="POST", endpoint="/ai_products/search", handler=search_ai_products_by_name_prefix_api) # 根据AI产品名称开头搜索AI产品