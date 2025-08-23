from __future__ import annotations

from typing import List, Dict, Optional, Tuple

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from .schemas import JD, ASRChunk, IE, Coverage, Rubric, RubricEvidence
from .contracts import LLMClientProtocol, get_llm_stub


class RubricRequest(BaseModel):
    jd: JD
    transcript: Optional[List[ASRChunk]] = None
    ie: Optional[IE] = None
    coverage: Optional[Coverage] = None


router = APIRouter()


SYSTEM_PROMPT = (
    "You are an AI assistant that scores competencies on a scale of 0..5. "
    "Provide mandatory evidence (quote+t0+t1) and red_flags. Return strict JSON."
)


def _stub_generate(req: RubricRequest, llm: LLMClientProtocol) -> Rubric:
    # The llm stub is invoked to respect the contract, but the scoring
    # logic is implemented here deterministically for testing purposes.
    llm.generate_json(SYSTEM_PROMPT, Rubric.model_json_schema())

    text = " ".join(chunk.text for chunk in req.transcript or [])
    scores: Dict[str, int] = {}
    red_flags: List[str] = []
    evidence: List[RubricEvidence] = []

    for comp in req.jd.competencies:
        comp_name = comp.name
        if comp_name.lower() in text.lower():
            scores[comp_name] = 4
            evidence.append(
                RubricEvidence(quote=comp_name, t0=0.0, t1=1.0, competency=comp_name)
            )
        else:
            scores[comp_name] = 2
            red_flags.append(f"no evidence for {comp_name}")

    return Rubric(scores=scores, red_flags=red_flags, evidence=evidence)


@router.post("/rubric/score", response_model=Rubric)
async def rubric_score(
    req: RubricRequest, llm: LLMClientProtocol = Depends(get_llm_stub)
) -> Rubric:
    # self-consistency with two generations
    runs = [_stub_generate(req, llm) for _ in range(2)]

    score_acc: Dict[str, List[int]] = {}
    red_flags_set = set()
    evidence_dict: Dict[Tuple[str, float, float, Optional[str]], RubricEvidence] = {}

    for run in runs:
        for comp, score in run.scores.items():
            score_acc.setdefault(comp, []).append(score)
        red_flags_set.update(run.red_flags)
        for ev in run.evidence:
            key = (ev.quote, ev.t0, ev.t1, ev.competency)
            evidence_dict[key] = ev

    merged_scores = {
        comp: int(round(sum(vals) / len(vals))) for comp, vals in score_acc.items()
    }
    merged_red_flags = sorted(red_flags_set)
    merged_evidence = list(evidence_dict.values())

    return Rubric(
        scores=merged_scores, red_flags=merged_red_flags, evidence=merged_evidence
    )
