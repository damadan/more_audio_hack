from __future__ import annotations

import re
from datetime import datetime
from typing import Dict

import dateparser

# Mapping of Russian number words to integers
NUMBER_WORDS: Dict[str, float] = {
    "ноль": 0,
    "один": 1,
    "одна": 1,
    "одного": 1,
    "одним": 1,
    "одной": 1,
    "два": 2,
    "две": 2,
    "двух": 2,
    "три": 3,
    "трех": 3,
    "четыре": 4,
    "четырех": 4,
    "пять": 5,
    "шесть": 6,
    "семь": 7,
    "восемь": 8,
    "девять": 9,
    "десять": 10,
}

YEAR_WORD_RE = r"(?:год(?:а|ов)?|лет)"


def parse_years(text: str) -> float | None:
    """Extract number of years from a Russian phrase.

    Supports digits (``"2 года"``), phrases with halves
    (``"три с половиной года"``), and common words such as
    ``"полтора года"`` and ``"полгода"``.
    Returns ``None`` if nothing could be parsed.
    """

    t = text.lower().strip()

    # Special cases
    if re.search(r"полгода", t):
        return 0.5
    if re.search(fr"полтора\s+{YEAR_WORD_RE}", t):
        return 1.5

    # Numeric values like "2" or "2.5"
    m = re.search(fr"(\d+[,.]?\d*)\s*{YEAR_WORD_RE}", t)
    if m:
        return float(m.group(1).replace(",", "."))

    # Numeric value with half: "3 с половиной года"
    m = re.search(fr"(\d+)\s+с\s+половиной\s+{YEAR_WORD_RE}", t)
    if m:
        return float(m.group(1)) + 0.5

    # Word with half: "три с половиной года"
    m = re.search(fr"([а-яё]+)\s+с\s+половиной\s+{YEAR_WORD_RE}", t)
    if m:
        base = NUMBER_WORDS.get(m.group(1))
        if base is not None:
            return base + 0.5

    # Plain word numbers: "три года"
    m = re.search(fr"\b([а-яё]+)\s+{YEAR_WORD_RE}", t)
    if m:
        base = NUMBER_WORDS.get(m.group(1))
        if base is not None:
            return float(base)

    return None


RANGE_RE = re.compile(
    r"с\s+(?P<start>.+?)(?:\s+(?:по|до)\s+(?P<end>.+))?$", re.IGNORECASE
)


def _parse_date(text: str) -> datetime | None:
    text = text.strip().lower()
    # Year only
    if re.fullmatch(r"\d{4}", text):
        return datetime(int(text), 1, 1)
    dt = dateparser.parse(text, languages=["ru"])
    if dt is not None:
        return dt.replace(day=1)
    return None


def parse_date_ranges(text: str) -> Dict[str, str]:
    """Parse date range expressions in Russian.

    Example::
        >>> parse_date_ranges("с 2021")
        {'start': '2021-01-01'}
    """

    match = RANGE_RE.search(text)
    result: Dict[str, str] = {}
    if not match:
        return result

    start_raw = match.group("start")
    start_dt = _parse_date(start_raw)
    if start_dt:
        result["start"] = start_dt.date().isoformat()

    end_raw = match.group("end")
    if end_raw:
        end_dt = _parse_date(end_raw)
        if end_dt:
            result["end"] = end_dt.date().isoformat()

    return result
