"""Embedding utilities for HR matching."""
from __future__ import annotations

from typing import Literal, List

import numpy as np

try:  # optional dependency
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:  # pragma: no cover - used only when available
    SentenceTransformer = None  # type: ignore

try:  # scikit-learn is required as a fallback
    from sklearn.feature_extraction.text import HashingVectorizer
except Exception as exc:  # pragma: no cover
    raise RuntimeError("scikit-learn is required for embeddings") from exc


_BACKEND_MODELS = {
    "CONSULTANTBERT": "BAAI/bge-small-en-v1.5",
    "TAROT": "BAAI/bge-small-en-v1.5",
    "BGE_M3": "BAAI/bge-small-en-v1.5",
}

_VECTOR_DIM = 768

# simple synonym expansion so that the hashing fallback is not entirely lexical
_SYNONYMS = {
    "serving": ["deploy", "deployment", "docker", "fastapi"],
}


def _expand_synonyms(text: str) -> str:
    tokens = text.split()
    extra: List[str] = []
    for t in tokens:
        extra.extend(_SYNONYMS.get(t.lower(), []))
    return " ".join(tokens + extra)


def embed_texts(
    texts: List[str],
    backend: Literal["CONSULTANTBERT", "TAROT", "BGE_M3"] = "BGE_M3",
) -> np.ndarray:
    """Embed a list of texts using the requested backend.

    If the backend model cannot be loaded, a simple ``HashingVectorizer`` is
    used as a fallback so that similarity can still be computed.
    """

    model_name = _BACKEND_MODELS.get(backend, _BACKEND_MODELS["BGE_M3"])
    if SentenceTransformer is not None:
        try:  # pragma: no cover - exercised only when models are available
            model = SentenceTransformer(model_name)
            return model.encode(texts, convert_to_numpy=True)
        except Exception:
            pass

    vectorizer = HashingVectorizer(n_features=_VECTOR_DIM, alternate_sign=False)
    expanded = [_expand_synonyms(t) for t in texts]
    return vectorizer.transform(expanded).toarray().astype(np.float32)


def similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Cosine similarity between two embedding matrices."""
    a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-9)
    b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-9)
    return a_norm @ b_norm.T


__all__ = ["embed_texts", "similarity"]
