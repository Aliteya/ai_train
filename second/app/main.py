from .utils import MyWorkflow, get_transcription, voice_acting

from fastapi import FastAPI, WebSocket,WebSocketDisconnect, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import asyncio
import numpy as np

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
    if request.url.path == "/audio/":
        return await call_next(request)
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

html ="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebSocket Audio Example</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 50px;
        }
        button {
            padding: 10px 20px;
            font-size: 16px;
            margin: 10px;
            cursor: pointer;
        }
        audio {
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>WebSocket Audio Example</h1>

    <!-- Кнопки для управления -->
    <button id="startRecording">Начать запись</button>
    <button id="stopRecording" disabled>Остановить запись</button>

    <!-- Аудиоплеер для воспроизведения ответа -->
    <h2>Ответ от сервера:</h2>
    <audio id="responseAudio" controls></audio>

    <script>
        let mediaRecorder;
        let audioChunks = [];
        let socket;

        // Функция для начала записи аудио
        document.getElementById("startRecording").addEventListener("click", async () => {
            try {
                console.log("Начинаем запись...");
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);

                // Собираем чанки данных
                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        console.log("Получен аудиочанк:", event.data);
                        audioChunks.push(event.data); // Собираем чанки
                    }
                };

                // Когда запись завершена, отправляем данные на сервер
                mediaRecorder.onstop = async () => {
                    console.log("Запись завершена, собираем данные...");

                    if (audioChunks.length > 0) {
                        const audioBlob = new Blob(audioChunks, { type: "audio/webm" }); // Создаем Blob из чанков
                        console.log("Отправляем аудио на сервер...");
                        if (socket && socket.readyState === WebSocket.OPEN) {
                            socket.send(audioBlob); // Отправляем Blob
                        } else {
                            console.error("WebSocket соединение закрыто или недоступно");
                        }

                        // Очищаем чанки
                        audioChunks = [];
                    }

                    // Возвращаем кнопки в исходное состояние
                    document.getElementById("startRecording").disabled = false;
                    document.getElementById("stopRecording").disabled = true;
                };

                // Начинаем запись
                mediaRecorder.start();
                document.getElementById("startRecording").disabled = true;
                document.getElementById("stopRecording").disabled = false;

                console.log("Запись начата.");
            } catch (error) {
                console.error("Ошибка при получении доступа к микрофону:", error);
            }
        });

        // Функция для остановки записи аудио
        document.getElementById("stopRecording").addEventListener("click", () => {
            if (mediaRecorder && mediaRecorder.state === "recording") {
                mediaRecorder.stop(); // Останавливаем запись
                console.log("Запись остановлена.");
            }
        });

        // Подключение к WebSocket
        window.onload = () => {
            socket = new WebSocket("ws://127.0.0.1:8000/audio/");

            socket.onopen = () => {
                console.log("WebSocket соединение установлено");
            };

            socket.onmessage = (event) => {
                if (event.data instanceof Blob) {
                    console.log("Получен аудиочанк");

                    // Создаем URL для воспроизведения аудио
                    const audioUrl = URL.createObjectURL(event.data);
                    const audioPlayer = document.getElementById("responseAudio");
                    audioPlayer.src = audioUrl;
                    audioPlayer.play();
                } else if (typeof event.data === "string") {
                    console.log("Получена текстовая транскрипция:", event.data);
                }
            };

            socket.onclose = () => {
                console.log("WebSocket соединение закрыто");
            };

            socket.onerror = (error) => {
                console.error("WebSocket ошибка:", error);
            };
        };
    </script>
</body>
</html>
"""

@voice_app.get("/")
async def root():
    return HTMLResponse(html)

@voice_app.websocket("/audio/")
async def voice_endpoint(websocket: WebSocket):
    logger.info("Попытка принять WebSocket-соединение...")
    await websocket.accept()

    print("соединение есть ")
    try: 
        while True: 
            
                print("аудио получаем")
                while True:
                    try:
                        data = await websocket.receive_bytes()
                        if not data:
                            break
                        audio = data
                        if audio:
                            break
                        
                    except WebSocketDisconnect:
                        print("Клиент закрыл соединение. Завершаем цикл.")
                        break
                transcription = await get_transcription(audio)
                print(transcription)
                workflow = MyWorkflow(on_start=lambda text: print(f"обрабатываю вопрос"))
                
                full_text = ""
                async for chunk in workflow.run(transcription):
                    print(f"Сгенерированный текстовый чанк: {chunk}")
                    full_text += chunk
                full_audio = await voice_acting(full_text)

                await websocket.send_bytes(full_audio)
    except Exception as e:
        logger.error(f"Ошибка при обработке WebSocket: {e}", exc_info=True)
        await websocket.close()