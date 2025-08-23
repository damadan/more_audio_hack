import pytest

from app.normalize import parse_years, parse_date_ranges


@pytest.mark.parametrize(
    "text,expected",
    [
        ("три с половиной года", 3.5),
        ("2 года", 2.0),
        ("четыре года", 4.0),
    ],
)
def test_parse_years(text, expected):
    assert parse_years(text) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("с 2021", {"start": "2021-01-01"}),
        (
            "с 2020 по 2022",
            {"start": "2020-01-01", "end": "2022-12-31"},
        ),
    ],
)
def test_parse_date_ranges(text, expected):
    assert parse_date_ranges(text) == expected
