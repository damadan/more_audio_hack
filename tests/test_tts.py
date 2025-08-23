import os
import sys

from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import app


def test_tts_returns_audio_bytes():
    client = TestClient(app)
    response = client.post("/tts", json={"text": "привет"})
    assert response.status_code == 200
    assert len(response.content) > 0
