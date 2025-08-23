from __future__ import annotations

from .schemas import JD


def build_context(jd: JD, gaps: list[str] | None) -> str:
    """Build a concise text summary of competencies and indicators.

    Each competency is rendered as "<name> (<weight%>): <ind1>, <ind2>".
    If ``gaps`` is provided, indicators matching the given words are
    wrapped in asterisks to highlight them.
    """
    highlight = {g.lower() for g in gaps} if gaps else set()
    parts: list[str] = []
    for comp in jd.competencies:
        indicators: list[str] = []
        for ind in comp.indicators:
            name = ind.name
            if name.lower() in highlight:
                name = f"*{name}*"
            indicators.append(name)
        parts.append(f"{comp.name} ({comp.weight:.0%}): {', '.join(indicators)}")
    return "; ".join(parts)
