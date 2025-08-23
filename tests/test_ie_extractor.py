from fastapi.testclient import TestClient

from main import app


def test_ie_extract_docker_skill():
    client = TestClient(app)
    resp = client.post("/ie/extract", json={"transcript": "деплой в Docker"})
    assert resp.status_code == 200
    data = resp.json()
    assert any(skill["name"] == "Docker" for skill in data["skills"])
