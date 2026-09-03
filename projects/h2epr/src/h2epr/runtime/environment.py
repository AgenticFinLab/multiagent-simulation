"""Order-independent declarative environment for current packages."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Mapping

from h2epr.canonical import canonical_sha256
from h2epr.masim_kernel import ActionDisposition, ActionIntent, StateDelta

from ._environment_core import (
    _DeclarativeEnvironmentBase,
    _DeclarativeEnvironmentCoreError,
    _identifier,
    _apply_delta,
    condition_matches,
)


class DeclarativeEnvironmentError(_DeclarativeEnvironmentCoreError):
    """A batch cannot be admitted without an order-independent result."""


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise DeclarativeEnvironmentError(code)


def _semantic_intent_key(intent: ActionIntent) -> tuple[str, str, str, str]:
    """Order scientific intents without using run-derived identifiers."""

    return (
        intent.actor_id,
        intent.action_type,
        canonical_sha256(dict(intent.parameters)),
        intent.policy_id,
    )


@dataclass(frozen=True)
class _Candidate:
    intent: ActionIntent
    planned: tuple[tuple[Mapping[str, Any], Any, Any], ...]


class DeclarativeEnvironment(_DeclarativeEnvironmentBase):
    """Reject every distinct concurrent writer before applying any write."""

    conflict_policy = (
        "reject_distinct_concurrent_writes_allow_idempotent_same_value"
    )

    def __init__(self, scenario: Mapping[str, Any]) -> None:
        super().__init__(scenario)
        _require(
            scenario["mechanism"]["conflict_policy"] == self.conflict_policy,
            "conflict_policy_mismatch",
        )

    def apply_batch(
        self,
        state: dict[str, Any],
        intents: tuple[ActionIntent, ...],
        run_seed: int,
        logical_tick: int,
    ) -> tuple[list[ActionDisposition], list[StateDelta]]:
        del run_seed
        _require(
            len({intent.actor_id for intent in intents}) == len(intents),
            "duplicate_actor_intent_in_batch",
        )
        prestate = copy.deepcopy(state)
        ordered = sorted(intents, key=_semantic_intent_key)
        rejected: dict[str, str] = {}
        candidates: list[_Candidate] = []

        for intent in ordered:
            handler = self.handlers.get(intent.action_type)
            if handler is None:
                rejected[intent.intent_id] = "intent_handler_missing"
                continue
            if intent.actor_id not in handler["eligible_actors"]:
                rejected[intent.intent_id] = "actor_not_authorized"
                continue
            parameters = dict(intent.parameters)
            parameter_error = self._parameter_error(handler, parameters)
            if parameter_error:
                rejected[intent.intent_id] = parameter_error
                continue
            target = parameters[handler["target_parameter"]]
            if target not in handler["eligible_targets"]:
                rejected[intent.intent_id] = "target_not_eligible"
                continue
            precondition_error = self._precondition_error(handler, prestate)
            if precondition_error:
                rejected[intent.intent_id] = precondition_error
                continue
            planned = tuple(self._planned_effects(handler, parameters, prestate))
            candidates.append(_Candidate(intent, planned))

        writers: dict[
            tuple[str, str],
            list[tuple[_Candidate, Mapping[str, Any], Any]],
        ] = {}
        for candidate in candidates:
            for effect, _before, after in candidate.planned:
                key = effect["entity_id"], effect["field_name"]
                writers.setdefault(key, []).append((candidate, effect, after))

        for rows in writers.values():
            if len(rows) < 2:
                continue
            idempotent = all(
                effect["operation"] == "set" and after == rows[0][2]
                for _candidate, effect, after in rows
            )
            if idempotent:
                continue
            for candidate, _effect, _after in rows:
                rejected[candidate.intent.intent_id] = "concurrent_field_conflict"

        dispositions: list[ActionDisposition] = []
        deltas: list[StateDelta] = []
        for candidate in candidates:
            intent = candidate.intent
            if intent.intent_id in rejected:
                continue
            intent_deltas: list[StateDelta] = []
            for index, (effect, _before, after) in enumerate(candidate.planned):
                key = effect["entity_id"], effect["field_name"]
                current = state["entities"][key[0]][key[1]]
                if current == after:
                    continue
                delta = StateDelta(
                    delta_id=(
                        f"delta.{_identifier(intent.intent_id, key[0], key[1], index)}"
                    ),
                    source_intent_id=intent.intent_id,
                    entity_id=key[0],
                    field_name=key[1],
                    before=copy.deepcopy(current),
                    after=copy.deepcopy(after),
                    delta_class=effect.get("delta_class", "declared_effect"),
                )
                state["entities"][key[0]][key[1]] = copy.deepcopy(after)
                intent_deltas.append(delta)
            deltas.extend(intent_deltas)
            reason = "admitted_applied" if intent_deltas else "admitted_no_effect"
            dispositions.append(
                ActionDisposition(
                    disposition_id=(
                        f"ad.{_identifier(intent.intent_id, logical_tick, reason)}"
                    ),
                    intent_id=intent.intent_id,
                    logical_tick=logical_tick,
                    status="accepted",
                    reason_code=reason,
                    state_delta_ids=tuple(row.delta_id for row in intent_deltas),
                )
            )

        accepted_ids = {row.intent_id for row in dispositions}
        for intent in ordered:
            if intent.intent_id in accepted_ids:
                continue
            reason = rejected.get(intent.intent_id)
            _require(reason is not None, "intent_disposition_missing")
            dispositions.append(self._reject(intent, logical_tick, reason))
        dispositions.sort(
            key=lambda row: _semantic_intent_key(
                next(intent for intent in ordered if intent.intent_id == row.intent_id)
            )
        )
        return dispositions, deltas


def build_environment(
    scenario: Mapping[str, Any],
) -> DeclarativeEnvironment:
    return DeclarativeEnvironment(scenario)


def apply_delta(state: dict[str, Any], delta: Mapping[str, Any]) -> None:
    _apply_delta(state, delta)


__all__ = [
    "DeclarativeEnvironment",
    "DeclarativeEnvironmentError",
    "apply_delta",
    "build_environment",
    "condition_matches",
]
