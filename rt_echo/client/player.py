from __future__ import annotations

import asyncio
from typing import Optional

import numpy as np
import sounddevice as sd


class PcmPlayer:
    """Play PCM16 audio blocks using ``sounddevice``."""

    def __init__(self, queue_size: int = 5) -> None:
        self._queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=queue_size)
        self._stream: Optional[sd.OutputStream] = None
        self._buffer = b""
        self._stopping = False
        self._drained = asyncio.Event()

    def _callback(
        self,
        outdata: np.ndarray,
        frames: int,
        time: sd.CallbackTime,
        status: sd.CallbackFlags,
    ) -> None:
        """Callback for ``sounddevice`` that feeds audio from the queue."""
        if status:
            # For simplicity, ignore status but could log/handle it.
            pass

        bytes_needed = frames * 2  # int16 -> 2 bytes per frame
        out = memoryview(outdata).cast("b")
        idx = 0
        while bytes_needed > 0:
            if self._buffer:
                take = min(len(self._buffer), bytes_needed)
                out[idx : idx + take] = self._buffer[:take]
                self._buffer = self._buffer[take:]
                idx += take
                bytes_needed -= take
            else:
                try:
                    chunk = self._queue.get_nowait()
                    self._queue.task_done()
                except asyncio.QueueEmpty:
                    # Underrun: fill remaining buffer with silence
                    out[idx : idx + bytes_needed] = b"\x00" * bytes_needed
                    bytes_needed = 0
                else:
                    self._buffer = chunk

        if self._stopping and not self._buffer and self._queue.empty():
            self._drained.set()

    async def __aenter__(self) -> "PcmPlayer":
        self._stopping = False
        self._drained.clear()
        self._stream = sd.OutputStream(
            samplerate=16000,
            channels=1,
            dtype="int16",
            blocksize=320,
            callback=self._callback,
        )
        self._stream.start()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.stop()

    async def play(self, bytes_pcm16: bytes) -> None:
        """Queue a PCM16 audio block for playback."""
        await self._queue.put(bytes_pcm16)

    async def stop(self) -> None:
        """Stop playback after draining the queue."""
        self._stopping = True
        await self._drained.wait()
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
