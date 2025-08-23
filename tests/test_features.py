import os
import sys

sys.path.append(os.getcwd())

from app.features import build_features
from app.schemas import JD, IE, Coverage, Rubric, Competency


def test_years_feature_converted_to_float():
    jd = JD(
        role="dev",
        lang="en",
        competencies=[Competency(name="python", weight=1.0, indicators=[])],
        knockouts=[],
    )
    ie = IE(skills=[], tools=[], years={"python": 5}, projects=[], roles=[])
    coverage = Coverage(per_indicator={}, per_competency={})
    rubric = Rubric(scores={}, red_flags=[], evidence=[])
    feats = build_features(jd, ie, coverage, rubric, {})
    assert feats["years_python"] == 5.0
