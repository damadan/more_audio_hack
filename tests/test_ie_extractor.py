from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_docker_skill_extraction():
    resp = client.post(
        "/ie/extract",
        json={"transcript": "деплой в Docker", "include_timestamps": False},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert any(skill["name"] == "Docker" for skill in data["skills"])
