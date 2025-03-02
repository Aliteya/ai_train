from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode

start_router = Router()

@start_router.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Пришлите <b>голосовое сообщение</b>",
                        parse_mode=ParseMode.HTML)