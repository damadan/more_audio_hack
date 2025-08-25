import numpy as np
from typing import Optional


class OpusDecoder:
    """Simplified Opus decoder stub.

    In tests we avoid real Opus decoding and expect raw PCM16 data. The class
    mirrors the API that would wrap libopus in production but simply interprets
    incoming bytes as little-endian int16 samples.
    """

    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels

    def decode(self, payload: bytes) -> np.ndarray:
        pcm = np.frombuffer(payload, dtype=np.int16)
        if self.channels > 1:
            pcm = pcm.reshape(-1, self.channels).mean(axis=1).astype(np.int16)
        return ensure_mono_16k(pcm, self.sample_rate)


def ensure_mono_16k(pcm: np.ndarray, in_sr: int) -> np.ndarray:
    """Downmix and resample to mono 16kHz int16.

    For tests we implement a very small subset: if `in_sr` already 16000 the
    data is returned as-is. Otherwise a naive resampler based on numpy
    interpolation is used. This is sufficient for unit tests and avoids heavy
    dependencies.
    """

    if pcm.ndim > 1:
        pcm = pcm.mean(axis=1)
    if in_sr == 16000:
        return pcm.astype(np.int16)
    # naive resample
    duration = pcm.shape[0] / in_sr
    target_samples = int(duration * 16000)
    x_old = np.linspace(0, duration, num=pcm.shape[0], endpoint=False)
    x_new = np.linspace(0, duration, num=target_samples, endpoint=False)
    resampled = np.interp(x_new, x_old, pcm).astype(np.int16)
    return resampled
