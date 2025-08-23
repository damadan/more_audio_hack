"""Matching and coverage computation."""
from __future__ import annotations

import re
from typing import Dict, List

import numpy as np
from fastapi import APIRouter
from pydantic import BaseModel

from .hr_embeddings import embed_texts, similarity
from .schemas import JD, Coverage

router = APIRouter(prefix="/match")


class CoverageRequest(BaseModel):
    jd: JD
    answers: str


@router.post("/coverage", response_model=Coverage)
async def match_coverage(req: CoverageRequest) -> Coverage:
    """Compute coverage of answers against a job description."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", req.answers) if s.strip()]
    if not sentences:
        sentences = [req.answers]

    indicators: List[str] = []
    comp_for_indicator: Dict[str, str] = {}
    for comp in req.jd.competencies:
        for ind in comp.indicators:
            indicators.append(ind.name)
            comp_for_indicator[ind.name] = comp.name

    sent_emb = embed_texts(sentences)
    ind_emb = embed_texts(indicators)

    try:  # pragma: no cover - exercised only when faiss is available
        import faiss

        faiss.normalize_L2(sent_emb)
        index = faiss.IndexFlatIP(sent_emb.shape[1])
        index.add(sent_emb)
        faiss.normalize_L2(ind_emb)
        sims, _ = index.search(ind_emb, k=sent_emb.shape[0])
    except Exception:
        sims = similarity(ind_emb, sent_emb)

    per_indicator = {
        name: float(np.max(sims[i])) if sims.size else 0.0
        for i, name in enumerate(indicators)
    }

    per_comp: Dict[str, float] = {}
    for comp in req.jd.competencies:
        vals = [per_indicator[ind.name] for ind in comp.indicators]
        per_comp[comp.name] = float(np.mean(vals)) if vals else 0.0

    return Coverage(per_indicator=per_indicator, per_competency=per_comp)


__all__ = ["router", "match_coverage", "CoverageRequest"]
