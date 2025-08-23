from __future__ import annotations

from pydantic import TypeAdapter

from .schemas import (
    JD,
    IE,
    Rubric,
    RubricEvidence,
    RubricScoreRequest,
    Coverage,
)
from .llm_client import LLMClient

RubricAdapter = TypeAdapter(Rubric)


def build_rubric_prompt(jd: JD, transcript: str | IE, coverage: Coverage | None) -> str:
    system = (
        "You are evaluating a candidate.\n"
        "Score each competency from 0 to 5 with the following anchors:\n"
        "0: no evidence of skill\n"
        "1: awareness only\n"
        "2: limited experience\n"
        "3: working proficiency\n"
        "4: strong proficiency\n"
        "5: expert mastery.\n"
        "Return JSON with keys {scores, red_flags, evidence}.\n"
        "Each evidence item must contain quote, t0, t1 and competency.\n"
        "List any concerns in red_flags."
    )
    jd_context = f"Job Description:\n{jd.model_dump_json(indent=2)}\n"
    if isinstance(transcript, IE):
        interview_context = f"IE:\n{transcript.model_dump_json(indent=2)}\n"
    else:
        interview_context = f"Transcript:\n{transcript}\n"
    coverage_context = (
        f"Coverage:\n{coverage.model_dump_json(indent=2)}\n" if coverage else ""
    )
    return f"{system}\n\n{jd_context}{interview_context}{coverage_context}"


def merge_rubrics(*rubrics: Rubric) -> Rubric:
    scores: dict[str, list[int]] = {}
    for r in rubrics:
        for name, score in r.scores.items():
            scores.setdefault(name, []).append(score)
    merged_scores = {name: round(sum(vals) / len(vals)) for name, vals in scores.items()}
    evidence_map: dict[tuple[str, float, float, str | None], RubricEvidence] = {}
    for r in rubrics:
        for ev in r.evidence:
            key = (ev.quote, ev.t0, ev.t1, ev.competency)
            evidence_map[key] = ev
    red_flags = list({rf for r in rubrics for rf in r.red_flags})
    return Rubric(scores=merged_scores, evidence=list(evidence_map.values()), red_flags=red_flags)


def score_rubric_llm(req: RubricScoreRequest) -> Rubric:
    prompt = build_rubric_prompt(req.jd, req.transcript, req.coverage)
    client = LLMClient.from_env()
    schema = Rubric.model_json_schema()
    raw1 = client.generate_json(prompt=prompt, json_schema=schema)
    raw2 = client.generate_json(prompt=prompt, json_schema=schema)
    r1 = RubricAdapter.validate_python(raw1)
    r2 = RubricAdapter.validate_python(raw2)
    return merge_rubrics(r1, r2)


def score_rubric_mock(req: RubricScoreRequest) -> Rubric:
    comps = [c.name for c in req.jd.competencies]
    docker_present = False
    if isinstance(req.transcript, IE):
        docker_present = any(s.name.lower() == "docker" for s in req.transcript.skills)
    scores = {}
    for name in comps:
        score = 4 if docker_present and name.lower() == "mlops" else 3
        scores[name] = score
    quote = ""
    if isinstance(req.transcript, str):
        quote = req.transcript.strip().split(".")[0]
    elif isinstance(req.transcript, IE):
        for sk in req.transcript.skills:
            if sk.evidence:
                quote = sk.evidence[0].quote
                break
    evidence = []
    if quote:
        evidence = [RubricEvidence(quote=quote, t0=0.0, t1=1.0, competency=None)]
    return Rubric(scores=scores, red_flags=[], evidence=evidence)


def score_rubric(req: RubricScoreRequest, use_mock: bool) -> Rubric:
    if use_mock:
        return score_rubric_mock(req)
    return score_rubric_llm(req)


__all__ = [
    "build_rubric_prompt",
    "merge_rubrics",
    "score_rubric",
]
