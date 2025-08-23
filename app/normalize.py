import re
from typing import Dict

# Mapping of Russian number words to floats
_NUM_WORDS = {
    "ноль": 0,
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
    "одиннадцать": 11,
    "двенадцать": 12,
    "тринадцать": 13,
    "четырнадцать": 14,
    "пятнадцать": 15,
    "шестнадцать": 16,
    "семнадцать": 17,
    "восемнадцать": 18,
    "девятнадцать": 19,
    "двадцать": 20,
}


def parse_years(text: str) -> float:
    """Parse Russian expressions for number of years into float."""
    text = text.lower()
    # numbers written with digits
    match = re.search(r"(\d+(?:[\.,]\d+)?)", text)
    if match:
        return float(match.group(1).replace(",", "."))

    # phrases like "полтора года"
    if "полтора" in text or "полутора" in text:
        return 1.5

    # phrases like "три с половиной года"
    if "с половиной" in text:
        base_part = text.split("с половиной")[0].strip().split()
        if base_part:
            last_word = base_part[-1]
            if last_word in _NUM_WORDS:
                return _NUM_WORDS[last_word] + 0.5

    # simple number words
    for word, value in _NUM_WORDS.items():
        if word in text:
            return float(value)

    return 0.0


def parse_date_ranges(text: str) -> Dict[str, str]:
    """Parse date ranges expressed in years.

    Supported formats:
    - "с 2021"
    - "до 2022"
    - "2019-2022"
    """
    text = text.lower()
    result: Dict[str, str] = {}

    m = re.search(r"(\d{4})\s*-\s*(\d{4})", text)
    if m:
        result["start"] = f"{m.group(1)}-01-01"
        result["end"] = f"{m.group(2)}-12-31"
        return result

    m = re.search(r"с\s*(\d{4})", text)
    if m:
        result["start"] = f"{m.group(1)}-01-01"

    m = re.search(r"до\s*(\d{4})", text)
    if m:
        result["end"] = f"{m.group(1)}-12-31"

    return result


__all__ = ["parse_years", "parse_date_ranges"]
