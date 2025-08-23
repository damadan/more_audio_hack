import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.match import build_indicator_index, match_spans, compute_coverage
from app.schemas import JD, JDCompetency, JDIndicator


@pytest.mark.integration
def test_serving_matches_docker_fastapi():
    jd = JD(
        role="dev",
        lang="ru",
        competencies=[
            JDCompetency(
                name="mlops",
                weight=1.0,
                indicators=[JDIndicator(name="serving")],
            )
        ],
        knockouts=[],
    )
    backend = "BGE_M3"
    index, meta = build_indicator_index(jd, backend)
    matches = match_spans("деплой через Docker/FastAPI", index, meta, backend, top_k=1)
    coverage = compute_coverage(matches, meta)
    assert coverage.per_indicator["serving"] > 0.6
    assert coverage.per_competency["mlops"] > 0.6
