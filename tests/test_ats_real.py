import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from main import app
from app.config import settings

client = TestClient(app)


def test_ats_real(monkeypatch):
    settings.ATS_MODE = "real"
    settings.MOCK_ATS_URL = "http://mock"
    called = {}

    class DummyResp:
        status_code = 200
        def json(self):
            return {"status": "ok"}

    def fake_post(url, json, headers, timeout):
        called["url"] = url
        called["json"] = json
        called["headers"] = headers
        return DummyResp()

    monkeypatch.setattr("requests.post", fake_post)

    payload = {
        "candidate_id": "cand1",
        "vacancy_id": "vac1",
        "decision": "move",
        "report_link": "http://report",
    }
    resp = client.post("/ats/sync", json=payload)
    assert resp.status_code == 200
    assert called["url"] == "http://mock"
    assert called["headers"]["Idempotency-Key"] == "cand1:vac1"
