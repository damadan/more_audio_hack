from __future__ import annotations

from typing import Dict, Union, Any

from .schemas import JD, IE, Coverage, Rubric


Number = Union[float, int]


def build_features(jd: JD, ie: IE, coverage: Coverage, rubric: Rubric, aux: Dict[str, Any]) -> Dict[str, Number]:
    """Build feature dictionary for ML models.

    Parameters
    ----------
    jd: JD
        Job description.
    ie: IE
        Information extraction result.
    coverage: Coverage
        Coverage of competencies.
    rubric: Rubric
        Rubric scores and red flags.
    aux: Dict[str, Any]
        Additional auxiliary data (currently unused).

    Returns
    -------
    Dict[str, Number]
        Flat dictionary of numeric features.
    """
    feats: Dict[str, Number] = {}

    # coverage per competency
    for comp, value in coverage.per_competency.items():
        feats[f"coverage_{comp}"] = float(value)

    # rubric scores
    for comp, score in rubric.scores.items():
        feats[f"rubric_{comp}"] = float(score)

    # years experience per technology/tool
    for tech, years in ie.years.items():
        feats[f"years_{tech}"] = float(years)

    # count of years entries (acts as number count proxy)
    feats["count_numbers"] = len(ie.years)

    # total metrics counts across projects
    feats["count_metrics"] = sum(len(p.metrics) for p in ie.projects)

    # placeholder flags
    feats["contradictions"] = 0
    feats["toxicity"] = 0
    feats["ko_flags"] = len(rubric.red_flags)
    feats["asr_conf"] = 1.0

    # hash of job title for categorical role information
    feats["title_hash"] = hash(jd.role) % (2 ** 31)

    return feats

