import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.parsers import parse_years, parse_date_ranges


def test_parse_years_with_half_words():
    assert parse_years("три с половиной года") == 3.5


def test_parse_years_digits():
    assert parse_years("2 года") == 2.0


def test_parse_years_polutora():
    assert parse_years("полтора года") == 1.5


def test_parse_date_ranges_start_only():
    assert parse_date_ranges("с 2021") == {"start": "2021-01-01"}


def test_parse_date_ranges_start_end():
    expected = {"start": "2020-01-01", "end": "2021-03-01"}
    assert parse_date_ranges("с января 2020 по март 2021") == expected
