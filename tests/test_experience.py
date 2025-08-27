from datetime import date

from hr_match_mcp.parsing import extract_experience_periods, total_years


class FixedDate(date):
    @classmethod
    def today(cls):
        return cls(2024, 1, 1)


def test_experience_periods_and_total_years(monkeypatch):
    monkeypatch.setattr("hr_match_mcp.parsing.date", FixedDate)
    text = (
        "Worked at X 2018-2020. Then Y Jan 2019 - Present. Also Z Март 2019 — Июль 2023."
    )
    periods = extract_experience_periods(text)
    assert len(periods) == 3
    years = total_years(periods)
    assert 5.9 < years < 6.1
