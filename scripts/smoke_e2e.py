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
    print("Running mode:", "MOCK" if mock else "REAL")

    def post(path: str, payload: dict, headers: dict | None = None):
        resp = requests.post(f"{BASE}{path}", json=payload, timeout=30, headers=headers)
        resp.raise_for_status()
        return resp.json()

    ie = post("/ie/extract", {"transcript": transcript, "include_timestamps": False})
    coverage = post("/match/coverage", {"jd": jd, "transcript": transcript})

    rubric_path = "/rubric/score"
    headers = {}
    if mock:
        rubric_path += "?mock=1"
        headers["X-Mock"] = "1"
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
