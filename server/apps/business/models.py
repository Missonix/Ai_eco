from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, VARCHAR
from core.database import Base
import logging

logger = logging.getLogger(__name__)


class Courses(Base):
    """
    课程模型，用于定义课程表
    """
    __tablename__ = 'courses'
    
    course_id = Column(String(50), primary_key=True, index=True)
    course_name = Column(VARCHAR(20), unique=True, index=True, nullable=False)
    is_deleted = Column(Boolean, default=False) # 是否是删除状态
    created_at = Column(DateTime, default=datetime.utcnow) # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # 更新时间

    def __repr__(self):
        return (f"Courses(course_id={self.course_id}, "
                f"course_name={self.course_name}, "
                f"created_at={self.created_at}, updated_at={self.updated_at}, is_deleted={self.is_deleted}")

    def to_dict(self):
        """转换为字典"""
        try:
            return {
                "course_id": self.course_id,
                "course_name": self.course_name,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            }
        except Exception as e:
            logger.error(f"Error converting course to dict: {str(e)}")
            return {}
        

class Ai_products(Base):
    """
    AI产品模型，用于定义AI产品表
    """
    __tablename__ = 'ai_products'

    ai_product_id = Column(String(50), primary_key=True, index=True) # ai产品id，唯一 主键
    ai_product_name = Column(VARCHAR(20), nullable=False) # ai产品名称
    created_at = Column(DateTime, default=datetime.utcnow) # 创建时间
    is_deleted = Column(Boolean, default=False) # 是否删除(逻辑删除)

    def __repr__(self):
        return (f"Ai_products(ai_product_id={self.ai_product_id}, "
                f"ai_product_name={self.ai_product_name}, "
                f"created_at={self.created_at}, is_deleted={self.is_deleted}")
    
    def to_dict(self):
        """转换为字典"""
        try:
            return {
                "ai_product_id": self.ai_product_id,
                "ai_product_name": self.ai_product_name,
                "created_at": self.created_at.isoformat() if self.created_at else None
            }
        except Exception as e:
            logger.error(f"Error converting ai_product to dict: {str(e)}")
            return {}
        
class Entitlement_rules(Base):
    """
    权益规则模型，用于定义权益规则表
    """
    __tablename__ = 'entitlement_rules'
    
    rule_id = Column(String(50), primary_key=True, index=True) # 权益id，唯一 主键
    course_id = Column(String(50), nullable=False) # 关联课程ID
    course_name = Column(VARCHAR(50), nullable=False) # 关联课程名称
    ai_product_id = Column(String(50), nullable=False) # 关联AI产品ID
    product_name = Column(VARCHAR(20), nullable=False) # 权益产品名称
    daily_limit = Column(Integer, nullable=False, default=5) # 每日使用上限
    validity_days = Column(Integer, nullable=False, default=30) # 权益有效期（天）外键
    created_at = Column(DateTime, default=datetime.utcnow) # 创建时间
    is_deleted = Column(Boolean, default=False) # 是否删除(逻辑删除)
    
    def __repr__(self):
        return (f"Entitlement_rules(rule_id={self.rule_id}, "
                f"course_id={self.course_id}, "
                f"course_name={self.course_name}, "
                f"ai_product_id={self.ai_product_id}, "
                f"product_name={self.product_name}, "
                f"daily_limit={self.daily_limit}, "
                f"validity_days={self.validity_days}, "
                f"created_at={self.created_at}, is_deleted={self.is_deleted}")
    
    def to_dict(self):
        """转换为字典"""
        try:
            return {
                "rule_id": self.rule_id,
                "course_id": self.course_id,
                "course_name": self.course_name,
                "ai_product_id": self.ai_product_id,
                "product_name": self.product_name,
                "daily_limit": self.daily_limit,
                "validity_days": self.validity_days,
                "created_at": self.created_at.isoformat() if self.created_at else None
            }
        except Exception as e:
            logger.error(f"Error converting user to dict: {str(e)}")
            return {}
        
class Orders(Base):
    """
    订单模型，用于定义订单表
    """
    __tablename__ = 'orders'

    order_id = Column(String(50), primary_key=True, index=True) # 生成的订单id，唯一 主键
    phone = Column(VARCHAR(20), nullable=False) # 用户手机号
    course_id = Column(String(50), nullable=False) # 课程ID
    purchase_time = Column(String(50), nullable=False) # 购买时间
    is_refund = Column(Boolean, default=False) # 是否退款
    is_generate = Column(Boolean, default=False) # 是否生成权益
    created_at = Column(DateTime, default=datetime.utcnow) # 创建时间
    is_deleted = Column(Boolean, default=False) # 是否删除(逻辑删除)
    
    def __repr__(self):
        return (f"Orders(order_id={self.order_id}, "
                f"phone={self.phone}, "
                f"course_id={self.course_id}, "
                f"purchase_time={self.purchase_time}, "
                f"is_refund={self.is_refund}, "
                f"is_generate={self.is_generate}, "
                f"created_at={self.created_at}, is_deleted={self.is_deleted}")
    
    def to_dict(self):
        """转换为字典"""
        try:
            return {
                "order_id": self.order_id,
                "phone": self.phone,
                "course_id": self.course_id,
                "purchase_time": self.purchase_time,  # 直接返回字符串
                "is_refund": self.is_refund,
                "is_generate": self.is_generate,
                "created_at": self.created_at.isoformat() if self.created_at else None
            }
        except Exception as e:
            logger.error(f"Error converting order to dict: {str(e)}")
            return {}
    
class User_entitlements(Base):
    """
    用户权益模型，用于定义用户权益表
    """
    __tablename__ = 'user_entitlements'

    entitlement_id = Column(String(50), primary_key=True, index=True) # 用户权益id，唯一 主键
    phone = Column(VARCHAR(20), nullable=False) # 用户手机号
    rule_id = Column(String(50), nullable=False) # 权益规则ID
    course_name = Column(VARCHAR(20), nullable=False) # 关联课程名称
    product_name = Column(VARCHAR(20), nullable=False) # 权益产品名称
    ai_product_id = Column(VARCHAR(50), nullable=True)  # 新增字段
    start_date = Column(DateTime, nullable=False) # 权益生效日期
    end_date = Column(DateTime, nullable=False) # 权益失效日期
    is_active = Column(Boolean, default=False) # 是否激活
    created_at = Column(DateTime, default=datetime.utcnow) # 创建时间
    daily_remaining = Column(Integer, nullable=False) # 当日剩余次数
    is_deleted = Column(Boolean, default=False) # 是否删除(逻辑删除)
    
    def __repr__(self):
        return (f"User_entitlements(entitlement_id={self.entitlement_id}, "
                f"phone={self.phone}, "
                f"rule_id={self.rule_id}, "
                f"course_name={self.course_name}, "
                f"ai_product_id={self.ai_product_id},"
                f"product_name={self.product_name}, "
                f"start_date={self.start_date}, "
                f"end_date={self.end_date}, "
                f"is_active={self.is_active}, "
                f"created_at={self.created_at}, "
                f"daily_remaining={self.daily_remaining}, "
                f"is_deleted={self.is_deleted}")
    
    def to_dict(self):
        """转换为字典"""
        try:
            return {
                "entitlement_id": self.entitlement_id,
                "phone": self.phone,
                "rule_id": self.rule_id,
                "course_name": self.course_name,
                "product_name": self.product_name,
                "ai_product_id": self.ai_product_id,
                "start_date": self.start_date.isoformat() if self.start_date else None,
                "end_date": self.end_date.isoformat() if self.end_date else None,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "daily_remaining": self.daily_remaining,
                "is_active": self.is_active
            }
        except Exception as e:
            logger.error(f"Error converting user to dict: {str(e)}")
            return {}
        
class Upload_error_orders(Base):
    """
    订单批量上传失败模型，用于定义订单批量上传失败表
    """
    __tablename__ = 'upload_error_orders'
    
    id = Column(Integer, primary_key=True, index=True) # 主键
    order_id = Column(String(50), nullable=False) # 订单ID
    error_message = Column(String(255), nullable=False) # 错误信息
    created_at = Column(DateTime, default=datetime.utcnow) # 创建时间
    is_deleted = Column(Boolean, default=False) # 是否删除(逻辑删除)
    
    def __repr__(self):
        return (f"Upload_error_orders(id={self.id}, "
                f"order_id={self.order_id}, "
                f"error_message={self.error_message}, "
                f"created_at={self.created_at}, is_deleted={self.is_deleted}")
        
    def to_dict(self):
        """转换为字典"""
        try:
            return {
                "id": self.id,
                "order_id": self.order_id,
                "error_message": self.error_message,
                "created_at": self.created_at.isoformat() if self.created_at else None
            }
        except Exception as e:
            logger.error(f"Error converting upload_error_orders to dict: {str(e)}")
            return {}

# 批量生成权益错误模型
class Batch_generate_entitlements_error(Base):
    """
    批量生成权益失败模型，用于定义批量生成权益失败表
    """
    __tablename__ = 'batch_generate_entitlements_error'
    
    id = Column(Integer, primary_key=True, index=True) # 主键
    order_id = Column(String(50), nullable=False) # 订单ID
    error_message = Column(String(255), nullable=False) # 错误信息
    created_at = Column(DateTime, default=datetime.utcnow) # 创建时间
    is_deleted = Column(Boolean, default=False) # 是否删除(逻辑删除)
    
    def __repr__(self):
        return (f"Batch_generate_entitlements_error(id={self.id}, "
                f"order_id={self.order_id}, "
                f"error_message={self.error_message}, "
                f"created_at={self.created_at}, is_deleted={self.is_deleted}")
    
    def to_dict(self):
        """转换为字典"""
        try:
            return {
                "id": self.id,
                "order_id": self.order_id,
                "error_message": self.error_message,
                "created_at": self.created_at.isoformat() if self.created_at else None
            }
        except Exception as e:
            logger.error(f"Error converting batch_generate_entitlements_error to dict: {str(e)}")
            return {}
    


