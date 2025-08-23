"""Normalize job titles using JobBERT if possible."""
from __future__ import annotations

import unicodedata


def _strip_diacritics(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if not unicodedata.combining(c))


def normalize_title(text: str) -> str:
    """Return a canonical job title.

    The function first attempts to use the ``JobBERT-v3`` model from
    HuggingFace to produce a canonical label.  If the model or the required
    libraries are not available, a very small heuristic normalisation is used
    which simply lowercases the text and strips diacritics.
    """

    try:  # pragma: no cover - exercised only when transformers/JobBERT present
        from transformers import pipeline  # type: ignore

        clf = pipeline("text-classification", model="jinaai/JobBERT-v3", top_k=1)
        result = clf(text)[0]
        label = result["label"] if isinstance(result, dict) else str(result)
        return label
    except Exception:
        return _strip_diacritics(text).lower()


__all__ = ["normalize_title"]
