from typing import List, Union, Dict

from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas import ASRChunk, IE, Evidence, Skill
from app.contracts import get_llm_stub

router = APIRouter()


class IERequest(BaseModel):
    transcript: Union[str, List[ASRChunk]]
    include_timestamps: bool = False


@router.post("/ie/extract", response_model=IE)
def ie_extract(req: IERequest) -> IE:
    # Normalize transcript to list of chunks
    if isinstance(req.transcript, list):
        chunks = req.transcript
    else:
        chunks = [ASRChunk(type="final", t0=0.0, t1=0.0, text=req.transcript)]

    # Build plain text for LLM step
    full_text = " ".join(c.text for c in chunks)

    # Step A: simple tagging for known skills
    skill_map: Dict[str, Skill] = {}
    for chunk in chunks:
        text_lower = chunk.text.lower()
        if "docker" in text_lower:
            name = "Docker"
            ev = Evidence(
                quote=chunk.text,
                t0=chunk.t0 if req.include_timestamps else 0.0,
                t1=chunk.t1 if req.include_timestamps else 0.0,
            )
            key = name.casefold()
            if key not in skill_map:
                skill_map[key] = Skill(name=name, evidence=[ev])
            else:
                skill_map[key].evidence.append(ev)

    # Step B: call LLM (stub) for remaining fields
    llm = get_llm_stub()
    llm_result = llm.generate_json(prompt=full_text, json_schema=IE.model_json_schema())

    skills = list(skill_map.values())
    tools = llm_result.get("tools", [])
    years = llm_result.get("years", {})
    projects = llm_result.get("projects", [])
    roles = llm_result.get("roles", [])

    return IE(skills=skills, tools=tools, years=years, projects=projects, roles=roles)


__all__ = ["router", "ie_extract"]
