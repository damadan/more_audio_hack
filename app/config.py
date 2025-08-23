from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Settings:
    APP_HOST: str = os.environ.get("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.environ.get("APP_PORT", "8080"))
    WS_BASE_URL: str = os.environ.get("WS_BASE_URL", "ws://localhost:8080")
    VLLM_BASE_URL: str | None = os.environ.get("VLLM_BASE_URL")
    ALLOW_RUBRIC_MOCK: int = int(os.environ.get("ALLOW_RUBRIC_MOCK", "1"))


settings = Settings()

__all__ = ["Settings", "settings"]
