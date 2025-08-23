import io
import math
import uuid
import wave
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from app.schemas import IE, Coverage, Rubric, FinalScore
from app.rubric import router as rubric_router

app = FastAPI()

# Enable CORS for all origins
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
    ws_url = f"/stream/{session_id}"
    return {"session_id": session_id, "ws_url": ws_url}


@app.websocket("/stream/{session_id}")
async def stream_ws(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            msg = await websocket.receive_text()
            if msg == "END":
                await websocket.send_json({"type": "final", "text": msg})
                break
            await websocket.send_json({"type": "partial", "text": msg})
    except WebSocketDisconnect:
        pass
    finally:
        await websocket.close()


@app.post("/tts")
async def tts_stub():
    sample_rate = 16_000
    duration = 1.0
    freq = 440.0
    n_samples = int(sample_rate * duration)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(n_samples):
            value = int(32767 * math.sin(2 * math.pi * freq * i / sample_rate))
            wf.writeframesraw(value.to_bytes(2, byteorder="little", signed=True))
    audio_bytes = buffer.getvalue()
    headers = {"Content-Type": "audio/wav"}
    return Response(content=audio_bytes, media_type="audio/wav", headers=headers)


@app.post("/dm/next")
async def dm_next():
    return {"response": "stub"}


@app.post("/ie/extract")
async def ie_extract() -> IE:
    return IE(skills=[], tools=[], years={}, projects=[], roles=[])


@app.post("/match/coverage")
async def match_coverage() -> Coverage:
    return Coverage(per_indicator={}, per_competency={})


# Rubric scoring endpoints
app.include_router(rubric_router)


@app.post("/score/final")
async def score_final() -> FinalScore:
    return FinalScore(overall=0.0, decision="reject", reasons=[], by_comp=[])


@app.post("/report")
async def report():
    return {"status": "stub"}
