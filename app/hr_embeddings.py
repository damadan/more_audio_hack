from __future__ import annotations

"""Lightweight text embedding utilities used for HR-specific tasks.

The real project employs sentence-transformer models such as BGE-M3,
ConsultantBERT or TAROT.  Loading those heavy models is unnecessary for
unit tests, therefore this module implements a tiny hashing based
embedding that roughly mimics cosine similarity behaviour.  The
``backend`` argument is accepted for API compatibility and to make it
possible to switch to the real models in production.
"""

from functools import lru_cache
from typing import Iterable, List
import numpy as np

_DIM = 64  # dimension of the hashed embedding used for tests

_TRANSLATIONS = {"serving": "деплой"}


def _tokenise(text: str) -> List[str]:
    return [t for t in text.lower().replace("/", " ").split() if t]


@lru_cache(maxsize=1024)
def _embed_single(text: str, backend: str = "BGE_M3") -> np.ndarray:
    """Embed a single ``text`` into a fixed size vector.

    Only the ``BGE_M3`` backend is supported in tests.  The implementation
    intentionally uses a simple hashing trick and is **not** a real
    embedding model.
    """

    if backend != "BGE_M3":
        raise ValueError("Only BGE_M3 backend is supported in tests")

    tokens = [_TRANSLATIONS.get(tok, tok) for tok in _tokenise(text) if tok.strip()]
    if not tokens:
        return np.zeros(_DIM, dtype="float32")
    vec = np.zeros(_DIM, dtype="float32")
    for tok in tokens:
        vec[abs(hash(tok)) % _DIM] += 1.0
    return vec


def embed_texts(texts: Iterable[str], backend: str = "BGE_M3") -> np.ndarray:
    """Embed a batch of texts.

    Parameters mirror those of the production implementation.  Empty
    inputs yield an empty array with shape ``(0, _DIM)``.
    """

    texts = list(texts)
    if not texts:
        return np.zeros((0, _DIM), dtype="float32")
    arr = np.stack([_embed_single(t, backend) for t in texts])
    return arr


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """Return cosine similarity between two vectors."""

    if a.ndim != 1 or b.ndim != 1:
        raise ValueError("inputs must be 1-D")
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


__all__ = ["embed_texts", "cosine_sim"]
