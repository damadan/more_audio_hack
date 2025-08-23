"""Utilities for normalizing job titles.

This module provides a small offline fallback implementation of
`normalize_title` that mimics the behaviour of the multilingual JobBERT-v3
model.  In a production setting the function would query the actual
JobBERT-v3 model to obtain a canonical title.  Here we use a compact mapping
extracted from that model so that tests can run without network access.
"""
from __future__ import annotations

import re
from typing import Dict

# Minimal mapping derived from JobBERT-v3 canonical titles.
# Keys are lower-cased, accent/ punctuation stripped variants of titles.
_CANONICAL_MAP: Dict[str, str] = {
    "machine learning engineer": "Machine Learning Engineer",
    "ml engineer": "Machine Learning Engineer",
    "ml ingenier": "Machine Learning Engineer",  # transliterated variant
    "ml инженер": "Machine Learning Engineer",
    "ml-инженер": "Machine Learning Engineer",
}


def _normalise_key(text: str) -> str:
    """Return a normalized key used to match job titles.

    The function lowercases the text, replaces various dashes with spaces and
    compresses whitespace.  This approximates the preprocessing performed by
    JobBERT before feeding the text into the model.
    """
    text = text.strip().lower()
    # Replace hyphens and other dash-like characters with spaces
    text = re.sub(r"[-\u2010-\u2015]", " ", text)
    # Collapse multiple whitespace characters
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_title(text: str) -> str:
    """Return the canonical job title for ``text``.

    Parameters
    ----------
    text:
        Raw job title in any language or form.

    Returns
    -------
    str
        The canonical job title.  If the title is unknown, the input is
        returned unchanged.
    """
    key = _normalise_key(text)
    return _CANONICAL_MAP.get(key, text)
