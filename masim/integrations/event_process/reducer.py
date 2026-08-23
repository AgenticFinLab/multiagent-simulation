"""Single-authority, deterministic event-process reducer mechanics."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping

from .model import ActionDisposition, ActionIntent, StateDelta
from .seals import canonical_sha256


@dataclass(frozen=True)
class ReducerResult:
    state: dict[str, Any]
    dispositions: tuple[ActionDisposition, ...]
    deltas: tuple[StateDelta, ...]
    prestate_sha256: str
    poststate_sha256: str


class AuthoritativeReducer:
    """Owns the sole state commit and delegates domain effects to one callback."""

    def __init__(
        self,
        state: Mapping[str, Any],
        apply_batch: Callable[[dict[str, Any], tuple[ActionIntent, ...], int, int], tuple[list[ActionDisposition], list[StateDelta]]],
    ) -> None:
        self._state = copy.deepcopy(dict(state))
        self._apply_batch = apply_batch
        self._seen_intent_ids: set[str] = set()

    @property
    def state(self) -> dict[str, Any]:
        return copy.deepcopy(self._state)

    def reduce(
        self,
        intents: Iterable[ActionIntent],
        *,
        logical_tick: int,
        run_seed: int,
    ) -> ReducerResult:
        ordered = tuple(sorted(intents, key=lambda value: value.intent_id))
        if len({item.intent_id for item in ordered}) != len(ordered):
            raise ValueError("duplicate_intent_id_in_batch")
        prestate = copy.deepcopy(self._state)
        prestate_hash = canonical_sha256(prestate)
        version = prestate.get("state_version")
        if isinstance(version, bool) or not isinstance(version, int):
            raise ValueError("invalid_state_version")
        for intent in ordered:
            if intent.logical_tick != logical_tick:
                raise ValueError("intent_tick_mismatch")
            if intent.prestate_version != version or intent.prestate_sha256 != prestate_hash:
                raise ValueError("intent_prestate_mismatch")
            if intent.intent_id in self._seen_intent_ids:
                raise ValueError("cross_tick_duplicate_intent_id")
        working_state = copy.deepcopy(prestate)
        dispositions, deltas = self._apply_batch(working_state, ordered, run_seed, logical_tick)
        if {item.intent_id for item in dispositions} != {item.intent_id for item in ordered}:
            raise ValueError("disposition_intent_closure_mismatch")
        delta_ids = {item.delta_id for item in deltas}
        if len(delta_ids) != len(deltas):
            raise ValueError("duplicate_delta_id")
        referenced = {delta for item in dispositions for delta in item.state_delta_ids}
        if referenced != delta_ids:
            raise ValueError("disposition_delta_closure_mismatch")
        working_state["state_version"] = version + 1
        self._state = working_state
        self._seen_intent_ids.update(item.intent_id for item in ordered)
        poststate_hash = canonical_sha256(self._state)
        return ReducerResult(
            copy.deepcopy(self._state),
            tuple(dispositions),
            tuple(deltas),
            prestate_hash,
            poststate_hash,
        )
