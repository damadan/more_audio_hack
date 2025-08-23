# Pydantic схемы
Основные модели (Pydantic v2) и примеры JSON.

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
        return m
```
Пример:
```json
{"role":"ML Engineer","lang":"ru","competencies":[{"name":"ML","weight":1.0,"indicators":[{"name":"python"}]}],"knockouts":[]}
```

## ASRChunk
```python
class ASRWord(BaseModel):
    w: str; t0: float; t1: float; conf: float
class ASRChunk(BaseModel):
    type: Literal["partial","final"]
    t0: float
    t1: float
    text: str
    conf: float | None = None
    words: list[ASRWord] | None = None
```
Пример:
```json
{"type":"partial","t0":0.0,"t1":0.0,"text":"hello"}
```

## IE
```python
class IEEvidence(BaseModel):
    quote: str; t0: float; t1: float
class IESkill(BaseModel):
    name: str; evidence: list[IEEvidence]
class IEProject(BaseModel):
    title: str; metrics: dict[str,float]
class IE(BaseModel):
    skills: list[IESkill]
    tools: list[str]
    years: dict[str,float]
    projects: list[IEProject]
    roles: list[str]
```
Пример:
```json
{"skills":[{"name":"Docker","evidence":[{"quote":"Docker","t0":0,"t1":0}]}],"tools":["Grafana"],"years":{},"projects":[],"roles":[]}
```

## Coverage
```python
class Coverage(BaseModel):
    per_indicator: dict[str,float]
    per_competency: dict[str,float]
```
Пример:
```json
{"per_indicator":{"python":0.9},"per_competency":{"ML":0.9}}
```

## Rubric
```python
class RubricEvidence(BaseModel):
    quote: str; t0: float; t1: float; competency: str | None = None
class Rubric(BaseModel):
    scores: dict[str,int]  # 0..5
    red_flags: list[str]
    evidence: list[RubricEvidence]
    @field_validator("scores")
    def _check_scores(cls, v):
        for s in v.values():
            if not 0 <= s <= 5: raise ValueError
        return v
```
Пример:
```json
{"scores":{"ML":3},"red_flags":[],"evidence":[{"quote":"Docker","t0":0,"t1":1,"competency":null}]}
```

## FinalScore
```python
class CompScore(BaseModel):
    name: str; score: float
class FinalScore(BaseModel):
    overall: float  # 0..1
    decision: Literal["move","discuss","reject"]
    reasons: list[str]
    by_comp: list[CompScore]
```
Пример:
```json
{"overall":0.73,"decision":"move","reasons":["low coverage for ML"],"by_comp":[{"name":"ML","score":0.9}]}
```
