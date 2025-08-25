from __future__ import annotations

from typing import Dict


class AudioStore:
    def __init__(self, bucket: str, endpoint: str | None = None):
        self.bucket = bucket
        self.endpoint = endpoint
        self._data: Dict[str, bytes] = {}

    async def put_segment(self, session_id: str, seg_id: str, pcm: bytes) -> str:
        key = f"{session_id}/{seg_id}.pcm"
        self._data[key] = pcm
        return key
