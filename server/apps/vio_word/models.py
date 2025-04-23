from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, VARCHAR
from core.database import Base
import logging

logger = logging.getLogger(__name__)


class Vio_word(Base):
    """
    AI违规词检测模型，用于定义AI违规词检测表
    """
    __tablename__ = 'vio_word'
    
    id = Column(Integer, primary_key=True, index=True) # 主键
    phone = Column(VARCHAR(20), nullable=False) # 用户手机号
    input = Column(VARCHAR(255), nullable=False) # 输入内容
    is_violation = Column(Boolean, default=False) # 是否违规
    words = Column(VARCHAR(255), nullable=False) # 违规词
    reasons = Column(VARCHAR(255), nullable=False) # 违规原因
    op = Column(VARCHAR(255), nullable=False) # 优化后的话术
    ideas = Column(VARCHAR(255), nullable=False) # 优化建议
    old_score = Column(Integer, nullable=False) # 违规分数
    new_score = Column(Integer, nullable=False) # 优化后分数
    old_rating = Column(VARCHAR(255), nullable=False) # 违规评级
    new_rating = Column(VARCHAR(255), nullable=False) # 优化后评级
    created_at = Column(DateTime, default=datetime.utcnow) # 创建时间
    is_deleted = Column(Boolean, default=False) # 是否删除(逻辑删除)
    
    def __repr__(self):
        return (f"Vio_word(id={self.id}, "
                f"phone={self.phone}, "
                f"input={self.input}, "
                f"is_violation={self.is_violation}, "
                f"words={self.words}, "
                f"reasons={self.reasons}, "
                f"op={self.op}, "
                f"ideas={self.ideas}, "
                f"old_score={self.old_score}, "
                f"new_score={self.new_score}, "
                f"old_rating={self.old_rating}, "
                f"new_rating={self.new_rating}, "
                f"created_at={self.created_at}, "
                f"is_deleted={self.is_deleted}")
    
    def to_dict(self):
        """转换为字典"""
        try:
            return {
                "id": self.id,
                "phone": self.phone,
                "input": self.input,
                "is_violation": self.is_violation,
                "words": self.words,
                "reasons": self.reasons,
                "op": self.op,
                "ideas": self.ideas,
                "old_score": self.old_score,
                "new_score": self.new_score,
                "old_rating": self.old_rating,
                "new_rating": self.new_rating,
                "created_at": self.created_at.isoformat() if self.created_at else None
            }
        except Exception as e:
            logger.error(f"Error converting vio_word to dict: {str(e)}")
            return {}
        
