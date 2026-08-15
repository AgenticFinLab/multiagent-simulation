"""Append-only hash-chained trace writer and deterministic replay checks."""

from __future__ import annotations

import copy
from typing import Any, Callable, Iterable, Mapping

from .seals import RunSeal, TickSeal, canonical_sha256


GENESIS_HASH = "0" * 64


class TraceWriter:
    def __init__(self, run_id: str, manifest_sha256: str) -> None:
        self.run_id = run_id
        self.manifest_sha256 = manifest_sha256
        self.records: list[dict[str, Any]] = []
        self._trace_ids: set[str] = set()
        self._tick_seals: list[TickSeal] = []

    def append(self, record_type: str, logical_tick: int, payload: Mapping[str, Any]) -> dict[str, Any]:
        if self.records and self.records[-1]["record_type"] == "run_seal":
            raise ValueError("record_after_run_seal")
        trace_id = f"trace.{self.run_id}.{len(self.records):08d}"
        if trace_id in self._trace_ids:
            raise ValueError("duplicate_trace_id")
        body = {
            "trace_id": trace_id,
            "run_id": self.run_id,
            "logical_tick": logical_tick,
            "sequence_in_run": len(self.records),
            "record_type": record_type,
            "payload": copy.deepcopy(dict(payload)),
            "previous_record_hash": self.records[-1]["record_hash"] if self.records else GENESIS_HASH,
        }
        body["record_hash"] = canonical_sha256(body)
        self.records.append(body)
        self._trace_ids.add(trace_id)
        return copy.deepcopy(body)

    def seal_tick(self, logical_tick: int, state: Mapping[str, Any]) -> TickSeal:
        current = [item for item in self.records if item["logical_tick"] == logical_tick]
        if not current or any(item["record_type"] == "tick_seal" for item in current):
            raise ValueError("tick_seal_cardinality_violation")
        seal = TickSeal(
            self.run_id,
            logical_tick,
            self.manifest_sha256,
            current[0]["record_hash"],
            current[-1]["record_hash"],
            canonical_sha256(state),
            len(current),
        ).sealed()
        self.append("tick_seal", logical_tick, seal.to_dict())
        self._tick_seals.append(seal)
        return seal

    def seal_run(
        self,
        final_state: Mapping[str, Any],
        unresolved_intent_ids: tuple[str, ...],
        unresolved_recipient_ids: tuple[str, ...],
    ) -> RunSeal:
        prefix_hash = canonical_sha256(self.records)
        seal = RunSeal(
            self.run_id,
            self.manifest_sha256,
            tuple(item.seal_sha256 for item in self._tick_seals),
            prefix_hash,
            canonical_sha256(final_state),
            tuple(sorted(set(unresolved_intent_ids))),
            tuple(sorted(set(unresolved_recipient_ids))),
        ).sealed()
        final_tick = self._tick_seals[-1].logical_tick if self._tick_seals else 0
        self.append("run_seal", final_tick, seal.to_dict())
        return seal


def validate_trace(records: Iterable[Mapping[str, Any]]) -> list[str]:
    rows = [dict(item) for item in records]
    errors: list[str] = []
    ids: set[str] = set()
    previous = GENESIS_HASH
    tick_seals: dict[int, int] = {}
    for index, row in enumerate(rows):
        trace_id = row.get("trace_id")
        if trace_id in ids:
            errors.append("DUPLICATE_TRACE_ID")
        ids.add(trace_id)
        if row.get("sequence_in_run") != index:
            errors.append("SEQUENCE_MISMATCH")
        if row.get("previous_record_hash") != previous:
            errors.append("CHAIN_PREDECESSOR_MISMATCH")
        preimage = {key: value for key, value in row.items() if key != "record_hash"}
        if row.get("record_hash") != canonical_sha256(preimage):
            errors.append("RECORD_HASH_MISMATCH")
        previous = row.get("record_hash")
        if row.get("record_type") == "tick_seal":
            tick = row.get("logical_tick")
            tick_seals[tick] = tick_seals.get(tick, 0) + 1
        elif row.get("record_type") != "run_seal" and tick_seals.get(row.get("logical_tick"), 0):
            errors.append("RECORD_AFTER_TICK_SEAL")
    if rows and rows[-1].get("record_type") != "run_seal":
        errors.append("RUN_SEAL_NOT_FINAL")
    scientific_ticks = {row["logical_tick"] for row in rows if row.get("record_type") not in {"run_seal"}}
    if any(tick_seals.get(tick) != 1 for tick in scientific_ticks):
        errors.append("TICK_SEAL_CARDINALITY")
    return sorted(set(errors))


def replay_trace(
    initial_state: Mapping[str, Any],
    records: Iterable[Mapping[str, Any]],
    apply_delta: Callable[[dict[str, Any], Mapping[str, Any]], None],
) -> dict[str, Any]:
    rows = list(records)
    errors = validate_trace(rows)
    if errors:
        raise ValueError("invalid_trace:" + ",".join(errors))
    state = copy.deepcopy(dict(initial_state))
    for row in rows:
        if row["record_type"] == "state_delta":
            apply_delta(state, row["payload"])
        elif row["record_type"] == "tick_commit":
            state["state_version"] = row["payload"]["state_version"]
            if canonical_sha256(state) != row["payload"]["state_sha256"]:
                raise ValueError("replay_state_hash_mismatch")
    return state
