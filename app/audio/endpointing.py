from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, List

from .frames import AudioFrame


@dataclass
class Segment:
    frames: List[AudioFrame]
    ts_start: float
    ts_end: float


class EndpointDetector:
    def __init__(self, min_speech_ms: int = 200, max_pause_ms: int = 300, max_segment_ms: int = 5000):
        self.min_speech_ms = min_speech_ms
        self.max_pause_ms = max_pause_ms
        self.max_segment_ms = max_segment_ms
        self._buf: list[AudioFrame] = []
        self._last_speech_ts: float | None = None
        self._segment_start: float | None = None

    def _current_duration_ms(self) -> float:
        if not self._buf:
            return 0.0
        return (self._buf[-1].t1 - self._buf[0].t0) * 1000.0

    def push(self, frame: AudioFrame, is_speech: bool) -> Iterator[Segment]:
        self._buf.append(frame)
        if is_speech:
            if self._segment_start is None:
                self._segment_start = frame.t0
            self._last_speech_ts = frame.t1
        should_close = False
        close_at_last_speech = False
        if self._segment_start is not None:
            duration_ms = (frame.t1 - self._segment_start) * 1000.0
            if duration_ms >= self.max_segment_ms - 1e-6:
                should_close = True
        if self._last_speech_ts is not None and not is_speech:
            pause_ms = (frame.t1 - self._last_speech_ts) * 1000.0
            if pause_ms >= self.max_pause_ms and self._current_duration_ms() >= self.min_speech_ms:
                should_close = True
                close_at_last_speech = True
        if should_close and self._buf:
            if close_at_last_speech and self._last_speech_ts is not None:
                end_idx = len(self._buf)
                while end_idx > 0 and self._buf[end_idx - 1].t1 > self._last_speech_ts:
                    end_idx -= 1
                seg_frames = self._buf[:end_idx]
                self._buf = self._buf[end_idx:]
            else:
                seg_frames = self._buf.copy()
                self._buf.clear()
            seg = Segment(frames=seg_frames, ts_start=seg_frames[0].t0, ts_end=seg_frames[-1].t1)
            self._last_speech_ts = None
            self._segment_start = None
            yield seg
