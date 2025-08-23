from __future__ import annotations

from typing import List

from .schemas import JD, DMTurn, Coverage
from .rag import build_context, retrieve_indicators


def build_prompt(jd: JD, turns: List[DMTurn], coverage: Coverage | None = None) -> str:
    """Construct prompt for the dialogue model with lightweight RAG context."""

    system = (
        "You are conducting an interview.\n"
        "Goal: assess candidate for the role based on the job description.\n"
        "Style: concise, professional, helpful.\n"
        "Restrictions: DO NOT collect or request personally identifiable information.\n"
        "Output: JSON with keys {action, question, followups, target_skill, reason}."
    )

    # retrieve relevant indicators from the last user turn
    query = ""
    if turns:
        for t in reversed(turns):
            if t.role == "user":
                query = t.text
                break
    indicators = retrieve_indicators(jd, query) if query else []

    gaps: List[str] | None = None
    if coverage is not None:
        gaps = [
            ind
            for ind, cov in coverage.per_indicator.items()
            if cov < 0.5
        ]

    jd_ctx = build_context(jd, gaps)
    history = "\n".join(f"{t.role.capitalize()}: {t.text}" for t in turns)
    indicator_ctx = f"Relevant indicators: {', '.join(indicators)}\n" if indicators else ""
    gap_ctx = (
        f"Current gaps: {', '.join(gaps)}\n" if gaps else ""
    )
    return f"{system}\n\n{jd_ctx}\n{indicator_ctx}{gap_ctx}Conversation so far:\n{history}\n"


__all__ = ["build_prompt"]
