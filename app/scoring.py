from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any

from .schemas import JD, IE, Coverage, Rubric, FinalScore, CompScore


def _slug(name: str) -> str:
    """Convert arbitrary names to snake_case feature names."""
    import re

    return re.sub(r"[^0-9a-zA-Z]+", "_", name.strip().lower())


def build_features(
    jd: JD,
    ie: IE,
    coverage: Coverage | None,
    rubric: Rubric | None,
    aux: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build feature mapping used for final scoring."""

    features: dict[str, Any] = {}
    if coverage:
        for name, val in coverage.per_competency.items():
            features[f"coverage_{_slug(name)}"] = float(val)
    if rubric:
        for name, val in rubric.scores.items():
            features[f"rubric_{_slug(name)}"] = float(val)
    for name, years in ie.years.items():
        features[f"years_{_slug(name)}"] = float(years)

    count_metrics = sum(len(p.metrics) for p in ie.projects)
    features["count_metrics"] = int(count_metrics)

    if aux is None:
        aux = {}
    # numbers are passed in aux["numbers"] as list of numbers
    numbers = aux.get("numbers", [])
    features["count_numbers"] = int(len(numbers))
    features["contradictions"] = int(aux.get("contradictions", 0))
    features["toxicity"] = int(aux.get("toxicity", 0))
    features["ko_flags"] = int(aux.get("ko_flags", 0))
    features["asr_conf"] = float(aux.get("asr_conf", 0.0))
    title = str(aux.get("title_canonical", ""))
    if title:
        features["title_canonical"] = hashlib.md5(title.encode()).hexdigest()
    else:
        features["title_canonical"] = ""
    return features


def _predict_probability(features: dict[str, Any]) -> float:
    """Predict probability using optional CatBoost model or stub logistic regression."""

    model_dir = Path("models")
    cat_model = model_dir / "catboost.cbm"
    calibrator = model_dir / "calibrator.pkl"
    if cat_model.exists() and calibrator.exists():  # pragma: no cover - optional path
        try:
            from catboost import CatBoostClassifier
            import numpy as np
            import pickle

            model = CatBoostClassifier()
            model.load_model(str(cat_model))
            with open(calibrator, "rb") as f:
                calib = pickle.load(f)
            numeric_keys = [
                k
                for k, v in features.items()
                if isinstance(v, (int, float))
            ]
            numeric_vals = [features[k] for k in numeric_keys]
            X = np.array([numeric_vals])
            prob = float(model.predict_proba(X)[0][1])
            prob = float(calib.predict_proba([[prob]])[0][1])
            return prob
        except Exception:
            pass  # fall back to stub below

    # Stub logistic regression using coverage and rubric averages
    coverage_vals = [
        v for k, v in features.items() if k.startswith("coverage_") and isinstance(v, (int, float))
    ]
    rubric_vals = [
        v for k, v in features.items() if k.startswith("rubric_") and isinstance(v, (int, float))
    ]
    coverage_avg = sum(coverage_vals) / len(coverage_vals) if coverage_vals else 0.0
    rubric_avg = (
        sum(rubric_vals) / (5.0 * len(rubric_vals)) if rubric_vals else 0.0
    )
    z = coverage_avg + rubric_avg
    return 1 / (1 + math.exp(-z))


def final_score(
    jd: JD,
    ie: IE,
    coverage: Coverage | None,
    rubric: Rubric | None,
    aux: dict[str, Any] | None,
) -> FinalScore:
    """Compute final score, decision and reasons."""

    features = build_features(jd, ie, coverage, rubric, aux)
    prob = _predict_probability(features)
    if prob > 0.8:
        decision = "move"
    elif prob > 0.6:
        decision = "discuss"
    else:
        decision = "reject"

    reasons: list[str] = []
    if coverage:
        for name, val in coverage.per_competency.items():
            if val < 0.5:
                reasons.append(f"low coverage for {name}")
    if rubric:
        for name, val in rubric.scores.items():
            if val < 3:
                reasons.append(f"low rubric for {name}")
        reasons.extend(rubric.red_flags)

    by_comp: list[CompScore] = []
    if coverage:
        for name, val in coverage.per_competency.items():
            by_comp.append(CompScore(name=name, score=float(val)))

    return FinalScore(overall=prob, decision=decision, reasons=reasons, by_comp=by_comp)


__all__ = ["build_features", "final_score"]
