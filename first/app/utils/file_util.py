from ..core import settings

from aiogram import Bot

async def save_file(bot: Bot, file_id):
    file = await bot.get_file(file_id)
    file_path = file.file_path
    with await bot.download_file(file_path) as downloaded_file:
        downloaded_file.seek(0)
        return downloaded_file.getvalue() 

async def get_transcribtion(audio_file, user_id):
    client = settings.get_ai_settings()
    response = await client.audio.transcriptions.create(
        model="whisper-1",
        file=(f"{user_id}_voice.ogg", audio_file)
    )
    return response.text

async def voice_acting(text):
    client = settings.get_ai_settings()
    response = await client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )
    return response.read()

async def upload_photo(image_file, user_id):
    client = settings.get_ai_settings()
    response = await client.files.create(
        file=(f"{user_id}_image.jpeg", image_file),
        purpose="vision"
    )
    return response.id