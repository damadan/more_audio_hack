from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, Dict

import fitz  # PyMuPDF

from .models import HRModels
from .parsing import parse_job, parse_resume
from .scoring import read_yaml_config, score_resume


_models_cache: dict[bool, HRModels] = {}


def _get_models(use_alt: bool) -> HRModels:
    if use_alt not in _models_cache:
        _models_cache[use_alt] = HRModels(use_alt=use_alt)
    return _models_cache[use_alt]


def parse_pdf(resume_pdf_base64: str) -> Dict[str, Any]:
    data = base64.b64decode(resume_pdf_base64)
    try:
        doc = fitz.open(stream=data, filetype="pdf")
        text = "\n".join(page.get_text() for page in doc)
    except Exception:
        text = data.decode("utf8", errors="ignore")
    cfg = read_yaml_config()
    models = _get_models(False)
    res = parse_resume(text, models, cfg)
    preview = text[:200]
    return {
        "title": res["title"],
        "skills": res["skills"],
        "years_exp": res["years_exp"],
        "text_preview": preview,
        "debug": {"lang": res["lang"]},
    }


def score(resume_pdf_base64: str, job_text: str, use_alt: bool = False) -> Dict[str, Any]:
    data = base64.b64decode(resume_pdf_base64)
    try:
        doc = fitz.open(stream=data, filetype="pdf")
        cv_text = "\n".join(page.get_text() for page in doc)
    except Exception:
        cv_text = data.decode("utf8", errors="ignore")
    models = _get_models(use_alt)
    cfg = read_yaml_config()
    cv = parse_resume(cv_text, models, cfg)
    jd = parse_job(job_text, models, cfg)
    final, parts, debug = score_resume(cv, jd, models, cfg)
    debug.update({"lang_cv": cv["lang"], "lang_jd": jd["lang"]})
    return {"score": final, "parts": parts, "debug": debug}
