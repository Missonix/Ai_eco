from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from core.database import Base
import logging

logger = logging.getLogger(__name__)


class User(Base):
    """
    用户模型，用于定义用户表
    """
    __tablename__ = 'users'
    
    user_id = Column(String(20), primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    nickname = Column(String(50), index=True, default='undefined', nullable=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    password = Column(String(255), nullable=False) # 密码
    is_admin = Column(Boolean, default=False) # 是否是管理员
    is_active = Column(Boolean, default=True) # 是否是激活状态
    is_deleted = Column(Boolean, default=False) # 是否是删除状态
    ip_address = Column(String(45), nullable=True)  # 支持IPv6地址长度
    last_login = Column(DateTime, nullable=True) # 最后登录时间
    created_at = Column(DateTime, default=datetime.utcnow) # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # 更新时间
    # 用户等级
    level = Column(Integer, default=0)
    # 使用次数
    usage_count = Column(Integer, default=0)

    def __repr__(self):
        return (f"User(user_id={self.user_id}, username={self.username}, nickname={self.nickname}, email={self.email}, "
                f"phone={self.phone}, password={self.password}, is_active={self.is_active}, is_admin={self.is_admin}, "
                f"created_at={self.created_at}, updated_at={self.updated_at}, is_deleted={self.is_deleted}, "
                f"ip_address={self.ip_address}, last_login={self.last_login}, level={self.level}, usage_count={self.usage_count})")

    def to_dict(self):
        """转换为字典"""
        try:
            return {
                "user_id": self.user_id,
                "username": self.username,
                "nickname": self.nickname,
                "email": self.email,
                "phone": self.phone,
                "password": self.password,  # 确保包含password字段
                "is_admin": self.is_admin,
                "is_active": self.is_active,
                "is_deleted": self.is_deleted,
                "ip_address": self.ip_address,
                "last_login": self.last_login.isoformat() if self.last_login else None,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None,
                "level": self.level,
                "usage_count": self.usage_count
            }
        except Exception as e:
            logger.error(f"Error converting user to dict: {str(e)}")
            return {}
