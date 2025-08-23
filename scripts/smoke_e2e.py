"""End-to-end smoke test calling main API endpoints."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import requests

BASE = "http://localhost:8080"


def _load_json(path: Path):
    with path.open("r", encoding="utf8") as f:
        return json.load(f)


def _should_mock() -> bool:
    base = os.environ.get("VLLM_BASE_URL")
    if not base:
        return True
    try:
        resp = requests.get(f"{base}/v1/models", timeout=5)
        resp.raise_for_status()
    except Exception:
        return True
    return False


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    jd = _load_json(root / "data" / "jd_ml_engineer.json")
    transcript_path = root / "transcripts" / "ru_sample.jsonl"
    with transcript_path.open("r", encoding="utf8") as f:
        transcript = " ".join(json.loads(line)["text"] for line in f)

    mock = _should_mock()
    print("SMOKE MODE:", "MOCK" if mock else "REAL")

    def post(path: str, payload: dict, headers: dict | None = None):
        resp = requests.post(f"{BASE}{path}", json=payload, timeout=30, headers=headers)
        resp.raise_for_status()
        if resp.content:
            try:
                return resp.json()
            except Exception:
                return {}
        return {}

    ie = post("/ie/extract", {"transcript": transcript, "include_timestamps": False})
    coverage = post("/match/coverage", {"jd": jd, "transcript": transcript})

    headers = {}
    dm_path = "/dm/next"
    rubric_path = "/rubric/score"
    if mock:
        dm_path += "?mock=1"
        rubric_path += "?mock=1"
        headers["X-Mock"] = "1"
    dm_resp = post(dm_path, {"jd": jd, "context": {"turns": [{"role": "user", "text": "hi"}]}, "coverage": coverage}, headers=headers)
    rubric = post(rubric_path, {"jd": jd, "transcript": ie, "coverage": coverage}, headers=headers)

    final = post("/score/final", {"jd": jd, "ie": ie, "coverage": coverage, "rubric": rubric})
    report_resp = requests.post(
        f"{BASE}/report",
        json={
            "candidate": "John Doe",
            "vacancy": jd["role"],
            "rubric": rubric,
            "final": final,
            "audio_url": "audio",
        },
        timeout=30,
    )
    report_resp.raise_for_status()
    report = report_resp.text

    ats_payload = {
        "candidate_id": "cand",
        "vacancy_id": "vac",
        "decision": final.get("decision", "move"),
        "report_link": "http://example.com",
    }
    ats_resp = post("/ats/sync", ats_payload)
    if os.environ.get("ATS_MODE", "mock") == "mock":
        assert ats_resp.get("status") == "mock-accepted"

    print("overall:", final.get("overall"))
    print("decision:", final.get("decision"))
    print("report length:", len(report))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print("smoke test failed", exc)
        raise SystemExit(1)
