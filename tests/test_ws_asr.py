import os
import sys

from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.asr_gateway import router


def test_ws_ping_pong():
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    with client.websocket_connect("/stream/test") as ws:
        ws.send_text("PING")
        data = ws.receive_json()
        assert data["type"] == "partial"
        ws.send_text("END")
        data = ws.receive_json()
        assert data["type"] == "final"
