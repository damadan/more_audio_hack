from __future__ import annotations

import re
from typing import List, Union, Dict

from fastapi import APIRouter
from pydantic import BaseModel

from .schemas import ASRChunk, IE, Skill, Evidence
from .contracts import LLMClientProtocol, get_llm_stub

router = APIRouter()


class IEExtractRequest(BaseModel):
    transcript: Union[List[ASRChunk], str]
    include_timestamps: bool = False


def _extract_text(data: Union[List[ASRChunk], str]) -> str:
    if isinstance(data, str):
        return data
    return " ".join(chunk.text for chunk in data)


def _simple_skill_tagger(
    transcript: Union[List[ASRChunk], str], include_ts: bool
) -> Dict[str, Skill]:
    text = _extract_text(transcript).lower()
    skills: Dict[str, Skill] = {}

    if "docker" in text:
        evidence: List[Evidence] = []
        if include_ts and isinstance(transcript, list):
            for chunk in transcript:
                if "docker" in chunk.text.lower():
                    evidence.append(
                        Evidence(quote=chunk.text, t0=chunk.t0, t1=chunk.t1)
                    )
                    break
        else:
            evidence.append(Evidence(quote="Docker", t0=0.0, t1=0.0))
        skills["docker"] = Skill(name="Docker", evidence=evidence)
    return skills


@router.post("/ie/extract", response_model=IE)
async def ie_extract(req: IEExtractRequest) -> IE:
    transcript = req.transcript
    include_ts = req.include_timestamps

    text = _extract_text(transcript)

    # Step A: tag skills/occupations/tools using ESCOXLM-R if available (stub)
    skills_map = _simple_skill_tagger(transcript, include_ts)

    # Step B: use LLM to gather numbers/dates/years/projects/metrics and evidence
    llm: LLMClientProtocol = get_llm_stub()
    schema = {
        "type": "object",
        "properties": {
            "skills": {"type": "array", "items": {"type": "string"}},
            "tools": {"type": "array", "items": {"type": "string"}},
            "years": {
                "type": "object",
                "additionalProperties": {"type": "number"},
            },
            "projects": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "metrics": {
                            "type": "object",
                            "additionalProperties": {"type": "number"},
                        },
                    },
                    "required": ["title", "metrics"],
                },
            },
            "roles": {"type": "array", "items": {"type": "string"}},
            "evidence": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "quote": {"type": "string"},
                        "t0": {"type": "number"},
                        "t1": {"type": "number"},
                    },
                    "required": ["quote", "t0", "t1"],
                },
            },
        },
        "required": ["skills", "tools", "years", "projects", "roles", "evidence"],
    }
    llm_result = llm.generate_json(text, schema)

    for sk in llm_result.get("skills", []):
        key = sk.casefold()
        if key not in skills_map:
            skills_map[key] = Skill(name=sk, evidence=[])

    tools: List[str] = []
    for tool in llm_result.get("tools", []):
        if tool.casefold() not in [t.casefold() for t in tools]:
            tools.append(tool)

    years = llm_result.get("years", {})
    projects = llm_result.get("projects", [])

    roles: List[str] = []
    for role in llm_result.get("roles", []):
        if role.casefold() not in [r.casefold() for r in roles]:
            roles.append(role)

    return IE(
        skills=list(skills_map.values()),
        tools=tools,
        years=years,
        projects=projects,
        roles=roles,
    )


__all__ = ["router"]
