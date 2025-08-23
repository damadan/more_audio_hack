from __future__ import annotations

import asyncio
import contextlib
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from .schemas import ASRChunk

router = APIRouter()


@router.websocket("/stream/{session_id}")
async def stream_ws(
    websocket: WebSocket,
    session_id: str,
    use_vad: bool = Query(False),
) -> None:
    """Simple ASR websocket gateway.

    Accepts either 20 ms PCM16 chunks (binary) or control messages in plain
    text. When the text "PING" is received the gateway will reply with
    partial hypotheses every ~250 ms. When "END" is received or the
    connection stays idle for 400 ms a final hypothesis is sent and the
    connection closes.

    Parameters
    ----------
    session_id: str
        Identifier of the audio stream session.
    use_vad: bool
        Whether to use ``webrtcvad`` for voice activity detection. If the
        module is missing the gateway continues without VAD.
    """

    await websocket.accept()

    # Optional VAD initialisation
    vad: Optional[object] = None
    if use_vad:
        try:
            import webrtcvad  # type: ignore

            vad = webrtcvad.Vad(2)
        except ModuleNotFoundError:
            vad = None

    text_buffer = ""
    closed = False

    async def send_partials() -> None:
        """Background task sending partial hypotheses every ~250 ms."""
        while True:
            await asyncio.sleep(0.25)
            if text_buffer:
                chunk = ASRChunk(type="partial", t0=0.0, t1=0.0, text=text_buffer)
                await websocket.send_json(chunk.model_dump())

    partial_task = asyncio.create_task(send_partials())
    try:
        while True:
            try:
                message = await asyncio.wait_for(websocket.receive(), timeout=0.4)
            except asyncio.TimeoutError:
                if text_buffer:
                    chunk = ASRChunk(type="final", t0=0.0, t1=0.0, text=text_buffer)
                    await websocket.send_json(chunk.model_dump())
                    text_buffer = ""
                continue

            if message["type"] == "websocket.disconnect":
                break

            if (data_text := message.get("text")) is not None:
                if data_text == "PING":
                    text_buffer = "PONG"
                elif data_text == "END":
                    if text_buffer:
                        chunk = ASRChunk(
                            type="final", t0=0.0, t1=0.0, text=text_buffer
                        )
                        await websocket.send_json(chunk.model_dump())
                        text_buffer = ""
                    break
                else:
                    text_buffer += data_text
            elif (data_bytes := message.get("bytes")) is not None:
                if vad:
                    # Consume the frame to keep VAD state; result is ignored.
                    vad.is_speech(data_bytes, 16000)
                # In a real implementation the audio would be forwarded to the
                # ASR backend. Here it's ignored.
    except WebSocketDisconnect:
        closed = True
    finally:
        partial_task.cancel()
        with contextlib.suppress(Exception):
            await partial_task
        if not closed:
            await websocket.close()


__all__ = ["router"]
