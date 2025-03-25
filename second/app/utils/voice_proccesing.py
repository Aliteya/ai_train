from ..core import settings

from openai import AsyncOpenAI
import tempfile

async def get_transcription(audio: bytes):
    client = AsyncOpenAI(api_key=settings.get_llm_key())
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as temp_file:
        temp_file.write(audio)
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=temp_file
        )
    return response.text

async def voice_acting(text: str):
       client = AsyncOpenAI(api_key=settings.get_llm_key())
       response = await "дописать"