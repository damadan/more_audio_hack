import numpy as np

try:
    from scipy import signal  # type: ignore
except Exception:  # pragma: no cover
    signal = None  # type: ignore

try:
    import resampy  # type: ignore
except Exception:  # pragma: no cover
    resampy = None  # type: ignore


def float32_to_pcm16(audio: np.ndarray) -> bytes:
    """Convert float32 numpy array to 16-bit PCM bytes."""
    audio = np.asarray(audio, dtype=np.float32)
    audio = np.clip(audio, -1.0, 1.0)
    return (audio * 32767).astype(np.int16).tobytes()


def pcm16_to_float32(pcm: bytes) -> np.ndarray:
    """Convert 16-bit PCM bytes to float32 numpy array."""
    audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32)
    return audio / 32767.0


def resample(audio: np.ndarray, src_sr: int, dst_sr: int) -> np.ndarray:
    """Resample audio from src_sr to dst_sr.

    Uses resampy or scipy if available, otherwise falls back to linear
    interpolation with NumPy.
    """
    audio = np.asarray(audio, dtype=np.float32)
    if src_sr == dst_sr:
        return audio

    if resampy is not None:  # pragma: no cover - only used when available
        return resampy.resample(audio, src_sr, dst_sr)

    if signal is not None:  # pragma: no cover - only used when available
        duration = audio.shape[0] / float(src_sr)
        n_samples = int(round(duration * dst_sr))
        return signal.resample(audio, n_samples)

    # Fallback: simple linear interpolation
    ratio = dst_sr / float(src_sr)
    x_old = np.linspace(0, len(audio), num=len(audio), endpoint=False)
    x_new = np.linspace(0, len(audio), num=int(len(audio) * ratio), endpoint=False)
    return np.interp(x_new, x_old, audio).astype(np.float32)
