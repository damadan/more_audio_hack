import re
from typing import Dict

# Mapping of Russian number words to integers
_WORDS_TO_NUM = {
    "ноль": 0,
    "нуль": 0,
    "один": 1,
    "одна": 1,
    "два": 2,
    "две": 2,
    "три": 3,
    "четыре": 4,
    "пять": 5,
    "шесть": 6,
    "семь": 7,
    "восемь": 8,
    "девять": 9,
    "десять": 10,
}


def parse_years(text: str) -> float:
    """Parse a Russian phrase describing a number of years into a float."""
    text_l = text.lower()
    # First try to find an explicit numeric value
    m = re.search(r"(\d+[\.,]?\d*)", text_l)
    if m:
        value = float(m.group(1).replace(",", "."))
    else:
        value = 0.0
        for token in re.split(r"\s+", text_l):
            value += _WORDS_TO_NUM.get(token, 0.0)
    # Check for half-year expressions
    if "полтора" in text_l or "полгода" in text_l or "половин" in text_l:
        value += 0.5
    return value


def parse_date_ranges(text: str) -> Dict[str, str]:
    """Parse simple Russian date range expressions into ISO date dict."""
    text_l = text.lower()
    result: Dict[str, str] = {}

    m = re.search(r"с\s*(\d{4})", text_l)
    if m:
        result["start"] = f"{m.group(1)}-01-01"

    m = re.search(r"по\s*(\d{4})", text_l)
    if m:
        result["end"] = f"{m.group(1)}-12-31"

    if not result:
        m = re.search(r"(\d{4})\s*[-–]\s*(\d{4})", text_l)
        if m:
            result["start"] = f"{m.group(1)}-01-01"
            result["end"] = f"{m.group(2)}-12-31"
    return result

__all__ = ["parse_years", "parse_date_ranges"]
