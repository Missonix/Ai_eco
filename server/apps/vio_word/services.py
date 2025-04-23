from robyn import Request, Response
from core.response import ApiResponse
from core.middleware import error_handler, request_logger
from core.logger import setup_logger
from core.database import AsyncSessionLocal
from apps.vio_word import crud as vio_word_crud

# 设置日志记录器
logger = setup_logger('vio_word_services')

async def get_vio_words_service(request: Request) -> Response:
    """
    获取所有违规词检测记录服务
    """
    try:
        # 获取分页参数
        try:
            page = int(request.query_params.get("page", "1"))
            page_size = int(request.query_params.get("page_size", "10"))
        except ValueError:
            page = 1
            page_size = 10
        
        # 验证分页参数
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
            
        # 获取过滤条件
        filters = {}
        if "phone" in request.query_params:
            filters["phone"] = request.query_params.get("phone")
        if "is_violation" in request.query_params:
            filters["is_violation"] = request.query_params.get("is_violation") == "true"
            
        # 获取排序条件
        order_by = {"created_at": "desc"}  # 默认按创建时间倒序排序
            
        async with AsyncSessionLocal() as db:
            try:
                vio_words, total_count = await vio_word_crud.get_vio_words_by_filters(
                    db, 
                    filters=filters,
                    order_by=order_by,
                    page=page,
                    page_size=page_size
                )
                
                # 计算总页数
                total_pages = (total_count + page_size - 1) // page_size
                
                return ApiResponse.success(
                    data={
                        "items": [word.to_dict() for word in vio_words],
                        "total": total_count,
                        "page": page,
                        "page_size": page_size,
                        "total_pages": total_pages
                    },
                    message="获取违规词检测记录成功"
                )
            except Exception as e:
                logger.error(f"查询违规词检测记录失败: {str(e)}")
                return ApiResponse.error(
                    message="获取违规词检测记录失败",
                    status_code=500
                )
    except Exception as e:
        logger.error(f"获取违规词检测记录服务异常: {str(e)}")
        return ApiResponse.error(
            message="获取违规词检测记录失败",
            status_code=500
        )

async def get_vio_word_service(request: Request) -> Response:
    """
    获取单个违规词检测记录服务
    """
    try:
        # 获取记录ID
        id = request.path_params.get("id")
        if not id:
            return ApiResponse.validation_error("记录ID不能为空")
            
        try:
            id = int(id)
        except ValueError:
            return ApiResponse.validation_error("记录ID必须是整数")
            
        async with AsyncSessionLocal() as db:
            try:
                vio_word = await vio_word_crud.get_vio_word(db, id)
                if not vio_word:
                    return ApiResponse.not_found("违规词检测记录不存在")
                    
                return ApiResponse.success(
                    data=vio_word.to_dict(),
                    message="获取违规词检测记录成功"
                )
            except Exception as e:
                logger.error(f"查询违规词检测记录失败: {str(e)}")
                return ApiResponse.error(
                    message="获取违规词检测记录失败",
                    status_code=500
                )
    except Exception as e:
        logger.error(f"获取违规词检测记录服务异常: {str(e)}")
        return ApiResponse.error(
            message="获取违规词检测记录失败",
            status_code=500
        ) 