from __future__ import annotations

import pytest

from h2epr.construction import (
    EndpointStatus,
    TimePrecision,
    TimeRole,
    parse_endpoint,
    parse_time_expression,
)


@pytest.mark.parametrize(
    ("raw", "precision"),
    [
        ("2026-01-02T03:04:05Z", TimePrecision.EXACT_DATETIME),
        ("2026-01-02", TimePrecision.DATE),
        ("2026-01", TimePrecision.MONTH),
        ("2026", TimePrecision.YEAR),
        ("2026-01-01 to 2026-02-01", TimePrecision.RANGE),
        ("during the synthetic period", TimePrecision.FREE_TEXT),
        ("unknown", TimePrecision.UNKNOWN),
        (None, TimePrecision.UNKNOWN),
    ],
)
def test_time_forms_remain_distinguishable(raw: object, precision: TimePrecision) -> None:
    value = parse_time_expression("synthetic", "/time", raw, TimeRole.OCCURRENCE)
    assert value.raw_value == raw
    assert value.precision is precision
    assert value.time_role is TimeRole.OCCURRENCE


def test_occurrence_and_information_availability_are_distinct() -> None:
    occurrence = parse_time_expression("synthetic", "/time", "2026", TimeRole.OCCURRENCE)
    availability = parse_time_expression("synthetic", "/time", "2026", TimeRole.INFORMATION_AVAILABLE)
    assert occurrence.raw_value == availability.raw_value
    assert occurrence.time_role is not availability.time_role


@pytest.mark.parametrize(
    ("raw", "precision"),
    [
        ("2026-13", TimePrecision.MONTH),
        ("2026-02-29", TimePrecision.DATE),
        ("2026-04-31", TimePrecision.DATE),
        ("2026-01-01T25:00:00Z", TimePrecision.EXACT_DATETIME),
        ("2026-01-01T03:04:05+24:00", TimePrecision.EXACT_DATETIME),
        ("0000", TimePrecision.YEAR),
        ("2026-02-30 to 2026-03-01", TimePrecision.RANGE),
    ],
    ids=[
        "invalid-month",
        "invalid-non-leap-day",
        "invalid-month-day",
        "invalid-hour",
        "invalid-offset",
        "year-zero",
        "invalid-range-component",
    ],
)
def test_calendar_invalid_shaped_time_retains_raw_without_normalization(
    raw: str, precision: TimePrecision
) -> None:
    value = parse_time_expression("synthetic", "/time", raw, TimeRole.OCCURRENCE)
    assert value.raw_value == raw
    assert value.precision is precision
    assert value.normalized_candidate is None
    assert value.interval_lower is None
    assert value.interval_upper is None
    assert value.diagnostic_status == "invalid_unparsed"


@pytest.mark.parametrize(
    ("raw", "lower", "upper"),
    [
        ("2024-02", "2024-02-01", "2024-02-29"),
        ("2023-02", "2023-02-01", "2023-02-28"),
        ("2026-04", "2026-04-01", "2026-04-30"),
        ("2026-01", "2026-01-01", "2026-01-31"),
    ],
    ids=["leap-february", "common-february", "thirty-day", "thirty-one-day"],
)
def test_month_interval_uses_actual_gregorian_end(
    raw: str, lower: str, upper: str
) -> None:
    value = parse_time_expression("synthetic", "/time", raw, TimeRole.OCCURRENCE)
    assert value.diagnostic_status == "parsed"
    assert value.interval_lower == lower
    assert value.interval_upper == upper


def test_valid_leap_day_and_structured_range_are_parsed() -> None:
    leap_day = parse_time_expression(
        "synthetic", "/time", "2024-02-29", TimeRole.OCCURRENCE
    )
    interval = parse_time_expression(
        "synthetic", "/time", "2024-02 to 2024-03", TimeRole.OCCURRENCE
    )
    assert leap_day.diagnostic_status == "parsed"
    assert leap_day.normalized_candidate == "2024-02-29"
    assert interval.diagnostic_status == "parsed"
    assert interval.interval_lower == "2024-02-01"
    assert interval.interval_upper == "2024-03-31"


@pytest.mark.parametrize(
    ("raw", "known", "status"),
    [
        ("participant-a", {"participant-a"}, EndpointStatus.KNOWN),
        ("participant-b", {"participant-a"}, EndpointStatus.UNRESOLVED),
        ("external:observer", set(), EndpointStatus.EXTERNAL),
        ("unknown", set(), EndpointStatus.UNKNOWN),
        ("", set(), EndpointStatus.UNKNOWN),
        ("bad\nidentifier", set(), EndpointStatus.SUSPICIOUS),
    ],
)
def test_endpoint_status_is_explicit(raw: str, known: set[str], status: EndpointStatus) -> None:
    endpoint = parse_endpoint("synthetic", "/endpoint", raw, known)
    assert endpoint.raw_identifier == raw
    assert endpoint.status is status
