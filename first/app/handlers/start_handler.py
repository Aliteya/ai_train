from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from ..core import settings
from ..utils import get_thread

start_router = Router()

@start_router.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Пришлите <b>голосовое сообщение</b> или картинку(не документом)",
                        parse_mode=ParseMode.HTML)
    
@start_router.message(Command("new_thread"))
async def new_thread_command(message: Message):
    user_id = message.from_user.id
    thread_id = await get_thread(user_id)
    redis_client = settings.get_thread_db()
    if thread_id:
        redis_client.delete(f"user:{user_id}:thread_id")
        return message.answer("Старый поток удалён. Создаю новый поток.")
    else:
        return message.answer("Поток не найден. Создаю новый поток.")
    
    
