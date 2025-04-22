from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import func
from core.database import AsyncSessionLocal
from core.logger import setup_logger
from apps.business.models import Courses, Entitlement_rules, Orders, User_entitlements
from common.utils.dynamic_query import dynamic_query

# 设置日志记录器
logger = setup_logger('business_crud')

"""
    定义CRUD操作, 解耦API和数据库操作
    只定义 单表的基础操作 和 动态查询功能
    CRUD层函数 返回值一律为 ORM实例对象
"""


# 课程表操作
async def get_course(db: AsyncSession, course_id: str):
    """
    根据课程ID获取单个课程
    """
    return await db.get(Courses, course_id)

async def get_courses(db: AsyncSession):
    """
    获取所有课程
    """
    return await db.execute(select(Courses))

async def create_course(db: AsyncSession, course: dict):
    """
    创建课程
    """
    new_course = Courses(**course)
    db.add(new_course)
    await db.commit()
    await db.refresh(new_course)
    return new_course

async def update_course(db: AsyncSession, course_id: str, course_data: dict):
    """
    更新课程
    """
    course = await db.get(Courses, course_id)
    if course is None:
        raise Exception("User not found")
    
    for key, value in course_data.items():
        setattr(course, key, value)
    
    await db.commit()
    await db.refresh(course)
    return course

async def delete_course(db: AsyncSession, course_id: str):
    """
    删除课程
    """
    target_course = await db.get(Courses, course_id)
    if target_course is None:
        raise Exception("Course not found")
    
    await db.delete(target_course)
    await db.commit()
    return target_course

# 动态查询
async def get_course_by_filter(db: AsyncSession, filters: dict):
    """
    根据过滤条件查询课程
    """
    query = await dynamic_query(db, Courses, filters)
    result = await db.execute(query)
    # 返回第一条完整记录（ORM 对象）
    # return result.first()
    course = result.scalar_one_or_none()
    return course

async def get_courses_by_filters(db: AsyncSession, filters=None, order_by=None, page: int = 1, page_size: int = 10):
    """
    批量查询课程，支持分页
    :param db: 数据库会话
    :param filters: 过滤条件
    :param order_by: 排序条件，如 {"created_at": "desc"}
    :param page: 页码，从1开始
    :param page_size: 每页数量
    :return: (课程列表, 总记录数)
    """
    try:
        # 构建基础查询
        query = await dynamic_query(db, Courses, filters, order_by)
        
        # 计算总记录数
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()
        
        # 添加分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # 执行查询
        result = await db.execute(query)
        courses = result.scalars().all()
        
        return courses, total_count
    except Exception as e:
        logger.error(f"查询课程列表失败: {str(e)}")
        raise

async def check_course_exists(course_id: str) -> bool:
    """
    检查课程是否已存在
    :param course_id: 课程ID
    :return: 是否存在
    """
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Courses).where(Courses.course_id == course_id)
            )
            course = result.scalar_one_or_none()
            return course is not None
    except Exception as e:
        logger.error(f"Error checking course existence: {str(e)}")
        raise




from apps.business.models import Ai_products

# AI产品表操作
async def get_ai_product(db: AsyncSession, ai_product_id: str):
    """
    根据AI产品ID获取单个AI产品
    """
    return await db.get(Ai_products, ai_product_id)

async def get_ai_products(db: AsyncSession):
    """
    获取所有AI产品
    """
    return await db.execute(select(Ai_products))

async def create_ai_product(db: AsyncSession, ai_product: dict):
    """
    创建AI产品
    """
    new_ai_product = Ai_products(**ai_product)
    db.add(new_ai_product)
    await db.commit()
    await db.refresh(new_ai_product)
    return new_ai_product

async def update_ai_product(db: AsyncSession, ai_product_id: str, ai_product_data: dict):
    """
    更新AI产品
    """
    ai_product = await db.get(Ai_products, ai_product_id)
    if ai_product is None:
        raise Exception("User not found")
    
    for key, value in ai_product_data.items():
        setattr(ai_product, key, value)
    
    await db.commit()
    await db.refresh(ai_product)
    return ai_product

async def delete_course(db: AsyncSession, ai_product_id: str):
    """
    删除AI产品
    """
    target_ai_product = await db.get(Ai_products, ai_product_id)
    if target_ai_product is None:
        raise Exception("Course not found")
    
    await db.delete(target_ai_product)
    await db.commit()
    return target_ai_product

# 动态查询
async def get_ai_product_by_filter(db: AsyncSession, filters: dict):
    """
    根据过滤条件查询AI产品
    """
    query = await dynamic_query(db, Ai_products, filters)
    result = await db.execute(query)
    # 返回第一条完整记录（ORM 对象）
    # return result.first()
    ai_product = result.scalar_one_or_none()
    return ai_product

async def get_ai_products_by_filters(db: AsyncSession, filters=None, order_by=None, page: int = 1, page_size: int = 10):
    """
    批量查询AI产品，支持分页
    :param db: 数据库会话
    :param filters: 过滤条件
    :param order_by: 排序条件，如 {"created_at": "desc"}
    :param page: 页码，从1开始
    :param page_size: 每页数量
    :return: (AI产品列表, 总记录数)
    """
    try:
        # 构建基础查询
        query = await dynamic_query(db, Ai_products, filters, order_by)
        
        # 计算总记录数
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()
        
        # 添加分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # 执行查询
        result = await db.execute(query)
        ai_products = result.scalars().all()
        
        return ai_products, total_count
    except Exception as e:
        logger.error(f"查询AI产品列表失败: {str(e)}")
        raise

async def check_ai_product_exists(ai_product_id: str) -> bool:
    """
    检查AI产品是否已存在
    :param ai_product_id: AI产品ID
    :return: 是否存在
    """
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Ai_products).where(Ai_products.ai_product_id == ai_product_id)
            )
            ai_product = result.scalar_one_or_none()
            return ai_product is not None
    except Exception as e:
        logger.error(f"Error checking ai_product existence: {str(e)}")
        raise




# 权益规则表操作
async def get_entitlement_rule(db: AsyncSession, rule_id: str):
    """
    根据权益规则ID获取单个权限规则
    """
    return await db.get(Entitlement_rules, rule_id)

async def create_entitlement_rule(db: AsyncSession, entitlement_rule: dict):
    """
    创建权益规则
    """
    new_entitlement_rule = Entitlement_rules(**entitlement_rule)
    db.add(new_entitlement_rule)
    await db.commit()
    await db.refresh(new_entitlement_rule)
    return new_entitlement_rule

async def update_entitlement_rule(db: AsyncSession, rule_id: str, entitlement_rule_data: dict):
    """
    更新权益规则
    """
    entitlement_rule = await db.get(Entitlement_rules, rule_id)
    if entitlement_rule is None:
        raise Exception("Entitlement rule not found")
    
    for key, value in entitlement_rule_data.items():
        setattr(entitlement_rule, key, value)
    
    await db.commit()
    await db.refresh(entitlement_rule)
    return entitlement_rule

async def delete_entitlement_rule(db: AsyncSession, rule_id: str):
    """
    删除权益规则
    """
    target_entitlement_rule = await db.get(Entitlement_rules, rule_id)
    if target_entitlement_rule is None:
        raise Exception("Entitlement rule not found")
    
    await db.delete(target_entitlement_rule)
    await db.commit()
    return target_entitlement_rule

# 动态查询
async def get_entitlement_rule_by_filter(db: AsyncSession, filters: dict):
    """
    根据过滤条件查询权益规则
    """
    query = await dynamic_query(db, Entitlement_rules, filters)
    result = await db.execute(query)
    # 返回第一条完整记录（ORM 对象）
    # return result.first()
    entitlement_rule = result.scalar_one_or_none()
    return entitlement_rule


async def get_entitlement_rules_by_filters(db: AsyncSession, filters=None, order_by=None, limit=None, offset=None):
    """
    批量查询权益规则
    """
    query = await dynamic_query(db, Entitlement_rules, filters, order_by, limit, offset)
    result = await db.execute(query)
    # 返回所有完整记录（ORM 对象列表）
    return result.scalars().all()

async def check_entitlement_rule_exists(rule_id: str) -> bool:
    """
    检查权益规则是否已存在
    :param rule_id: 权益规则ID
    :return: 是否存在
    """
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Entitlement_rules).where(Entitlement_rules.rule_id == rule_id)
            )
            entitlement_rule = result.scalar_one_or_none()
            return entitlement_rule is not None
    except Exception as e:
        logger.error(f"Error checking entitlement rule existence: {str(e)}")
        raise




# 订单表操作
async def get_order(db: AsyncSession, order_id: str):
    """
    根据订单ID获取单个订单
    """
    return await db.get(Orders, order_id)

async def create_order(db: AsyncSession, order: dict):
    """
    创建订单
    """
    new_order = Orders(**order)
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    return new_order

async def update_order(db: AsyncSession, order_id: str, order_data: dict):
    """
    更新订单
    """
    order = await db.get(Orders, order_id)
    if order is None:
        raise Exception("Order not found")
    
    for key, value in order_data.items():
        setattr(order, key, value)
    
    await db.commit()
    await db.refresh(order)
    return order

async def delete_order(db: AsyncSession, order_id: str):
    """
    删除订单
    """
    target_order = await db.get(Orders, order_id)
    if target_order is None:
        raise Exception("Order not found")
    
    await db.delete(target_order)
    await db.commit()
    return target_order

# 动态查询
async def get_order_by_filter(db: AsyncSession, filters: dict):
    """
    根据过滤条件查询订单
    """
    query = await dynamic_query(db, Orders, filters)
    result = await db.execute(query)
    # 返回第一条完整记录（ORM 对象）
    # return result.first()
    order = result.scalar_one_or_none()
    return order


async def get_orders_by_filters(db: AsyncSession, filters=None, order_by=None, page: int = 1, page_size: int = 10):
    """
    批量查询订单，支持分页
    :param db: 数据库会话
    :param filters: 过滤条件
    :param order_by: 排序条件，如 {"created_at": "desc"}
    :param page: 页码，从1开始
    :param page_size: 每页数量
    :return: (订单列表, 总记录数)
    """
    try:
        # 构建基础查询
        query = await dynamic_query(db, Orders, filters, order_by)
        
        # 计算总记录数
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()
        
        # 添加分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # 执行查询
        result = await db.execute(query)
        orders = result.scalars().all()
        
        return orders, total_count
    except Exception as e:
        logger.error(f"查询订单列表失败: {str(e)}")
        raise

async def check_order_exists(order_id: str) -> bool:
    """
    检查订单是否已存在
    :param order_id: 订单ID
    :return: 是否存在
    """
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Orders).where(Orders.order_id == order_id)
            )
            order = result.scalar_one_or_none()
            return order is not None
    except Exception as e:
        logger.error(f"Error checking order existence: {str(e)}")
        raise




# 用户权益表操作
async def get_user_entitlement(db: AsyncSession, entitlement_id: str):
    """
    根据用户权益ID获取单个用户权益
    """
    return await db.get(User_entitlements, entitlement_id)

async def create_user_entitlement(db: AsyncSession, user_entitlement: dict):
    """
    创建用户权益
    """
    new_user_entitlement = User_entitlements(**user_entitlement)
    db.add(new_user_entitlement)
    await db.commit()
    await db.refresh(new_user_entitlement)
    return new_user_entitlement

async def update_user_entitlement(db: AsyncSession, entitlement_id: str, user_entitlement_data: dict):
    """
    更新用户权益
    """
    user_entitlement = await db.get(User_entitlements, entitlement_id)
    if user_entitlement is None:
        raise Exception("User entitlement not found")
    
    for key, value in user_entitlement_data.items():
        setattr(user_entitlement, key, value)
    
    await db.commit()
    await db.refresh(user_entitlement)
    return user_entitlement

async def delete_user_entitlement(db: AsyncSession, entitlement_id: str):
    """
    删除用户权益
    """
    target_user_entitlement = await db.get(User_entitlements, entitlement_id)
    if target_user_entitlement is None:
        raise Exception("User entitlement not found")
    
    await db.delete(target_user_entitlement)
    await db.commit()
    return target_user_entitlement

# 动态查询
async def get_user_entitlement_by_filter(db: AsyncSession, filters: dict):
    """
    根据过滤条件查询用户权益
    """
    query = await dynamic_query(db, User_entitlements, filters)
    result = await db.execute(query)
    # 返回第一条完整记录（ORM 对象）
    # return result.first()
    user_entitlement = result.scalar_one_or_none()
    return user_entitlement


async def get_user_entitlements_by_filters(db: AsyncSession, filters=None, order_by=None, page: int = 1, page_size: int = 10):
    """
    批量查询用户权益，支持分页
    :param db: 数据库会话
    :param filters: 过滤条件
    :param order_by: 排序条件，如 {"created_at": "desc"}
    :param page: 页码，从1开始
    :param page_size: 每页数量
    :return: (用户权益列表, 总记录数)
    """
    try:
        # 构建基础查询
        query = await dynamic_query(db, User_entitlements, filters, order_by)
        
        # 计算总记录数
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()
        
        # 添加分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # 执行查询
        result = await db.execute(query)
        entitlements = result.scalars().all()
        
        return entitlements, total_count
    except Exception as e:
        logger.error(f"查询用户权益列表失败: {str(e)}")
        raise

async def check_user_entitlement_exists(entitlement_id: str) -> bool:
    """
    检查用户权益是否已存在
    :param entitlement_id: 用户权益ID
    :return: 是否存在
    """
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(User_entitlements).where(User_entitlements.entitlement_id == entitlement_id)
            )
            user_entitlement = result.scalar_one_or_none()
            return user_entitlement is not None
    except Exception as e:
        logger.error(f"Error checking user entitlement existence: {str(e)}")
        raise
