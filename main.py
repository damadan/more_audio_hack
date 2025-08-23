from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json
import logging
import time
import uuid
from pathlib import Path

from app.schemas import ASRChunk, TTSRequest
from app.tts import pcm_to_wav, stream_bytes, synthesize

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logger = logging.getLogger("stream")
logger.setLevel(logging.INFO)
_handler = logging.FileHandler(log_dir / "stream.log")
_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(_handler)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.post("/interview/start")
async def interview_start():
    session_id = str(uuid.uuid4())
    ws_url = f"ws://localhost:8000/stream/{session_id}"
    return {"session_id": session_id, "ws_url": ws_url}


@app.websocket("/stream/{session_id}")
async def stream(session_id: str, websocket: WebSocket, use_vad: bool = False):
    await websocket.accept()
    vad = None
    if use_vad:
        try:
            import webrtcvad

            vad = webrtcvad.Vad(2)
        except Exception:  # pragma: no cover - optional dependency
            vad = None

    text_buffer = ""
    last_partial = 0.0
    silence_ms = 0.0

    def log_chunk(chunk: ASRChunk) -> None:
        logger.info(json.dumps({"session_id": session_id, **chunk.model_dump()}))

    def is_speech_pcm(pcm: bytes) -> bool:
        if vad:
            return vad.is_speech(pcm, 16000)
        if not pcm:
            return False
        samples = struct.unpack("<" + "h" * (len(pcm) // 2), pcm)
        energy = sum(abs(s) for s in samples) / len(samples)
        return energy > 500

    try:
        while True:
            message = await websocket.receive()
            if message.get("type") == "websocket.disconnect":
                break
            data = message.get("text")
            if data is not None:
                if data == "PING":
                    await websocket.send_text("PONG")
                    continue
                if data == "END":
                    chunk = ASRChunk(type="final", t0=0.0, t1=0.0, text=text_buffer)
                    await websocket.send_json(chunk.model_dump())
                    log_chunk(chunk)
                    await websocket.close()
                    break
                text_buffer += data
                now = time.monotonic()
                if now - last_partial >= 0.25:
                    chunk = ASRChunk(type="partial", t0=0.0, t1=0.0, text=text_buffer)
                    await websocket.send_json(chunk.model_dump())
                    log_chunk(chunk)
                    last_partial = now
            else:
                pcm = message.get("bytes") or b""
                if not pcm:
                    continue
                if is_speech_pcm(pcm):
                    silence_ms = 0.0
                else:
                    silence_ms += 20.0
                    if silence_ms >= 400.0 and text_buffer:
                        chunk = ASRChunk(type="final", t0=0.0, t1=0.0, text=text_buffer)
                        await websocket.send_json(chunk.model_dump())
                        log_chunk(chunk)
                        text_buffer = ""
                        await websocket.close()
                        break
                now = time.monotonic()
                if now - last_partial >= 0.25:
                    chunk = ASRChunk(type="partial", t0=0.0, t1=0.0, text=text_buffer)
                    await websocket.send_json(chunk.model_dump())
                    log_chunk(chunk)
                    last_partial = now
    except WebSocketDisconnect:
        pass


@app.post("/tts")
async def tts(req: TTSRequest):
    pcm, sample_rate = synthesize(req.text, req.voice)
    if req.format == "wav":
        data = pcm_to_wav(pcm, sample_rate)
        media_type = "audio/wav"
    else:
        data = pcm
        media_type = "audio/L16"
    return StreamingResponse(stream_bytes(data), media_type=media_type)


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
