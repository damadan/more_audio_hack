from __future__ import annotations

import asyncio
import logging
from collections import deque
from typing import Deque
import contextlib

import websockets

from common.config import load_config

STEP_SEC = 0.5
WINDOW_SEC = 2.0
BYTES_PER_SAMPLE = 2


class Session:
    """Store incoming audio frames and provide sliding window access."""

    def __init__(self, sample_rate: int) -> None:
        self.sample_rate = sample_rate
        self.max_bytes = int(sample_rate * WINDOW_SEC * BYTES_PER_SAMPLE)
        self.frames: Deque[bytes] = deque()
        self.size = 0

    def add_frame(self, frame: bytes) -> None:
        self.frames.append(frame)
        self.size += len(frame)
        while self.size > self.max_bytes and self.frames:
            removed = self.frames.popleft()
            self.size -= len(removed)

    def window(self) -> bytes:
        return b"".join(self.frames)


async def process_window(session: Session) -> None:
    data = session.window()
    if not data:
        return
    logging.info("Processing %d bytes of audio", len(data))
    # Placeholder for actual audio processing logic.


async def handler(ws: websockets.WebSocketServerProtocol, path: str) -> None:
    cfg = load_config()
    session = Session(cfg.asr_sr)
    loop_task = asyncio.create_task(_processing_loop(session))
    try:
        async for message in ws:
            if isinstance(message, bytes):
                session.add_frame(message)
            else:
                logging.debug("Ignoring non-binary message: %r", message)
    finally:
        loop_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await loop_task


async def _processing_loop(session: Session) -> None:
    while True:
        await asyncio.sleep(STEP_SEC)
        await process_window(session)


async def main() -> None:
    cfg = load_config()
    async with websockets.serve(handler, "0.0.0.0", cfg.ws_port):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
