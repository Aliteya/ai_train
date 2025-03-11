from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from ..utils import save_file, mood_determination, voice_acting


photo_router = Router()

@photo_router.message(F.photo)
async def view_photo(message: Message):
    file_id = message.photo[-1].file_id
    photo_file = await save_file(message.bot, file_id)
    mood = await mood_determination(message.from_user.id, photo_file)
    audio_data = await voice_acting(mood)
    audio_file = BufferedInputFile(audio_data, filename="response.ogg")

    return message.reply_voice(voice=audio_file)