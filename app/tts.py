from __future__ import annotations

import io
import logging
import math
import struct
import wave
from typing import Generator, Optional, Tuple

logger = logging.getLogger(__name__)

_xtts = None
_silero = None
_silero_sr = 16000


def _try_xtts(text: str, voice: Optional[str]) -> Optional[Tuple[bytes, int]]:
    """Try synthesizing speech with XTTS-v2.

    Returns a tuple ``(pcm_bytes, sample_rate)`` on success or ``None`` if the
    model is not available or synthesis fails.
    """
    global _xtts
    try:
        if _xtts is None:
            from TTS.api import TTS  # type: ignore
            _xtts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
        wav = _xtts.tts(text, speaker_wav=voice, language="ru")
        import numpy as np  # type: ignore
        pcm = (np.asarray(wav) * 32767).astype("<i2").tobytes()
        sr = getattr(getattr(_xtts, "synthesizer", None), "output_sample_rate", 24000)
        return pcm, sr
    except Exception as exc:  # pragma: no cover - optional dependency
        logger.warning("XTTS not available: %s", exc)
        return None


def _try_silero(text: str, voice: Optional[str]) -> Optional[Tuple[bytes, int]]:
    """Fallback to Silero TTS when XTTS is unavailable."""
    global _silero, _silero_sr
    try:
        import torch  # type: ignore
        if _silero is None:
            _silero, symbols, _silero_sr, example = torch.hub.load(
                repo_or_dir="snakers4/silero-models",
                model="silero_tts",
                language="ru",
                speaker="v3_1_ru",
            )
        audio = _silero.apply_tts(text=text, speaker=voice or "v3_1_ru", sample_rate=_silero_sr)
        pcm = (audio.numpy() * 32767).astype("<i2").tobytes()
        return pcm, _silero_sr
    except Exception as exc:  # pragma: no cover - optional dependency
        logger.warning("Silero TTS not available: %s", exc)
        return None


def _sine_fallback(text: str, sample_rate: int = 16_000) -> Tuple[bytes, int]:
    """Generate a simple sine wave when no TTS engine is available."""
    duration = 1.0
    frequency = 440.0
    amplitude = 32767
    n_samples = int(sample_rate * duration)
    buf = bytearray()
    for i in range(n_samples):
        value = int(amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
        buf.extend(struct.pack("<h", value))
    return bytes(buf), sample_rate


def synthesize(text: str, voice: Optional[str] = None) -> Tuple[bytes, int]:
    """Synthesize speech using XTTS-v2 with Silero fallback.

    Returns ``(pcm_bytes, sample_rate)``.
    """
    for func in (_try_xtts, _try_silero):
        result = func(text, voice)
        if result is not None:
            return result
    return _sine_fallback(text)


def stream_bytes(data: bytes, chunk_size: int = 2048) -> Generator[bytes, None, None]:
    """Yield ``data`` in small chunks suitable for streaming."""
    for i in range(0, len(data), chunk_size):
        yield data[i : i + chunk_size]


def pcm_to_wav(pcm: bytes, sample_rate: int) -> bytes:
    """Wrap raw PCM data in a WAV container and return bytes."""
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm)
    return buffer.getvalue()

