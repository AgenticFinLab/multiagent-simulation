"""Independent verification primitives for compact run releases."""

from __future__ import annotations

import copy
import json
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping, Sequence

import jsonschema

from h2epr.benchmark.package import EventPackage
from h2epr.canonical import canonical_sha256, file_sha256
from h2epr.conformance import (
    ConformanceError,
    read_jsonl,
)
from h2epr.masim_kernel import (
    ActionIntent,
    AuthoritativeReducer,
    MessageIntent,
    replay_trace,
    source_inventory as masim_source_inventory,
    validate_trace,
)
from h2epr.runtime.benchmark_runner import (
    OUTPUT_ROLES,
    build_run_manifest,
    h2epr_runtime_source_inventory,
    materialize_run,
)
from h2epr.runtime.environment import apply_delta, build_environment
from h2epr.runtime.information import message_contract_error
from h2epr.runtime._environment_core import condition_matches
from h2epr.runtime.generated_epg import (
    GeneratedEPGError,
    compile_generated_epg,
    validate_generated_epg,
)


class _PublicationCoreError(ValueError):
    """Custody or release material does not satisfy publication invariants."""


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_ROOT = PROJECT_ROOT / "schemas"
_TRACE_RECORD_TYPES = {
    "action_disposition",
    "action_intent",
    "generated_annotation",
    "message_disposition",
    "message_intent",
    "observation",
    "participant_decision",
    "run_seal",
    "stage_entry",
    "state_delta",
    "tick_commit",
    "tick_open",
    "tick_seal",
}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _PublicationCoreError(f"json_unreadable:{path}") from exc
    if not isinstance(value, dict):
        raise _PublicationCoreError(f"json_object_required:{path}")
    return value


def _read_json_value(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _PublicationCoreError(f"{label}_unreadable") from exc


def _validate(value: Mapping[str, Any], schema_name: str, label: str) -> None:
    schema = _read_json(SCHEMA_ROOT / schema_name)
    try:
        jsonschema.Draft202012Validator(schema).validate(value)
    except jsonschema.ValidationError as exc:
        raise _PublicationCoreError(
            f"{label}_schema_invalid:{exc.json_path}"
        ) from exc


def _validate_schema(
    value: Mapping[str, Any], schema_name: str, label: str
) -> None:
    schema = _read_json(SCHEMA_ROOT / schema_name)
    try:
        jsonschema.Draft202012Validator(schema).validate(value)
    except jsonschema.ValidationError as exc:
        raise _PublicationCoreError(
            f"{label}_schema_invalid:{exc.json_path}"
        ) from exc


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise _PublicationCoreError(code)


def _self_hash_matches(value: Mapping[str, Any], field: str) -> bool:
    return value[field] == canonical_sha256(
        {key: item for key, item in value.items() if key != field}
    )


def _safe_custody_file(root: Path, relative_path: str) -> Path:
    _require(root.is_dir() and not root.is_symlink(), "run_custody_root_unsafe")
    relative = Path(relative_path)
    _require(
        not relative.is_absolute() and ".." not in relative.parts,
        f"run_output_path_unsafe:{relative_path}",
    )
    path = root / relative
    _require(
        path.is_file() and not path.is_symlink(),
        f"run_output_missing_or_unsafe:{relative_path}",
    )
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise _PublicationCoreError(
            f"run_output_escapes_custody:{relative_path}"
        ) from exc
    return path


def _validate_custody_locator(value: Any) -> None:
    _require(isinstance(value, str), "run_custody_locator_invalid")
    relative = Path(value)
    allowed = set(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-/"
    )
    _require(
        not relative.is_absolute()
        and ".." not in relative.parts
        and len(relative.parts) > 3
        and relative.parts[:3]
        == (".local-runtime", "h2epr-simulation", "runs")
        and set(value) <= allowed
        and relative.as_posix() == value,
        "run_custody_locator_invalid",
    )


def _derive_coordinate_results(
    trace: Sequence[Mapping[str, Any]],
    package: EventPackage,
) -> list[dict[str, Any]]:
    actor_ids = sorted(package.scenario["active_actor_ids"])
    results: list[dict[str, Any]] = []
    try:
        for coordinate in package.scenario["timeline"]:
            logical_tick = coordinate["logical_tick"]
            rows = [row for row in trace if row["logical_tick"] == logical_tick]
            by_type = {
                record_type: [
                    row for row in rows if row["record_type"] == record_type
                ]
                for record_type in _TRACE_RECORD_TYPES
            }
            _require(
                len(by_type["tick_open"]) == 1
                and len(by_type["tick_commit"]) == 1
                and len(by_type["tick_seal"]) == 1,
                f"run_coordinate_control_cardinality_mismatch:{logical_tick}",
            )
            _require(
                by_type["tick_open"][0]["payload"]["coordinate"]
                == coordinate,
                f"run_coordinate_identity_mismatch:{logical_tick}",
            )
            observations = by_type["observation"]
            decisions = by_type["participant_decision"]
            actions = by_type["action_intent"]
            _require(
                sorted(row["payload"]["contract"]["actor_id"] for row in observations)
                == actor_ids
                and sorted(row["payload"]["actor_id"] for row in decisions)
                == actor_ids
                and sorted(row["payload"]["actor_id"] for row in actions)
                == actor_ids,
                f"run_coordinate_actor_universe_mismatch:{logical_tick}",
            )
            commit = by_type["tick_commit"][0]["payload"]
            tick_seal = by_type["tick_seal"][0]["payload"]
            _require(
                commit["coordinate_id"] == coordinate["coordinate_id"],
                f"run_coordinate_commit_identity_mismatch:{logical_tick}",
            )
            results.append(
                {
                    "logical_tick": logical_tick,
                    "coordinate_id": coordinate["coordinate_id"],
                    "stage_id": coordinate["stage_id"],
                    "episode_id": coordinate["episode_id"],
                    "action_intent_count": len(actions),
                    "message_intent_count": len(by_type["message_intent"]),
                    "delivered_message_count": sum(
                        len(row["payload"]["contract"]["delivered_messages"])
                        for row in observations
                    ),
                    "state_delta_count": len(by_type["state_delta"]),
                    "annotation_count": len(by_type["generated_annotation"]),
                    "poststate_sha256": commit["state_sha256"],
                    "tick_seal_sha256": tick_seal["seal_sha256"],
                }
            )
    except (KeyError, TypeError) as exc:
        raise _PublicationCoreError("run_coordinate_trace_shape_invalid") from exc
    return results


def _derive_run_counts(
    trace: Sequence[Mapping[str, Any]],
    package: EventPackage,
    graph: Mapping[str, Any],
) -> dict[str, int]:
    counts = {
        "trace_records": len(trace),
        "ticks": len(package.scenario["timeline"]),
        "actors": len(package.scenario["active_actor_ids"]),
        "graph_nodes": len(graph["nodes"]),
        "graph_edges": len(graph["edges"]),
    }
    try:
        for row in trace:
            record_type = row["record_type"]
            _require(
                record_type in _TRACE_RECORD_TYPES,
                f"run_trace_record_type_unknown:{record_type}",
            )
            record_key = f"record.{record_type}"
            counts[record_key] = counts.get(record_key, 0) + 1
            if record_type == "action_intent":
                action_key = f"action.{row['payload']['action_type']}"
                counts[action_key] = counts.get(action_key, 0) + 1
    except (KeyError, TypeError) as exc:
        raise _PublicationCoreError("run_count_trace_shape_invalid") from exc
    return dict(sorted(counts.items()))


def _verify_trace_semantics(
    trace: Sequence[Mapping[str, Any]],
    package: EventPackage,
    manifest: Mapping[str, Any],
) -> None:
    """Rederive decision lineage instead of trusting a sealed producer trace."""

    expected_actors = sorted(package.scenario["active_actor_ids"])
    expected_policy = package.backend_configuration["settings"]["policy_id"]
    action_intents: dict[str, Mapping[str, Any]] = {}
    message_intents: dict[str, Mapping[str, Any]] = {}
    message_disposition_ids: set[str] = set()
    memory = {actor: {"received_messages": [], "own_actions": []}
              for actor in expected_actors}
    latest_transport: dict[str, Mapping[str, Any]] = {}
    prestate = copy.deepcopy(package.scenario["initial_state"])
    environment = build_environment(package.scenario)
    verifier_reducer = AuthoritativeReducer(prestate, environment.apply_batch)

    try:
        for coordinate in package.scenario["timeline"]:
            logical_tick = coordinate["logical_tick"]
            rows = [row for row in trace if row["logical_tick"] == logical_tick]
            observations = [
                row["payload"] for row in rows if row["record_type"] == "observation"
            ]
            decisions = [
                row["payload"]
                for row in rows
                if row["record_type"] == "participant_decision"
            ]
            actions = [
                row["payload"]
                for row in rows
                if row["record_type"] == "action_intent"
            ]
            messages = [
                row["payload"]
                for row in rows
                if row["record_type"] == "message_intent"
            ]
            dispositions = [
                row["payload"]
                for row in rows
                if row["record_type"] == "action_disposition"
            ]
            deltas = [
                row["payload"]
                for row in rows
                if row["record_type"] == "state_delta"
            ]
            delivered: dict[str, list[dict[str, Any]]] = {actor: [] for actor in expected_actors}
            for row in rows:
                if row["record_type"] != "message_disposition" or row["payload"]["status"] != "delivered":
                    continue
                disposition = row["payload"]
                message_id = disposition["message_intent_id"]
                _require(message_id in message_intents, "run_delivery_precedes_submission")
                source = message_intents[message_id]
                due = source["logical_tick"] + source["latency_ticks"]
                _require(logical_tick >= due, "run_delivery_precedes_availability")
                latest_transport[message_id] = disposition
                delivered[source["recipient_id"]].append({
                    "sender_id": source["sender_id"], "recipient_id": source["recipient_id"],
                    "send_tick": source["logical_tick"], "earliest_delivery_tick": due,
                    "due_tick": due, "first_consumable_tick": logical_tick,
                    "message_kind": source["message_kind"], "payload": source["payload"],
                })
            for actor_id in expected_actors:
                delivered[actor_id].sort(key=canonical_sha256)
                memory[actor_id]["received_messages"].extend(delivered[actor_id])

            observation_by_actor = {
                row["contract"]["actor_id"]: row for row in observations
            }
            decision_by_actor = {row["actor_id"]: row for row in decisions}
            action_by_actor = {row["actor_id"]: row for row in actions}
            _require(
                len(observation_by_actor) == len(observations)
                and len(decision_by_actor) == len(decisions)
                and len(action_by_actor) == len(actions)
                and sorted(observation_by_actor) == expected_actors
                and sorted(decision_by_actor) == expected_actors
                and sorted(action_by_actor) == expected_actors,
                f"run_decision_actor_closure_mismatch:{logical_tick}",
            )

            messages_by_action: dict[str, list[Mapping[str, Any]]] = {}
            for message in messages:
                try:
                    message_intent = MessageIntent(**message)
                except (TypeError, ValueError) as exc:
                    raise _PublicationCoreError(
                        f"run_message_intent_invalid:{logical_tick}"
                    ) from exc
                error = message_contract_error(message_intent, package.scenario["mechanism"])
                _require(error is None, f"run_message_contract_invalid:{error}")
                message_id = message["message_intent_id"]
                _require(
                    message_id not in message_intents,
                    f"run_message_intent_duplicate:{message_id}",
                )
                message_intents[message_id] = message
                messages_by_action.setdefault(
                    message["source_action_intent_id"], []
                ).append(message)

            for actor_id in expected_actors:
                observation = observation_by_actor[actor_id]
                decision = decision_by_actor[actor_id]
                action = action_by_actor[actor_id]
                contract = observation["contract"]
                runtime = observation["runtime"]
                _validate_schema(
                    contract,
                    "participant-observation.schema.json",
                    f"run_observation:{logical_tick}:{actor_id}",
                )
                _validate_schema(
                    decision,
                    "participant-decision.schema.json",
                    f"run_decision:{logical_tick}:{actor_id}",
                )
                _require(contract["delivered_messages"] == delivered[actor_id]
                         and contract["memory"] == memory[actor_id],
                         f"run_observation_memory_not_trace_derived:{logical_tick}:{actor_id}")
                expected_pending = sorted([
                    {"lifecycle_id": "message_delivery", "status": item["status"],
                     "counterparty_id": item["recipient_id"]}
                    for item in latest_transport.values()
                    if item["sender_id"] == actor_id and item["status"] not in {
                        "delivered", "expired", "rejected", "duplicate", "failed"
                    }
                ], key=canonical_sha256)
                _require(contract["pending_lifecycles"] == expected_pending,
                         f"run_pending_lifecycle_projection_mismatch:{logical_tick}:{actor_id}")
                for visibility, key in (("public", "public_state"), ("actor_private", "private_state")):
                    entities: dict[str, dict[str, Any]] = {}
                    for field in package.scenario["mechanism"]["state_fields"]:
                        if field["visibility"] != visibility or (
                            visibility == "actor_private" and field["entity_id"] != actor_id
                        ):
                            continue
                        entities.setdefault(field["entity_id"], {})[field["field_name"]] = (
                            prestate["entities"][field["entity_id"]][field["field_name"]]
                        )
                    _require(contract[key] == {"state_version": prestate["state_version"],
                                               "entities": entities},
                             f"run_state_visibility_projection_mismatch:{logical_tick}:{actor_id}")
                try:
                    ActionIntent(**action)
                except (TypeError, ValueError) as exc:
                    raise _PublicationCoreError(
                        f"run_action_intent_invalid:{logical_tick}:{actor_id}"
                    ) from exc
                _require(
                    contract["logical_tick"] == logical_tick
                    and decision["logical_tick"] == logical_tick
                    and action["logical_tick"] == logical_tick
                    and runtime["coordinate"] == {
                        "coordinate_id": coordinate["coordinate_id"],
                        "logical_tick": logical_tick,
                    }
                    and runtime["prestate_version"] == action["prestate_version"]
                    and runtime["prestate_sha256"] == action["prestate_sha256"]
                    and action["run_id"] == manifest["run_id"]
                    and decision["backend"] == manifest["backend"] == "rule",
                    f"run_decision_coordinate_mismatch:{logical_tick}:{actor_id}",
                )
                _require(
                    decision["action"]["action_type"] == action["action_type"]
                    and decision["action"]["parameters"] == action["parameters"],
                    f"run_decision_action_mismatch:{logical_tick}:{actor_id}",
                )
                _require(
                    action["action_type"]
                    in package.scenario["action_spaces"][actor_id]
                    and action["action_type"]
                    in contract["permitted_action_types"],
                    f"run_action_not_permitted:{logical_tick}:{actor_id}",
                )
                _require(
                    action["policy_id"] == expected_policy
                    and decision["decision_record"].get("policy_id")
                    == expected_policy,
                    f"run_decision_policy_mismatch:{logical_tick}:{actor_id}",
                )
                intent_id = action["intent_id"]
                _require(
                    intent_id not in action_intents,
                    f"run_action_intent_duplicate:{intent_id}",
                )
                action_intents[intent_id] = action
                expected_messages = [
                    {
                        "recipient_id": row["recipient_id"],
                        "message_type": row["message_kind"],
                        "payload": row["payload"],
                    }
                    for row in messages_by_action.get(intent_id, [])
                ]
                _require(
                    decision["messages"] == expected_messages,
                    f"run_decision_message_mismatch:{logical_tick}:{actor_id}",
                )
                record = decision["decision_record"]
                _require(record.get("reason_kind") == "configured_policy_rationale"
                         and record.get("observation_sha256") == canonical_sha256(contract),
                         f"run_decision_evidence_identity_mismatch:{logical_tick}:{actor_id}")

            # Reconstruct common admission from verified projections, not from
            # the backend's rationale or the producer's accepted flag.
            environment.bind_observations(observation_by_actor)
            expected = verifier_reducer.reduce(
                [ActionIntent(**action) for action in actions],
                logical_tick=logical_tick, run_seed=0,
            )
            expected_dispositions = {item.intent_id: item.to_dict() for item in expected.dispositions}
            for disposition in dispositions:
                derived = expected_dispositions.get(disposition["intent_id"])
                _require(derived is not None and all(canonical_sha256(disposition.get(key)) == canonical_sha256(value)
                                                     for key, value in derived.items()),
                         f"run_shared_admission_not_reproduced:{logical_tick}")
            _require({item.delta_id: item.to_dict() for item in expected.deltas}
                     == {item["delta_id"]: item for item in deltas},
                     f"run_environment_effects_not_reproduced:{logical_tick}")

            disposition_by_intent = {
                row["intent_id"]: row for row in dispositions
            }
            delta_by_id = {row["delta_id"]: row for row in deltas}
            _require(
                len(disposition_by_intent) == len(dispositions)
                and set(disposition_by_intent) == {
                    row["intent_id"] for row in actions
                }
                and len(delta_by_id) == len(deltas),
                f"run_disposition_delta_closure_mismatch:{logical_tick}",
            )
            for intent_id, disposition in disposition_by_intent.items():
                action = action_intents[intent_id]
                _require(
                    disposition["actor_id"] == action["actor_id"]
                    and disposition["action_type"] == action["action_type"]
                    and disposition["logical_tick"] == logical_tick,
                    f"run_disposition_action_mismatch:{logical_tick}:{intent_id}",
                )
                expected_lifecycle = (
                    "applied"
                    if disposition["status"] == "accepted"
                    and disposition["state_delta_ids"]
                    else "no_effect"
                    if disposition["status"] == "accepted"
                    else "rejected"
                )
                _require(
                    disposition["lifecycle_state"] == expected_lifecycle,
                    f"run_disposition_lifecycle_mismatch:{logical_tick}:{intent_id}",
                )
                memory[action["actor_id"]]["own_actions"].append({
                    "logical_tick": logical_tick, "action_type": action["action_type"],
                    "parameters": action["parameters"], "status": disposition["status"],
                    "reason_code": disposition["reason_code"],
                    "lifecycle_state": disposition["lifecycle_state"],
                })
                for delta_id in disposition["state_delta_ids"]:
                    _require(
                        delta_id in delta_by_id
                        and delta_by_id[delta_id]["source_intent_id"] == intent_id,
                        f"run_disposition_delta_mismatch:{logical_tick}:{intent_id}",
                    )
                _require(
                    {
                        delta_id
                        for delta_id, delta in delta_by_id.items()
                        if delta["source_intent_id"] == intent_id
                    }
                    == set(disposition["state_delta_ids"]),
                    f"run_delta_disposition_mismatch:{logical_tick}:{intent_id}",
                )
            for delta in deltas:
                apply_delta(prestate, delta)
            prestate["state_version"] += 1
            for row in rows:
                if row["record_type"] == "message_disposition" and row["payload"]["status"] != "duplicate":
                    latest_transport[row["payload"]["message_intent_id"]] = row["payload"]
        for row in trace:
            if row["record_type"] != "message_disposition":
                continue
            disposition = row["payload"]
            message_id = disposition["message_intent_id"]
            _require(
                message_id in message_intents,
                f"run_message_disposition_orphan:{message_id}",
            )
            message = message_intents[message_id]
            _require(
                disposition["sender_id"] == message["sender_id"]
                and disposition["recipient_id"] == message["recipient_id"],
                f"run_message_disposition_identity_mismatch:{message_id}",
            )
            disposition_id = disposition["disposition_id"]
            _require(
                disposition_id not in message_disposition_ids,
                f"run_message_disposition_duplicate:{disposition_id}",
            )
            message_disposition_ids.add(disposition_id)

        _require(
            all(
                any(
                    row["record_type"] == "message_disposition"
                    and row["payload"]["message_intent_id"] == message_id
                    for row in trace
                )
                for message_id in message_intents
            ),
            "run_message_intent_without_disposition",
        )
    except _PublicationCoreError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise _PublicationCoreError("run_trace_semantic_shape_invalid") from exc


def _verify_rule_reproduction(
    root: Path,
    package: EventPackage,
    data_root: Path,
    *,
    expected_identity_variant: str,
    materializer: Callable[..., dict[str, Any]] = materialize_run,
    output_roles: Sequence[str] = OUTPUT_ROLES,
) -> None:
    receipt = _read_json(_safe_custody_file(root, "run_receipt.json"))
    with tempfile.TemporaryDirectory(prefix="h2epr-publication-reproduction-") as temporary:
        reproduced = Path(temporary) / "run"
        try:
            materializer(
                package_root=package.root,
                data_root=data_root,
                output_root=reproduced,
                backend="rule",
                run_seed=0,
                identity_variant=expected_identity_variant,
                custody_locator=receipt["custody"]["relative_locator"],
            )
        except Exception as exc:
            raise _PublicationCoreError("run_independent_reproduction_failed") from exc
        for filename in (*output_roles, "run_receipt.json"):
            _require(
                (root / filename).read_bytes()
                == (reproduced / filename).read_bytes(),
                f"run_independent_reproduction_mismatch:{filename}",
            )


def _verify_run_custody(
    root: Path,
    package: EventPackage,
    *,
    expected_identity_variant: str,
    runtime_source_inventory: Callable[[], list[dict[str, str]]] = (
        h2epr_runtime_source_inventory
    ),
    run_manifest_builder: Callable[..., dict[str, Any]] = build_run_manifest,
    delta_applier: Callable[[dict[str, Any], Mapping[str, Any]], None] = (
        apply_delta
    ),
    output_roles: Sequence[str] = OUTPUT_ROLES,
) -> tuple[dict[str, Any], dict[str, Any]]:
    _require(not (root / "failure-receipt.json").exists(), "failed_attempt_not_publishable")
    manifest_path = _safe_custody_file(root, "run_manifest.json")
    receipt_path = _safe_custody_file(root, "run_receipt.json")
    manifest = _read_json(manifest_path)
    receipt = _read_json(receipt_path)
    _validate(manifest, "run-manifest.schema.json", "run_manifest")
    _validate(receipt, "run-receipt.schema.json", "run_receipt")
    _require(
        _self_hash_matches(manifest, "run_manifest_sha256"),
        "run_manifest_self_hash_mismatch",
    )
    _require(
        _self_hash_matches(receipt, "receipt_sha256"),
        "run_receipt_self_hash_mismatch",
    )
    _require(
        manifest["run_id"] == receipt["run_id"],
        "run_identity_mismatch",
    )
    _require(
        manifest["package_sha256"]
        == receipt["package_sha256"]
        == package.package_sha256,
        "run_package_identity_mismatch",
    )
    _require(
        manifest["binding_sha256"]
        == receipt["binding_sha256"]
        == package.binding_sha256,
        "run_binding_identity_mismatch",
    )
    _require(
        manifest["run_manifest_sha256"] == receipt["run_manifest_sha256"],
        "receipt_manifest_identity_mismatch",
    )
    _require(
        manifest["run_settings"]["identity_variant"]
        == expected_identity_variant,
        "run_identity_variant_mismatch",
    )
    _require(manifest["run_settings"]["seed"] == 0, "run_seed_mismatch")
    _require(
        manifest["h2epr_runtime_sources"]
        == runtime_source_inventory(),
        "h2epr_runtime_source_inventory_drift",
    )
    _require(
        manifest["masim_kernel_sources"] == masim_source_inventory(),
        "masim_kernel_source_inventory_drift",
    )
    expected_manifest = run_manifest_builder(
        package,
        backend="rule",
        run_seed=0,
        identity_variant=expected_identity_variant,
    )
    _require(
        manifest == expected_manifest,
        "run_manifest_not_independently_derived",
    )

    inventory = receipt["output_files"]
    _require(
        [row["relative_path"] for row in inventory] == list(output_roles),
        "run_output_role_inventory_mismatch",
    )
    for row in inventory:
        path = _safe_custody_file(root, row["relative_path"])
        _require(
            path.stat().st_size == row["size_bytes"],
            f"run_output_size_mismatch:{row['relative_path']}",
        )
        _require(
            file_sha256(path) == row["sha256"],
            f"run_output_hash_mismatch:{row['relative_path']}",
        )
    _require(
        canonical_sha256(inventory) == receipt["custody"]["inventory_sha256"],
        "run_custody_inventory_hash_mismatch",
    )
    _validate_custody_locator(receipt["custody"]["relative_locator"])
    _require(
        receipt["claim_boundary"] == package.manifest["claim_boundary"],
        "run_claim_boundary_mismatch",
    )

    try:
        trace = read_jsonl(
            _safe_custody_file(root, "simulation_trace.jsonl")
        )
    except ConformanceError as exc:
        raise _PublicationCoreError("run_trace_unreadable") from exc
    trace_errors = validate_trace(trace)
    _require(
        not trace_errors,
        "run_trace_invalid:" + ",".join(trace_errors),
    )
    _require(
        canonical_sha256(trace) == receipt["trace_sha256"],
        "run_trace_identity_mismatch",
    )
    _require(
        trace[0]["run_id"] == manifest["run_id"],
        "run_trace_identity_mismatch",
    )
    _verify_trace_semantics(trace, package, manifest)

    final_state = _read_json(_safe_custody_file(root, "final_state.json"))
    _require(
        canonical_sha256(final_state) == receipt["final_state_sha256"],
        "run_final_state_identity_mismatch",
    )
    try:
        replayed = replay_trace(
            package.scenario["initial_state"],
            trace,
            delta_applier,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise _PublicationCoreError("run_authoritative_replay_failed") from exc
    _require(replayed == final_state, "run_authoritative_replay_mismatch")
    expected_outcomes = [
        {
            "expectation_id": row["expectation_id"],
            "observed_value": replayed["entities"][row["entity_id"]][row["field_name"]],
            "met": condition_matches(
                replayed["entities"][row["entity_id"]][row["field_name"]],
                row["operator"], row["value"],
            ),
        }
        for row in package.scenario["mechanism"].get("outcome_expectations", [])
    ]
    _require(receipt["outcome_assessments"] == expected_outcomes,
             "run_outcome_assessment_not_independently_derived")

    replay_receipt = _read_json(
        _safe_custody_file(root, "replay_receipt.json")
    )
    _validate(replay_receipt, "replay-receipt.schema.json", "replay_receipt")
    _require(
        _self_hash_matches(replay_receipt, "receipt_sha256"),
        "replay_receipt_self_hash_mismatch",
    )
    _require(
        replay_receipt["run_id"] == manifest["run_id"]
        and replay_receipt["record_count"] == len(trace)
        and replay_receipt["tick_count"] == len(package.scenario["timeline"])
        and replay_receipt["trace_sha256"] == receipt["trace_sha256"]
        and replay_receipt["final_state_sha256"]
        == receipt["final_state_sha256"]
        and replay_receipt["replayed_state_sha256"]
        == receipt["final_state_sha256"]
        and replay_receipt["trace_errors"] == [],
        "replay_receipt_evidence_mismatch",
    )

    tick_seals = _read_json_value(
        _safe_custody_file(root, "tick_seals.json"),
        "tick_seals",
    )
    _require(isinstance(tick_seals, list), "tick_seals_shape_invalid")
    trace_tick_seals = [
        row["payload"] for row in trace if row["record_type"] == "tick_seal"
    ]
    _require(tick_seals == trace_tick_seals, "tick_seal_inventory_mismatch")
    expected_ticks = [row["logical_tick"] for row in package.scenario["timeline"]]
    _require(
        [row.get("logical_tick") for row in tick_seals] == expected_ticks,
        "tick_seal_timeline_mismatch",
    )
    _require(
        all(
            row.get("run_id") == manifest["run_id"]
            and row.get("manifest_sha256") == manifest["run_manifest_sha256"]
            for row in tick_seals
        ),
        "tick_seal_identity_mismatch",
    )

    run_seal = _read_json(_safe_custody_file(root, "run_seal.json"))
    trace_run_seals = [
        row["payload"] for row in trace if row["record_type"] == "run_seal"
    ]
    _require(trace_run_seals == [run_seal], "run_seal_trace_mismatch")
    _require(
        run_seal["run_id"] == manifest["run_id"]
        and run_seal["manifest_sha256"] == manifest["run_manifest_sha256"]
        and run_seal["final_state_sha256"] == receipt["final_state_sha256"]
        and run_seal["seal_sha256"] == receipt["run_seal_sha256"]
        and run_seal["unresolved_intent_ids"] == []
        and run_seal["unresolved_recipient_ids"] == [],
        "run_seal_evidence_mismatch",
    )

    coordinate_results = _read_json_value(
        _safe_custody_file(root, "coordinate_results.json"),
        "coordinate_results",
    )
    _require(
        isinstance(coordinate_results, list),
        "coordinate_results_shape_invalid",
    )
    _require(
        coordinate_results == _derive_coordinate_results(trace, package),
        "coordinate_results_not_trace_derived",
    )

    graph = _read_json(_safe_custody_file(root, "generated_epg.json"))
    try:
        validate_generated_epg(graph, trace)
    except GeneratedEPGError as exc:
        raise _PublicationCoreError("run_generated_epg_invalid") from exc
    expected_graph = compile_generated_epg(package, manifest, trace)
    _require(
        graph == expected_graph,
        "run_generated_epg_not_independently_derived",
    )
    _require(
        graph["seal"]["artifact_sha256"] == receipt["generated_epg_sha256"],
        "run_graph_identity_mismatch",
    )
    _require(
        receipt["counts"] == _derive_run_counts(trace, package, graph),
        "run_count_evidence_mismatch",
    )
    _require(receipt["replay_passed"], "run_replay_not_closed")
    _require(receipt["trace_coverage_passed"], "run_trace_coverage_not_closed")
    _require(
        receipt["unresolved_transport_count"] == 0,
        "run_transport_not_closed",
    )
    return manifest, receipt


def _write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _seal_inventory(root: Path) -> None:
    rows = [
        f"{file_sha256(path)}  {path.relative_to(root).as_posix()}"
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != "SHA256SUMS"
    ]
    _write_text(root / "SHA256SUMS", "\n".join(rows))


@contextmanager
def _staged_release_root(target: Path) -> Iterator[Path]:
    """Build a release beside its target and promote it with one rename."""

    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        dir=target.parent,
        prefix=f".{target.name}.publication-",
    ) as temporary:
        staged = Path(temporary) / target.name
        staged.mkdir()
        yield staged
        staged.rename(target)
