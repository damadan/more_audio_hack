from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import websockets

from rt_echo.common.config import load_config

from .asr import AsrEngine
from .session import EchoSession
from .tts_piper import PiperTTS
from .tts_silero import SileroTTS


async def reader(ws: websockets.WebSocketServerProtocol, session: EchoSession) -> None:
    """Receive binary PCM frames from the websocket and feed the session."""
    async for message in ws:
        if isinstance(message, bytes):
            session.push(message)


async def writer(ws: websockets.WebSocketServerProtocol, session: EchoSession) -> None:
    """Run session processing loop and stream synthesized speech."""
    await session.tick(ws)


async def start_server() -> None:
    """Load configuration, initialise engines and start websocket server."""
    cfg = load_config()
    asr = AsrEngine(cfg)

    if cfg.tts_engine.lower() == "piper":
        model_path = Path(f"{cfg.ru_speaker}.onnx")
        speaker_json = Path(f"{cfg.ru_speaker}.json")
        tts = PiperTTS(str(model_path), str(speaker_json))
    elif cfg.tts_engine.lower() == "silero":
        tts = SileroTTS(cfg.ru_speaker)
    else:
        raise ValueError(f"Unknown TTS engine: {cfg.tts_engine}")

    async def handler(ws: websockets.WebSocketServerProtocol) -> None:
        session = EchoSession(cfg, asr, tts)
        r_task = asyncio.create_task(reader(ws, session))
        w_task = asyncio.create_task(writer(ws, session))
        done, pending = await asyncio.wait({r_task, w_task}, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()

    async with websockets.serve(handler, "0.0.0.0", cfg.ws_port):
        await asyncio.Future()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_server())


if __name__ == "__main__":  # pragma: no cover - manual entry point
    main()
