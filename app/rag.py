from __future__ import annotations

from typing import List, Optional

from .schemas import JD


def build_context(jd: JD, gaps: Optional[List[str]] = None) -> str:
    """Build a short string summarizing JD competencies and indicators.

    Indicators listed in ``gaps`` are highlighted with ``[GAP]``.
    """
    parts: List[str] = []
    gap_set = set(gaps or [])
    for comp in jd.competencies:
        indicators: List[str] = []
        for ind in comp.indicators:
            name = ind.name
            if name in gap_set:
                name = f"{name} [GAP]"
            indicators.append(name)
        comp_part = f"{comp.name} {comp.weight:.2f}: " + ", ".join(indicators)
        parts.append(comp_part)
    return "; ".join(parts)


__all__ = ["build_context"]
