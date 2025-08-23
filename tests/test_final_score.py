import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from main import app
from app.scoring import build_features
from app.schemas import (
    JD,
    JDCompetency,
    JDIndicator,
    IE,
    Coverage,
    Rubric,
    RubricEvidence,
)

client = TestClient(app)


def sample_jd():
    return JD(
        role="dev",
        lang="en",
        competencies=[
            JDCompetency(
                name="monitoring",
                weight=1.0,
                indicators=[JDIndicator(name="monitoring")],
            )
        ],
        knockouts=[],
    )


def test_build_features_years():
    jd = sample_jd()
    ie = IE(skills=[], tools=[], years={"python": 5}, projects=[], roles=[])
    coverage = Coverage(per_indicator={}, per_competency={})
    rubric = Rubric(scores={}, red_flags=[], evidence=[])
    feats = build_features(jd, ie, coverage, rubric, {})
    assert feats["years_python"] == 5.0


def test_low_coverage_not_move():
    payload = {
        "jd": sample_jd().model_dump(),
        "ie": IE(skills=[], tools=[], years={}, projects=[], roles=[]).model_dump(),
        "coverage": {
            "per_indicator": {},
            "per_competency": {"monitoring": 0.2},
        },
        "rubric": {
            "scores": {"monitoring": 5},
            "red_flags": [],
            "evidence": [],
        },
        "aux": {},
    }
    resp = client.post("/score/final", json=payload)
    assert resp.status_code == 200
    assert resp.json()["decision"] != "move"
