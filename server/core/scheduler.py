import asyncio
import logging
from datetime import datetime, time
from apps.business.services import update_daily_remaining_service

logger = logging.getLogger(__name__)

async def run_at_specific_time(target_time: time, coro):
    """
    在指定时间运行协程
    :param target_time: 目标时间
    :param coro: 要运行的协程
    """
    while True:
        now = datetime.now().time()
        if now >= target_time:
            # 如果当前时间已经超过目标时间，等待到明天
            tomorrow = datetime.now().date() + datetime.timedelta(days=1)
            target_datetime = datetime.combine(tomorrow, target_time)
        else:
            # 否则等待到今天的目标时间
            today = datetime.now().date()
            target_datetime = datetime.combine(today, target_time)
        
        # 计算需要等待的秒数
        wait_seconds = (target_datetime - datetime.now()).total_seconds()
        
        # 等待到目标时间
        await asyncio.sleep(wait_seconds)
        
        try:
            # 执行目标协程
            await coro()
        except Exception as e:
            logger.error(f"定时任务执行失败: {str(e)}")

async def start_scheduler():
    """
    启动调度器，设置所有定时任务
    """
    # 设置每日0:00更新用户权益剩余额度的任务
    midnight = time(0, 0)
    asyncio.create_task(run_at_specific_time(midnight, update_daily_remaining_service))
    logger.info("定时任务调度器已启动") 