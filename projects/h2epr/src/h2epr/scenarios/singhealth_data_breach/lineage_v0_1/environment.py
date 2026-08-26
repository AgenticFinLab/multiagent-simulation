"""Bounded environment policies for the SingHealth lineage carrier checks."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping, Sequence

from .binding import LineageBinding, LineageBindingError


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
class VerificationResult:
    result_id: str
    result_version: int
    request_intent_id: str
    request_id: str
    request_version: int
    finding_id: str
    finding_version: int
    producer_actor_id: str
    status: str
    produced_tick: int
    delivered_tick: int | None = None
    delivery_ref: str | None = None
    delivered: bool = False


class LineageEnvironmentV0_1:
    """Six event-local policy implementations, limited to the bound lineage."""

    _TRANSITIONS = {
        "participant_intent": {
            "issued": {"admitted", "rejected"},
            "admitted": {"pending"},
            "pending": {
                "acknowledged",
                "partial",
                "completed",
                "failed",
                "expired",
                "cancelled",
                "superseded",
            },
            "acknowledged": {
                "partial",
                "completed",
                "failed",
                "expired",
                "cancelled",
                "superseded",
            },
            "partial": {
                "completed",
                "failed",
                "expired",
                "cancelled",
                "superseded",
            },
        },
        "information_product": {
            "produced": {"routed"},
            "routed": {"delivered", "failed", "expired"},
            "delivered": {"acknowledged", "corrected", "superseded"},
            "acknowledged": {"corrected", "superseded"},
        },
        "investigation_or_verification_request": {
            "requested": {"authority_checked", "failed", "expired"},
            "authority_checked": {"assigned", "executing", "failed"},
            "assigned": {"executing", "failed", "expired"},
            "executing": {"partial", "completed", "failed"},
            "partial": {"completed", "failed", "expired"},
        },
    }

    def __init__(self, binding: LineageBinding) -> None:
        self.binding = binding

    def order_events(self, events: Sequence[Mapping[str, Any]]) -> tuple[str, ...]:
        """Validate a finite logical partial order and return its stable order."""

        by_id: dict[str, Mapping[str, Any]] = {}
        for event in events:
            if set(event) != {"event_id", "logical_tick", "predecessor_ids"}:
                raise LineageBindingError("LINEAGE_TIME_EVENT_FIELDS_MISMATCH")
            event_id = event["event_id"]
            tick = event["logical_tick"]
            predecessors = event["predecessor_ids"]
            if (
                not isinstance(event_id, str)
                or not event_id
                or event_id in by_id
                or isinstance(tick, bool)
                or not isinstance(tick, int)
                or tick < 0
                or not isinstance(predecessors, (list, tuple))
                or len(predecessors) != len(set(predecessors))
                or any(not isinstance(item, str) or not item for item in predecessors)
            ):
                raise LineageBindingError("LINEAGE_TIME_EVENT_INVALID")
            by_id[event_id] = event
        for event_id, event in by_id.items():
            for predecessor_id in event["predecessor_ids"]:
                if predecessor_id not in by_id:
                    raise LineageBindingError("LINEAGE_TIME_PREDECESSOR_UNKNOWN")
                if by_id[predecessor_id]["logical_tick"] >= event["logical_tick"]:
                    raise LineageBindingError("LINEAGE_TIME_CAUSAL_ORDER_INVALID")
            if event_id in event["predecessor_ids"]:
                raise LineageBindingError("LINEAGE_TIME_SELF_PREDECESSOR")
        return tuple(
            event_id
            for event_id, _ in sorted(
                by_id.items(), key=lambda item: (item[1]["logical_tick"], item[0])
            )
        )

    def assert_authority(
        self, action_key: str, action: Mapping[str, Any]
    ) -> None:
        """Check the selected unit/office capacity and exact route carrier."""

        self.binding.validate_action(action_key, action)
        contract = self.binding.actions[action_key]
        route = self.binding.routes[contract.message_route_id]
        values = self.binding.semantic_values(action)
        actor = self.binding.actors[contract.actor_id]
        if (
            values.get("capacity_id") != actor["selected_capacity_id"]
            or values.get("route_id") != route.route_id
            or route.required_source_capacity_id != actor["selected_capacity_id"]
            or tuple(action["claimed_authority_refs"])
            != (actor["authority_record_id"],)
        ):
            raise LineageBindingError("LINEAGE_AUTHORITY_CAPACITY_ROUTE_MISMATCH")

    def admit_idempotency(
        self,
        action: Mapping[str, Any],
        active_idempotency_keys: Sequence[str],
    ) -> str:
        key = action.get("idempotency_key")
        if not isinstance(key, str) or not key:
            raise LineageBindingError("LINEAGE_IDEMPOTENCY_KEY_INVALID")
        if key in active_idempotency_keys:
            raise LineageBindingError("LINEAGE_DUPLICATE_ACTIVE_INTENT")
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
        """Materialize delivery without implying acknowledgement or response."""

        self.binding.validate_message(action_key, action, message)
        contract = self.binding.actions[action_key]
        route = self.binding.routes[contract.message_route_id]
        self.assert_authority(action_key, action)
        if (
            route_id != route.route_id
            or not isinstance(delivery_ref, str)
            or not delivery_ref
            or isinstance(delivered_tick, bool)
            or not isinstance(delivered_tick, int)
            or delivered_tick != action["logical_tick"] + route.latency_ticks
        ):
            raise LineageBindingError("LINEAGE_ROUTE_DELIVERY_MISMATCH")
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

    def produce_verification_result(
        self,
        request_action: Mapping[str, Any],
        request_delivery: MessageDelivery,
        *,
        result_id: str,
        result_version: int,
        status: str,
        producer_actor_id: str,
        produced_tick: int,
    ) -> VerificationResult:
        """Create a result only after the exact request reaches its recipient."""

        self.binding.validate_action(
            "operations.request_fact_verification", request_action
        )
        values = self.binding.semantic_values(request_action)
        technical_actor_id = "actor.0616.unit.technical.scm-application-database"
        if (
            not request_delivery.delivered
            or request_delivery.action_intent_id != request_action["intent_id"]
            or request_delivery.recipient_id != technical_actor_id
            or producer_actor_id != technical_actor_id
            or not isinstance(result_id, str)
            or not result_id
            or isinstance(result_version, bool)
            or not isinstance(result_version, int)
            or result_version < 0
            or status not in {"verified", "disputed", "partial", "failed"}
            or isinstance(produced_tick, bool)
            or not isinstance(produced_tick, int)
            or produced_tick <= request_delivery.delivered_tick
        ):
            raise LineageBindingError("LINEAGE_VERIFICATION_RESULT_INVALID")
        return VerificationResult(
            result_id=result_id,
            result_version=result_version,
            request_intent_id=request_action["intent_id"],
            request_id=values["request_id"],
            request_version=values["request_version"],
            finding_id=values["source_finding_id"],
            finding_version=values["source_finding_version"],
            producer_actor_id=producer_actor_id,
            status=status,
            produced_tick=produced_tick,
        )

    def deliver_verification_result(
        self,
        result: VerificationResult,
        *,
        delivery_ref: str,
        recipient_actor_id: str,
        delivered_tick: int,
    ) -> VerificationResult:
        operations_actor_id = (
            "actor.0616.unit.operations.application-scm-coordination"
        )
        if (
            result.delivered
            or not isinstance(delivery_ref, str)
            or not delivery_ref
            or recipient_actor_id != operations_actor_id
            or delivered_tick != result.produced_tick
        ):
            raise LineageBindingError("LINEAGE_VERIFICATION_DELIVERY_INVALID")
        return replace(
            result,
            delivered_tick=delivered_tick,
            delivery_ref=delivery_ref,
            delivered=True,
        )

    def assert_transition(self, family: str, source: str, target: str) -> None:
        try:
            allowed = self._TRANSITIONS[family][source]
        except KeyError as exc:
            raise LineageBindingError("LINEAGE_LIFECYCLE_STATE_UNKNOWN") from exc
        if target not in allowed:
            raise LineageBindingError("LINEAGE_LIFECYCLE_TRANSITION_INVALID")


__all__ = [
    "LineageEnvironmentV0_1",
    "MessageDelivery",
    "VerificationResult",
]
