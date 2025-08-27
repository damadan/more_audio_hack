from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
import yaml

from .models import HRModels


@lru_cache(maxsize=1)
def read_yaml_config(path: str = "config/scoring.yaml") -> dict:
    with open(path, encoding="utf8") as f:
        return yaml.safe_load(f)


def must_have_covered(
    jd_must: List[str],
    cv_skills: List[str],
    skill_vectors: Dict[str, np.ndarray],
    semantic_thr: float,
) -> Tuple[bool, List[str]]:
    cv_vecs = [skill_vectors[s] for s in cv_skills if s in skill_vectors]
    missing: List[str] = []
    for m in jd_must:
        if m in cv_skills:
            continue
        mv = skill_vectors.get(m)
        if mv is not None and cv_vecs:
            sims = [float(mv @ v) for v in cv_vecs]
            if sims and max(sims) >= semantic_thr:
                continue
        missing.append(m)
    return (len(missing) == 0, missing)


def skills_overlap(jd_skills: Iterable[str], cv_skills: Iterable[str]) -> Tuple[List[str], List[str], List[str]]:
    jd_set = set(jd_skills)
    cv_set = set(cv_skills)
    tp = sorted(jd_set & cv_set)
    fn = sorted(jd_set - cv_set)
    fp = sorted(cv_set - jd_set)
    return tp, fn, fp


def combine_score(S_sem: float, S_skill: float, S_title: float, penalty: float, weights: Dict[str, float]) -> float:
    total = (
        weights.get("semantic", 0) * S_sem
        + weights.get("skills", 0) * S_skill
        + weights.get("title", 0) * S_title
    )
    total = total * 100 - penalty
    return round(max(total, 0.0), 2)


def score_resume(cv: dict, jd: dict, models: HRModels, cfg: dict) -> Tuple[float, dict, dict]:
    thr = cfg["thresholds"]["skill_semantic"]
    covered, missing = must_have_covered(jd["must"], cv["skills"], models.skill_vectors, thr)
    tp, fn, fp = skills_overlap(jd["skills"], cv["skills"])
    S_sem = 1.0 if covered else 0.0
    S_skill = len(tp) / max(len(jd["skills"]), 1)
    S_title = 1.0 if cv["title"] and jd["title"] and cv["title"].lower() == jd["title"].lower() else 0.0
    penalty = 0.0
    if cv["years_exp"] < 0:
        penalty += cfg["penalties"]["lacking_years"]
    if not covered:
        penalty += cfg["penalties"]["missing_musthave"]
    score = combine_score(S_sem, S_skill, S_title, penalty, cfg["weights"])
    parts = {
        "sem": S_sem,
        "skills": S_skill,
        "title": S_title,
        "penalty": penalty,
        "skills_tp": tp,
        "skills_fn": fn,
        "skills_fp": fp,
    }
    debug = {
        "cv_title": cv["title"],
        "jd_title": jd["title"],
        "missing_must": missing,
        "thresholds": cfg["thresholds"],
    }
    return score, parts, debug
