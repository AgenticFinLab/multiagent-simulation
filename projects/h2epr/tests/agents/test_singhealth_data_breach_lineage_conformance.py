from __future__ import annotations

import copy
import json
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping

import pytest

from masim.integrations.event_process import canonical_sha256, validate_trace
from h2epr.scenarios.singhealth_data_breach.lineage_conformance_v0_1 import (
    LineageConformanceError,
    LineageProjection,
    build_positive_lineage,
    load_conformance_binding,
    replay_lineage_records,
    run_lineage_conformance,
    validate_lineage_projection,
    validate_lineage_trace_semantics,
)
from h2epr.scenarios.singhealth_data_breach.lineage_v0_1 import (
    LineageBindingError,
)
from support.schema_registry import definition_errors


def _records(run: Any, record_type: str) -> list[Mapping[str, Any]]:
    return [
        row["payload"]
        for row in run.records
        if row["record_type"] == record_type
    ]


def _reproject_action_and_message(
    projection: LineageProjection,
    *,
    action_key: str,
    action: Mapping[str, Any],
    message: Mapping[str, Any],
    semantic_updates: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    binding = projection.binding
    semantic_parameters = binding.semantic_values(action)
    semantic_parameters.update(copy.deepcopy(dict(semantic_updates)))
    drifted_action = binding.project_action(
        action_key,
        intent_id=action["intent_id"],
        run_id=action["run_id"],
        logical_tick=action["logical_tick"],
        decision_ref=action["decision_ref"],
        observation_refs=action["observation_refs"],
        semantic_parameters=semantic_parameters,
        earliest_effect_time=action["earliest_effect_time"],
    )
    drifted_message = binding.project_message(
        action_key,
        drifted_action,
        message_intent_id=message["message_intent_id"],
        earliest_delivery_time=message["earliest_delivery_time"],
        correlation_ids=message["correlation_ids"],
    )
    return drifted_action, drifted_message


def test_selected_projection_and_trace_payloads_fit_v1_carriers() -> None:
    run = run_lineage_conformance()

    for observation in run.projection.observations:
        assert definition_errors("ObservationPayload", observation) == []
    for action in run.projection.actions:
        assert definition_errors("ActionIntent", action) == []
    for message in run.projection.messages:
        assert definition_errors("MessageIntent", message) == []
    for disposition in _records(run, "action_disposition_recorded"):
        assert definition_errors("ActionDisposition", disposition) == []
    for disposition in _records(run, "communication_disposition_recorded"):
        assert definition_errors("CommunicationDisposition", disposition) == []
    for delta in _records(run, "state_delta"):
        assert definition_errors("StateDelta", delta) == []

    assert len(_records(run, "action_disposition_recorded")) == 4
    assert len(_records(run, "communication_disposition_recorded")) == 4
    assert len(_records(run, "state_delta")) == 10


def test_trace_and_replay_are_byte_deterministic_without_simulation() -> None:
    first = run_lineage_conformance()
    second = run_lineage_conformance()

    assert first.manifest == second.manifest
    assert first.records == second.records
    assert first.run_seal == second.run_seal
    assert first.final_state == first.replayed_state == second.final_state
    assert first.trace_errors() == []
    assert len(first.records) == 64
    assert {row["logical_tick"] for row in first.records} == set(range(9))
    assert first.manifest["simulation_started"] is False
    assert first.manifest["full_configuration_execution_enabled"] is False
    assert first.manifest["actor_ids"] == [
        "actor.0616.unit.technical.scm-application-database",
        "actor.0616.unit.operations.application-scm-coordination",
        "actor.0616.office.singhealth-gcio",
    ]
    assert len(first.manifest["action_keys"]) == 4
    assert len(first.manifest["route_ids"]) == 4
    assert first.manifest["verification_result_count"] == 1
    assert first.final_state["clarification_stage"] == (
        "delivered_awaiting_response"
    )
    assert first.run_seal["unresolved_intent_ids"] == [
        "intent.0616.gcio.request_clarification.001"
    ]
    assert first.run_seal["unresolved_recipient_ids"] == [
        "actor.0616.unit.operations.application-scm-coordination"
    ]


def test_external_binding_manifest_anchor_fails_closed_on_drift() -> None:
    with pytest.raises(LineageBindingError, match="LINEAGE_MANIFEST_HASH_MISMATCH"):
        load_conformance_binding(expected_manifest_sha256="0" * 64)


def test_selected_capacity_and_exact_delivery_gate_remain_closed() -> None:
    projection = build_positive_lineage()
    wrong_capacity = copy.deepcopy(projection.clarification_action)
    for field in wrong_capacity["parameters"]:
        if field["field_name"] == "capacity_id":
            field["runtime_value"]["value"] = "capacity.0616.singhealth.gcio"

    with pytest.raises(LineageBindingError, match="SEMANTIC_ENVELOPE_MISMATCH"):
        projection.binding.validate_action(
            "gcio.request_operational_clarification",
            wrong_capacity,
        )

    undelivered = replace(projection.verification_delivery, delivered=False)
    with pytest.raises(
        LineageConformanceError,
        match="LINEAGE_CONFORMANCE_DELIVERY_GATE_MISMATCH",
    ):
        validate_lineage_projection(
            replace(projection, verification_delivery=undelivered)
        )


def test_verification_request_rejects_well_formed_drifted_finding() -> None:
    projection = build_positive_lineage()
    action, message = _reproject_action_and_message(
        projection,
        action_key="operations.request_fact_verification",
        action=projection.verification_action,
        message=projection.verification_message,
        semantic_updates={
            "source_finding_id": "finding.0616.scm.unrelated.001",
        },
    )

    with pytest.raises(
        LineageConformanceError,
        match="LINEAGE_CONFORMANCE_VERIFICATION_REQUEST_LINEAGE_MISMATCH",
    ):
        validate_lineage_projection(
            replace(
                projection,
                verification_action=action,
                verification_message=message,
            )
        )


def test_verification_result_rejects_a_different_request_lineage() -> None:
    projection = build_positive_lineage()
    drifted_result = replace(
        projection.verification_result,
        request_id="request.0616.verify_unrelated.001",
    )

    with pytest.raises(
        LineageConformanceError,
        match="LINEAGE_CONFORMANCE_VERIFICATION_RESULT_LINEAGE_MISMATCH",
    ):
        validate_lineage_projection(
            replace(projection, verification_result=drifted_result)
        )

    with pytest.raises(
        LineageConformanceError,
        match="LINEAGE_CONFORMANCE_VERIFICATION_RESULT_LINEAGE_MISMATCH",
    ):
        validate_lineage_projection(
            replace(
                projection,
                verification_result_recipient_id=(
                    "actor.0616.unit.technical.scm-application-database"
                ),
            )
        )


def test_escalation_rejects_well_formed_drifted_result_reference() -> None:
    projection = build_positive_lineage()
    action, message = _reproject_action_and_message(
        projection,
        action_key="operations.escalate_operational_concern",
        action=projection.escalation_action,
        message=projection.escalation_message,
        semantic_updates={
            "verification_result_ref": "result.0616.verify_unrelated.001",
        },
    )

    with pytest.raises(
        LineageConformanceError,
        match="LINEAGE_CONFORMANCE_ESCALATION_LINEAGE_MISMATCH",
    ):
        validate_lineage_projection(
            replace(
                projection,
                escalation_action=action,
                escalation_message=message,
            )
        )


def test_clarification_rejects_well_formed_drifted_account() -> None:
    projection = build_positive_lineage()
    action, message = _reproject_action_and_message(
        projection,
        action_key="gcio.request_operational_clarification",
        action=projection.clarification_action,
        message=projection.clarification_message,
        semantic_updates={
            "cited_account_id": "account.0616.operations.unrelated.001",
        },
    )

    with pytest.raises(
        LineageConformanceError,
        match="LINEAGE_CONFORMANCE_CLARIFICATION_LINEAGE_MISMATCH",
    ):
        validate_lineage_projection(
            replace(
                projection,
                clarification_action=action,
                clarification_message=message,
            )
        )


def test_request_result_delivery_and_unresolved_reply_remain_separate() -> None:
    run = run_lineage_conformance()
    verification = run.projection.binding.semantic_values(
        run.projection.verification_action
    )
    result_fields = {
        "verification_result_ref",
        "verification_result_version",
        "verification_status",
        "verification_result_delivery_ref",
    }

    assert result_fields.isdisjoint(verification)
    assert all(
        action["resource_offer_or_request"] == []
        for action in run.projection.actions
    )
    assert len(_records(run, "verification_result_produced")) == 1
    assert len(_records(run, "verification_result_delivered")) == 1
    assert _records(run, "verification_result_delivered")[0][
        "recipient_actor_id"
    ] == "actor.0616.unit.operations.application-scm-coordination"
    assert run.final_state["verification_result_stage"] == "delivered"
    assert run.final_state["clarification_stage"] == (
        "delivered_awaiting_response"
    )


def test_same_tick_result_order_is_a_semantic_invariant() -> None:
    run = run_lineage_conformance()
    reordered = copy.deepcopy(list(run.records))
    produced_index = next(
        index
        for index, row in enumerate(reordered)
        if row["record_type"] == "verification_result_produced"
    )
    delivered_index = next(
        index
        for index, row in enumerate(reordered)
        if row["record_type"] == "verification_result_delivered"
    )
    reordered[produced_index], reordered[delivered_index] = (
        reordered[delivered_index],
        reordered[produced_index],
    )

    with pytest.raises(
        LineageConformanceError,
        match="LINEAGE_CONFORMANCE_TRACE_CAUSAL_ORDER_MISMATCH",
    ):
        validate_lineage_trace_semantics(reordered)


def test_trace_tamper_and_wrong_replay_prestate_are_rejected() -> None:
    run = run_lineage_conformance()
    tampered = copy.deepcopy(list(run.records))
    first_delta = next(
        row for row in tampered if row["record_type"] == "state_delta"
    )
    first_delta["payload"]["after"] = "invented_state"
    assert "RECORD_HASH_MISMATCH" in validate_trace(tampered)

    wrong_initial = dict(run.initial_state)
    wrong_initial["finding_stage"] = "already_issued"
    with pytest.raises(
        LineageConformanceError,
        match="LINEAGE_CONFORMANCE_REPLAY_PRESTATE_MISMATCH",
    ):
        replay_lineage_records(wrong_initial, run.records)


def test_closeout_receipt_matches_the_regenerated_expected_vector() -> None:
    run = run_lineage_conformance()
    project_root = Path(__file__).resolve().parents[2]
    receipt = json.loads(
        (
            project_root
            / "scenarios/singhealth_data_breach/"
            "lineage-conformance-v0.1/receipt.json"
        ).read_text(encoding="utf-8")
    )
    trace = receipt["trace"]
    scope = receipt["scope"]

    assert receipt["status"] == "accepted"
    assert receipt["verdict"] == "PASS_BOUNDED_LINEAGE_CONFORMANCE"
    assert set(receipt["binding"]) == {
        "release_manifest_sha256",
        "binding_sha256",
        "binding_surfaces_verified",
        "configuration_admission_surfaces_verified",
    }
    assert all(
        set(row) == {"check_id", "status", "summary"}
        and row["status"] == "pass"
        for row in receipt["verification"]
    )
    receipt_text = json.dumps(receipt, sort_keys=True)
    assert "worktree" not in receipt_text
    assert "git_diff" not in receipt_text
    assert "tests_passed" not in receipt_text
    assert receipt["binding"]["release_manifest_sha256"] == (
        run.projection.binding.release_manifest_sha256
    )
    assert receipt["binding"]["binding_sha256"] == (
        run.projection.binding.binding_sha256
    )
    assert scope["actor_ids"] == run.manifest["actor_ids"]
    assert scope["action_count"] == len(run.manifest["action_keys"])
    assert scope["route_count"] == len(run.manifest["route_ids"])
    assert scope["logical_tick_count"] == run.manifest["logical_tick_count"]
    assert scope["state_delta_count"] == run.manifest["state_delta_count"]
    assert scope["verification_result_count"] == run.manifest[
        "verification_result_count"
    ]
    assert scope["simulation_started"] is False
    assert scope["full_configuration_execution_enabled"] is False
    assert trace["conformance_implementation_sha256"] == run.manifest[
        "conformance_implementation_sha256"
    ]
    assert trace["conformance_run_manifest_sha256"] == run.manifest[
        "manifest_sha256"
    ]
    assert trace["record_count"] == len(run.records)
    assert trace["first_record_hash"] == run.records[0]["record_hash"]
    assert trace["final_record_hash"] == run.records[-1]["record_hash"]
    assert trace["ordered_tick_seal_hashes"] == [
        row["payload"]["seal_sha256"]
        for row in run.records
        if row["record_type"] == "tick_seal"
    ]
    assert trace["run_seal_sha256"] == run.run_seal["seal_sha256"]
    assert trace["scientific_prefix_sha256"] == run.run_seal[
        "scientific_prefix_sha256"
    ]
    assert trace["final_state_sha256"] == canonical_sha256(run.final_state)
    assert trace["replay_state_sha256"] == canonical_sha256(
        run.replayed_state
    )
    assert trace["trace_errors"] == run.trace_errors() == []
    assert trace["deterministic_repeat_equal"] is True
    assert receipt["open_boundary"]["unresolved_intent_ids"] == run.run_seal[
        "unresolved_intent_ids"
    ]
    assert receipt["open_boundary"]["unresolved_recipient_ids"] == (
        run.run_seal["unresolved_recipient_ids"]
    )
