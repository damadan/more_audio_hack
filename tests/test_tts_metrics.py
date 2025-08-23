import sys
from pathlib import Path
import re

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_tts_metrics():
    resp = client.post("/tts", json={"text": "привет"})
    assert resp.status_code == 200
    assert len(resp.content) > 100
    metrics = client.get("/metrics").text
    lines = [l for l in metrics.splitlines() if l.startswith("tts_bytes_total")]
    assert lines, metrics
    value = float(lines[0].split()[-1])
    assert value > 0
