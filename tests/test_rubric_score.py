import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from main import app
from app.llm_client import LLMClient


client = TestClient(app)


def sample_request():
    return {
        "jd": {
            "role": "dev",
            "lang": "en",
            "competencies": [
                {"name": "monitoring", "weight": 1.0, "indicators": [{"name": "monitoring"}]}
            ],
            "knockouts": [],
        },
        "transcript": "I worked on deployments and logging",
    }


def test_rubric_score_monitoring_missing(monkeypatch):
    monkeypatch.setenv("VLLM_BASE_URL", "http://mock")
    monkeypatch.setenv("VLLM_MODEL", "test-model")
    calls = {"n": 0}

    def fake_generate_json(self, prompt, json_schema, temperature=0.2, max_tokens=1024):
        calls["n"] += 1
        transcript_part = prompt.split("Transcript:\n", 1)[-1].lower()
        if "monitoring" in transcript_part:
            return {"scores": {"monitoring": 5}, "red_flags": [], "evidence": []}
        return {
            "scores": {"monitoring": 1},
            "red_flags": ["no monitoring experience"],
            "evidence": [],
        }

    monkeypatch.setattr(LLMClient, "generate_json", fake_generate_json)

    resp = client.post("/rubric/score", json=sample_request())
    assert resp.status_code == 200
    data = resp.json()
    assert data["scores"]["monitoring"] <= 1
    assert any("monitoring" in rf.lower() for rf in data["red_flags"])
    assert calls["n"] == 2

