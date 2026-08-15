"""Fail-closed adapter from accepted G2 rows to G3 scientific inputs."""

from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from h2epr.bundles import build_panic_1907_bundle_set
from h2epr.bundles.canonical import manifest_hash
from h2epr.bundles.validation import validate_bundle_pair, validate_execution_manifest


POLICY_ID = "h2epr.0288.rule.runtime.policy.v1"
PROFILE_ORDER = ("low_stress", "balanced", "high_stress")
ACTOR_IDS = (
    "depositors_cohort",
    "jp_morgan",
    "knickerbocker_trust",
    "member_banks_cohort",
    "nych",
    "nyse",
    "other_trusts_cohort",
)


@dataclass(frozen=True)
class AcceptedRunInput:
    row: dict[str, Any]
    event_bundle: dict[str, Any]
    run_manifest: dict[str, Any]
    initial_state: dict[str, Any]
    action_spaces: dict[str, tuple[str, ...]]


def _reject_runtime_fields(config: Mapping[str, Any]) -> None:
    forbidden = {
        "knowledge",
        "rag",
        "model",
        "provider",
        "client",
        "api_key",
        "runtime_env_pip",
        "remote_ray_address",
        "reference_locator",
        "resume",
    }
    for key, value in config.items():
        if key.lower() in forbidden and value not in (None, False, "", [], {}):
            raise ValueError(f"forbidden_runtime_field:{key}")


def validate_run_input(row: Mapping[str, Any], bundle: Mapping[str, Any], *, runtime_config: Mapping[str, Any] | None = None) -> None:
    if set(row) != {
        "case_id",
        "profile_id",
        "profile_event_bundle_logical_name",
        "profile_event_bundle_sha256",
        "run_seed",
    }:
        raise ValueError("execution_row_shape_mismatch")
    profile = row["profile_id"]
    if profile not in PROFILE_ORDER or row["case_id"] != f"{profile}.seed.{row['run_seed']}":
        raise ValueError("execution_row_identity_mismatch")
    if row["profile_event_bundle_logical_name"] != f"event_bundles/{profile}.json":
        raise ValueError("execution_row_logical_name_mismatch")
    if row["profile_event_bundle_sha256"] != bundle.get("artifact_sha256"):
        raise ValueError("execution_row_bundle_hash_mismatch")
    context = bundle.get("protocol_context", {})
    if context.get("contamination_status") != "full_draft_exposed" or context.get("protocol_eligibility") != "architecture_demo_only":
        raise ValueError("runtime_identity_not_demo_eligible")
    if bundle.get("backend") != "rule" or bundle.get("resume_allowed") is not False:
        raise ValueError("runtime_backend_or_resume_mismatch")
    if bundle.get("exogenous_manifest") != []:
        raise ValueError("historical_exogenous_manifest_forbidden")
    if bundle.get("source_kind") != "authentic_finmycelium_draft":
        raise ValueError("unlisted_source_parent")
    _reject_runtime_fields(runtime_config or {})


def _value(field: Mapping[str, Any]) -> Any:
    if "value" in field:
        return field["value"]
    return field["runtime_value"]["value"]


def _initial_state(bundle: Mapping[str, Any]) -> dict[str, Any]:
    world = bundle["initial_world_state"]
    actors: dict[str, dict[str, Any]] = {
        actor_id: {
            "liquid_resource_bp": None,
            "confidence_index_bp": None,
            "withdrawal_pressure_bp": None,
            "coordination_readiness_bp": None,
            "resource_stress_bp": None,
            "operational_status": "open",
        }
        for actor_id in ACTOR_IDS
    }
    withdrawal_demand = 0
    for resource in world["resources"]:
        owner = resource["owner_entity_id"]
        resource_type = resource["resource_type"]
        quantity = _value(resource["quantity"])
        if owner == "depositors_cohort" and resource_type == "withdrawal_demand_bp":
            withdrawal_demand = quantity
        elif owner in actors:
            actors[owner][resource_type] = quantity
    for field in world["process_states"]:
        name = field["field_name"]
        actor_id = name.rsplit(".", 1)[-1]
        if actor_id in actors:
            actors[actor_id]["operational_status"] = _value(field)
    exposures: list[tuple[str, str, int]] = []
    for field in world["relations"]:
        _, _, source, target = field["field_name"].split(".")
        exposures.append((source, target, _value(field)))
    return {
        "state_version": 0,
        "actors": actors,
        "withdrawal_demand_bp": withdrawal_demand,
        "exposures": [list(item) for item in sorted(exposures)],
    }


def _run_manifest(row: Mapping[str, Any], bundle: Mapping[str, Any]) -> dict[str, Any]:
    identity_preimage = {
        "case_id": row["case_id"],
        "event_bundle_sha256": bundle["artifact_sha256"],
        "policy_id": POLICY_ID,
        "run_seed": row["run_seed"],
    }
    run_id = "run." + hashlib.sha256(
        repr(sorted(identity_preimage.items())).encode("utf-8")
    ).hexdigest()[:24]
    manifest = {
        "manifest_version": "h2epr.g3.run_manifest.v1",
        "run_id": run_id,
        **identity_preimage,
        "event_bundle_id": bundle["runtime_bundle_id"],
        "construction_parent": copy.deepcopy(bundle["source_construction_bundle"]),
        "protocol_context": copy.deepcopy(bundle["protocol_context"]),
        "backend": "rule",
        "not_historically_calibrated": True,
        "logical_clock": {
            "start_date": "1907-10-21",
            "end_date": "1907-11-30",
            "inclusive_tick_count": 41,
            "date_semantics": "neutral_clock_coordinate",
        },
        "participant_ids": list(ACTOR_IDS),
        "manifest_sha256": "0" * 64,
    }
    manifest["manifest_sha256"] = manifest_hash(manifest)
    return manifest


def build_accepted_run_input(approved_root: Path, case_id: str, *, runtime_config: Mapping[str, Any] | None = None) -> AcceptedRunInput:
    candidate = build_panic_1907_bundle_set(approved_root)
    if candidate.validation_errors:
        raise ValueError("g2_builder_validation_failed")
    rows = [item for item in candidate.execution_manifest["execution_matrix"] if item["case_id"] == case_id]
    if len(rows) != 1:
        raise ValueError("execution_case_cardinality_mismatch")
    row = copy.deepcopy(rows[0])
    bundle = copy.deepcopy(candidate.event_bundles[row["profile_id"]])
    if validate_bundle_pair(candidate.constructions[row["profile_id"]], bundle):
        raise ValueError("g2_bundle_pair_invalid")
    if validate_execution_manifest(candidate.execution_manifest, candidate.event_bundles):
        raise ValueError("g2_execution_manifest_invalid")
    validate_run_input(row, bundle, runtime_config=runtime_config)
    action_spaces = {
        item["runtime_actor_id"]: tuple(item["action_space_refs"])
        for item in bundle["participant_artifacts"]
    }
    if set(action_spaces) != set(ACTOR_IDS):
        raise ValueError("participant_universe_mismatch")
    return AcceptedRunInput(row, bundle, _run_manifest(row, bundle), _initial_state(bundle), action_spaces)
