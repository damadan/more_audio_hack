from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))
from main import app


def _sample_jd():
    return {
        "role": "Developer",
        "lang": "en",
        "competencies": [
            {
                "name": "Programming",
                "weight": 1.0,
                "indicators": [{"name": "Python"}],
            }
        ],
        "knockouts": [],
    }


def test_dm_next_empty_context():
    client = TestClient(app)
    payload = {"jd": _sample_jd(), "context": {"turns": []}}
    response = client.post("/dm/next", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "ask"
    assert data["question"]
