import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_extract_docker_skill():
    resp = client.post(
        "/ie/extract",
        json={"transcript": "Мы используем Docker для деплоя", "include_timestamps": False},
    )
    assert resp.status_code == 200
    data = resp.json()
    docker = next((s for s in data["skills"] if s["name"] == "Docker"), None)
    assert docker is not None
    assert docker["evidence"]
    assert docker["evidence"][0]["quote"] == "Docker"
