import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


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


def test_dm_mock_gap():
    resp = client.post("/dm/next?mock=1", json=sample_request(), headers={"X-Mock": "1"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["target_skill"] == "monitoring"
    assert data["action"] in {"ask", "end"}
    assert "reason" in data
