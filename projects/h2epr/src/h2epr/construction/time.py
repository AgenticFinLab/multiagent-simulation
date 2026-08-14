"""Non-coercive time and endpoint interpretation proposals."""

from __future__ import annotations

import calendar
import re
from datetime import date, datetime

from .model import EndpointRef, EndpointStatus, TimeExpression, TimePrecision, TimeRole


DATETIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})?$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MONTH = re.compile(r"^\d{4}-\d{2}$")
YEAR = re.compile(r"^\d{4}$")
RANGE = re.compile(r"^(.+?)\s+(?:to|–|—)\s+(.+?)$", re.IGNORECASE)


def _valid_datetime(value: str) -> bool:
    try:
        datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except ValueError:
        return False
    return int(value[:4]) >= 1


def _valid_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return int(value[:4]) >= 1


def _structured_bounds(value: str) -> tuple[TimePrecision, str, str] | None:
    if DATETIME.fullmatch(value):
        return (TimePrecision.EXACT_DATETIME, value, value) if _valid_datetime(value) else None
    if DATE.fullmatch(value):
        return (TimePrecision.DATE, value, value) if _valid_date(value) else None
    if MONTH.fullmatch(value):
        year, month = (int(part) for part in value.split("-"))
        if year < 1 or not 1 <= month <= 12:
            return None
        last_day = calendar.monthrange(year, month)[1]
        return TimePrecision.MONTH, f"{value}-01", f"{value}-{last_day:02d}"
    if YEAR.fullmatch(value):
        year = int(value)
        if year < 1:
            return None
        return TimePrecision.YEAR, f"{value}-01-01", f"{value}-12-31"
    return None


def _invalid_shaped(
    source_id: str,
    pointer: str,
    raw_value: object,
    precision: TimePrecision,
    time_role: TimeRole,
    uncertainty: str,
) -> TimeExpression:
    return TimeExpression(
        source_id=source_id,
        pointer=pointer,
        raw_value=raw_value,
        normalized_candidate=None,
        precision=precision,
        interval_lower=None,
        interval_upper=None,
        uncertainty=uncertainty,
        diagnostic_status="invalid_unparsed",
        time_role=time_role,
    )


def parse_time_expression(
    source_id: str, pointer: str, raw_value: object, time_role: TimeRole
) -> TimeExpression:
    normalized = raw_value.strip() if isinstance(raw_value, str) else None
    lower = upper = None
    uncertainty = ""
    status = "parsed"
    if raw_value is None or not normalized or normalized.lower() in {"unknown", "n/a", "unspecified"}:
        precision = TimePrecision.UNKNOWN
        normalized = None
        uncertainty = "source time unavailable or unknown"
        status = "unknown"
    elif DATETIME.fullmatch(normalized) and not _valid_datetime(normalized):
        return _invalid_shaped(
            source_id, pointer, raw_value, TimePrecision.EXACT_DATETIME,
            time_role, "calendar-invalid exact datetime",
        )
    elif DATETIME.fullmatch(normalized):
        precision = TimePrecision.EXACT_DATETIME
        lower = upper = normalized
    elif DATE.fullmatch(normalized) and not _valid_date(normalized):
        return _invalid_shaped(
            source_id, pointer, raw_value, TimePrecision.DATE,
            time_role, "calendar-invalid date",
        )
    elif DATE.fullmatch(normalized):
        precision = TimePrecision.DATE
        lower = upper = normalized
    elif MONTH.fullmatch(normalized):
        precision = TimePrecision.MONTH
        bounds = _structured_bounds(normalized)
        if bounds is None:
            return _invalid_shaped(
                source_id, pointer, raw_value, precision,
                time_role, "calendar-invalid month",
            )
        _, lower, upper = bounds
        uncertainty = "month precision"
    elif YEAR.fullmatch(normalized):
        precision = TimePrecision.YEAR
        if int(normalized) < 1:
            return _invalid_shaped(
                source_id, pointer, raw_value, precision,
                time_role, "calendar-invalid year",
            )
        lower = normalized + "-01-01"
        upper = normalized + "-12-31"
        uncertainty = "year precision"
    elif match := RANGE.fullmatch(normalized):
        precision = TimePrecision.RANGE
        start_raw, end_raw = (item.strip() for item in match.groups())
        start = _structured_bounds(start_raw)
        end = _structured_bounds(end_raw)
        if start is None or end is None:
            return _invalid_shaped(
                source_id, pointer, raw_value, precision,
                time_role, "calendar-invalid structured range",
            )
        lower, upper = start[1], end[2]
        if lower > upper:
            return _invalid_shaped(
                source_id, pointer, raw_value, precision,
                time_role, "reverse-ordered structured range",
            )
        uncertainty = "source interval"
    else:
        precision = TimePrecision.FREE_TEXT
        uncertainty = "normalization not asserted"
        status = "unparsed_free_text"
    return TimeExpression(
        source_id=source_id,
        pointer=pointer,
        raw_value=raw_value,
        normalized_candidate=normalized,
        precision=precision,
        interval_lower=lower,
        interval_upper=upper,
        uncertainty=uncertainty,
        diagnostic_status=status,
        time_role=time_role,
    )


def parse_endpoint(
    source_id: str, pointer: str, raw_identifier: object, known_ids: set[str]
) -> EndpointRef:
    raw = "" if raw_identifier is None else str(raw_identifier)
    if not raw or raw.lower() in {"unknown", "none", "n/a", "unspecified"}:
        status = EndpointStatus.UNKNOWN
        normalized = None
    elif any(character.isspace() and character not in {" "} for character in raw) or len(raw) > 256:
        status = EndpointStatus.SUSPICIOUS
        normalized = None
    elif raw.startswith("external:"):
        status = EndpointStatus.EXTERNAL
        normalized = raw
    elif raw in known_ids:
        status = EndpointStatus.KNOWN
        normalized = raw
    else:
        status = EndpointStatus.UNRESOLVED
        normalized = raw
    return EndpointRef(source_id, pointer, raw, status, normalized)
