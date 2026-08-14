"""Offline schema and cross-object validation for G2 artifacts."""

from __future__ import annotations

import copy
import json
import warnings
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

warnings.filterwarnings(
    "ignore", category=DeprecationWarning, message="jsonschema.RefResolver.*"
)
from jsonschema import Draft202012Validator, RefResolver

from h2epr.artifacts.provenance import TARGET_IDENTITY
from h2epr.artifacts.registry import RegistryCompilation, validate_registry_compilation
from h2epr.policies.rules import validate_rule_policy
from h2epr.world.normalized import PROFILES, validate_world

from .canonical import construction_bundle_hash, runtime_bundle_hash


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_ROOT = PROJECT_ROOT / "contracts" / "v1" / "schemas"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_store() -> tuple[dict[str, Any], dict[str, Path]]:
    store: dict[str, Any] = {}
    by_name: dict[str, Path] = {}
    for path in sorted(SCHEMA_ROOT.rglob("*.schema.json")):
        document = _load_json(path)
        if path.name in by_name or document["$id"] in store:
            raise RuntimeError("duplicate_schema_identity")
        by_name[path.name] = path
        store[document["$id"]] = document
    return store, by_name


def schema_errors(schema_name: str, instance: Any) -> list[str]:
    store, by_name = _schema_store()
    schema = _load_json(by_name[schema_name])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        validator = Draft202012Validator(
            schema, resolver=RefResolver.from_schema(schema, store=store)
        )
    errors = sorted(
        validator.iter_errors(instance), key=lambda item: list(item.absolute_path)
    )
    return [
        f"/{'/'.join(str(part) for part in error.absolute_path)}:{error.validator}"
        for error in errors
    ]


def _walk_runtime_values(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        required = {
            "value",
            "provenance",
            "availability_at_t0",
            "visibility",
            "consumers",
            "review_state",
        }
        if required.issubset(value):
            yield value
        for child in value.values():
            yield from _walk_runtime_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_runtime_values(child)


def runtime_value_errors(root: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for runtime_value in _walk_runtime_values(root):
        top = (
            runtime_value["availability_at_t0"],
            runtime_value["visibility"],
            runtime_value["consumers"],
            runtime_value["review_state"],
        )
        for provenance in runtime_value["provenance"]:
            observed = (
                provenance.get("availability_at_t0"),
                provenance.get("visibility"),
                provenance.get("consumers"),
                provenance.get("review_state"),
            )
            if observed != top:
                errors.append("PROVENANCE_RUNTIME_METADATA_MISMATCH")
            if provenance.get("availability_at_t0") in {
                "unknown",
                "unavailable",
                "construction_only_contaminated",
            } and (
                runtime_value["availability_at_t0"] == "available"
                or runtime_value["visibility"] == "runtime_public"
            ):
                errors.append("NONAVAILABLE_VALUE_EXPOSED")
    return errors


def _identity_tuple_errors(identity: dict[str, Any]) -> list[str]:
    return [
        f"TARGET_IDENTITY_MISMATCH:{key}"
        for key, value in TARGET_IDENTITY.items()
        if identity.get(key) != value
    ]


def validate_bundle_pair(
    construction: dict[str, Any], runtime: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    errors.extend(
        "CONSTRUCTION_SCHEMA:" + item
        for item in schema_errors(
            "full_draft_target_demo_construction_bundle.schema.json", construction
        )
    )
    errors.extend(
        "RUNTIME_SCHEMA:" + item
        for item in schema_errors("runtime_scenario_bundle.schema.json", runtime)
    )
    errors.extend(_identity_tuple_errors(construction.get("artifact_identity", {})))
    errors.extend(_identity_tuple_errors(runtime.get("artifact_identity", {})))
    if construction_bundle_hash(construction) != construction.get(
        "construction_seal", {}
    ).get("content_sha256"):
        errors.append("CONSTRUCTION_SEAL_MISMATCH")
    if runtime_bundle_hash(runtime) != runtime.get("artifact_sha256"):
        errors.append("RUNTIME_HASH_MISMATCH")
    construction_ref = {
        "artifact_id": construction.get("artifact_identity", {}).get("artifact_id"),
        "artifact_kind": construction.get("artifact_identity", {}).get("artifact_kind"),
        **{
            key: construction.get("artifact_identity", {}).get(key)
            for key in TARGET_IDENTITY
        },
        "artifact_sha256": construction.get("construction_seal", {}).get(
            "content_sha256"
        ),
    }
    if runtime.get("source_construction_bundle") != construction_ref:
        errors.append("SOURCE_CONSTRUCTION_PARENT_MISMATCH")
    if runtime.get("artifact_identity", {}).get("parent_artifacts") != [
        construction_ref
    ]:
        errors.append("RUNTIME_PARENT_MISMATCH")
    if runtime.get("protocol_context", {}).get(
        "root_construction_artifact_id"
    ) != construction_ref["artifact_id"]:
        errors.append("ROOT_CONSTRUCTION_ID_MISMATCH")
    if runtime.get("entity_registry") != construction.get("entity_registry"):
        errors.append("ENTITY_REGISTRY_COMPILATION_MISMATCH")
    expected_participants = copy.deepcopy(construction.get("participant_artifacts"))
    if isinstance(expected_participants, list):
        for participant in expected_participants:
            identity = (
                participant.get("artifact_identity")
                if isinstance(participant, dict)
                else None
            )
            if not isinstance(identity, dict):
                expected_participants = None
                break
            identity["parent_artifacts"] = [copy.deepcopy(construction_ref)]
    if runtime.get("participant_artifacts") != expected_participants:
        errors.append("PARTICIPANT_ARTIFACT_PROJECTION_MISMATCH")
    if runtime.get("action_registry") != construction.get("action_registry"):
        errors.append("ACTION_REGISTRY_PROJECTION_MISMATCH")
    if runtime.get("communication_routes") != construction.get(
        "communication_routes"
    ):
        errors.append("COMMUNICATION_ROUTE_PROJECTION_MISMATCH")
    if runtime.get("observation_access_rules") != construction.get(
        "observation_access_rules"
    ):
        errors.append("OBSERVATION_ACCESS_PROJECTION_MISMATCH")
    if runtime.get("initial_world_state") != construction.get("initial_world_state"):
        errors.append("WORLD_COMPILATION_MISMATCH")
    if runtime.get("exogenous_manifest"):
        errors.append("HISTORICAL_EXOGENOUS_NOT_EMPTY")
    errors.extend(runtime_value_errors(construction))
    errors.extend(runtime_value_errors(runtime))
    serialized = json.dumps(runtime, ensure_ascii=False).lower()
    for forbidden in (
        "reference_epg",
        "expected_outcome",
        "future_episode",
        "future_stage",
    ):
        if forbidden in serialized:
            errors.append(f"FORBIDDEN_RUNTIME_MARKER:{forbidden}")
    return sorted(set(errors))


def validate_execution_manifest(
    manifest: dict[str, Any], event_bundles: dict[str, dict[str, Any]]
) -> list[str]:
    errors: list[str] = []
    rows = manifest.get("execution_matrix", [])
    if len(rows) != 9:
        errors.append("EXECUTION_MATRIX_CARDINALITY")
    expected_rows = {
        (profile_id, seed) for profile_id in sorted(PROFILES) for seed in (0, 1, 2)
    }
    observed_rows = {(row.get("profile_id"), row.get("run_seed")) for row in rows}
    if observed_rows != expected_rows:
        errors.append("EXECUTION_MATRIX_PRODUCT_MISMATCH")
    expected_fields = {
        "case_id",
        "profile_id",
        "profile_event_bundle_logical_name",
        "profile_event_bundle_sha256",
        "run_seed",
    }
    for row in rows:
        if set(row) != expected_fields:
            errors.append("EXECUTION_MATRIX_FIELD_MISMATCH")
        logical_name = row.get("profile_event_bundle_logical_name")
        if not isinstance(logical_name, str):
            errors.append("EVENT_BUNDLE_LOGICAL_NAME_INVALID")
            continue
        pure = PurePosixPath(logical_name)
        if pure.is_absolute() or ".." in pure.parts:
            errors.append("ABSOLUTE_OR_TRAVERSING_LOGICAL_NAME")
        profile_id = row.get("profile_id")
        if isinstance(profile_id, str) and logical_name != (
            f"event_bundles/{profile_id}.json"
        ):
            errors.append("MATRIX_BUNDLE_LOGICAL_NAME_MISMATCH")
        bundle = event_bundles.get(profile_id)
        if bundle is None or row.get("profile_event_bundle_sha256") != bundle.get(
            "artifact_sha256"
        ):
            errors.append("MATRIX_BUNDLE_HASH_MISMATCH")
    return sorted(set(errors))


def validate_g2_objects(
    *,
    registry: RegistryCompilation,
    policies: list[dict],
    constructions: dict[str, dict],
    event_bundles: dict[str, dict],
    execution_manifest: dict,
    resource_owners: Iterable[str],
) -> list[str]:
    errors = validate_registry_compilation(registry)
    for policy in policies:
        errors.extend(validate_rule_policy(policy))
    if set(constructions) != set(PROFILES) or set(event_bundles) != set(PROFILES):
        errors.append("PROFILE_BUNDLE_UNIVERSE_MISMATCH")
    for profile_id in sorted(set(constructions) & set(event_bundles)):
        errors.extend(validate_bundle_pair(constructions[profile_id], event_bundles[profile_id]))
        errors.extend(
            validate_world(
                constructions[profile_id]["initial_world_state"],
                owners=resource_owners,
            )
        )
    errors.extend(validate_execution_manifest(execution_manifest, event_bundles))
    return sorted(set(errors))
