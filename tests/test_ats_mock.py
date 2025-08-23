import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from main import app
from app.config import settings

client = TestClient(app)


def test_ats_mock(monkeypatch):
    settings.ATS_MODE = "mock"
    settings.MOCK_ATS_URL = None
    called = False

    def fake_post(*args, **kwargs):  # pragma: no cover
        nonlocal called
        called = True
        class Resp:
            status_code = 200
            def json(self):
                return {"status": "ok"}
        return Resp()

    monkeypatch.setattr("requests.post", fake_post)
    payload = {
        "candidate_id": "c1",
        "vacancy_id": "v1",
        "decision": "move",
        "report_link": "http://r",
    }
    resp = client.post("/ats/sync", json=payload)
    assert resp.status_code == 202
    assert resp.json()["status"] == "mock-accepted"
    assert called is False
