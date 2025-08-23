import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
import main
from app.llm_client import LLMClient

client = TestClient(main.app)


def sample_request():
    return {
        "jd": {
            "role": "dev",
            "lang": "en",
            "competencies": [
                {"name": "ops", "weight": 1.0, "indicators": [{"name": "monitoring"}]}
            ],
            "knockouts": [],
        },
        "context": {"turns": [{"role": "user", "text": "hi"}]},
        "coverage": {
            "per_indicator": {"monitoring": 0.0},
            "per_competency": {"ops": 0.0},
        },
    }


def test_dm_real(monkeypatch):
    monkeypatch.setenv("VLLM_BASE_URL", "http://mock")
    monkeypatch.setenv("VLLM_MODEL", "test")
    monkeypatch.setattr(main, "_vllm_available", lambda: True)

    def fake_generate_json(self, prompt, json_schema, temperature=0.2, max_tokens=1024):
        return {
            "action": "ask",
            "question": "Q",
            "followups": [],
            "target_skill": "monitoring",
            "reason": "gap",
        }

    monkeypatch.setattr(LLMClient, "generate_json", fake_generate_json)
    resp = client.post("/dm/next", json=sample_request())
    assert resp.status_code == 200
    assert resp.json()["target_skill"] == "monitoring"
