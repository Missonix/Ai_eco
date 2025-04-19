import json
import re
import random
from datetime import datetime, timedelta
from robyn import Headers, Request, Response, jsonify, status_codes
from apps.users.models import User
from apps.business.models import Courses, Entitlement_rules, Orders, User_entitlements
from apps.users import crud as user_crud
from apps.business import crud as business_crud
from core.auth import TokenService, verify_password, get_password_hash, get_token_from_request
from sqlalchemy.ext.asyncio import AsyncSession
from apps.users.queries import get_user_by_phone
from core.database import AsyncSessionLocal
from core.response import ApiResponse
from core.logger import setup_logger
from core.cache import Cache
from apps.users.utils import generate_user_id
from apps.business.utils import (
    generate_course_id,
    generate_ai_product_id,
    generate_rule_id,
    generate_order_id,
    generate_entitlement_id
)

# 设置日志记录器
logger = setup_logger('business_services')

"""
    crud -> services -> api
    服务层:根据业务逻辑整合crud数据操作 封装业务方法 可以由上层函数直接调用
    服务层 应该完成 业务逻辑（如判断数据是否存在、响应失败的处理逻辑）
"""

async def create_course_service(request):
    """
    创建课程服务
    """
    try:
        course_data = request.json()
        course_name = course_data.get("course_name")
        
        if not course_name:
            return ApiResponse.validation_error("课程名称不能为空")
            
        async with AsyncSessionLocal() as db:
            # 检查课程名是否已存在
            existing_course = await business_crud.get_course_by_filter(db, {"course_name": course_name})
            if existing_course:
                return ApiResponse.error(
                    message="课程名称已存在",
                    status_code=status_codes.HTTP_409_CONFLICT
                )
            
            # 生成课程ID
            course_data["course_id"] = generate_course_id()
            course_data["is_deleted"] = False
            
            try:
                new_course = await business_crud.create_course(db, course_data)
                return ApiResponse.success(
                    data=new_course.to_dict(),
                    message="课程创建成功"
                )
            except Exception as e:
                logger.error(f"创建课程失败: {str(e)}")
                return ApiResponse.error(
                    message="创建课程失败",
                    status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
    except Exception as e:
        logger.error(f"创建课程服务异常: {str(e)}")
        return ApiResponse.error(
            message="创建课程失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def update_course_service(request):
    """
    更新课程服务
    """
    try:
        course_id = request.path_params.get("course_id")
        request_data = request.json()
        
        if not course_id:
            return ApiResponse.validation_error("课程ID不能为空")
            
        if not request_data:
            return ApiResponse.validation_error("请求数据不能为空")
            
        async with AsyncSessionLocal() as db:
            # 检查课程是否存在
            course = await business_crud.get_course(db, course_id)
            if not course:
                return ApiResponse.not_found("课程不存在")
            
            # 如果更新课程名称，检查新名称是否已存在
            if "course_name" in request_data:
                existing_course = await business_crud.get_course_by_filter(
                    db, 
                    {"course_name": request_data["course_name"]}
                )
                if existing_course and existing_course.course_id != course_id:
                    return ApiResponse.error(
                        message="课程名称已存在",
                        status_code=status_codes.HTTP_409_CONFLICT
                    )
            
            try:
                updated_course = await business_crud.update_course(db, course_id, request_data)
                return ApiResponse.success(
                    data=updated_course.to_dict(),
                    message="课程更新成功"
                )
            except Exception as e:
                logger.error(f"更新课程失败: {str(e)}")
                return ApiResponse.error(
                    message="更新课程失败",
                    status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
    except Exception as e:
        logger.error(f"更新课程服务异常: {str(e)}")
        return ApiResponse.error(
            message="更新课程失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_course_service(request):
    """
    通过课程ID或课程名称获取单个课程
    """
    try:
        request_data = request.json()
        course_id = request_data.get("course_id")
        course_name = request_data.get("course_name")
        
        if not course_id and not course_name:
            return ApiResponse.validation_error("请提供课程ID或课程名称")
            
        async with AsyncSessionLocal() as db:
            if course_id:
                course = await business_crud.get_course(db, course_id)
            else:
                course = await business_crud.get_course_by_filter(db, {"course_name": course_name})
                
            if not course:
                return ApiResponse.not_found("课程不存在")
                
            return ApiResponse.success(
                data=course.to_dict(),
                message="获取课程成功"
            )
            
    except Exception as e:
        logger.error(f"获取课程服务异常: {str(e)}")
        return ApiResponse.error(
            message="获取课程失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_course_by_id_service(request):
    """
    通过课程ID获取单个课程
    """
    try:
        course_id = request.path_params.get("course_id")
        if not course_id:
            return ApiResponse.validation_error("课程ID不能为空")
            
        async with AsyncSessionLocal() as db:
            course = await business_crud.get_course(db, course_id)
            if not course:
                return ApiResponse.not_found("课程不存在")
                
            return ApiResponse.success(
                data=course.to_dict(),
                message="获取课程成功"
            )
    except Exception as e:
        logger.error(f"通过课程ID获取单个课程服务异常: {str(e)}")
        return ApiResponse.error(
            message="获取课程失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )
            

async def get_all_courses_service(request):
    """
    获取所有课程服务
    """
    try:
        async with AsyncSessionLocal() as db:
            # 添加过滤条件，只获取未删除的课程
            filters = {"is_deleted": False}
            result = await business_crud.get_courses_by_filters(db, filters)
            courses = result
            return ApiResponse.success(
                data=[course.to_dict() for course in courses],
                message="获取所有课程成功"
            )
    except Exception as e:
        logger.error(f"获取所有课程服务异常: {str(e)}")
        return ApiResponse.error(
            message="获取所有课程失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def delete_course_service(request):
    """
    删除课程服务
    """
    try:
        course_id = request.path_params.get("course_id")
        
        if not course_id:
            return ApiResponse.validation_error("课程ID不能为空")
            
        async with AsyncSessionLocal() as db:
            # 检查课程是否存在
            course = await business_crud.get_course(db, course_id)
            if not course:
                return ApiResponse.not_found("课程不存在")
            
            try:
                # 软删除，更新is_deleted字段
                await business_crud.update_course(db, course_id, {"is_deleted": True})
                return ApiResponse.success(message="课程删除成功")
            except Exception as e:
                logger.error(f"删除课程失败: {str(e)}")
                return ApiResponse.error(
                    message="删除课程失败",
                    status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
    except Exception as e:
        logger.error(f"删除课程服务异常: {str(e)}")
        return ApiResponse.error(
            message="删除课程失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )


async def create_ai_product_service(request):
    """
    创建AI产品服务
    """
    try:
        ai_product_data = request.json()
        ai_product_name = ai_product_data.get("ai_product_name")
        
        if not ai_product_name:
            return ApiResponse.validation_error("AI产品名称不能为空")
            
        async with AsyncSessionLocal() as db:
            # 检查AI产品名是否已存在
            existing_ai_product = await business_crud.get_ai_product_by_filter(db, {"ai_product_name": ai_product_name})
            if existing_ai_product:
                return ApiResponse.error(
                    message="AI产品名称已存在",
                    status_code=status_codes.HTTP_409_CONFLICT
                )

            # 生成AI产品ID
            ai_product_data["ai_product_id"] = generate_ai_product_id()
            ai_product_data["is_deleted"] = False
            
            try:
                new_ai_product = await business_crud.create_ai_product(db, ai_product_data)
                return ApiResponse.success(
                    data=new_ai_product.to_dict(),
                    message="AI产品创建成功"
                )
            except Exception as e:
                logger.error(f"创建AI产品失败: {str(e)}")
                return ApiResponse.error(
                    message="创建AI产品失败",
                    status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
                )

    except Exception as e:
        logger.error(f"创建AI产品服务异常: {str(e)}")
        return ApiResponse.error(
            message="创建AI产品失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def update_ai_product_service(request):
    """
    更新AI产品服务
    """
    try:
        ai_product_id = request.path_params.get("ai_product_id")
        request_data = request.json()
        
        if not ai_product_id:
            return ApiResponse.validation_error("AI产品ID不能为空")
            
        if not request_data:
            return ApiResponse.validation_error("请求数据不能为空")
            
        async with AsyncSessionLocal() as db:
            # 检查课程是否存在
            ai_product = await business_crud.get_ai_product(db, ai_product_id)
            if not ai_product:
                return ApiResponse.not_found("AI产品不存在")
            
            # 如果更新课程名称，检查新名称是否已存在
            if "ai_product_name" in request_data:
                existing_ai_product = await business_crud.get_ai_product_by_filter(
                    db, 
                    {"ai_product_name": request_data["ai_product_name"]}
                )
                if existing_ai_product and existing_ai_product.ai_product_id != ai_product_id:
                    return ApiResponse.error(
                        message="AI产品名称已存在",
                        status_code=status_codes.HTTP_409_CONFLICT
                    )
            
            try:
                updated_ai_product = await business_crud.update_ai_product(db, ai_product_id, request_data)
                return ApiResponse.success(
                    data=updated_ai_product.to_dict(),
                    message="AI产品更新成功"
                )
            except Exception as e:
                logger.error(f"更新AI产品失败: {str(e)}")
                return ApiResponse.error(
                    message="更新AI产品失败",
                    status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
                )

    except Exception as e:
        logger.error(f"更新AI产品服务异常: {str(e)}")
        return ApiResponse.error(
            message="更新AI产品失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_ai_product_service(request):
    """
    通过AI产品ID或AI产品名称获取单个AI产品
    """
    try:
        request_data = request.json()
        ai_product_id = request_data.get("ai_product_id")
        ai_product_name = request_data.get("ai_product_name")
        
        if not ai_product_id and not ai_product_name:
            return ApiResponse.validation_error("请提供AI产品ID或AI产品名称")
            
        async with AsyncSessionLocal() as db:
            if ai_product_id:
                ai_product = await business_crud.get_ai_product(db, ai_product_id)
            else:
                ai_product = await business_crud.get_ai_product_by_filter(db, {"ai_product_name": ai_product_name})
                
            if not ai_product:
                return ApiResponse.not_found("AI产品不存在")
                
            return ApiResponse.success(
                data=ai_product.to_dict(),
                message="获取AI产品成功"
            )

    except Exception as e:
        logger.error(f"获取课程服务异常: {str(e)}")
        return ApiResponse.error(
            message="获取AI产品失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_ai_product_by_id_service(request):
    """
    通过AI产品ID获取单个AI产品
    """
    try:
        ai_product_id = request.path_params.get("ai_product_id")
        if not ai_product_id:
            return ApiResponse.validation_error("AI产品ID不能为空")
            
        async with AsyncSessionLocal() as db:
            ai_product = await business_crud.get_ai_product(db, ai_product_id)
            if not ai_product:
                return ApiResponse.not_found("AI产品不存在")
                
            return ApiResponse.success(
                data=ai_product.to_dict(),
                message="获取AI产品成功"
            )
    except Exception as e:
        logger.error(f"通过AI产品ID获取单个AI产品服务异常: {str(e)}")
        return ApiResponse.error(
            message="获取AI产品失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )
            

async def get_all_ai_products_service(request):
    """
    获取所有AI产品服务
    """
    try:
        async with AsyncSessionLocal() as db:
            # 添加过滤条件，只获取未删除的课程
            filters = {"is_deleted": False}
            result = await business_crud.get_ai_products_by_filters(db, filters)
            ai_products = result
            return ApiResponse.success(
                data=[ai_product.to_dict() for ai_product in ai_products],
                message="获取所有AI产品成功"
            )
    except Exception as e:
        logger.error(f"获取所有AI产品服务异常: {str(e)}")
        return ApiResponse.error(
            message="获取所有AI产品失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def delete_ai_product_service(request):
    """
    删除AI产品服务
    """
    try:
        ai_product_id = request.path_params.get("ai_product_id")
        
        if not ai_product_id:
            return ApiResponse.validation_error("AI产品ID不能为空")
            
        async with AsyncSessionLocal() as db:
            # 检查课程是否存在
            ai_product = await business_crud.get_ai_product(db, ai_product_id)
            if not ai_product:
                return ApiResponse.not_found("AI产品不存在")
            
            try:
                # 软删除，更新is_deleted字段
                await business_crud.update_ai_product(db, ai_product_id, {"is_deleted": True})
                return ApiResponse.success(message="AI产品删除成功")
            except Exception as e:
                logger.error(f"删除AI产品失败: {str(e)}")
                return ApiResponse.error(
                    message="删除AI产品失败",
                    status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
    except Exception as e:
        logger.error(f"删除AI产品服务异常: {str(e)}")
        return ApiResponse.error(
            message="删除AI产品失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )




async def create_entitlement_rule_service(request):
    """
    创建权益规则服务
    """
    try:
        request_data = request.json()
        course_id = request_data.get("course_id")
        ai_product_id = request_data.get("ai_product_id")
        
        if not all([course_id, ai_product_id]):
            return ApiResponse.validation_error("课程ID和AI产品ID不能为空")
            
        async with AsyncSessionLocal() as db:
            # 检查课程是否存在
            course = await business_crud.get_course(db, course_id)
            if not course:
                return ApiResponse.not_found("课程不存在")
            
            # 检查AI产品是否存在
            ai_product = await business_crud.get_ai_product(db, ai_product_id)
            if not ai_product:
                return ApiResponse.not_found("AI产品不存在")
            
            # 检查课程和AI产品的组合是否已存在
            filters = {"course_id": course_id, "ai_product_id": ai_product_id}
            existing_rule = await business_crud.get_entitlement_rule_by_filter(db, filters)
            if existing_rule:
                return ApiResponse.error(
                    message="该课程和AI产品的组合已存在",
                    status_code=status_codes.HTTP_409_CONFLICT
                )
            
            # 设置默认值
            if "daily_limit" not in request_data:
                request_data["daily_limit"] = 5
            if "validity_days" not in request_data:
                request_data["validity_days"] = 30
            
            # 生成权益规则ID
            request_data["rule_id"] = generate_rule_id()
            request_data["is_deleted"] = False
            
            try:
                new_rule = await business_crud.create_entitlement_rule(db, request_data)
                return ApiResponse.success(
                    data=new_rule.to_dict(),
                    message="权益规则创建成功"
                )
            except Exception as e:
                logger.error(f"创建权益规则失败: {str(e)}")
                return ApiResponse.error(
                    message="创建权益规则失败",
                    status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
    except Exception as e:
        logger.error(f"创建权益规则服务异常: {str(e)}")
        return ApiResponse.error(
            message="创建权益规则失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def update_entitlement_rule_service(request):
    """
    更新权益规则服务
    """
    try:
        rule_id = request.path_params.get("rule_id")
        request_data = request.json()
        
        if not rule_id:
            return ApiResponse.validation_error("权益规则ID不能为空")
            
        async with AsyncSessionLocal() as db:
            # 检查权益规则是否存在
            rule = await business_crud.get_entitlement_rule(db, rule_id)
            if not rule:
                return ApiResponse.not_found("权益规则不存在")
            
            try:
                updated_rule = await business_crud.update_entitlement_rule(db, rule_id, request_data)
                return ApiResponse.success(
                    data=updated_rule.to_dict(),
                    message="权益规则更新成功"
                )
            except Exception as e:
                logger.error(f"更新权益规则失败: {str(e)}")
                return ApiResponse.error(
                    message="更新权益规则失败",
                    status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
    except Exception as e:
        logger.error(f"更新权益规则服务异常: {str(e)}")
        return ApiResponse.error(
            message="更新权益规则失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_entitlement_rule_service(request):
    """
    获取单个权益规则服务
    """
    try:
        rule_id = request.path_params.get("rule_id")
        
        if not rule_id:
            return ApiResponse.validation_error("权益规则ID不能为空")
            
        async with AsyncSessionLocal() as db:
            rule = await business_crud.get_entitlement_rule(db, rule_id)
            if not rule:
                return ApiResponse.not_found("权益规则不存在")
            
            return ApiResponse.success(
                data=rule.to_dict(),
                message="获取权益规则成功"
            )
            
    except Exception as e:
        logger.error(f"获取权益规则服务异常: {str(e)}")
        return ApiResponse.error(
            message="获取权益规则失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_all_entitlement_rules_service(request):
    """
    获取所有权益规则服务
    """
    try:
        async with AsyncSessionLocal() as db:
            # 添加过滤条件，只获取未删除的权益规则
            filters = {"is_deleted": False}
            rules = await business_crud.get_entitlement_rules_by_filters(db, filters)
            return ApiResponse.success(
                data=[rule.to_dict() for rule in rules],
                message="获取所有权益规则成功"
            )
    except Exception as e:
        logger.error(f"获取所有权益规则服务异常: {str(e)}")
        return ApiResponse.error(
            message="获取所有权益规则失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_entitlement_rules_by_filter_service(request):
    """
    根据条件查询权益规则服务
    """
    try:
        request_data = request.json()
        filters = {}
        
        # 构建过滤条件
        if "course_id" in request_data:
            filters["course_id"] = request_data["course_id"]
        if "ai_product_id" in request_data:
            filters["ai_product_id"] = request_data["ai_product_id"]
        if "daily_limit" in request_data:
            filters["daily_limit"] = request_data["daily_limit"]
        if "validity_days" in request_data:
            filters["validity_days"] = request_data["validity_days"]
            
        # 添加未删除的过滤条件
        filters["is_deleted"] = False
            
        async with AsyncSessionLocal() as db:
            rules = await business_crud.get_entitlement_rules_by_filters(db, filters)
            return ApiResponse.success(
                data=[rule.to_dict() for rule in rules],
                message="获取权益规则成功"
            )
            
    except Exception as e:
        logger.error(f"查询权益规则服务异常: {str(e)}")
        return ApiResponse.error(
            message="查询权益规则失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def delete_entitlement_rule_service(request):
    """
    删除权益规则服务
    """
    try:
        rule_id = request.path_params.get("rule_id")
        
        if not rule_id:
            return ApiResponse.validation_error("权益规则ID不能为空")
            
        async with AsyncSessionLocal() as db:
            # 检查权益规则是否存在
            rule = await business_crud.get_entitlement_rule(db, rule_id)
            if not rule:
                return ApiResponse.not_found("权益规则不存在")
            
            try:
                # 软删除，更新is_deleted字段
                await business_crud.update_entitlement_rule(db, rule_id, {"is_deleted": True})
                return ApiResponse.success(message="权益规则删除成功")
            except Exception as e:
                logger.error(f"删除权益规则失败: {str(e)}")
                return ApiResponse.error(
                    message="删除权益规则失败",
                    status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
    except Exception as e:
        logger.error(f"删除权益规则服务异常: {str(e)}")
        return ApiResponse.error(
            message="删除权益规则失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )
    




async def create_order_service(request):
    """
    创建订单服务
    """
    try:
        order_data = request.json()
        order_id = order_data.get("order_id")
        phone = order_data.get("phone")
        course_name = order_data.get("course_name")
        purchase_time = order_data.get("purchase_time")
        is_refund = order_data.get("is_refund")
        
        if not all([order_id, phone, course_name, purchase_time, is_refund]):
            return ApiResponse.validation_error("订单号、手机号、课程名称、购买时间、是否退款不能为空")
            
        # 转换is_refund为布尔值
        is_refund_bool = True if is_refund == "已退款" else False
        
        # 转换purchase_time为datetime对象
        try:
            purchase_time_dt = datetime.strptime(purchase_time, "%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            logger.error(f"购买时间格式错误: {str(e)}")
            return ApiResponse.validation_error("购买时间格式错误，应为'YYYY-MM-DD HH:MM:SS'格式")
            
        async with AsyncSessionLocal() as db:
            # 根据课程名称获取课程ID
            course = await business_crud.get_course_by_filter(db, {"course_name": course_name})
            if not course:
                return ApiResponse.not_found("课程不存在")
            
            # 检查订单号是否已存在
            existing_order = await business_crud.get_order(db, order_id)
            if existing_order:
                return ApiResponse.error(
                    message="订单号已存在",
                    status_code=status_codes.HTTP_409_CONFLICT
                )
            
            # 准备订单数据
            order_data = {
                "order_id": order_id,
                "phone": phone,
                "course_id": course.course_id,
                "purchase_time": purchase_time_dt,
                "is_refund": is_refund_bool,
                "is_deleted": False
            }
            
            try:
                new_order = await business_crud.create_order(db, order_data)
                return ApiResponse.success(
                    data=new_order.to_dict(),
                    message="订单创建成功"
                )
            except Exception as e:
                logger.error(f"创建订单失败: {str(e)}")
                return ApiResponse.error(
                    message="创建订单失败",
                    status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
    except Exception as e:
        logger.error(f"创建订单服务异常: {str(e)}")
        return ApiResponse.error(
            message="创建订单失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def delete_order_service(request):
    """
    删除订单服务
    """
    try:
        order_id = request.path_params.get("order_id")
        
        if not order_id:
            return ApiResponse.validation_error("订单ID不能为空")
            
        async with AsyncSessionLocal() as db:
            # 检查订单是否存在
            order = await business_crud.get_order(db, order_id)
            if not order:
                return ApiResponse.not_found("订单不存在")
            
            try:
                # 软删除，更新is_deleted字段
                await business_crud.update_order(db, order_id, {"is_deleted": True})
                return ApiResponse.success(message="订单删除成功")
            except Exception as e:
                logger.error(f"删除订单失败: {str(e)}")
                return ApiResponse.error(
                    message="删除订单失败",
                    status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
    except Exception as e:
        logger.error(f"删除订单服务异常: {str(e)}")
        return ApiResponse.error(
            message="删除订单失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def update_order_service(request):
    """
    更新订单服务
    """
    try:
        order_id = request.path_params.get("order_id")
        request_data = request.json()
        
        if not order_id:
            return ApiResponse.validation_error("订单ID不能为空")
            
        if not request_data:
            return ApiResponse.validation_error("请求数据不能为空")
            
        # 只允许更新特定字段
        allowed_fields = ["phone", "course_name", "purchase_time", "is_refund"]
        update_data = {k: v for k, v in request_data.items() if k in allowed_fields}
        
        if not update_data:
            return ApiResponse.validation_error("没有有效的更新字段")
            
        # 处理is_refund字段
        if "is_refund" in update_data:
            is_refund = update_data["is_refund"]
            if is_refund in ["已退款", "无"]:
                update_data["is_refund"] = True if is_refund == "已退款" else False
            else:
                return ApiResponse.validation_error("is_refund字段值必须为'已退款'或'无'")
        
        # 处理purchase_time字段
        if "purchase_time" in update_data:
            try:
                purchase_time = update_data["purchase_time"]
                purchase_time_dt = datetime.strptime(purchase_time, "%Y-%m-%d %H:%M:%S")
                update_data["purchase_time"] = purchase_time_dt
            except ValueError as e:
                logger.error(f"购买时间格式错误: {str(e)}")
                return ApiResponse.validation_error("购买时间格式错误，应为'YYYY-MM-DD HH:MM:SS'格式")
            
        async with AsyncSessionLocal() as db:
            # 检查订单是否存在
            order = await business_crud.get_order(db, order_id)
            if not order:
                return ApiResponse.not_found("订单不存在")
            
            # 如果更新课程名称，检查新课程是否存在并获取课程ID
            if "course_name" in update_data:
                course = await business_crud.get_course_by_filter(db, {"course_name": update_data["course_name"]})
                if not course:
                    return ApiResponse.not_found("课程不存在")
                # 替换course_name为course_id
                update_data["course_id"] = course.course_id
                del update_data["course_name"]
            
            try:
                updated_order = await business_crud.update_order(db, order_id, update_data)
                return ApiResponse.success(
                    data=updated_order.to_dict(),
                    message="订单更新成功"
                )
            except Exception as e:
                logger.error(f"更新订单失败: {str(e)}")
                return ApiResponse.error(
                    message="更新订单失败",
                    status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
    except Exception as e:
        logger.error(f"更新订单服务异常: {str(e)}")
        return ApiResponse.error(
            message="更新订单失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_order_service(request):
    """
    获取单个订单服务
    """
    try:
        order_id = request.path_params.get("order_id")
        
        if not order_id:
            return ApiResponse.validation_error("订单ID不能为空")
            
        async with AsyncSessionLocal() as db:
            order = await business_crud.get_order(db, order_id)
            if not order:
                return ApiResponse.not_found("订单不存在")
            
            return ApiResponse.success(
                data=order.to_dict(),
                message="获取订单成功"
            )
            
    except Exception as e:
        logger.error(f"获取订单服务异常: {str(e)}")
        return ApiResponse.error(
            message="获取订单失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
async def get_all_orders_service(request):
    """
    获取所有订单服务
    """
    try:
        async with AsyncSessionLocal() as db:
            filters = {"is_deleted": False}
            orders = await business_crud.get_orders_by_filters(db, filters) 
            return ApiResponse.success(
                data=[order.to_dict() for order in orders],
                message="获取所有订单成功"
            )
    except Exception as e:
        logger.error(f"获取所有订单服务异常: {str(e)}")
        return ApiResponse.error(
            message="获取所有订单失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_orders_by_filter_service(request):
    """
    根据条件查询订单服务
    """
    try:
        request_data = request.json()
        filters = {}
        
        # 构建过滤条件
        if "phone" in request_data:
            filters["phone"] = request_data["phone"]
        if "course_name" in request_data:
            async with AsyncSessionLocal() as db:
                course = await business_crud.get_course_by_filter(db, {"course_name": request_data["course_name"]})
                if not course:
                    return ApiResponse.not_found("课程不存在")
                filters["course_id"] = course.course_id
        if "purchase_time" in request_data:
            # 转换purchase_time为datetime对象
            try:
                purchase_time_dt = datetime.strptime(request_data["purchase_time"], "%Y-%m-%d %H:%M:%S")
                filters["purchase_time"] = purchase_time_dt
            except ValueError as e:
                logger.error(f"购买时间格式错误: {str(e)}")
                return ApiResponse.validation_error("购买时间格式错误，应为'YYYY-MM-DD HH:MM:SS'格式")
        if "is_refund" in request_data:
            # 转换is_refund为布尔值
            is_refund_bool = True if request_data["is_refund"] == "已退款" else False
            filters["is_refund"] = is_refund_bool
        if "created_at" in request_data:
            filters["created_at"] = request_data["created_at"]

        # 添加未删除的过滤条件
        filters["is_deleted"] = False
            
        async with AsyncSessionLocal() as db:
            orders = await business_crud.get_orders_by_filters(db, filters)
            if not orders:
                return ApiResponse.success(
                    data=[],
                    message="未找到符合条件的订单"
                )
            return ApiResponse.success(
                data=[order.to_dict() for order in orders],
                message="获取订单成功"
            )
            
    except Exception as e:
        logger.error(f"查询订单服务异常: {str(e)}")
        return ApiResponse.error(
            message="查询订单失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )
    




async def create_user_entitlement_service(request):
    """
    创建用户权益服务
    """
    try:
        request_data = request.json()
        phone = request_data.get("phone")
        rule_id = request_data.get("rule_id")
        
        if not all([phone, rule_id]):
            return ApiResponse.validation_error("手机号和权益规则ID不能为空")
            
        async with AsyncSessionLocal() as db:
            # 检查权益规则是否存在
            rule = await business_crud.get_entitlement_rule(db, rule_id)
            if not rule:
                return ApiResponse.not_found("权益规则不存在")
            
            # 计算权益有效期
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=rule.validity_days)
            
            # 准备用户权益数据
            entitlement_data = {
                "entitlement_id": generate_entitlement_id(),
                "phone": phone,
                "rule_id": rule_id,
                "start_date": start_date,
                "end_date": end_date,
                "daily_remaining": rule.daily_limit,
                "is_deleted": False
            }
            
            try:
                new_entitlement = await business_crud.create_user_entitlement(db, entitlement_data)
                return ApiResponse.success(
                    data=new_entitlement.to_dict(),
                    message="用户权益创建成功"
                )
            except Exception as e:
                logger.error(f"创建用户权益失败: {str(e)}")
                return ApiResponse.error(
                    message="创建用户权益失败",
                    status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
    except Exception as e:
        logger.error(f"创建用户权益服务异常: {str(e)}")
        return ApiResponse.error(
            message="创建用户权益失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def delete_user_entitlement_service(request):
    """
    删除用户权益服务
    """
    try:
        entitlement_id = request.path_params.get("entitlement_id")
        
        if not entitlement_id:
            return ApiResponse.validation_error("用户权益ID不能为空")
            
        async with AsyncSessionLocal() as db:
            # 检查用户权益是否存在
            entitlement = await business_crud.get_user_entitlement(db, entitlement_id)
            if not entitlement:
                return ApiResponse.not_found("用户权益不存在")
            
            try:
                # 软删除，更新is_deleted字段
                await business_crud.update_user_entitlement(db, entitlement_id, {"is_deleted": True})
                return ApiResponse.success(message="用户权益删除成功")
            except Exception as e:
                logger.error(f"删除用户权益失败: {str(e)}")
                return ApiResponse.error(
                    message="删除用户权益失败",
                    status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
    except Exception as e:
        logger.error(f"删除用户权益服务异常: {str(e)}")
        return ApiResponse.error(
            message="删除用户权益失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def update_user_entitlement_service(request):
    """
    更新用户权益服务
    """
    try:
        entitlement_id = request.path_params.get("entitlement_id")
        request_data = request.json()
        
        if not entitlement_id:
            return ApiResponse.validation_error("用户权益ID不能为空")
            
        if not request_data:
            return ApiResponse.validation_error("请求数据不能为空")
            
        # 只允许更新特定字段
        allowed_fields = ["phone", "rule_id", "end_date", "daily_remaining"]
        update_data = {k: v for k, v in request_data.items() if k in allowed_fields}
        
        if not update_data:
            return ApiResponse.validation_error("没有有效的更新字段")
            
        async with AsyncSessionLocal() as db:
            # 检查用户权益是否存在
            entitlement = await business_crud.get_user_entitlement(db, entitlement_id)
            if not entitlement:
                return ApiResponse.not_found("用户权益不存在")
            
            # 如果更新rule_id，检查新规则是否存在
            if "rule_id" in update_data:
                rule = await business_crud.get_entitlement_rule(db, update_data["rule_id"])
                if not rule:
                    return ApiResponse.not_found("权益规则不存在")
            
            try:
                updated_entitlement = await business_crud.update_user_entitlement(db, entitlement_id, update_data)
                return ApiResponse.success(
                    data=updated_entitlement.to_dict(),
                    message="用户权益更新成功"
                )
            except Exception as e:
                logger.error(f"更新用户权益失败: {str(e)}")
                return ApiResponse.error(
                    message="更新用户权益失败",
                    status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
    except Exception as e:
        logger.error(f"更新用户权益服务异常: {str(e)}")
        return ApiResponse.error(
            message="更新用户权益失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_user_entitlement_service(request):
    """
    获取单个用户权益服务
    """
    try:
        entitlement_id = request.path_params.get("entitlement_id")
        
        if not entitlement_id:
            return ApiResponse.validation_error("用户权益ID不能为空")
            
        async with AsyncSessionLocal() as db:
            entitlement = await business_crud.get_user_entitlement(db, entitlement_id)
            if not entitlement:
                return ApiResponse.not_found("用户权益不存在")
            
            return ApiResponse.success(
                data=entitlement.to_dict(),
                message="获取用户权益成功"
            )
            
    except Exception as e:
        logger.error(f"获取用户权益服务异常: {str(e)}")
        return ApiResponse.error(
            message="获取用户权益失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_all_user_entitlements_service(request):
    """
    获取所有用户权益服务
    """
    try:
        async with AsyncSessionLocal() as db:
            # 添加过滤条件，只获取未删除的用户权益
            filters = {"is_deleted": False}
            entitlements = await business_crud.get_user_entitlements_by_filters(db, filters)
            return ApiResponse.success(
                data=[entitlement.to_dict() for entitlement in entitlements],
                message="获取所有用户权益成功"
            )
    except Exception as e:
        logger.error(f"获取所有用户权益服务异常: {str(e)}")
        return ApiResponse.error(
            message="获取所有用户权益失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_user_entitlements_by_filter_service(request):
    """
    根据条件查询用户权益服务
    """
    try:
        request_data = request.json()
        filters = {}
        
        # 构建过滤条件
        if "entitlement_id" in request_data:
            filters["entitlement_id"] = request_data["entitlement_id"]
        if "phone" in request_data:
            filters["phone"] = request_data["phone"]
        if "rule_id" in request_data:
            filters["rule_id"] = request_data["rule_id"]
        if "start_date" in request_data:
            try:
                start_date = datetime.strptime(request_data["start_date"], "%Y-%m-%d %H:%M:%S")
                filters["start_date"] = start_date
            except ValueError as e:
                logger.error(f"开始日期格式错误: {str(e)}")
                return ApiResponse.validation_error("开始日期格式错误，应为'YYYY-MM-DD HH:MM:SS'格式")
        if "end_date" in request_data:
            try:
                end_date = datetime.strptime(request_data["end_date"], "%Y-%m-%d %H:%M:%S")
                filters["end_date"] = end_date
            except ValueError as e:
                logger.error(f"结束日期格式错误: {str(e)}")
                return ApiResponse.validation_error("结束日期格式错误，应为'YYYY-MM-DD HH:MM:SS'格式")
        if "daily_remaining" in request_data:
            filters["daily_remaining"] = request_data["daily_remaining"]
            
        # 添加未删除的过滤条件
        filters["is_deleted"] = False
            
        async with AsyncSessionLocal() as db:
            entitlements = await business_crud.get_user_entitlements_by_filters(db, filters)
            if not entitlements:
                return ApiResponse.success(
                    data=[],
                    message="未找到符合条件的用户权益"
                )
            return ApiResponse.success(
                data=[entitlement.to_dict() for entitlement in entitlements],
                message="获取用户权益成功"
            )
            
    except Exception as e:
        logger.error(f"查询用户权益服务异常: {str(e)}")
        return ApiResponse.error(
            message="查询用户权益失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )
    









