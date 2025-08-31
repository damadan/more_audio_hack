import argparse
import asyncio
import time
import wave
from pathlib import Path
from typing import cast

import websockets
from websockets.legacy.client import WebSocketClientProtocol

CHUNK_SAMPLES = 320  # 20ms @ 16kHz
SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2  # bytes for PCM16
CHUNK_DURATION = CHUNK_SAMPLES / SAMPLE_RATE


async def send_audio(ws: WebSocketClientProtocol, wav_path: Path) -> float:
    """Stream audio to the websocket in 20ms chunks.

    Returns the timestamp of when the first chunk was sent.
    """
    t_send_first: float | None = None
    with wave.open(str(wav_path), "rb") as wf:
        if wf.getframerate() != SAMPLE_RATE:
            raise ValueError(f"Unexpected sample rate: {wf.getframerate()}")
        if wf.getnchannels() != CHANNELS:
            raise ValueError(f"Unexpected channel count: {wf.getnchannels()}")
        if wf.getsampwidth() != SAMPLE_WIDTH:
            raise ValueError(f"Unexpected sample width: {wf.getsampwidth()}")

        frames_per_chunk = CHUNK_SAMPLES
        chunk_bytes = frames_per_chunk * SAMPLE_WIDTH
        first = True
        while True:
            data = wf.readframes(frames_per_chunk)
            if not data:
                break
            if len(data) < chunk_bytes:
                data += b"\x00" * (chunk_bytes - len(data))
            if first:
                t_send_first = time.perf_counter()
                first = False
            await ws.send(data)
            await asyncio.sleep(CHUNK_DURATION)
    await ws.send(b"")
    if t_send_first is None:
        raise RuntimeError("No audio frames were sent")
    return t_send_first


async def recv_first(ws: WebSocketClientProtocol) -> float:
    """Wait for the first bytes from the server and return their timestamp."""
    async for message in ws:
        if isinstance(message, bytes) and message:
            return time.perf_counter()
    raise RuntimeError("Websocket closed without receiving audio")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Measure TTS E2E latency")
    parser.add_argument("--ws", required=True, help="Websocket URL, e.g. ws://host:8000")
    parser.add_argument("--wav", required=True, help="Input WAV file (16kHz mono)")
    args = parser.parse_args()

    wav_path = Path(args.wav)

    async with websockets.connect(args.ws) as ws:
        ws_proto = cast(WebSocketClientProtocol, ws)
        recv_task = asyncio.create_task(recv_first(ws_proto))
        t_send_first = await send_audio(ws_proto, wav_path)
        t_recv_first = await recv_task

    latency_ms = (t_recv_first - t_send_first) * 1000
    print(f"E2E latency: {latency_ms:.1f} ms")


if __name__ == "__main__":
    asyncio.run(main())
