from robyn.robyn import Request
from apps.business.services import (create_course_service, 
                                    delete_course_service, 
                                    get_course_service, 
                                    update_course_service, 
                                    get_all_courses_service, 
                                    get_course_by_id_service, 
                                    delete_course_permanently_service,
                                    delete_ai_product_permanently_service
                                    )

"""
    定义业务API接口
    接口层 应该专注于 处理基础的数据库操作 并 返回成功的状态码及数据内容
    接口层避免直接暴露在外,应该由服务层调用
"""

# 查询
async def get_all_courses_api(request: Request):
    """
    获取所有课程 接口
    """
    return await get_all_courses_service(request)

# 通过课程ID获取单个课程
async def get_course_by_id_api(request: Request):
    """
    通过课程ID获取单个课程 接口
    """
    return await get_course_by_id_service(request)

async def get_course_api(request: Request):
    """
    通过课程ID或课程名称获取单个课程 接口
    """
    return await get_course_service(request)

async def create_course_api(request: Request):
    """
    创建课程
    """
    return await create_course_service(request) 

async def update_course_api(request: Request):
    """
    更新课程
    """
    return await update_course_service(request)

async def delete_course_api(request: Request):
    """
    删除课程
    """
    return await delete_course_service(request)

async def delete_course_permanently_api(request: Request):
    """
    彻底删除课程
    """
    return await delete_course_permanently_service(request)



from apps.business.services import (
    create_ai_product_service,  # 创建AI产品服务
    update_ai_product_service,  # 更新AI产品服务
    get_ai_product_by_id_service,  # 通过AI产品ID获取单个AI产品服务
    get_all_ai_products_service,  # 获取所有AI产品服务
    delete_ai_product_service  # 删除AI产品服务
)

# 查询
async def get_all_ai_products_api(request: Request):
    """
    获取所有AI产品 接口
    """
    return await get_all_ai_products_service(request)

# 通过课程ID获取单个课程
async def get_ai_product_by_id_api(request: Request):
    """
    通过AI产品ID获取单个AI产品 接口
    """
    return await get_ai_product_by_id_service(request)

async def create_ai_product_api(request: Request):
    """
    创建AI产品
    """
    return await create_ai_product_service(request) 

async def update_ai_product_api(request: Request):
    """
    更新AI产品
    """
    return await update_ai_product_service(request)

async def delete_ai_product_api(request: Request):
    """
    删除AI产品
    """
    return await delete_ai_product_service(request)

async def delete_ai_product_permanently_api(request: Request):
    """
    彻底删除AI产品
    """
    return await delete_ai_product_permanently_service(request)


from apps.business.services import (
    create_entitlement_rule_service,  # 创建权益规则服务
    update_entitlement_rule_service,  # 更新权益规则服务
    delete_entitlement_rule_service,  # 删除权益规则服务
    get_entitlement_rule_service,  # 获取单个权益规则服务
    get_all_entitlement_rules_service,  # 获取所有权益规则服务
    get_entitlement_rules_by_filter_service  # 通过条件获取单个权益规则服务
)

# 查询
async def get_all_entitlement_rules_api(request: Request):
    """
    获取所有权益规则 接口
    """
    return await get_all_entitlement_rules_service(request)

# 通过课程ID获取单个权益规则
async def get_entitlement_rule_by_id_api(request: Request):
    """
    通过课程ID获取单个权益规则 接口
    """
    return await get_entitlement_rule_service(request)

async def get_entitlement_rules_by_filter_api(request: Request):
    """
    通过条件查询单个权益规则 接口
    """
    return await get_entitlement_rules_by_filter_service(request)

async def create_entitlement_rule_api(request: Request):
    """
    创建权益规则
    """
    return await create_entitlement_rule_service(request) 

async def update_entitlement_rule_api(request: Request):
    """
    更新权益规则
    """
    return await update_entitlement_rule_service(request)

async def delete_entitlement_rule_api(request: Request):
    """
    删除权益规则
    """
    return await delete_entitlement_rule_service(request)


from apps.business.services import (
    create_order_service,
    update_order_service,
    delete_order_service,
    get_order_service,
    get_orders_by_filter_service,
    get_all_orders_service
)


# 创建单个订单(测试)
async def create_order_api(request: Request):
    """
    创建单个订单
    """
    return await create_order_service(request)

# 批量导入订单


# 更新订单
async def update_order_api(request: Request):
    """
    更新订单
    """
    return await update_order_service(request)


# 根据订单id查询单个订单
async def get_order_by_id_api(request: Request):
    """
    根据订单id查询单个订单
    """
    return await get_order_service(request)


# 获取所有订单
async def get_all_orders_api(request: Request):
    """
    获取所有订单
    """
    return await get_all_orders_service(request)


# 根据条件搜索订单
async def get_orders_by_filter_api(request: Request):
    """
    根据条件搜索订单
    """
    return await get_orders_by_filter_service(request)


# 删除订单
async def delete_order_api(request: Request):
    """
    删除订单
    """
    return await delete_order_service(request)


from apps.business.services import (
    create_user_entitlement_service,
    update_user_entitlement_service,
    delete_user_entitlement_service,
    get_user_entitlement_service,
    get_user_entitlements_by_filter_service,
    get_all_user_entitlements_service,
    generate_user_entitlement_from_order_service
)


async def create_user_entitlement_api(request: Request):
    """
    创建用户权益
    """
    return await create_user_entitlement_service(request)

async def update_user_entitlement_api(request: Request):
    """
    更新用户权益
    """
    return await update_user_entitlement_service(request)

async def delete_user_entitlement_api(request: Request):
    """
    删除用户权益
    """
    return await delete_user_entitlement_service(request)

async def get_user_entitlement_by_id_api(request: Request):
    """
    根据用户权益ID获取单个用户权益
    """
    return await get_user_entitlement_service(request)

async def get_all_user_entitlements(request: Request):
    """
    获取所有用户权益
    """
    return await get_all_user_entitlements_service(request)

async def get_user_entitlements_by_filter_api(request: Request):
    """
    根据条件查询用户权益
    """
    return await get_user_entitlements_by_filter_service(request)


async def generate_user_entitlement_from_order_api(request: Request):
    """
    根据订单生成用户权益
    """
    return await generate_user_entitlement_from_order_service(request)

from apps.business.services import batch_generate_user_entitlements_service

async def batch_generate_user_entitlements_api(request: Request):
    """
    批量根据订单生成用户权益
    """
    return await batch_generate_user_entitlements_service(request)

from apps.business.services import get_upload_error_orders_service

async def get_upload_error_orders_api(request: Request):
    """
    获取上传错误订单
    """
    return await get_upload_error_orders_service(request)

from apps.business.services import get_batch_generate_errors_service

async def get_batch_generate_errors_api(request: Request):
    """
    获取批量生成权益错误
    """
    return await get_batch_generate_errors_service(request)


async def get_course_count(request: Request):
    """
    获取课程总数
    """
    from apps.business.services import get_course_count_service
    return await get_course_count_service(request)


async def get_ai_product_count(request: Request):
    """
    获取AI产品总数
    """
    from apps.business.services import get_ai_product_count_service
    return await get_ai_product_count_service(request) 

async def get_entitlement_rule_count(request: Request):
    """
    获取权益规则总数
    """
    from apps.business.services import get_entitlement_rule_count_service
    return await get_entitlement_rule_count_service(request) 

async def get_order_count(request: Request):
    """
    获取订单总数
    """
    from apps.business.services import get_order_count_service
    return await get_order_count_service(request) 
    
async def get_user_entitlement_count(request: Request):
    """
    获取用户权益总数
    """
    from apps.business.services import get_user_entitlement_count_service
    return await get_user_entitlement_count_service(request) 


async def search_courses_by_name_prefix_api(request: Request):
    """
    根据课程名称开头搜索课程
    """
    from apps.business.services import search_courses_by_name_prefix_service
    return await search_courses_by_name_prefix_service(request)

async def search_ai_products_by_name_prefix_api(request: Request):
    """
    根据AI产品名称开头搜索AI产品
    """
    from apps.business.services import search_ai_products_by_name_prefix_service
    return await search_ai_products_by_name_prefix_service(request)