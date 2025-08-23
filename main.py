import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import IE, Coverage, Rubric, FinalScore
from app.tts_local import router as tts_router

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tts_router)


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


@app.post("/dm/next")
async def dm_next():
    return {"response": "stub"}


@app.post("/ie/extract")
async def ie_extract() -> IE:
    return IE(skills=[], tools=[], years={}, projects=[], roles=[])


@app.post("/match/coverage")
async def match_coverage() -> Coverage:
    return Coverage(per_indicator={}, per_competency={})


@app.post("/rubric/score")
async def rubric_score() -> Rubric:
    return Rubric(scores={}, red_flags=[], evidence=[])


@app.post("/score/final")
async def score_final() -> FinalScore:
    return FinalScore(overall=0.0, decision="reject", reasons=[], by_comp=[])


@app.post("/report")
async def report():
    return {"status": "stub"}
