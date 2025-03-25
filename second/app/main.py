from .utils import MyWorkflow, get_transcription

from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

voice_app = FastAPI()

origins = ["*"]

voice_app.add_middleware(CORSMiddleware,
                         allow_origins=origins,
                         allow_credentials=True,
                         allow_methods=["*"],
                         allow_headers=["*"],)

@voice_app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Запрос {request.method} {request.url}")
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return JSONResponse(status_code=500, content="Internal Server Error")
    logger.info(
        f"Статус ответа {response.status_code}"
    )
    return response

@voice_app.get("/")
async def root():
    return {"data": "You're in root"}

@voice_app.websocket("/audio/")
async def voice_endpoint(websocket: WebSocket):
    await websocket.accept()

    try: 
        audio = b""
        while True:
            data = await websocket.receive_bytes()
            if not data:
                break

            audio += data
        transcription = await get_transcription(audio)
        workflow = MyWorkflow(on_start=lambda text: print(f"обрабатываю вопрос"))
        async def process_and_send():
            async for chunk in workflow.run(transcription):
                audio_chunk = await "Дописать"
        await process_and_send()

    except Exception as e:
        await websocket.close()