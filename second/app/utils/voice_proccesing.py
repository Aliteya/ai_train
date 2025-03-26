from ..core import settings

from openai import AsyncOpenAI
import uuid   
import asyncio
import os

async def get_transcription(audio: bytes):
    print("транскрипция")
    client = AsyncOpenAI(api_key=settings.get_llm_key())

    file_name = f"input_audio_{uuid.uuid4()}.wav"
    with open(file_name, "wb") as f:
        f.write(audio)
    with open(file_name, "rb") as f: 
        response = await client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    os.remove(file_name)
    print(response.text)
    return response.text

async def voice_acting(text: str):
    print("озвучка")
    client = AsyncOpenAI(api_key=settings.get_llm_key())
    response = await client.audio.speech.create(
            model="gpt-4o-mini-tts", 
            voice="alloy",
            input=text
        )
    print("Собираем полное аудио...")
    full_audio = b""
    for chunk in response.iter_bytes():
        full_audio += chunk
    return full_audio
    

    # for chunk in response.iter_bytes():
    #     print("кидаю чанк")
    #     yield chunk
    #     await asyncio.sleep(0)

       