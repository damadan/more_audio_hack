from __future__ import annotations

from typing import List, Optional, Literal

from fastapi import APIRouter
from pydantic import BaseModel

from .schemas import JD, Coverage
from .contracts import LLMClientProtocol, get_llm_stub
from .rag import build_context

try:  # prefer real client if available
    from app.llm_client import LLMClient  # type: ignore
    llm_client: LLMClientProtocol = LLMClient()  # type: ignore[assignment]
except Exception:  # pragma: no cover - fallback when real client missing
    llm_client = get_llm_stub()


class Turn(BaseModel):
    role: Literal["user", "assistant"]
    text: str


class DialogContext(BaseModel):
    turns: List[Turn]


class DMRequest(BaseModel):
    jd: JD
    context: DialogContext
    coverage: Optional[Coverage] = None


class DMResponse(BaseModel):
    action: Literal["ask", "end"]
    question: str
    followups: List[str]
    target_skill: Optional[str] = None
    reason: str


router = APIRouter()


@router.post("/dm/next", response_model=DMResponse)
def dm_next(req: DMRequest) -> DMResponse:
    system_prompt = (
        "Goal: conduct a job interview to assess candidate skills. "
        "Style: professional and concise. Avoid collecting personal identifiable information. "
        "Respond strictly in JSON matching the provided schema."
    )
    conversation = "\n".join(f"{t.role}: {t.text}" for t in req.context.turns)
    jd_summary = build_context(req.jd, None)
    prompt = (
        f"{system_prompt}\n\n"
        f"Job description: {jd_summary}\n"
        f"Conversation so far:\n{conversation}\n"
    )
    schema = DMResponse.model_json_schema()
    try:
        raw = llm_client.generate_json(prompt=prompt, json_schema=schema)
        return DMResponse.model_validate(raw)
    except Exception:
        return DMResponse(
            action="ask",
            question="Could you tell me about yourself?",
            followups=[],
            target_skill=None,
            reason="start" if not req.context.turns else "error",
        )


__all__ = ["router"]
