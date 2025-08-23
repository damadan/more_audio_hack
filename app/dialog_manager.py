from __future__ import annotations

from typing import List

from .schemas import JD, DMTurn, Coverage, DMRequest, NextAction
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


def mock_next(req: DMRequest) -> NextAction:
    """Generate a deterministic ``NextAction`` without calling LLM."""
    coverage = req.coverage
    gaps = []
    if coverage:
        gaps = [ind for ind, cov in coverage.per_indicator.items() if cov < 0.5]
    followups: List[str] = []
    if gaps:
        target = gaps[0]
        question = f"Расскажите про {target}?"
        followups = ["Какие инструменты использовали?"]
        return NextAction(
            action="ask",
            question=question,
            followups=followups[:2],
            target_skill=target,
            reason="gap",
        )
    if req.jd.knockouts:
        target = req.jd.knockouts[0]
        question = f"Есть опыт с {target}?"
        followups = ["Насколько глубоко?"]
        return NextAction(
            action="ask",
            question=question,
            followups=followups[:2],
            target_skill=target,
            reason="knockout",
        )
    if req.jd.competencies:
        comp = sorted(req.jd.competencies, key=lambda c: c.weight, reverse=True)[0]
        target = comp.indicators[0].name if comp.indicators else comp.name
        question = f"Расскажите про {target}"
        followups = ["Пример из практики?"]
        return NextAction(
            action="ask",
            question=question,
            followups=followups[:2],
            target_skill=target,
            reason="weight",
        )
    return NextAction(action="end", reason="done")


__all__ = ["build_prompt", "mock_next"]
