import json
import re
import random
from datetime import datetime, timedelta
from robyn import Headers, Request, Response, jsonify, status_codes
from apps.users import crud
from apps.users.models import User
from core.auth import TokenService, verify_password, get_password_hash, get_token_from_request
from sqlalchemy.ext.asyncio import AsyncSession
from apps.users.queries import get_user_by_phone
from core.database import AsyncSessionLocal
from core.response import ApiResponse
from core.logger import setup_logger
from core.cache import Cache
from apps.users.utils import generate_user_id

# 设置日志记录器
logger = setup_logger('user_services')

"""
    crud -> services -> api
    服务层:根据业务逻辑整合crud数据操作 封装业务方法 可以由上层函数直接调用
    服务层 应该完成 业务逻辑（如判断数据是否存在、响应失败的处理逻辑）
"""

# 登录
async def login_user(request):
    """
    登录用户
    """
    try:
        request_data = request.json()
        phone = request_data.get("phone")
        password = request_data.get("password")

        if not phone or not password:
            logger.warning("Missing phone or password")
            return ApiResponse.validation_error("手机号和密码不能为空")

        # 获取用户响应
        async with AsyncSessionLocal() as db:
            user = await crud.get_user_by_filter(db, {"phone": phone})
            if not user:
                return ApiResponse.not_found("用户不存在")

            if not verify_password(password, user.password):
                logger.warning(f"Invalid password attempt for phone: {phone}")
                return ApiResponse.error(
                    message="密码错误",
                    status_code=status_codes.HTTP_401_UNAUTHORIZED
                )

            # 更新用户登录时间
            await crud.update_user(db, user.user_id, {"last_login": datetime.utcnow()})
            from apps.business import crud as business_crud
            # 根据phone查询用户权益表
            async with AsyncSessionLocal() as db:
                # 添加过滤条件，只获取未删除的用户权益
                filters = {"phone": phone, "is_deleted": False}
                # 按创建时间倒序排序
                order_by = {"created_at": "desc"}
                
                entitlements, total_count = await business_crud.get_user_entitlements_by_filters(
                    db, 
                    filters=filters,
                    order_by=order_by,
                    page=1,
                    page_size=99
                )
                
                # 计算总页数
                total_pages = (total_count + 10 - 1) // 10
                
                # 生成Token
                token_data = {
                    "user_id": user.user_id,
                    "phone": user.phone,
                    "entitlements": [
                        {
                            "entitlement_id": entitlement.entitlement_id,
                            "rule_id": entitlement.rule_id,
                            "course_name": entitlement.course_name,
                            "ai_product_id": entitlement.ai_product_id,
                            "product_name": entitlement.product_name,
                            "start_date": entitlement.start_date.isoformat() if entitlement.start_date else None,
                            "end_date": entitlement.end_date.isoformat() if entitlement.end_date else None,
                            "daily_remaining": entitlement.daily_remaining,
                            "is_active": entitlement.is_active
                        }
                        for entitlement in entitlements
                    ]
                }
            
            # 创建访问令牌
            access_token = TokenService.create_access_token(token_data)

            # 创建响应
            response = ApiResponse.success(
                message="登录成功",
                data={
                    "user_id": user.user_id,
                    "phone": user.phone,
                    "access_token": access_token,
                    "entitlements": {
                        "items": [
                            {
                                "entitlement_id": entitlement.entitlement_id,
                                "rule_id": entitlement.rule_id,
                                "course_name": entitlement.course_name,
                                "ai_product_id": entitlement.ai_product_id,
                                "product_name": entitlement.product_name,
                                "start_date": entitlement.start_date.isoformat() if entitlement.start_date else None,
                                "end_date": entitlement.end_date.isoformat() if entitlement.end_date else None,
                                "daily_remaining": entitlement.daily_remaining,
                                "is_active": entitlement.is_active
                            }
                            for entitlement in entitlements
                        ],
                        "total": total_count,
                        "page": 1,
                        "page_size": 10,
                        "total_pages": total_pages
                    }
                }
            )
            
            # 设置访问令牌到HttpOnly Cookie
            response.headers["Set-Cookie"] = (
                f"access_token=Bearer {access_token}; "
                f"HttpOnly; Secure; Path=/; SameSite=Strict; "
                f"Max-Age={30*60}"  # 30分钟
            )

            return response

    except Exception as e:
        logger.error(f"Error processing user login: {str(e)}")
        return ApiResponse.error(message="登录处理失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

# 退出登录
async def logout_user(request):
    """
    退出登录
    """
    try:
        # 获取当前令牌
        token = get_token_from_request(request)
        payload = TokenService.decode_token(token)
        user_id = payload.get("user_id")
        
        if token:
            # 将令牌加入黑名单
            TokenService.revoke_token(token)
        
        # 创建响应
        response = ApiResponse.success(message="退出登录成功")
        
        # 清除Cookie中的访问令牌
        response.headers["Set-Cookie"] = (
            "access_token=; HttpOnly; Secure; Path=/; SameSite=Strict; Max-Age=0"
        )
        
        return response
    except Exception as e:
        print(f"Error: {e}")
        return ApiResponse.error(message="退出登录失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

# 注册
async def register(request):
    """
    注册
    """
    try:
        logger.info("Starting registration precheck process")

        # 获取请求数据
        try:
            user_data = request.json()
            logger.debug(f"Received registration request: {user_data}")
        except Exception as e:
            logger.error(f"Error parsing JSON data: {str(e)}")
            return ApiResponse.validation_error("无效的 JSON 格式")

        # 验证必填字段
        required_fields = ['phone', 'password']
        
        for field in required_fields:
            if field not in user_data:
                logger.warning(f"Missing required field: {field}")
                return ApiResponse.validation_error(f"缺少必填字段: {field}")
        
        phone = user_data['phone']

        # 检查手机号是否已存在
        try:
            if await crud.check_phone_exists(phone):
                logger.warning(f"Phone number already exists: {phone}")
                return ApiResponse.validation_error("手机号已被注册")
        except Exception as e:
            logger.error(f"Error checking phone existence: {str(e)}")
            return ApiResponse.error("手机号检查失败")

        # 创建用户
        try:
            # 确保密码被正确加密
            user_data['password'] = get_password_hash(user_data['password'])
            user_data['last_login'] = datetime.utcnow()
            
            async with AsyncSessionLocal() as db:
                try:
                    # 再次检查用户是否已存在
                    existing_user_phone = await crud.get_user_by_filter(db, {"phone": phone})
                    if existing_user_phone:
                        logger.warning(f"User already exists with phone: {phone}")
                        return ApiResponse.error(f"手机号{phone}已被注册")

                    user_data["user_id"] = generate_user_id()

                    new_user = await crud.create_user(db, user_data)
                    logger.info(f"Created new user with ID: {new_user.user_id if new_user else 'None'}")

                    if new_user and new_user.user_id:
                        from apps.business import crud as business_crud
                        # 根据phone查询用户权益表
                        async with AsyncSessionLocal() as db:
                            # 添加过滤条件，只获取未删除的用户权益
                            filters = {"phone": phone, "is_deleted": False}
                            # 按创建时间倒序排序
                            order_by = {"created_at": "desc"}
                            
                            entitlements, total_count = await business_crud.get_user_entitlements_by_filters(
                                db, 
                                filters=filters,
                                order_by=order_by,
                                page=1,
                                page_size=99
                            )
                            
                            # 计算总页数
                            total_pages = (total_count + 10 - 1) // 10
                            
                            if entitlements:
                                # 更新用户权益表的is_active为True
                                for entitlement in entitlements:
                                    await business_crud.update_user_entitlement(db, entitlement.entitlement_id, {"is_active": True})
                                # 生成Token
                                token_data = {
                                    "user_id": new_user.user_id,
                                    "phone": new_user.phone,
                                    "entitlements": [
                                        {
                                            "entitlement_id": entitlement.entitlement_id,
                                            "rule_id": entitlement.rule_id,
                                            "course_name": entitlement.course_name,
                                            "ai_product_id": entitlement.ai_product_id,
                                            "product_name": entitlement.product_name,
                                            "start_date": entitlement.start_date.isoformat() if entitlement.start_date else None,
                                            "end_date": entitlement.end_date.isoformat() if entitlement.end_date else None,
                                            "daily_remaining": entitlement.daily_remaining,
                                            "is_active": True
                                        }
                                        for entitlement in entitlements
                                    ]
                                }
                            else:
                                logger.error("User creation returned None or invalid user")
                                await db.rollback()
                                return ApiResponse.error("请先购买权益")

                        # 创建访问令牌和刷新令牌
                        access_token = TokenService.create_access_token(token_data)

                        # 创建响应
                        response = ApiResponse.success(
                            message="注册成功并已登录",
                            data={
                                "user_id": new_user.user_id,
                                "access_token": access_token,
                                "phone": new_user.phone,
                                "entitlements": {
                                    "items": [
                                        {
                                            "entitlement_id": entitlement.entitlement_id,
                                            "rule_id": entitlement.rule_id,
                                            "course_name": entitlement.course_name,
                                            "ai_product_id": entitlement.ai_product_id,
                                            "product_name": entitlement.product_name,
                                            "start_date": entitlement.start_date.isoformat() if entitlement.start_date else None,
                                            "end_date": entitlement.end_date.isoformat() if entitlement.end_date else None,
                                            "daily_remaining": entitlement.daily_remaining,
                                            "is_active": True
                                        }
                                        for entitlement in entitlements
                                    ],
                                    "total": total_count,
                                    "page": 1,
                                    "page_size": 99,
                                    "total_pages": total_pages
                                }
                            }
                        )

                        # 设置访问令牌到HttpOnly Cookie
                        response.headers["Set-Cookie"] = (
                            f"access_token=Bearer {access_token}; "
                            f"HttpOnly; Secure; Path=/; SameSite=Strict; "
                            f"Max-Age={30*60}"  # 30分钟
                        )
                        
                        logger.info(f"User registered and logged in successfully: {phone}")
                        return response
                    else:
                        logger.error("User creation returned None or invalid user")
                        await db.rollback()
                        return ApiResponse.error("用户创建失败")
                        
                except Exception as db_error:
                    logger.error(f"Database error during user creation: {str(db_error)}")
                    await db.rollback()
                    return ApiResponse.error("用户创建失败")
                    
        except Exception as e:
            logger.error(f"Error processing user registration: {str(e)}")
            return ApiResponse.error("注册处理失败")
            
    except Exception as e:
        logger.error(f"Verification and registration failed: {str(e)}")
        return ApiResponse.error("注册失败")





async def create_user_service(request):
    """
    创建用户接口 管理员权限
    """
    try:
        user_data = request.json()
        phone = user_data.get("phone")
        password = user_data.get("password")
        
        # 确保必填字段都存在
        if not all([phone, password]):
            return ApiResponse.validation_error("缺少必填字段")

        # 检查用户是否已存在
        async with AsyncSessionLocal() as db:
            user_exists = (
                await crud.get_user_by_filter(db, {"phone": phone})
            )
            
            if user_exists:
                return ApiResponse.error(
                    message="用户已存在",
                    status_code=status_codes.HTTP_409_CONFLICT
                )

            user_data["user_id"] = generate_user_id()
            user_data["password"] = get_password_hash(user_data["password"])

            try:
                inserted_user = await crud.create_user(db, user_data)
                if not inserted_user:
                    raise Exception("User creation failed")
                return ApiResponse.success(
                    data=inserted_user.to_dict(),
                    message="用户创建成功"
                )
            except Exception as e:
                raise Exception(f"Database integrity error: {str(e)}")

    except Exception as e:
        print(f"Error: {e}")
        return ApiResponse.error(message="创建用户失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

async def update_user_service(request):
    """
    通过id 更新用户密码
    """
    try:
        async with AsyncSessionLocal() as db:
            user_id = request.path_params.get("user_id")
            user_data = request.json()
            user_obj = await crud.get_user(db, user_id)
            if not user_obj:
                return ApiResponse.not_found("用户不存在")

            user_data["password"] = get_password_hash(user_data["password"])
    
            user = await crud.update_user(db, user_id, user_data)
            if not user:
                raise Exception("User update failed")
            
            return ApiResponse.success(
                data=user.to_dict(),
                message="用户更新成功"
            )
    except Exception as e:
        print(f"Error: {e}")
        await db.rollback()
        return ApiResponse.error(message="更新用户失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

async def update_user_field_service(request):
    """
    更新用户指定字段 params url使用接口
    """
    try:
        async with AsyncSessionLocal() as db:
            user_id = request.path_params.get("user_id")

            user_obj = await crud.get_user(db, user_id)
            if not user_obj:
                return ApiResponse.not_found("用户不存在")
            
            user_data = request.json()

            # 处理布尔值字段
            if 'is_deleted' in user_data:
                if isinstance(user_data['is_deleted'], str):
                    user_data['is_deleted'] = user_data['is_deleted'].lower() == 'true'
                else:
                    user_data['is_deleted'] = bool(user_data['is_deleted'])

            if "password" in user_data:
                user_data["password"] = get_password_hash(user_data["password"])

                
            user = await crud.update_user(db, user_id, user_data)
            if not user:
                raise Exception("User update failed")
            
            return ApiResponse.success(
                data=user.to_dict(),
                message="用户字段更新成功"
            )
    except Exception as e:
        print(f"Error: {e}")
        await db.rollback()
        return ApiResponse.error(message="更新用户字段失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

# 废弃密钥
async def delete_user_service(request):
    """
    删除用户
    """
    try:
        async with AsyncSessionLocal() as db:
            user_id = request.path_params.get("user_id")
            user_obj = await crud.get_user(db, user_id)
            if not user_obj:
                return ApiResponse.not_found("用户不存在")
            
            user = await crud.delete_user(db, user_id) 
            if not user:
                raise Exception("User delete failed")
            
            return ApiResponse.success(message="用户删除成功")
    except Exception as e:
        print(f"Error: {e}")
        return ApiResponse.error(message="删除用户失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

# 刷新访问令牌
async def refresh_token(request):
    """
    刷新访问令牌
    """
    try:
        refresh_token = request.json().get("refresh_token")
        if not refresh_token:
            return ApiResponse.validation_error("缺少刷新令牌")
        
        # 验证刷新令牌
        payload = TokenService.decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return ApiResponse.unauthorized("无效的刷新令牌")
        
        # 创建新的访问令牌
        token_data = {
            "user_id": payload["user_id"],
            "phone": payload["phone"]
        }
        new_access_token = TokenService.create_access_token(token_data)
        
        # 创建响应
        response = ApiResponse.success(
            message="令牌刷新成功",
            data={"phone": payload["sub"]}
        )
        
        # 设置新的访问令牌
        response.headers["Set-Cookie"] = (
            f"access_token=Bearer {new_access_token}; "
            f"HttpOnly; Secure; Path=/; SameSite=Strict; "
            f"Max-Age={30*60}"  # 30分钟
        )
        
        return response
    except Exception as e:
        print(f"Error refreshing token: {e}")
        return ApiResponse.error(message="令牌刷新失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

# 检查并自动续期令牌
async def check_and_refresh_token(request):
    """
    检查并自动续期令牌
    """
    try:
        token = get_token_from_request(request)
        if not token:
            return None
            
        # 检查令牌是否需要续期
        needs_refresh, payload = TokenService.check_token_needs_refresh(token)
        if needs_refresh and payload:
            # 创建新的访问令牌
            token_data = {
                "user_id": payload["user_id"],
                "phone": payload["phone"]
            }
            new_access_token = TokenService.create_access_token(token_data)
            
            # 创建响应
            response = ApiResponse.success(
                message="令牌已自动续期",
                data={
                    "user_id": payload["user_id"],
                    "phone": payload["phone"]
                }
            )
            
            # 设置新的访问令牌
            response.headers["Set-Cookie"] = (
                f"access_token=Bearer {new_access_token}; "
                f"HttpOnly; Secure; Path=/; SameSite=Strict; "
                f"Max-Age={30*60}"  # 30分钟
            )
            
            return response
            
        return None
    except Exception as e:
        logger.error(f"Error checking token refresh: {str(e)}")
        return None

# 生成Token
async def get_token(request):
    # 生成Token
    try:
        user_id = request.path_params.get("user_id")
        token_data = {
            "user_id": user_id
        }

        # 创建访问令牌和刷新令牌
        access_token = TokenService.create_access_token(token_data)
        # refresh_token = TokenService.create_refresh_token(token_data)

        # 创建响应
        response = ApiResponse.success(
            message=f"用户{user_id}已获取access_token",
            data={
                "user_id": user_id,
                "access_token": access_token
            }
        )
        
        return response
    except Exception as e:
        return ApiResponse.error(
            message="获取token失败"
        )

# 检查令牌状态
async def check_token(request):
    """
    检查令牌状态
    """
    try:
        token = get_token_from_request(request)
        if not token:
            return ApiResponse.error(f"没有获取到token")
        logger.info(f"token2是:{token}")
            
        # 检查令牌是否需要续期
        needs_refresh, payload = TokenService.check_token_needs_refresh(token)
        logger.info(f"是否需要刷新:{needs_refresh},解码后的数据是：{payload}")
        if needs_refresh and payload:
            # 创建响应
            response = ApiResponse.success(
                message="token已过期",
                data={
                    "user_id": payload["user_id"],
                    "phone": payload["phone"]
                }
            )
            
            return response
        elif not needs_refresh and payload:
            # 如果不需要续期，返回成功响应
            return ApiResponse.success(message="token生效中，无需续期",
                                       data={
                                            "user_id": payload["user_id"],
                                            "phone": payload["phone"]
                                        })
                                    
    except Exception as e:
        logger.error(f"Error checking token refresh: {str(e)}")
        response = ApiResponse.error(f"查询失败")
        return response

# 获取密钥信息
async def get_userinfo(request):
    """
    从token中获取用户信息
    """
    try:
        token = get_token_from_request(request)
        if not token:
            return ApiResponse.error(f"没有获取到token")
        logger.info(f"token是:{token}")
            
        # 检查令牌是否需要续期
        needs_refresh, payload = TokenService.check_token_needs_refresh(token)
        logger.info(f"是否需要刷新:{needs_refresh},解码后的数据是：{payload}")
        if not payload:
            return ApiResponse.unauthorized("无效的token")

        if needs_refresh and payload:
        
            # 创建新的访问令牌
            token_data = {
                "user_id": payload["user_id"],
                "phone": payload["phone"]
            }
            new_access_token = TokenService.create_access_token(token_data)
            
            # 创建响应
            response = ApiResponse.success(
                message="令牌刷新成功",
                data={
                    "user_id": payload["user_id"],
                    "phone": payload["phone"],
                    "access_token": new_access_token
                    }
                )
            
            # 设置新的访问令牌
            response.headers["Set-Cookie"] = (
                f"access_token=Bearer {new_access_token}; "
                f"HttpOnly; Secure; Path=/; SameSite=Strict; "
                f"Max-Age={30*60}"  # 30分钟
            )
            
            return response
        elif not needs_refresh and payload:
            # 如果不需要续期，返回成功响应
            return ApiResponse.success(message="获取用户信息成功",
                                       data={
                                            "user_id": payload["user_id"],
                                            "phone": payload["phone"],
                                            "access_token": token
                                        })
                                    
    except Exception as e:
        logger.error(f"无法获取用户信息: {str(e)}")
        response = ApiResponse.error(f"获取用户信息失败")
        return response

# 管理员服务层函数
async def create_admin_service(request):
    """
    创建管理员服务
    """
    try:
        admin_data = request.json()
        username = admin_data.get("username")
        password = admin_data.get("password")
        
        # 确保必填字段都存在
        if not all([username, password]):
            return ApiResponse.validation_error("缺少必填字段")

        # 检查管理员是否已存在
        async with AsyncSessionLocal() as db:
            admin_exists = await crud.check_username_exists(username)
            if admin_exists:
                return ApiResponse.error(
                    message="管理员用户名已存在",
                    status_code=status_codes.HTTP_409_CONFLICT
                )

            # 生成管理员ID
            admin_data["admin_id"] = f"admin_{int(datetime.utcnow().timestamp())}"
            # 加密密码
            admin_data["password"] = get_password_hash(admin_data["password"])

            try:
                inserted_admin = await crud.create_admin(db, admin_data)
                if not inserted_admin:
                    raise Exception("Admin creation failed")
                return ApiResponse.success(
                    data=inserted_admin.to_dict(),
                    message="管理员创建成功"
                )
            except Exception as e:
                raise Exception(f"Database integrity error: {str(e)}")

    except Exception as e:
        logger.error(f"创建管理员失败: {str(e)}")
        return ApiResponse.error(
            message="创建管理员失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def update_admin_service(request):
    """
    更新管理员服务
    """
    try:
        admin_id = request.path_params.get("admin_id")
        admin_data = request.json()
        
        if not admin_id:
            return ApiResponse.validation_error("管理员ID不能为空")
            
        async with AsyncSessionLocal() as db:
            admin = await crud.get_admin(db, admin_id)
            if not admin:
                return ApiResponse.not_found("管理员不存在")
            
            # 如果更新密码，需要加密
            if "password" in admin_data:
                admin_data["password"] = get_password_hash(admin_data["password"])
            
            try:
                updated_admin = await crud.update_admin(db, admin_id, admin_data)
                return ApiResponse.success(
                    data=updated_admin.to_dict(),
                    message="管理员更新成功"
                )
            except Exception as e:
                logger.error(f"更新管理员失败: {str(e)}")
                return ApiResponse.error(
                    message="更新管理员失败",
                    status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
    except Exception as e:
        logger.error(f"更新管理员服务异常: {str(e)}")
        return ApiResponse.error(
            message="更新管理员失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def delete_admin_service(request):
    """
    删除管理员服务
    """
    try:
        admin_id = request.path_params.get("admin_id")
        
        if not admin_id:
            return ApiResponse.validation_error("管理员ID不能为空")
            
        async with AsyncSessionLocal() as db:
            admin = await crud.get_admin(db, admin_id)
            if not admin:
                return ApiResponse.not_found("管理员不存在")
            
            try:
                await crud.delete_admin(db, admin_id)
                return ApiResponse.success(message="管理员删除成功")
            except Exception as e:
                logger.error(f"删除管理员失败: {str(e)}")
                return ApiResponse.error(
                    message="删除管理员失败",
                    status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
    except Exception as e:
        logger.error(f"删除管理员服务异常: {str(e)}")
        return ApiResponse.error(
            message="删除管理员失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_admin_service(request):
    """
    获取单个管理员服务
    """
    try:
        admin_id = request.path_params.get("admin_id")
        
        if not admin_id:
            return ApiResponse.validation_error("管理员ID不能为空")
            
        async with AsyncSessionLocal() as db:
            admin = await crud.get_admin(db, admin_id)
            if not admin:
                return ApiResponse.not_found("管理员不存在")
            
            return ApiResponse.success(
                data=admin.to_dict(),
                message="获取管理员成功"
            )
            
    except Exception as e:
        logger.error(f"获取管理员服务异常: {str(e)}")
        return ApiResponse.error(
            message="获取管理员失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def get_admins_service(request):
    """
    获取所有管理员服务
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
        filters = {"is_deleted": False}
        if "username" in request.query_params:
            filters["username"] = request.query_params.get("username")
            
        # 获取排序条件
        order_by = {"created_at": "desc"}  # 默认按创建时间倒序排序
            
        async with AsyncSessionLocal() as db:
            try:
                admins, total_count = await crud.get_admins_by_filters(
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
                        "items": [admin.to_dict() for admin in admins],
                        "total": total_count,
                        "page": page,
                        "page_size": page_size,
                        "total_pages": total_pages
                    },
                    message="获取管理员列表成功"
                )
            except Exception as e:
                logger.error(f"查询管理员列表失败: {str(e)}")
                return ApiResponse.error(
                    message="获取管理员列表失败",
                    status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
                )
    except Exception as e:
        logger.error(f"获取管理员列表服务异常: {str(e)}")
        return ApiResponse.error(
            message="获取管理员列表失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

# 管理员登录
async def login_admin_service(request):
    """
    管理员登录服务
    """
    try:
        request_data = request.json()
        username = request_data.get("username")
        password = request_data.get("password")

        if not username or not password:
            logger.warning("Missing username or password")
            return ApiResponse.validation_error("用户名和密码不能为空")

        # 获取管理员响应
        async with AsyncSessionLocal() as db:
            admin = await crud.get_admin_by_filter(db, {"username": username})
            if not admin:
                return ApiResponse.not_found("管理员不存在")

            if not verify_password(password, admin.password):
                logger.warning(f"Invalid password attempt for username: {username}")
                return ApiResponse.error(
                    message="密码错误",
                    status_code=status_codes.HTTP_401_UNAUTHORIZED
                )

            # 更新管理员登录时间
            await crud.update_admin(db, admin.admin_id, {"last_login": datetime.utcnow()})
            
            # 生成Token
            token_data = {
                "admin_id": admin.admin_id,
                "username": admin.username,
                "type": "admin"  # 标记为管理员token
            }
            
            # 创建访问令牌
            access_token = TokenService.create_access_token(token_data)

            # 创建响应
            response = ApiResponse.success(
                message="登录成功",
                data={
                    "admin_id": admin.admin_id,
                    "username": admin.username,
                    "access_token": access_token
                }
            )
            
            # 设置访问令牌到HttpOnly Cookie
            response.headers["Set-Cookie"] = (
                f"access_token=Bearer {access_token}; "
                f"HttpOnly; Secure; Path=/; SameSite=Strict; "
                f"Max-Age={30*60}"  # 30分钟
            )

            return response

    except Exception as e:
        logger.error(f"Error processing admin login: {str(e)}")
        return ApiResponse.error(
            message="登录处理失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

# 管理员退出登录
async def logout_admin_service(request):
    """
    管理员退出登录服务
    """
    try:
        # 创建响应
        response = ApiResponse.success(message="退出登录成功")
        
        # 清除Cookie中的访问令牌
        response.headers["Set-Cookie"] = (
            "access_token=; HttpOnly; Secure; Path=/; SameSite=Strict; Max-Age=0"
        )
        
        return response
            
    except Exception as e:
        logger.error(f"Error processing admin logout: {str(e)}")
        return ApiResponse.error(
            message="退出登录失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

# 获取用户总数
async def get_user_count_service(request):
    """
    获取用户总数服务
    """
    try:
        async with AsyncSessionLocal() as db:
            # 获取过滤条件
            filters = {"is_deleted": False}
            
            # 获取用户总数
            users = await crud.get_users_by_filters(db, filters)
            total_count = len(users)
            
            return ApiResponse.success(
                data={
                    "total": total_count
                },
                message="获取用户总数成功"
            )
    except Exception as e:
        logger.error(f"获取用户总数失败: {str(e)}")
        return ApiResponse.error(
            message="获取用户总数失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

# 根据手机号开头搜索用户
async def search_users_by_phone_prefix_service(request):
    """
    根据手机号开头搜索用户服务
    """
    try:
        request_data = request.json()
        phone_prefix = request_data.get("phone_prefix")
        
        if not phone_prefix:
            return ApiResponse.validation_error("手机号前缀不能为空")
            
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
            
        async with AsyncSessionLocal() as db:
            # 获取所有用户
            users = await crud.get_users_by_filters(db, {"is_deleted": False})
            
            # 过滤出手机号以指定前缀开头的用户
            filtered_users = [
                user for user in users 
                if user.phone.startswith(phone_prefix)
            ]
            
            # 计算总记录数
            total_count = len(filtered_users)
            
            # 手动分页
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_users = filtered_users[start_idx:end_idx]
            
            # 计算总页数
            total_pages = (total_count + page_size - 1) // page_size
            
            return ApiResponse.success(
                data={
                    "items": [user.to_dict() for user in paginated_users],
                    "total": total_count,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages
                },
                message="搜索用户成功"
            )
    except Exception as e:
        logger.error(f"搜索用户失败: {str(e)}")
        return ApiResponse.error(
            message="搜索用户失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )