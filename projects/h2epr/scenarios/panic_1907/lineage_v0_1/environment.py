"""Versioned environment-policy implementations for the bounded lineage."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any, Mapping, Sequence

from .binding import LineageBinding, LineageBindingError


POLICY_IMPLEMENTATION_IDS = {
    "POL-FACILITY-01": "h2epr.policy.0288.facility.dated_activation.v0_1",
    "POL-INFO-01": "h2epr.policy.0288.info.delivery.v0_1",
    "POL-LIFECYCLE-01": "h2epr.policy.0288.lifecycle.event_revisit.v0_1",
    "POL-RESULT-01": "h2epr.policy.0288.result.layered.v0_1",
    "POL-REVIEW-01": "h2epr.policy.0288.review.typed_completeness.v0_1",
    "POL-TIME-01": "h2epr.policy.0288.time.partial_order.v0_1",
}

_FACILITY_ACTIVATION = datetime.fromisoformat("1907-10-26T00:00:00-05:00")
_SELECTED_TRANSITIONS = {
    "LF-SUPPORT": frozenset(
        {
            ("draft", "authorized"),
            ("authorized", "issued"),
            ("issued", "hop-delivered"),
            ("received", "classified"),
            ("classified", "referred"),
            ("classified", "reviewing"),
            ("classified", "declined"),
            ("reviewing", "declined"),
            ("declined", "closed"),
        }
    ),
    "LF-COMM": frozenset(
        {
            ("authorized", "issued"),
            ("issued", "transport-pending"),
            ("transport-pending", "delivered"),
            ("transport-pending", "failed"),
            ("transport-pending", "expired"),
        }
    ),
}


@dataclass(frozen=True)
class OrderedEvent:
    event_id: str
    event_time: str
    predecessor_ids: tuple[str, ...]


@dataclass(frozen=True)
class MessageStages:
    message_intent_id: str
    route_id: str
    issued: bool
    route_admitted: bool
    delivered: bool
    delivered_at: str


@dataclass(frozen=True)
class ReviewResult:
    classification: str
    present_item_ids: tuple[str, ...]
    missing_item_ids: tuple[str, ...]
    disputed_item_ids: tuple[str, ...]


@dataclass(frozen=True)
class ResultLayers:
    action_intent_id: str
    action_admission: str
    business_disposition_id: str
    business_disposition: str
    execution_result: str
    reason_code: str
    delivered: bool
    delivery_ref: str | None


class LineageEnvironmentV0_1:
    """Concrete implementations of only the six selected environment policies."""

    def __init__(self, binding: LineageBinding) -> None:
        self.binding = binding
        actual = {
            policy_id: item.implementation_id
            for policy_id, item in binding.policy_bindings.items()
        }
        if actual != POLICY_IMPLEMENTATION_IDS:
            raise LineageBindingError("LINEAGE_ENVIRONMENT_POLICY_SET_MISMATCH")

    def order_events(self, events: Sequence[Mapping[str, Any]]) -> tuple[str, ...]:
        """Honor predecessors, then event time, then a residual stable-ID tie."""

        parsed: dict[str, OrderedEvent] = {}
        times: dict[str, datetime] = {}
        for raw in events:
            if set(raw) != {"event_id", "event_time", "predecessor_ids"}:
                raise LineageBindingError("LINEAGE_TIME_EVENT_FIELDS_MISMATCH")
            event_id = _stable_id(raw["event_id"], "event_id")
            if event_id in parsed:
                raise LineageBindingError("LINEAGE_TIME_EVENT_DUPLICATE")
            predecessors = tuple(
                _stable_id(item, "predecessor_id")
                for item in _sequence(raw["predecessor_ids"], "predecessor_ids")
            )
            if len(predecessors) != len(set(predecessors)):
                raise LineageBindingError("LINEAGE_TIME_PREDECESSOR_DUPLICATE")
            event_time = _aware_time(raw["event_time"], "event_time")
            parsed[event_id] = OrderedEvent(
                event_id=event_id,
                event_time=raw["event_time"],
                predecessor_ids=predecessors,
            )
            times[event_id] = event_time
        for event in parsed.values():
            for predecessor in event.predecessor_ids:
                if predecessor not in parsed:
                    raise LineageBindingError("LINEAGE_TIME_PREDECESSOR_UNKNOWN")
                if times[predecessor] > times[event.event_id]:
                    raise LineageBindingError("LINEAGE_TIME_CAUSAL_ORDER_CONFLICT")
        remaining = set(parsed)
        emitted: list[str] = []
        emitted_set: set[str] = set()
        while remaining:
            ready = [
                event_id
                for event_id in remaining
                if set(parsed[event_id].predecessor_ids).issubset(emitted_set)
            ]
            if not ready:
                raise LineageBindingError("LINEAGE_TIME_PREDECESSOR_CYCLE")
            selected = min(ready, key=lambda item: (times[item], item))
            emitted.append(selected)
            emitted_set.add(selected)
            remaining.remove(selected)
        return tuple(emitted)

    def deliver_message(
        self,
        action_key: str,
        action: Mapping[str, Any],
        message: Mapping[str, Any],
        *,
        route_id: str,
        delivered_at: str,
    ) -> MessageStages:
        """Admit one exact route and keep issue, route, and delivery distinct."""

        self.binding.validate_message(action_key, action, message)
        contract = self.binding.actions[action_key]
        if contract.message_route_id != route_id:
            raise LineageBindingError("LINEAGE_INFO_ROUTE_MISMATCH")
        route = self.binding.routes[route_id]
        if (
            message["sender_id"] != route.source_actor_id
            or tuple(message["recipient_ids"]) != (route.target_actor_id,)
        ):
            raise LineageBindingError("LINEAGE_INFO_ENDPOINT_MISMATCH")
        delivery = _aware_time(delivered_at, "delivered_at")
        earliest = _interval_edge(message["earliest_delivery_time"], "lower")
        expiry = (
            None
            if message["expiry_time"] is None
            else _interval_edge(message["expiry_time"], "upper")
        )
        if delivery < earliest:
            raise LineageBindingError("LINEAGE_INFO_DELIVERY_TOO_EARLY")
        if expiry is not None and delivery > expiry:
            raise LineageBindingError("LINEAGE_INFO_DELIVERY_EXPIRED")
        return MessageStages(
            message_intent_id=message["message_intent_id"],
            route_id=route_id,
            issued=True,
            route_admitted=True,
            delivered=True,
            delivered_at=delivered_at,
        )

    @staticmethod
    def classify_information(
        *,
        required_item_ids: Sequence[str],
        present_item_ids: Sequence[str],
        disputed_item_ids: Sequence[str] = (),
        conditionally_omittable_item_ids: Sequence[str] = (),
    ) -> ReviewResult:
        """Return a typed completeness class; no score or solvency inference exists."""

        required = _unique_ids(required_item_ids, "required_item_ids")
        present = _unique_ids(present_item_ids, "present_item_ids", allow_empty=True)
        disputed = _unique_ids(
            disputed_item_ids, "disputed_item_ids", allow_empty=True
        )
        omittable = _unique_ids(
            conditionally_omittable_item_ids,
            "conditionally_omittable_item_ids",
            allow_empty=True,
        )
        if not set(present).issubset(required) or not set(disputed).issubset(required):
            raise LineageBindingError("LINEAGE_REVIEW_ITEM_OUTSIDE_REQUIREMENTS")
        if set(present).intersection(disputed) or not set(omittable).issubset(required):
            raise LineageBindingError("LINEAGE_REVIEW_ITEM_CLASS_CONFLICT")
        missing = tuple(sorted(set(required) - set(present) - set(disputed)))
        if disputed:
            classification = "disputed"
        elif not missing:
            classification = "complete"
        elif set(missing).issubset(omittable):
            classification = "conditionally_complete"
        else:
            classification = "incomplete"
        return ReviewResult(
            classification=classification,
            present_item_ids=tuple(sorted(present)),
            missing_item_ids=missing,
            disputed_item_ids=tuple(sorted(disputed)),
        )

    @staticmethod
    def facility_eligibility(*, event_time: str, membership: str) -> str:
        """Do not back-project the later member facility before activation."""

        current = _aware_time(event_time, "event_time")
        if membership not in {"member", "nonmember", "unknown"}:
            raise LineageBindingError("LINEAGE_FACILITY_MEMBERSHIP_INVALID")
        if current < _FACILITY_ACTIVATION:
            return "not_applicable"
        if membership == "member":
            return "eligible"
        if membership == "nonmember":
            return "ineligible"
        return "unknown"

    @staticmethod
    def assert_transition(family_id: str, before: str, after: str) -> None:
        """Admit only the selected positive lifecycle transitions."""

        transitions = _SELECTED_TRANSITIONS.get(family_id)
        if transitions is None:
            raise LineageBindingError("LINEAGE_LIFECYCLE_FAMILY_UNBOUND")
        if (before, after) not in transitions:
            raise LineageBindingError("LINEAGE_LIFECYCLE_TRANSITION_INVALID")

    @staticmethod
    def carry_forward(
        *,
        object_id: str,
        owner_actor_id: str,
        state: str,
        version: int,
        reason_code: str,
        next_event_id: str,
    ) -> dict[str, Any]:
        """Represent one unresolved object at the horizon without silent closure."""

        return {
            "object_id": _stable_id(object_id, "object_id"),
            "owner_actor_id": _stable_id(owner_actor_id, "owner_actor_id"),
            "state": _stable_id(state, "state"),
            "version": _nonnegative_integer(version, "version"),
            "reason_code": _stable_id(reason_code, "reason_code"),
            "next_event_id": _stable_id(next_event_id, "next_event_id"),
            "terminal": False,
        }

    @staticmethod
    def record_scoped_disposition(
        *,
        action_intent_id: str,
        business_disposition_id: str,
        reason_code: str,
    ) -> ResultLayers:
        """Keep action admission, disposition, execution, and delivery separate."""

        return ResultLayers(
            action_intent_id=_stable_id(action_intent_id, "action_intent_id"),
            action_admission="accepted",
            business_disposition_id=_stable_id(
                business_disposition_id, "business_disposition_id"
            ),
            business_disposition="other_scoped_decline",
            execution_result="not_applicable_no_resource_action",
            reason_code=_stable_id(reason_code, "reason_code"),
            delivered=False,
            delivery_ref=None,
        )

    @staticmethod
    def deliver_result(result: ResultLayers, *, delivery_ref: str) -> ResultLayers:
        if result.delivered:
            raise LineageBindingError("LINEAGE_RESULT_ALREADY_DELIVERED")
        return replace(
            result,
            delivered=True,
            delivery_ref=_stable_id(delivery_ref, "delivery_ref"),
        )


def _stable_id(value: Any, label: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value.strip() != value
        or len(value) > 128
        or not value[0].isalnum()
        or any(character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._:-" for character in value)
    ):
        raise LineageBindingError(f"LINEAGE_ENVIRONMENT_STABLE_ID_INVALID:{label}")
    return value


def _sequence(value: Any, label: str) -> Sequence[Any]:
    if not isinstance(value, (list, tuple)):
        raise LineageBindingError(f"LINEAGE_ENVIRONMENT_SEQUENCE_INVALID:{label}")
    return value


def _unique_ids(
    value: Sequence[str], label: str, *, allow_empty: bool = False
) -> tuple[str, ...]:
    items = tuple(_stable_id(item, label) for item in _sequence(value, label))
    if (not items and not allow_empty) or len(items) != len(set(items)):
        raise LineageBindingError(f"LINEAGE_ENVIRONMENT_IDS_INVALID:{label}")
    return items


def _aware_time(value: Any, label: str) -> datetime:
    if not isinstance(value, str):
        raise LineageBindingError(f"LINEAGE_ENVIRONMENT_TIME_INVALID:{label}")
    try:
        result = datetime.fromisoformat(value)
    except ValueError as exc:
        raise LineageBindingError(
            f"LINEAGE_ENVIRONMENT_TIME_INVALID:{label}"
        ) from exc
    if result.tzinfo is None:
        raise LineageBindingError(f"LINEAGE_ENVIRONMENT_TIME_INVALID:{label}")
    return result


def _interval_edge(value: Any, edge: str) -> datetime:
    if not isinstance(value, Mapping) or edge not in value:
        raise LineageBindingError("LINEAGE_ENVIRONMENT_INTERVAL_INVALID")
    return _aware_time(value[edge], f"interval.{edge}")


def _nonnegative_integer(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        raise LineageBindingError(f"LINEAGE_ENVIRONMENT_INTEGER_INVALID:{label}")
    return value


__all__ = [
    "LineageEnvironmentV0_1",
    "MessageStages",
    "OrderedEvent",
    "POLICY_IMPLEMENTATION_IDS",
    "ResultLayers",
    "ReviewResult",
]
