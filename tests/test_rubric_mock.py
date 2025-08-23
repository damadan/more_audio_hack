import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from main import app
from app.llm_client import LLMClient
from app.config import settings

client = TestClient(app)


def sample_req():
    return {
        "jd": {
            "role": "dev",
            "lang": "en",
            "competencies": [
                {"name": "mlops", "weight": 1.0, "indicators": [{"name": "serving"}]}
            ],
            "knockouts": [],
        },
        "transcript": {
            "skills": [
                {
                    "name": "Docker",
                    "evidence": [{"quote": "used docker", "t0": 0, "t1": 1}],
                }
            ],
            "tools": [],
            "years": {},
            "projects": [],
            "roles": [],
        },
    }


def test_rubric_mock(monkeypatch):
    monkeypatch.setattr(settings, "ALLOW_RUBRIC_MOCK", 1)
    # ensure LLM is not called
    def _fail(*a, **k):
        raise AssertionError("LLM called")

    monkeypatch.setattr(LLMClient, "generate_json", _fail)
    resp = client.post("/rubric/score?mock=1", json=sample_req(), headers={"X-Mock": "1"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["scores"]["mlops"] == 4
    assert data["red_flags"] == []
    assert data["evidence"][0]["t0"] == 0


def test_rubric_real(monkeypatch):
    monkeypatch.setattr(settings, "ALLOW_RUBRIC_MOCK", 1)
    monkeypatch.setenv("VLLM_BASE_URL", "http://mock")
    monkeypatch.setenv("VLLM_MODEL", "test-model")
    calls = {"n": 0}

    def fake_gen(self, prompt, json_schema, temperature=0.2, max_tokens=1024):
        calls["n"] += 1
        return {"scores": {"mlops": 5}, "red_flags": [], "evidence": []}

    monkeypatch.setattr(LLMClient, "generate_json", fake_gen)
    resp = client.post("/rubric/score", json=sample_req())
    assert resp.status_code == 200
    data = resp.json()
    assert data["scores"]["mlops"] == 5
    # called twice because of merge
    assert calls["n"] == 2
