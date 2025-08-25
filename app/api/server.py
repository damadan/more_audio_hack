from __future__ import annotations

import asyncio
import json
from uuid import uuid4
from typing import AsyncIterator

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from .schemas import (
    CreateSessionRequest,
    CreateSessionResponse,
    StartMessage,
    StopMessage,
    TranscriptEvent,
)
from ..audio.codecs import OpusDecoder
from ..audio.frames import AudioFrame
from ..audio.vad import VADService
from ..audio.endpointing import EndpointDetector, Segment
from ..asr.online_vosk import OnlineASR
from ..asr.hybrid_refiner import HybridRefiner, RefinerConfig
from ..asr.postprocess import postprocess_event
from ..storage.transcripts import TranscriptRepository

router = APIRouter()


def model_for(lang: str) -> str:
    return ""


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/sessions", response_model=CreateSessionResponse)
async def create_session(_: CreateSessionRequest) -> CreateSessionResponse:
    return CreateSessionResponse(session_id=uuid4().hex)


async def _ws_iter(ws: WebSocket) -> AsyncIterator[bytes | str]:
    try:
        while True:
            msg = await ws.receive()
            if "bytes" in msg and msg["bytes"] is not None:
                yield msg["bytes"]
            elif "text" in msg and msg["text"] is not None:
                yield msg["text"]
            else:
                break
    except WebSocketDisconnect:
        return


@router.websocket("/stream")
async def stream(ws: WebSocket, repo: TranscriptRepository = Depends(TranscriptRepository)):
    await ws.accept()
    start = StartMessage.model_validate_json(await ws.receive_text())
    session_id = uuid4().hex
    decoder = OpusDecoder()
    vad = VADService()
    endp = EndpointDetector()
    asr = OnlineASR(model_dir=model_for(start.lang), lang=start.lang)
    refiner = HybridRefiner(RefinerConfig()) if start.profile == "hybrid" else None

    async def send_event(ev: TranscriptEvent) -> None:
        ev = ev.model_copy(update={"session_id": session_id})
        await repo.append(session_id, ev)
        await ws.send_text(ev.model_dump_json())

    async for msg in _ws_iter(ws):
        if isinstance(msg, bytes):
            pcm = decoder.decode(msg)
            t0 = 0.0 if not hasattr(stream, "_time") else stream._time
            t1 = t0 + len(pcm) / 16000.0
            stream._time = t1
            frame = AudioFrame(pcm=pcm, sample_rate=16000, t0=t0, t1=t1)
            is_speech = vad.is_speech(frame)
            partial = asr.accept_frame(frame)
            if partial:
                await send_event(postprocess_event(partial, start.lang))
            for seg in endp.push(frame, is_speech):
                final = asr.finalize_segment()
                if final:
                    await send_event(postprocess_event(final, start.lang))
                if refiner:
                    asyncio.create_task(_refine_and_emit(refiner, seg, start.lang, send_event))
        else:
            ctrl = json.loads(msg)
            if ctrl.get("type") == "stop":
                break
    await ws.close()


async def _refine_and_emit(refiner: HybridRefiner, seg: Segment, lang: str, send_event):
    ev = refiner.refine(seg, lang)
    await send_event(postprocess_event(ev, lang))
