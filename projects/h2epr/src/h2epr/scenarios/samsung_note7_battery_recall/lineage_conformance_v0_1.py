"""Deterministic conformance for the bounded Note7 remedy lineage.

This is not a simulator. It projects one fully exposed synthetic branch,
checks cross-hop provenance, records a fifteen-tick hash-chained trace, and
replays only the symbolic state needed for causal and result separation.
"""

from __future__ import annotations

import copy
import hashlib
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from masim.integrations.event_process import TraceWriter, canonical_sha256, replay_trace, validate_trace

from .lineage_v0_1 import (
    CONSUMER_ACTOR_ID,
    OUTLET_ACTOR_ID,
    REGIONAL_ACTOR_ID,
    SAMSUNG_ACTOR_ID,
    MessageDelivery,
    Note7LineageBinding,
    Note7LineageEnvironmentV0_1,
    PositiveNote7LineagePoliciesV0_1,
    ProductPostureResult,
    RemedyOfferDelivery,
    load_note7_lineage_binding,
)


CONFORMANCE_FORMAT = "h2epr.lineage-conformance.v0.1"
CONFORMANCE_ID = "conformance.h2epr.0481.samsung_regional_outlet_consumer.v0_1"
RUN_ID = "run.h2epr.0481.remedy_lineage.conformance.001"
BINDING_MANIFEST_SHA256 = "e97b0eda9a0f5d7abf5b9d0d9f6a4702787a03c0a637f93278ad6b1a6cd88e6b"
PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_BINDING_MANIFEST = PROJECT_ROOT / "agents/bindings/samsung_note7_battery_recall/samsung-regional-outlet-consumer-v0.1/manifest.json"


class Note7LineageConformanceError(ValueError):
    """A cross-hop, trace-order, or replay invariant failed."""


@dataclass(frozen=True)
class Note7LineageProjection:
    binding: Note7LineageBinding
    direction_observation: Mapping[str, Any]
    direction_action: Mapping[str, Any]
    direction_message: Mapping[str, Any]
    direction_delivery: MessageDelivery
    program_observation: Mapping[str, Any]
    program_action: Mapping[str, Any]
    program_message: Mapping[str, Any]
    program_delivery: MessageDelivery
    coordination_observation: Mapping[str, Any]
    coordination_action: Mapping[str, Any]
    coordination_message: Mapping[str, Any]
    coordination_delivery: MessageDelivery
    proposal_observation: Mapping[str, Any]
    proposal_action: Mapping[str, Any]
    proposal_message: Mapping[str, Any]
    proposal_delivery: MessageDelivery
    posture_observation: Mapping[str, Any]
    posture_action: Mapping[str, Any]
    posture_result: ProductPostureResult
    remedy_offer: RemedyOfferDelivery
    request_observation: Mapping[str, Any]
    request_action: Mapping[str, Any]
    request_message: Mapping[str, Any]
    request_delivery: MessageDelivery
    response_observation: Mapping[str, Any]
    response_action: Mapping[str, Any]
    response_message: Mapping[str, Any]
    response_delivery: MessageDelivery

    @property
    def observations(self) -> tuple[Mapping[str, Any], ...]:
        return (self.direction_observation, self.program_observation, self.coordination_observation, self.proposal_observation, self.posture_observation, self.request_observation, self.response_observation)

    @property
    def actions(self) -> tuple[Mapping[str, Any], ...]:
        return (self.direction_action, self.program_action, self.coordination_action, self.proposal_action, self.posture_action, self.request_action, self.response_action)

    @property
    def messages(self) -> tuple[Mapping[str, Any], ...]:
        return (self.direction_message, self.program_message, self.coordination_message, self.proposal_message, self.request_message, self.response_message)

    @property
    def deliveries(self) -> tuple[MessageDelivery, ...]:
        return (self.direction_delivery, self.program_delivery, self.coordination_delivery, self.proposal_delivery, self.request_delivery, self.response_delivery)


@dataclass(frozen=True)
class Note7LineageConformanceRun:
    manifest: Mapping[str, Any]
    initial_state: Mapping[str, Any]
    final_state: Mapping[str, Any]
    replayed_state: Mapping[str, Any]
    records: tuple[Mapping[str, Any], ...]
    run_seal: Mapping[str, Any]
    projection: Note7LineageProjection

    def trace_errors(self) -> list[str]:
        return validate_trace(self.records)


@dataclass(frozen=True)
class _Transition:
    state_path: str
    after: Any
    operation: str = "transition"


def _fail(code: str) -> None:
    raise Note7LineageConformanceError(code)


def _time(day: int, hour: int) -> dict[str, Any]:
    value = f"2016-09-{day:02d}T{hour:02d}:00:00+00:00"
    return {"lower": value, "upper": value, "precision": "exact_datetime", "timezone": "UTC", "uncertainty": "synthetic conformance coordinate"}


def load_conformance_binding(manifest_path: str | Path = DEFAULT_BINDING_MANIFEST, *, expected_manifest_sha256: str = BINDING_MANIFEST_SHA256) -> Note7LineageBinding:
    return load_note7_lineage_binding(manifest_path, expected_manifest_sha256=expected_manifest_sha256, project_root=PROJECT_ROOT)


def _observation(binding: Note7LineageBinding, action_key: str, suffix: str, values: Mapping[str, Any]) -> Mapping[str, Any]:
    return binding.project_observation(action_key, observation_id=f"observation.0481.{suffix}.001", values=values)


def _action(binding: Note7LineageBinding, decision, observation: Mapping[str, Any], *, suffix: str, tick: int, day: int, hour: int) -> Mapping[str, Any]:
    return binding.project_action(
        decision.action_key,
        intent_id=f"intent.0481.{suffix}.001",
        run_id=RUN_ID,
        logical_tick=tick,
        decision_ref=f"decision.0481.{suffix}.001",
        observation_refs=(observation["observation_id"],),
        semantic_parameters=decision.semantic_parameters,
        earliest_effect_time=_time(day, hour),
    )


def _message(binding: Note7LineageBinding, action_key: str, action: Mapping[str, Any], *, suffix: str, day: int, hour: int, correlations: Sequence[str]) -> Mapping[str, Any]:
    return binding.project_message(
        action_key,
        action,
        message_intent_id=f"message.0481.{suffix}.001",
        earliest_delivery_time=_time(day, hour),
        correlation_ids=(action["intent_id"], *correlations),
    )


def build_positive_note7_lineage(binding: Note7LineageBinding | None = None) -> Note7LineageProjection:
    selected = binding or load_conformance_binding()
    policies = PositiveNote7LineagePoliciesV0_1(selected)
    environment = Note7LineageEnvironmentV0_1(selected)

    direction_observation = _observation(selected, "samsung.issue_product_flow_direction", "samsung.direction_basis", {
        "investigation_update": "investigation.0481.synthetic.material_concern.v0",
        "product_flow_snapshot": "snapshot.0481.synthetic.product_flow.v0",
        "authority_or_partner_record": "authority_record.0481.synthetic.samsung_scope.v0",
        "intent_result_notice": "never_issued",
    })
    direction_decision = policies.decide_product_flow_direction(
        direction_observation,
        direction_id="direction.0481.synthetic.stop_sales.v0",
        direction_version=0,
        product_class_ref="product_class.0481.note7.original",
        action="stop_sales",
        jurisdiction_ref="jurisdiction.0481.singapore",
        timing_ref="time.0481.synthetic.tick.0",
        review_condition_ref="review.0481.direction.after_partner_delivery",
        expiry_time=_time(15, 23),
    )
    direction_action = _action(selected, direction_decision, direction_observation, suffix="samsung.direction", tick=0, day=2, hour=9)
    direction_message = _message(selected, direction_decision.action_key, direction_action, suffix="samsung_to_regional.direction", day=2, hour=10, correlations=("direction.0481.synthetic.stop_sales.v0",))
    direction_delivery = environment.deliver_message(direction_decision.action_key, direction_action, direction_message, route_id="route.0481.samsung_to_regional.direction", delivery_ref="delivery.0481.samsung_to_regional.direction.001", delivered_tick=1)

    program_observation = _observation(selected, "samsung.announce_replacement_program", "samsung.program_basis", {
        "investigation_update": "investigation.0481.synthetic.material_concern.v0",
        "product_flow_snapshot": "snapshot.0481.synthetic.product_flow.v0",
        "authority_or_partner_record": "partner_record.0481.synthetic.regional_route.v0",
        "intent_result_notice": "never_issued",
    })
    program_decision = policies.decide_replacement_program(
        program_observation,
        program_id="program.0481.synthetic.replacement.v0",
        program_version=0,
        product_class_ref="product_class.0481.note7.original",
        remedy_kind="replacement",
        eligibility_proposal_ref="eligibility_proposal.0481.synthetic.original_device",
        timing_ref="time.0481.synthetic.tick.2",
        uncertainty="bounded",
        review_condition_ref="review.0481.program.after_regional_delivery",
        expiry_time=_time(15, 23),
    )
    program_action = _action(selected, program_decision, program_observation, suffix="samsung.program", tick=2, day=2, hour=11)
    program_message = _message(selected, program_decision.action_key, program_action, suffix="samsung_to_regional.program", day=2, hour=12, correlations=(direction_action["intent_id"],))
    program_delivery = environment.deliver_message(program_decision.action_key, program_action, program_message, route_id="route.0481.samsung_to_regional.direction", delivery_ref="delivery.0481.samsung_to_regional.program.001", delivered_tick=3)

    coordination_observation = _observation(selected, "regional.coordinate_local_partner_response", "regional.coordination_basis", {
        "delivered_central_direction": program_message["message_intent_id"],
        "partner_response": "partner_response.0481.synthetic.not_yet_received",
        "local_inventory_observation": "inventory_observation.0481.synthetic.qualified_unknown",
        "intent_result_notice": "never_issued",
    })
    coordination_decision = policies.decide_partner_coordination(
        coordination_observation,
        direction_action=direction_action,
        direction_message=direction_message,
        direction_delivery=direction_delivery,
        program_action=program_action,
        program_message=program_message,
        program_delivery=program_delivery,
        coordination_id="coordination.0481.synthetic.outlet_response.v0",
        coordination_version=0,
        requested_action="prepare_exchange",
        jurisdiction_ref="jurisdiction.0481.singapore",
        timing_ref="time.0481.synthetic.tick.4",
        review_condition_ref="review.0481.coordination.after_outlet_delivery",
        expiry_time=_time(15, 23),
    )
    coordination_action = _action(selected, coordination_decision, coordination_observation, suffix="regional.coordination", tick=4, day=2, hour=13)
    coordination_message = _message(selected, coordination_decision.action_key, coordination_action, suffix="regional_to_outlet.coordination", day=2, hour=14, correlations=(direction_message["message_intent_id"], program_message["message_intent_id"]))
    coordination_delivery = environment.deliver_message(coordination_decision.action_key, coordination_action, coordination_message, route_id="route.0481.regional_to_outlet.coordination", delivery_ref="delivery.0481.regional_to_outlet.coordination.001", delivered_tick=5)

    proposal_observation = _observation(selected, "regional.propose_local_remedy", "regional.proposal_basis", {
        "delivered_central_direction": program_message["message_intent_id"],
        "local_authority_record": "authority_record.0481.synthetic.singapore_terms.v0",
        "partner_response": "partner_response.0481.synthetic.review_open",
        "local_inventory_observation": "inventory_observation.0481.synthetic.exchange_stock_qualified",
        "intent_result_notice": "never_issued",
    })
    proposal_decision = policies.decide_local_remedy(
        proposal_observation,
        coordination_action=coordination_action,
        coordination_message=coordination_message,
        coordination_delivery=coordination_delivery,
        proposal_id="proposal.0481.synthetic.local_exchange.v0",
        proposal_version=0,
        eligibility_proposal_ref="eligibility_proposal.0481.synthetic.original_device",
        remedy_kind="exchange",
        channel_ref="channel.0481.synthetic.singapore_outlet",
        timing_ref="time.0481.synthetic.tick.6",
        stock_qualification_ref="stock_qualification.0481.synthetic.not_guaranteed",
        uncertainty="bounded",
        review_condition_ref="review.0481.proposal.after_outlet_delivery",
        expiry_time=_time(15, 23),
    )
    proposal_action = _action(selected, proposal_decision, proposal_observation, suffix="regional.proposal", tick=6, day=2, hour=15)
    proposal_message = _message(selected, proposal_decision.action_key, proposal_action, suffix="regional_to_outlet.proposal", day=2, hour=16, correlations=(coordination_action["intent_id"], program_action["intent_id"]))
    proposal_delivery = environment.deliver_message(proposal_decision.action_key, proposal_action, proposal_message, route_id="route.0481.regional_to_outlet.coordination", delivery_ref="delivery.0481.regional_to_outlet.proposal.001", delivered_tick=7)

    posture_observation = _observation(selected, "outlet.set_local_product_posture", "outlet.posture_basis", {
        "delivered_product_direction": proposal_message["message_intent_id"],
        "delivered_authority_notice": "authority_notice.0481.synthetic.local_scope.v0",
        "local_inventory_observation": "inventory_observation.0481.synthetic.exchange_stock_qualified",
        "intent_result_notice": "never_issued",
    })
    posture_decision = policies.decide_outlet_posture(
        posture_observation,
        proposal_action=proposal_action,
        proposal_message=proposal_message,
        proposal_delivery=proposal_delivery,
        posture_id="posture.0481.synthetic.outlet_exchange.v0",
        posture_version=0,
        product_class_ref="product_class.0481.note7.original",
        posture="exchange",
        basis_refs=(proposal_message["message_intent_id"], proposal_delivery.delivery_ref),
        timing_ref="time.0481.synthetic.tick.8",
        review_condition_ref="review.0481.posture.after_adjudication",
        expiry_time=_time(15, 23),
    )
    posture_action = _action(selected, posture_decision, posture_observation, suffix="outlet.posture", tick=8, day=2, hour=17)
    posture_result = environment.adjudicate_product_posture(posture_action, result_id="result.0481.synthetic.outlet_posture.admitted.v0", result_version=0, status="admitted", produced_tick=9)
    remedy_offer = environment.deliver_remedy_offer(
        proposal_action,
        proposal_delivery,
        posture_result,
        offer_id="offer.0481.synthetic.exchange.v0",
        offer_version=0,
        offer_delivery_ref="delivery.0481.outlet_to_consumer.offer.001",
        delivered_tick=10,
    )

    request_observation = _observation(selected, "consumer.request_exchange_or_refund", "consumer.request_basis", {
        "local_device_experience": "device_experience.0481.synthetic.original_device_present",
        "delivered_safety_message": "safety_message.0481.synthetic.stop_use.delivered",
        "local_remedy_offer": remedy_offer.offer_id,
        "intent_result_notice": "never_issued",
    })
    request_decision = policies.decide_consumer_request(
        request_observation,
        offer=remedy_offer,
        request_id="request.0481.synthetic.exchange.v0",
        request_version=0,
        device_ref="device.0481.synthetic.consumer_original",
        selected_remedy="exchange",
        event_time_ref="time.0481.synthetic.tick.11",
        uncertainty="bounded",
        review_condition_ref="review.0481.request.after_outlet_delivery",
        expiry_time=_time(15, 23),
    )
    request_action = _action(selected, request_decision, request_observation, suffix="consumer.request", tick=11, day=2, hour=20)
    request_message = _message(selected, request_decision.action_key, request_action, suffix="consumer_to_outlet.request", day=2, hour=21, correlations=(remedy_offer.offer_id, remedy_offer.offer_delivery_ref))
    request_delivery = environment.deliver_message(request_decision.action_key, request_action, request_message, route_id="route.0481.consumer_to_outlet.remedy_request", delivery_ref="delivery.0481.consumer_to_outlet.request.001", delivered_tick=12)

    response_observation = _observation(selected, "outlet.respond_to_remedy_request", "outlet.response_basis", {
        "delivered_product_direction": proposal_message["message_intent_id"],
        "local_inventory_observation": "inventory_observation.0481.synthetic.exchange_stock_qualified",
        "consumer_request": request_message["message_intent_id"],
        "intent_result_notice": "never_issued",
    })
    response_decision = policies.decide_outlet_response(
        response_observation,
        request_action=request_action,
        request_message=request_message,
        request_delivery=request_delivery,
        posture_result=posture_result,
        response_id="response.0481.synthetic.request_acceptance.v0",
        response_version=0,
        stated_basis_ref="basis.0481.synthetic.request_and_posture",
        proposed_path="accepted_for_adjudication",
        uncertainty="bounded",
        review_condition_ref="review.0481.response.await_fulfillment",
        expiry_time=_time(15, 23),
    )
    response_action = _action(selected, response_decision, response_observation, suffix="outlet.response", tick=13, day=2, hour=22)
    response_message = _message(selected, response_decision.action_key, response_action, suffix="outlet_to_consumer.response", day=2, hour=23, correlations=(request_action["intent_id"], request_message["message_intent_id"]))
    response_delivery = environment.deliver_message(response_decision.action_key, response_action, response_message, route_id="route.0481.outlet_to_consumer.remedy_response", delivery_ref="delivery.0481.outlet_to_consumer.response.001", delivered_tick=14)

    projection = Note7LineageProjection(
        selected,
        direction_observation, direction_action, direction_message, direction_delivery,
        program_observation, program_action, program_message, program_delivery,
        coordination_observation, coordination_action, coordination_message, coordination_delivery,
        proposal_observation, proposal_action, proposal_message, proposal_delivery,
        posture_observation, posture_action, posture_result, remedy_offer,
        request_observation, request_action, request_message, request_delivery,
        response_observation, response_action, response_message, response_delivery,
    )
    validate_note7_lineage_projection(projection)
    return projection


def validate_note7_lineage_projection(projection: Note7LineageProjection) -> None:
    binding = projection.binding
    keyed_actions = tuple(zip(binding.actions, projection.actions))
    keyed_messages = (
        ("samsung.issue_product_flow_direction", projection.direction_action, projection.direction_message),
        ("samsung.announce_replacement_program", projection.program_action, projection.program_message),
        ("regional.coordinate_local_partner_response", projection.coordination_action, projection.coordination_message),
        ("regional.propose_local_remedy", projection.proposal_action, projection.proposal_message),
        ("consumer.request_exchange_or_refund", projection.request_action, projection.request_message),
        ("outlet.respond_to_remedy_request", projection.response_action, projection.response_message),
    )
    for action_key, action in keyed_actions:
        binding.validate_action(action_key, action)
    for action_key, action, message in keyed_messages:
        binding.validate_message(action_key, action, message)
    if tuple(action["logical_tick"] for action in projection.actions) != (0, 2, 4, 6, 8, 11, 13):
        _fail("NOTE7_CONFORMANCE_ACTION_ORDER_MISMATCH")
    expected_deliveries = (
        (projection.direction_delivery, projection.direction_action, projection.direction_message, REGIONAL_ACTOR_ID, 1),
        (projection.program_delivery, projection.program_action, projection.program_message, REGIONAL_ACTOR_ID, 3),
        (projection.coordination_delivery, projection.coordination_action, projection.coordination_message, OUTLET_ACTOR_ID, 5),
        (projection.proposal_delivery, projection.proposal_action, projection.proposal_message, OUTLET_ACTOR_ID, 7),
        (projection.request_delivery, projection.request_action, projection.request_message, OUTLET_ACTOR_ID, 12),
        (projection.response_delivery, projection.response_action, projection.response_message, CONSUMER_ACTOR_ID, 14),
    )
    for delivery, action, message, recipient, tick in expected_deliveries:
        if not delivery.delivered or delivery.action_intent_id != action["intent_id"] or delivery.message_intent_id != message["message_intent_id"] or delivery.recipient_id != recipient or delivery.delivered_tick != tick:
            _fail("NOTE7_CONFORMANCE_DELIVERY_GATE_MISMATCH")
    coordination = binding.semantic_values(projection.coordination_action)
    if coordination["direction_delivery_ref"] != projection.direction_delivery.delivery_ref or coordination["program_delivery_ref"] != projection.program_delivery.delivery_ref or coordination["source_message_refs"] != sorted((projection.direction_message["message_intent_id"], projection.program_message["message_intent_id"])):
        _fail("NOTE7_CONFORMANCE_COORDINATION_LINEAGE_MISMATCH")
    proposal = binding.semantic_values(projection.proposal_action)
    if proposal["coordination_delivery_ref"] != projection.coordination_delivery.delivery_ref or projection.coordination_delivery.delivered_tick >= projection.proposal_action["logical_tick"]:
        _fail("NOTE7_CONFORMANCE_PROPOSAL_LINEAGE_MISMATCH")
    posture = binding.semantic_values(projection.posture_action)
    result = projection.posture_result
    if result.action_intent_id != projection.posture_action["intent_id"] or result.posture_id != posture["posture_id"] or result.posture_version != posture["posture_version"] or result.product_class_ref != posture["product_class_ref"] or result.status != "admitted" or result.produced_tick != 9:
        _fail("NOTE7_CONFORMANCE_POSTURE_RESULT_MISMATCH")
    offer = projection.remedy_offer
    if (
        offer.proposal_action_intent_id != projection.proposal_action["intent_id"]
        or offer.proposal_id != proposal["proposal_id"]
        or offer.proposal_version != proposal["proposal_version"]
        or offer.posture_result_id != result.result_id
        or offer.consumer_actor_id != CONSUMER_ACTOR_ID
        or offer.route_id != "opening.0481.route.outlet-consumer"
        or offer.delivered_tick != 10
    ):
        _fail("NOTE7_CONFORMANCE_OFFER_LINEAGE_MISMATCH")
    request = binding.semantic_values(projection.request_action)
    if request["offer_id"] != offer.offer_id or request["offer_version"] != offer.offer_version or request["offer_delivery_ref"] != offer.offer_delivery_ref or offer.delivered_tick >= projection.request_action["logical_tick"]:
        _fail("NOTE7_CONFORMANCE_REQUEST_LINEAGE_MISMATCH")
    response = binding.semantic_values(projection.response_action)
    if response["request_id"] != request["request_id"] or response["request_version"] != request["request_version"] or response["request_message_ref"] != projection.request_message["message_intent_id"] or response["request_delivery_ref"] != projection.request_delivery.delivery_ref or response["posture_result_ref"] != result.result_id or projection.request_delivery.delivered_tick >= projection.response_action["logical_tick"]:
        _fail("NOTE7_CONFORMANCE_RESPONSE_LINEAGE_MISMATCH")
    forbidden_result_names = {"eligibility_result", "stock_result", "handoff_result", "payment_result", "completion_result", "exchange_result", "refund_result"}
    if any(forbidden_result_names.intersection(binding.semantic_values(action)) for action in projection.actions) or any(action["resource_offer_or_request"] for action in projection.actions):
        _fail("NOTE7_CONFORMANCE_RESULT_LAYER_MISMATCH")


def _decision_payload(decision_id: str, policy_id: str, action_key: str, commitments: Sequence[str], observation_id: str, action_id: str, message_ids: Sequence[str]) -> dict[str, Any]:
    return {"decision_id": decision_id, "decision_policy_id": policy_id, "action_key": action_key, "commitment_ids": list(commitments), "observation_refs": [observation_id], "action_intent_ids": [action_id], "message_intent_ids": list(message_ids), "exposure": "full_draft_exposed_conformance_only"}


def _prepare_deltas(state: Mapping[str, Any], disposition_id: str, parents: Sequence[str], transitions: Sequence[_Transition]) -> list[dict[str, Any]]:
    shadow = copy.deepcopy(dict(state))
    result: list[dict[str, Any]] = []
    for transition in transitions:
        if transition.state_path not in shadow or shadow[transition.state_path] == transition.after:
            _fail("NOTE7_CONFORMANCE_STATE_TRANSITION_INVALID")
        before_version = shadow["state_version"]
        after_version = before_version + 1
        delta_id = "delta." + canonical_sha256({"state_path": transition.state_path, "before": shadow[transition.state_path], "after": transition.after, "state_after_version": after_version, "disposition_id": disposition_id, "causal_parent_ids": list(parents)})[:48]
        delta = {"delta_id": delta_id, "disposition_id": disposition_id, "entity_id": "entity.h2epr.0481.lineage_state", "state_path": transition.state_path, "operation": transition.operation, "before": copy.deepcopy(shadow[transition.state_path]), "after": copy.deepcopy(transition.after), "unit": "state.symbolic", "state_before_version": before_version, "state_after_version": after_version, "invariant_checks": ["invariant.0481.lineage.prestate_exact"], "causal_parent_ids": list(parents)}
        result.append(delta)
        shadow[transition.state_path] = copy.deepcopy(transition.after)
        shadow["state_version"] = after_version
    return result


def _apply_delta(state: dict[str, Any], payload: Mapping[str, Any]) -> None:
    path = payload["state_path"]
    if path not in state or state[path] != payload["before"] or state["state_version"] != payload["state_before_version"]:
        _fail("NOTE7_CONFORMANCE_REPLAY_PRESTATE_MISMATCH")
    state[path] = copy.deepcopy(payload["after"])
    state["state_version"] = payload["state_after_version"]


def replay_note7_lineage_records(initial_state: Mapping[str, Any], records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return replay_trace(initial_state, records, _apply_delta)


def _record_deltas(writer: TraceWriter, state: dict[str, Any], tick: int, deltas: Sequence[Mapping[str, Any]]) -> None:
    for delta in deltas:
        _apply_delta(state, delta)
        writer.append("state_delta", tick, delta)


def _disposition(action: Mapping[str, Any], disposition_id: str, deltas: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {"disposition_id": disposition_id, "intent_id": action["intent_id"], "reducer_id": "reducer.h2epr.0481.lineage_conformance", "reducer_version": "v0_1", "status": "accepted", "reason_codes": ["reason.bounded_lineage_action_admitted"], "accepted_parameters": copy.deepcopy(list(action["parameters"]) + list(action["resource_offer_or_request"])), "rejected_parameters": [], "conflict_set_ids": [], "state_before_version": deltas[0]["state_before_version"], "state_after_version": deltas[-1]["state_after_version"], "delta_ids": [row["delta_id"] for row in deltas], "explicit_no_effect": False, "retry_policy": "none"}


def _record_action(writer: TraceWriter, state: dict[str, Any], *, tick: int, observation: Mapping[str, Any], action: Mapping[str, Any], policy_id: str, action_key: str, commitments: Sequence[str], message_ids: Sequence[str], transition: _Transition) -> None:
    writer.append("observation_delivered", tick, observation)
    writer.append("decision_recorded", tick, _decision_payload(action["decision_ref"], policy_id, action_key, commitments, observation["observation_id"], action["intent_id"], message_ids))
    writer.append("action_intent_created", tick, action)
    disposition_id = "action_disposition." + action["intent_id"]
    deltas = _prepare_deltas(state, disposition_id, (action["intent_id"],), (transition,))
    writer.append("action_disposition_recorded", tick, _disposition(action, disposition_id, deltas))
    _record_deltas(writer, state, tick, deltas)


def _record_message(writer: TraceWriter, binding: Note7LineageBinding, tick: int, action_key: str, message: Mapping[str, Any]) -> None:
    route = binding.routes[binding.actions[action_key].message_route_id]
    disposition = {"communication_disposition_id": "communication_disposition." + message["message_intent_id"], "message_intent_id": message["message_intent_id"], "run_id": message["run_id"], "logical_tick": tick, "sender_id": message["sender_id"], "recipient_ids": copy.deepcopy(message["recipient_ids"]), "requested_channel": message["channel"], "adjudicated_at": copy.deepcopy(message["created_at"]), "policy_id": binding.policies["POL-0481-ROUTE-01"], "policy_version": "0.1.0", "status": "accepted", "reason_codes": ["reason.exact_lineage_route_admitted"], "route_id": route.route_id, "message_id": "transport." + message["message_intent_id"], "terminal": True, "duplicate_of_message_intent_id": None}
    writer.append("message_intent_created", tick, message)
    writer.append("communication_disposition_recorded", tick, disposition)
    writer.append("message_sent", tick, {"message_intent_id": message["message_intent_id"], "message_id": disposition["message_id"], "route_id": route.route_id, "transport_status": "sent"})


def _record_delivery(writer: TraceWriter, state: dict[str, Any], tick: int, delivery: MessageDelivery, transition: _Transition) -> None:
    writer.append("message_delivered", tick, asdict(delivery))
    deltas = _prepare_deltas(state, "disposition." + delivery.delivery_ref, (delivery.message_intent_id, delivery.delivery_ref), (transition,))
    _record_deltas(writer, state, tick, deltas)


def _commit(writer: TraceWriter, state: Mapping[str, Any], tick: int) -> None:
    writer.append("tick_commit", tick, {"state_sha256": canonical_sha256(state), "state_version": state["state_version"]})
    writer.seal_tick(tick, state)


def run_note7_lineage_conformance(manifest_path: str | Path = DEFAULT_BINDING_MANIFEST, *, expected_manifest_sha256: str = BINDING_MANIFEST_SHA256) -> Note7LineageConformanceRun:
    binding = load_conformance_binding(manifest_path, expected_manifest_sha256=expected_manifest_sha256)
    projection = build_positive_note7_lineage(binding)
    implementation_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    preimage = {"format": CONFORMANCE_FORMAT, "conformance_id": CONFORMANCE_ID, "run_id": RUN_ID, "binding_release_id": binding.release_id, "binding_release_manifest_sha256": binding.release_manifest_sha256, "binding_sha256": binding.binding_sha256, "conformance_implementation_sha256": implementation_sha256, "actor_ids": list(binding.actor_ids), "action_keys": list(binding.actions), "route_ids": list(binding.routes), "logical_tick_count": 15, "state_delta_count": 15, "product_posture_result_count": 1, "remedy_offer_delivery_count": 1, "simulation_started": False, "full_configuration_execution_enabled": False, "held_out_or_clean_builder_claim": False, "post_seal_evaluation_performed": False, "historical_validity_claim": False, "scientific_validity_claim": False, "exposure": "full_draft_exposed_conformance_only"}
    manifest = dict(preimage)
    manifest["manifest_sha256"] = canonical_sha256(preimage)
    writer = TraceWriter(RUN_ID, manifest["manifest_sha256"])
    state: dict[str, Any] = {"state_version": 0, "direction_stage": "none", "program_stage": "none", "coordination_stage": "none", "proposal_stage": "none", "posture_stage": "none", "offer_stage": "none", "request_stage": "none", "response_stage": "none"}
    initial_state = copy.deepcopy(state)
    writer.append("scenario_identity_bound", 0, {"conformance_id": CONFORMANCE_ID, "manifest_sha256": manifest["manifest_sha256"], "binding_release_manifest_sha256": binding.release_manifest_sha256, "simulation_started": False, "validity_claim": "none"})
    policies = PositiveNote7LineagePoliciesV0_1
    action_rows = (
        (0, projection.direction_observation, projection.direction_action, projection.direction_message, "samsung.issue_product_flow_direction", policies.SAMSUNG_POLICY_ID, "direction_stage"),
        (2, projection.program_observation, projection.program_action, projection.program_message, "samsung.announce_replacement_program", policies.SAMSUNG_POLICY_ID, "program_stage"),
        (4, projection.coordination_observation, projection.coordination_action, projection.coordination_message, "regional.coordinate_local_partner_response", policies.REGIONAL_POLICY_ID, "coordination_stage"),
        (6, projection.proposal_observation, projection.proposal_action, projection.proposal_message, "regional.propose_local_remedy", policies.REGIONAL_POLICY_ID, "proposal_stage"),
    )
    delivery_rows = (
        (1, projection.direction_delivery, "direction_stage"),
        (3, projection.program_delivery, "program_stage"),
        (5, projection.coordination_delivery, "coordination_stage"),
        (7, projection.proposal_delivery, "proposal_stage"),
    )
    for tick in range(8):
        for row in action_rows:
            if row[0] == tick:
                _, observation, action, message, action_key, policy_id, state_path = row
                _record_action(writer, state, tick=tick, observation=observation, action=action, policy_id=policy_id, action_key=action_key, commitments=binding.actions[action_key].commitment_ids, message_ids=(message["message_intent_id"],), transition=_Transition(state_path, "issued"))
                _record_message(writer, binding, tick, action_key, message)
        for row in delivery_rows:
            if row[0] == tick:
                _record_delivery(writer, state, tick, row[1], _Transition(row[2], "delivered"))
        _commit(writer, state, tick)

    _record_action(writer, state, tick=8, observation=projection.posture_observation, action=projection.posture_action, policy_id=policies.OUTLET_POLICY_ID, action_key="outlet.set_local_product_posture", commitments=binding.actions["outlet.set_local_product_posture"].commitment_ids, message_ids=(), transition=_Transition("posture_stage", "issued"))
    _commit(writer, state, 8)
    writer.append("product_posture_result_produced", 9, asdict(projection.posture_result))
    _record_deltas(writer, state, 9, _prepare_deltas(state, "disposition." + projection.posture_result.result_id, (projection.posture_action["intent_id"], projection.posture_result.result_id), (_Transition("posture_stage", "admitted"),)))
    _commit(writer, state, 9)
    writer.append("remedy_offer_delivered", 10, asdict(projection.remedy_offer))
    _record_deltas(writer, state, 10, _prepare_deltas(state, "disposition." + projection.remedy_offer.offer_delivery_ref, (projection.posture_result.result_id, projection.remedy_offer.offer_delivery_ref), (_Transition("offer_stage", "delivered"),)))
    _commit(writer, state, 10)
    _record_action(writer, state, tick=11, observation=projection.request_observation, action=projection.request_action, policy_id=policies.CONSUMER_POLICY_ID, action_key="consumer.request_exchange_or_refund", commitments=binding.actions["consumer.request_exchange_or_refund"].commitment_ids, message_ids=(projection.request_message["message_intent_id"],), transition=_Transition("request_stage", "issued"))
    _record_message(writer, binding, 11, "consumer.request_exchange_or_refund", projection.request_message)
    _commit(writer, state, 11)
    _record_delivery(writer, state, 12, projection.request_delivery, _Transition("request_stage", "delivered"))
    _commit(writer, state, 12)
    _record_action(writer, state, tick=13, observation=projection.response_observation, action=projection.response_action, policy_id=policies.OUTLET_POLICY_ID, action_key="outlet.respond_to_remedy_request", commitments=binding.actions["outlet.respond_to_remedy_request"].commitment_ids, message_ids=(projection.response_message["message_intent_id"],), transition=_Transition("response_stage", "issued"))
    _record_message(writer, binding, 13, "outlet.respond_to_remedy_request", projection.response_message)
    _commit(writer, state, 13)
    _record_delivery(writer, state, 14, projection.response_delivery, _Transition("response_stage", "delivered_awaiting_fulfillment"))
    _commit(writer, state, 14)
    run_seal = writer.seal_run(state, (projection.request_action["intent_id"],), (OUTLET_ACTOR_ID,))
    errors = validate_trace(writer.records)
    if errors:
        _fail("NOTE7_CONFORMANCE_TRACE_INVALID:" + ",".join(errors))
    validate_note7_lineage_trace_semantics(writer.records)
    replayed = replay_note7_lineage_records(initial_state, writer.records)
    if replayed != state or sum(row["record_type"] == "state_delta" for row in writer.records) != 15:
        _fail("NOTE7_CONFORMANCE_REPLAY_MISMATCH")
    return Note7LineageConformanceRun(copy.deepcopy(manifest), copy.deepcopy(initial_state), copy.deepcopy(state), copy.deepcopy(replayed), tuple(copy.deepcopy(writer.records)), run_seal.to_dict(), projection)


def _position(records: Sequence[Mapping[str, Any]], record_type: str, predicate: Callable[[Mapping[str, Any]], bool]) -> tuple[int, int]:
    matches = [(index, row["logical_tick"]) for index, row in enumerate(records) if row.get("record_type") == record_type and isinstance(row.get("payload"), Mapping) and predicate(row["payload"])]
    if len(matches) != 1:
        _fail("NOTE7_CONFORMANCE_TRACE_EVENT_CARDINALITY_MISMATCH")
    return matches[0]


def validate_note7_lineage_trace_semantics(records: Sequence[Mapping[str, Any]]) -> None:
    specs = (
        ("direction_decision", "decision_recorded", lambda value: value.get("action_key") == "samsung.issue_product_flow_direction", 0),
        ("direction_delivery", "message_delivered", lambda value: value.get("delivery_ref") == "delivery.0481.samsung_to_regional.direction.001", 1),
        ("program_decision", "decision_recorded", lambda value: value.get("action_key") == "samsung.announce_replacement_program", 2),
        ("program_delivery", "message_delivered", lambda value: value.get("delivery_ref") == "delivery.0481.samsung_to_regional.program.001", 3),
        ("coordination_decision", "decision_recorded", lambda value: value.get("action_key") == "regional.coordinate_local_partner_response", 4),
        ("coordination_delivery", "message_delivered", lambda value: value.get("delivery_ref") == "delivery.0481.regional_to_outlet.coordination.001", 5),
        ("proposal_decision", "decision_recorded", lambda value: value.get("action_key") == "regional.propose_local_remedy", 6),
        ("proposal_delivery", "message_delivered", lambda value: value.get("delivery_ref") == "delivery.0481.regional_to_outlet.proposal.001", 7),
        ("posture_decision", "decision_recorded", lambda value: value.get("action_key") == "outlet.set_local_product_posture", 8),
        ("posture_result", "product_posture_result_produced", lambda value: value.get("result_id") == "result.0481.synthetic.outlet_posture.admitted.v0", 9),
        ("offer_delivery", "remedy_offer_delivered", lambda value: value.get("offer_delivery_ref") == "delivery.0481.outlet_to_consumer.offer.001", 10),
        ("consumer_request", "decision_recorded", lambda value: value.get("action_key") == "consumer.request_exchange_or_refund", 11),
        ("request_delivery", "message_delivered", lambda value: value.get("delivery_ref") == "delivery.0481.consumer_to_outlet.request.001", 12),
        ("outlet_response", "decision_recorded", lambda value: value.get("action_key") == "outlet.respond_to_remedy_request", 13),
        ("response_delivery", "message_delivered", lambda value: value.get("delivery_ref") == "delivery.0481.outlet_to_consumer.response.001", 14),
    )
    positions: list[int] = []
    for _, record_type, predicate, tick in specs:
        position, actual_tick = _position(records, record_type, predicate)
        if actual_tick != tick:
            _fail("NOTE7_CONFORMANCE_TRACE_EVENT_TICK_MISMATCH")
        positions.append(position)
    if positions != sorted(positions):
        _fail("NOTE7_CONFORMANCE_TRACE_CAUSAL_ORDER_MISMATCH")
    if not records or records[-1].get("record_type") != "run_seal":
        _fail("NOTE7_CONFORMANCE_RUN_SEAL_MISSING")
    payload = records[-1].get("payload")
    if tuple(payload.get("unresolved_intent_ids", ())) != ("intent.0481.consumer.request.001",) or tuple(payload.get("unresolved_recipient_ids", ())) != (OUTLET_ACTOR_ID,):
        _fail("NOTE7_CONFORMANCE_UNRESOLVED_BOUNDARY_MISMATCH")


__all__ = [
    "BINDING_MANIFEST_SHA256",
    "CONFORMANCE_FORMAT",
    "CONFORMANCE_ID",
    "DEFAULT_BINDING_MANIFEST",
    "RUN_ID",
    "Note7LineageConformanceError",
    "Note7LineageConformanceRun",
    "Note7LineageProjection",
    "build_positive_note7_lineage",
    "load_conformance_binding",
    "replay_note7_lineage_records",
    "run_note7_lineage_conformance",
    "validate_note7_lineage_projection",
    "validate_note7_lineage_trace_semantics",
]
