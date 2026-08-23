"""Closed scientific values exchanged by an event-process runtime.

These values deliberately contain logical coordinates only.  Wall-clock and
worker metadata belong in operational receipts, never in scientific bytes.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field, fields
from types import MappingProxyType
from typing import Any, Mapping


def _identifier(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError(f"invalid_{field_name}")


def _logical_tick(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("invalid_logical_tick")


def _mapping(value: Mapping[str, Any], field_name: str) -> None:
    if not isinstance(value, Mapping):
        raise TypeError(f"{field_name}_must_be_mapping")


def _freeze(value: Any) -> Any:
    """Detach and recursively freeze JSON-like scientific values."""
    if isinstance(value, Mapping):
        return MappingProxyType({copy.deepcopy(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(_freeze(item) for item in value)
    return copy.deepcopy(value)


def _plain(value: Any) -> Any:
    """Return detached plain values suitable for canonical serialization."""
    if isinstance(value, Mapping):
        return {copy.deepcopy(key): _plain(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return tuple(_plain(item) for item in value)
    if isinstance(value, frozenset):
        return frozenset(_plain(item) for item in value)
    return copy.deepcopy(value)


def _freeze_fields(instance: Any, *names: str) -> None:
    for name in names:
        object.__setattr__(instance, name, _freeze(getattr(instance, name)))


class ClosedValue:
    """Mixin providing deterministic plain-object serialization."""

    def to_dict(self) -> dict[str, Any]:
        return {item.name: _plain(getattr(self, item.name)) for item in fields(self)}


@dataclass(frozen=True)
class ObservationEnvelope(ClosedValue):
    actor_id: str
    logical_tick: int
    physical_masim_round: int
    execution_level: int
    prestate_version: int
    prestate_sha256: str
    public_state: Mapping[str, Any]
    private_state: Mapping[str, Any]
    delivered_messages: tuple[Mapping[str, Any], ...] = ()
    prior_generated_state: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _identifier(self.actor_id, "actor_id")
        _logical_tick(self.logical_tick)
        if self.physical_masim_round != self.logical_tick or self.execution_level != 0:
            raise ValueError("physical_logical_coordinate_mismatch")
        if isinstance(self.prestate_version, bool) or self.prestate_version < 0:
            raise ValueError("invalid_prestate_version")
        if len(self.prestate_sha256) != 64:
            raise ValueError("invalid_prestate_sha256")
        _mapping(self.public_state, "public_state")
        _mapping(self.private_state, "private_state")
        _mapping(self.prior_generated_state, "prior_generated_state")
        if not isinstance(self.delivered_messages, (list, tuple)) or not all(
            isinstance(item, Mapping) for item in self.delivered_messages
        ):
            raise TypeError("delivered_messages_must_be_sequence_of_mappings")
        _freeze_fields(
            self,
            "public_state",
            "private_state",
            "delivered_messages",
            "prior_generated_state",
        )


@dataclass(frozen=True)
class ActionIntent(ClosedValue):
    intent_id: str
    run_id: str
    actor_id: str
    logical_tick: int
    prestate_version: int
    prestate_sha256: str
    action_type: str
    parameters: Mapping[str, Any]
    policy_id: str

    def __post_init__(self) -> None:
        for name in ("intent_id", "run_id", "actor_id", "action_type", "policy_id"):
            _identifier(getattr(self, name), name)
        _logical_tick(self.logical_tick)
        if isinstance(self.prestate_version, bool) or self.prestate_version < 0:
            raise ValueError("invalid_prestate_version")
        if len(self.prestate_sha256) != 64:
            raise ValueError("invalid_prestate_sha256")
        _mapping(self.parameters, "parameters")
        _freeze_fields(self, "parameters")


@dataclass(frozen=True)
class MessageIntent(ClosedValue):
    message_intent_id: str
    run_id: str
    source_action_intent_id: str
    sender_id: str
    recipient_id: str
    route_id: str
    logical_tick: int
    latency_ticks: int
    message_kind: str
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "message_intent_id",
            "run_id",
            "source_action_intent_id",
            "sender_id",
            "recipient_id",
            "route_id",
            "message_kind",
        ):
            _identifier(getattr(self, name), name)
        if self.sender_id == self.recipient_id:
            raise ValueError("self_message_forbidden")
        _logical_tick(self.logical_tick)
        if isinstance(self.latency_ticks, bool) or self.latency_ticks < 1:
            raise ValueError("invalid_message_latency")
        _mapping(self.payload, "payload")
        _freeze_fields(self, "payload")


@dataclass(frozen=True)
class ActionDisposition(ClosedValue):
    disposition_id: str
    intent_id: str
    logical_tick: int
    status: str
    reason_code: str
    state_delta_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.status not in {"accepted", "rejected", "invalid", "duplicate", "failed"}:
            raise ValueError("invalid_action_disposition_status")
        for name in ("disposition_id", "intent_id", "reason_code"):
            _identifier(getattr(self, name), name)
        _logical_tick(self.logical_tick)
        if self.status != "accepted" and self.state_delta_ids:
            raise ValueError("nonaccepted_disposition_has_delta")
        _freeze_fields(self, "state_delta_ids")


@dataclass(frozen=True)
class MessageDisposition(ClosedValue):
    disposition_id: str
    message_intent_id: str
    sender_id: str
    recipient_id: str
    logical_tick: int
    status: str
    reason_code: str
    predecessor_disposition_id: str | None = None
    duplicate_of_intent_id: str | None = None

    def __post_init__(self) -> None:
        if self.status not in {
            "queued",
            "delayed",
            "sent",
            "delivered",
            "expired",
            "rejected",
            "duplicate",
            "failed",
        }:
            raise ValueError("invalid_message_disposition_status")
        for name in ("disposition_id", "message_intent_id", "sender_id", "recipient_id", "reason_code"):
            _identifier(getattr(self, name), name)
        _logical_tick(self.logical_tick)


@dataclass(frozen=True)
class StateDelta(ClosedValue):
    delta_id: str
    source_intent_id: str
    entity_id: str
    field_name: str
    before: Any
    after: Any
    delta_class: str

    def __post_init__(self) -> None:
        for name in ("delta_id", "source_intent_id", "entity_id", "field_name", "delta_class"):
            _identifier(getattr(self, name), name)
        if self.before == self.after:
            raise ValueError("zero_effect_state_delta")
        _freeze_fields(self, "before", "after")
