from __future__ import annotations

import math
from typing import Literal, Optional, Dict, List

from pydantic import BaseModel, Field, model_validator, conint


class Indicator(BaseModel):
    name: str


class Competency(BaseModel):
    name: str
    weight: float
    indicators: List[Indicator]


class JD(BaseModel):
    role: str
    lang: str
    competencies: List[Competency]
    knockouts: List[str]

    @model_validator(mode="after")
    def _validate_weights(self) -> "JD":
        total = sum(c.weight for c in self.competencies)
        if not math.isclose(total, 1.0, abs_tol=1e-6):
            raise ValueError("sum of competency weights must be 1.0")
        return self


class Word(BaseModel):
    w: str
    t0: float
    t1: float
    conf: float


class ASRChunk(BaseModel):
    type: Literal["partial", "final"]
    t0: float
    t1: float
    text: str
    conf: Optional[float] = None
    words: Optional[List[Word]] = None


class Evidence(BaseModel):
    quote: str
    t0: float
    t1: float


class Skill(BaseModel):
    name: str
    evidence: List[Evidence]


class Project(BaseModel):
    title: str
    metrics: Dict[str, float]


class IE(BaseModel):
    skills: List[Skill]
    tools: List[str]
    years: Dict[str, float]
    projects: List[Project]
    roles: List[str]


class Coverage(BaseModel):
    per_indicator: Dict[str, float]
    per_competency: Dict[str, float]


class RubricEvidence(BaseModel):
    quote: str
    t0: float
    t1: float
    competency: Optional[str] = None


class Rubric(BaseModel):
    scores: Dict[str, conint(ge=0, le=5)]
    red_flags: List[str]
    evidence: List[RubricEvidence]


class ByCompetencyScore(BaseModel):
    name: str
    score: float


class FinalScore(BaseModel):
    overall: float = Field(ge=0, le=1)
    decision: Literal["move", "discuss", "reject"]
    reasons: List[str]
    by_comp: List[ByCompetencyScore]


__all__ = [
    "JD",
    "ASRChunk",
    "IE",
    "Coverage",
    "Rubric",
    "FinalScore",
]
