from __future__ import annotations

import copy
import json
from dataclasses import replace
from pathlib import Path

import pytest

from h2epr.scenarios.samsung_note7_battery_recall.lineage_conformance_v0_1 import (
    Note7LineageConformanceError,
    build_positive_note7_lineage,
    replay_note7_lineage_records,
    run_note7_lineage_conformance,
    validate_note7_lineage_projection,
    validate_note7_lineage_trace_semantics,
)
from masim.integrations.event_process import validate_trace
from support.schema_registry import definition_errors


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_expected_vector_is_deterministic_replayable_and_open_at_fulfillment() -> None:
    first = run_note7_lineage_conformance()
    second = run_note7_lineage_conformance()

    assert first.manifest == second.manifest
    assert first.records == second.records
    assert first.run_seal == second.run_seal
    assert len(first.records) == 101
    assert first.trace_errors() == []
    assert first.replayed_state == first.final_state
    assert first.final_state == {
        "state_version": 15,
        "direction_stage": "delivered",
        "program_stage": "delivered",
        "coordination_stage": "delivered",
        "proposal_stage": "delivered",
        "posture_stage": "admitted",
        "offer_stage": "delivered",
        "request_stage": "delivered",
        "response_stage": "delivered_awaiting_fulfillment",
    }
    assert first.run_seal["unresolved_intent_ids"] == ["intent.0481.consumer.request.001"]
    assert first.run_seal["unresolved_recipient_ids"] == [
        "actor.0481.unit.outlet-singapore-channel"
    ]


def test_trace_payloads_use_v1_carriers_where_the_contract_applies() -> None:
    run = run_note7_lineage_conformance()
    contract_names = {
        "observation_delivered": "ObservationPayload",
        "action_intent_created": "ActionIntent",
        "action_disposition_recorded": "ActionDisposition",
        "message_intent_created": "MessageIntent",
        "communication_disposition_recorded": "CommunicationDisposition",
        "state_delta": "StateDelta",
    }

    for record in run.records:
        contract_name = contract_names.get(record["record_type"])
        if contract_name is not None:
            assert definition_errors(contract_name, record["payload"]) == []


def test_cross_hop_request_and_response_substitution_is_rejected() -> None:
    projection = build_positive_note7_lineage()

    request_values = projection.binding.semantic_values(projection.request_action)
    request_values["offer_id"] = "offer.0481.synthetic.other.v0"
    wrong_request = projection.binding.project_action(
        "consumer.request_exchange_or_refund",
        intent_id=projection.request_action["intent_id"],
        run_id=projection.request_action["run_id"],
        logical_tick=projection.request_action["logical_tick"],
        decision_ref=projection.request_action["decision_ref"],
        observation_refs=projection.request_action["observation_refs"],
        semantic_parameters=request_values,
        earliest_effect_time=projection.request_action["earliest_effect_time"],
    )
    wrong_request_message = projection.binding.project_message(
        "consumer.request_exchange_or_refund",
        wrong_request,
        message_intent_id=projection.request_message["message_intent_id"],
        earliest_delivery_time=projection.request_message["earliest_delivery_time"],
        correlation_ids=projection.request_message["correlation_ids"],
    )
    with pytest.raises(Note7LineageConformanceError, match="REQUEST_LINEAGE_MISMATCH"):
        validate_note7_lineage_projection(
            replace(
                projection,
                request_action=wrong_request,
                request_message=wrong_request_message,
            )
        )

    response_values = projection.binding.semantic_values(projection.response_action)
    response_values["request_message_ref"] = "message.0481.consumer_to_outlet.other.001"
    wrong_response = projection.binding.project_action(
        "outlet.respond_to_remedy_request",
        intent_id=projection.response_action["intent_id"],
        run_id=projection.response_action["run_id"],
        logical_tick=projection.response_action["logical_tick"],
        decision_ref=projection.response_action["decision_ref"],
        observation_refs=projection.response_action["observation_refs"],
        semantic_parameters=response_values,
        earliest_effect_time=projection.response_action["earliest_effect_time"],
    )
    wrong_response_message = projection.binding.project_message(
        "outlet.respond_to_remedy_request",
        wrong_response,
        message_intent_id=projection.response_message["message_intent_id"],
        earliest_delivery_time=projection.response_message["earliest_delivery_time"],
        correlation_ids=projection.response_message["correlation_ids"],
    )
    with pytest.raises(Note7LineageConformanceError, match="RESPONSE_LINEAGE_MISMATCH"):
        validate_note7_lineage_projection(
            replace(
                projection,
                response_action=wrong_response,
                response_message=wrong_response_message,
            )
        )


def test_semantic_trace_order_rejects_same_records_in_the_wrong_order() -> None:
    run = run_note7_lineage_conformance()
    tampered = list(copy.deepcopy(run.records))
    posture = next(
        index
        for index, row in enumerate(tampered)
        if row["record_type"] == "product_posture_result_produced"
    )
    offer = next(
        index
        for index, row in enumerate(tampered)
        if row["record_type"] == "remedy_offer_delivered"
    )
    tampered[posture], tampered[offer] = tampered[offer], tampered[posture]

    with pytest.raises(Note7LineageConformanceError, match="TRACE_EVENT_TICK_MISMATCH|TRACE_CAUSAL_ORDER_MISMATCH"):
        validate_note7_lineage_trace_semantics(tampered)


def test_trace_mutation_and_wrong_replay_prestate_are_detected() -> None:
    run = run_note7_lineage_conformance()
    tampered = list(copy.deepcopy(run.records))
    delta = next(row for row in tampered if row["record_type"] == "state_delta")
    delta["payload"]["after"] = "fabricated"
    assert "RECORD_HASH_MISMATCH" in validate_trace(tampered)

    wrong_initial = dict(run.initial_state)
    wrong_initial["direction_stage"] = "already_issued"
    with pytest.raises(Note7LineageConformanceError, match="REPLAY_PRESTATE_MISMATCH"):
        replay_note7_lineage_records(wrong_initial, run.records)


def test_closeout_receipt_matches_the_regenerated_vector() -> None:
    run = run_note7_lineage_conformance()
    receipt = json.loads(
        (
            PROJECT_ROOT
            / "scenarios/samsung_note7_battery_recall/lineage-conformance-v0.1/receipt.json"
        ).read_text(encoding="utf-8")
    )

    assert receipt["status"] == "accepted"
    assert receipt["verdict"] == "PASS_BOUNDED_LINEAGE_CONFORMANCE"
    assert receipt["binding"]["release_manifest_sha256"] == run.projection.binding.release_manifest_sha256
    assert receipt["binding"]["binding_sha256"] == run.projection.binding.binding_sha256
    assert receipt["scope"]["actor_ids"] == run.manifest["actor_ids"]
    assert receipt["scope"]["action_count"] == len(run.manifest["action_keys"])
    assert receipt["scope"]["route_count"] == len(run.manifest["route_ids"])
    assert receipt["scope"]["logical_tick_count"] == run.manifest["logical_tick_count"]
    assert receipt["scope"]["state_delta_count"] == run.manifest["state_delta_count"]
    assert receipt["trace"]["conformance_implementation_sha256"] == run.manifest["conformance_implementation_sha256"]
    assert receipt["trace"]["conformance_run_manifest_sha256"] == run.manifest["manifest_sha256"]
    assert receipt["trace"]["record_count"] == len(run.records)
    assert receipt["trace"]["first_record_hash"] == run.records[0]["record_hash"]
    assert receipt["trace"]["final_record_hash"] == run.records[-1]["record_hash"]
    assert receipt["trace"]["ordered_tick_seal_hashes"] == [
        row["payload"]["seal_sha256"]
        for row in run.records
        if row["record_type"] == "tick_seal"
    ]
    assert receipt["trace"]["scientific_prefix_sha256"] == run.run_seal["scientific_prefix_sha256"]
    assert receipt["trace"]["run_seal_sha256"] == run.run_seal["seal_sha256"]
    assert receipt["trace"]["final_state_sha256"] == run.run_seal["final_state_sha256"]
    assert receipt["trace"]["replay_state_sha256"] == run.run_seal["final_state_sha256"]
    assert receipt["open_boundary"]["unresolved_intent_ids"] == run.run_seal["unresolved_intent_ids"]
    assert receipt["open_boundary"]["unresolved_recipient_ids"] == run.run_seal["unresolved_recipient_ids"]
    assert all(row["status"] == "pass" for row in receipt["verification"])
    receipt_text = json.dumps(receipt, sort_keys=True)
    assert "worktree" not in receipt_text
    assert "git_diff" not in receipt_text
    assert "tests_passed" not in receipt_text
