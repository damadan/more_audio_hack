from fastapi.testclient import TestClient

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from main import app


def test_metrics_endpoint_exposes_prometheus_metrics():
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.text
    assert "http_requests_total" in data
    assert "request_latency_seconds" in data
    assert "asr_partial_latency" in data
    assert "asr_final_latency" in data
    assert "llm_latency" in data
    assert "score_overall_hist" in data
