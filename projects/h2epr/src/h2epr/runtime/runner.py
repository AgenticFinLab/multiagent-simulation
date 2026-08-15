"""G3-only offline Rule canary assembly and execution entry point."""

from __future__ import annotations

import asyncio
import copy
import json
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterable, Mapping

from masim.integrations.event_process import (
    ActionDisposition,
    ActionIntent,
    AppendOnlyTransport,
    AuthoritativeReducer,
    MessageIntent,
    ObservationEnvelope,
    StateDelta,
    TraceWriter,
    canonical_bytes,
    canonical_sha256,
    replay_trace,
    validate_trace,
)
from masim.simulator.base import SimulationConfig
from masim.simulator.phased import NAMED_BARRIERS, PhasedSimulationRunner, PhasedSimulator

from h2epr.world import (
    clamp_basis_points,
    neighbor_stress,
    next_confidence,
    next_withdrawal_pressure,
    pro_rata_floor_then_seeded_remainder,
)

from .adapter import ACTOR_IDS, AcceptedRunInput, build_accepted_run_input
from .detectors import P007Detector
from .participant import RuleParticipantPersona


RESOURCE_OWNERS = (
    "jp_morgan",
    "knickerbocker_trust",
    "member_banks_cohort",
    "nych",
    "other_trusts_cohort",
)


def _configure_local_only_ray_environment() -> None:
    os.environ["RAY_ENABLE_WINDOWS_OR_OSX_CLUSTER"] = "0"
    os.environ["RAY_USAGE_STATS_ENABLED"] = "0"


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value) + b"\n")


def _delta(
    intent_id: str,
    entity_id: str,
    field_name: str,
    before: Any,
    after: Any,
    delta_class: str,
    index: int,
) -> StateDelta | None:
    if before == after:
        return None
    return StateDelta(
        f"delta.{intent_id}.{index:04d}",
        intent_id,
        entity_id,
        field_name,
        before,
        after,
        delta_class,
    )


def _apply_delta_to_state(state: dict[str, Any], payload: Mapping[str, Any]) -> None:
    entity_id = payload["entity_id"]
    field_name = payload["field_name"]
    if entity_id == "__world__":
        target = state
    else:
        target = state["actors"][entity_id]
    if target[field_name] != payload["before"]:
        raise ValueError("replay_delta_before_mismatch")
    target[field_name] = payload["after"]


class H2EPRWorldReducer:
    """Event-specific effects injected into the domain-neutral authority shell."""

    def __init__(self, action_spaces: Mapping[str, tuple[str, ...]]) -> None:
        self.action_spaces = {key: set(value) for key, value in action_spaces.items()}

    def apply_batch(
        self,
        state: dict[str, Any],
        intents: tuple[ActionIntent, ...],
        run_seed: int,
        logical_tick: int,
    ) -> tuple[list[ActionDisposition], list[StateDelta]]:
        dispositions: list[ActionDisposition] = []
        deltas: list[StateDelta] = []
        accepted_support_by_recipient = {owner: 0 for owner in RESOURCE_OWNERS}
        unmet_withdrawal_by_owner = {owner: 0 for owner in RESOURCE_OWNERS}
        valid: list[ActionIntent] = []
        for intent in intents:
            reason = self._validate_intent(intent, state)
            if reason:
                dispositions.append(
                    ActionDisposition(
                        f"ad.{intent.intent_id}", intent.intent_id, logical_tick, "rejected", reason
                    )
                )
            else:
                valid.append(intent)

        withdrawal_by_owner: dict[str, dict[str, int]] = {}
        support_by_provider: dict[str, dict[str, int]] = {}
        for intent in valid:
            params = intent.parameters
            if intent.action_type == "withdraw_resource":
                withdrawal_by_owner.setdefault(params["resource_owner_id"], {})[intent.intent_id] = params["amount_bp"]
            elif intent.action_type == "offer_or_provide_resource":
                support_by_provider.setdefault(intent.actor_id, {})[intent.intent_id] = params["amount_bp"]

        accepted_amounts: dict[str, int] = {}
        for owner, claims in sorted(withdrawal_by_owner.items()):
            accepted_amounts.update(
                pro_rata_floor_then_seeded_remainder(
                    state["actors"][owner]["liquid_resource_bp"],
                    claims,
                    run_seed=run_seed,
                    logical_tick=logical_tick,
                )
            )
        provisional_support_amounts: dict[str, int] = {}
        for provider, claims in sorted(support_by_provider.items()):
            available = max(0, state["actors"][provider]["liquid_resource_bp"] - 3000)
            provisional_support_amounts.update(
                pro_rata_floor_then_seeded_remainder(
                    available,
                    claims,
                    run_seed=run_seed,
                    logical_tick=logical_tick,
                )
            )
        support_by_recipient: dict[str, dict[str, int]] = {}
        for intent in valid:
            if intent.action_type == "offer_or_provide_resource":
                support_by_recipient.setdefault(intent.parameters["recipient_id"], {})[
                    intent.intent_id
                ] = provisional_support_amounts[intent.intent_id]
        for recipient, claims in sorted(support_by_recipient.items()):
            headroom = max(0, 10000 - state["actors"][recipient]["liquid_resource_bp"])
            accepted_amounts.update(
                pro_rata_floor_then_seeded_remainder(
                    headroom,
                    claims,
                    run_seed=run_seed,
                    logical_tick=logical_tick,
                )
            )

        for intent in valid:
            params = intent.parameters
            owned_delta_ids: list[str] = []
            if intent.action_type == "withdraw_resource":
                owner = params["resource_owner_id"]
                accepted = accepted_amounts[intent.intent_id]
                unmet_withdrawal_by_owner[owner] += params["amount_bp"] - accepted
                if accepted:
                    before = state["actors"][owner]["liquid_resource_bp"]
                    after = before - accepted
                    item = _delta(intent.intent_id, owner, "liquid_resource_bp", before, after, "withdrawal_sink", len(deltas))
                    if item:
                        state["actors"][owner]["liquid_resource_bp"] = after
                        deltas.append(item)
                        owned_delta_ids.append(item.delta_id)
                    before_demand = state["withdrawal_demand_bp"]
                    after_demand = before_demand - accepted
                    item = _delta(intent.intent_id, "__world__", "withdrawal_demand_bp", before_demand, after_demand, "withdrawal_sink", len(deltas))
                    if item:
                        state["withdrawal_demand_bp"] = after_demand
                        deltas.append(item)
                        owned_delta_ids.append(item.delta_id)
            elif intent.action_type == "offer_or_provide_resource":
                recipient = params["recipient_id"]
                accepted = accepted_amounts[intent.intent_id]
                if accepted:
                    source_before = state["actors"][intent.actor_id]["liquid_resource_bp"]
                    source_after = source_before - accepted
                    target_before = state["actors"][recipient]["liquid_resource_bp"]
                    target_after = target_before + accepted
                    for entity, before, after in (
                        (intent.actor_id, source_before, source_after),
                        (recipient, target_before, target_after),
                    ):
                        item = _delta(intent.intent_id, entity, "liquid_resource_bp", before, after, "support_transfer", len(deltas))
                        if item:
                            state["actors"][entity]["liquid_resource_bp"] = after
                            deltas.append(item)
                            owned_delta_ids.append(item.delta_id)
                    accepted_support_by_recipient[recipient] += accepted
            elif intent.action_type == "change_operational_status":
                before = state["actors"][intent.actor_id]["operational_status"]
                after = params["target_status"]
                item = _delta(intent.intent_id, intent.actor_id, "operational_status", before, after, "operational_transition", len(deltas))
                if item:
                    state["actors"][intent.actor_id]["operational_status"] = after
                    deltas.append(item)
                    owned_delta_ids.append(item.delta_id)
            dispositions.append(
                ActionDisposition(
                    f"ad.{intent.intent_id}",
                    intent.intent_id,
                    logical_tick,
                    "accepted",
                    "accepted_by_authoritative_reducer",
                    tuple(owned_delta_ids),
                )
            )

        p006_intents = {item.actor_id: item.intent_id for item in valid}
        snapshot = copy.deepcopy(state)
        weights_by_owner: dict[str, dict[str, int]] = {owner: {} for owner in RESOURCE_OWNERS}
        for source, target, weight in state["exposures"]:
            weights_by_owner[source][target] = weight
        for owner in RESOURCE_OWNERS:
            actor = state["actors"][owner]
            prior = snapshot["actors"][owner]
            neighbor_values = {
                target: 10000 - snapshot["actors"][target]["liquid_resource_bp"]
                for target in weights_by_owner[owner]
            }
            observed_neighbor = neighbor_stress(weights_by_owner[owner], neighbor_values)
            updates = {
                "resource_stress_bp": 10000 - actor["liquid_resource_bp"],
                "withdrawal_pressure_bp": next_withdrawal_pressure(
                    prior["withdrawal_pressure_bp"],
                    prior["confidence_index_bp"],
                    observed_neighbor,
                    accepted_support_by_recipient[owner],
                ),
                "confidence_index_bp": next_confidence(
                    prior["confidence_index_bp"],
                    accepted_support_by_recipient[owner],
                    unmet_withdrawal_by_owner[owner],
                    observed_neighbor,
                ),
            }
            source_intent = p006_intents.get(owner, f"system.p006.{logical_tick}.{owner}")
            for field_name, after in updates.items():
                after = clamp_basis_points(after)
                before = actor[field_name]
                item = _delta(source_intent, owner, field_name, before, after, "p006_recomputed", len(deltas))
                if item:
                    actor[field_name] = after
                    deltas.append(item)
                    # System-derived deltas must be owned by an accepted actor intent.
                    matching = next((disp for disp in dispositions if disp.intent_id == source_intent), None)
                    if matching:
                        index = dispositions.index(matching)
                        dispositions[index] = ActionDisposition(
                            matching.disposition_id,
                            matching.intent_id,
                            matching.logical_tick,
                            matching.status,
                            matching.reason_code,
                            matching.state_delta_ids + (item.delta_id,),
                        )
                    else:
                        # All owners are actors and emit one primary intent each tick.
                        raise AssertionError("p006_source_intent_missing")
        return sorted(dispositions, key=lambda item: item.intent_id), deltas

    def _validate_intent(self, intent: ActionIntent, state: Mapping[str, Any]) -> str | None:
        if intent.actor_id not in self.action_spaces:
            return "unknown_actor"
        if intent.action_type not in self.action_spaces[intent.actor_id]:
            return "action_not_in_declared_space"
        params = intent.parameters
        if intent.action_type == "withdraw_resource":
            if params.get("resource_owner_id") not in RESOURCE_OWNERS or not isinstance(params.get("amount_bp"), int) or params["amount_bp"] <= 0:
                return "invalid_withdrawal_parameters"
        elif intent.action_type == "offer_or_provide_resource":
            if params.get("recipient_id") not in RESOURCE_OWNERS or not isinstance(params.get("amount_bp"), int) or params["amount_bp"] <= 0:
                return "invalid_support_parameters"
        elif intent.action_type == "change_operational_status":
            if params.get("target_status") not in {"open", "restricted", "closed"}:
                return "invalid_operational_status"
        elif intent.action_type == "request_support":
            if params.get("recipient_id") not in RESOURCE_OWNERS or params.get("amount_bp") != 1000:
                return "invalid_support_request"
        return None


class H2EPRCanaryEngine:
    def __init__(self, accepted: AcceptedRunInput, output_root: Path, *, actor_submission_order: str = "canonical") -> None:
        self.accepted = accepted
        self.output_root = output_root
        self.actor_submission_order = actor_submission_order
        self.logical_ticks = tuple(range(1, 42))
        self.handles: dict[str, Any] = {}
        self.tick_results: dict[int, dict[str, Any]] = {}
        self.reducer = AuthoritativeReducer(
            accepted.initial_state,
            H2EPRWorldReducer(accepted.action_spaces).apply_batch,
        )
        self.transport = AppendOnlyTransport(accepted.event_bundle["communication_routes"])
        self.trace = TraceWriter(accepted.run_manifest["run_id"], accepted.run_manifest["manifest_sha256"])
        exposures = [(source, target) for source, target, _ in accepted.initial_state["exposures"]]
        self.detector = P007Detector(exposures, RESOURCE_OWNERS)
        self.annotations: list[dict[str, Any]] = []
        self._coordination_emitted = False
        self._latest_support_failed: set[str] = set()
        self._ray_started_here = False

    def launch_participants(self) -> dict[str, Any]:
        _configure_local_only_ray_environment()
        import ray

        if not ray.is_initialized():
            ray_root = self.output_root / "operational" / "ray"
            ray_root.mkdir(parents=True, exist_ok=True)
            ray.init(
                address=None,
                num_cpus=1,
                num_gpus=0,
                include_dashboard=False,
                log_to_driver=False,
                runtime_env={"pip": [], "env_vars": {}},
                _node_ip_address="127.0.0.1",
                _temp_dir=str(ray_root),
            )
            self._ray_started_here = True
        RemotePersona = ray.remote(num_cpus=0.1, num_gpus=0)(RuleParticipantPersona)
        run_id = self.accepted.run_manifest["run_id"]
        seed = self.accepted.row["run_seed"]
        return {
            actor_id: RemotePersona.remote(
                {
                    "name": actor_id,
                    "identity": actor_id,
                    "steps_per_turn": 1,
                    "extras": {
                        "allowed_actions": list(self.accepted.action_spaces[actor_id]),
                        "run_id": run_id,
                        "run_seed": seed,
                    },
                }
            )
            for actor_id in ACTOR_IDS
        }

    async def setup(self, handles: Mapping[str, Any]) -> None:
        import ray

        self.handles = dict(handles)
        ray.get([self.handles[actor].initialize.remote() for actor in sorted(self.handles)])

    def _prior_state(self, actor_id: str) -> dict[str, Any]:
        unresolved_message_ids, _ = self.transport.unresolved()
        unresolved_actors = sorted(
            {
                self.transport._intents[item].sender_id
                for item in unresolved_message_ids
                if self.transport._intents[item].message_kind == "support_request"
            }
        )
        return {
            "unresolved_request_actor_ids": unresolved_actors,
            "latest_support_failed": actor_id in self._latest_support_failed,
            "coordination_emitted": self._coordination_emitted,
        }

    async def run_tick(self, logical_tick: int, barriers: tuple[str, ...]) -> dict[str, Any]:
        import ray

        if barriers != NAMED_BARRIERS:
            raise ValueError("named_barrier_order_mismatch")
        state = self.reducer.state
        prestate_hash = canonical_sha256(state)
        date_value = (date(1907, 10, 21) + timedelta(days=logical_tick - 1)).isoformat()
        self.trace.append("tick_open", logical_tick, {"logical_date": date_value, "physical_masim_round": logical_tick, "execution_level": 0})

        _, due_dispositions = self.transport.route_due(logical_tick)
        for item in due_dispositions:
            self.trace.append("message_disposition", logical_tick, item.to_dict())
        delivered_by_actor = {
            actor_id: self.transport.consume(actor_id, logical_tick)
            for actor_id in ACTOR_IDS
        }
        for actor_id, delivered in delivered_by_actor.items():
            if any(item["message_kind"] in {"support_denial"} for item in delivered):
                self._latest_support_failed.add(actor_id)

        observations = {
            actor_id: ObservationEnvelope(
                actor_id,
                logical_tick,
                logical_tick,
                0,
                state["state_version"],
                prestate_hash,
                copy.deepcopy(state),
                copy.deepcopy(state["actors"][actor_id]),
                tuple(copy.deepcopy(delivered_by_actor[actor_id])),
                self._prior_state(actor_id),
            ).to_dict()
            for actor_id in ACTOR_IDS
        }
        for actor_id in ACTOR_IDS:
            self.trace.append("observation", logical_tick, observations[actor_id])

        submission = list(ACTOR_IDS)
        if self.actor_submission_order == "reverse":
            submission.reverse()
        futures = {actor_id: self.handles[actor_id].operate.remote(observations[actor_id]) for actor_id in submission}
        raw_results = ray.get(list(futures.values()))
        results = {item["actor_id"]: item for item in raw_results}
        if set(results) != set(ACTOR_IDS):
            raise RuntimeError("participant_result_universe_mismatch")
        action_intents: list[ActionIntent] = []
        message_intents: list[MessageIntent] = []
        for actor_id in ACTOR_IDS:
            result = results[actor_id]
            if result["operation_count"] != logical_tick:
                raise RuntimeError("participant_operation_cardinality_mismatch")
            decision = copy.deepcopy(result["decision_record"])
            action = ActionIntent(**decision["action_intent"])
            messages = [MessageIntent(**item) for item in decision["message_intents"]]
            if action.actor_id != actor_id or any(item.sender_id != actor_id or item.source_action_intent_id != action.intent_id for item in messages):
                raise RuntimeError("participant_intent_lineage_mismatch")
            action_intents.append(action)
            message_intents.extend(messages)
            self.trace.append("action_intent", logical_tick, action.to_dict())
            for message in messages:
                self.trace.append("message_intent", logical_tick, message.to_dict())

        reducer_result = self.reducer.reduce(
            action_intents,
            logical_tick=logical_tick,
            run_seed=self.accepted.row["run_seed"],
        )
        disposition_by_intent = {item.intent_id: item for item in reducer_result.dispositions}
        accepted_messages = [
            item for item in message_intents
            if disposition_by_intent[item.source_action_intent_id].status == "accepted"
        ]
        message_dispositions = self.transport.submit(accepted_messages, logical_tick=logical_tick)
        for disposition in reducer_result.dispositions:
            payload = disposition.to_dict()
            payload["action_type"] = next(item.action_type for item in action_intents if item.intent_id == disposition.intent_id)
            self.trace.append("action_disposition", logical_tick, payload)
            if payload["action_type"] == "coordinate_collective_action" and disposition.status == "accepted":
                self._coordination_emitted = True
        for disposition in message_dispositions:
            self.trace.append("message_disposition", logical_tick, disposition.to_dict())
        for delta in reducer_result.deltas:
            self.trace.append("state_delta", logical_tick, delta.to_dict())
        self.trace.append(
            "tick_commit",
            logical_tick,
            {
                "state_version": reducer_result.state["state_version"],
                "state_sha256": reducer_result.poststate_sha256,
                "prestate_sha256": reducer_result.prestate_sha256,
            },
        )
        unresolved_ids, unresolved_recipients = self.transport.unresolved()
        enriched_dispositions = []
        by_action = {item.intent_id: item.action_type for item in action_intents}
        for item in reducer_result.dispositions:
            payload = item.to_dict()
            payload["action_type"] = by_action[item.intent_id]
            enriched_dispositions.append(payload)
        annotations, stage = self.detector.detect(
            logical_tick,
            reducer_result.state,
            enriched_dispositions,
            [item.to_dict() for item in reducer_result.deltas],
            unresolved_ids,
        )
        for annotation in annotations:
            self.trace.append("generated_annotation", logical_tick, annotation)
        self.annotations.extend(annotations)
        if stage:
            self.trace.append("generated_stage_first_hit", logical_tick, {"stage": stage, "provenance": "generated_simulation_trace_only"})
        tick_seal = self.trace.seal_tick(logical_tick, reducer_result.state)
        result = {
            "logical_tick": logical_tick,
            "logical_date": date_value,
            "prestate_sha256": prestate_hash,
            "poststate_sha256": reducer_result.poststate_sha256,
            "action_intent_count": len(action_intents),
            "message_intent_count": len(message_intents),
            "tick_seal_sha256": tick_seal.seal_sha256,
        }
        self.tick_results[logical_tick] = result
        return result

    async def shutdown(self) -> None:
        import ray

        try:
            if self.handles:
                ray.get([handle.shutdown.remote() for handle in self.handles.values()], timeout=30)
                for handle in self.handles.values():
                    ray.kill(handle, no_restart=True)
        finally:
            if self._ray_started_here and ray.is_initialized():
                ray.shutdown()

    def phase_execute(self, round_num: int, level_handles: Mapping[str, Any]) -> dict[str, Any]:
        return {"round": round_num, "handles": sorted(level_handles)}

    def phase_collect(self, execute_result: Mapping[str, Any]) -> dict[str, Any]:
        return dict(execute_result)

    def phase_dispatch(self, all_info_lists: list[list[dict[str, Any]]]) -> None:
        if all_info_lists:
            raise ValueError("legacy_dispatch_not_used_by_phased_runtime")

    def get_tick_result(self, logical_tick: int) -> dict[str, Any] | None:
        return copy.deepcopy(self.tick_results.get(logical_tick))

    def finalize(self) -> dict[str, Any]:
        state = self.reducer.state
        unresolved_ids, unresolved_recipients = self.transport.unresolved()
        run_seal = self.trace.seal_run(state, unresolved_ids, unresolved_recipients)
        trace_errors = validate_trace(self.trace.records)
        if trace_errors:
            raise RuntimeError("trace_validation_failed:" + ",".join(trace_errors))
        replayed = replay_trace(self.accepted.initial_state, self.trace.records, _apply_delta_to_state)
        if replayed != state:
            raise RuntimeError("replay_final_state_mismatch")
        _write_json(self.output_root / "run_manifest.json", self.accepted.run_manifest)
        trace_path = self.output_root / "simulation_trace.jsonl"
        trace_path.write_bytes(b"".join(canonical_bytes(row) + b"\n" for row in self.trace.records))
        _write_json(self.output_root / "final_state.json", state)
        _write_json(self.output_root / "p007_annotations.json", self.annotations)
        _write_json(self.output_root / "tick_seals.json", [item["payload"] for item in self.trace.records if item["record_type"] == "tick_seal"])
        _write_json(self.output_root / "run_seal.json", run_seal.to_dict())
        replay_receipt = {
            "status": "pass",
            "run_id": self.accepted.run_manifest["run_id"],
            "record_count": len(self.trace.records),
            "tick_count": len(self.logical_ticks),
            "final_state_sha256": canonical_sha256(state),
            "replayed_state_sha256": canonical_sha256(replayed),
            "trace_errors": [],
        }
        _write_json(self.output_root / "replay_receipt.json", replay_receipt)
        return {
            "run_id": self.accepted.run_manifest["run_id"],
            "manifest_sha256": self.accepted.run_manifest["manifest_sha256"],
            "run_seal_sha256": run_seal.seal_sha256,
            "final_state_sha256": canonical_sha256(state),
            "trace_sha256": canonical_sha256(self.trace.records),
            "record_count": len(self.trace.records),
            "tick_count": len(self.logical_ticks),
            "unresolved_intent_ids": list(unresolved_ids),
            "unresolved_recipient_ids": list(unresolved_recipients),
        }


class H2EPRSimulator(PhasedSimulator):
    """Project binding for the generic paired phased simulator."""


class H2EPRSimulationRunner(PhasedSimulationRunner):
    simulator_class = H2EPRSimulator


async def _run_case_async(
    approved_root: Path,
    case_id: str,
    output_root: Path,
    *,
    actor_submission_order: str = "canonical",
) -> dict[str, Any]:
    if output_root.exists():
        raise FileExistsError("output_root_must_be_fresh")
    accepted = build_accepted_run_input(approved_root, case_id, runtime_config={})
    output_root.mkdir(parents=True)
    engine = H2EPRCanaryEngine(accepted, output_root, actor_submission_order=actor_submission_order)
    config = SimulationConfig(
        setting={
            "name": "h2epr_g3_offline_rule_canary",
            "record_path": str(output_root / "operational"),
            "round_history_limit": 50,
            "phased_engine_factory": lambda: engine,
        },
        ray={
            "address": None,
            "num_cpus": 1,
            "num_gpus": 0,
            "include_dashboard": False,
            "log_to_driver": False,
            "runtime_env": {"pip": [], "env_vars": {}},
        },
        players={},
        topology={},
        environment={},
        communication={},
        knowledge={},
        simulation_id=accepted.run_manifest["run_id"],
    )
    runner = H2EPRSimulationRunner(config)
    try:
        results = await runner.execute()
        if len(results) != 41:
            raise RuntimeError("logical_tick_count_mismatch")
        return engine.finalize()
    except Exception:
        # Runner.execute already calls engine shutdown through the simulator.
        raise


def run_case(
    approved_root: Path,
    case_id: str,
    output_root: Path,
    *,
    actor_submission_order: str = "canonical",
) -> dict[str, Any]:
    return asyncio.run(
        _run_case_async(
            approved_root,
            case_id,
            output_root,
            actor_submission_order=actor_submission_order,
        )
    )
