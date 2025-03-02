from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from ..utils import save_voice_file, get_transcribtion, ask_question, voice_acting
import io

voice_router = Router()

@voice_router.message(F.voice)
async def hear_voice(message: Message):
    file_id = message.voice.file_id
    audio_file = await save_voice_file(message.bot, file_id)
    transcribtion = await get_transcribtion(audio_file)
    answer = await ask_question(transcribtion)

    audio_data = await voice_acting(answer)
    audio_file = BufferedInputFile(audio_data, filename="response.ogg")

    return message.reply_voice(voice=audio_file)

