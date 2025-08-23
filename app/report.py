from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .schemas import JD, Coverage, Rubric, FinalScore

router = APIRouter()

templates_env = Environment(
    loader=FileSystemLoader("app/templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


class ReportRequest(BaseModel):
    jd: JD
    coverage: Coverage
    rubric: Rubric
    final: FinalScore


@router.post("/report", response_class=HTMLResponse)
def report(req: ReportRequest) -> HTMLResponse:
    template = templates_env.get_template("report.html")
    html = template.render(jd=req.jd, coverage=req.coverage, rubric=req.rubric, final=req.final)
    return HTMLResponse(content=html)

