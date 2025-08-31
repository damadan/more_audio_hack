import asyncio
import logging
from typing import Optional

import websockets
from websockets.server import WebSocketServerProtocol

# --- конфиг
from rt_echo.common.config import load_config
# --- ASR / TTS / сессия
from rt_echo.server.asr import AsrEngine
from rt_echo.server.session import EchoSession
try:
    from rt_echo.server.tts_piper import PiperTTS as TTSEngine
except Exception:  # pragma: no cover - Piper may be optional
    # fallback на Silero, если Piper не используется в проекте
    from rt_echo.server.tts_silero import SileroTTS as TTSEngine


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("rt-echo")

cfg = load_config()  # читает env: ASR_MODEL, ASR_DEVICE, ASR_COMPUTE_TYPE, RU_SPEAKER, WS_PORT
WS_PORT = getattr(cfg, "ws_port", 8000)

asr_engine: Optional[AsrEngine] = None
tts_engine: Optional[TTSEngine] = None


async def ws_handler(ws: WebSocketServerProtocol) -> None:
    """На каждое подключение — своя EchoSession."""
    assert asr_engine and tts_engine
    session = EchoSession(cfg, asr_engine, tts_engine)
    writer_task = asyncio.create_task(session.tick(ws))  # периодический ASR→TTS→send
    try:
        async for msg in ws:
            if isinstance(msg, bytes):
                session.push(msg)  # PCM16@16k входящий блок
    finally:
        writer_task.cancel()


async def health_server() -> None:
    """Простой /healthz на 8001 (не мешает WS на 8000)."""

    async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        req = await reader.read(1024)
        if b"GET /healthz" in req:
            body = b'{"status":"ok"}'
            writer.write(
                b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                + f"Content-Length: {len(body)}\r\n\r\n".encode()
                + body
            )
        else:  # pragma: no cover - other paths are not used in tests
            writer.write(b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n")
        await writer.drain()
        writer.close()

    srv = await asyncio.start_server(handle, host="0.0.0.0", port=8001)
    log.info("/healthz ready on :8001")
    async with srv:
        await srv.serve_forever()


async def main() -> None:
    global asr_engine, tts_engine
    log.info(
        "Loading ASR: model=%s device=%s compute=%s",
        cfg.asr_model,
        cfg.asr_device,
        cfg.asr_compute_type,
    )
    asr_engine = AsrEngine(cfg.asr_model, cfg.asr_device, cfg.asr_compute_type)

    log.info("Loading TTS engine…")
    # PiperTTS обычно принимает путь к .onnx, SileroTTS — имя спикера.
    try:
        tts_engine = TTSEngine(cfg)  # если твой класс принимает cfg
    except TypeError:  # pragma: no cover - compatibility path
        # совместимость со старой сигнатурой
        tts_engine = TTSEngine(getattr(cfg, "ru_speaker", "kseniya_16khz"))

    ws_srv = await websockets.serve(ws_handler, "0.0.0.0", WS_PORT, max_size=2**23)
    log.info("WS server on :%d", WS_PORT)

    await asyncio.gather(ws_srv.wait_closed(), health_server())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

