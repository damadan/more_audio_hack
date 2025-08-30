from __future__ import annotations

"""Minimal Silero TTS placeholder used for tests and local development."""

import numpy as np


class SileroTTS:
    """Simple stub implementation that outputs silence.

    Parameters
    ----------
    speaker: str
        Speaker identifier, kept for API compatibility.
    device: str
        Device identifier (e.g., "cpu"), unused in this stub.
    """

    sample_rate = 16_000

    def __init__(self, speaker: str = "ru_v3", device: str = "cpu") -> None:
        self.speaker = speaker
        self.device = device

    def synthesize(self, text: str) -> bytes:
        """Return a short silence placeholder for the given text."""

        duration = max(len(text) * 0.05, 0.2)  # seconds of audio
        samples = int(self.sample_rate * duration)
        pcm = np.zeros(samples, dtype=np.int16)
        return pcm.tobytes()
