from fastapi.testclient import TestClient
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from main import app
from app.schemas import Rubric, RubricEvidence, FinalScore, CompScore

client = TestClient(app)

def make_payload():
    rubric = Rubric(
        scores={"Python": 4, "ML": 3},
        red_flags=[],
        evidence=[
            RubricEvidence(quote="foo", t0=0.0, t1=1.0, competency="Python"),
            RubricEvidence(quote="bar", t0=1.0, t1=2.0, competency="ML"),
        ],
    )
    final = FinalScore(
        overall=0.75,
        decision="move",
        reasons=["good"],
        by_comp=[CompScore(name="Python", score=0.8)],
    )
    return {"candidate": "John", "vacancy": "Dev", "rubric": rubric.model_dump(), "final": final.model_dump()}


def test_report_contains_competencies_and_overall():
    payload = make_payload()
    resp = client.post("/report", json=payload)
    assert resp.status_code == 200
    html = resp.text
    assert "Overall: 75%" in html
    for comp in ["Python", "ML"]:
        assert comp in html
