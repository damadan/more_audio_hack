import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.context import build_context
from app.schemas import JD, JDCompetency, JDIndicator


def test_build_context_highlights_gaps():
    jd = JD(
        role="dev",
        lang="en",
        competencies=[
            JDCompetency(
                name="skill",
                weight=1.0,
                indicators=[JDIndicator(name="monitoring")],
            )
        ],
        knockouts=[],
    )
    context = build_context(jd, gaps=["monitoring"])
    assert "monitoring" in context.lower()
