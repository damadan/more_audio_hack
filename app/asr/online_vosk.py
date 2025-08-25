from __future__ import annotations

from typing import Optional
import numpy as np
import time

from ..audio.frames import AudioFrame
from ..api.schemas import TranscriptEvent, Word


class OnlineASR:
    """Toy implementation of online ASR used in tests.

    The real project uses Vosk, but for unit tests we simulate decoding by
    appending a dummy character for each frame. This keeps the interface similar
    while remaining lightweight and deterministic.
    """

    def __init__(self, model_dir: str | None = None, sample_rate: int = 16000, lang: str = "ru", hotwords: list[str] | None = None):
        self.sample_rate = sample_rate
        self.lang = lang
        self.buffer: list[str] = []
        self._seg_t0: float | None = None
        self._seg_t1: float | None = None

    def accept_frame(self, frame: AudioFrame) -> Optional[TranscriptEvent]:
        self._seg_t0 = self._seg_t0 or frame.t0
        self._seg_t1 = frame.t1
        self.buffer.append("a")
        text = "".join(self.buffer)
        return TranscriptEvent(
            type="partial",
            session_id="",
            ts_start=self._seg_t0,
            ts_end=self._seg_t1,
            text=text,
            words=[Word(w="a", start=self._seg_t0 or 0.0, end=self._seg_t1 or 0.0, conf=1.0)],
            stability=0.9,
        )

    def finalize_segment(self) -> Optional[TranscriptEvent]:
        if not self.buffer:
            return None
        text = "".join(self.buffer)
        time.sleep(0.002)
        ev = TranscriptEvent(
            type="final",
            session_id="",
            ts_start=self._seg_t0 or 0.0,
            ts_end=self._seg_t1 or 0.0,
            text=text,
            words=[Word(w=text, start=self._seg_t0 or 0.0, end=self._seg_t1 or 0.0, conf=1.0)],
        )
        self.buffer.clear()
        self._seg_t0 = None
        self._seg_t1 = None
        return ev
