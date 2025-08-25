from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import AsyncIterator, Dict

from .base import EventBus
from ..audio.frames import AudioFrame
from ..api.schemas import TranscriptEvent


class RedisEventBus(EventBus):
    """In-memory stand in for Redis pub/sub used in tests."""

    def __init__(self) -> None:
        self._audio: Dict[str, asyncio.Queue[AudioFrame]] = defaultdict(asyncio.Queue)
        self._events: Dict[str, asyncio.Queue[TranscriptEvent]] = defaultdict(asyncio.Queue)

    async def publish_audio(self, session_id: str, frame: AudioFrame) -> None:
        await self._audio[session_id].put(frame)

    async def subscribe_audio(self, session_id: str) -> AsyncIterator[AudioFrame]:
        q = self._audio[session_id]
        while True:
            frame = await q.get()
            yield frame

    async def publish_event(self, session_id: str, ev: TranscriptEvent) -> None:
        await self._events[session_id].put(ev)

    async def subscribe_events(self, session_id: str) -> AsyncIterator[TranscriptEvent]:
        q = self._events[session_id]
        while True:
            ev = await q.get()
            yield ev
