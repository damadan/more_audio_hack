from __future__ import annotations

"""Simple retrieval augmented generation helpers."""

from typing import List

from .schemas import JD
from .hr_embeddings import embed_texts


def build_context(jd: JD, gaps: List[str] | None) -> str:
    highlight = {g.lower() for g in gaps} if gaps else set()
    parts: List[str] = []
    for comp in jd.competencies:
        indicators: List[str] = []
        for ind in comp.indicators:
            name = ind.name
            if name.lower() in highlight:
                name = f"*{name}*"
            indicators.append(name)
        parts.append(f"{comp.name} ({comp.weight:.0%}): {', '.join(indicators)}")
    return "; ".join(parts)


def retrieve_indicators(jd: JD, query: str, k: int = 5) -> List[str]:
    """Return top ``k`` indicators most similar to ``query``."""

    indicators: List[str] = []
    for comp in jd.competencies:
        for ind in comp.indicators:
            indicators.append(ind.name)
    if not indicators or not query:
        return []
    ind_vecs = embed_texts(indicators)
    q_vec = embed_texts([query])[0]
    scores = ind_vecs @ q_vec
    order = scores.argsort()[::-1]
    return [indicators[i] for i in order[:k]]


__all__ = ["build_context", "retrieve_indicators"]
