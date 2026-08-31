"""Deterministic phased execution for the accepted Note7 runtime bundle."""

from __future__ import annotations

import asyncio
import copy
from dataclasses import dataclass, fields, is_dataclass
from pathlib import Path
from typing import Any, Mapping

from masim.integrations.event_process import (
    ActionIntent,
    AppendOnlyTransport,
    AuthoritativeReducer,
    ObservationEnvelope,
    TraceWriter,
    canonical_sha256,
    replay_trace,
    validate_trace,
)
from masim.simulator.base import SimulationConfig
from masim.simulator.phased import (
    NAMED_BARRIERS,
    PhasedSimulationRunner,
    PhasedSimulator,
)

from .executable_admission import ExecutableAdmission
from .runtime_components import (
    Note7Environment,
    Note7ObservationProjector,
    Note7ParticipantExecutor,
    Note7Reducer,
    Note7TraceCompiler,
)


class Note7ExecutionError(RuntimeError):
    """The admitted package could not complete a deterministic run."""


def _plain(value: Any) -> Any:
    if is_dataclass(value):
        return {
            item.name: _plain(getattr(value, item.name))
            for item in fields(value)
        }
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return copy.deepcopy(value)


def _apply_delta(state: dict[str, Any], payload: Mapping[str, Any]) -> None:
    target = (
        state
        if payload["entity_id"] == "__world__"
        else state["actors"][payload["entity_id"]]
    )
    field_name = payload["field_name"]
    if canonical_sha256(target[field_name]) != canonical_sha256(payload["before"]):
        raise Note7ExecutionError(
            "note7_replay_delta_before_mismatch:"
            f"{payload['entity_id']}:{field_name}:"
            f"actual={canonical_sha256(target[field_name])}:"
            f"declared={canonical_sha256(payload['before'])}"
        )
    target[field_name] = copy.deepcopy(payload["after"])


def _carry_forward_record(
    *,
    object_id: str,
    owner_actor_id: str,
    state_id: str,
    version: int,
) -> dict[str, Any]:
    """Preserve one unresolved accepted lifecycle object at the horizon."""

    if (
        any(
            not isinstance(value, str)
            or not value
            or value.strip() != value
            for value in (object_id, owner_actor_id, state_id)
        )
        or type(version) is not int
        or version < 0
    ):
        raise Note7ExecutionError(
            "note7_execution_carry_forward_invalid"
        )
    return {
        "object_id": object_id,
        "owner_actor_id": owner_actor_id,
        "state": state_id,
        "version": version,
        "reason_code": "analytic_horizon_reached",
        "next_event_id": "event.0481.post_horizon",
        "terminal": False,
    }


def build_note7_run_manifest(admission: ExecutableAdmission) -> dict[str, Any]:
    """Build the reproducible run identity without operational coordinates."""

    bundle = admission.runtime_bundle_document
    preimage = {
        "format_identity": "h2epr.rule-run-manifest.v0_1",
        "run_id": "run.h2epr.0481.canonical.v0_1",
        "event_id": "H2EPR-0481",
        "package_id": admission.package_id,
        "package_version": admission.package_version,
        "package_source_sha256": admission.package_source_sha256,
        "runtime_bundle_id": admission.runtime_bundle_id,
        "runtime_bundle_version": admission.runtime_bundle_version,
        "runtime_bundle_source_sha256": (
            admission.runtime_bundle_source_sha256
        ),
        "runtime_bundle_canonical_sha256": (
            admission.runtime_bundle_canonical_sha256
        ),
        "run_profile_id": bundle["run_profile_id"],
        "run_seed": bundle["run_seed"],
        "participant_ids": sorted(
            row["actor_id"] for row in bundle["actor_registry"]
        ),
        "logical_clock": _plain(bundle["clock"]),
        "component_bindings": _plain(
            admission.package_document["component_bindings"]
        ),
        "resume_allowed": False,
        "historical_calibration": False,
        "historical_validation": False,
        "output_interpretation": "simulation_generated_mechanism_coverage",
    }
    return {**preimage, "manifest_sha256": canonical_sha256(preimage)}


@dataclass(frozen=True)
class Note7RunArtifacts:
    """Reproducibility documents produced by one complete materialization."""

    run_manifest: dict[str, Any]
    simulation_trace: list[dict[str, Any]]
    final_state: dict[str, Any]
    tick_seals: list[dict[str, Any]]
    run_seal: dict[str, Any]
    replay_receipt: dict[str, Any]
    generated_epg: dict[str, Any]
    execution_receipt: dict[str, Any]

    def document_hashes(self) -> dict[str, str]:
        return {
            "run_manifest": canonical_sha256(self.run_manifest),
            "simulation_trace": canonical_sha256(self.simulation_trace),
            "final_state": canonical_sha256(self.final_state),
            "tick_seals": canonical_sha256(self.tick_seals),
            "run_seal": canonical_sha256(self.run_seal),
            "replay_receipt": canonical_sha256(self.replay_receipt),
            "generated_epg": canonical_sha256(self.generated_epg),
            "execution_receipt": canonical_sha256(self.execution_receipt),
        }


class Note7FullRosterEngine:
    """Local engine injected into MASim's public named-barrier lifecycle."""

    def __init__(self, admission: ExecutableAdmission) -> None:
        if not admission.accepted or not admission.execution_eligible:
            raise Note7ExecutionError("note7_execution_package_not_eligible")
        self.admission = admission
        self.bundle = _plain(admission.runtime_bundle_document)
        self.manifest = build_note7_run_manifest(admission)
        self.actor_ids = tuple(
            sorted(row["actor_id"] for row in self.bundle["actor_registry"])
        )
        self.context_recipient_ids = tuple(
            sorted(
                {
                    row["target_id"]
                    for row in self.bundle["communication_routes"]
                    if row["target_id"] not in self.actor_ids
                }
            )
        )
        self.logical_ticks = tuple(
            row["logical_tick"] for row in self.bundle["clock"]["logical_ticks"]
        )
        self._clock_by_tick = {
            row["logical_tick"]: row for row in self.bundle["clock"]["logical_ticks"]
        }
        self._exogenous_by_tick: dict[int, list[dict[str, Any]]] = {}
        for row in self.bundle["exogenous_inputs"]:
            if row["release_tick"] is not None:
                self._exogenous_by_tick.setdefault(row["release_tick"], []).append(row)
        self.projector = Note7ObservationProjector(self.bundle)
        self.executor = Note7ParticipantExecutor()
        self.environment = Note7Environment(self.bundle)
        self.reducer = AuthoritativeReducer(
            self.bundle["initial_state"], Note7Reducer(self.bundle).apply_batch
        )
        self.transport = AppendOnlyTransport(self.bundle["communication_routes"])
        self.trace = TraceWriter(
            self.manifest["run_id"], self.manifest["manifest_sha256"]
        )
        self.compiler = Note7TraceCompiler()
        self.tick_results: dict[int, dict[str, Any]] = {}
        self._released_input_ids: list[str] = []
        self._operated_actor_ids: set[str] = set()
        self._evaluated_commitment_keys: set[tuple[str, str, str]] = set()
        self._scenario_policy_ids: set[str] = set()
        self._finalized = False

    def launch_participants(self) -> dict[str, str]:
        return {actor_id: actor_id for actor_id in self.actor_ids}

    async def setup(self, handles: Mapping[str, Any]) -> None:
        if tuple(sorted(handles)) != self.actor_ids:
            raise Note7ExecutionError("note7_execution_actor_launch_mismatch")

    async def run_tick(
        self, logical_tick: int, barriers: tuple[str, ...]
    ) -> dict[str, Any]:
        if barriers != NAMED_BARRIERS:
            raise Note7ExecutionError("note7_execution_barrier_order_mismatch")
        if logical_tick not in self._clock_by_tick or logical_tick in self.tick_results:
            raise Note7ExecutionError("note7_execution_tick_invalid_or_repeated")
        clock = self._clock_by_tick[logical_tick]
        self.trace.append(
            "tick_open",
            logical_tick,
            {
                "logical_date": clock["logical_date"],
                "partial_order_slot": clock["partial_order_slot"],
                "physical_masim_round": logical_tick,
                "execution_level": 0,
                "intraday_precision_claimed": False,
            },
        )
        for item in sorted(
            self._exogenous_by_tick.get(logical_tick, ()),
            key=lambda value: value["id"],
        ):
            self._released_input_ids.append(item["id"])
            self.trace.append(
                "exogenous_input_release",
                logical_tick,
                {
                    "input_id": item["id"],
                    "source_class": item["family"],
                    "outcome_forcing": item["outcome_forcing"],
                    "effect": item["typed_effect"],
                },
            )

        deliveries, delivery_dispositions = self.transport.route_due(logical_tick)
        for disposition in delivery_dispositions:
            self.trace.append(
                "message_disposition", logical_tick, disposition.to_dict()
            )
        delivered_by_actor = {
            actor_id: self.transport.consume(actor_id, logical_tick)
            for actor_id in self.actor_ids
        }
        delivered_by_context = {
            recipient_id: self.transport.consume(recipient_id, logical_tick)
            for recipient_id in self.context_recipient_ids
        }
        consumed_count = sum(
            len(rows) for rows in delivered_by_actor.values()
        ) + sum(len(rows) for rows in delivered_by_context.values())
        if len(deliveries) != consumed_count:
            raise Note7ExecutionError(
                "note7_execution_delivery_consumption_mismatch"
            )

        state = self.reducer.state
        prestate_hash = canonical_sha256(state)
        due_rules = self.projector.due_rules(logical_tick)
        due_count_by_actor = {actor_id: 0 for actor_id in self.actor_ids}
        for rule in due_rules:
            due_count_by_actor[rule["actor_id"]] += 1
        for actor_id in self.actor_ids:
            observation = ObservationEnvelope(
                actor_id=actor_id,
                logical_tick=logical_tick,
                physical_masim_round=logical_tick,
                execution_level=0,
                prestate_version=state["state_version"],
                prestate_sha256=prestate_hash,
                public_state={
                    "state_version": state["state_version"],
                    "released_exogenous_input_ids": sorted(
                        self._released_input_ids
                    ),
                    "open_lifecycle_object_count": sum(
                        not item["terminal"]
                        for item in state["lifecycle_objects"].values()
                    ),
                },
                private_state=state["actors"][actor_id],
                delivered_messages=delivered_by_actor[actor_id],
                prior_generated_state={
                    "due_decision_count": due_count_by_actor[actor_id]
                },
            )
            self.trace.append(
                "observation", logical_tick, observation.to_dict()
            )
            self._operated_actor_ids.add(actor_id)

        action_intents: list[ActionIntent] = []
        for rule in due_rules:
            context = self.projector.project(
                actor_id=rule["actor_id"],
                capability_id=rule["capability_id"],
                commitment_id=rule["commitment_id"],
                logical_tick=logical_tick,
                state=state,
            )
            projected = self.executor.evaluate(
                context,
                run_id=self.manifest["run_id"],
                logical_tick=logical_tick,
                prestate_version=state["state_version"],
                prestate_sha256=prestate_hash,
                primary_lifecycle_id=rule["primary_lifecycle_id"],
            )
            decision = projected.decision
            actual = {
                "branch_id": decision.branch_id,
                "intent_id": decision.intent_id,
                "no_intent_reason_code": decision.no_intent_reason_code,
            }
            if actual != rule["expected_outcome"]:
                raise Note7ExecutionError(
                    "note7_execution_projected_outcome_mismatch:"
                    f"{rule['actor_id']}:{rule['commitment_id']}"
                )
            decision_payload = {
                "actor_id": decision.actor_id,
                "capability_id": decision.capability_id,
                "commitment_id": decision.commitment_id,
                "branch_id": decision.branch_id,
                "semantic_intent_id": decision.intent_id,
                "no_intent_reason_code": decision.no_intent_reason_code,
                "revisit_trigger_ids": list(decision.revisit_trigger_ids),
                "consumed_observation_ids": list(
                    decision.consumed_observation_ids
                ),
                "persistent_state_ids": list(decision.persistent_state_ids),
                "consumed_configuration_parameter_ids": list(
                    decision.consumed_configuration_parameter_ids
                ),
                "lifecycle_ids": list(decision.lifecycle_ids),
                "proposed_private_state_updates": dict(
                    decision.proposed_private_state_updates
                ),
                "observation_rule_id": rule["observation_rule_id"],
            }
            self.trace.append(
                "participant_decision", logical_tick, decision_payload
            )
            self._evaluated_commitment_keys.add(
                (
                    decision.actor_id,
                    decision.capability_id,
                    decision.commitment_id,
                )
            )
            if projected.action_intent is not None:
                action_intents.append(projected.action_intent)
                self.trace.append(
                    "action_intent",
                    logical_tick,
                    projected.action_intent.to_dict(),
                )

        reducer_result = self.reducer.reduce(
            action_intents,
            logical_tick=logical_tick,
            run_seed=self.bundle["run_seed"],
        )
        by_intent = {intent.intent_id: intent for intent in action_intents}
        for disposition in reducer_result.dispositions:
            payload = disposition.to_dict()
            payload["action_type"] = by_intent[disposition.intent_id].action_type
            self.trace.append("action_disposition", logical_tick, payload)
        for delta in reducer_result.deltas:
            self.trace.append("state_delta", logical_tick, delta.to_dict())

        for disposition in reducer_result.dispositions:
            for application in self.environment.policy_applications(
                by_intent[disposition.intent_id],
                disposition,
                logical_date=clock["logical_date"],
            ):
                self.trace.append(
                    "scenario_policy_application", logical_tick, application
                )
                self._scenario_policy_ids.add(application["policy_id"])

        messages = []
        for disposition in reducer_result.dispositions:
            messages.extend(
                self.environment.messages_for(
                    by_intent[disposition.intent_id], disposition
                )
            )
        for message in messages:
            self.trace.append("message_intent", logical_tick, message.to_dict())
        for disposition in self.transport.submit(
            messages, logical_tick=logical_tick
        ):
            self.trace.append(
                "message_disposition", logical_tick, disposition.to_dict()
            )

        if logical_tick == self.logical_ticks[-1]:
            self._append_completion_records(logical_tick, reducer_result.state)
        self.trace.append(
            "tick_commit",
            logical_tick,
            {
                "state_version": reducer_result.state["state_version"],
                "state_sha256": reducer_result.poststate_sha256,
                "prestate_sha256": reducer_result.prestate_sha256,
            },
        )
        tick_seal = self.trace.seal_tick(logical_tick, reducer_result.state)
        result = {
            "logical_tick": logical_tick,
            "logical_date": clock["logical_date"],
            "partial_order_slot": clock["partial_order_slot"],
            "decision_count": len(due_rules),
            "action_intent_count": len(action_intents),
            "message_intent_count": len(messages),
            "tick_seal_sha256": tick_seal.seal_sha256,
            "poststate_sha256": reducer_result.poststate_sha256,
        }
        self.tick_results[logical_tick] = result
        return copy.deepcopy(result)

    def _append_completion_records(
        self, logical_tick: int, state: Mapping[str, Any]
    ) -> None:
        open_objects = tuple(
            sorted(
                (
                    object_id,
                    item,
                )
                for object_id, item in state["lifecycle_objects"].items()
                if not item["terminal"]
            )
        )
        for object_id, item in open_objects:
            carried = _carry_forward_record(
                object_id=object_id,
                owner_actor_id=item["owner_actor_id"],
                state_id=item["state_id"],
                version=item["version"],
            )
            self.trace.append("carry_forward", logical_tick, _plain(carried))
        unresolved_ids, unresolved_recipients = self.transport.unresolved()
        if unresolved_ids or unresolved_recipients:
            raise Note7ExecutionError("note7_execution_due_message_unresolved")
        self.trace.append(
            "completion",
            logical_tick,
            {
                "condition_ids": self.bundle["completion_policy"][
                    "normal_condition_ids"
                ],
                "status": "normal",
                "carried_forward_object_count": len(open_objects),
                "unresolved_message_intent_count": 0,
            },
        )

    async def shutdown(self) -> None:
        return None

    def phase_execute(
        self, round_num: int, level_handles: Mapping[str, Any]
    ) -> dict[str, Any]:
        return {"logical_tick": round_num, "actor_ids": sorted(level_handles)}

    def phase_collect(self, execute_result: Mapping[str, Any]) -> dict[str, Any]:
        return copy.deepcopy(dict(execute_result))

    def phase_dispatch(self, all_info_lists: list[list[dict[str, Any]]]) -> None:
        if all_info_lists:
            raise Note7ExecutionError("note7_execution_legacy_dispatch_forbidden")

    def get_tick_result(self, logical_tick: int) -> dict[str, Any] | None:
        return copy.deepcopy(self.tick_results.get(logical_tick))

    def finalize(self) -> Note7RunArtifacts:
        if self._finalized:
            raise Note7ExecutionError("note7_execution_already_finalized")
        if tuple(sorted(self.tick_results)) != self.logical_ticks:
            raise Note7ExecutionError("note7_execution_tick_coverage_incomplete")
        expected_commitments = len(self.bundle["observation_rules"])
        if (
            self._operated_actor_ids != set(self.actor_ids)
            or len(self._evaluated_commitment_keys) != expected_commitments
            or len(self._scenario_policy_ids) != 9
        ):
            raise Note7ExecutionError("note7_execution_semantic_coverage_incomplete")
        final_state = self.reducer.state
        unresolved_ids, unresolved_recipients = self.transport.unresolved()
        if unresolved_ids or unresolved_recipients:
            raise Note7ExecutionError("note7_execution_unresolved_transport")
        run_seal = self.trace.seal_run(
            final_state, unresolved_ids, unresolved_recipients
        )
        trace_errors = validate_trace(self.trace.records)
        if trace_errors:
            raise Note7ExecutionError(
                "note7_execution_trace_invalid:" + ",".join(trace_errors)
            )
        replayed = replay_trace(
            self.bundle["initial_state"], self.trace.records, _apply_delta
        )
        if canonical_sha256(replayed) != canonical_sha256(final_state):
            raise Note7ExecutionError("note7_execution_replay_state_mismatch")
        generated_epg = self.compiler.compile(
            self.trace.records, run_seal_sha256=run_seal.seal_sha256
        )
        tick_seals = [
            copy.deepcopy(row["payload"])
            for row in self.trace.records
            if row["record_type"] == "tick_seal"
        ]
        replay_receipt = {
            "format_identity": "h2epr.replay-receipt.v0_1",
            "status": "pass",
            "run_id": self.manifest["run_id"],
            "record_count": len(self.trace.records),
            "tick_count": len(self.logical_ticks),
            "trace_sha256": canonical_sha256(self.trace.records),
            "final_state_sha256": canonical_sha256(final_state),
            "replayed_state_sha256": canonical_sha256(replayed),
            "trace_errors": [],
        }
        record_counts: dict[str, int] = {}
        for row in self.trace.records:
            record_counts[row["record_type"]] = (
                record_counts.get(row["record_type"], 0) + 1
            )
        lifecycle_ids = {
            item["lifecycle_id"]
            for item in final_state["lifecycle_objects"].values()
        }
        execution_receipt = {
            "format_identity": "h2epr.rule-execution-receipt.v0_1",
            "status": "pass",
            "event_id": "H2EPR-0481",
            "run_id": self.manifest["run_id"],
            "manifest_sha256": self.manifest["manifest_sha256"],
            "runtime_bundle_sha256": (
                self.admission.runtime_bundle_canonical_sha256
            ),
            "simulation_trace_sha256": canonical_sha256(self.trace.records),
            "run_seal_sha256": run_seal.seal_sha256,
            "final_state_sha256": canonical_sha256(final_state),
            "replay_receipt_sha256": canonical_sha256(replay_receipt),
            "generated_epg_sha256": generated_epg["seal"]["artifact_sha256"],
            "coverage": {
                "actors_operated": len(self._operated_actor_ids),
                "actor_capability_bindings": sum(
                    len(row["capability_projections"])
                    for row in self.bundle["carrier_projections"]
                ),
                "commitments_evaluated": len(
                    self._evaluated_commitment_keys
                ),
                "scenario_policies_exercised": len(
                    self._scenario_policy_ids
                ),
                "lifecycle_families_realized": len(lifecycle_ids),
                "record_counts": dict(sorted(record_counts.items())),
            },
            "completion_status": "normal",
            "unresolved_message_intent_ids": [],
            "claim_boundary": _plain(self.bundle["claim_boundary"]),
        }
        self._finalized = True
        return Note7RunArtifacts(
            run_manifest=copy.deepcopy(self.manifest),
            simulation_trace=copy.deepcopy(self.trace.records),
            final_state=final_state,
            tick_seals=tick_seals,
            run_seal=run_seal.to_dict(),
            replay_receipt=replay_receipt,
            generated_epg=generated_epg,
            execution_receipt=execution_receipt,
        )


class Note7FullRosterSimulator(PhasedSimulator):
    """Project binding for the public MASim phased simulator."""


class Note7FullRosterRunner(PhasedSimulationRunner):
    simulator_class = Note7FullRosterSimulator


async def _materialize(
    admission: ExecutableAdmission,
    operational_root: Path,
) -> Note7RunArtifacts:
    if operational_root.exists() and any(operational_root.iterdir()):
        raise FileExistsError("note7_operational_root_must_be_fresh")
    operational_root.mkdir(parents=True, exist_ok=True)
    engine = Note7FullRosterEngine(admission)
    config = SimulationConfig(
        setting={
            "name": "h2epr_0481_full_roster_rule",
            "record_path": str(operational_root),
            "round_history_limit": len(engine.logical_ticks),
            "phased_engine_factory": lambda: engine,
        },
        ray={},
        players={},
        topology={},
        environment={},
        communication={},
        knowledge={},
        simulation_id=engine.manifest["run_id"],
    )
    runner = Note7FullRosterRunner(config)
    results = await runner.execute()
    if len(results) != len(engine.logical_ticks):
        raise Note7ExecutionError("note7_execution_result_tick_count_mismatch")
    return engine.finalize()


def materialize_note7_run(
    admission: ExecutableAdmission,
    operational_root: str | Path,
) -> Note7RunArtifacts:
    """Run one fresh, offline, deterministic materialization."""

    return asyncio.run(_materialize(admission, Path(operational_root)))


__all__ = [
    "Note7ExecutionError",
    "Note7FullRosterEngine",
    "Note7FullRosterRunner",
    "Note7FullRosterSimulator",
    "Note7RunArtifacts",
    "build_note7_run_manifest",
    "materialize_note7_run",
]
