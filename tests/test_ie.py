import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_ie_pipeline_extracts_entities():
    text = "Проект мониторинга в Grafana, деплой через Docker, AUC 0.86"
    resp = client.post(
        "/ie/extract",
        json={"transcript": text, "include_timestamps": False},
    )
    assert resp.status_code == 200
    data = resp.json()
    skills = {s["name"] for s in data["skills"]}
    assert "Docker" in skills
    assert "Grafana" in data["tools"]
    assert data["projects"]
    metrics = data["projects"][0]["metrics"]
    assert metrics.get("AUC") == 0.86
