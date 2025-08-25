from __future__ import annotations

from typing import Dict, List

from ..api.schemas import TranscriptEvent


class TranscriptRepository:
    """Simple in-memory transcript storage used in tests."""

    def __init__(self, dsn: str | None = None):
        self._data: Dict[str, List[TranscriptEvent]] = {}

    async def append(self, session_id: str, ev: TranscriptEvent) -> None:
        self._data.setdefault(session_id, []).append(ev)

    async def get_full(self, session_id: str) -> List[TranscriptEvent]:
        return list(self._data.get(session_id, []))
