import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_tts_returns_audio():
    resp = client.post("/tts", json={"text": "привет"})
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "audio/wav"
    assert len(resp.content) > 1000


def test_tts_pcm16k():
    resp = client.post("/tts", json={"text": "привет", "format": "pcm16k"})
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "audio/L16"
    assert len(resp.content) > 1000

