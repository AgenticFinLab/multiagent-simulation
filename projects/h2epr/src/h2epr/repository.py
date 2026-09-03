"""Load the declarative registry of current H2EPR event practices."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

from h2epr.canonical import canonical_sha256


class CurrentEventRegistryError(ValueError):
    """The current-event registry is invalid or points outside the project."""


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = PROJECT_ROOT / "schemas" / "current-event-registry.schema.json"
FILE_FIELDS = {
    "source_profile_relative_path",
    "package_assembly_relative_path",
    "simulation_reading_relative_path",
}
DIRECTORY_FIELDS = {
    "package_relative_path",
    "roster_release_relative_path",
    "participant_interface_release_relative_path",
    "scenario_release_relative_path",
    "shared_configuration_release_relative_path",
    "rule_configuration_release_relative_path",
    "rule_execution_release_relative_path",
    "rule_run_release_relative_path",
}


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise CurrentEventRegistryError(code)


def _safe_asset(
    project_root: Path,
    value: str,
    label: str,
    *,
    directory: bool,
) -> Path:
    relative = Path(value)
    _require(
        not relative.is_absolute() and ".." not in relative.parts,
        f"current_event_path_unsafe:{label}",
    )
    path = project_root / relative
    predicate = path.is_dir if directory else path.is_file
    _require(
        predicate() and not path.is_symlink(),
        f"current_event_asset_missing_or_unsafe:{label}",
    )
    try:
        path.resolve().relative_to(project_root.resolve())
    except ValueError as exc:
        raise CurrentEventRegistryError(
            f"current_event_path_escapes_project:{label}"
        ) from exc
    return path


def load_current_event_registry(
    project_root: Path = PROJECT_ROOT,
    registry_path: Path | None = None,
) -> dict[str, Any]:
    """Validate identity, uniqueness, and every declared current asset path."""

    project_root = project_root.resolve()
    path = registry_path or project_root / "events" / "current-events.json"
    _require(path.is_file() and not path.is_symlink(), "current_event_registry_missing")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CurrentEventRegistryError("current_event_registry_unreadable") from exc
    _require(isinstance(value, dict), "current_event_registry_object_required")
    try:
        jsonschema.Draft202012Validator(schema).validate(value)
    except jsonschema.ValidationError as exc:
        raise CurrentEventRegistryError(
            f"current_event_registry_schema_invalid:{exc.json_path}"
        ) from exc
    _require(
        value["registry_sha256"]
        == canonical_sha256(
            {key: item for key, item in value.items() if key != "registry_sha256"}
        ),
        "current_event_registry_self_hash_mismatch",
    )
    event_ids = [row["event_id"] for row in value["events"]]
    slugs = [row["event_slug"] for row in value["events"]]
    _require(len(event_ids) == len(set(event_ids)), "current_event_id_duplicate")
    _require(len(slugs) == len(set(slugs)), "current_event_slug_duplicate")
    for row in value["events"]:
        slug = row["event_slug"]
        for field in sorted(FILE_FIELDS):
            _safe_asset(
                project_root,
                row[field],
                f"{slug}:{field}",
                directory=False,
            )
        for field in sorted(DIRECTORY_FIELDS):
            _safe_asset(
                project_root,
                row[field],
                f"{slug}:{field}",
                directory=True,
            )
    return value


__all__ = [
    "CurrentEventRegistryError",
    "load_current_event_registry",
]
