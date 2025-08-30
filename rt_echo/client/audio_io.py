from __future__ import annotations

import asyncio
from typing import Optional

import numpy as np
import sounddevice as sd


class MicStreamer:
    """Stream microphone audio blocks using ``sounddevice``."""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[bytes] = asyncio.Queue()
        self._stream: Optional[sd.InputStream] = None

    def _callback(self, indata: np.ndarray, frames: int, time: sd.CallbackTime, status: sd.CallbackFlags) -> None:
        """Callback for ``sounddevice`` that queues raw PCM16 audio blocks."""
        # ``indata`` is a NumPy array with dtype=int16. Convert to bytes and enqueue.
        if status:
            # For simplicity, ignore status but could log/handle it.
            pass
        self._queue.put_nowait(indata.tobytes())

    async def __aenter__(self) -> "MicStreamer":
        self._stream = sd.InputStream(
            samplerate=16000,
            channels=1,
            dtype="int16",
            blocksize=320,
            callback=self._callback,
        )
        self._stream.start()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    async def read_block(self) -> bytes:
        """Read the next audio block from the microphone."""
        return await self._queue.get()
