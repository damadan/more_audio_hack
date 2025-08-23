from __future__ import annotations

import re

from app.schemas import ASRChunk, IE, IEEvidence, IESkill, IEProject
from app.llm_client import LLMClient


DOCKER_RE = re.compile(r"\bdocker\b", re.IGNORECASE)


def tag_esco(text: str) -> dict[str, list[str]]:
    """Very small placeholder for ESCOXLM-R tagger.

    Only recognises the word ``Docker`` to keep tests lightweight.
    Returns mapping with keys ``skills``, ``tools`` and ``roles``.
    """

    skills: list[str] = []
    tools: list[str] = []
    roles: list[str] = []
    if DOCKER_RE.search(text):
        skills.append("Docker")
    return {"skills": skills, "tools": tools, "roles": roles}


def _collect_evidence(
    name: str, chunks: list[ASRChunk], include_timestamps: bool
) -> list[IEEvidence]:
    quote = name
    t0 = t1 = 0.0
    if include_timestamps:
        for ch in chunks:
            if name.lower() in ch.text.lower():
                t0 = ch.t0
                t1 = ch.t1
                break
    return [IEEvidence(quote=quote, t0=t0, t1=t1)]


def extract_ie(
    chunks: list[ASRChunk],
    include_timestamps: bool,
    llm: LLMClient | None = None,
) -> IE:
    """Run IE pipeline over ``chunks``."""

    text = " ".join(ch.text for ch in chunks)
    tagged = tag_esco(text)

    skills: list[IESkill] = []
    for name in dict.fromkeys(tagged["skills"]):
        evidence = _collect_evidence(name, chunks, include_timestamps)
        skills.append(IESkill(name=name, evidence=evidence))

    tools = list(dict.fromkeys(tagged["tools"]))
    roles = list(dict.fromkeys(tagged["roles"]))

    years: dict[str, float] = {}
    projects: list[IEProject] = []

    if llm is not None:
        schema = {
            "type": "object",
            "properties": {
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
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["years", "projects"],
            "additionalProperties": False,
        }
        prompt = f"Extract years and projects with metrics from the transcript:\n{text}"
        try:
            data = llm.generate_json(prompt, schema)
            years = data.get("years", {})
            projects = [
                IEProject(title=p["title"], metrics=p["metrics"])
                for p in data.get("projects", [])
            ]
        except Exception:
            pass

    return IE(
        skills=skills,
        tools=tools,
        years=years,
        projects=projects,
        roles=roles,
    )
