"""Event-neutral, deterministic lifecycle state graphs."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Sequence


class LifecycleRuleError(ValueError):
    """A lifecycle definition or supplied record is invalid."""


def _stable_id(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value.strip() != value
        or len(value) > 192
        or not value[0].isalnum()
        or any(
            character
            not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._:-"
            for character in value
        )
    ):
        raise LifecycleRuleError(f"stable_id_invalid:{label}")
    return value


@dataclass(frozen=True)
class LifecycleRecord:
    """One authoritative business object at a specific version."""

    object_id: str
    lifecycle_id: str
    owner_actor_id: str
    state_id: str
    version: int
    terminal: bool
    predecessor_object_id: str | None = None
    causal_parent_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class LifecycleTransitionResult:
    """Applied or typed non-mutating result of one requested transition."""

    applied: bool
    reason_code: str
    cause_id: str
    before: LifecycleRecord
    after: LifecycleRecord


@dataclass(frozen=True)
class LifecycleRule:
    """One closed state graph with typed, non-mutating invalid transitions."""

    lifecycle_id: str
    implementation_id: str
    implementation_version: str
    owner_layer: str
    participant_capability_ids: tuple[str, ...]
    state_ids: tuple[str, ...]
    initial_state_ids: tuple[str, ...]
    terminal_state_ids: tuple[str, ...]
    transitions: tuple[tuple[str, str], ...]
    invalid_transition_behavior: str = "typed_failure_without_state_change"

    def __post_init__(self) -> None:
        for value in (
            self.lifecycle_id,
            self.implementation_id,
            self.implementation_version,
            *self.participant_capability_ids,
            *self.state_ids,
            *self.initial_state_ids,
            *self.terminal_state_ids,
        ):
            _stable_id(value, "lifecycle_definition")
        if (
            self.owner_layer != "reducer"
            or self.invalid_transition_behavior
            != "typed_failure_without_state_change"
            or not self.participant_capability_ids
            or not self.state_ids
            or not self.initial_state_ids
            or len(self.participant_capability_ids)
            != len(set(self.participant_capability_ids))
            or len(self.state_ids) != len(set(self.state_ids))
            or len(self.initial_state_ids) != len(set(self.initial_state_ids))
            or len(self.terminal_state_ids) != len(set(self.terminal_state_ids))
            or not set(self.initial_state_ids) <= set(self.state_ids)
            or not set(self.terminal_state_ids) <= set(self.state_ids)
            or not self.transitions
            or len(self.transitions) != len(set(self.transitions))
            or any(
                source not in self.state_ids or target not in self.state_ids
                for source, target in self.transitions
            )
        ):
            raise LifecycleRuleError(
                f"lifecycle_definition_invalid:{self.lifecycle_id}"
            )

    def open_record(
        self,
        *,
        object_id: str,
        owner_actor_id: str,
        initial_state_id: str,
        predecessor_object_id: str | None = None,
        causal_parent_ids: Sequence[str] = (),
    ) -> LifecycleRecord:
        """Open a version-zero record at a declared initial state."""

        if initial_state_id not in self.initial_state_ids:
            raise LifecycleRuleError("lifecycle_initial_state_invalid")
        predecessor = (
            None
            if predecessor_object_id is None
            else _stable_id(predecessor_object_id, "predecessor_object_id")
        )
        parents = tuple(
            _stable_id(item, "causal_parent_id") for item in causal_parent_ids
        )
        if len(parents) != len(set(parents)):
            raise LifecycleRuleError("lifecycle_causal_parent_duplicate")
        return LifecycleRecord(
            object_id=_stable_id(object_id, "object_id"),
            lifecycle_id=self.lifecycle_id,
            owner_actor_id=_stable_id(owner_actor_id, "owner_actor_id"),
            state_id=initial_state_id,
            version=0,
            terminal=initial_state_id in self.terminal_state_ids,
            predecessor_object_id=predecessor,
            causal_parent_ids=parents,
        )

    def transition(
        self,
        record: LifecycleRecord,
        *,
        target_state_id: str,
        cause_id: str,
    ) -> LifecycleTransitionResult:
        """Apply one declared edge or return a typed unchanged result."""

        self._validate_record(record)
        cause = _stable_id(cause_id, "cause_id")
        if target_state_id not in self.state_ids:
            return LifecycleTransitionResult(
                applied=False,
                reason_code="lifecycle_target_state_unknown",
                cause_id=cause,
                before=record,
                after=record,
            )
        if (record.state_id, target_state_id) not in self.transitions:
            return LifecycleTransitionResult(
                applied=False,
                reason_code="lifecycle_transition_invalid",
                cause_id=cause,
                before=record,
                after=record,
            )
        after = replace(
            record,
            state_id=target_state_id,
            version=record.version + 1,
            terminal=target_state_id in self.terminal_state_ids,
            causal_parent_ids=tuple(
                dict.fromkeys((*record.causal_parent_ids, cause))
            ),
        )
        return LifecycleTransitionResult(
            applied=True,
            reason_code="lifecycle_transition_applied",
            cause_id=cause,
            before=record,
            after=after,
        )

    def _validate_record(self, record: LifecycleRecord) -> None:
        if (
            record.lifecycle_id != self.lifecycle_id
            or record.state_id not in self.state_ids
            or type(record.version) is not int
            or record.version < 0
            or type(record.terminal) is not bool
            or record.terminal != (record.state_id in self.terminal_state_ids)
        ):
            raise LifecycleRuleError("lifecycle_record_invalid")
        _stable_id(record.object_id, "object_id")
        _stable_id(record.owner_actor_id, "owner_actor_id")
        if record.predecessor_object_id is not None:
            _stable_id(record.predecessor_object_id, "predecessor_object_id")
        parents = tuple(
            _stable_id(item, "causal_parent_id")
            for item in record.causal_parent_ids
        )
        if len(parents) != len(set(parents)):
            raise LifecycleRuleError("lifecycle_record_parent_duplicate")


def chain_states(*states: str) -> tuple[tuple[str, str], ...]:
    """Return the adjacent directed edges for one declared state chain."""

    return tuple(zip(states, states[1:]))


__all__ = [
    "LifecycleRecord",
    "LifecycleRule",
    "LifecycleRuleError",
    "LifecycleTransitionResult",
    "chain_states",
]
