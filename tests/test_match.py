import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.schemas import JD, Competency, Indicator
from app.match import match_coverage, CoverageRequest


def test_serving_matches_deploy():
    jd = JD(
        role="devops",
        lang="en",
        competencies=[
            Competency(name="Infrastructure", weight=1.0, indicators=[Indicator(name="serving")])
        ],
        knockouts=[],
    )
    answers = "I can deploy through Docker and FastAPI."
    req = CoverageRequest(jd=jd, answers=answers)
    cov = asyncio.run(match_coverage(req))
    assert cov.per_indicator["serving"] > 0.5
