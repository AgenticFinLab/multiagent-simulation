from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from support.case_registry import (
    canonical_case_population,
    public_case_id,
    public_case_partition,
)
from support.schema_registry import SCHEMAS, SCHEMA_PATHS, SCHEMA_STORE


SCHEMA_CASES = [case for case in canonical_case_population() if public_case_partition(case) == "schema"]


@pytest.mark.parametrize("case", SCHEMA_CASES, ids=public_case_id)
def test_schema_behavior_case(case: dict) -> None:
    assert case["status"] == "pass", case


def test_schema_catalog_is_exact_and_offline() -> None:
    catalog = json.loads((SCHEMAS / "catalog.json").read_text(encoding="utf-8"))
    assert catalog["network_resolution"] == "prohibited"
    assert catalog["base_uri"] == "https://raw.githubusercontent.com/AgenticFinLab/multiagent-simulation/main/projects/h2epr/contracts/v1/schemas/"
    assert catalog["schema_count"] == 28 == len(SCHEMA_PATHS)
    expected_paths = {path.relative_to(SCHEMAS).as_posix() for path in SCHEMA_PATHS}
    assert {row["path"] for row in catalog["schemas"]} == expected_paths
    assert len({row["schema_id"] for row in catalog["schemas"]}) == 28
    assert all(row["schema_id"].startswith(catalog["base_uri"]) for row in catalog["schemas"])
    assert set(SCHEMA_STORE) == {row["schema_id"] for row in catalog["schemas"]}
    for row in catalog["schemas"]:
        path = SCHEMAS / row["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        assert schema["$id"] == row["schema_id"]
        for ref in _references(schema):
            if ref.startswith("#"):
                continue
            target = ref.split("#", 1)[0]
            assert target in SCHEMA_STORE, f"offline reference not cataloged: {ref}"


def _references(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "$ref" and isinstance(child, str):
                yield child
            else:
                yield from _references(child)
    elif isinstance(value, list):
        for child in value:
            yield from _references(child)
