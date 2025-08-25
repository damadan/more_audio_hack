from __future__ import annotations

from .frames import AudioFrame
import numpy as np

try:
    import webrtcvad  # type: ignore
except Exception:  # pragma: no cover - fallback
    webrtcvad = None  # type: ignore


class VADService:
    def __init__(self, aggressiveness: int = 2, frame_ms: int = 20):
        self.frame_ms = frame_ms
        self.sample_rate = 16000
        self.frame_bytes = int(self.sample_rate * frame_ms / 1000) * 2
        if webrtcvad is not None:
            self.vad = webrtcvad.Vad(aggressiveness)
        else:  # simple energy threshold fallback
            self.vad = None

    def is_speech(self, frame: AudioFrame) -> bool:
        pcm = frame.pcm
        if len(pcm) * 2 != self.frame_bytes:
            pcm = np.resize(pcm, self.frame_bytes // 2)
        if self.vad is None:
            energy = float((pcm.astype(np.float32) ** 2).mean())
            return energy > 1.0  # naive threshold
        return self.vad.is_speech(pcm.tobytes(), self.sample_rate)
