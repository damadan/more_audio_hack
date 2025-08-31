from typing import Tuple, cast  # noqa: F401 (for compatibility, may be unused)

import numpy as np
from scipy.signal import resample_poly


def pcm16_to_float32(b: bytes) -> np.ndarray:
    arr = np.frombuffer(b, dtype=np.int16)
    return arr.astype(np.float32) / 32768.0


def float32_to_pcm16(w: np.ndarray) -> bytes:
    w = np.clip(w, -1.0, 1.0).astype(np.float32)
    return (w * 32767.0).astype(np.int16).tobytes()


def resample(w: np.ndarray, src_sr: int, dst_sr: int) -> np.ndarray:
    if src_sr == dst_sr:
        return w
    from math import gcd

    g = gcd(src_sr, dst_sr)
    up, down = dst_sr // g, src_sr // g
    return cast(np.ndarray, resample_poly(w, up, down)).astype(np.float32)


__all__ = ["pcm16_to_float32", "float32_to_pcm16", "resample"]

