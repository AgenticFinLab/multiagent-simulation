from __future__ import annotations

import copy

import pytest

from masim.integrations.event_process import TraceWriter, replay_trace, validate_trace


def _apply(state, payload):
    assert state[payload["field_name"]] == payload["before"]
    state[payload["field_name"]] = payload["after"]


def _trace():
    writer = TraceWriter("run", "a" * 64)
    writer.append("tick_open", 1, {})
    writer.append("state_delta", 1, {"entity_id": "__world__", "field_name": "value", "before": 1, "after": 2})
    writer.append("tick_commit", 1, {"state_version": 1, "state_sha256": "unused"})
    # Build replay-compatible hash after version commit.
    from masim.integrations.event_process import canonical_sha256
    writer.records[-1]["payload"]["state_sha256"] = canonical_sha256({"state_version": 1, "value": 2})
    writer.records[-1]["record_hash"] = canonical_sha256({k: v for k, v in writer.records[-1].items() if k != "record_hash"})
    writer.seal_tick(1, {"state_version": 1, "value": 2})
    writer.seal_run({"state_version": 1, "value": 2}, (), ())
    return writer


def test_hash_chain_tick_and_run_seal_validate() -> None:
    writer = _trace()
    assert validate_trace(writer.records) == []
    assert writer.records[-1]["record_type"] == "run_seal"


def test_mutated_record_breaks_hash_chain() -> None:
    rows = copy.deepcopy(_trace().records)
    rows[1]["payload"]["after"] = 9
    assert "RECORD_HASH_MISMATCH" in validate_trace(rows)


def test_duplicate_tick_seal_is_rejected() -> None:
    writer = TraceWriter("run", "a" * 64)
    writer.append("tick_open", 1, {})
    writer.seal_tick(1, {})
    with pytest.raises(ValueError, match="cardinality"):
        writer.seal_tick(1, {})


def test_replay_reproduces_final_state() -> None:
    writer = _trace()
    assert replay_trace({"state_version": 0, "value": 1}, writer.records, _apply) == {"state_version": 1, "value": 2}
