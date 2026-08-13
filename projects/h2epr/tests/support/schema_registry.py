"""Offline schema catalog loading and Draft 2020-12 validation."""
from __future__ import annotations
import hashlib
import json
import warnings
from pathlib import Path
from typing import Any

warnings.filterwarnings("ignore", category=DeprecationWarning, message="jsonschema.RefResolver.*")
from jsonschema import Draft202012Validator, RefResolver

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
FIXTURES = HERE.parent / "fixtures" / "v1"
SYNTHETIC = FIXTURES / "valid"
SCHEMAS = REPO_ROOT / "projects" / "h2epr" / "contracts" / "v1" / "schemas"
SCHEMA_PATHS = tuple(sorted(SCHEMAS.rglob("*.schema.json")))

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

SCHEMA_BY_NAME: dict[str, Path] = {}
SCHEMA_STORE: dict[str, Any] = {}
for _schema_path in SCHEMA_PATHS:
    if _schema_path.name in SCHEMA_BY_NAME:
        raise RuntimeError(f"duplicate schema basename: {_schema_path.name}")
    SCHEMA_BY_NAME[_schema_path.name] = _schema_path
    _document = load_json(_schema_path)
    _schema_id = _document["$id"]
    if _schema_id in SCHEMA_STORE:
        raise RuntimeError(f"duplicate schema id: {_schema_id}")
    SCHEMA_STORE[_schema_id] = _document

def _validator(schema: dict[str, Any]) -> Draft202012Validator:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        return Draft202012Validator(schema, resolver=RefResolver.from_schema(schema, store=SCHEMA_STORE))

def schema_errors(schema_name: str, instance: Any) -> list[str]:
    schema = load_json(SCHEMA_BY_NAME[schema_name])
    errors = sorted(_validator(schema).iter_errors(instance), key=lambda item: list(item.absolute_path))
    return [f"/{'/'.join(str(part) for part in error.absolute_path)}:{error.validator}" for error in errors[:12]]

def definition_errors(definition: str, instance: Any) -> list[str]:
    core = load_json(SCHEMA_BY_NAME["h2epr_core.schema.json"])
    schema = {"$schema": core["$schema"], "$id": f"urn:h2epr:definition:{definition}", "$ref": f"{core['$id']}#/$defs/{definition}"}
    errors = sorted(_validator(schema).iter_errors(instance), key=lambda item: list(item.absolute_path))
    return [f"/{'/'.join(str(part) for part in error.absolute_path)}:{error.validator}" for error in errors[:12]]
