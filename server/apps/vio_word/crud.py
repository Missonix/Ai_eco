from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import AsyncSessionLocal
from core.logger import setup_logger
from apps.vio_word.models import Vio_word

# 设置日志记录器
logger = setup_logger('vio_word_crud')

async def create_vio_word(db: AsyncSession, vio_word_data: dict):
    """创建违规词检测记录"""
    try:
        new_vio_word = Vio_word(**vio_word_data)
        db.add(new_vio_word)
        await db.commit()
        await db.refresh(new_vio_word)
        return new_vio_word
    except Exception as e:
        await db.rollback()
        raise e

async def get_vio_word(db: AsyncSession, id: int):
    """获取单个违规词检测记录"""
    return await db.get(Vio_word, id)

async def get_vio_words_by_filters(db: AsyncSession, filters: dict = None, order_by: dict = None, page: int = 1, page_size: int = 10):
    """根据条件查询违规词检测记录"""
    try:
        # 构建基础查询
        query = select(Vio_word).where(Vio_word.is_deleted == False)
        
        # 添加过滤条件
        if filters:
            if "phone" in filters:
                query = query.where(Vio_word.phone == filters["phone"])
            if "is_violation" in filters:
                query = query.where(Vio_word.is_violation == filters["is_violation"])
            if "created_at" in filters:
                query = query.where(Vio_word.created_at == filters["created_at"])
        
        # 添加排序条件
        if order_by:
            for key, value in order_by.items():
                if value.lower() == "desc":
                    query = query.order_by(getattr(Vio_word, key).desc())
                else:
                    query = query.order_by(getattr(Vio_word, key))
        
        # 执行查询
        result = await db.execute(query)
        vio_words = result.scalars().all()
        
        # 计算总记录数
        total_count = len(vio_words)
        
        # 手动分页
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_vio_words = vio_words[start_idx:end_idx]
        
        return paginated_vio_words, total_count
    except Exception as e:
        logger.error(f"查询违规词检测记录失败: {str(e)}")
        raise

async def update_vio_word(db: AsyncSession, id: int, update_data: dict):
    """更新违规词检测记录"""
    try:
        vio_word = await db.get(Vio_word, id)
        if vio_word:
            for key, value in update_data.items():
                setattr(vio_word, key, value)
            await db.commit()
            await db.refresh(vio_word)
        return vio_word
    except Exception as e:
        await db.rollback()
        raise e

async def delete_vio_word(db: AsyncSession, id: int):
    """删除违规词检测记录（软删除）"""
    try:
        vio_word = await db.get(Vio_word, id)
        if vio_word:
            vio_word.is_deleted = True
            await db.commit()
        return vio_word
    except Exception as e:
        await db.rollback()
        raise e 