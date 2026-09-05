"""Cross-event deterministic benchmark runtime primitives."""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from h2epr.benchmark.package import EventPackage
from h2epr.canonical import canonical_sha256, file_sha256
from h2epr.masim_kernel import (
    ActionIntent,
    MessageDisposition,
    MessageIntent,
    ObservationEnvelope,
    canonical_sha256 as masim_sha256,
    replay_trace,
    validate_trace,
)

from ._environment_core import _apply_delta, condition_matches
from .generated_epg import compile_generated_epg


class _BenchmarkRunCoreError(RuntimeError):
    """A run violates package, lifecycle, trace, or release invariants."""


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_ROOT = PROJECT_ROOT / "schemas"
_NAMED_BARRIERS = (
    "open_logical_coordinate",
    "route_due_messages",
    "build_observations_from_one_sealed_prestate",
    "collect_one_decision_per_actor",
    "validate_action_message_and_authority_contracts",
    "reduce_intents_atomically",
    "record_dispositions_and_state_deltas",
    "derive_annotations_and_stage_entry",
    "seal_tick",
)
_OUTPUT_ROLES = (
    "coordinate_results.json",
    "final_state.json",
    "generated_epg.json",
    "replay_receipt.json",
    "run_manifest.json",
    "run_seal.json",
    "simulation_trace.jsonl",
    "tick_seals.json",
)


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise _BenchmarkRunCoreError(code)


def _validate(value: Mapping[str, Any], schema_name: str, label: str) -> None:
    schema = json.loads((SCHEMA_ROOT / schema_name).read_text(encoding="utf-8"))
    try:
        jsonschema.Draft202012Validator(schema).validate(value)
    except jsonschema.ValidationError as exc:
        raise _BenchmarkRunCoreError(f"{label}_schema_invalid:{exc.json_path}") from exc


class _AnnotationDetector:
    def __init__(self, scenario: Mapping[str, Any]) -> None:
        self.declarations = copy.deepcopy(scenario["mechanism"]["annotations"])
        self.emitted: set[str] = set()

    def detect(
        self,
        *,
        logical_tick: int,
        state: Mapping[str, Any],
        accepted_intent_ids: list[str],
        delta_ids: list[str],
    ) -> list[dict[str, Any]]:
        result = []
        for row in self.declarations:
            if row["one_shot"] and row["annotation_id"] in self.emitted:
                continue
            matched = all(
                condition_matches(
                    state["entities"][condition["entity_id"]][condition["field_name"]],
                    condition["operator"],
                    condition["value"],
                )
                for condition in row["when_all"]
            )
            if not matched:
                continue
            result.append(
                {
                    "annotation_id": row["annotation_id"],
                    "label": row["label"],
                    "logical_tick": logical_tick,
                    "participant_ids": copy.deepcopy(row["participant_ids"]),
                    "source_intent_ids": sorted(accepted_intent_ids),
                    "source_delta_ids": sorted(delta_ids),
                    "provenance": "generated_from_declared_state_condition",
                }
            )
            self.emitted.add(row["annotation_id"])
        return result


@dataclass(frozen=True)
class _BenchmarkRunArtifacts:
    run_manifest: dict[str, Any]
    simulation_trace: list[dict[str, Any]]
    coordinate_results: list[dict[str, Any]]
    final_state: dict[str, Any]
    tick_seals: list[dict[str, Any]]
    run_seal: dict[str, Any]
    replay_receipt: dict[str, Any]
    generated_epg: dict[str, Any]
    run_receipt: dict[str, Any]


class _BenchmarkEngineBase:
    async def setup(self) -> None:
        await self.backend.setup()

    async def shutdown(self) -> None:
        await self.backend.shutdown()

    def _pending_lifecycles(self, actor_id: str) -> list[dict[str, Any]]:
        latest: dict[str, Any] = {}
        for row in self.transport.history:
            if row.status != "duplicate":
                latest[row.message_intent_id] = row
        return [
            {
                "lifecycle_id": "message_delivery",
                "message_intent_id": intent_id,
                "status": row.status,
                "counterparty_id": (
                    row.recipient_id if row.sender_id == actor_id else row.sender_id
                ),
            }
            for intent_id, row in sorted(latest.items())
            if row.status not in {"delivered", "expired", "rejected", "duplicate", "failed"}
            and actor_id in {row.sender_id, row.recipient_id}
        ]

    def _state_projection(
        self, state: Mapping[str, Any], visibility: str, actor_id: str | None = None
    ) -> dict[str, Any]:
        declarations = self.package.scenario["mechanism"]["state_fields"]
        entities: dict[str, dict[str, Any]] = {}
        for row in declarations:
            if row["visibility"] != visibility:
                continue
            if visibility == "actor_private" and row["entity_id"] != actor_id:
                continue
            entities.setdefault(row["entity_id"], {})[row["field_name"]] = copy.deepcopy(
                state["entities"][row["entity_id"]][row["field_name"]]
            )
        return {"state_version": state["state_version"], "entities": entities}

    def _observation_bundle(
        self,
        *,
        actor_id: str,
        coordinate: Mapping[str, Any],
        state: Mapping[str, Any],
        prestate_sha256: str,
        delivered_messages: tuple[Mapping[str, Any], ...],
    ) -> dict[str, Any]:
        logical_tick = coordinate["logical_tick"]
        public_state = self._state_projection(state, "public")
        private_state = self._state_projection(state, "actor_private", actor_id)
        envelope = ObservationEnvelope(
            actor_id=actor_id,
            logical_tick=logical_tick,
            physical_masim_round=logical_tick,
            execution_level=0,
            prestate_version=state["state_version"],
            prestate_sha256=prestate_sha256,
            public_state=public_state,
            private_state=private_state,
            delivered_messages=delivered_messages,
            prior_generated_state=copy.deepcopy(self.participant_memory[actor_id]),
        ).to_dict()
        contract = {
            "schema_version": "h2epr.participant-observation.v3",
            "actor_id": actor_id,
            "logical_tick": logical_tick,
            "public_state": public_state,
            "private_state": private_state,
            "delivered_messages": copy.deepcopy(list(delivered_messages)),
            "pending_lifecycles": self._pending_lifecycles(actor_id),
            "memory": copy.deepcopy(self.participant_memory[actor_id]),
            "permitted_action_types": copy.deepcopy(
                self.package.scenario["action_spaces"][actor_id]
            ),
        }
        return {
            "contract": contract,
            "runtime": {
                "coordinate": {
                    "coordinate_id": coordinate["coordinate_id"],
                    "logical_tick": logical_tick,
                },
                "prestate_version": state["state_version"],
                "prestate_sha256": prestate_sha256,
                "physical_masim_round": logical_tick,
                "execution_level": 0,
                "masim_envelope_sha256": masim_sha256(envelope),
            },
        }

    async def run_coordinate(
        self,
        coordinate: Mapping[str, Any],
        barriers: tuple[str, ...] = _NAMED_BARRIERS,
    ) -> dict[str, Any]:
        if barriers != _NAMED_BARRIERS:
            raise _BenchmarkRunCoreError("named_barrier_order_mismatch")
        logical_tick = coordinate["logical_tick"]
        state = self.reducer.state
        prestate_sha256 = masim_sha256(state)
        self.trace.append(
            "tick_open",
            logical_tick,
            {
                "coordinate": copy.deepcopy(dict(coordinate)),
                "physical_masim_round": logical_tick,
                "execution_level": 0,
            },
        )
        _, due_dispositions = self.transport.route_due(logical_tick)
        for disposition in due_dispositions:
            self.trace.append(
                "message_disposition", logical_tick, disposition.to_dict()
            )
        delivered_by_actor = {
            actor_id: self.transport.consume(actor_id, logical_tick)
            for actor_id in self.actor_ids
        }
        observations = {
            actor_id: self._observation_bundle(
                actor_id=actor_id,
                coordinate=coordinate,
                state=state,
                prestate_sha256=prestate_sha256,
                delivered_messages=delivered_by_actor[actor_id],
            )
            for actor_id in self.actor_ids
        }
        for actor_id in self.actor_ids:
            self.trace.append("observation", logical_tick, observations[actor_id])
        decisions = await self.backend.decide(observations)
        if tuple(sorted(decisions)) != self.actor_ids:
            raise _BenchmarkRunCoreError("backend_decision_actor_universe_mismatch")
        actions: list[ActionIntent] = []
        messages: list[MessageIntent] = []
        for actor_id in self.actor_ids:
            action, outbound = decisions[actor_id]
            if action.actor_id != actor_id or any(
                message.sender_id != actor_id
                or message.source_action_intent_id != action.intent_id
                for message in outbound
            ):
                raise _BenchmarkRunCoreError("backend_decision_lineage_mismatch")
            decision_projection = self.backend.decision_projection(
                logical_tick, actor_id
            )
            self.trace.append(
                "participant_decision", logical_tick, decision_projection
            )
            actions.append(action)
            messages.extend(outbound)
            self.trace.append("action_intent", logical_tick, action.to_dict())
            for message in outbound:
                self.trace.append(
                    "message_intent", logical_tick, message.to_dict()
                )
        reducer_result = self.reducer.reduce(
            actions,
            logical_tick=logical_tick,
            run_seed=self.run_seed,
        )
        action_by_intent = {action.intent_id: action for action in actions}
        disposition_by_intent = {
            disposition.intent_id: disposition
            for disposition in reducer_result.dispositions
        }
        accepted_messages = [
            message
            for message in messages
            if disposition_by_intent[message.source_action_intent_id].status
            == "accepted"
        ]
        rejected_messages = [
            message
            for message in messages
            if disposition_by_intent[message.source_action_intent_id].status
            != "accepted"
        ]
        message_dispositions = list(
            self.transport.submit(accepted_messages, logical_tick=logical_tick)
        )
        message_dispositions.extend(
            MessageDisposition(
                disposition_id=(
                    f"md.{message.message_intent_id}.source-action-rejected"
                ),
                message_intent_id=message.message_intent_id,
                sender_id=message.sender_id,
                recipient_id=message.recipient_id,
                logical_tick=logical_tick,
                status="rejected",
                reason_code="source_action_not_accepted",
            )
            for message in rejected_messages
        )
        enriched_dispositions: list[dict[str, Any]] = []
        accepted_intent_ids: list[str] = []
        for disposition in reducer_result.dispositions:
            action = action_by_intent[disposition.intent_id]
            payload = disposition.to_dict()
            payload.update(
                {
                    "actor_id": action.actor_id,
                    "action_type": action.action_type,
                    "lifecycle_state": (
                        "applied"
                        if disposition.status == "accepted"
                        and disposition.state_delta_ids
                        else "no_effect"
                        if disposition.status == "accepted"
                        else "rejected"
                    ),
                }
            )
            enriched_dispositions.append(payload)
            self.trace.append("action_disposition", logical_tick, payload)
            if disposition.status == "accepted":
                accepted_intent_ids.append(disposition.intent_id)
        for disposition in sorted(
            message_dispositions,
            key=lambda row: (row.message_intent_id, row.status),
        ):
            self.trace.append(
                "message_disposition", logical_tick, disposition.to_dict()
            )
        delta_rows: list[dict[str, Any]] = []
        for delta in reducer_result.deltas:
            payload = delta.to_dict()
            delta_rows.append(payload)
            self.trace.append("state_delta", logical_tick, payload)
        self.trace.append(
            "tick_commit",
            logical_tick,
            {
                "state_version": reducer_result.state["state_version"],
                "state_sha256": reducer_result.poststate_sha256,
                "prestate_sha256": reducer_result.prestate_sha256,
                "coordinate_id": coordinate["coordinate_id"],
            },
        )
        if coordinate["stage_id"] not in self._seen_stage_ids:
            self.trace.append(
                "stage_entry",
                logical_tick,
                {
                    "stage_id": coordinate["stage_id"],
                    "episode_id": coordinate["episode_id"],
                    "coordinate_id": coordinate["coordinate_id"],
                    "provenance": "configuration_timeline_dataset_derived",
                },
            )
            self._seen_stage_ids.add(coordinate["stage_id"])
        annotations = self.detector.detect(
            logical_tick=logical_tick,
            state=reducer_result.state,
            accepted_intent_ids=accepted_intent_ids,
            delta_ids=[row["delta_id"] for row in delta_rows],
        )
        for annotation in annotations:
            self.trace.append("generated_annotation", logical_tick, annotation)
        tick_seal = self.trace.seal_tick(logical_tick, reducer_result.state)
        result = {
            "logical_tick": logical_tick,
            "coordinate_id": coordinate["coordinate_id"],
            "stage_id": coordinate["stage_id"],
            "episode_id": coordinate["episode_id"],
            "action_intent_count": len(actions),
            "message_intent_count": len(messages),
            "delivered_message_count": sum(map(len, delivered_by_actor.values())),
            "state_delta_count": len(delta_rows),
            "annotation_count": len(annotations),
            "poststate_sha256": reducer_result.poststate_sha256,
            "tick_seal_sha256": tick_seal.seal_sha256,
        }
        self.coordinate_results[logical_tick] = result
        return copy.deepcopy(result)

    def _validate_termination(self, final_state: Mapping[str, Any]) -> None:
        for condition in self.package.scenario["mechanism"]["termination_invariants"]:
            try:
                value = final_state["entities"][condition["entity_id"]][
                    condition["field_name"]
                ]
            except KeyError as exc:
                raise _BenchmarkRunCoreError("termination_invariant_field_missing") from exc
            if not condition_matches(
                value, condition["operator"], condition["value"]
            ):
                raise _BenchmarkRunCoreError(
                    f"termination_invariant_failed:{condition['entity_id']}:{condition['field_name']}"
                )

    def finalize(self) -> _BenchmarkRunArtifacts:
        expected_ticks = tuple(row["logical_tick"] for row in self.timeline)
        if tuple(sorted(self.coordinate_results)) != expected_ticks:
            raise _BenchmarkRunCoreError("runtime_tick_coverage_incomplete")
        final_state = self.reducer.state
        unresolved_ids, unresolved_recipients = self.transport.unresolved()
        if (
            self.package.scenario["termination"]["require_no_unresolved_messages"]
            and unresolved_ids
        ):
            raise _BenchmarkRunCoreError("unresolved_transport_at_termination")
        self._validate_termination(final_state)
        run_seal = self.trace.seal_run(
            final_state, unresolved_ids, unresolved_recipients
        )
        trace_errors = validate_trace(self.trace.records)
        if trace_errors:
            raise _BenchmarkRunCoreError(
                "trace_validation_failed:" + ",".join(trace_errors)
            )
        replayed = replay_trace(
            self.package.scenario["initial_state"],
            self.trace.records,
            _apply_delta,
        )
        if masim_sha256(replayed) != masim_sha256(final_state):
            raise _BenchmarkRunCoreError("authoritative_replay_mismatch")
        graph = compile_generated_epg(
            self.package, self.manifest, self.trace.records
        )
        tick_seals = [
            copy.deepcopy(row["payload"])
            for row in self.trace.records
            if row["record_type"] == "tick_seal"
        ]
        replay_receipt = {
            "receipt_version": "h2epr.benchmark.replay-receipt.v3",
            "status": "pass",
            "run_id": self.manifest["run_id"],
            "record_count": len(self.trace.records),
            "tick_count": len(self.timeline),
            "trace_sha256": masim_sha256(self.trace.records),
            "final_state_sha256": masim_sha256(final_state),
            "replayed_state_sha256": masim_sha256(replayed),
            "trace_errors": [],
            "receipt_sha256": "0" * 64,
        }
        replay_receipt["receipt_sha256"] = canonical_sha256(
            {
                key: item
                for key, item in replay_receipt.items()
                if key != "receipt_sha256"
            }
        )
        counts: dict[str, int] = {
            "trace_records": len(self.trace.records),
            "ticks": len(self.timeline),
            "actors": len(self.actor_ids),
            "graph_nodes": len(graph["nodes"]),
            "graph_edges": len(graph["edges"]),
        }
        for row in self.trace.records:
            record_key = f"record.{row['record_type']}"
            counts[record_key] = counts.get(record_key, 0) + 1
            if row["record_type"] == "action_intent":
                action_key = f"action.{row['payload']['action_type']}"
                counts[action_key] = counts.get(action_key, 0) + 1
        receipt = {
            "schema_version": "h2epr.run-receipt.v4",
            "run_id": self.manifest["run_id"],
            "package_sha256": self.package.package_sha256,
            "binding_sha256": self.package.binding_sha256,
            "run_manifest_sha256": self.manifest["run_manifest_sha256"],
            "trace_sha256": masim_sha256(self.trace.records),
            "final_state_sha256": masim_sha256(final_state),
            "run_seal_sha256": run_seal.seal_sha256,
            "replay_passed": True,
            "generated_epg_sha256": graph["seal"]["artifact_sha256"],
            "trace_coverage_passed": not graph["trace_coverage"]["unreferenced_trace_ids"],
            "counts": dict(sorted(counts.items())),
            "unresolved_transport_count": len(unresolved_ids),
            "outcome_assessments": [
                {
                    "expectation_id": row["expectation_id"],
                    "observed_value": copy.deepcopy(
                        final_state["entities"][row["entity_id"]][row["field_name"]]
                    ),
                    "met": condition_matches(
                        final_state["entities"][row["entity_id"]][row["field_name"]],
                        row["operator"], row["value"],
                    ),
                }
                for row in self.package.scenario["mechanism"].get("outcome_expectations", [])
            ],
            "claim_boundary": copy.deepcopy(self.package.manifest["claim_boundary"]),
            "custody": {
                "relative_locator": ".local-runtime/h2epr-simulation/runs/unpublished",
                "inventory_sha256": "0" * 64,
            },
            "output_files": [],
            "receipt_sha256": "0" * 64,
        }
        return _BenchmarkRunArtifacts(
            run_manifest=copy.deepcopy(self.manifest),
            simulation_trace=copy.deepcopy(self.trace.records),
            coordinate_results=[
                copy.deepcopy(self.coordinate_results[tick])
                for tick in expected_ticks
            ],
            final_state=final_state,
            tick_seals=tick_seals,
            run_seal=run_seal.to_dict(),
            replay_receipt=replay_receipt,
            generated_epg=graph,
            run_receipt=receipt,
        )


def _build_determinism_receipt(
    *,
    left_root: Path,
    right_root: Path,
    package: EventPackage,
    identity_conformance_receipt_sha256: str,
) -> dict[str, Any]:
    compared = []
    for filename in (*_OUTPUT_ROLES, "run_receipt.json"):
        left_sha = file_sha256(left_root / filename)
        right_sha = file_sha256(right_root / filename)
        compared.append(
            {
                "artifact_role": filename,
                "run_a_sha256": left_sha,
                "run_b_sha256": right_sha,
                "identical": left_sha == right_sha,
            }
        )
    left_receipt = json.loads((left_root / "run_receipt.json").read_text(encoding="utf-8"))
    right_receipt = json.loads((right_root / "run_receipt.json").read_text(encoding="utf-8"))
    receipt = {
        "schema_version": "h2epr.determinism-receipt.v3",
        "receipt_id": f"{package.manifest['package_id']}.rule-determinism",
        "package_sha256": package.package_sha256,
        "binding_sha256": package.binding_sha256,
        "run_a_id": left_receipt["run_id"],
        "run_b_id": right_receipt["run_id"],
        "compared_artifacts": compared,
        "all_byte_identical": all(row["identical"] for row in compared),
        "identity_conformance_receipt_sha256": identity_conformance_receipt_sha256,
        "receipt_sha256": "0" * 64,
    }
    receipt["receipt_sha256"] = canonical_sha256(
        {key: item for key, item in receipt.items() if key != "receipt_sha256"}
    )
    _validate(receipt, "determinism-receipt.schema.json", "determinism_receipt")
    return receipt
