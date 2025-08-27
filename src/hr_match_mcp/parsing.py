from __future__ import annotations

import base64
import re
from datetime import date, datetime
from functools import lru_cache
from typing import Iterable, List, Tuple

import numpy as np
from rapidfuzz import fuzz, process
import dateparser
import spacy

from .models import HRModels


# ------------------- Skills -------------------

def _generate_ngrams(words: List[str], max_n: int = 3) -> Iterable[str]:
    for n in range(1, max_n + 1):
        for i in range(len(words) - n + 1):
            yield " ".join(words[i : i + n])


def extract_skills(text: str, models: HRModels, cfg: dict) -> List[str]:
    """Return list of canonical skills mentioned in text."""
    nlp = models.skill_nlp
    doc = nlp(text)
    found: set[str] = set()
    # Step 1: PhraseMatcher
    matches = models.phrase_matcher(doc)
    for _, start, end in matches:
        span = doc[start:end]
        found.add(span.label_ or span.text.lower())
    # Normalize to canonical for phrase matches
    canonical_map = {s: c for c, syns in models.taxonomy.items() for s in {c, *syns}}
    found = {canonical_map.get(f, f) for f in found}

    if found:
        pass
    else:
        # Step 2: fuzzy against all synonyms
        syn_map = {s: c for c, syns in models.taxonomy.items() for s in syns}
        words = re.findall(r"[\w#+]+", text.lower())
        for ng in _generate_ngrams(words):
            best = process.extractOne(ng, syn_map.keys(), scorer=fuzz.ratio, score_cutoff=cfg["thresholds"]["skill_fuzzy"])
            if best:
                found.add(syn_map[best[0]])

    # Step 4: semantic fallback for unmatched tokens (limited to up to 50 unique tokens)
    if cfg and cfg["thresholds"].get("skill_semantic"):
        syn_map = {s: c for c, syns in models.taxonomy.items() for s in {c, *syns}}
        all_words = {w for w in re.findall(r"[\w#+]+", text.lower()) if w not in syn_map}
        for w in list(all_words)[:50]:
            vec = models.embed_text(w)
            sims = {c: float(vec @ models.skill_vectors[c]) for c in models.skill_vectors}
            if sims:
                best_c, best_sim = max(sims.items(), key=lambda x: x[1])
                if best_sim >= cfg["thresholds"]["skill_semantic"]:
                    found.add(best_c)

    return sorted(found)


# ------------------- Title extraction -------------------

def extract_title(text: str) -> str | None:
    pattern = re.compile(r"(Data|ML|Backend|Frontend|QA|Руководитель|Аналитик|Разработчик|Инженер)", re.I)
    m = pattern.search(text)
    return m.group(0) if m else None


# ------------------- Experience -------------------

_interval_re = re.compile(
    r"(?P<start>[A-Za-zА-Яа-я]{3,9}\s+\d{4}|\d{1,2}[./]\d{4}|\d{4})\s*[-–—]\s*(?P<end>Present|Now|Current|[A-Za-zА-Яа-я]{3,9}\s+\d{4}|\d{1,2}[./]\d{4}|\d{4})",
    re.I,
)


def _parse_dt(text: str) -> date | None:
    text = text.strip()
    if re.fullmatch(r"\d{4}", text):
        return date(int(text), 1, 1)
    dt = dateparser.parse(text, languages=["en", "ru"])
    if dt:
        return dt.date().replace(day=1)
    return None


def extract_experience_periods(text: str) -> List[Tuple[date, date]]:
    periods: List[Tuple[date, date]] = []
    for m in _interval_re.finditer(text):
        start_raw, end_raw = m.group("start"), m.group("end")
        start = _parse_dt(start_raw)
        if not start:
            continue
        if re.match(r"present|now|current", end_raw, re.I):
            end = date.today()
        else:
            end = _parse_dt(end_raw)
            if end and len(end_raw) == 4:
                # Year-only, interpret as Jan 1 of year
                pass
        if start and end and end >= start:
            periods.append((start, end))
    return periods


def merge_intervals(intervals: List[Tuple[date, date]]) -> List[Tuple[date, date]]:
    if not intervals:
        return []
    intervals = sorted(intervals, key=lambda x: x[0])
    merged = [list(intervals[0])]
    for s, e in intervals[1:]:
        last_s, last_e = merged[-1]
        if s <= last_e:
            merged[-1][1] = max(last_e, e)
        else:
            merged.append([s, e])
    return [(s, e) for s, e in merged]


def years_between(s: date, e: date) -> float:
    return (e - s).days / 365.25


def total_years(periods: Iterable[Tuple[date, date]]) -> float:
    merged = merge_intervals(list(periods))
    total = sum(years_between(s, e) for s, e in merged)
    return round(total, 2)


# ------------------- Resume/Job parsing -------------------

def parse_resume(text: str, models: HRModels, cfg: dict) -> dict:
    title = extract_title(text) or ""
    skills = extract_skills(text, models, cfg)
    periods = extract_experience_periods(text)
    years = total_years(periods)
    lang = models.detect_language(text)
    return {"title": title, "skills": skills, "years_exp": years, "lang": lang}


def _extract_section(text: str, headers: Iterable[str]) -> str:
    pattern = r"|".join(re.escape(h) for h in headers)
    regex = re.compile(rf"({pattern})(.*?)(\n\n|$)", re.I | re.S)
    m = regex.search(text)
    return m.group(2) if m else ""


def parse_job(text: str, models: HRModels, cfg: dict) -> dict:
    title = extract_title(text) or ""
    must_text = _extract_section(text, ["Requirements", "Требования", "Must have", "Обязательно"])
    must_skills = extract_skills(must_text, models, cfg)
    skills = extract_skills(text, models, cfg)
    lang = models.detect_language(text)
    return {"title": title, "skills": skills, "must": must_skills, "lang": lang}
