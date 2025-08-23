from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import io
import math
import struct
import uuid
import wave

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.post("/interview/start")
async def interview_start():
    session_id = str(uuid.uuid4())
    ws_url = f"ws://localhost:8000/stream/{session_id}"
    return {"session_id": session_id, "ws_url": ws_url}


@app.websocket("/stream/{session_id}")
async def stream(session_id: str, websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data == "END":
                await websocket.send_json({"type": "final", "text": data})
            else:
                await websocket.send_json({"type": "partial", "text": data})
    except WebSocketDisconnect:
        pass


@app.post("/tts")
async def tts():
    sample_rate = 16000
    duration = 1.0
    frequency = 440.0
    n_samples = int(sample_rate * duration)
    amplitude = 32767

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(n_samples):
            value = int(amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
            wf.writeframes(struct.pack('<h', value))
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="audio/wav")


@app.post("/dm/next")
async def dm_next():
    return {"result": "stub"}


@app.post("/ie/extract")
async def ie_extract():
    return {"result": "stub"}


@app.post("/match/coverage")
async def match_coverage():
    return {"result": "stub"}


@app.post("/rubric/score")
async def rubric_score():
    return {"result": "stub"}


@app.post("/score/final")
async def score_final():
    return {"result": "stub"}


@app.post("/report")
async def report():
    return {"result": "stub"}
