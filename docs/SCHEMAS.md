# Pydantic схемы

Ниже приведены основные модели (Pydantic v2), используемые в API.

## JD

```python
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
    def _check_weights(cls, m):
        assert abs(sum(c.weight for c in m.competencies) - 1.0) < 1e-6
```

Пример:
```json
{
  "role": "ML Engineer",
  "lang": "ru",
  "competencies": [
    {"name": "ML", "weight": 1.0, "indicators": [{"name": "python"}]}
  ],
  "knockouts": []
}
```

## ASRChunk

```python
class ASRWord(BaseModel):
    w: str; t0: float; t1: float; conf: float

class ASRChunk(BaseModel):
    type: Literal["partial", "final"]
    t0: float
    t1: float
    text: str
    conf: float | None = None
    words: list[ASRWord] | None = None
```

## IE

```python
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
```

## Coverage

```python
class Coverage(BaseModel):
    per_indicator: dict[str, float]
    per_competency: dict[str, float]
```

## Rubric

```python
class RubricEvidence(BaseModel):
    quote: str
    t0: float
    t1: float
    competency: str | None = None

class Rubric(BaseModel):
    scores: dict[str, int]  # 0..5
    red_flags: list[str]
    evidence: list[RubricEvidence]
```

## FinalScore

```python
class CompScore(BaseModel):
    name: str
    score: float

class FinalScore(BaseModel):
    overall: float  # 0..1
    decision: Literal["move", "discuss", "reject"]
    reasons: list[str]
    by_comp: list[CompScore]
```

Дополнительные схемы (`TTSRequest`, `DMRequest`, `ReportRequest` и др.)
аналогично определены в [app/schemas.py](../app/schemas.py).

