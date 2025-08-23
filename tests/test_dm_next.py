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
                {"name": "skill1", "weight": 1.0, "indicators": [{"name": "ind1"}]}
            ],
            "knockouts": [],
        },
        "context": {"turns": [{"role": "user", "text": "hi"}]},
    }


def test_dm_next_success(monkeypatch):
    monkeypatch.setenv("VLLM_BASE_URL", "http://mock")
    monkeypatch.setenv("VLLM_MODEL", "test-model")

    def fake_generate_json(self, prompt, json_schema, temperature=0.2, max_tokens=1024):
        return {
            "action": "ask",
            "question": "What is your experience?",
            "followups": ["Tell me more"],
            "target_skill": "skill1",
            "reason": "Need info",
        }

    monkeypatch.setattr(LLMClient, "generate_json", fake_generate_json)
    resp = client.post("/dm/next", json=sample_request())
    assert resp.status_code == 200
    assert resp.json()["action"] == "ask"


def test_dm_next_invalid_json(monkeypatch):
    monkeypatch.setenv("VLLM_BASE_URL", "http://mock")
    monkeypatch.setenv("VLLM_MODEL", "test-model")
    monkeypatch.setattr(
        LLMClient,
        "generate_json",
        lambda self, prompt, json_schema, temperature=0.2, max_tokens=1024: {"foo": "bar"},
    )

    resp = client.post("/dm/next", json=sample_request())
    assert resp.status_code == 500
