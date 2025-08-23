import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_ws_echo():
    with client.websocket_connect("/stream/test-session") as ws:
        ws.send_text("hello")
        data = ws.receive_json()
        assert data["type"] == "partial"
        assert data["text"] == "hello"
        ws.send_text("END")
        data = ws.receive_json()
        assert data["type"] == "final"
        assert data["text"] == "hello"
