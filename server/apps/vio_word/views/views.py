from robyn import Request, Response
from core.response import ApiResponse
from apps.vio_word.core import vio_word_check
from core.middleware import error_handler, request_logger, auth_required, admin_required, rate_limit, auth_userinfo
from core.logger import setup_logger
import json
from apps.users.crud import get_user, update_user
from core.database import AsyncSessionLocal
# 设置日志记录器
logger = setup_logger('vio_word_views')

@error_handler
@request_logger
@rate_limit(max_requests=5, time_window=60)  # 每分钟最多5次请求
async def vio_check(request: Request) -> Response:
    """传入话术，返回违规词检测结果"""
    request = request.json()
    input = request.get("input")

    usr_id = request.get("user_id")
    async with AsyncSessionLocal() as db:
        user_obj = await get_user(db, usr_id)
        usage_count = user_obj.usage_count 
        if usage_count == 0:
            return Response(
                status_code=403,
                headers={"Content-Type": "application/json"},
                description=json.dumps({"code": 403, "message": "使用次数不足"})
            )

    result = await vio_word_check(input)  # 正确等待异步函数的结果
    if result == False:
        response_data = {
            "code": 500,
            "message": "fail",
            "data": {
                "result": "检测失败"
            }
        }
        return Response(
            status_code=500,
            headers={"Content-Type": "application/json"},
            description=json.dumps(response_data)
        )
    
    usage_count -= 1
    async with AsyncSessionLocal() as db:
        await update_user(db, usr_id, {"usage_count": usage_count})


    # 构建标准响应格式
    response_data = {
        "code": 200,
        "message": "success",
        "data": {
            "result": result,
            "usage_count": usage_count
        }
    }
    
    return Response(
        status_code=200,
        headers={"Content-Type": "application/json"},
        description=json.dumps(response_data)
    )








