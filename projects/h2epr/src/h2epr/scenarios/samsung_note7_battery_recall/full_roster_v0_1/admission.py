"""Fail-closed admission for Note7 full-roster Policy Realization."""

from __future__ import annotations

import copy
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from h2epr.bundles.canonical import sha256_value
from h2epr.execution import (
    ExecutionIOCode,
    ExecutionIOError,
    path_within,
    read_json_object,
)

from .catalog import (
    CONFIGURATION_CANONICAL_SHA256,
    CONFIGURATION_ID,
    CONFIGURATION_PATH,
    CONFIGURATION_RELEASE_MANIFEST_SHA256,
    CONFIGURATION_SOURCE_SHA256,
    CONFIGURATION_VERSION,
    EVENT_ID,
    MAPPING_PROFILE_ID,
    MAPPING_PROFILE_PATH,
    MAPPING_PROFILE_SHA256,
    ROSTER_RELEASE_MANIFEST_PATH,
    ROSTER_RELEASE_MANIFEST_SHA256,
    Note7PolicyCatalog,
    Note7PolicyCatalogError,
    build_note7_policy_catalog,
)
from .errors import (
    PolicyRealizationAdmissionError,
    PolicyRealizationErrorCode,
)
from .registry import (
    implementation_versions,
    lifecycle_rules,
    participant_policies_by_capability,
    scenario_policies,
)


POLICY_REALIZATION_FORMAT = "h2epr.policy-realization.v0_1"
POLICY_REALIZATION_SCHEMA_PATH = Path(
    "execution/schemas/policy-realization-v0.1.schema.json"
)
CONFIGURATION_RELEASE_MANIFEST_PATH = Path(
    "configs/samsung_note7_battery_recall/scenario-configuration-v0.1/manifest.json"
)
CONFIGURATION_ADMISSION_RECEIPT_PATH = Path(
    "configs/samsung_note7_battery_recall/configuration-admission-v0.1/receipt.json"
)
CONFIGURATION_ADMISSION_RECEIPT_SHA256 = (
    "07c94c5df9836b4b1838a512a3a81dddcb07493d2d9995d98d27f94bba502a71"
)
CONSOLIDATED_MAPPING_MANIFEST_PATH = Path(
    "agents/bindings/samsung_note7_battery_recall/consolidated/manifest.json"
)
CONSOLIDATED_MAPPING_MANIFEST_SHA256 = (
    "c52d27ce2e753fee7394480ca70355b7c293e70b755470da360f58e917e7ceb1"
)
SCENARIO_RELEASE_MANIFEST_PATH = Path(
    "scenarios/samsung_note7_battery_recall/definition-v0.1/manifest.json"
)
SCENARIO_RELEASE_MANIFEST_SHA256 = (
    "fa90d60c8eccdad6e903de6e5ed761e49615d6cdf5edb7815aadf12d0761582e"
)

_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_COVERAGE_KEYS = (
    "actor_instances",
    "actor_capability_bindings",
    "population_units",
    "exogenous_inputs",
    "structural_selections",
    "decision_commitments",
    "observation_placements",
    "private_state_placements",
    "configuration_parameter_bindings",
    "intent_placements",
    "lifecycle_families",
    "selected_policies",
)

_EXPECTED_SEMANTIC_PARENT = {
    "configuration_id": CONFIGURATION_ID,
    "configuration_version": CONFIGURATION_VERSION,
    "configuration_status": "accepted_non_executable_configuration",
    "configuration_path": CONFIGURATION_PATH.as_posix(),
    "configuration_source_sha256": CONFIGURATION_SOURCE_SHA256,
    "configuration_canonical_sha256": CONFIGURATION_CANONICAL_SHA256,
    "configuration_release_manifest_path": (
        CONFIGURATION_RELEASE_MANIFEST_PATH.as_posix()
    ),
    "configuration_release_manifest_sha256": (
        CONFIGURATION_RELEASE_MANIFEST_SHA256
    ),
    "configuration_admission_receipt_path": (
        CONFIGURATION_ADMISSION_RECEIPT_PATH.as_posix()
    ),
    "configuration_admission_receipt_sha256": (
        CONFIGURATION_ADMISSION_RECEIPT_SHA256
    ),
    "roster_release_manifest_path": ROSTER_RELEASE_MANIFEST_PATH.as_posix(),
    "roster_release_manifest_sha256": ROSTER_RELEASE_MANIFEST_SHA256,
    "consolidated_mapping_manifest_path": (
        CONSOLIDATED_MAPPING_MANIFEST_PATH.as_posix()
    ),
    "consolidated_mapping_manifest_sha256": (
        CONSOLIDATED_MAPPING_MANIFEST_SHA256
    ),
    "mapping_profile_id": MAPPING_PROFILE_ID,
    "mapping_profile_path": MAPPING_PROFILE_PATH.as_posix(),
    "mapping_profile_sha256": MAPPING_PROFILE_SHA256,
    "scenario_release_manifest_path": SCENARIO_RELEASE_MANIFEST_PATH.as_posix(),
    "scenario_release_manifest_sha256": SCENARIO_RELEASE_MANIFEST_SHA256,
}


@dataclass(frozen=True)
class PolicyRealizationAdmission:
    """Immutable result of semantic and implementation admission."""

    realization_id: str
    version: str
    status: str
    event_id: str
    project_relative_path: str
    source_sha256: str
    canonical_sha256: str
    schema_id: str
    schema_sha256: str
    semantic_complete: bool
    implementation_complete: bool
    accepted: bool
    missing_implementation_ids: tuple[str, ...]
    coverage: Mapping[str, int]
    document: Mapping[str, Any]


def _fail(
    code: PolicyRealizationErrorCode,
    *,
    pointer: str = "",
    detail: str = "",
) -> None:
    raise PolicyRealizationAdmissionError(code, pointer=pointer, detail=detail)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path, *, pointer: str) -> tuple[dict[str, Any], bytes]:
    try:
        return read_json_object(path, pointer=pointer)
    except ExecutionIOError as exc:
        codes = {
            ExecutionIOCode.SOURCE_NOT_FOUND: (
                PolicyRealizationErrorCode.SOURCE_NOT_FOUND
            ),
            ExecutionIOCode.PATH_UNSAFE: PolicyRealizationErrorCode.PATH_UNSAFE,
            ExecutionIOCode.JSON_INVALID: PolicyRealizationErrorCode.JSON_INVALID,
            ExecutionIOCode.JSON_DUPLICATE_KEY: (
                PolicyRealizationErrorCode.JSON_DUPLICATE_KEY
            ),
        }
        _fail(codes[exc.code], pointer=exc.pointer, detail=exc.detail)


def _project_root(path: Path, supplied: str | Path | None) -> Path:
    if supplied is not None:
        root = Path(supplied).resolve()
    else:
        root = next(
            (
                parent
                for parent in path.resolve().parents
                if parent.joinpath("src/h2epr").is_dir()
                and parent.joinpath("execution/schemas").is_dir()
            ),
            Path(),
        )
    if not root.is_dir() or not root.joinpath("src/h2epr").is_dir():
        _fail(PolicyRealizationErrorCode.PREFLIGHT_INVALID, detail="project_root")
    return root


def _inside(root: Path, path: Path, *, pointer: str) -> Path:
    try:
        return path_within(root, path, pointer=pointer)
    except ExecutionIOError as exc:
        _fail(
            PolicyRealizationErrorCode.PATH_UNSAFE,
            pointer=exc.pointer,
            detail=exc.detail,
        )


def _verify_parent_files(root: Path) -> None:
    for path_key, sha256_key in (
        ("configuration_path", "configuration_source_sha256"),
        (
            "configuration_release_manifest_path",
            "configuration_release_manifest_sha256",
        ),
        (
            "configuration_admission_receipt_path",
            "configuration_admission_receipt_sha256",
        ),
        ("roster_release_manifest_path", "roster_release_manifest_sha256"),
        (
            "consolidated_mapping_manifest_path",
            "consolidated_mapping_manifest_sha256",
        ),
        ("mapping_profile_path", "mapping_profile_sha256"),
        ("scenario_release_manifest_path", "scenario_release_manifest_sha256"),
    ):
        path = _inside(
            root,
            root / str(_EXPECTED_SEMANTIC_PARENT[path_key]),
            pointer=f"/semantic_parent/{path_key}",
        )
        expected = str(_EXPECTED_SEMANTIC_PARENT[sha256_key])
        if not path.is_file() or _sha256_file(path) != expected:
            _fail(
                PolicyRealizationErrorCode.INTEGRITY_MISMATCH,
                pointer=f"/semantic_parent/{path_key}",
                detail="parent_sha256_mismatch",
            )


def _validate_schema(
    root: Path,
    document: Mapping[str, Any],
) -> tuple[str, str]:
    path = _inside(
        root,
        root / POLICY_REALIZATION_SCHEMA_PATH,
        pointer="/policy_realization_schema",
    )
    schema, raw = _read_json(path, pointer="/policy_realization_schema")
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        _fail(
            PolicyRealizationErrorCode.SCHEMA_INVALID,
            pointer="/policy_realization_schema",
            detail=str(exc.validator or "draft_2020_12"),
        )
    errors = sorted(
        Draft202012Validator(schema).iter_errors(document),
        key=lambda error: tuple(str(item) for item in error.absolute_path),
    )
    if errors:
        error = errors[0]
        pointer = "/" + "/".join(
            str(item).replace("~", "~0").replace("/", "~1")
            for item in error.absolute_path
        )
        _fail(
            PolicyRealizationErrorCode.SCHEMA_VALIDATION_FAILED,
            pointer=pointer,
            detail=f"validator={error.validator}",
        )
    schema_id = schema.get("$id")
    if not isinstance(schema_id, str) or not schema_id:
        _fail(
            PolicyRealizationErrorCode.SCHEMA_INVALID,
            pointer="/policy_realization_schema/$id",
            detail="id_required",
        )
    return schema_id, hashlib.sha256(raw).hexdigest()


def _resolve_pointer(document: Any, pointer: str) -> Any:
    current = document
    for token in pointer.split("/")[1:]:
        key = token.replace("~1", "/").replace("~0", "~")
        try:
            if isinstance(current, Sequence) and not isinstance(
                current,
                (str, bytes, bytearray),
            ):
                current = current[int(key)]
            else:
                current = current[key]
        except (KeyError, IndexError, TypeError, ValueError):
            _fail(
                PolicyRealizationErrorCode.CONFIGURATION_POINTER_INVALID,
                pointer=pointer,
                detail="unresolved",
            )
    return current


def _unique_map(
    rows: Sequence[Mapping[str, Any]],
    key: str,
    *,
    pointer: str,
) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for index, row in enumerate(rows):
        value = str(row[key])
        if value in result:
            _fail(
                PolicyRealizationErrorCode.SEMANTIC_REFERENCE_INVALID,
                pointer=f"{pointer}/{index}/{key}",
                detail="duplicate",
            )
        result[value] = row
    return result


def _require_exact_set(
    actual: set[str],
    expected: set[str],
    *,
    code: PolicyRealizationErrorCode,
    pointer: str,
) -> None:
    if actual != expected:
        _fail(
            code,
            pointer=pointer,
            detail=(
                f"missing={','.join(sorted(expected - actual))}:"
                f"extra={','.join(sorted(actual - expected))}"
            ),
        )


def _implementation_ref(
    row: Mapping[str, Any],
    *,
    pointer: str,
    declared: dict[str, str],
) -> None:
    identifier = str(row["implementation_id"])
    version = str(row["implementation_version"])
    prior = declared.get(identifier)
    if prior is not None and prior != version:
        _fail(
            PolicyRealizationErrorCode.IMPLEMENTATION_VERSION_MISMATCH,
            pointer=pointer,
            detail=identifier,
        )
    declared[identifier] = version


def _validate_participants(
    document: Mapping[str, Any],
    catalog: Note7PolicyCatalog,
    configuration: Mapping[str, Any],
    declared_implementations: dict[str, str],
) -> None:
    rows = document["participant_policy_realizations"]
    by_key = _unique_map(
        rows,
        "realization_key",
        pointer="/participant_policy_realizations",
    )
    _require_exact_set(
        set(by_key),
        set(catalog.placements),
        code=PolicyRealizationErrorCode.PLACEMENT_COVERAGE_MISMATCH,
        pointer="/participant_policy_realizations",
    )
    policies = participant_policies_by_capability()
    for key, placement in catalog.placements.items():
        row = by_key[key]
        pointer = f"/participant_policy_realizations/{key}"
        if (
            row["actor_id"],
            row["capability_id"],
            row["participant_product_id"],
        ) != (
            placement.actor_id,
            placement.capability_id,
            placement.participant_product_id,
        ):
            _fail(
                PolicyRealizationErrorCode.SEMANTIC_REFERENCE_INVALID,
                pointer=pointer,
                detail="placement_identity_mismatch",
            )
        policy = policies[placement.capability_id]
        if (
            row["implementation_id"] != policy.implementation_id
            or row["implementation_version"]
            != policy.implementation_version
        ):
            _fail(
                PolicyRealizationErrorCode.SEMANTIC_REFERENCE_INVALID,
                pointer=f"{pointer}/implementation_id",
                detail="capability_implementation_mismatch",
            )
        _implementation_ref(
            row,
            pointer=f"{pointer}/implementation_id",
            declared=declared_implementations,
        )

        bindings = {
            (str(item["parameter_id"]), str(item["source_pointer"]))
            for item in row["configuration_parameter_bindings"]
        }
        if bindings != set(placement.configuration_parameter_bindings):
            _fail(
                PolicyRealizationErrorCode.CONFIGURATION_POINTER_INVALID,
                pointer=f"{pointer}/configuration_parameter_bindings",
                detail="binding_set_mismatch",
            )
        for _, source_pointer in bindings:
            _resolve_pointer(configuration, source_pointer)

        states = _unique_map(
            row["private_state_realizations"],
            "state_id",
            pointer=f"{pointer}/private_state_realizations",
        )
        _require_exact_set(
            set(states),
            set(policy.private_state_ids),
            code=PolicyRealizationErrorCode.SEMANTIC_REFERENCE_INVALID,
            pointer=f"{pointer}/private_state_realizations",
        )
        allowed_triggers = (
            set(policy.observation_ids)
            | set(policy.intent_ids)
            | set(policy.lifecycle_ids)
        )
        if any(
            not set(state["update_trigger_ids"]) <= allowed_triggers
            for state in states.values()
        ):
            _fail(
                PolicyRealizationErrorCode.SEMANTIC_REFERENCE_INVALID,
                pointer=f"{pointer}/private_state_realizations",
                detail="state_trigger_unresolved",
            )

        decisions = _unique_map(
            row["decision_realizations"],
            "commitment_id",
            pointer=f"{pointer}/decision_realizations",
        )
        _require_exact_set(
            set(decisions),
            set(policy.commitment_ids),
            code=PolicyRealizationErrorCode.SEMANTIC_REFERENCE_INVALID,
            pointer=f"{pointer}/decision_realizations",
        )
        for commitment_id, expected in policy.decisions.items():
            decision = decisions[commitment_id]
            actual = {
                "consumed_observation_ids": set(
                    decision["consumed_observation_ids"]
                ),
                "persistent_state_ids": set(
                    decision["persistent_state_ids"]
                ),
                "emittable_intent_ids": set(
                    decision["emittable_intent_ids"]
                ),
                "no_intent_reason_codes": set(
                    decision["no_intent_reason_codes"]
                ),
                "revisit_trigger_ids": set(
                    decision["revisit_trigger_ids"]
                ),
                "lifecycle_ids": set(decision["lifecycle_ids"]),
            }
            expected_sets = {
                "consumed_observation_ids": set(expected.observation_ids),
                "persistent_state_ids": set(expected.private_state_ids),
                "emittable_intent_ids": set(expected.intent_ids),
                "no_intent_reason_codes": set(
                    expected.no_intent_reason_codes
                ),
                "revisit_trigger_ids": set(expected.revisit_trigger_ids),
                "lifecycle_ids": set(expected.lifecycle_ids),
            }
            if actual != expected_sets:
                _fail(
                    PolicyRealizationErrorCode.SEMANTIC_REFERENCE_INVALID,
                    pointer=f"{pointer}/decision_realizations/{commitment_id}",
                    detail="decision_implementation_mismatch",
                )


def _validate_scenario_policies(
    document: Mapping[str, Any],
    catalog: Note7PolicyCatalog,
    configuration: Mapping[str, Any],
    declared_implementations: dict[str, str],
) -> None:
    rows = _unique_map(
        document["scenario_policy_realizations"],
        "policy_id",
        pointer="/scenario_policy_realizations",
    )
    _require_exact_set(
        set(rows),
        set(catalog.selected_policy_ids),
        code=PolicyRealizationErrorCode.POLICY_COVERAGE_MISMATCH,
        pointer="/scenario_policy_realizations",
    )
    configured = {
        str(row["policy_id"]): row
        for row in configuration["policy_selections"]
    }
    implemented = {
        policy.policy_id: policy for policy in scenario_policies().values()
    }
    for policy_id, row in rows.items():
        pointer = f"/scenario_policy_realizations/{policy_id}"
        selected = configured[policy_id]
        policy = implemented[policy_id]
        expected_pointer = catalog.selected_policy_pointers[policy_id]
        if (
            row["semantic_version"] != selected["semantic_version"]
            or row["selection"] != selected["selection"]
            or set(row["configuration_source_pointers"])
            != {expected_pointer}
            or row["implementation_id"] != policy.implementation_id
            or row["implementation_version"]
            != policy.implementation_version
            or row["owner_layer"] != policy.owner_layer
            or set(row["governed_semantic_ids"])
            != set(policy.governed_semantic_ids)
            or set(row["rejection_reason_codes"])
            != set(policy.rejection_reason_codes)
        ):
            _fail(
                PolicyRealizationErrorCode.POLICY_COVERAGE_MISMATCH,
                pointer=pointer,
                detail="policy_implementation_mismatch",
            )
        _resolve_pointer(configuration, expected_pointer)
        _implementation_ref(
            row,
            pointer=f"{pointer}/implementation_id",
            declared=declared_implementations,
        )


def _validate_lifecycles(
    document: Mapping[str, Any],
    catalog: Note7PolicyCatalog,
    declared_implementations: dict[str, str],
) -> None:
    rows = _unique_map(
        document["lifecycle_realizations"],
        "lifecycle_id",
        pointer="/lifecycle_realizations",
    )
    _require_exact_set(
        set(rows),
        set(catalog.lifecycle_ids),
        code=PolicyRealizationErrorCode.LIFECYCLE_COVERAGE_MISMATCH,
        pointer="/lifecycle_realizations",
    )
    implemented = {
        rule.lifecycle_id: rule for rule in lifecycle_rules().values()
    }
    for lifecycle_id, row in rows.items():
        rule = implemented[lifecycle_id]
        pointer = f"/lifecycle_realizations/{lifecycle_id}"
        if (
            row["implementation_id"] != rule.implementation_id
            or row["implementation_version"]
            != rule.implementation_version
            or row["owner_layer"] != rule.owner_layer
            or set(row["participant_capability_ids"])
            != set(rule.participant_capability_ids)
            or set(row["state_ids"]) != set(rule.state_ids)
            or set(row["terminal_state_ids"])
            != set(rule.terminal_state_ids)
            or row["invalid_transition_behavior"]
            != rule.invalid_transition_behavior
        ):
            _fail(
                PolicyRealizationErrorCode.LIFECYCLE_COVERAGE_MISMATCH,
                pointer=pointer,
                detail="lifecycle_implementation_mismatch",
            )
        _implementation_ref(
            row,
            pointer=f"{pointer}/implementation_id",
            declared=declared_implementations,
        )


def _validate_coverage(
    document: Mapping[str, Any],
    catalog: Note7PolicyCatalog,
) -> None:
    actual = {
        key: document["coverage_expectations"][key]
        for key in _COVERAGE_KEYS
    }
    expected = {key: catalog.coverage[key] for key in _COVERAGE_KEYS}
    if actual != expected:
        _fail(
            PolicyRealizationErrorCode.COVERAGE_MISMATCH,
            pointer="/coverage_expectations",
            detail=f"expected={expected}:actual={actual}",
        )


def _verify_configuration_receipt(root: Path) -> None:
    receipt, _ = _read_json(
        root / CONFIGURATION_ADMISSION_RECEIPT_PATH,
        pointer="/semantic_parent/configuration_admission_receipt_path",
    )
    configuration = receipt.get("configuration", {})
    execution = receipt.get("execution_boundary", {})
    if (
        receipt.get("verdict") != "PASS_BOUNDED_CONFIGURATION_ADMISSION"
        or configuration.get("configuration_id") != CONFIGURATION_ID
        or configuration.get("source_sha256") != CONFIGURATION_SOURCE_SHA256
        or configuration.get("canonical_sha256")
        != CONFIGURATION_CANONICAL_SHA256
        or execution.get("execution_eligible") is not False
    ):
        _fail(
            PolicyRealizationErrorCode.PARENT_MISMATCH,
            pointer="/semantic_parent/configuration_admission_receipt_path",
            detail="receipt_boundary_mismatch",
        )


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType(
            {key: _freeze(item) for key, item in value.items()}
        )
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def load_note7_policy_realization(
    realization_path: str | Path,
    *,
    expected_source_sha256: str | None,
    project_root: str | Path | None = None,
) -> PolicyRealizationAdmission:
    """Validate one candidate or accepted Note7 Policy Realization."""

    if (
        not isinstance(expected_source_sha256, str)
        or _SHA256.fullmatch(expected_source_sha256) is None
    ):
        _fail(
            PolicyRealizationErrorCode.PREFLIGHT_INVALID,
            pointer="/expected_source_sha256",
            detail="sha256_required",
        )
    supplied = Path(realization_path)
    root = _project_root(supplied, project_root)
    path = _inside(
        root,
        supplied if supplied.is_absolute() else root / supplied,
        pointer="/policy_realization",
    )
    document, raw = _read_json(path, pointer="/policy_realization")
    source_sha256 = hashlib.sha256(raw).hexdigest()
    if source_sha256 != expected_source_sha256:
        _fail(
            PolicyRealizationErrorCode.INTEGRITY_MISMATCH,
            pointer="/policy_realization",
            detail="expected_source_sha256_mismatch",
        )
    schema_id, schema_sha256 = _validate_schema(root, document)
    if document.get("format_identity") != POLICY_REALIZATION_FORMAT:
        _fail(
            PolicyRealizationErrorCode.SCHEMA_VALIDATION_FAILED,
            pointer="/format_identity",
            detail="unsupported",
        )
    if document.get("event_id") != EVENT_ID:
        _fail(
            PolicyRealizationErrorCode.PARENT_MISMATCH,
            pointer="/event_id",
            detail="event_identity",
        )
    if document.get("semantic_parent") != _EXPECTED_SEMANTIC_PARENT:
        _fail(
            PolicyRealizationErrorCode.PARENT_MISMATCH,
            pointer="/semantic_parent",
            detail="exact_parent_required",
        )
    _verify_parent_files(root)
    _verify_configuration_receipt(root)
    try:
        catalog = build_note7_policy_catalog(project_root=root)
    except Note7PolicyCatalogError as exc:
        _fail(
            PolicyRealizationErrorCode.PARENT_MISMATCH,
            pointer="/semantic_parent",
            detail=str(exc),
        )
    configuration, _ = _read_json(
        root / CONFIGURATION_PATH,
        pointer="/semantic_parent/configuration_path",
    )
    declared_implementations: dict[str, str] = {}
    _validate_participants(
        document,
        catalog,
        configuration,
        declared_implementations,
    )
    _validate_scenario_policies(
        document,
        catalog,
        configuration,
        declared_implementations,
    )
    _validate_lifecycles(document, catalog, declared_implementations)
    _validate_coverage(document, catalog)

    available = implementation_versions()
    missing: list[str] = []
    for identifier, version in sorted(declared_implementations.items()):
        actual = available.get(identifier)
        if actual is None:
            missing.append(identifier)
        elif actual != version:
            _fail(
                PolicyRealizationErrorCode.IMPLEMENTATION_VERSION_MISMATCH,
                pointer="/implementation_registry",
                detail=f"{identifier}:expected={version}:actual={actual}",
            )
    if document["status"] == "accepted_policy_realization" and missing:
        _fail(
            PolicyRealizationErrorCode.IMPLEMENTATION_MISSING,
            pointer="/implementation_registry",
            detail=",".join(missing),
        )
    accepted = document["status"] == "accepted_policy_realization" and not missing
    return PolicyRealizationAdmission(
        realization_id=document["realization_id"],
        version=document["version"],
        status=document["status"],
        event_id=document["event_id"],
        project_relative_path=path.relative_to(root).as_posix(),
        source_sha256=source_sha256,
        canonical_sha256=sha256_value(document),
        schema_id=schema_id,
        schema_sha256=schema_sha256,
        semantic_complete=True,
        implementation_complete=not missing,
        accepted=accepted,
        missing_implementation_ids=tuple(missing),
        coverage=MappingProxyType(
            {key: int(catalog.coverage[key]) for key in _COVERAGE_KEYS}
        ),
        document=_freeze(copy.deepcopy(document)),
    )


def expected_note7_semantic_parent() -> Mapping[str, Any]:
    """Return the exact semantic-parent identity required by this admission."""

    return MappingProxyType(copy.deepcopy(_EXPECTED_SEMANTIC_PARENT))


__all__ = [
    "PolicyRealizationAdmission",
    "expected_note7_semantic_parent",
    "load_note7_policy_realization",
]
