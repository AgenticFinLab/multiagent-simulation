"""Fail-closed adapter from immutable G2/G3 evidence to V1 wrappers."""

from __future__ import annotations

import copy
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Mapping

from masim.integrations.event_process import (
    RunSeal as RawRunSeal,
    TickSeal as RawTickSeal,
    canonical_sha256 as raw_sha256,
    replay_trace as replay_raw_trace,
    validate_trace as validate_raw_trace,
)

from h2epr.bundles.canonical import (
    manifest_hash as g2_manifest_hash,
    runtime_bundle_hash,
    sha256_value,
)

from .canonical import (
    CANONICALIZATION_VERSION,
    manifest_sha256,
    record_sha256,
    stable_id,
    trace_sha256,
)
from .inventory import LoadedInventory
from .policy import CompilerPolicy
from .schema import require_schema


class SourcePackageError(ValueError):
    """The immutable G2/G3 source package is not eligible for compilation."""


@dataclass(frozen=True)
class SourcePackage:
    raw_manifest: dict[str, Any]
    raw_records: tuple[dict[str, Any], ...]
    final_state: dict[str, Any]
    annotations: tuple[dict[str, Any], ...]
    tick_seals: tuple[dict[str, Any], ...]
    run_seal: dict[str, Any]
    replay_receipt: dict[str, Any]
    event_bundle: dict[str, Any]
    roster_report: dict[str, Any]
    execution_matrix: dict[str, Any]
    inventory_receipt: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class V1Wrappers:
    run_manifest: dict[str, Any]
    simulation_trace: dict[str, Any]


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise SourcePackageError(code)


def _initial_state_from_trace(
    rows: list[dict[str, Any]], actor_ids: list[str]
) -> dict[str, Any]:
    first_tick = min(row["logical_tick"] for row in rows if row["record_type"] == "tick_open")
    observations = [
        row["payload"]
        for row in rows
        if row["record_type"] == "observation" and row["logical_tick"] == first_tick
    ]
    _require(len(observations) == len(actor_ids), "initial_observation_cardinality_mismatch")
    _require(sorted(item["actor_id"] for item in observations) == actor_ids, "initial_observation_actor_universe_mismatch")
    states = [item["public_state"] for item in observations]
    _require(all(item == states[0] for item in states), "initial_observation_state_disagreement")
    _require(all(item["prestate_version"] == states[0]["state_version"] for item in observations), "initial_observation_state_version_mismatch")
    _require(all(item["prestate_sha256"] == raw_sha256(states[0]) for item in observations), "initial_observation_state_hash_mismatch")
    return copy.deepcopy(states[0])


def _apply_raw_delta(state: dict[str, Any], payload: Mapping[str, Any]) -> None:
    target = state if payload["entity_id"] == "__world__" else state["actors"][payload["entity_id"]]
    _require(target[payload["field_name"]] == payload["before"], "replay_delta_before_mismatch")
    target[payload["field_name"]] = payload["after"]


def _validate_raw_seals(package: SourcePackage) -> None:
    rows = list(package.raw_records)
    _require(validate_raw_trace(rows) == [], "raw_trace_invalid")
    trace_tick_payloads = [row["payload"] for row in rows if row["record_type"] == "tick_seal"]
    _require(trace_tick_payloads == list(package.tick_seals), "tick_seal_file_trace_mismatch")
    verified_ticks: list[RawTickSeal] = []
    for payload in package.tick_seals:
        seal = RawTickSeal(
            run_id=payload["run_id"],
            logical_tick=payload["logical_tick"],
            manifest_sha256=payload["manifest_sha256"],
            first_record_hash=payload["first_record_hash"],
            final_preseal_record_hash=payload["final_preseal_record_hash"],
            state_sha256=payload["state_sha256"],
            record_count=payload["record_count"],
            seal_sha256=payload["seal_sha256"],
        )
        _require(seal.verify(), "raw_tick_seal_invalid")
        tick_rows = [
            row
            for row in rows
            if row["logical_tick"] == seal.logical_tick
            and row["record_type"] not in {"tick_seal", "run_seal"}
        ]
        _require(bool(tick_rows), "raw_tick_without_scientific_records")
        _require(seal.first_record_hash == tick_rows[0]["record_hash"], "raw_tick_first_hash_mismatch")
        _require(seal.final_preseal_record_hash == tick_rows[-1]["record_hash"], "raw_tick_last_hash_mismatch")
        _require(seal.record_count == len(tick_rows), "raw_tick_record_count_mismatch")
        commits = [row for row in tick_rows if row["record_type"] == "tick_commit"]
        _require(len(commits) == 1, "raw_tick_commit_cardinality")
        _require(seal.state_sha256 == commits[0]["payload"]["state_sha256"], "raw_tick_state_hash_mismatch")
        _require(seal.manifest_sha256 == package.raw_manifest["manifest_sha256"], "raw_tick_manifest_hash_mismatch")
        verified_ticks.append(seal)
    raw_run_payloads = [row["payload"] for row in rows if row["record_type"] == "run_seal"]
    _require(raw_run_payloads == [package.run_seal], "run_seal_file_trace_mismatch")
    payload = package.run_seal
    seal = RawRunSeal(
        run_id=payload["run_id"],
        manifest_sha256=payload["manifest_sha256"],
        ordered_tick_seal_hashes=tuple(payload["ordered_tick_seal_hashes"]),
        scientific_prefix_sha256=payload["scientific_prefix_sha256"],
        final_state_sha256=payload["final_state_sha256"],
        unresolved_intent_ids=tuple(payload["unresolved_intent_ids"]),
        unresolved_recipient_ids=tuple(payload["unresolved_recipient_ids"]),
        seal_sha256=payload["seal_sha256"],
    )
    _require(seal.verify(), "raw_run_seal_invalid")
    _require(
        list(seal.ordered_tick_seal_hashes) == [item.seal_sha256 for item in verified_ticks],
        "raw_run_tick_seal_set_mismatch",
    )
    _require(
        seal.scientific_prefix_sha256 == raw_sha256(rows[:-1]),
        "raw_run_prefix_hash_mismatch",
    )
    message_intents = {
        row["payload"]["message_intent_id"]: row["payload"]
        for row in rows
        if row["record_type"] == "message_intent"
    }
    disposition_history: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["record_type"] == "message_disposition":
            disposition_history[row["payload"]["message_intent_id"]].append(row["payload"])
    _require(set(disposition_history) == set(message_intents), "raw_message_disposition_universe_mismatch")
    unresolved_ids: list[str] = []
    unresolved_recipients: list[str] = []
    for intent_id in sorted(message_intents):
        history = disposition_history[intent_id]
        _require(history[0]["status"] == "queued", "raw_message_initial_disposition_not_queued")
        for index, disposition in enumerate(history):
            expected_predecessor = None if index == 0 else history[index - 1]["disposition_id"]
            _require(disposition["predecessor_disposition_id"] == expected_predecessor, "raw_message_disposition_predecessor_mismatch")
            _require(disposition["sender_id"] == message_intents[intent_id]["sender_id"], "raw_message_sender_mismatch")
            _require(disposition["recipient_id"] == message_intents[intent_id]["recipient_id"], "raw_message_recipient_mismatch")
        _require(tuple(item["status"] for item in history) in {("queued",), ("queued", "delivered")}, "raw_message_disposition_history_invalid")
        if history[-1]["status"] == "queued":
            unresolved_ids.append(intent_id)
            unresolved_recipients.append(f"{intent_id}:{message_intents[intent_id]['recipient_id']}")
    _require(list(seal.unresolved_intent_ids) == unresolved_ids, "raw_run_unresolved_intent_set_mismatch")
    _require(list(seal.unresolved_recipient_ids) == sorted(unresolved_recipients), "raw_run_unresolved_recipient_set_mismatch")


def _validate_lineage(package: SourcePackage) -> None:
    manifest = package.raw_manifest
    bundle = package.event_bundle
    matrix = package.execution_matrix
    roster = package.roster_report
    _require(g2_manifest_hash(manifest) == manifest.get("manifest_sha256"), "raw_manifest_hash_mismatch")
    _require(runtime_bundle_hash(bundle) == bundle.get("artifact_sha256"), "event_bundle_hash_mismatch")
    _require(g2_manifest_hash(matrix) == matrix.get("manifest_sha256"), "execution_matrix_hash_mismatch")
    roster_preimage = copy.deepcopy(roster)
    roster_preimage.pop("report_sha256", None)
    _require(sha256_value(roster_preimage) == roster.get("report_sha256"), "roster_report_hash_mismatch")
    _require(manifest["event_bundle_id"] == bundle["runtime_bundle_id"], "event_bundle_id_mismatch")
    _require(manifest["event_bundle_sha256"] == bundle["artifact_sha256"], "event_bundle_lineage_hash_mismatch")
    _require(manifest["construction_parent"] == bundle["source_construction_bundle"], "construction_parent_mismatch")
    _require(manifest["protocol_context"] == bundle["protocol_context"], "protocol_context_mismatch")
    identity_fields = (
        "construction_state", "artifact_scope", "source_scope", "builder_access",
        "contamination_status", "protocol_eligibility",
    )
    _require(all(bundle["artifact_identity"].get(key) == bundle["protocol_context"].get(key) for key in identity_fields), "event_bundle_identity_tuple_mismatch")
    _require(all(bundle["source_construction_bundle"].get(key) == bundle["protocol_context"].get(key) for key in identity_fields), "construction_identity_tuple_mismatch")
    _require(bundle["protocol_context"]["root_construction_artifact_id"] == bundle["source_construction_bundle"]["artifact_id"], "root_construction_id_mismatch")
    rows = [row for row in matrix["execution_matrix"] if row.get("case_id") == manifest["case_id"]]
    _require(len(rows) == 1, "execution_matrix_case_cardinality")
    row = rows[0]
    _require(row["run_seed"] == manifest["run_seed"], "execution_matrix_seed_mismatch")
    profile_id = manifest["case_id"].split(".seed.", 1)[0]
    _require(row["profile_id"] == profile_id, "execution_matrix_profile_mismatch")
    _require(row["profile_event_bundle_logical_name"] == f"event_bundles/{profile_id}.json", "execution_matrix_logical_name_mismatch")
    _require(row["profile_event_bundle_sha256"] == bundle["artifact_sha256"], "execution_matrix_bundle_hash_mismatch")
    _require(matrix["roster_report_sha256"] == roster["report_sha256"], "matrix_roster_hash_mismatch")
    _require(bundle["source_kind"] == "authentic_finmycelium_draft", "source_kind_mismatch")
    _require(bundle["backend"] == "rule", "backend_not_rule")
    _require(bundle["resume_allowed"] is False, "resume_allowed")
    _require(bundle["exogenous_manifest"] == [], "historical_exogenous_input_present")
    _require(manifest["not_historically_calibrated"] is True, "historical_calibration_claim_mismatch")
    _require(
        manifest["participant_ids"]
        == sorted(item["runtime_actor_id"] for item in bundle["participant_artifacts"]),
        "participant_universe_mismatch",
    )
    roster_runtime_ids = {item["runtime_entity_id"] for item in roster["runtime_to_source"]}
    _require(set(manifest["participant_ids"]).issubset(roster_runtime_ids), "roster_runtime_actor_unresolved")


def _validate_replay_and_annotations(package: SourcePackage) -> None:
    rows = list(package.raw_records)
    manifest = package.raw_manifest
    _require(all(row.get("run_id") == manifest["run_id"] for row in rows), "raw_trace_run_id_mismatch")
    _require(package.run_seal["manifest_sha256"] == manifest["manifest_sha256"], "run_seal_manifest_mismatch")
    _require(raw_sha256(package.final_state) == package.run_seal["final_state_sha256"], "final_state_hash_mismatch")
    initial = _initial_state_from_trace(rows, manifest["participant_ids"])
    replayed = replay_raw_trace(initial, rows, _apply_raw_delta)
    _require(replayed == package.final_state, "replayed_state_content_mismatch")
    receipt = package.replay_receipt
    _require(receipt.get("status") == "pass" and receipt.get("trace_errors") == [], "replay_receipt_not_pass")
    _require(receipt.get("run_id") == manifest["run_id"], "replay_receipt_run_mismatch")
    _require(receipt.get("record_count") == len(rows), "replay_receipt_record_count_mismatch")
    _require(receipt.get("tick_count") == len(package.tick_seals), "replay_receipt_tick_count_mismatch")
    _require(receipt.get("replayed_state_sha256") == raw_sha256(replayed), "replay_receipt_state_hash_mismatch")
    generated = [row["payload"] for row in rows if row["record_type"] == "generated_annotation"]
    _require(generated == list(package.annotations), "p007_annotation_trace_mismatch")
    intent_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        if row["record_type"] == "action_intent":
            intent_counts[row["payload"]["intent_id"]] += 1
    for annotation in package.annotations:
        _require(annotation.get("provenance") == "generated_simulation_trace_only", "p007_provenance_mismatch")
        _require(all(intent_counts.get(intent_id) == 1 for intent_id in annotation["source_intent_ids"]), "p007_intent_ref_unresolved")
        _require(set(annotation["participant_ids"]).issubset(manifest["participant_ids"]), "p007_participant_ref_unresolved")
    tick_opens = [row for row in rows if row["record_type"] == "tick_open"]
    logical_clock = manifest["logical_clock"]
    _require(len(tick_opens) == logical_clock["inclusive_tick_count"], "logical_clock_tick_count_mismatch")
    _require(tick_opens[0]["payload"]["logical_date"] == logical_clock["start_date"], "logical_clock_start_mismatch")
    _require(tick_opens[-1]["payload"]["logical_date"] == logical_clock["end_date"], "logical_clock_end_mismatch")


def load_and_validate_source(inventory: LoadedInventory) -> SourcePackage:
    values = inventory.by_name()
    package = SourcePackage(
        raw_manifest=copy.deepcopy(values["g3.run_manifest"].value),
        raw_records=tuple(copy.deepcopy(values["g3.simulation_trace"].value)),
        final_state=copy.deepcopy(values["g3.final_state"].value),
        annotations=tuple(copy.deepcopy(values["g3.p007_annotations"].value)),
        tick_seals=tuple(copy.deepcopy(values["g3.tick_seals"].value)),
        run_seal=copy.deepcopy(values["g3.run_seal"].value),
        replay_receipt=copy.deepcopy(values["g3.replay_receipt"].value),
        event_bundle=copy.deepcopy(values["g2.event_bundle"].value),
        roster_report=copy.deepcopy(values["g2.roster_report"].value),
        execution_matrix=copy.deepcopy(values["g2.execution_matrix"].value),
        inventory_receipt=tuple(inventory.receipt_rows()),
    )
    validate_source_package(package)
    return package


def validate_source_package(package: SourcePackage) -> None:
    """Validate one already materialized package without changing its bytes."""
    _validate_lineage(package)
    _validate_raw_seals(package)
    _validate_replay_and_annotations(package)


def _lineage_ref(identity: Mapping[str, Any], artifact_sha256: str) -> dict[str, Any]:
    return {
        "artifact_id": identity["artifact_id"],
        "artifact_kind": identity["artifact_kind"],
        "construction_state": identity["construction_state"],
        "artifact_scope": identity["artifact_scope"],
        "source_scope": identity["source_scope"],
        "builder_access": identity["builder_access"],
        "contamination_status": identity["contamination_status"],
        "protocol_eligibility": identity["protocol_eligibility"],
        "artifact_sha256": artifact_sha256,
    }


def _artifact_identity(
    artifact_id: str,
    artifact_kind: str,
    producer_version: str,
    context: Mapping[str, Any],
    parents: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "artifact_kind": artifact_kind,
        "schema_version": "h2epr.contracts.v1",
        "producer_version": producer_version,
        "construction_state": context["construction_state"],
        "artifact_scope": context["artifact_scope"],
        "source_scope": context["source_scope"],
        "builder_access": context["builder_access"],
        "contamination_status": context["contamination_status"],
        "protocol_eligibility": context["protocol_eligibility"],
        "parent_artifacts": copy.deepcopy(parents),
        "review_state": "reviewed",
    }


def _time_interval(day: str | None, timezone: str, uncertainty: str = "") -> dict[str, Any]:
    if day is None:
        return {
            "lower": None,
            "upper": None,
            "precision": "unknown",
            "timezone": timezone,
            "uncertainty": uncertainty or "logical time unavailable",
        }
    return {
        "lower": f"{day}T00:00:00",
        "upper": f"{day}T23:59:59",
        "precision": "date",
        "timezone": timezone,
        "uncertainty": uncertainty,
    }


def _runtime_value(value: Any, raw_record: Mapping[str, Any]) -> dict[str, Any]:
    metadata = {
        "availability_at_t0": "not_applicable",
        "visibility": "runtime_system_only",
        "consumers": ["h2epr.g4.compiler"],
        "review_state": "reviewed",
    }
    provenance = {
        "source_kind": "simulation_trace",
        "source_ref_id": raw_record["trace_id"],
        "claim_ref_ids": [raw_record["trace_id"]],
        "derivation_class": "simulation_generated",
        "content_sha256": raw_record["record_hash"],
        "availability_at_t0": metadata["availability_at_t0"],
        "availability_adjudication_id": None,
        "visibility": metadata["visibility"],
        "consumers": metadata["consumers"],
        "review_state": metadata["review_state"],
    }
    return {
        "value": copy.deepcopy(value),
        "provenance": [provenance],
        **metadata,
        "visibility_scope_ids": [],
    }


def _runtime_fields(values: Mapping[str, Any], raw_record: Mapping[str, Any]) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for key in sorted(values):
        value = values[key]
        if isinstance(value, (str, int, float, bool)) or value is None:
            stored = value
            name = key
        elif isinstance(value, list) and len(value) <= 256 and all(
            isinstance(item, (str, int, float, bool)) or item is None for item in value
        ):
            stored = value
            name = key
        else:
            stored = sha256_value(value)
            name = f"{key}_sha256"
        fields.append({"field_name": name, "runtime_value": _runtime_value(stored, raw_record)})
    return fields


def _action_targets(
    payload: Mapping[str, Any], participant_ids: set[str]
) -> list[str]:
    return sorted(
        {
            value
            for key, value in payload["parameters"].items()
            if key.endswith("_id") and isinstance(value, str) and value in participant_ids
        }
    )


def _record_base(
    *,
    trace_id: str,
    trace_artifact_id: str,
    run_id: str,
    context: Mapping[str, Any],
    record_type: str,
    logical_tick: int,
    tick_phase: str,
    sequence_in_tick: int,
    simulation_time: Mapping[str, Any],
    masim_round: int | None,
    execution_level: int | None,
    actor_id: str | None,
    target_ids: list[str],
    visibility: str,
    channel: str | None,
    payload: Mapping[str, Any],
    observation_refs: list[str],
    decision_refs: list[str],
    intent_refs: list[str],
    message_refs: list[str],
    parent_trace_ids: list[str],
    causal_parent_ids: list[str],
    state_before_version: int | None,
    state_after_version: int | None,
    component_id: str,
    rule_id: str | None,
    previous_record_hash: str,
) -> dict[str, Any]:
    record = {
        "trace_id": trace_id,
        "trace_artifact_id": trace_artifact_id,
        "run_id": run_id,
        "schema_version": "h2epr.trace.record.v1",
        "protocol_context": copy.deepcopy(context),
        "record_type": record_type,
        "logical_tick": logical_tick,
        "tick_phase": tick_phase,
        "sequence_in_tick": sequence_in_tick,
        "simulation_time": copy.deepcopy(dict(simulation_time)),
        "masim_round": masim_round,
        "execution_level": execution_level,
        "first_consumable_round": None,
        "actor_id": actor_id,
        "target_ids": sorted(set(target_ids)),
        "visibility": visibility,
        "channel": channel,
        "payload": copy.deepcopy(dict(payload)),
        "observation_refs": sorted(set(observation_refs)),
        "decision_refs": sorted(set(decision_refs)),
        "intent_refs": sorted(set(intent_refs)),
        "message_refs": sorted(set(message_refs)),
        "parent_trace_ids": list(parent_trace_ids),
        "causal_parent_ids": sorted(set(causal_parent_ids)),
        "state_before_version": state_before_version,
        "state_after_version": state_after_version,
        "source_kind": "simulation",
        "component_id": component_id,
        "component_version": "h2epr.g4.wrapper.v1",
        "rule_id": rule_id,
        "rule_version": "h2epr.g4.wrapper.v1" if rule_id else None,
        "rng_draw_id": None,
        "canonicalization_version": CANONICALIZATION_VERSION,
        "record_hash_preimage": "omit_record_hash_and_operational_metadata_include_previous_record_hash",
        "previous_record_hash": previous_record_hash,
        "record_hash": "0" * 64,
    }
    record["record_hash"] = record_sha256(record)
    return record


def _build_manifest(
    package: SourcePackage,
    policy: CompilerPolicy,
    code_artifact_hashes: list[str],
) -> dict[str, Any]:
    raw = package.raw_manifest
    bundle = package.event_bundle
    context = raw["protocol_context"]
    manifest_id = stable_id("manifest", raw["run_id"], raw["manifest_sha256"])
    runtime_parent = _lineage_ref(bundle["artifact_identity"], bundle["artifact_sha256"])
    participant_hashes = sorted(sha256_value(item) for item in bundle["participant_artifacts"])
    manifest = {
        "artifact_identity": _artifact_identity(
            manifest_id, "run_manifest", policy.compiler_version, context, [runtime_parent]
        ),
        "manifest_id": manifest_id,
        "run_id": raw["run_id"],
        "scenario_id": stable_id("scenario", bundle["event_identity"]["value"], raw["case_id"]),
        "event_id": bundle["event_identity"]["value"],
        "protocol_context": copy.deepcopy(context),
        "source_kind": bundle["source_kind"],
        "runtime_bundle_sha256": bundle["artifact_sha256"],
        "config_sha256": policy.file_sha256,
        "code_artifact_hashes": sorted(set(code_artifact_hashes)),
        "contract_versions": [
            "h2epr.contracts.v1",
            "h2epr.g4.generated.epg.v1",
            "h2epr.g4.wrapper.v1",
        ],
        "time_policy": copy.deepcopy(bundle["time_policy"]),
        "participant_artifact_hashes": participant_hashes,
        "component_versions": [
            policy.compiler_version,
            policy.detector_registry_version,
            policy.grouping_policy_version,
            policy.stage_policy_version,
        ],
        "rng_streams": [{"stream_id": "g3.rule.canary", "seed": raw["run_seed"]}],
        "resume_allowed": False,
        "fresh_output_attestation": True,
        "leakage_preflight": {
            "policy_version": policy.policy_id,
            "status": "pass",
            "checks": [
                "explicit_ten_file_inventory",
                "generated_trace_only",
                "no_external_knowledge_input",
                "source_lineage_closed",
            ],
            "scanner_version": "h2epr.g4.inventory.validator.v1",
        },
        "reference_access": "denied",
        "canonicalization_version": CANONICALIZATION_VERSION,
        "manifest_hash_preimage": "omit_manifest_sha256_and_operational_metadata",
        "manifest_sha256": "0" * 64,
    }
    manifest["manifest_sha256"] = manifest_sha256(manifest)
    require_schema("run_manifest", manifest)
    return manifest


def _build_trace(package: SourcePackage, manifest: dict[str, Any]) -> dict[str, Any]:
    raw_rows = list(package.raw_records)
    context = manifest["protocol_context"]
    run_id = manifest["run_id"]
    trace_artifact_id = stable_id("trace", run_id, package.raw_manifest["manifest_sha256"])
    trace_parent = _lineage_ref(manifest["artifact_identity"], manifest["manifest_sha256"])
    dates = {
        row["logical_tick"]: row["payload"]["logical_date"]
        for row in raw_rows
        if row["record_type"] == "tick_open"
    }
    rounds = {
        row["logical_tick"]: row["payload"]["physical_masim_round"]
        for row in raw_rows
        if row["record_type"] == "tick_open"
    }
    levels = {
        row["logical_tick"]: row["payload"]["execution_level"]
        for row in raw_rows
        if row["record_type"] == "tick_open"
    }
    participant_ids = set(package.raw_manifest["participant_ids"])
    raw_trace_by_intent = {
        row["payload"]["intent_id"]: row["trace_id"]
        for row in raw_rows
        if row["record_type"] == "action_intent"
    }
    raw_disposition_by_intent = {
        row["payload"]["intent_id"]: row
        for row in raw_rows
        if row["record_type"] == "action_disposition"
    }
    raw_delta_by_intent: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in raw_rows:
        if row["record_type"] == "state_delta":
            raw_delta_by_intent[row["payload"]["source_intent_id"]].append(row)
    observations: dict[tuple[int, str], tuple[str, str]] = {}
    action_by_actor_tick: dict[tuple[int, str], dict[str, Any]] = {}
    messages_by_action: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in raw_rows:
        payload = row["payload"]
        if row["record_type"] == "observation":
            observations[(row["logical_tick"], payload["actor_id"])] = (
                row["trace_id"],
                stable_id("observation", row["trace_id"]),
            )
        elif row["record_type"] == "action_intent":
            action_by_actor_tick[(row["logical_tick"], payload["actor_id"])] = row
        elif row["record_type"] == "message_intent":
            messages_by_action[payload["source_action_intent_id"]].append(row)

    records: list[dict[str, Any]] = []
    sequence_by_tick: dict[int, int] = defaultdict(int)
    decision_trace_by_action: dict[str, str] = {}
    decision_id_by_action: dict[str, str] = {}
    wrapped_trace_by_disposition_id: dict[str, str] = {}

    def append(
        *,
        trace_id: str,
        record_type: str,
        logical_tick: int,
        tick_phase: str,
        payload: Mapping[str, Any],
        actor_id: str | None = None,
        target_ids: list[str] | None = None,
        visibility: str = "system",
        channel: str | None = None,
        observation_refs: list[str] | None = None,
        decision_refs: list[str] | None = None,
        intent_refs: list[str] | None = None,
        message_refs: list[str] | None = None,
        causal_parent_ids: list[str] | None = None,
        state_before_version: int | None = None,
        state_after_version: int | None = None,
        component_id: str = "h2epr.g4.source.adapter",
        rule_id: str | None = "h2epr.g4.wrapper.rule",
    ) -> dict[str, Any]:
        previous_hash = records[-1]["record_hash"] if records else manifest["manifest_sha256"]
        parent_ids = [records[-1]["trace_id"]] if records else []
        item = _record_base(
            trace_id=trace_id,
            trace_artifact_id=trace_artifact_id,
            run_id=run_id,
            context=context,
            record_type=record_type,
            logical_tick=logical_tick,
            tick_phase=tick_phase,
            sequence_in_tick=sequence_by_tick[logical_tick],
            simulation_time=_time_interval(dates.get(logical_tick), package.event_bundle["time_policy"]["timezone"]),
            masim_round=rounds.get(logical_tick),
            execution_level=levels.get(logical_tick),
            actor_id=actor_id,
            target_ids=target_ids or [],
            visibility=visibility,
            channel=channel,
            payload=payload,
            observation_refs=observation_refs or [],
            decision_refs=decision_refs or [],
            intent_refs=intent_refs or [],
            message_refs=message_refs or [],
            parent_trace_ids=parent_ids,
            causal_parent_ids=causal_parent_ids or parent_ids,
            state_before_version=state_before_version,
            state_after_version=state_after_version,
            component_id=component_id,
            rule_id=rule_id,
            previous_record_hash=previous_hash,
        )
        records.append(item)
        sequence_by_tick[logical_tick] += 1
        return item

    def append_decision(raw_action: Mapping[str, Any]) -> None:
        action = raw_action["payload"]
        tick = raw_action["logical_tick"]
        actor = action["actor_id"]
        observation_trace, observation_id = observations[(tick, actor)]
        decision_id = stable_id("decision", run_id, tick, actor)
        decision_trace_id = stable_id("decision.trace", run_id, tick, actor)
        messages = messages_by_action[action["intent_id"]]
        payload = {
            "decision_id": decision_id,
            "run_id": run_id,
            "logical_tick": tick,
            "actor_id": actor,
            "observation_refs": [observation_id],
            "rule_ids": [action["policy_id"]],
            "action_intent_ids": [action["intent_id"]],
            "message_intent_ids": sorted(item["payload"]["message_intent_id"] for item in messages),
            "structured_reason_codes": ["rule_policy_selected_recorded_intents"],
            "decision_schema_version": "h2epr.g4.derived.decision.v1",
        }
        append(
            trace_id=decision_trace_id,
            record_type="decision_recorded",
            logical_tick=tick,
            tick_phase="decide",
            payload=payload,
            actor_id=actor,
            visibility="actor_private",
            observation_refs=[observation_id],
            decision_refs=[decision_id],
            intent_refs=[action["intent_id"]] + [item["payload"]["message_intent_id"] for item in messages],
            causal_parent_ids=[observation_trace],
            state_before_version=action["prestate_version"],
            state_after_version=action["prestate_version"],
            component_id="h2epr.g4.decision.materializer",
            rule_id="h2epr.g4.decision.from_recorded_intents",
        )
        decision_trace_by_action[action["intent_id"]] = decision_trace_id
        decision_id_by_action[action["intent_id"]] = decision_id

    for raw in raw_rows:
        raw_type = raw["record_type"]
        tick = raw["logical_tick"]
        payload = raw["payload"]
        if raw_type == "run_seal":
            continue
        if raw_type == "action_intent":
            append_decision(raw)
        if raw_type == "tick_seal":
            prior_tick = [item for item in records if item["logical_tick"] == tick]
            first_observation = next(
                item for item in raw_rows if item["logical_tick"] == tick and item["record_type"] == "observation"
            )
            seal_payload = {
                "seal_type": "tick",
                "logical_tick": tick,
                "manifest_sha256": manifest["manifest_sha256"],
                "first_record_hash": prior_tick[0]["record_hash"],
                "last_record_hash_before_seal": prior_tick[-1]["record_hash"],
                "record_count_before_seal": len(prior_tick),
                "state_before_version": first_observation["payload"]["prestate_version"],
                "state_after_version": tick,
                "state_before_sha256": first_observation["payload"]["prestate_sha256"],
                "state_after_sha256": payload["state_sha256"],
                "closure_check_version": "h2epr.g4.tick.closure.v1",
                "closure_result": "pass",
                "tick_validity": "valid",
                "canonicalization_version": CANONICALIZATION_VERSION,
            }
            append(
                trace_id=raw["trace_id"], record_type="tick_sealed", logical_tick=tick,
                tick_phase="seal", payload=seal_payload,
                causal_parent_ids=[prior_tick[-1]["trace_id"]],
                state_before_version=seal_payload["state_before_version"],
                state_after_version=seal_payload["state_after_version"],
                component_id="h2epr.g4.trace.sealer", rule_id="h2epr.g4.tick.seal",
            )
            continue
        if raw_type == "tick_open":
            event = {"event_id": stable_id("tick.open", run_id, tick), "event_type": "tick_opened", "fields": _runtime_fields(payload, raw), "reason_codes": ["source_tick_open"]}
            append(trace_id=raw["trace_id"], record_type="tick_opened", logical_tick=tick, tick_phase="open", payload=event, state_before_version=tick - 1, state_after_version=tick - 1)
        elif raw_type == "observation":
            observation_id = observations[(tick, payload["actor_id"])][1]
            obs = {"observation_id": observation_id, "fields": _runtime_fields(payload, raw)}
            append(trace_id=raw["trace_id"], record_type="observation_delivered", logical_tick=tick, tick_phase="observe", payload=obs, actor_id=payload["actor_id"], visibility="actor_private", observation_refs=[observation_id], state_before_version=payload["prestate_version"], state_after_version=payload["prestate_version"])
        elif raw_type == "action_intent":
            observation_trace, observation_id = observations[(tick, payload["actor_id"])]
            decision_id = decision_id_by_action[payload["intent_id"]]
            action = {
                "intent_id": payload["intent_id"], "run_id": run_id, "logical_tick": tick,
                "actor_id": payload["actor_id"], "action_type": payload["action_type"],
                "action_schema_version": "h2epr.g3.action.intent.v1",
                "target_entity_ids": _action_targets(payload, participant_ids),
                "parameters": _runtime_fields(payload["parameters"], raw),
                "claimed_authority_refs": [], "resource_offer_or_request": [],
                "earliest_effect_time": _time_interval(dates[tick], package.event_bundle["time_policy"]["timezone"]),
                "expiry_time": None, "observation_refs": [observation_id], "decision_ref": decision_id,
                "idempotency_key": payload["intent_id"], "visibility": "public",
            }
            append(trace_id=raw["trace_id"], record_type="action_intent_created", logical_tick=tick, tick_phase="decide", payload=action, actor_id=payload["actor_id"], target_ids=_action_targets(payload, participant_ids), visibility="public", observation_refs=[observation_id], decision_refs=[decision_id], intent_refs=[payload["intent_id"]], causal_parent_ids=[decision_trace_by_action[payload["intent_id"]]], state_before_version=payload["prestate_version"], state_after_version=payload["prestate_version"], component_id="h2epr.g3.rule.policy", rule_id=payload["policy_id"])
        elif raw_type == "action_disposition":
            source_trace = raw_trace_by_intent[payload["intent_id"]]
            delta_rows = raw_delta_by_intent[payload["intent_id"]]
            raw_action = next(item for item in raw_rows if item["record_type"] == "action_intent" and item["payload"]["intent_id"] == payload["intent_id"])
            accepted_parameters = _runtime_fields(raw_action["payload"]["parameters"], raw_action)
            disposition = {
                "disposition_id": payload["disposition_id"], "intent_id": payload["intent_id"],
                "reducer_id": "h2epr.g3.authoritative.reducer", "reducer_version": "h2epr.g3.reducer.v1",
                "status": payload["status"], "reason_codes": [payload["reason_code"]],
                "accepted_parameters": accepted_parameters, "rejected_parameters": [], "conflict_set_ids": [],
                "state_before_version": tick - 1, "state_after_version": tick,
                "delta_ids": sorted(item["payload"]["delta_id"] for item in delta_rows),
                "explicit_no_effect": not delta_rows, "retry_policy": "none",
            }
            wrapped = append(trace_id=raw["trace_id"], record_type="action_disposition_recorded", logical_tick=tick, tick_phase="reduce", payload=disposition, actor_id=raw_action["payload"]["actor_id"], target_ids=_action_targets(raw_action["payload"], participant_ids), visibility="system", decision_refs=[decision_id_by_action[payload["intent_id"]]], intent_refs=[payload["intent_id"]], causal_parent_ids=[source_trace], state_before_version=tick - 1, state_after_version=tick, component_id="h2epr.g3.authoritative.reducer", rule_id="h2epr.g3.reducer.adjudication")
            wrapped_trace_by_disposition_id[payload["disposition_id"]] = wrapped["trace_id"]
        elif raw_type == "state_delta":
            intent_id = payload["source_intent_id"]
            disposition_row = raw_disposition_by_intent[intent_id]
            before, after = payload["before"], payload["after"]
            operation = "increment" if after > before else "decrement" if after < before else "set"
            delta = {
                "delta_id": payload["delta_id"], "disposition_id": disposition_row["payload"]["disposition_id"],
                "entity_id": "world" if payload["entity_id"] == "__world__" else payload["entity_id"],
                "state_path": payload["field_name"], "operation": operation, "before": before, "after": after,
                "unit": "basis_points", "state_before_version": tick - 1, "state_after_version": tick,
                "invariant_checks": ["basis_points_domain"], "causal_parent_ids": [intent_id],
            }
            append(trace_id=raw["trace_id"], record_type="state_transition_applied", logical_tick=tick, tick_phase="reduce", payload=delta, target_ids=[delta["entity_id"]], visibility="system", intent_refs=[intent_id], causal_parent_ids=[wrapped_trace_by_disposition_id[delta["disposition_id"]]], state_before_version=tick - 1, state_after_version=tick, component_id="h2epr.g3.authoritative.reducer", rule_id=f"h2epr.g3.delta.{payload['delta_class']}")
        elif raw_type == "message_intent":
            source_intent = payload["source_action_intent_id"]
            created = date.fromisoformat(dates[tick])
            due = created + timedelta(days=payload["latency_ticks"])
            message = {
                "message_intent_id": payload["message_intent_id"], "run_id": run_id, "logical_tick": tick,
                "sender_id": payload["sender_id"], "recipient_ids": [payload["recipient_id"]],
                "performative": payload["message_kind"], "content_schema_version": "h2epr.g3.message.content.v1",
                "structured_content": _runtime_fields(payload["payload"], raw), "channel": payload["route_id"],
                "confidentiality": "restricted",
                "created_at": _time_interval(created.isoformat(), package.event_bundle["time_policy"]["timezone"]),
                "earliest_delivery_time": _time_interval(due.isoformat(), package.event_bundle["time_policy"]["timezone"]),
                "expiry_time": None, "decision_ref": decision_id_by_action[source_intent],
                "idempotency_key": payload["message_intent_id"], "correlation_ids": [source_intent],
            }
            append(trace_id=raw["trace_id"], record_type="message_intent_created", logical_tick=tick, tick_phase="communicate", payload=message, actor_id=payload["sender_id"], target_ids=[payload["recipient_id"]], visibility="restricted", channel=payload["route_id"], decision_refs=[decision_id_by_action[source_intent]], intent_refs=[source_intent, payload["message_intent_id"]], causal_parent_ids=[raw_trace_by_intent[source_intent]], state_before_version=tick - 1, state_after_version=tick - 1, component_id="h2epr.g3.transport", rule_id="h2epr.g3.message.intent")
        elif raw_type == "message_disposition":
            event = {"event_id": payload["disposition_id"], "event_type": f"message_{payload['status']}", "fields": _runtime_fields(payload, raw), "reason_codes": [payload["reason_code"]]}
            message_intent_trace = next(item["trace_id"] for item in raw_rows if item["record_type"] == "message_intent" and item["payload"]["message_intent_id"] == payload["message_intent_id"])
            causal = [message_intent_trace]
            if payload["predecessor_disposition_id"]:
                predecessor = next(item["trace_id"] for item in raw_rows if item["record_type"] == "message_disposition" and item["payload"]["disposition_id"] == payload["predecessor_disposition_id"])
                causal.append(predecessor)
            append(trace_id=raw["trace_id"], record_type="local_outcome_detected", logical_tick=tick, tick_phase="communicate", payload=event, actor_id=payload["sender_id"], target_ids=[payload["recipient_id"]], visibility="restricted", intent_refs=[payload["message_intent_id"]], causal_parent_ids=causal, component_id="h2epr.g3.transport", rule_id="h2epr.g4.transport.disposition.event")
        elif raw_type == "tick_commit":
            event = {"event_id": stable_id("tick.commit", run_id, tick), "event_type": "tick_commit", "fields": _runtime_fields(payload, raw), "reason_codes": ["authoritative_state_committed"]}
            delta_refs = [item["trace_id"] for item in raw_rows if item["logical_tick"] == tick and item["record_type"] == "state_delta"]
            append(trace_id=raw["trace_id"], record_type="local_outcome_detected", logical_tick=tick, tick_phase="commit", payload=event, causal_parent_ids=delta_refs or [records[-1]["trace_id"]], state_before_version=tick - 1, state_after_version=tick, component_id="h2epr.g3.authoritative.reducer", rule_id="h2epr.g3.tick.commit")
        elif raw_type == "generated_annotation":
            event = {"event_id": stable_id("annotation", raw["trace_id"]), "event_type": payload["annotation_type"], "fields": _runtime_fields(payload, raw), "reason_codes": ["generated_trace_detector"]}
            causal = [raw_trace_by_intent[intent_id] for intent_id in payload["source_intent_ids"]]
            append(trace_id=raw["trace_id"], record_type="local_outcome_detected", logical_tick=tick, tick_phase="detect", payload=event, target_ids=payload["participant_ids"], visibility="public", intent_refs=payload["source_intent_ids"], causal_parent_ids=causal or [records[-1]["trace_id"]], state_before_version=tick, state_after_version=tick, component_id="h2epr.g3.p007.detector", rule_id="h2epr.g4.generated.annotation")
        elif raw_type == "generated_stage_first_hit":
            same_tick_annotations = [item["trace_id"] for item in raw_rows if item["logical_tick"] == tick and item["record_type"] == "generated_annotation"]
            event = {"event_id": stable_id("stage.hit", raw["trace_id"]), "event_type": payload["stage"], "fields": _runtime_fields(payload, raw), "reason_codes": ["generated_first_hit"]}
            append(trace_id=raw["trace_id"], record_type="phase_transition_detected", logical_tick=tick, tick_phase="detect", payload=event, visibility="public", causal_parent_ids=same_tick_annotations or [records[-1]["trace_id"]], state_before_version=tick, state_after_version=tick, component_id="h2epr.g3.p007.detector", rule_id="h2epr.g4.stage.first.hit")
        else:
            raise SourcePackageError(f"unsupported_raw_record_type:{raw_type}")

    last_tick = max(dates)
    prefix = list(records)
    tick_seal_hashes = [item["record_hash"] for item in prefix if item["record_type"] == "tick_sealed"]
    run_payload = {
        "seal_type": "run", "run_id": run_id, "manifest_sha256": manifest["manifest_sha256"],
        "trace_prefix_sha256": trace_sha256(prefix), "record_count_before_run_seal": len(prefix),
        "first_record_hash": prefix[0]["record_hash"], "last_record_hash_before_run_seal": prefix[-1]["record_hash"],
        "tick_seal_record_hashes": tick_seal_hashes,
        "terminal_state_version": package.final_state["state_version"],
        "terminal_state_sha256": sha256_value(package.final_state),
        "closure_check_version": "h2epr.g4.run.closure.v1", "closure_result": "pass",
        "run_validity": "valid", "canonicalization_version": CANONICALIZATION_VERSION,
    }
    append(trace_id=next(row["trace_id"] for row in raw_rows if row["record_type"] == "run_seal"), record_type="run_sealed", logical_tick=last_tick, tick_phase="seal", payload=run_payload, causal_parent_ids=[item["trace_id"] for item in prefix if item["record_type"] == "tick_sealed"], state_before_version=package.final_state["state_version"], state_after_version=package.final_state["state_version"], component_id="h2epr.g4.trace.sealer", rule_id="h2epr.g4.run.seal")

    trace = {
        "artifact_identity": _artifact_identity(trace_artifact_id, "simulation_trace", "h2epr.g4.wrapper.v1", context, [trace_parent]),
        "protocol_context": copy.deepcopy(context), "trace_artifact_id": trace_artifact_id,
        "run_id": run_id, "source_manifest_sha256": manifest["manifest_sha256"],
        "trace_usage_class": "compiler_evaluator_eligible", "records": records,
        "trace_hash_preimage": "canonical_record_array_including_run_seal_omit_each_record_operational_metadata",
        "canonicalization_version": CANONICALIZATION_VERSION, "trace_sha256": trace_sha256(records),
    }
    require_schema("simulation_trace", trace)
    validate_v1_trace(trace)
    return trace


def validate_v1_trace(trace: Mapping[str, Any]) -> None:
    records = list(trace["records"])
    _require(records and records[-1]["record_type"] == "run_sealed", "v1_run_seal_not_final")
    ids = [item["trace_id"] for item in records]
    _require(len(ids) == len(set(ids)), "v1_duplicate_trace_id")
    positions = {trace_id: index for index, trace_id in enumerate(ids)}
    previous = trace["source_manifest_sha256"]
    tick_groups: dict[int, list[dict[str, Any]]] = defaultdict(list)
    known_observations: set[str] = set()
    known_decisions: set[str] = set()
    known_intents: set[str] = set()
    for index, record in enumerate(records):
        _require(record["previous_record_hash"] == previous, "v1_previous_record_hash_mismatch")
        _require(record["record_hash"] == record_sha256(record), "v1_record_hash_mismatch")
        previous = record["record_hash"]
        for ref in record["parent_trace_ids"] + record["causal_parent_ids"]:
            _require(ref in positions and positions[ref] < index, "v1_trace_ref_not_unique_earlier")
        if record["record_type"] == "observation_delivered":
            known_observations.add(record["payload"]["observation_id"])
        elif record["record_type"] == "decision_recorded":
            _require(set(record["payload"]["observation_refs"]).issubset(known_observations), "v1_decision_observation_unresolved")
            known_decisions.add(record["payload"]["decision_id"])
        elif record["record_type"] == "action_intent_created":
            _require(record["payload"]["decision_ref"] in known_decisions, "v1_action_decision_unresolved")
            known_intents.add(record["payload"]["intent_id"])
        elif record["record_type"] == "message_intent_created":
            _require(record["payload"]["decision_ref"] in known_decisions, "v1_message_decision_unresolved")
            _require(set(record["payload"]["correlation_ids"]).issubset(known_intents), "v1_message_action_unresolved")
            known_intents.add(record["payload"]["message_intent_id"])
        if record["record_type"] != "run_sealed":
            tick_groups[record["logical_tick"]].append(record)
    _require(trace["trace_sha256"] == trace_sha256(records), "v1_trace_hash_mismatch")
    _require(sorted(tick_groups) == list(range(min(tick_groups), max(tick_groups) + 1)), "v1_tick_gap")
    for tick, group in sorted(tick_groups.items()):
        _require([item["sequence_in_tick"] for item in group] == list(range(len(group))), "v1_tick_sequence_mismatch")
        seals = [item for item in group if item["record_type"] == "tick_sealed"]
        _require(len(seals) == 1 and group[-1] is seals[0], "v1_tick_seal_not_unique_terminal")
        before = group[:-1]
        payload = seals[0]["payload"]
        _require(payload["first_record_hash"] == before[0]["record_hash"], "v1_tick_first_hash_mismatch")
        _require(payload["last_record_hash_before_seal"] == before[-1]["record_hash"], "v1_tick_last_hash_mismatch")
        _require(payload["record_count_before_seal"] == len(before), "v1_tick_record_count_mismatch")
    run_record = records[-1]
    prefix = records[:-1]
    payload = run_record["payload"]
    _require(run_record["logical_tick"] == max(tick_groups), "v1_run_seal_tick_mismatch")
    _require(run_record["sequence_in_tick"] == max(item["sequence_in_tick"] for item in tick_groups[max(tick_groups)]) + 1, "v1_run_seal_sequence_mismatch")
    _require(payload["trace_prefix_sha256"] == trace_sha256(prefix), "v1_run_prefix_hash_mismatch")
    _require(payload["record_count_before_run_seal"] == len(prefix), "v1_run_record_count_mismatch")
    _require(payload["tick_seal_record_hashes"] == [item["record_hash"] for item in prefix if item["record_type"] == "tick_sealed"], "v1_run_tick_set_mismatch")


def build_v1_wrappers(
    package: SourcePackage,
    policy: CompilerPolicy,
    code_artifact_hashes: list[str],
) -> V1Wrappers:
    manifest = _build_manifest(package, policy, code_artifact_hashes)
    trace = _build_trace(package, manifest)
    return V1Wrappers(manifest, trace)
