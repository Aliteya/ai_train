from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from ..utils import save_file, get_transcribtion, ask_question, voice_acting,  send_amplitude_event

voice_router = Router()

@voice_router.message(F.voice)
async def hear_voice(message: Message):
    file_id = message.voice.file_id
    audio_file = await save_file(message.bot, file_id)
    transcribtion = await get_transcribtion(audio_file, message.from_user.id)
    answer = await ask_question(message.from_user.id, transcribtion)
    audio_data = await voice_acting(answer)
    audio_file = BufferedInputFile(audio_data, filename="response.ogg")

    await message.reply_voice(voice=audio_file)

    send_amplitude_event(
        user_id=str(message.from_user.id),
        event_type="voice_message_processed",
        event_properties={
            "transcribtion": transcribtion,
            "answer": answer
        }
    )

