"""Explicit, offline V1 schema validation for G4 outputs."""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any

warnings.filterwarnings(
    "ignore", category=DeprecationWarning, message="jsonschema.RefResolver.*"
)
from jsonschema import Draft202012Validator, RefResolver


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_ROOT = PROJECT_ROOT / "contracts" / "v1" / "schemas"
_SCHEMA_PATHS = {
    "run_manifest": SCHEMA_ROOT / "runtime" / "run_manifest.schema.json",
    "simulation_trace": SCHEMA_ROOT / "runtime" / "simulation_trace.schema.json",
    "generated_epg": SCHEMA_ROOT / "compiler" / "generated_epg.schema.json",
}
_CORE_PATH = SCHEMA_ROOT / "core" / "h2epr_core.schema.json"


class SchemaValidationError(ValueError):
    """A G4 artifact failed the immutable V1 schema."""


def schema_errors(schema_name: str, instance: Any) -> list[str]:
    if schema_name not in _SCHEMA_PATHS:
        raise KeyError(f"unknown_schema:{schema_name}")
    core = json.loads(_CORE_PATH.read_text(encoding="utf-8"))
    schema = json.loads(_SCHEMA_PATHS[schema_name].read_text(encoding="utf-8"))
    store = {core["$id"]: core, schema["$id"]: schema}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        validator = Draft202012Validator(
            schema, resolver=RefResolver.from_schema(schema, store=store)
        )
    errors = sorted(
        validator.iter_errors(instance), key=lambda error: list(error.absolute_path)
    )
    return [
        f"/{'/'.join(str(part) for part in error.absolute_path)}:{error.validator}"
        for error in errors
    ]


def require_schema(schema_name: str, instance: Any) -> None:
    errors = schema_errors(schema_name, instance)
    if errors:
        raise SchemaValidationError(f"{schema_name}:" + ",".join(errors[:20]))
