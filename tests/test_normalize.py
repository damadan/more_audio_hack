import pytest

from app.normalize import parse_years, parse_date_ranges


def test_parse_years_simple_word():
    assert parse_years("два года") == 2


def test_parse_years_half_phrase():
    assert parse_years("три с половиной года") == 3.5


def test_parse_years_poltor():
    assert parse_years("полтора года") == 1.5


def test_parse_date_range_start():
    assert parse_date_ranges("с 2021") == {"start": "2021-01-01"}


def test_parse_date_range_between():
    assert parse_date_ranges("2019-2022") == {
        "start": "2019-01-01",
        "end": "2022-12-31",
    }
