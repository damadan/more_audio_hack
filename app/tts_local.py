from __future__ import annotations

import importlib
import io
import math
import wave
from typing import Iterator, Literal, Optional

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

SAMPLE_RATE = 16_000


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None
    format: Literal["wav", "pcm16k"] = "wav"


def _chunk_bytes(data: bytes, chunk_size: int = 4096) -> Iterator[bytes]:
    for i in range(0, len(data), chunk_size):
        yield data[i : i + chunk_size]


def _pcm_to_wav(pcm: bytes, sample_rate: int = SAMPLE_RATE) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm)
    return buffer.getvalue()


def _sine_wave_pcm(
    duration: float = 1.0, freq: float = 440.0, sample_rate: int = SAMPLE_RATE
) -> bytes:
    n_samples = int(sample_rate * duration)
    buf = io.BytesIO()
    for i in range(n_samples):
        value = int(32767 * math.sin(2 * math.pi * freq * i / sample_rate))
        buf.write(value.to_bytes(2, "little", signed=True))
    return buf.getvalue()


def _synthesize_coqui(text: str, voice: Optional[str]) -> Optional[bytes]:
    spec = importlib.util.find_spec("TTS")
    if spec is None:
        return None
    try:
        from TTS.api import TTS as CoquiTTS

        tts = CoquiTTS(
            model_name="tts_models/multilingual/multi-dataset/xtts_v2",
            progress_bar=False,
            gpu=False,
        )
        try:
            chunks = tts.tts_stream(text=text, speaker=voice, language="ru")
        except Exception:
            audio = tts.tts(text=text, speaker=voice, language="ru")
            chunks = [audio]
        import numpy as np

        pcm_buf = io.BytesIO()
        for chunk in chunks:
            arr = np.array(chunk)
            arr = np.clip(arr, -1.0, 1.0)
            pcm_buf.write((arr * 32767).astype("<i2").tobytes())
        return pcm_buf.getvalue()
    except Exception:
        return None


def _synthesize_silero(text: str, voice: Optional[str]) -> Optional[bytes]:
    spec = importlib.util.find_spec("torch")
    if spec is None:
        return None
    try:
        import torch

        model, example_text, sample_rate = torch.hub.load(
            repo_or_dir="snakers4/silero-models",
            model="silero_tts",
            language="ru",
            speaker=voice or "baya",
            trust_repo=True,
        )
        audio = model.apply_tts(
            text=text, speaker=voice or "baya", sample_rate=SAMPLE_RATE
        )
        import numpy as np

        arr = audio.cpu().numpy()
        arr = np.clip(arr, -1.0, 1.0)
        return (arr * 32767).astype("<i2").tobytes()
    except Exception:
        return None


router = APIRouter()


@router.post("/tts")
async def tts_endpoint(req: TTSRequest):
    pcm = _synthesize_coqui(req.text, req.voice)
    if pcm is None:
        pcm = _synthesize_silero(req.text, req.voice)
    if pcm is None:
        pcm = _sine_wave_pcm()

    if req.format == "wav":
        data = _pcm_to_wav(pcm)
        media_type = "audio/wav"
    else:
        data = pcm
        media_type = "audio/L16"

    return StreamingResponse(_chunk_bytes(data), media_type=media_type)
