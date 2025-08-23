from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse, Response
import json
import logging
import time
import uuid
import struct
from pathlib import Path
import re

from prometheus_client import (
    Counter,
    Histogram,
    CONTENT_TYPE_LATEST,
    generate_latest,
)
from starlette.middleware.base import BaseHTTPMiddleware

from pydantic import TypeAdapter, ValidationError

from app.llm_client import LLMClient
from app.schemas import (
    ASRChunk,
    TTSRequest,
    DMRequest,
    NextAction,
    JD,
    DMTurn,
    IEExtractRequest,
    IE,
    RubricScoreRequest,
    Rubric,
    Coverage,
    CoverageRequest,
    RubricEvidence,
    FinalScoreRequest,
    FinalScore,
    ReportRequest,
    ATSSyncRequest,
)
from app.dialog_manager import build_prompt as dm_build_prompt
from app.match import (
    build_indicator_index,
    match_spans,
    compute_coverage,
)
from app.tts import pcm_to_wav, stream_bytes, synthesize
from app.ie import extract_ie
from app.scoring import final_score as compute_final_score

from jinja2 import Environment, FileSystemLoader
import os
import asyncio
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PIIFormatter(logging.Formatter):
    email_re = re.compile(r"[\w\.-]+@[\w\.-]+")
    phone_re = re.compile(r"\+?\d[\d\s-]{7,}\d")

    def format(self, record: logging.LogRecord) -> str:  # pragma: no cover - formatting
        msg = record.getMessage()
        msg = self.email_re.sub("[REDACTED_EMAIL]", msg)
        msg = self.phone_re.sub("[REDACTED_PHONE]", msg)
        data = {
            "level": record.levelname,
            "time": self.formatTime(record, self.datefmt),
            "message": msg,
        }
        return json.dumps(data)


handler = logging.StreamHandler()
handler.setFormatter(PIIFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logger = logging.getLogger("stream")
_handler = logging.FileHandler(log_dir / "stream.log")
_handler.setFormatter(PIIFormatter())
logger.addHandler(_handler)


REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "http_status"]
)
REQUEST_LATENCY = Histogram(
    "request_latency_seconds", "Request latency", ["method", "endpoint"]
)
ASR_PARTIAL_LATENCY = Histogram("asr_partial_latency", "ASR partial latency")
ASR_FINAL_LATENCY = Histogram("asr_final_latency", "ASR final latency")
SCORE_OVERALL_HIST = Histogram("score_overall_hist", "Final score histogram")


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        REQUEST_COUNT.labels(request.method, request.url.path, str(response.status_code)).inc()
        REQUEST_LATENCY.labels(request.method, request.url.path).observe(time.time() - start)
        return response


app.add_middleware(MetricsMiddleware)

templates = Environment(loader=FileSystemLoader(Path("app") / "templates"))

DM_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"enum": ["ask", "end"]},
        "question": {"type": "string"},
        "followups": {"type": "array", "items": {"type": "string"}},
        "target_skill": {"type": "string"},
        "reason": {"type": "string"},
    },
    "required": ["action", "reason"],
    "additionalProperties": False,
}

NextActionAdapter = TypeAdapter(NextAction)
RubricAdapter = TypeAdapter(Rubric)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


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
            msg_start = time.monotonic()
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
                    ASR_FINAL_LATENCY.observe(time.monotonic() - msg_start)
                    await websocket.close()
                    break
                text_buffer += data
                now = time.monotonic()
                if now - last_partial >= 0.25:
                    chunk = ASRChunk(type="partial", t0=0.0, t1=0.0, text=text_buffer)
                    await websocket.send_json(chunk.model_dump())
                    log_chunk(chunk)
                    ASR_PARTIAL_LATENCY.observe(time.monotonic() - msg_start)
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
                        ASR_FINAL_LATENCY.observe(time.monotonic() - msg_start)
                        text_buffer = ""
                        await websocket.close()
                        break
                now = time.monotonic()
                if now - last_partial >= 0.25:
                    chunk = ASRChunk(type="partial", t0=0.0, t1=0.0, text=text_buffer)
                    await websocket.send_json(chunk.model_dump())
                    log_chunk(chunk)
                    ASR_PARTIAL_LATENCY.observe(time.monotonic() - msg_start)
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




def build_rubric_prompt(jd: JD, transcript: str | IE, coverage: Coverage | None) -> str:
    system = (
        "You are evaluating a candidate.\n"
        "Score each competency from 0 to 5 with the following anchors:\n"
        "0: no evidence of skill\n"
        "1: awareness only\n"
        "2: limited experience\n"
        "3: working proficiency\n"
        "4: strong proficiency\n"
        "5: expert mastery.\n"
        "Return JSON with keys {scores, red_flags, evidence}.\n"
        "Each evidence item must contain quote, t0, t1 and competency.\n"
        "List any concerns in red_flags."
    )
    jd_context = f"Job Description:\n{jd.model_dump_json(indent=2)}\n"
    if isinstance(transcript, IE):
        interview_context = f"IE:\n{transcript.model_dump_json(indent=2)}\n"
    else:
        interview_context = f"Transcript:\n{transcript}\n"
    coverage_context = (
        f"Coverage:\n{coverage.model_dump_json(indent=2)}\n" if coverage else ""
    )
    return f"{system}\n\n{jd_context}{interview_context}{coverage_context}"


def merge_rubrics(*rubrics: Rubric) -> Rubric:
    scores: dict[str, list[int]] = {}
    for r in rubrics:
        for name, score in r.scores.items():
            scores.setdefault(name, []).append(score)
    merged_scores = {
        name: round(sum(vals) / len(vals)) for name, vals in scores.items()
    }
    evidence_map: dict[tuple[str, float, float, str | None], RubricEvidence] = {}
    for r in rubrics:
        for ev in r.evidence:
            key = (ev.quote, ev.t0, ev.t1, ev.competency)
            evidence_map[key] = ev
    red_flags = list({rf for r in rubrics for rf in r.red_flags})
    return Rubric(
        scores=merged_scores, evidence=list(evidence_map.values()), red_flags=red_flags
    )


@app.post("/dm/next")
async def dm_next(req: DMRequest) -> NextAction:
    prompt = dm_build_prompt(req.jd, req.context.turns, req.coverage)
    client = LLMClient.from_env()
    raw = client.generate_json(prompt=prompt, json_schema=DM_JSON_SCHEMA)
    try:
        return NextActionAdapter.validate_python(raw)
    except ValidationError as exc:  # pragma: no cover - should rarely happen
        raise HTTPException(status_code=500, detail=f"LLM JSON invalid: {exc}")


@app.post("/ie/extract")
async def ie_extract(req: IEExtractRequest) -> IE:
    if isinstance(req.transcript, str):
        chunks = [ASRChunk(type="final", t0=0.0, t1=0.0, text=req.transcript)]
    else:
        chunks = req.transcript
    try:
        llm = LLMClient.from_env()
    except Exception:
        llm = None
    return extract_ie(chunks, req.include_timestamps, llm)


@app.post("/match/coverage")
async def match_coverage(req: CoverageRequest) -> Coverage:
    backend = os.environ.get("HR_EMB_BACKEND", "BGE_M3")
    index, meta = build_indicator_index(req.jd, backend)
    matches = match_spans(req.transcript, index, meta, backend, top_k=3)
    return compute_coverage(matches, meta)


@app.post("/rubric/score")
async def rubric_score(req: RubricScoreRequest) -> Rubric:
    prompt = build_rubric_prompt(req.jd, req.transcript, req.coverage)
    client = LLMClient.from_env()
    schema = Rubric.model_json_schema()
    raw1 = client.generate_json(prompt=prompt, json_schema=schema)
    raw2 = client.generate_json(prompt=prompt, json_schema=schema)
    try:
        r1 = RubricAdapter.validate_python(raw1)
        r2 = RubricAdapter.validate_python(raw2)
    except ValidationError as exc:  # pragma: no cover - should rarely happen
        raise HTTPException(status_code=500, detail=f"LLM JSON invalid: {exc}")
    return merge_rubrics(r1, r2)


@app.post("/score/final")
async def score_final(req: FinalScoreRequest) -> FinalScore:
    res = compute_final_score(req.jd, req.ie, req.coverage, req.rubric, req.aux)
    SCORE_OVERALL_HIST.observe(res.overall)
    return res


@app.post("/report")
async def report(req: ReportRequest, fmt: str = "html"):
    template = templates.get_template("report.html")
    overall_pct = round(req.final.overall * 100)
    html = template.render(
        candidate=req.candidate,
        vacancy=req.vacancy,
        rubric=req.rubric,
        final=req.final,
        overall_pct=overall_pct,
        audio_url=req.audio_url,
        labels=list(req.rubric.scores.keys()),
        scores=list(req.rubric.scores.values()),
    )
    if fmt == "pdf":
        try:
            from weasyprint import HTML

            pdf = HTML(string=html).write_pdf()
            return Response(content=pdf, media_type="application/pdf")
        except Exception as exc:  # pragma: no cover - optional dependency
            raise HTTPException(status_code=500, detail=f"pdf generation failed: {exc}")
    return HTMLResponse(html)


@app.post("/ats/sync")
async def ats_sync(req: ATSSyncRequest):
    url = os.environ.get("MOCK_ATS_URL")
    if not url:
        raise HTTPException(status_code=500, detail="MOCK_ATS_URL not set")
    headers = {"Idempotency-Key": f"{req.candidate_id}:{req.vacancy_id}"}
    payload = req.model_dump()
    delay = 1.0
    for attempt in range(3):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=5)
            if resp.status_code == 200:
                return {"status": "ok"}
            if resp.status_code >= 500:
                raise Exception("server error")
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        except HTTPException:
            raise
        except Exception:
            if attempt == 2:
                raise HTTPException(status_code=502, detail="ATS sync failed")
            await asyncio.sleep(delay)
            delay *= 2
    return {"status": "ok"}
