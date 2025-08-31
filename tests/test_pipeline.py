import asyncio
import os
import sys
import time
from types import SimpleNamespace

import numpy as np
import websockets

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from server.session import EchoSession

SAMPLE_RATE = 16_000
CHUNK_MS = 20
CHUNK_BYTES = SAMPLE_RATE * CHUNK_MS // 1000 * 2
LATENCY_THRESHOLD = 2.0  # seconds


class DummyAsr:
    """Stub ASR that always returns a constant Russian phrase."""

    def transcribe_window(self, _audio: np.ndarray) -> str:
        return "привет "


class DummyTTS:
    """Stub TTS that returns non-empty float audio."""

    def synthesize(self, _text: str) -> tuple[np.ndarray, int]:
        return np.zeros(200, dtype=np.float32), SAMPLE_RATE


async def reader(ws, session) -> None:
    async for message in ws:
        if isinstance(message, bytes):
            session.push(message)


async def writer(ws, session) -> None:
    await session.tick(ws)


def generate_audio(duration: float = 1.0) -> bytes:
    """Generate a 440 Hz sine wave PCM16 byte stream."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    audio = 0.1 * np.sin(2 * np.pi * 440 * t)
    return (audio * 32767).astype(np.int16).tobytes()


async def run_client(uri: str, pcm_bytes: bytes):
    async with websockets.connect(uri) as ws:
        start_event = asyncio.Event()

        async def sender() -> None:
            for i in range(0, len(pcm_bytes), CHUNK_BYTES):
                await ws.send(pcm_bytes[i : i + CHUNK_BYTES])
                if i == 0:
                    start_event.set()
                await asyncio.sleep(CHUNK_MS / 1000)

        send_task = asyncio.create_task(sender())
        await start_event.wait()
        start = time.perf_counter()
        response = await asyncio.wait_for(ws.recv(), timeout=5)
        latency = time.perf_counter() - start
        await send_task
        return response, latency


async def run_test():
    cfg = SimpleNamespace(asr_sr=SAMPLE_RATE, window_sec=2.0, step_sec=0.5)
    asr = DummyAsr()
    tts = DummyTTS()

    async def handler(ws) -> None:
        session = EchoSession(cfg, asr, tts)
        r_task = asyncio.create_task(reader(ws, session))
        w_task = asyncio.create_task(writer(ws, session))
        await asyncio.wait({r_task, w_task}, return_when=asyncio.FIRST_COMPLETED)

    async with websockets.serve(handler, "localhost", 0) as server:
        port = server.sockets[0].getsockname()[1]
        pcm = generate_audio()
        return await run_client(f"ws://localhost:{port}", pcm)


def test_pipeline():
    response, latency = asyncio.run(run_test())
    assert isinstance(response, bytes)
    assert len(response) > 0
    assert latency < LATENCY_THRESHOLD
