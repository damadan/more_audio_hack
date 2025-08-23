from __future__ import annotations

import asyncio
import logging
from typing import Tuple

import requests
from fastapi import HTTPException

from .config import settings
from .schemas import ATSSyncRequest

logger = logging.getLogger(__name__)


async def sync(req: ATSSyncRequest) -> Tuple[int, dict]:
    """Synchronise decision with ATS.

    Returns ``(status_code, payload)``."""
    if settings.ATS_MODE != "real" or not settings.MOCK_ATS_URL:
        logger.warning("ATS in mock mode: ATS_MODE=%s, MOCK_ATS_URL=%s", settings.ATS_MODE, settings.MOCK_ATS_URL)
        return 202, {"status": "mock-accepted"}

    url = settings.MOCK_ATS_URL
    headers = {"Idempotency-Key": f"{req.candidate_id}:{req.vacancy_id}"}
    payload = req.model_dump()
    delay = 1.0
    for attempt in range(3):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=5)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                except Exception:
                    data = {"status": "ok"}
                return 200, data
            if resp.status_code >= 500:
                raise Exception("server error")
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        except HTTPException:
            raise
        except Exception:
            if attempt == 2:
                raise HTTPException(status_code=502, detail="ATS sync failed")
            await asyncio.sleep(delay)
            delay *= 2
    return 200, {"status": "ok"}


__all__ = ["sync"]
