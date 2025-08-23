from __future__ import annotations

import os
import time
from typing import Dict

import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class ATSSyncRequest(BaseModel):
    candidate_id: str
    vacancy_id: str
    decision: str
    report_link: str


@router.post("/ats/sync")
def ats_sync(req: ATSSyncRequest) -> Dict[str, str]:
    url = os.getenv("MOCK_ATS_URL")
    if not url:
        raise HTTPException(status_code=500, detail="MOCK_ATS_URL not set")

    payload = {
        "candidate_id": req.candidate_id,
        "vacancy_id": req.vacancy_id,
        "decision": req.decision,
        "report_link": req.report_link,
    }
    headers = {"Idempotency-Key": f"{req.candidate_id}-{req.vacancy_id}"}

    for attempt in range(3):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=5)
            if resp.status_code >= 500:
                raise RuntimeError("server error")
            return {"status": "ok"}
        except Exception:
            if attempt == 2:
                raise HTTPException(status_code=502, detail="ATS unreachable")
            time.sleep(2 ** attempt)

    return {"status": "error"}

