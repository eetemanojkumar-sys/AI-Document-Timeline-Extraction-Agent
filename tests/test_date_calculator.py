import pytest
from app.tools.date_calculator import calculate_relative_date

def test_add_days():
    assert calculate_relative_date("2026-10-01", 5, "days") == "2026-10-06"

def test_add_weeks():
    assert calculate_relative_date("2026-10-01", 2, "weeks") == "2026-10-15"

def test_add_months():
    assert calculate_relative_date("2026-01-31", 1, "months") == "2026-02-28"

def test_bad_unit():
    with pytest.raises(ValueError):
        calculate_relative_date("2026-10-01", 1, "fortnights")
