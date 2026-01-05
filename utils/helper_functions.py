from datetime import datetime, timezone
import re


def datetime_to_string(data: datetime):
    # normalize to UTC and format with Z
    if data.tzinfo is None:
        data = data.replace(tzinfo=timezone.utc)
    else:
        data = data.astimezone(timezone.utc)
    return data.strftime("%Y-%m-%dT%H:%M:%SZ")


def datetime_from_string(value: str) -> datetime | None:
    """
    Parse common ISO8601 datetime strings and return a timezone-aware datetime.
    Accepts:
      - 2025-12-17T12:34:56Z
      - 2025-12-17T12:34:56+02:00
      - 2025-12-17T12:34:56+0200
    If no timezone is present, returns a UTC-aware datetime (assumption).
    Returns None if parsing fails.
    """

    if isinstance(value, datetime):
        # If timezone-naive, assume UTC
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value

    if not isinstance(value, str):
        return None

    s = value.strip()
    # trailing Z -> +00:00
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"

    # normalize +0200 -> +02:00
    s = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", s)

    # Try stdlib (requires offset with colon to return aware dt)
    try:
        dt = datetime.fromisoformat(s)
    except Exception:
        dt = None

    if dt is None:
        return None

    # If dt is naive, assume UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt
