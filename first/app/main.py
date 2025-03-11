import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from .utils import create_assist
from .core import settings 
from .handlers import start_router, voice_router, photo_router
from .database import init_db, close_db_connections


logger = logging.getLogger(__name__)



async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')
    try:
        logger.info('Starting bot')
        bot = Bot(token=settings.get_bot_settings())
        dp = Dispatcher()

        await create_assist()
        await init_db()
        dp.include_router(start_router)
        dp.include_router(voice_router)
        dp.include_router(photo_router)

        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await close_db_connections()

asyncio.run(main())