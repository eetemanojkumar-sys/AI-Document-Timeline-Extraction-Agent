from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

def calculate_relative_date(start_date: str, amount: int, unit: str) -> str:
    """Calculate a relative date from YYYY-MM-DD. Supports days, weeks, months, years."""
    start = date.fromisoformat(start_date)
    unit = unit.lower().strip()
    if not -36500 <= amount <= 36500:
        raise ValueError("Amount is outside the supported range.")
    if unit in {"day", "days"}:
        result = start + timedelta(days=amount)
    elif unit in {"week", "weeks"}:
        result = start + timedelta(weeks=amount)
    elif unit in {"month", "months"}:
        result = start + relativedelta(months=amount)
    elif unit in {"year", "years"}:
        result = start + relativedelta(years=amount)
    else:
        raise ValueError("Unsupported unit. Use days, weeks, months, or years.")
    return result.isoformat()
