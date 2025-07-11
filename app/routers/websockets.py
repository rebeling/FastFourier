import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.services.audio import process_audio_chunk
from app.analysis import analyze_answer

router = APIRouter()


@router.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket, question: str, job_title: str, topic: str):
    await websocket.accept()
    print("Client connected")
    pcm_chunks = bytearray()
    try:
        while True:
            message = await websocket.receive()
            if message.get("type") == "websocket.disconnect":
                break

            data = message.get("bytes") or message.get("text")

            if data == "stop":
                if pcm_chunks:
                    text, performance = process_audio_chunk(pcm_chunks)
                    print("Recognized:", text)
                    print(f"[Performance] {performance}")
                    feedback = await analyze_answer(job_title, topic, question, text)
                    response = {
                        "transcription": text or "[silence]",
                        "feedback": feedback,
                    }
                    await websocket.send_text(json.dumps(response))
                pcm_chunks = bytearray()
            elif isinstance(data, bytes):
                pcm_chunks.extend(data)
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket Error: {e}")
        await websocket.send_text(json.dumps({"error": f"[error: {str(e)}]"}));
