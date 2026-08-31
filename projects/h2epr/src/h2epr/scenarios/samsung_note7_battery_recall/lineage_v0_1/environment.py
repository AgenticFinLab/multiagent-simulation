"""Bounded environment policies for the Note7 remedy lineage."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .binding import Note7LineageBinding, Note7LineageBindingError


def _runtime_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise Note7LineageBindingError(f"NOTE7_LINEAGE_RUNTIME_ID_INVALID:{label}")
    return value


def _runtime_version(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise Note7LineageBindingError(f"NOTE7_LINEAGE_RUNTIME_VERSION_INVALID:{label}")
    return value


@dataclass(frozen=True)
class MessageDelivery:
    delivery_ref: str
    action_intent_id: str
    message_intent_id: str
    route_id: str
    source_opening_route_id: str
    sender_id: str
    recipient_id: str
    issued_tick: int
    delivered_tick: int
    delivered: bool


@dataclass(frozen=True)
class ProductPostureResult:
    result_id: str
    result_version: int
    action_intent_id: str
    posture_id: str
    posture_version: int
    product_class_ref: str
    status: str
    producer_process_id: str
    produced_tick: int


@dataclass(frozen=True)
class RemedyOfferDelivery:
    offer_delivery_ref: str
    proposal_action_intent_id: str
    proposal_id: str
    proposal_version: int
    posture_result_id: str
    offer_id: str
    offer_version: int
    outlet_actor_id: str
    consumer_actor_id: str
    route_id: str
    delivered_tick: int
    delivered: bool


class Note7LineageEnvironmentV0_1:
    """Seven policy implementations, only for the accepted bounded slice."""

    _TRANSITIONS = {
        "participant_intent": {
            "issued": {"admitted", "rejected"},
            "admitted": {"pending"},
            "pending": {"acknowledged", "partial", "completed", "failed", "expired", "cancelled", "superseded"},
            "acknowledged": {"partial", "completed", "failed", "expired", "cancelled", "superseded"},
            "partial": {"completed", "failed", "expired", "cancelled", "superseded"},
        },
        "product_flow_posture": {
            "proposed": {"admitted", "failed", "superseded"},
            "admitted": {"active", "partial", "failed", "reversed", "superseded"},
            "active": {"partial", "completed", "failed", "reversed", "superseded"},
        },
        "remedy_offer_and_fulfillment": {
            "proposed": {"reviewed", "failed", "superseded"},
            "reviewed": {"available", "failed", "superseded"},
            "available": {"selected", "failed", "superseded"},
            "selected": {"accepted", "failed", "superseded"},
            "accepted": {"handed_off", "refunded", "exchanged", "failed"},
        },
    }

    def __init__(self, binding: Note7LineageBinding) -> None:
        self.binding = binding

    def assert_authority(self, action_key: str, action: Mapping[str, Any]) -> None:
        self.binding.validate_action(action_key, action)
        contract = self.binding.actions[action_key]
        values = self.binding.semantic_values(action)
        actor = self.binding.actors[contract.actor_id]
        if values.get("capacity_id") != actor["selected_capacity_id"] or tuple(action["claimed_authority_refs"]) != (actor["authority_record_id"],):
            raise Note7LineageBindingError("NOTE7_LINEAGE_AUTHORITY_MISMATCH")

    def admit_idempotency(self, action: Mapping[str, Any], active_keys: Sequence[str]) -> str:
        key = action.get("idempotency_key")
        if not isinstance(key, str) or not key:
            raise Note7LineageBindingError("NOTE7_LINEAGE_IDEMPOTENCY_KEY_INVALID")
        if key in active_keys:
            raise Note7LineageBindingError("NOTE7_LINEAGE_DUPLICATE_ACTIVE_INTENT")
        return key

    def deliver_message(
        self,
        action_key: str,
        action: Mapping[str, Any],
        message: Mapping[str, Any],
        *,
        route_id: str,
        delivery_ref: str,
        delivered_tick: int,
    ) -> MessageDelivery:
        self.binding.validate_message(action_key, action, message)
        self.assert_authority(action_key, action)
        contract = self.binding.actions[action_key]
        if contract.message_route_id is None:
            raise Note7LineageBindingError("NOTE7_LINEAGE_MESSAGE_ROUTE_MISSING")
        route = self.binding.routes[contract.message_route_id]
        if route_id != route.route_id or not isinstance(delivery_ref, str) or not delivery_ref or delivered_tick != action["logical_tick"] + route.latency_ticks:
            raise Note7LineageBindingError("NOTE7_LINEAGE_ROUTE_DELIVERY_MISMATCH")
        return MessageDelivery(
            delivery_ref=delivery_ref,
            action_intent_id=action["intent_id"],
            message_intent_id=message["message_intent_id"],
            route_id=route.route_id,
            source_opening_route_id=route.source_opening_route_id,
            sender_id=route.source_actor_id,
            recipient_id=route.target_actor_id,
            issued_tick=action["logical_tick"],
            delivered_tick=delivered_tick,
            delivered=True,
        )

    def adjudicate_product_posture(
        self,
        action: Mapping[str, Any],
        *,
        result_id: str,
        result_version: int,
        status: str,
        produced_tick: int,
    ) -> ProductPostureResult:
        self.assert_authority("outlet.set_local_product_posture", action)
        values = self.binding.semantic_values(action)
        if status not in {"admitted", "partial", "failed"} or produced_tick <= action["logical_tick"]:
            raise Note7LineageBindingError("NOTE7_LINEAGE_PRODUCT_POSTURE_RESULT_INVALID")
        return ProductPostureResult(
            result_id=_runtime_id(result_id, "result_id"),
            result_version=_runtime_version(result_version, "result_version"),
            action_intent_id=action["intent_id"],
            posture_id=values["posture_id"],
            posture_version=values["posture_version"],
            product_class_ref=values["product_class_ref"],
            status=status,
            producer_process_id="process.0481.product-flow-production-and-partner-response",
            produced_tick=produced_tick,
        )

    def deliver_remedy_offer(
        self,
        proposal_action: Mapping[str, Any],
        proposal_delivery: MessageDelivery,
        posture_result: ProductPostureResult,
        *,
        offer_id: str,
        offer_version: int,
        offer_delivery_ref: str,
        delivered_tick: int,
    ) -> RemedyOfferDelivery:
        self.binding.validate_action("regional.propose_local_remedy", proposal_action)
        proposal = self.binding.semantic_values(proposal_action)
        outlet = "actor.0481.unit.outlet-singapore-channel"
        consumer = "actor.0481.unit.consumer-primary"
        if (
            not proposal_delivery.delivered
            or proposal_delivery.action_intent_id != proposal_action["intent_id"]
            or proposal_delivery.recipient_id != outlet
            or posture_result.status != "admitted"
            or posture_result.produced_tick >= delivered_tick
        ):
            raise Note7LineageBindingError("NOTE7_LINEAGE_REMEDY_OFFER_DELIVERY_INVALID")
        return RemedyOfferDelivery(
            offer_delivery_ref=_runtime_id(offer_delivery_ref, "offer_delivery_ref"),
            proposal_action_intent_id=proposal_action["intent_id"],
            proposal_id=proposal["proposal_id"],
            proposal_version=proposal["proposal_version"],
            posture_result_id=posture_result.result_id,
            offer_id=_runtime_id(offer_id, "offer_id"),
            offer_version=_runtime_version(offer_version, "offer_version"),
            outlet_actor_id=outlet,
            consumer_actor_id=consumer,
            route_id="opening.0481.route.outlet-consumer",
            delivered_tick=delivered_tick,
            delivered=True,
        )

    def assert_transition(self, family: str, source: str, target: str) -> None:
        try:
            allowed = self._TRANSITIONS[family][source]
        except KeyError as exc:
            raise Note7LineageBindingError("NOTE7_LINEAGE_LIFECYCLE_STATE_UNKNOWN") from exc
        if target not in allowed:
            raise Note7LineageBindingError("NOTE7_LINEAGE_LIFECYCLE_TRANSITION_INVALID")


__all__ = [
    "MessageDelivery",
    "Note7LineageEnvironmentV0_1",
    "ProductPostureResult",
    "RemedyOfferDelivery",
]
