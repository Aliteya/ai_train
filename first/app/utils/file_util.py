from aiogram import Bot
import uuid
from ..core import settings

async def save_voice_file(bot: Bot, file_id):
    file = await bot.get_file(file_id)
    file_path = file.file_path

    downloaded_file = await bot.download_file(file_path)
    return downloaded_file

async def get_transcribtion(audio_file, user_id):
    client = settings.get_ai_settings()
    response = await client.audio.transcriptions.create(
        model="whisper-1",
        file=(f"{user_id}_voice.ogg", audio_file)
    )
    audio_file.close()
    return response.text

async def voice_acting(text):
    client = settings.get_ai_settings()
    response = await client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )
    return response.read()
