from datetime import datetime, timezone
from enum import Enum
import re

STRING_SEPARATOR = " | "


class InlineList(list):
    """Class wrapper to indicate that the list should be written as one line in YAML.
    Used for 'bbox' property."""

    pass


def is_valid_string(text):
    if len(str(text).replace(" ", "")) >= 1:
        return True
    return False


def get_enum_value_from_string(enum_type: Enum, text: str):
    if isinstance(enum_type, type) and issubclass(enum_type, Enum):
        for member in enum_type:
            if text == member.value:
                return member
        # handle case with non-string enums
        for member in enum_type:
            if text == str(member.value) or (text == "" and member.value is None):
                return member

    raise ValueError(f"Unexpected value '{text}', expected type: '{enum_type}'")


def bbox_from_list(raw_bbox_list: list):

    # this loop is to not add empty decimals unnecessarily
    list_bbox_val = []
    for part in raw_bbox_list:
        if isinstance(part, str):  # if the list is read from UI widgets
            part = part.strip()
            if "." in part:
                list_bbox_val.append(float(part))
            else:
                list_bbox_val.append(int(part))
        else:  # if the list is already taken from actual data (int or float)
            list_bbox_val.append(part)

    if len(list_bbox_val) != 4 and len(list_bbox_val) != 6:
        raise ValueError(
            f"Wrong number of values: {len(list_bbox_val)}. Expected: 4 or 6"
        )

    return InlineList(list_bbox_val)


def to_iso8601(dt: datetime) -> str:
    """
    Convert datetime to UTC ISO 8601 string, for both naive and aware datetimes.
    """
    if dt.tzinfo is None:
        # Treat naive datetime as UTC
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        # Convert to UTC
        dt = dt.astimezone(timezone.utc)

    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


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
    if not isinstance(value, str):
        return None

    s = value.strip()
    # quick normalization: trailing Z -> +00:00
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"

    # normalize +0200 -> +02:00
    s = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", s)

    # Try stdlib first (requires offset with colon to return aware dt)
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
