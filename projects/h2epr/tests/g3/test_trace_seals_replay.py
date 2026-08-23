from __future__ import annotations

import copy

import pytest

from masim.integrations.event_process import TraceWriter, canonical_sha256, replay_trace, validate_trace


def _apply(state, payload):
    assert state[payload["field_name"]] == payload["before"]
    state[payload["field_name"]] = payload["after"]


def _trace():
    writer = TraceWriter("run", "a" * 64)
    writer.append("tick_open", 1, {})
    writer.append("state_delta", 1, {"entity_id": "__world__", "field_name": "value", "before": 1, "after": 2})
    writer.append("tick_commit", 1, {"state_version": 1, "state_sha256": "unused"})
    # Build replay-compatible hash after version commit.
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


def _reseal_and_rehash(rows: list[dict]) -> None:
    previous = "0" * 64
    tick_hashes = []
    for index, row in enumerate(rows):
        row["previous_record_hash"] = previous
        payload = row["payload"]
        if row["record_type"] == "tick_seal":
            payload["seal_sha256"] = canonical_sha256(
                {key: value for key, value in payload.items() if key != "seal_sha256"}
            )
            tick_hashes.append(payload["seal_sha256"])
        elif row["record_type"] == "run_seal":
            payload["ordered_tick_seal_hashes"] = tick_hashes
            payload["scientific_prefix_sha256"] = canonical_sha256(rows[:index])
            payload["seal_sha256"] = canonical_sha256(
                {key: value for key, value in payload.items() if key != "seal_sha256"}
            )
        row["record_hash"] = canonical_sha256(
            {key: value for key, value in row.items() if key != "record_hash"}
        )
        previous = row["record_hash"]


def test_forged_tick_seal_cannot_override_record_count_semantics() -> None:
    rows = copy.deepcopy(_trace().records)
    tick_payload = next(row["payload"] for row in rows if row["record_type"] == "tick_seal")
    tick_payload["record_count"] += 1
    _reseal_and_rehash(rows)

    errors = validate_trace(rows)
    assert "TICK_SEAL_RECORD_COUNT_MISMATCH" in errors
    assert "RECORD_HASH_MISMATCH" not in errors
    assert "TICK_SEAL_HASH_MISMATCH" not in errors


def test_forged_run_seal_cannot_override_final_state_semantics() -> None:
    rows = copy.deepcopy(_trace().records)
    rows[-1]["payload"]["final_state_sha256"] = "b" * 64
    _reseal_and_rehash(rows)

    errors = validate_trace(rows)
    assert "RUN_SEAL_FINAL_STATE_HASH_MISMATCH" in errors
    assert "RUN_SEAL_HASH_MISMATCH" not in errors


def test_noncanonical_record_is_reported_without_aborting_validation() -> None:
    rows = copy.deepcopy(_trace().records)
    rows[0]["payload"]["unsupported"] = {"value"}

    errors = validate_trace(rows)
    assert "RECORD_NOT_CANONICALIZABLE" in errors
    assert "RUN_SEAL_PREFIX_NOT_CANONICALIZABLE" in errors


def test_malformed_tick_commit_payload_is_reported_without_attribute_error() -> None:
    rows = copy.deepcopy(_trace().records)
    commit = next(row for row in rows if row["record_type"] == "tick_commit")
    commit["payload"] = []

    errors = validate_trace(rows)
    assert "TICK_COMMIT_PAYLOAD_INVALID" in errors


def test_replay_reproduces_final_state() -> None:
    writer = _trace()
    assert replay_trace({"state_version": 0, "value": 1}, writer.records, _apply) == {"state_version": 1, "value": 2}
