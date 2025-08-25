from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np

from ..audio.endpointing import Segment
from ..api.schemas import TranscriptEvent, Word


@dataclass(slots=True)
class RefinerConfig:
    model_size: str = "small"
    compute_type: str = "int8"
    vad_filter: bool = True


class HybridRefiner:
    """Stub refiner using faster-whisper API in production.

    For unit tests we avoid heavy dependencies and simply return a dummy refined
    text based on the length of the audio buffer.
    """

    def __init__(self, cfg: RefinerConfig):
        self.cfg = cfg

    def refine(self, seg: Segment, lang: str) -> TranscriptEvent:
        pcm = np.concatenate([f.pcm for f in seg.frames])
        length = pcm.shape[0]
        refined_text = f"refined-{length}"
        return TranscriptEvent(
            type="segment_final",
            session_id="",
            ts_start=seg.ts_start,
            ts_end=seg.ts_end,
            text="",
            revised_text=refined_text,
            words=[Word(w=refined_text, start=seg.ts_start, end=seg.ts_end, conf=1.0)],
            diff_from_online=self.compute_diff("", refined_text),
        )

    @staticmethod
    def compute_diff(online_text: str, refined_text: str) -> str:
        if online_text == refined_text:
            return ""
        return f"+{refined_text}"
