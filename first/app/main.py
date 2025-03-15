import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from .utils import create_assist, create_vector_store
from .core import settings, redis_settings
from .handlers import start_router, voice_router, photo_router
from .database import init_db, close_db_connections
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

async def initialize_redis():
    redis = Redis.from_url(redis_settings.get_thread_db())
    return RedisStorage(redis=redis)

async def initialize_bot_and_dispatcher(storage):
    bot = Bot(token=settings.get_bot_settings())
    dp = Dispatcher(storage=storage)
    return bot, dp

async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')
    try:

        logger.info('Starting bot')
        
        storage = await initialize_redis()
        bot, dp = await initialize_bot_and_dispatcher(storage)
        
        await create_assist()
        await create_vector_store()
        await init_db()
        
        dp.include_router(start_router)
        dp.include_router(voice_router)
        dp.include_router(photo_router)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await close_db_connections()

asyncio.run(main())