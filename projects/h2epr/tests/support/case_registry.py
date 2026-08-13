"""Stable registry for the exact H2EPR Phase-0 contract case population."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from functools import lru_cache
from typing import Any

from .cases import boundary_regressions, communication, construction, repository
from .cases import schema as schema_cases
from .cases import trace_and_identity


CASE_COUNT = 345
CASE_RESPONSIBILITIES = frozenset(
    {"schema", "construction", "communication", "trace_and_identity", "repository"}
)
SEMANTIC_CONDITION_MAX_LENGTH = 96
_FORBIDDEN_AUDIT_IDENTITY = re.compile(
    r"(?:^|[^a-z0-9])(?:baseline|extended|replacement|supervisor|directive|"
    r"promotion|r[1-6]|80|166|225|278)(?:[^a-z0-9]|$)|"
    r"(?:^|[^a-z0-9])(?:case-vector|vector-retained|predecessor-escape|"
    r"contract-behavior)(?:[^a-z0-9]|$)"
)
_RAW_TIMESTAMP = re.compile(r"(?:^|[^0-9])\d{4}-\d{2}-\d{2}t\d{2}(?:[^0-9]|$)")
_OPAQUE_HEX_SUFFIX = re.compile(r"(?:^|[-_.:])[0-9a-f]{12,}$")
_KNOWN_CLIPPED_SEGMENTS = frozenset(
    {"artif", "atte", "bundl", "constru", "envel", "erro", "recor", "sche", "sha2", "sour", "validat"}
)
_RESPONSIBILITY_ID = {
    "schema": "schema",
    "construction": "construction",
    "communication": "communication",
    "trace_and_identity": "trace-and-identity",
    "repository": "repository",
}


def behavior_identity(case: dict[str, Any]) -> str:
    """Construct public identity only from explicit stable behavior fields."""
    responsibility = _RESPONSIBILITY_ID[case["responsibility"]]
    return f"{responsibility}-{case['expected_result']}-{case['semantic_condition_id']}"


def _canonical_descriptor_sha256(descriptor: dict[str, Any]) -> str:
    payload = json.dumps(
        descriptor,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _descriptor_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        return set(value) | set().union(*(_descriptor_keys(child) for child in value.values()), set())
    if isinstance(value, list):
        return set().union(*(_descriptor_keys(child) for child in value), set())
    return set()


def audit_identity_errors(value: str) -> list[str]:
    """Return public audit-lineage or opaque-fingerprint identity violations."""
    lowered = value.lower()
    errors: list[str] = []
    if _FORBIDDEN_AUDIT_IDENTITY.search(lowered):
        errors.append("forbidden-audit-identity")
    if _RAW_TIMESTAMP.search(lowered):
        errors.append("raw-timestamp-identity")
    if _OPAQUE_HEX_SUFFIX.search(lowered):
        errors.append("opaque-hex-fingerprint")
    return errors


def semantic_identity_errors(value: str) -> list[str]:
    """Return mechanical public-name violations; human review remains required."""
    errors = audit_identity_errors(value)
    if len(value) > SEMANTIC_CONDITION_MAX_LENGTH:
        errors.append("semantic-name-too-long")
    if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value) is None:
        errors.append("semantic-name-not-kebab-case")
    segments = value.split("-")
    if len(segments) < 3:
        errors.append("semantic-name-too-generic")
    if _KNOWN_CLIPPED_SEGMENTS.intersection(segments):
        errors.append("semantic-name-contains-clipped-segment")
    return errors


def descriptor_identity_values(descriptor: dict[str, Any]) -> tuple[str, ...]:
    """Return only descriptor fields that contribute public audit identity."""
    return tuple(
        value
        for key in ("base_locator", "named_bounded_helper")
        if isinstance((value := descriptor.get(key)), str)
    )


def _build_population() -> list[dict[str, Any]]:
    non_repository = [
        *schema_cases.build_cases(),
        *construction.build_cases(),
        *communication.build_cases(),
        *trace_and_identity.build_cases(),
    ]
    cases = [
        *non_repository,
        *repository.build_cases(non_repository),
        *boundary_regressions.build_cases(),
    ]
    cases.sort(key=lambda case: case["legacy_position"])
    observed_positions = [case["legacy_position"] for case in cases]
    if observed_positions != list(range(CASE_COUNT)):
        raise RuntimeError(
            "case position closure mismatch: "
            f"observed={len(observed_positions)} unique={len(set(observed_positions))}"
        )
    for case in cases:
        if case["responsibility"] not in CASE_RESPONSIBILITIES:
            raise RuntimeError(
                f"unknown case responsibility: {case['responsibility']}"
            )
        semantic_id = case.get("semantic_condition_id")
        if not isinstance(semantic_id, str) or semantic_identity_errors(semantic_id):
            raise RuntimeError(
                f"invalid semantic condition ID: {semantic_id}:"
                f"{semantic_identity_errors(semantic_id) if isinstance(semantic_id, str) else ['not-string']}"
            )
        descriptor = case.get("mutation_descriptor")
        if not isinstance(descriptor, dict):
            raise RuntimeError(f"missing mutation descriptor: {semantic_id}")
        forbidden_descriptor_keys = {
            "legacy_case_id",
            "legacy_position",
            "suite",
            "historical_suite",
            "directive",
            "promotion",
        }
        if _descriptor_keys(descriptor) & forbidden_descriptor_keys:
            raise RuntimeError(f"legacy/audit field in mutation descriptor: {semantic_id}")
        descriptor_identity_violations = {
            value: audit_identity_errors(value)
            for value in descriptor_identity_values(descriptor)
            if audit_identity_errors(value)
        }
        if descriptor_identity_violations:
            raise RuntimeError(
                f"audit identity in mutation descriptor: {semantic_id}:"
                f"{descriptor_identity_violations}"
            )
        expected_descriptor_hash = _canonical_descriptor_sha256(descriptor)
        if case.get("mutation_descriptor_sha256") != expected_descriptor_hash:
            raise RuntimeError(f"mutation descriptor hash mismatch: {semantic_id}")
        case["case_id"] = behavior_identity(case)
        case["behavior_case_id"] = case["case_id"]
    case_ids = [case["case_id"] for case in cases]
    if len(case_ids) != len(set(case_ids)):
        raise RuntimeError("stable case IDs are not unique")
    for case_id in case_ids:
        if audit_identity_errors(case_id):
            raise RuntimeError(f"forbidden stable case ID segment: {case_id}")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", case_id):
            raise RuntimeError(f"stable case ID is not lowercase kebab-case: {case_id}")
    semantic_ids = [case["semantic_condition_id"] for case in cases]
    if len(semantic_ids) != len(set(semantic_ids)):
        raise RuntimeError("semantic condition IDs are not globally unique")
    return sorted(cases, key=lambda case: case["case_id"])


@lru_cache(maxsize=1)
def _cached_population() -> tuple[dict[str, Any], ...]:
    """Build once on first use; category modules own all case construction."""
    return tuple(copy.deepcopy(_build_population()))


def canonical_case_population() -> list[dict[str, Any]]:
    """Return a fresh copy of the exact 345-case effective population."""
    return copy.deepcopy(list(_cached_population()))


def public_case_partition(case: dict[str, Any]) -> str:
    """Return the case's single explicit responsibility partition."""
    return str(case["responsibility"])


def public_case_id(case: dict[str, Any]) -> str:
    """Return the stable behavior-only pytest parameter ID."""
    return str(case["case_id"])


def legacy_to_public_map() -> list[dict[str, Any]]:
    """Return the bijective legacy-to-stable semantic locator surface."""
    return [
        {
            "legacy_position": case["legacy_position"],
            "legacy_case_id": case["legacy_case_id"],
            "case_id": case["case_id"],
            "behavior_case_id": case["behavior_case_id"],
            "semantic_condition_id": case["semantic_condition_id"],
            "mutation_descriptor_sha256": case["mutation_descriptor_sha256"],
            "responsibility": case["responsibility"],
            "category": case["category"],
            "expected_result": case["expected_result"],
            "observed_result": case["observed_result"],
            "status": case["status"],
            "suite": case.get("suite", "contract"),
            "validator_name": case["validator_name"],
        }
        for case in canonical_case_population()
    ]
