import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from main import app
from app.config import settings


client = TestClient(app)


def test_default_ws_url(monkeypatch):
    monkeypatch.setattr(settings, "WS_BASE_URL", "ws://localhost:8080")
    resp = client.post("/interview/start")
    assert resp.status_code == 200
    ws_url = resp.json()["ws_url"]
    assert ws_url.startswith("ws://localhost:8080/stream/")


def test_custom_ws_url(monkeypatch):
    monkeypatch.setattr(settings, "WS_BASE_URL", "ws://example:9999")
    resp = client.post("/interview/start")
    assert resp.status_code == 200
    ws_url = resp.json()["ws_url"]
    assert ws_url.startswith("ws://example:9999/stream/")
