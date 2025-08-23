from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Dict, Any, List

from fastapi import APIRouter
from pydantic import BaseModel

from .features import build_features
from .schemas import JD, IE, Coverage, Rubric, FinalScore, ByCompetencyScore

try:  # optional dependencies
    from sklearn.linear_model import LogisticRegression  # type: ignore
except Exception:  # pragma: no cover - fallback if sklearn missing
    LogisticRegression = None  # type: ignore

try:
    import joblib  # type: ignore
except Exception:  # pragma: no cover
    joblib = None  # type: ignore

router = APIRouter()


class ScoreRequest(BaseModel):
    jd: JD
    ie: IE
    coverage: Coverage
    rubric: Rubric
    aux: Dict[str, Any] = {}


def _load_catboost():
    model_dir = Path("models")
    model_path = model_dir / "catboost.cbm"
    calibrator_path = model_dir / "calibrator.pkl"
    if model_path.exists() and calibrator_path.exists():
        try:
            from catboost import CatBoostClassifier  # type: ignore

            model = CatBoostClassifier()
            model.load_model(str(model_path))
            calibrator = joblib.load(calibrator_path) if joblib else None
            return model, calibrator
        except Exception:
            pass
    return None, None


def _fallback_probability(features: List[float], coverage: Coverage, rubric: Rubric) -> float:
    cov_vals = list(coverage.per_competency.values())
    rub_vals = list(rubric.scores.values())
    if cov_vals or rub_vals:
        cov_avg = sum(cov_vals) / len(cov_vals) if cov_vals else 0.0
        rub_avg = (sum(rub_vals) / len(rub_vals) / 5) if rub_vals else 0.0
        return 0.7 * cov_avg + 0.3 * rub_avg
    if LogisticRegression is not None:
        lr = LogisticRegression()
        lr.fit([[0.0] * len(features), [1.0] * len(features)], [0, 1])
        return float(lr.predict_proba([features])[0][1])
    return 0.5


@router.post("/score/final", response_model=FinalScore)
def score_final(req: ScoreRequest) -> FinalScore:
    feats = build_features(req.jd, req.ie, req.coverage, req.rubric, req.aux)
    keys = sorted(feats.keys())
    feature_vector = [feats[k] for k in keys]

    model, calibrator = _load_catboost()
    if model is not None:
        prob = float(model.predict_proba([feature_vector])[0][1])
        if calibrator is not None:
            prob = float(calibrator.predict_proba([[prob]])[0][1])
    else:
        prob = _fallback_probability(feature_vector, req.coverage, req.rubric)

    if prob > 0.8:
        decision = "move"
    elif prob > 0.6:
        decision = "discuss"
    else:
        decision = "reject"

    reasons: List[str] = []
    for comp, cov in req.coverage.per_competency.items():
        if cov < 0.5:
            reasons.append(f"low coverage: {comp}")
    for comp, score in req.rubric.scores.items():
        if score < 3:
            reasons.append(f"low rubric: {comp}")
    reasons.extend(req.rubric.red_flags)

    by_comp = [
        ByCompetencyScore(
            name=comp.name,
            score=req.coverage.per_competency.get(comp.name, 0.0),
        )
        for comp in req.jd.competencies
    ]

    return FinalScore(overall=prob, decision=decision, reasons=reasons, by_comp=by_comp)

