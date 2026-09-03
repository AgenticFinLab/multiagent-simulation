from __future__ import annotations

from pathlib import Path

from h2epr.repository import load_current_event_registry


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PROJECT_ROOT.parents[1]
DATA_ROOT = REPOSITORY_ROOT / "data" / "h2epr"
SCHEMA_ROOT = PROJECT_ROOT / "schemas"
CURRENT_REGISTRY = load_current_event_registry(PROJECT_ROOT)
CURRENT_EVENTS = tuple(CURRENT_REGISTRY["events"])
CURRENT_CASES = (
    ("H2EPR-0288", "panic_1907", 16, 12, 15, 813, 851, 2074),
    ("H2EPR-0616", "singhealth_data_breach", 9, 8, 11, 438, 466, 1131),
    (
        "H2EPR-0481",
        "samsung_note7_battery_recall",
        9,
        8,
        19,
        729,
        772,
        1872,
    ),
)


def event_row(value: dict[str, str] | str) -> dict[str, str]:
    if isinstance(value, dict):
        return value
    return next(row for row in CURRENT_EVENTS if row["event_slug"] == value)


def package_root(value: dict[str, str] | str) -> Path:
    return PROJECT_ROOT / event_row(value)["package_relative_path"]


def assembly_path(value: dict[str, str] | str) -> Path:
    return PROJECT_ROOT / event_row(value)["package_assembly_relative_path"]


__all__ = [
    "CURRENT_EVENTS",
    "CURRENT_CASES",
    "CURRENT_REGISTRY",
    "DATA_ROOT",
    "PROJECT_ROOT",
    "REPOSITORY_ROOT",
    "SCHEMA_ROOT",
    "assembly_path",
    "event_row",
    "package_root",
]
