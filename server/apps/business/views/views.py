@error_handler
@request_logger
# @auth_required
# @admin_required
async def get_entitlement_rule_count(request: Request) -> Response:
    """
    获取权益规则总数
    """
    from apps.business.services import get_entitlement_rule_count_service
    return await get_entitlement_rule_count_service(request)

@error_handler
@request_logger
# @auth_required
# @admin_required
async def get_order_count(request: Request) -> Response:
    """
    获取订单总数
    """
    from apps.business.services import get_order_count_service
    return await get_order_count_service(request)

@error_handler
@request_logger
# @auth_required
# @admin_required
async def get_user_entitlement_count(request: Request) -> Response:
    """
    获取用户权益总数
    """
    from apps.business.services import get_user_entitlement_count_service
    return await get_user_entitlement_count_service(request) 