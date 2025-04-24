from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from core.database import AsyncSessionLocal
from core.logger import setup_logger
from apps.users.models import User, Admin
from common.utils.dynamic_query import dynamic_query

# 设置日志记录器
logger = setup_logger('user_crud')

"""
    定义用户CRUD操作, 解耦API和数据库操作
    只定义 单表的基础操作 和 动态查询功能
    CRUD层函数 返回值一律为 ORM实例对象
"""

# 单表基础操作
async def get_user(db: AsyncSession, user_id: str):
    """
    根据用户ID获取单个用户
    """
    return await db.get(User, user_id)

async def create_user(db: AsyncSession, user: dict):
    """
    创建用户
    """
    new_user = User(**user)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def update_user(db: AsyncSession, user_id: str, user_data: dict):
    """
    更新用户
    """
    user = await db.get(User, user_id)
    if user is None:
        raise Exception("User not found")
    
    for key, value in user_data.items():
        setattr(user, key, value)
    
    await db.commit()
    await db.refresh(user)
    return user

async def delete_user(db: AsyncSession, user_id: str):
    """
    删除用户
    """
    target_user = await db.get(User, user_id)
    if target_user is None:
        raise Exception("User not found")
    
    await db.delete(target_user)
    await db.commit()
    return target_user

# 动态查询
async def get_user_by_filter(db: AsyncSession, filters: dict):
    """
    根据过滤条件查询用户
    """
    query = await dynamic_query(db, User, filters)
    result = await db.execute(query)
    # 返回第一条完整记录（ORM 对象）
    # return result.first()
    user = result.scalar_one_or_none()
    return user


async def get_users_by_filters(db: AsyncSession, filters=None, order_by=None, limit=None, offset=None):
    """
    批量查询用户
    """
    query = await dynamic_query(db, User, filters, order_by, limit, offset)
    result = await db.execute(query)
    # 返回所有完整记录（ORM 对象列表）
    return result.scalars().all()

async def check_phone_exists(phone: str) -> bool:
    """
    检查手机号是否已存在
    :param phone: 手机号
    :return: 是否存在
    """
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(User).where(User.phone == phone)
            )
            user = result.scalar_one_or_none()
            return user is not None
    except Exception as e:
        logger.error(f"Error checking phone existence: {str(e)}")
        raise

# 管理员CRUD操作
async def get_admin(db: AsyncSession, admin_id: str):
    """
    根据管理员ID获取单个管理员
    """
    return await db.get(Admin, admin_id)

async def create_admin(db: AsyncSession, admin: dict):
    """
    创建管理员
    """
    new_admin = Admin(**admin)
    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)
    return new_admin

async def update_admin(db: AsyncSession, admin_id: str, admin_data: dict):
    """
    更新管理员
    """
    admin = await db.get(Admin, admin_id)
    if admin is None:
        raise Exception("Admin not found")
    
    for key, value in admin_data.items():
        setattr(admin, key, value)
    
    await db.commit()
    await db.refresh(admin)
    return admin

async def delete_admin(db: AsyncSession, admin_id: str):
    """
    删除管理员
    """
    target_admin = await db.get(Admin, admin_id)
    if target_admin is None:
        raise Exception("Admin not found")
    
    await db.delete(target_admin)
    await db.commit()
    return target_admin

async def get_admin_by_filter(db: AsyncSession, filters: dict):
    """
    根据过滤条件查询管理员
    """
    query = await dynamic_query(db, Admin, filters)
    result = await db.execute(query)
    # 返回第一条完整记录（ORM 对象）
    admin = result.scalar_one_or_none()
    return admin

async def get_admins_by_filters(db: AsyncSession, filters=None, order_by=None, page: int = 1, page_size: int = 10):
    """
    批量查询管理员，支持分页
    :param db: 数据库会话
    :param filters: 过滤条件
    :param order_by: 排序条件，如 {"created_at": "desc"}
    :param page: 页码，从1开始
    :param page_size: 每页数量
    :return: (管理员列表, 总记录数)
    """
    try:
        # 构建基础查询
        query = await dynamic_query(db, Admin, filters, order_by)
        
        # 计算总记录数
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()
        
        # 添加分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # 执行查询
        result = await db.execute(query)
        admins = result.scalars().all()
        
        return admins, total_count
    except Exception as e:
        logger.error(f"查询管理员列表失败: {str(e)}")
        raise

async def check_admin_exists(admin_id: str) -> bool:
    """
    检查管理员ID是否已存在
    :param admin_id: 管理员ID
    :return: 是否存在
    """
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Admin).where(Admin.admin_id == admin_id)
            )
            admin = result.scalar_one_or_none()
            return admin is not None
    except Exception as e:
        logger.error(f"Error checking admin existence: {str(e)}")
        raise

async def check_username_exists(username: str) -> bool:
    """
    检查管理员用户名是否已存在
    :param username: 管理员用户名
    :return: 是否存在
    """
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Admin).where(Admin.username == username)
            )
            admin = result.scalar_one_or_none()
            return admin is not None
    except Exception as e:
        logger.error(f"Error checking username existence: {str(e)}")
        raise


