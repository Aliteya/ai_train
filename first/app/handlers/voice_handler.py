from aiogram import Router, F
from aiogram.types import Message
from ..utils import save_voice_file, get_transcribtion

voice_router = Router()

@voice_router.message(F.voice)
async def hear_voice(message: Message):
    file_id = message.voice.file_id
    audio_file = await save_voice_file(message.bot, file_id)
    transcribtion = await get_transcribtion(audio_file)
    return message.reply(transcribtion)

