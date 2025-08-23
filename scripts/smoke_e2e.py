"""End-to-end smoke test calling main API endpoints."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import requests

BASE = "http://localhost:8080"


def _load_json(path: Path):
    with path.open("r", encoding="utf8") as f:
        return json.load(f)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    jd = _load_json(root / "data" / "jd_ml_engineer.json")
    transcript_path = root / "transcripts" / "ru_sample.jsonl"
    with transcript_path.open("r", encoding="utf8") as f:
        transcript = " ".join(json.loads(line)["text"] for line in f)

    def post(path: str, payload: dict):
        resp = requests.post(f"{BASE}{path}", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    ie = post("/ie/extract", {"transcript": transcript, "include_timestamps": False})
    coverage = post("/match/coverage", {"jd": jd, "transcript": transcript})
    rubric = post("/rubric/score", {"jd": jd, "transcript": ie, "coverage": coverage})
    final = post("/score/final", {"jd": jd, "ie": ie, "coverage": coverage, "rubric": rubric})
    report = post(
        "/report",
        {
            "candidate": "John Doe",
            "vacancy": jd["role"],
            "rubric": rubric,
            "final": final,
            "audio_url": "audio",
        },
    )

    print("overall:", final.get("overall"))
    print("decision:", final.get("decision"))
    print("report length:", len(report))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print("smoke test failed", exc)
        raise
