import os
import wave
import whisper
import warnings

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from tempfile import NamedTemporaryFile


warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")
os.makedirs("audio_ws_chunks", exist_ok=True)

model = whisper.load_model("base")

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")

    pcm_chunks = bytearray()

    try:
        while True:
            chunk = await websocket.receive_bytes()
            pcm_chunks.extend(chunk)

            # After ~5 seconds of 16kHz mono audio (5s * 16000 samples * 2 bytes)
            if len(pcm_chunks) >= 16000 * 2 * 2: #5:
                with NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
                    # Write WAV header + raw PCM data
                    with wave.open(wav_file, "wb") as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)  # 16-bit PCM = 2 bytes
                        wf.setframerate(16000)
                        wf.writeframes(pcm_chunks)
                    tmp_filename = wav_file.name

                try:
                    result = model.transcribe(tmp_filename, language="en")
                    text = result["text"].strip()
                    print("Recognized:", text)
                    await websocket.send_text(text or "[silence]")
                except Exception as e:
                    print("Whisper error:", e)
                    await websocket.send_text(f"[error: {str(e)}]")
                finally:
                    os.remove(tmp_filename)

                pcm_chunks = bytearray()

    except WebSocketDisconnect:
        print("Client disconnected")
