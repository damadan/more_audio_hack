from __future__ import annotations

import numpy as np

from rt_echo.common.audio import resample


TARGET_SR = 16_000


def ensure_pcm16_16k(wav_f32: np.ndarray, sr: int) -> bytes:
    """Convert ``wav_f32`` to PCM16 @ 16 kHz.

    Any input floating point waveform with sample rate ``sr`` is first
    resampled to 16 kHz if necessary, then clipped to ``[-1, 1]`` and
    converted to 16-bit signed little-endian PCM bytes.
    """

    wav_f32 = np.asarray(wav_f32, dtype=np.float32)
    if sr != TARGET_SR:
        wav_f32 = resample(wav_f32, sr, TARGET_SR)
    wav_f32 = np.clip(wav_f32, -1.0, 1.0)
    return (wav_f32 * 32767).astype(np.int16).tobytes()
