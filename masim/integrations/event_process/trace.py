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
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    for item in records:
        if not isinstance(item, Mapping):
            errors.append("INVALID_RECORD")
            rows.append({})
        else:
            rows.append(dict(item))

    ids: set[str] = set()
    previous = GENESIS_HASH
    expected_run_id: str | None = None
    sealed_ticks: set[int] = set()
    tick_seal_rows: list[tuple[int, dict[str, Any]]] = []
    run_seal_rows: list[tuple[int, dict[str, Any]]] = []
    for index, row in enumerate(rows):
        trace_id = row.get("trace_id")
        if not isinstance(trace_id, str) or not trace_id:
            errors.append("INVALID_TRACE_ID")
        elif trace_id in ids:
            errors.append("DUPLICATE_TRACE_ID")
        else:
            ids.add(trace_id)
        run_id = row.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            errors.append("INVALID_RUN_ID")
        elif expected_run_id is None:
            expected_run_id = run_id
        elif run_id != expected_run_id:
            errors.append("RECORD_RUN_ID_MISMATCH")
        logical_tick = row.get("logical_tick")
        if isinstance(logical_tick, bool) or not isinstance(logical_tick, int) or logical_tick < 0:
            errors.append("INVALID_LOGICAL_TICK")
        if row.get("sequence_in_run") != index:
            errors.append("SEQUENCE_MISMATCH")
        if row.get("previous_record_hash") != previous:
            errors.append("CHAIN_PREDECESSOR_MISMATCH")
        preimage = {key: value for key, value in row.items() if key != "record_hash"}
        try:
            record_hash = canonical_sha256(preimage)
        except (TypeError, ValueError):
            errors.append("RECORD_NOT_CANONICALIZABLE")
            record_hash = None
        if row.get("record_hash") != record_hash:
            errors.append("RECORD_HASH_MISMATCH")
        previous = row.get("record_hash")
        if row.get("record_type") == "tick_seal":
            tick_seal_rows.append((index, row))
            if isinstance(logical_tick, int) and not isinstance(logical_tick, bool):
                sealed_ticks.add(logical_tick)
        elif row.get("record_type") == "run_seal":
            run_seal_rows.append((index, row))
        elif logical_tick in sealed_ticks:
            errors.append("RECORD_AFTER_TICK_SEAL")

    if len(run_seal_rows) != 1:
        errors.append("RUN_SEAL_CARDINALITY")
    if not rows or rows[-1].get("record_type") != "run_seal":
        errors.append("RUN_SEAL_NOT_FINAL")
    scientific_ticks = {
        row.get("logical_tick")
        for row in rows
        if row.get("record_type") != "run_seal"
        and isinstance(row.get("logical_tick"), int)
        and not isinstance(row.get("logical_tick"), bool)
    }
    seal_count_by_tick = {
        tick: sum(row.get("logical_tick") == tick for _, row in tick_seal_rows)
        for tick in scientific_ticks
    }
    if any(seal_count_by_tick.get(tick) != 1 for tick in scientific_ticks):
        errors.append("TICK_SEAL_CARDINALITY")

    verified_tick_seals: list[tuple[int, TickSeal]] = []
    for seal_index, row in tick_seal_rows:
        tick = row.get("logical_tick")
        payload = row.get("payload")
        try:
            seal = TickSeal.from_dict(payload)
        except (KeyError, TypeError, ValueError):
            errors.append("TICK_SEAL_PAYLOAD_INVALID")
            continue
        if not seal.verify():
            errors.append("TICK_SEAL_HASH_MISMATCH")
        if seal.run_id != row.get("run_id"):
            errors.append("TICK_SEAL_RUN_ID_MISMATCH")
        if seal.logical_tick != tick:
            errors.append("TICK_SEAL_TICK_MISMATCH")
        preseal_rows = [
            item
            for prior_index, item in enumerate(rows[:seal_index])
            if item.get("logical_tick") == tick
            and item.get("record_type") not in {"tick_seal", "run_seal"}
        ]
        if not preseal_rows:
            errors.append("TICK_SEAL_WITHOUT_RECORDS")
        else:
            if seal.first_record_hash != preseal_rows[0].get("record_hash"):
                errors.append("TICK_SEAL_FIRST_HASH_MISMATCH")
            if seal.final_preseal_record_hash != preseal_rows[-1].get("record_hash"):
                errors.append("TICK_SEAL_FINAL_HASH_MISMATCH")
        if seal.record_count != len(preseal_rows):
            errors.append("TICK_SEAL_RECORD_COUNT_MISMATCH")
        commits = [item for item in preseal_rows if item.get("record_type") == "tick_commit"]
        if len(commits) > 1:
            errors.append("TICK_COMMIT_CARDINALITY")
        elif commits:
            commit_payload = commits[0].get("payload")
            if not isinstance(commit_payload, Mapping):
                errors.append("TICK_COMMIT_PAYLOAD_INVALID")
            elif seal.state_sha256 != commit_payload.get("state_sha256"):
                errors.append("TICK_SEAL_STATE_HASH_MISMATCH")
        verified_tick_seals.append((seal_index, seal))

    manifests = {seal.manifest_sha256 for _, seal in verified_tick_seals}
    if len(manifests) > 1:
        errors.append("TICK_SEAL_MANIFEST_MISMATCH")
    if len(run_seal_rows) == 1:
        run_index, row = run_seal_rows[0]
        try:
            run_seal = RunSeal.from_dict(row.get("payload"))
        except (KeyError, TypeError, ValueError):
            errors.append("RUN_SEAL_PAYLOAD_INVALID")
        else:
            if not run_seal.verify():
                errors.append("RUN_SEAL_HASH_MISMATCH")
            if run_seal.run_id != row.get("run_id"):
                errors.append("RUN_SEAL_RUN_ID_MISMATCH")
            if manifests and run_seal.manifest_sha256 not in manifests:
                errors.append("RUN_SEAL_MANIFEST_MISMATCH")
            ordered_seals = [seal for index, seal in verified_tick_seals if index < run_index]
            if run_seal.ordered_tick_seal_hashes != tuple(
                seal.seal_sha256 for seal in ordered_seals
            ):
                errors.append("RUN_SEAL_TICK_SET_MISMATCH")
            try:
                prefix_sha256 = canonical_sha256(rows[:run_index])
            except (TypeError, ValueError):
                errors.append("RUN_SEAL_PREFIX_NOT_CANONICALIZABLE")
            else:
                if run_seal.scientific_prefix_sha256 != prefix_sha256:
                    errors.append("RUN_SEAL_PREFIX_HASH_MISMATCH")
            if ordered_seals:
                if row.get("logical_tick") != ordered_seals[-1].logical_tick:
                    errors.append("RUN_SEAL_TICK_MISMATCH")
                if run_seal.final_state_sha256 != ordered_seals[-1].state_sha256:
                    errors.append("RUN_SEAL_FINAL_STATE_HASH_MISMATCH")
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
