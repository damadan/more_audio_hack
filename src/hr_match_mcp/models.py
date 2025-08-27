from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, Set

import numpy as np
from langdetect import detect
import spacy
from spacy.matcher import PhraseMatcher
import csv
import hashlib

try:  # pragma: no cover - optional dependency
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover
    SentenceTransformer = None  # type: ignore


@lru_cache(maxsize=1)
def load_taxonomy(path: str | Path) -> Dict[str, Set[str]]:
    """Load skills taxonomy from CSV.

    The CSV must contain columns ``canonical`` and ``synonyms`` where
    synonyms are separated by ``;``.
    """
    taxonomy: Dict[str, Set[str]] = {}
    with open(path, newline='', encoding='utf8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            canonical = row["canonical"].strip().lower()
            syns = {s.strip().lower() for s in row.get("synonyms", "").split(";") if s.strip()}
            taxonomy[canonical] = syns
    return taxonomy


def build_phrase_matcher(nlp: spacy.language.Language, taxonomy: Dict[str, Set[str]]) -> PhraseMatcher:
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    for canonical, syns in taxonomy.items():
        phrases = [canonical, *syns]
        patterns = [nlp.make_doc(p) for p in phrases]
        matcher.add(canonical, patterns)
    return matcher


def encode_canonical_skills(embed: SentenceTransformer, taxonomy: Dict[str, Set[str]]) -> Dict[str, np.ndarray]:
    keys = list(taxonomy.keys())
    vecs = embed.encode(keys, normalize_embeddings=True)
    return {k: v for k, v in zip(keys, vecs)}


class DummySentenceTransformer:
    """Fallback encoder when sentence-transformers is unavailable."""

    def encode(self, texts: Iterable[str], normalize_embeddings: bool = True):  # type: ignore[override]
        vecs = []
        for t in texts:
            h = hashlib.sha256(t.lower().encode()).digest()
            arr = np.frombuffer(h, dtype=np.uint8).astype(np.float32)[:32]
            if normalize_embeddings:
                norm = np.linalg.norm(arr) or 1.0
                arr = arr / norm
            vecs.append(arr)
        return np.stack(vecs)


def _load_st_model(name: str):
    if SentenceTransformer is None:
        return DummySentenceTransformer()
    try:
        mdl_dir = os.getenv("MODELS_DIR")
        if mdl_dir:
            local = Path(mdl_dir) / name.replace("/", "__")
            if local.exists():
                return SentenceTransformer(str(local))
        return SentenceTransformer(name, cache_folder=os.getenv("HF_HOME"))
    except Exception:  # pragma: no cover - network failures
        return DummySentenceTransformer()


class HRModels:
    """Container for heavy NLP models and resources."""

    def __init__(self, use_alt: bool = False, taxonomy_path: str | None = "data/skills_taxonomy.csv") -> None:
        model_name = "sentence-transformers/paraphrase-MiniLM-L3-v2" if not use_alt else "sentence-transformers/all-MiniLM-L6-v2"
        self.embed = _load_st_model(model_name)
        self.taxonomy = load_taxonomy(Path(taxonomy_path)) if taxonomy_path else {}
        self.skill_nlp = spacy.blank("en")
        self.phrase_matcher = build_phrase_matcher(self.skill_nlp, self.taxonomy)
        self.skill_vectors = encode_canonical_skills(self.embed, self.taxonomy)

    @staticmethod
    def detect_language(text: str) -> str:
        try:
            return detect(text)
        except Exception:
            return "unknown"

    @lru_cache(maxsize=1024)
    def embed_text(self, text: str) -> np.ndarray:
        return self.embed.encode([text], normalize_embeddings=True)[0]
