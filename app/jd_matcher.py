from __future__ import annotations

import re
from typing import Dict, Iterable, List, Tuple

import faiss
import numpy as np

from .schemas import Coverage, JD


_TRANSLATIONS = {"serving": "деплой"}


def _tokenize(text: str) -> List[str]:
    return re.findall(r"\w+", text.lower())


def _norm_tokens(tokens: Iterable[str]) -> List[str]:
    return [_TRANSLATIONS.get(t, t) for t in tokens]


def _embed(tokens: Iterable[str], vocab: Dict[str, int]) -> np.ndarray:
    vec = np.zeros(len(vocab), dtype="float32")
    for t in _norm_tokens(tokens):
        if t in vocab:
            vec[vocab[t]] += 1.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


def build_indicator_index(jd: JD) -> Tuple[faiss.IndexFlatIP, List[Tuple[str, str]], Dict[str, int]]:
    """Build FAISS index and vocabulary from JD indicators."""
    vocab: Dict[str, int] = {}
    meta: List[Tuple[str, str]] = []
    vectors: List[np.ndarray] = []
    for comp in jd.competencies:
        for ind in comp.indicators:
            tokens = _norm_tokens(_tokenize(ind.name))
            for t in tokens:
                if t not in vocab:
                    vocab[t] = len(vocab)
            meta.append((comp.name, ind.name))
    for comp, ind in meta:
        tokens = _norm_tokens(_tokenize(ind))
        vectors.append(_embed(tokens, vocab))
    dim = len(vocab) if vocab else 1
    index = faiss.IndexFlatIP(dim)
    if vectors:
        index.add(np.array(vectors, dtype="float32"))
    return index, meta, vocab


def match_spans(
    answer: str,
    index: faiss.IndexFlatIP,
    meta: List[Tuple[str, str]],
    vocab: Dict[str, int],
    top_k: int = 5,
) -> List[dict]:
    """Split answer into sentences and return top-k indicator matches."""
    spans = [s.strip() for s in re.split(r"[.!?\n]+", answer) if s.strip()]
    if not spans:
        return []
    span_vecs = [_embed(_tokenize(span), vocab) for span in spans]
    D, I = index.search(np.array(span_vecs, dtype="float32"), top_k)
    matches: List[dict] = []
    for i, span in enumerate(spans):
        for j in range(top_k):
            idx = int(I[i, j])
            sim = float(D[i, j])
            comp, ind = meta[idx]
            matches.append({"span": span, "competency": comp, "indicator": ind, "similarity": sim})
    return matches


def compute_coverage(matches: Iterable[dict], meta: List[Tuple[str, str]]) -> Coverage:
    """Compute coverage per indicator and per competency."""
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
