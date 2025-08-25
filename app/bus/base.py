from __future__ import annotations

from typing import AsyncIterator

from ..audio.frames import AudioFrame
from ..api.schemas import TranscriptEvent


class EventBus:
    async def publish_audio(self, session_id: str, frame: AudioFrame) -> None:
        raise NotImplementedError

    async def subscribe_audio(self, session_id: str) -> AsyncIterator[AudioFrame]:
        raise NotImplementedError

    async def publish_event(self, session_id: str, ev: TranscriptEvent) -> None:
        raise NotImplementedError

    async def subscribe_events(self, session_id: str) -> AsyncIterator[TranscriptEvent]:
        raise NotImplementedError
