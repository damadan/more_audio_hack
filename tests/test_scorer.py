import os
import sys

sys.path.append(os.getcwd())

from fastapi.testclient import TestClient

from main import app
from app.schemas import JD, IE, Coverage, Rubric, Competency


def test_low_monitoring_coverage_not_move():
    client = TestClient(app)
    jd = JD(role="dev", lang="en", competencies=[Competency(name="monitoring", weight=1.0, indicators=[])], knockouts=[])
    ie = IE(skills=[], tools=[], years={"python": 5}, projects=[], roles=[])
    coverage = Coverage(per_indicator={}, per_competency={"monitoring": 0.1})
    rubric = Rubric(scores={"monitoring": 5}, red_flags=[], evidence=[])
    payload = {
        "jd": jd.model_dump(),
        "ie": ie.model_dump(),
        "coverage": coverage.model_dump(),
        "rubric": rubric.model_dump(),
        "aux": {}
    }
    response = client.post("/score/final", json=payload)
    assert response.status_code == 200
    assert response.json()["decision"] != "move"
