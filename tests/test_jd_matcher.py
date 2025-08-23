import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.jd_matcher import build_indicator_index, match_spans, compute_coverage
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
                indicators=[JDIndicator(name="деплой через Docker/FastAPI")],
            )
        ],
        knockouts=[],
    )
    index, meta, vocab = build_indicator_index(jd)
    matches = match_spans("serving", index, meta, vocab, top_k=1)
    assert matches[0]["indicator"] == "деплой через Docker/FastAPI"
    coverage = compute_coverage(matches, meta)
    assert coverage.per_indicator["деплой через Docker/FastAPI"] == matches[0]["similarity"]
    assert coverage.per_competency["mlops"] == matches[0]["similarity"]
