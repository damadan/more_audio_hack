from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass
class AppConfig:
    """Application configuration loaded from environment variables."""

    asr_model: str = "small"
    asr_device: str = "cpu"
    asr_compute_type: str = "int8"
    asr_sr: int = 16000
    ws_port: int = 8000
    http_port: int = 8080
    tts_engine: str = "piper"
    ru_speaker: str = "kseniya_16khz"


def load_config() -> AppConfig:
    """Load :class:`AppConfig` from environment variables."""

    return AppConfig(
        asr_model=os.getenv("ASR_MODEL", "small"),
        asr_device=os.getenv("ASR_DEVICE", "cpu"),
        asr_compute_type=os.getenv("ASR_COMPUTE_TYPE", "int8"),
        asr_sr=int(os.getenv("ASR_SR", 16000)),
        ws_port=int(os.getenv("WS_PORT", 8000)),
        http_port=int(os.getenv("HTTP_PORT", 8080)),
        tts_engine=os.getenv("TTS_ENGINE", "piper"),
        ru_speaker=os.getenv("RU_SPEAKER", "kseniya_16khz"),
    )
