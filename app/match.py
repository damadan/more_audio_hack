from __future__ import annotations

"""Job description coverage using simple embedding search."""

import re
from typing import Dict, Iterable, List, Tuple

import faiss
import numpy as np

from .schemas import Coverage, JD
from .hr_embeddings import embed_texts


def _split_sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"[.!?\n]+", text) if s.strip()]


def build_indicator_index(jd: JD, backend: str) -> Tuple[faiss.IndexFlatIP, List[Tuple[str, str]]]:
    """Embed all indicators from ``jd`` and return FAISS index."""

    indicators: List[str] = []
    meta: List[Tuple[str, str]] = []
    for comp in jd.competencies:
        for ind in comp.indicators:
            indicators.append(ind.name)
            meta.append((comp.name, ind.name))
    if not indicators:
        dim = 1
        index = faiss.IndexFlatIP(dim)
        return index, meta
    vecs = embed_texts(indicators, backend)
    dim = vecs.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(vecs.astype("float32"))
    return index, meta


def match_spans(answer: str, index: faiss.IndexFlatIP, meta: List[Tuple[str, str]], backend: str, top_k: int = 5) -> List[dict]:
    """Split ``answer`` into spans and return top-k matches for each span."""

    spans = _split_sentences(answer)
    if not spans:
        return []
    span_vecs = embed_texts(spans, backend)
    D, I = index.search(span_vecs.astype("float32"), top_k)
    matches: List[dict] = []
    for i, span in enumerate(spans):
        for j in range(top_k):
            idx = int(I[i, j])
            if idx >= len(meta):
                continue
            sim = float(D[i, j])
            comp, ind = meta[idx]
            matches.append({"span": span, "competency": comp, "indicator": ind, "similarity": sim})
    return matches


def compute_coverage(matches: Iterable[dict], meta: List[Tuple[str, str]]) -> Coverage:
    """Aggregate matches to per-indicator and per-competency coverage."""

    per_indicator: Dict[str, float] = {ind: 0.0 for _, ind in meta}
    indicator_to_comp: Dict[str, str] = {ind: comp for comp, ind in meta}
    for m in matches:
        ind = m["indicator"]
        sim = m["similarity"]
        if sim > per_indicator[ind]:
            per_indicator[ind] = sim
    per_comp: Dict[str, float] = {}
    counts: Dict[str, int] = {}
    for ind, cov in per_indicator.items():
        comp = indicator_to_comp[ind]
        per_comp[comp] = per_comp.get(comp, 0.0) + cov
        counts[comp] = counts.get(comp, 0) + 1
    for comp in per_comp:
        per_comp[comp] /= counts[comp]
    return Coverage(per_indicator=per_indicator, per_competency=per_comp)


__all__ = ["build_indicator_index", "match_spans", "compute_coverage"]
