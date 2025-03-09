from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from ..utils import save_voice_file, get_transcribtion, ask_question, voice_acting, get_thread
from aiogram.filters import Command
from ..core import settings

voice_router = Router()

@voice_router.message(F.voice)
async def hear_voice(message: Message):
    file_id = message.voice.file_id
    audio_file = await save_voice_file(message.bot, file_id)
    transcribtion = await get_transcribtion(audio_file, message.from_user.id)
    answer = await ask_question(message.from_user.id, transcribtion)
    audio_data = await voice_acting(answer)
    audio_file = BufferedInputFile(audio_data, filename="response.ogg")

    return message.reply_voice(voice=audio_file)

@voice_router.message(Command("new_thread"))
async def new_thread_command(message: Message):
    user_id = message.from_user.id
    thread_id = await get_thread(user_id)
    redis_client = settings.get_thread_db()
    if thread_id:
        redis_client.delete(f"user:{user_id}:thread_id")
        return message.answer("Старый поток удалён. Создаю новый поток.")
    else:
        return message.answer("Поток не найден. Создаю новый поток.")
