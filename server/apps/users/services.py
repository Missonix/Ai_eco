import json
import re
import random
from datetime import datetime, timedelta
from robyn import Headers, Request, Response, jsonify, status_codes
from apps.users import crud
from apps.users.models import User
from core.auth import TokenService, verify_password, get_password_hash, get_token_from_request
from sqlalchemy.ext.asyncio import AsyncSession
from apps.users.queries import get_user_by_email, get_user_by_phone
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

async def create_user_service(request):
    """
    创建用户接口 管理员权限
    """
    try:
        user_data = request.json()
        username = user_data.get("username")
        email = user_data.get("email")
        # phone = user_data.get("phone")
        password = user_data.get("password")
        try:
            level = user_data.get("level")
        except:
            level = 1
        try:
            usage_count = user_data.get("usage_count")
        except:
            usage_count = 1
        
        # 确保必填字段都存在
        if not all([email, password, username]):
            return ApiResponse.validation_error("缺少必填字段")

        # 检查用户是否已存在
        async with AsyncSessionLocal() as db:
            user_exists = (
                await crud.get_user_by_filter(db, {"username": username}) or 
                         await crud.get_user_by_filter(db, {"email": email}) 
                        #  or await crud.get_user_by_filter(db, {"phone": phone})
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
    更新用户密码
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
            bool_fields = ['is_admin', 'is_active', 'is_deleted']
            for field in bool_fields:
                if field in user_data:
                    if isinstance(user_data[field], str):
                        user_data[field] = user_data[field].lower() == 'true'
                    else:
                        user_data[field] = bool(user_data[field])

            if "password" in user_data:
                user_data["password"] = get_password_hash(user_data["password"])

            if "level" in user_data:
                user_data["level"] = int(user_data["level"])
            if "usage_count" in user_data:
                user_data["usage_count"] = int(user_data["usage_count"])
                
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
    
async def update_user_field_by_email(email, password):
    """
    更新用户password json使用接口
    """
    try:
        async with AsyncSessionLocal() as db:

            user_obj = await crud.get_user_by_filter(db, {"email": email})
            if not user_obj:
                return ApiResponse.not_found("用户不存在")

            user_data = {
                "password": get_password_hash(password)
            }
            old_password = user_obj.password
            
                
            user = await crud.update_user(db, user_obj.user_id, user_data)
            if not user:
                raise Exception("User update failed")

            return ApiResponse.success(
                data=user.to_dict(),
                message="密码更新成功",
                old_password=old_password
            )
    except Exception as e:
        print(f"Error: {e}")
        await db.rollback()
        return ApiResponse.error(message="密码更新失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

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

async def login_user(request):
    """
    用户名登录用户
    """
    try:
        request_data = request.json()
        username = request_data.get("account")  # 修改参数名为username
        password = request_data.get("password")

        if not username or not password:
            logger.warning("Missing username or password")
            return ApiResponse.validation_error("用户名和密码不能为空")

        # 获取用户响应
        async with AsyncSessionLocal() as db:
            user = await crud.get_user_by_filter(db, {"username": username})
            if not user:
                return ApiResponse.not_found("用户不存在")

            if not verify_password(password, user.password):
                logger.warning(f"Invalid password attempt for username: {username}")
                return ApiResponse.error(
                    message="密码错误",
                    status_code=status_codes.HTTP_401_UNAUTHORIZED
                )

            # 获取用户IP地址
            ip_address = request.headers.get("X-Real-IP") or request.headers.get("X-Forwarded-For") or request.ip_addr
            
            # 更新用户IP地址和登录时间
            await crud.update_user(db, user.user_id, {"is_activate": True, "ip_address": ip_address, "last_login": datetime.utcnow()})
            logger.info(f"Updated user {user.username} IP address to {ip_address}, user is_activate is True")
            
            # 生成Token
            token_data = {
                "user_id": user.user_id,
                "username": user.username,
                "is_admin": user.is_admin,
                "is_active": True
            }
            
            # 创建访问令牌
            access_token = TokenService.create_access_token(token_data)

            # 创建响应
            response = ApiResponse.success(
                message="登录成功",
                data={
                    "user_id": user.user_id,
                    "username": user.username,
                    "is_admin": user.is_admin,
                    "is_active": True,
                    "ip_address": ip_address,
                    "access_token": access_token,
                    "level": user.level,
                    "usage_count": user.usage_count
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
            "username": payload["username"],
            "is_admin": payload.get("is_admin", False),
            "is_active": True
        }
        new_access_token = TokenService.create_access_token(token_data)
        
        # 创建响应
        response = ApiResponse.success(
            message="令牌刷新成功",
            data={"username": payload["sub"]}
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

async def send_verification_code_by_email(request):
    """
    生成验证码并发送至邮箱
    """
    try:
        request_data = request.json()
        email = request_data.get("email")
        try:
            if not await crud.check_email_exists(email):
                logger.warning(f"Email already exists: {email}")
                return ApiResponse.validation_error("当前邮箱未注册")
        except Exception as e:
            logger.error(f"Error checking email existence: {str(e)}")
            return ApiResponse.error("邮箱检查失败")

        from apps.users.utils import generate_numeric_verification_code, send_verification_email
        code = generate_numeric_verification_code()
        logger.debug(f"Generated verification code for {email}: {code}")
        
        # 缓存验证码和用户数据
        try:
            cache_data = {
                'code': code,
                'user_data': {
                    'email': email
                }
            }
            await Cache.set(f"registration:{email}", cache_data, expire=300)  # 5分钟过期
            logger.info(f"Verification code and user data cached for {email}")
        except Exception as e:
            logger.error(f"Failed to cache verification data: {str(e)}")
            return ApiResponse.error("验证数据缓存失败")
            
        # 发送验证码邮件
        try:
            email_sent = await send_verification_email(email, code)
            if not email_sent:
                logger.error("Failed to send verification email")
                return ApiResponse.error("验证码发送失败")
        except Exception as e:
            logger.error(f"Error sending verification email: {str(e)}")
            return ApiResponse.error("验证码发送失败")
            
        logger.info("Registration precheck completed successfully")
        return ApiResponse.success("验证码已发送")
    except Exception as e:
        logger.error(f"send verification code failed: {str(e)}")
        return ApiResponse.error("发送验证码失败")

async def login_user_by_email(request):
    """
    邮箱登录用户
    """
    try:
        request_data = request.json()
        email = request_data.get("email")
        code = request_data.get("code")

        if not email or not code:
            logger.warning("Missing email or code")
            return ApiResponse.validation_error("邮箱和验证码不能为空")

        # 获取用户响应
        user_response = await get_user_by_email(email) 
        logger.debug(f"User response status: {user_response.status_code}")

        if user_response.status_code != status_codes.HTTP_200_OK:
            return ApiResponse.not_found("用户不存在")
        
        try:
            response_data = json.loads(user_response.description)
            logger.debug(f"Response data: {response_data}")

            if not isinstance(response_data, dict):
                logger.error("Response data is not a dictionary")
                return ApiResponse.error(message="响应数据格式错误", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

            if "data" not in response_data:
                logger.error("No 'data' field in response")
                return ApiResponse.error(message="响应数据格式错误", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

            user_data = response_data["data"]
            logger.debug(f"User data: {user_data}")

            if not isinstance(user_data, dict):
                logger.error("User data is not a dictionary")
                return ApiResponse.error(message="用户数据格式错误", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

            try:
                cached_data = await Cache.get(f"registration:{email}")
                if not cached_data:
                    logger.warning(f"No registration data found for email: {email}")
                    return ApiResponse.error("验证码已过期")
                    
                if code != cached_data['code']:
                    logger.warning(f"Invalid verification code for email: {email}")
                    return ApiResponse.error("验证码错误")
                    
                    
            except Exception as e:
                logger.error(f"Error retrieving registration data from cache: {str(e)}")
                return ApiResponse.error("验证码验证失败")


            # 获取用户IP地址
            ip_address = request.headers.get("X-Real-IP") or request.headers.get("X-Forwarded-For") or request.ip_addr
            
            # 更新用户IP地址
            async with AsyncSessionLocal() as db:
                user = await crud.get_user_by_filter(db, {"email": user_data.get("email")})
                if user:
                    await crud.update_user(db, user_data.get("user_id"), {"ip_address": ip_address, "last_login": datetime.utcnow()})
                    # logger.info(f"Updated user {user_data.get("username")} IP address to {ip_address}")
            
            # 生成Token
            token_data = {
                "user_id": user_data.get("user_id"),
                "username": user_data.get("username"),
                "is_admin": user_data.get("is_admin", False),
                "is_active": True   
            }
            
            # 创建访问令牌和刷新令牌
            access_token = TokenService.create_access_token(token_data)
            refresh_token = TokenService.create_refresh_token(token_data)

            # 创建响应
            response = ApiResponse.success(
                message="登录成功",
                data={
                    "user_id": user_data["user_id"],
                    "username": user_data["username"],
                    "is_admin": user_data.get("is_admin", False),
                    "is_active": True,
                    "access_token": access_token,
                    "ip_address": ip_address
                }
            )
            
            # 设置访问令牌到HttpOnly Cookie
            response.headers["Set-Cookie"] = (
                f"access_token=Bearer {access_token}; "
                f"HttpOnly; Secure; Path=/; SameSite=Strict; "
                f"Max-Age={30*60}"  # 30分钟
            )

            return response

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding user data: {str(e)}")
            return ApiResponse.error(message="用户数据解析失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Error processing user login: {str(e)}")
        return ApiResponse.error(message="登录处理失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

async def forgot_password_by_email(request):
    """
    忘记密码
    """
    try:
        request_data = request.json()
        email = request_data.get("email")
        code = request_data.get("code")
        password = request_data.get("password")

        if not email or not code or not password:
            logger.warning("Missing email or code or password")
            return ApiResponse.validation_error("邮箱和验证码和密码不能为空")

        # 获取用户响应
        user_response = await get_user_by_email(email) 
        logger.debug(f"User response status: {user_response.status_code}")

        if user_response.status_code != status_codes.HTTP_200_OK:
            return ApiResponse.not_found("用户不存在")
        
        try:
            response_data = json.loads(user_response.description)
            logger.debug(f"Response data: {response_data}")

            if not isinstance(response_data, dict):
                logger.error("Response data is not a dictionary")
                return ApiResponse.error(message="响应数据格式错误", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

            if "data" not in response_data:
                logger.error("No 'data' field in response")
                return ApiResponse.error(message="响应数据格式错误", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

            user_data = response_data["data"]
            logger.debug(f"User data: {user_data}")

            if not isinstance(user_data, dict):
                logger.error("User data is not a dictionary")
                return ApiResponse.error(message="用户数据格式错误", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

            try:
                cached_data = await Cache.get(f"registration:{email}")
                if not cached_data:
                    logger.warning(f"No registration data found for email: {email}")
                    return ApiResponse.error("验证码已过期")
                    
                if code != cached_data['code']:
                    logger.warning(f"Invalid verification code for email: {email}")
                    return ApiResponse.error("验证码错误")
                    
                    
            except Exception as e:
                logger.error(f"Error retrieving registration data from cache: {str(e)}")
                return ApiResponse.error("验证码验证失败")
            
            
            change_password = await update_user_field_by_email(email, password)
            if not change_password:
                logger.warning(f"change password failed")
                return ApiResponse.error("修改密码失败")
            
            logger.info(f"change password success")


            # 获取用户IP地址
            ip_address = request.headers.get("X-Real-IP") or request.headers.get("X-Forwarded-For") or request.ip_addr
            
            # 更新用户IP地址
            async with AsyncSessionLocal() as db:
                user = await crud.get_user_by_filter(db, {"email": user_data["email"]})
                if user:
                    await crud.update_user(db, user.user_id, {"ip_address": ip_address, "last_login": datetime.utcnow()})
                    logger.info(f"Updated user {user.username} IP address to {ip_address}")
            
            # 生成Token
            token_data = {
                "user_id": user_data["user_id"],
                "username": user_data["username"],
                "is_admin": user_data.get("is_admin", False),
                "is_active": True
            }
            
            # 创建访问令牌和刷新令牌
            access_token = TokenService.create_access_token(token_data)
            # refresh_token = TokenService.create_refresh_token(token_data)

            # 创建响应
            response = ApiResponse.success(
                message="登录成功",
                data={
                    "user_id": user_data["user_id"],
                    "username": user_data["username"],
                    "is_admin": user_data.get("is_admin", False),
                    "is_active": True,
                    "access_token": access_token,
                    "ip_address": ip_address
                }
            )
            
            # 设置访问令牌到HttpOnly Cookie
            response.headers["Set-Cookie"] = (
                f"access_token=Bearer {access_token}; "
                f"HttpOnly; Secure; Path=/; SameSite=Strict; "
                f"Max-Age={30*60}"  # 30分钟
            )

            return response

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding user data: {str(e)}")
            return ApiResponse.error(message="用户数据解析失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Error processing user login: {str(e)}")
        return ApiResponse.error(message="登录处理失败", status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)

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
                "username": payload["username"],
                "is_admin": payload.get("is_admin", False),
                "is_active": True
            }
            new_access_token = TokenService.create_access_token(token_data)
            
            # 创建响应
            response = ApiResponse.success(
                message="令牌已自动续期",
                data={
                    "user_id": payload["user_id"],
                    "username": payload["username"],
                    "is_admin": payload.get("is_admin", False),
                    "is_active": True
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

async def logout_user(request):
    """
    退出登录
    """
    try:
        # 获取当前令牌
        token = get_token_from_request(request)
        payload = TokenService.decode_token(token)
        user_id = payload.get("user_id")
        async with AsyncSessionLocal() as db:
            try:
                await crud.update_user(db, user_id, {"is_active": False})
            except Exception as e:
                logger.error(f"Error updating user status: {str(e)}")
        
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

async def get_user_ip_history(request):
    """
    获取用户IP地址历史
    """
    try:
        user_id = request.path_params.get("user_id")
        
        async with AsyncSessionLocal() as db:
            user = await crud.get_user(db, user_id)
            if not user:
                return ApiResponse.not_found("用户不存在")
            
            # 构建IP地址历史信息
            ip_history = {
                "user_id": user.user_id,
                "current_ip": user.ip_address,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "user_info": {
                    "username": user.username,
                    "is_admin": user.is_admin,
                    "is_active": True
                }
            }
            
            logger.info(f"Retrieved IP history for user {user.username}")
            return ApiResponse.success(
                data=ip_history,
                message="获取用户IP历史成功"
            )
            
    except Exception as e:
        logger.error(f"Error getting user IP history: {str(e)}")
        return ApiResponse.error(
            message="获取用户IP历史失败",
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def register_precheck_and_send_verification(request):
    """
    注册预检并发送验证码
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
        required_fields = ['username', 'email']
        # required_fields = ['email']
        
        for field in required_fields:
            if field not in user_data:
                logger.warning(f"Missing required field: {field}")
                return ApiResponse.validation_error(f"缺少必填字段: {field}")
        
        username = user_data['username']
        email = user_data['email']
        # phone = user_data['phone']
        
        
        # 检查用户名是否已存在
        # try:
        #     if await crud.check_username_exists(username):
        #         logger.warning(f"Username already exists: {username}")
        #         return ApiResponse.validation_error("用户名已存在")
        # except Exception as e:
        #     logger.error(f"Error checking username existence: {str(e)}")
        #     return ApiResponse.error("用户名检查失败")
            
        # 检查邮箱是否已存在
        try:
            if await crud.check_email_exists(email):
                logger.warning(f"Email already exists: {email}")
                return ApiResponse.validation_error("该邮箱已被注册")
            elif await crud.check_username_exists(username):
                logger.warning(f"Username already exists: {username}")
                return ApiResponse.validation_error("该用户名已被注册，请换个用户名吧~")
        except Exception as e:
            logger.error(f"Error checking email existence: {str(e)}")
            return ApiResponse.error("邮箱检查失败")
            
        # 检查手机号是否已存在
        # try:
        #     if await crud.check_phone_exists(phone):
        #         logger.warning(f"Phone number already exists: {phone}")
        #         return ApiResponse.validation_error("手机号已被注册")
        # except Exception as e:
        #     logger.error(f"Error checking phone existence: {str(e)}")
        #     return ApiResponse.error("手机号检查失败")
            
        # 生成验证码
        from apps.users.utils import generate_numeric_verification_code, send_verification_email
        code = generate_numeric_verification_code()
        logger.debug(f"Generated verification code for {username}: {email}: {code}")
        
        # 缓存验证码和用户数据
        try:
            cache_data = {
                'code': code,
                'user_data': {
                    'username': username,
                    'email': email
                    # 'phone': phone,
                    # 'password': user_data['password']
                }
            }
            await Cache.set(f"registration:{username}", cache_data, expire=300)  # 5分钟过期
            logger.info(f"Verification code and user data cached for {username}: {email}")
        except Exception as e:
            logger.error(f"Failed to cache verification data: {str(e)}")
            return ApiResponse.error("验证数据缓存失败")
            
        # 发送验证码邮件
        try:
            email_sent = await send_verification_email(email, code, username)
            if not email_sent:
                logger.error("Failed to send verification email")
                return ApiResponse.error("验证码发送失败")
        except Exception as e:
            logger.error(f"Error sending verification email: {str(e)}")
            return ApiResponse.error("验证码发送失败")
            
        logger.info("Registration precheck completed successfully")
        return ApiResponse.success("验证码已发送")
        
    except Exception as e:
        logger.error(f"Registration precheck failed: {str(e)}")
        return ApiResponse.error("注册预检失败")

async def verify_and_register(request: Request) -> Response:
    """
    验证码验证并注册用户，注册成功后自动登录
    """
    try:
        logger.info("Starting verification and registration process")
        
        # 获取请求数据
        try:
            request_data = request.json()
            logger.debug(f"Received verification request: {request_data}")
        except Exception as e:
            logger.error(f"Error parsing JSON data: {str(e)}")
            return ApiResponse.validation_error("无效的 JSON 格式")
            
        email = request_data.get('email')
        username = request_data.get('username')
        code = request_data.get('code')

        
        if not email or not code:
            logger.warning("Missing email or verification code")
            return ApiResponse.validation_error("邮箱和验证码不能为空")
            
        # 从Redis获取验证码和用户数据
        try:
            cached_data = await Cache.get(f"registration:{username}")
            if not cached_data:
                logger.warning(f"No registration data found for email: {username}:{email}")
                return ApiResponse.error("验证码已过期")
                
            if code != cached_data['code']:
                logger.warning(f"Invalid verification code for email: {username}:{email}")
                return ApiResponse.error("验证码错误")
                
            user_data = cached_data['user_data']
                
        except Exception as e:
            logger.error(f"Error retrieving registration data from cache: {str(e)}")
            return ApiResponse.error("验证码验证失败")
        
            
        # 创建用户
        try:
            # 确保密码被正确加密
            user_data['password'] = get_password_hash(request_data['password'])
            user_data['user_id'] = generate_user_id()
            username = user_data['username']
            # 获取用户IP地址
            ip_address = request.headers.get("X-Real-IP") or request.headers.get("X-Forwarded-For") or request.ip_addr
            user_data['ip_address'] = ip_address
            user_data['last_login'] = datetime.utcnow()
            user_data['is_admin'] = False  # 默认设置为普通用户
            
            async with AsyncSessionLocal() as db:
                try:
                    # 再次检查用户是否已存在
                    existing_user_email = await crud.get_user_by_filter(db, {"email": email})
                    existing_user_username = await crud.get_user_by_filter(db, {"username": username})
                    if existing_user_email:
                        logger.warning(f"User already exists with email: {email}")
                        return ApiResponse.error(f"邮箱{email}已被注册")
                    elif existing_user_username:
                        logger.warning(f"User already exists with username: {username}")
                        return ApiResponse.error(f"用户名{username}已存在")
                        
                    new_user = await crud.create_user(db, user_data)
                    logger.info(f"Created new user with ID: {new_user.user_id if new_user else 'None'}")

                    if new_user and new_user.user_id:
                        # 删除注册缓存数据
                        try:
                            cache_deleted = await Cache.delete(f"registration:{username}")
                            if not cache_deleted:
                                logger.warning(f"Failed to delete registration cache for username: {username}")
                        except Exception as cache_error:
                            logger.error(f"Error deleting registration cache: {str(cache_error)}")
                        
                        # 生成Token
                        token_data = {
                            "user_id": new_user.user_id,
                            "username": new_user.username,
                            "is_admin": new_user.is_admin, 
                            "is_active": True
                        }

                        
                        # 创建访问令牌和刷新令牌
                        access_token = TokenService.create_access_token(token_data)
                        # refresh_token = TokenService.create_refresh_token(token_data)

                        
                        # 创建响应
                        response = ApiResponse.success(
                            message="注册成功并已登录",
                            data={
                                "user_id": new_user.user_id,
                                "username": new_user.username,
                                "is_admin": new_user.is_admin,
                                "is_active": True,
                                "access_token": access_token,
                                "ip_address": ip_address
                            }
                        )
                        
                        # 设置访问令牌到HttpOnly Cookie
                        response.headers["Set-Cookie"] = (
                            f"access_token=Bearer {access_token}; "
                            f"HttpOnly; Secure; Path=/; SameSite=Strict; "
                            f"Max-Age={30*60}"  # 30分钟
                        )
                        
                        logger.info(f"User registered and logged in successfully: {email}")
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
                    "username": payload["username"],
                    "is_admin": payload.get("is_admin", False),
                    "is_active": payload.get("is_active", True)
                }
            )
            
            return response
        elif not needs_refresh and payload:
            # 如果不需要续期，返回成功响应
            return ApiResponse.success(message="token生效中，无需续期",
                                       data={
                                            "user_id": payload["user_id"],
                                            "username": payload["username"],
                                            "is_admin": payload.get("is_admin", False),
                                            "is_active": payload.get("is_active", True)
                                        })
                                    
    except Exception as e:
        logger.error(f"Error checking token refresh: {str(e)}")
        response = ApiResponse.error(f"查询失败")
        return response

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
                "username": payload["username"],
                "is_admin": payload.get("is_admin", False),
                "is_active": True
            }
            new_access_token = TokenService.create_access_token(token_data)
            
            # 创建响应
            response = ApiResponse.success(
                message="令牌刷新成功",
                data={
                    "user_id": payload["user_id"],
                    "username": payload["username"],
                    "is_admin": payload.get("is_admin", False),
                    "is_active": payload.get("is_active", True),
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
                                            "username": payload["username"],
                                            "is_admin": payload.get("is_admin", False),
                                            "is_active": payload.get("is_active", True),
                                            "access_token": token
                                        })
                                    
    except Exception as e:
        logger.error(f"无法获取用户信息: {str(e)}")
        response = ApiResponse.error(f"获取用户信息失败")
        return response