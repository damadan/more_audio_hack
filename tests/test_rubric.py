from fastapi.testclient import TestClient

from main import app


def test_monitoring_absent_triggers_low_score_or_flag():
    client = TestClient(app)
    jd = {
        "role": "secops",
        "lang": "en",
        "competencies": [
            {
                "name": "monitoring",
                "weight": 1.0,
                "indicators": [{"name": "monitoring"}],
            }
        ],
        "knockouts": [],
    }
    transcript = [
        {"type": "final", "t0": 0.0, "t1": 1.0, "text": "system analysis"}
    ]
    resp = client.post("/rubric/score", json={"jd": jd, "transcript": transcript})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    score = data["scores"].get("monitoring", 5)
    has_red_flag = any("monitoring" in rf.lower() for rf in data["red_flags"])
    assert score < 3 or has_red_flag
