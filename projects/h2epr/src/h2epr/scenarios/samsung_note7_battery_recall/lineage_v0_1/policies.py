"""Positive participant decisions for the bounded Note7 remedy lineage."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .binding import Note7LineageBinding, Note7LineageBindingError
from .environment import MessageDelivery, ProductPostureResult, RemedyOfferDelivery


SAMSUNG_ACTOR_ID = "actor.0481.interface.samsung-crisis"
REGIONAL_ACTOR_ID = "actor.0481.unit.samsung-regional-singapore"
OUTLET_ACTOR_ID = "actor.0481.unit.outlet-singapore-channel"
CONSUMER_ACTOR_ID = "actor.0481.unit.consumer-primary"

_REOPENING = {"never_issued", "failed", "expired", "cancelled", "superseded"}


def _value(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise Note7LineageBindingError(f"NOTE7_LINEAGE_POLICY_VALUE_INVALID:{label}")
    return value


def _version(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise Note7LineageBindingError(f"NOTE7_LINEAGE_POLICY_VALUE_INVALID:{label}")
    return value


def _sorted(values: Sequence[str], label: str) -> list[str]:
    result = [_value(item, label) for item in values]
    if not result or len(result) != len(set(result)):
        raise Note7LineageBindingError(f"NOTE7_LINEAGE_POLICY_VALUE_INVALID:{label}")
    return sorted(result)


def _delivery(delivery: MessageDelivery, action: Mapping[str, Any], message: Mapping[str, Any], recipient: str, label: str) -> None:
    if not delivery.delivered or delivery.action_intent_id != action["intent_id"] or delivery.message_intent_id != message["message_intent_id"] or delivery.recipient_id != recipient:
        raise Note7LineageBindingError(f"NOTE7_LINEAGE_REQUIRED_DELIVERY_MISSING:{label}")


def _reopening(value: str, label: str) -> None:
    if value not in _REOPENING:
        raise Note7LineageBindingError(f"NOTE7_LINEAGE_ACTIVE_EQUIVALENT_INTENT:{label}")


@dataclass(frozen=True)
class Note7LineageDecision:
    decision_policy_id: str
    action_key: str
    commitment_ids: tuple[str, ...]
    semantic_parameters: Mapping[str, Any]


class PositiveNote7LineagePoliciesV0_1:
    """One deterministic synthetic branch for four selected participants."""

    SAMSUNG_POLICY_ID = "h2epr.decision.0481.samsung.initial_remedy.v0_1"
    REGIONAL_POLICY_ID = "h2epr.decision.0481.regional.coordinate_remedy.v0_1"
    OUTLET_POLICY_ID = "h2epr.decision.0481.outlet.posture_and_response.v0_1"
    CONSUMER_POLICY_ID = "h2epr.decision.0481.consumer.request_remedy.v0_1"

    def __init__(self, binding: Note7LineageBinding) -> None:
        self.binding = binding

    def decide_product_flow_direction(self, observation: Mapping[str, Any], *, direction_id: str, direction_version: int, product_class_ref: str, action: str, jurisdiction_ref: str, timing_ref: str, review_condition_ref: str, expiry_time: Mapping[str, Any] | None) -> Note7LineageDecision:
        values = self.binding.read_observation("samsung.issue_product_flow_direction", observation)
        _reopening(values["intent_result_notice"], "product_flow_direction")
        return Note7LineageDecision(
            self.SAMSUNG_POLICY_ID,
            "samsung.issue_product_flow_direction",
            ("h2epr.commitment.0481.samsung_crisis_decision_interface.DC-SAM-2",),
            {
                "action": action,
                "capacity_id": "capacity.0481.samsung.product-safety",
                "direction_id": _value(direction_id, "direction_id"),
                "direction_version": _version(direction_version, "direction_version"),
                "expiry_time": expiry_time,
                "jurisdiction_ref": jurisdiction_ref,
                "product_class_ref": product_class_ref,
                "recipient_id": REGIONAL_ACTOR_ID,
                "review_condition_ref": review_condition_ref,
                "route_id": "route.0481.samsung_to_regional.direction",
                "sender_id": SAMSUNG_ACTOR_ID,
                "source_object_refs": _sorted((values["investigation_update"], values["product_flow_snapshot"], values["authority_or_partner_record"]), "source_object_refs"),
                "timing_ref": timing_ref,
            },
        )

    def decide_replacement_program(self, observation: Mapping[str, Any], *, program_id: str, program_version: int, product_class_ref: str, remedy_kind: str, eligibility_proposal_ref: str, timing_ref: str, uncertainty: str, review_condition_ref: str, expiry_time: Mapping[str, Any] | None) -> Note7LineageDecision:
        values = self.binding.read_observation("samsung.announce_replacement_program", observation)
        _reopening(values["intent_result_notice"], "replacement_program")
        return Note7LineageDecision(
            self.SAMSUNG_POLICY_ID,
            "samsung.announce_replacement_program",
            ("h2epr.commitment.0481.samsung_crisis_decision_interface.DC-SAM-2",),
            {
                "capacity_id": "capacity.0481.samsung.product-safety",
                "eligibility_proposal_ref": eligibility_proposal_ref,
                "expiry_time": expiry_time,
                "product_class_ref": product_class_ref,
                "program_id": program_id,
                "program_version": program_version,
                "recipient_id": REGIONAL_ACTOR_ID,
                "remedy_kind": remedy_kind,
                "review_condition_ref": review_condition_ref,
                "route_id": "route.0481.samsung_to_regional.direction",
                "sender_id": SAMSUNG_ACTOR_ID,
                "source_object_refs": _sorted((values["investigation_update"], values["product_flow_snapshot"]), "source_object_refs"),
                "timing_ref": timing_ref,
                "uncertainty": uncertainty,
            },
        )

    def decide_partner_coordination(self, observation: Mapping[str, Any], *, direction_action: Mapping[str, Any], direction_message: Mapping[str, Any], direction_delivery: MessageDelivery, program_action: Mapping[str, Any], program_message: Mapping[str, Any], program_delivery: MessageDelivery, coordination_id: str, coordination_version: int, requested_action: str, jurisdiction_ref: str, timing_ref: str, review_condition_ref: str, expiry_time: Mapping[str, Any] | None) -> Note7LineageDecision:
        _delivery(direction_delivery, direction_action, direction_message, REGIONAL_ACTOR_ID, "direction")
        _delivery(program_delivery, program_action, program_message, REGIONAL_ACTOR_ID, "program")
        values = self.binding.read_observation("regional.coordinate_local_partner_response", observation)
        if values["delivered_central_direction"] != program_message["message_intent_id"]:
            raise Note7LineageBindingError("NOTE7_LINEAGE_REGIONAL_DIRECTION_MISMATCH")
        _reopening(values["intent_result_notice"], "partner_coordination")
        return Note7LineageDecision(
            self.REGIONAL_POLICY_ID,
            "regional.coordinate_local_partner_response",
            ("h2epr.commitment.0481.samsung_regional_implementation_units.situation_a",),
            {
                "capacity_id": "capacity.0481.unit.samsung-regional-singapore",
                "coordination_id": coordination_id,
                "coordination_version": coordination_version,
                "direction_delivery_ref": direction_delivery.delivery_ref,
                "expiry_time": expiry_time,
                "jurisdiction_ref": jurisdiction_ref,
                "program_delivery_ref": program_delivery.delivery_ref,
                "recipient_id": OUTLET_ACTOR_ID,
                "requested_action": requested_action,
                "review_condition_ref": review_condition_ref,
                "route_id": "route.0481.regional_to_outlet.coordination",
                "sender_id": REGIONAL_ACTOR_ID,
                "source_message_refs": _sorted((direction_message["message_intent_id"], program_message["message_intent_id"]), "source_message_refs"),
                "timing_ref": timing_ref,
            },
        )

    def decide_local_remedy(self, observation: Mapping[str, Any], *, coordination_action: Mapping[str, Any], coordination_message: Mapping[str, Any], coordination_delivery: MessageDelivery, proposal_id: str, proposal_version: int, eligibility_proposal_ref: str, remedy_kind: str, channel_ref: str, timing_ref: str, stock_qualification_ref: str, uncertainty: str, review_condition_ref: str, expiry_time: Mapping[str, Any] | None) -> Note7LineageDecision:
        _delivery(coordination_delivery, coordination_action, coordination_message, OUTLET_ACTOR_ID, "coordination")
        values = self.binding.read_observation("regional.propose_local_remedy", observation)
        _reopening(values["intent_result_notice"], "local_remedy")
        return Note7LineageDecision(
            self.REGIONAL_POLICY_ID,
            "regional.propose_local_remedy",
            ("h2epr.commitment.0481.samsung_regional_implementation_units.situation_b",),
            {
                "capacity_id": "capacity.0481.unit.samsung-regional-singapore",
                "channel_ref": channel_ref,
                "coordination_delivery_ref": coordination_delivery.delivery_ref,
                "eligibility_proposal_ref": eligibility_proposal_ref,
                "expiry_time": expiry_time,
                "proposal_id": proposal_id,
                "proposal_version": proposal_version,
                "recipient_id": OUTLET_ACTOR_ID,
                "remedy_kind": remedy_kind,
                "review_condition_ref": review_condition_ref,
                "route_id": "route.0481.regional_to_outlet.coordination",
                "sender_id": REGIONAL_ACTOR_ID,
                "source_object_refs": _sorted((values["delivered_central_direction"], values["local_inventory_observation"], values["partner_response"]), "source_object_refs"),
                "stock_qualification_ref": stock_qualification_ref,
                "timing_ref": timing_ref,
                "uncertainty": uncertainty,
            },
        )

    def decide_outlet_posture(self, observation: Mapping[str, Any], *, proposal_action: Mapping[str, Any], proposal_message: Mapping[str, Any], proposal_delivery: MessageDelivery, posture_id: str, posture_version: int, product_class_ref: str, posture: str, basis_refs: Sequence[str], timing_ref: str, review_condition_ref: str, expiry_time: Mapping[str, Any] | None) -> Note7LineageDecision:
        _delivery(proposal_delivery, proposal_action, proposal_message, OUTLET_ACTOR_ID, "local_remedy")
        values = self.binding.read_observation("outlet.set_local_product_posture", observation)
        if values["delivered_product_direction"] != proposal_message["message_intent_id"]:
            raise Note7LineageBindingError("NOTE7_LINEAGE_OUTLET_POSTURE_BASIS_MISMATCH")
        _reopening(values["intent_result_notice"], "outlet_posture")
        return Note7LineageDecision(
            self.OUTLET_POLICY_ID,
            "outlet.set_local_product_posture",
            ("h2epr.commitment.0481.carrier_and_retail_remedy_outlets.situation_a",),
            {
                "basis_refs": _sorted(basis_refs, "basis_refs"),
                "capacity_id": "capacity.0481.unit.outlet-singapore-channel",
                "expiry_time": expiry_time,
                "posture": posture,
                "posture_id": posture_id,
                "posture_version": posture_version,
                "product_class_ref": product_class_ref,
                "review_condition_ref": review_condition_ref,
                "timing_ref": timing_ref,
            },
        )

    def decide_consumer_request(self, observation: Mapping[str, Any], *, offer: RemedyOfferDelivery, request_id: str, request_version: int, device_ref: str, selected_remedy: str, event_time_ref: str, uncertainty: str, review_condition_ref: str, expiry_time: Mapping[str, Any] | None) -> Note7LineageDecision:
        values = self.binding.read_observation("consumer.request_exchange_or_refund", observation)
        if not offer.delivered or offer.consumer_actor_id != CONSUMER_ACTOR_ID or values["local_remedy_offer"] != offer.offer_id:
            raise Note7LineageBindingError("NOTE7_LINEAGE_CONSUMER_OFFER_MISMATCH")
        _reopening(values["intent_result_notice"], "consumer_request")
        return Note7LineageDecision(
            self.CONSUMER_POLICY_ID,
            "consumer.request_exchange_or_refund",
            ("h2epr.commitment.0481.note7_owners_and_prospective_consumers.situation_c",),
            {
                "capacity_id": "capacity.0481.unit.consumer-primary",
                "device_ref": device_ref,
                "event_time_ref": event_time_ref,
                "expiry_time": expiry_time,
                "offer_delivery_ref": offer.offer_delivery_ref,
                "offer_id": offer.offer_id,
                "offer_version": offer.offer_version,
                "recipient_id": OUTLET_ACTOR_ID,
                "request_id": request_id,
                "request_version": request_version,
                "review_condition_ref": review_condition_ref,
                "route_id": "route.0481.consumer_to_outlet.remedy_request",
                "selected_remedy": selected_remedy,
                "sender_id": CONSUMER_ACTOR_ID,
                "uncertainty": uncertainty,
            },
        )

    def decide_outlet_response(self, observation: Mapping[str, Any], *, request_action: Mapping[str, Any], request_message: Mapping[str, Any], request_delivery: MessageDelivery, posture_result: ProductPostureResult, response_id: str, response_version: int, stated_basis_ref: str, proposed_path: str, uncertainty: str, review_condition_ref: str, expiry_time: Mapping[str, Any] | None) -> Note7LineageDecision:
        _delivery(request_delivery, request_action, request_message, OUTLET_ACTOR_ID, "consumer_request")
        request = self.binding.semantic_values(request_action)
        values = self.binding.read_observation("outlet.respond_to_remedy_request", observation)
        if values["consumer_request"] != request_message["message_intent_id"] or posture_result.status != "admitted":
            raise Note7LineageBindingError("NOTE7_LINEAGE_OUTLET_RESPONSE_BASIS_MISMATCH")
        _reopening(values["intent_result_notice"], "outlet_response")
        return Note7LineageDecision(
            self.OUTLET_POLICY_ID,
            "outlet.respond_to_remedy_request",
            ("h2epr.commitment.0481.carrier_and_retail_remedy_outlets.situation_b",),
            {
                "capacity_id": "capacity.0481.unit.outlet-singapore-channel",
                "expiry_time": expiry_time,
                "posture_result_ref": posture_result.result_id,
                "proposed_path": proposed_path,
                "recipient_id": CONSUMER_ACTOR_ID,
                "request_delivery_ref": request_delivery.delivery_ref,
                "request_id": request["request_id"],
                "request_message_ref": request_message["message_intent_id"],
                "request_version": request["request_version"],
                "response_id": response_id,
                "response_version": response_version,
                "review_condition_ref": review_condition_ref,
                "route_id": "route.0481.outlet_to_consumer.remedy_response",
                "sender_id": OUTLET_ACTOR_ID,
                "stated_basis_ref": stated_basis_ref,
                "uncertainty": uncertainty,
            },
        )


__all__ = [
    "CONSUMER_ACTOR_ID",
    "OUTLET_ACTOR_ID",
    "REGIONAL_ACTOR_ID",
    "SAMSUNG_ACTOR_ID",
    "Note7LineageDecision",
    "PositiveNote7LineagePoliciesV0_1",
]
