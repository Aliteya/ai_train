from ..utils import save_file, mood_determination, voice_acting, send_amplitude_event

from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext

photo_router = Router()

@photo_router.message(F.photo | (F.document & F.document.mime_type.startswith("image/")))
async def view_photo(message: Message, state: FSMContext):
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document and message.document.mime_type.startswith("image/"):
        file_id = message.document.file_id
    photo_file = await save_file(message.bot, file_id)
    mood = await mood_determination(message.from_user.id, photo_file, state)
    audio_data = await voice_acting(mood)
    audio_file = BufferedInputFile(audio_data, filename="response.ogg")

    await message.reply_voice(voice=audio_file)
    send_amplitude_event(
        user_id=str(message.from_user.id),
        event_type="photo_processed",
        event_properties={
            "mood": mood
        }
    )