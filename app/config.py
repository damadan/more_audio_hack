from __future__ import annotations

from pydantic import BaseSettings


class Settings(BaseSettings):
    postgres_dsn: str = "sqlite://"
    redis_dsn: str = "redis://localhost:6379/0"
    s3_bucket: str = "audio"
    s3_endpoint: str | None = None
    vosk_model_ru: str = ""
    vosk_model_en: str = ""
    whisper_model_size: str = "tiny"
    profile_default: str = "hybrid"
    postproc_enabled: bool = True
    hybrid_enabled: bool = True


settings = Settings()
