from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, VARCHAR
from core.database import Base
import logging

logger = logging.getLogger(__name__)


class User(Base):
    """
    用户模型，用于定义用户表
    """
    __tablename__ = 'users'
    
    user_id = Column(String(20), primary_key=True, index=True)
    phone = Column(VARCHAR(20), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False) # 密码
    is_deleted = Column(Boolean, default=False) # 是否是删除状态
    last_login = Column(DateTime, nullable=True) # 最后登录时间
    created_at = Column(DateTime, default=datetime.utcnow) # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # 更新时间

    def __repr__(self):
        return (f"User(user_id={self.user_id}, "
                f"phone={self.phone}, password={self.password}, "
                f"created_at={self.created_at}, updated_at={self.updated_at}, is_deleted={self.is_deleted}, "
                f"last_login={self.last_login})")

    def to_dict(self):
        """转换为字典"""
        try:
            return {
                "user_id": self.user_id,
                "phone": self.phone,
                "password": self.password,  # 确保包含password字段
                "is_deleted": self.is_deleted,
                "last_login": self.last_login.isoformat() if self.last_login else None,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            }
        except Exception as e:
            logger.error(f"Error converting user to dict: {str(e)}")
            return {}
