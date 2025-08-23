import types
from fastapi.testclient import TestClient
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from main import app
import os

client = TestClient(app)

class DummyResp:
    def __init__(self, status_code=200):
        self.status_code = status_code
        self.text = "ok"

def test_ats_sync_sends_payload(monkeypatch):
    called = {}

    def fake_post(url, json, headers, timeout):
        called['url'] = url
        called['json'] = json
        called['headers'] = headers
        return DummyResp()

    monkeypatch.setenv("MOCK_ATS_URL", "http://mock")
    monkeypatch.setattr("requests.post", fake_post)

    payload = {
        "candidate_id": "cand1",
        "vacancy_id": "vac1",
        "decision": "move",
        "report_link": "http://report"
    }
    resp = client.post("/ats/sync", json=payload)
    assert resp.status_code == 200
    assert called['url'] == "http://mock"
    assert called['json'] == payload
    assert called['headers']['Idempotency-Key'] == "cand1:vac1"
