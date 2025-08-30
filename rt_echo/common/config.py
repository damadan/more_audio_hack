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
    window_sec: float = 2.0
    step_sec: float = 0.5


def load_config() -> AppConfig:
    """Load :class:`AppConfig` from environment variables."""
    profile = os.getenv("APP_PROFILE", "balanced")
    presets = {
        "fast": {
            "asr_model": "small",
            "asr_compute_type": "int8",
            "window_sec": 0.8,
            "step_sec": 0.25,
        },
        "balanced": {
            "asr_model": "medium",
            "asr_compute_type": "int8",
            "window_sec": 2.0,
            "step_sec": 0.5,
        },
        "quality": {
            "asr_model": "large-v3",
            "asr_compute_type": "fp16",
            "window_sec": 2.0,
            "step_sec": 0.5,
        },
    }
    preset = presets.get(profile, presets["balanced"])

    return AppConfig(
        asr_model=os.getenv("ASR_MODEL", preset["asr_model"]),
        asr_device=os.getenv("ASR_DEVICE", "cpu"),
        asr_compute_type=os.getenv("ASR_COMPUTE_TYPE", preset["asr_compute_type"]),
        asr_sr=int(os.getenv("ASR_SR", 16000)),
        ws_port=int(os.getenv("WS_PORT", 8000)),
        http_port=int(os.getenv("HTTP_PORT", 8080)),
        tts_engine=os.getenv("TTS_ENGINE", "piper"),
        ru_speaker=os.getenv("RU_SPEAKER", "kseniya_16khz"),
        window_sec=float(os.getenv("WINDOW_SEC", preset["window_sec"])),
        step_sec=float(os.getenv("STEP_SEC", preset["step_sec"])),
    )
