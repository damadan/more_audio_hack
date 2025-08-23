from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class JDIndicator(BaseModel):
    name: str


class JDCompetency(BaseModel):
    name: str
    weight: float
    indicators: list[JDIndicator]


class JD(BaseModel):
    role: str
    lang: str
    competencies: list[JDCompetency]
    knockouts: list[str]

    @model_validator(mode="after")
    def _check_weights(cls, model: "JD") -> "JD":
        total = sum(c.weight for c in model.competencies)
        if abs(total - 1.0) > 1e-6:
            raise ValueError("sum of competency weights must be 1.0")
        return model


class ASRWord(BaseModel):
    w: str
    t0: float
    t1: float
    conf: float


class ASRChunk(BaseModel):
    type: Literal["partial", "final"]
    t0: float
    t1: float
    text: str
    conf: float | None = None
    words: list[ASRWord] | None = None


class IEEvidence(BaseModel):
    quote: str
    t0: float
    t1: float


class IESkill(BaseModel):
    name: str
    evidence: list[IEEvidence]


class IEProject(BaseModel):
    title: str
    metrics: dict[str, float]


class IE(BaseModel):
    skills: list[IESkill]
    tools: list[str]
    years: dict[str, float]
    projects: list[IEProject]
    roles: list[str]


class Coverage(BaseModel):
    per_indicator: dict[str, float]
    per_competency: dict[str, float]


class RubricEvidence(BaseModel):
    quote: str
    t0: float
    t1: float
    competency: str | None = None


class Rubric(BaseModel):
    scores: dict[str, int]
    red_flags: list[str]
    evidence: list[RubricEvidence]

    @field_validator("scores")
    def _check_scores(cls, v: dict[str, int]) -> dict[str, int]:
        for score in v.values():
            if not 0 <= score <= 5:
                raise ValueError("scores must be in range 0..5")
        return v


class CompScore(BaseModel):
    name: str
    score: float


class FinalScore(BaseModel):
    overall: float = Field(ge=0.0, le=1.0)
    decision: Literal["move", "discuss", "reject"]
    reasons: list[str]
    by_comp: list[CompScore]


__all__ = [
    "JDIndicator",
    "JDCompetency",
    "JD",
    "ASRWord",
    "ASRChunk",
    "IEEvidence",
    "IESkill",
    "IEProject",
    "IE",
    "Coverage",
    "RubricEvidence",
    "Rubric",
    "CompScore",
    "FinalScore",
]
