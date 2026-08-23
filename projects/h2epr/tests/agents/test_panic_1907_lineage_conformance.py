from __future__ import annotations

import copy
import json
from dataclasses import replace
from pathlib import Path

import pytest

from masim.integrations.event_process import canonical_sha256, validate_trace
from scenarios.panic_1907.lineage_conformance_v0_1 import (
    LineageConformanceError,
    build_positive_lineage,
    load_conformance_binding,
    replay_lineage_records,
    run_lineage_conformance,
    validate_lineage_projection,
)
from scenarios.panic_1907.lineage_v0_1 import (
    LineageBindingError,
    PositiveLineagePoliciesV0_1,
)
from support.schema_registry import definition_errors


def _records(run, record_type: str) -> list[dict]:
    return [
        row["payload"] for row in run.records if row["record_type"] == record_type
    ]


def test_e7_projection_and_trace_payloads_fit_the_selected_v1_carriers() -> None:
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
    assert len(_records(run, "communication_disposition_recorded")) == 3
    assert len(_records(run, "state_delta")) == 8


def test_e7_trace_and_replay_are_byte_deterministic_without_simulation() -> None:
    first = run_lineage_conformance()
    second = run_lineage_conformance()

    assert first.manifest == second.manifest
    assert first.records == second.records
    assert first.run_seal == second.run_seal
    assert first.final_state == first.replayed_state == second.final_state
    assert first.trace_errors() == []
    assert len(first.records) == 50
    assert {row["logical_tick"] for row in first.records} == {0, 1, 2, 3, 4}
    assert first.manifest["simulation_started"] is False
    assert first.manifest["full_configuration_execution_enabled"] is False


def test_external_e6_manifest_anchor_fails_closed_on_drift() -> None:
    with pytest.raises(LineageBindingError, match="LINEAGE_MANIFEST_HASH_MISMATCH"):
        load_conformance_binding(expected_manifest_sha256="0" * 64)


@pytest.mark.parametrize(
    ("field_name", "replacement", "error_code"),
    (
        (
            "target_entity_ids",
            ["actor.new_york_clearing_house"],
            "LINEAGE_ACTION_TARGET_MISMATCH",
        ),
        (
            "claimed_authority_refs",
            ["auth.unrelated"],
            "LINEAGE_ACTION_AUTHORITY_MISMATCH",
        ),
    ),
)
def test_kt_cannot_bypass_nbc_or_borrow_authority(
    field_name: str,
    replacement: list[str],
    error_code: str,
) -> None:
    projection = build_positive_lineage()
    mutated = copy.deepcopy(projection.kt_action)
    mutated[field_name] = replacement

    with pytest.raises(LineageBindingError, match=error_code):
        projection.binding.validate_action("kt.submit_support_request", mutated)


def test_cross_hop_validator_rejects_valid_carrier_with_drifted_nbc_provenance() -> None:
    projection = build_positive_lineage()
    binding = projection.binding
    semantic_parameters = binding.semantic_values(projection.nbc_action)
    semantic_parameters["original_request_content_sha256"] = "0" * 64
    drifted_action = binding.project_action(
        "nbc.forward_request_with_provenance",
        intent_id=projection.nbc_action["intent_id"],
        run_id=projection.nbc_action["run_id"],
        logical_tick=projection.nbc_action["logical_tick"],
        decision_ref=projection.nbc_action["decision_ref"],
        observation_refs=projection.nbc_action["observation_refs"],
        semantic_parameters=semantic_parameters,
        earliest_effect_time=projection.nbc_action["earliest_effect_time"],
    )
    drifted_message = binding.project_message(
        "nbc.forward_request_with_provenance",
        drifted_action,
        message_intent_id=projection.nbc_message["message_intent_id"],
        earliest_delivery_time=projection.nbc_message["earliest_delivery_time"],
        correlation_ids=projection.nbc_message["correlation_ids"],
    )

    with pytest.raises(
        LineageConformanceError,
        match="LINEAGE_CONFORMANCE_NBC_PROVENANCE_MISMATCH",
    ):
        validate_lineage_projection(
            replace(
                projection,
                nbc_action=drifted_action,
                nbc_message=drifted_message,
            )
        )


def test_downstream_decision_requires_the_exact_delivered_hop() -> None:
    projection = build_positive_lineage()
    undelivered = replace(projection.kt_delivery, delivered=False)

    with pytest.raises(
        LineageConformanceError,
        match="LINEAGE_CONFORMANCE_DELIVERY_GATE_MISMATCH",
    ):
        validate_lineage_projection(replace(projection, kt_delivery=undelivered))


def test_nych_intake_rejects_a_different_but_well_formed_message_reference() -> None:
    projection = build_positive_lineage()
    binding = projection.binding
    semantic_parameters = binding.semantic_values(projection.classify_action)
    semantic_parameters["delivered_message_ref"] = "message.unrelated.001"
    drifted_action = binding.project_action(
        "nych.record_and_classify_request",
        intent_id=projection.classify_action["intent_id"],
        run_id=projection.classify_action["run_id"],
        logical_tick=projection.classify_action["logical_tick"],
        decision_ref=projection.classify_action["decision_ref"],
        observation_refs=projection.classify_action["observation_refs"],
        semantic_parameters=semantic_parameters,
        earliest_effect_time=projection.classify_action["earliest_effect_time"],
    )

    with pytest.raises(
        LineageConformanceError,
        match="LINEAGE_CONFORMANCE_NYCH_INTAKE_MISMATCH",
    ):
        validate_lineage_projection(
            replace(projection, classify_action=drifted_action)
        )


def test_later_facility_cannot_be_back_projected_into_october_21_intake() -> None:
    projection = build_positive_lineage()
    binding = projection.binding
    policies = PositiveLineagePoliciesV0_1(binding)
    invalid_observation = binding.project_observation(
        "nych.record_and_classify_request",
        observation_id="observation.0288.nych.invalid_facility.001",
        values={
            "delivered_request": projection.nbc_message["message_intent_id"],
            "facility_eligibility": "ineligible",
            "relationship_status": [
                "rel.kt_nych.membership",
                "rel.nbc_nych.membership",
            ],
            "request_authorization_evidence": "sufficient",
            "route_classification": "nonmember_clearing_matter",
        },
    )

    with pytest.raises(
        LineageBindingError,
        match="LINEAGE_NYCH_INTAKE_BASIS_MISMATCH",
    ):
        policies.decide_nych_classification(
            invalid_observation,
            nbc_action=projection.nbc_action,
            nbc_message=projection.nbc_message,
            case_id="case.kt_nbc_nych.001",
            case_version=0,
        )


def test_action_admission_business_result_and_delivery_remain_separate() -> None:
    run = run_lineage_conformance()
    decline_action = run.projection.decline_action
    disposition = _records(run, "business_disposition_recorded")
    delivered = _records(run, "result_delivered")

    assert decline_action["resource_offer_or_request"] == []
    assert disposition == [
        {
            "action_intent_id": decline_action["intent_id"],
            "action_admission": "accepted",
            "business_disposition_id": "disposition.nych.case.001",
            "business_disposition": "other_scoped_decline",
            "execution_result": "not_applicable_no_resource_action",
            "reason_code": "no_competent_authority",
            "delivered": False,
            "delivery_ref": None,
        }
    ]
    assert delivered[0]["delivered"] is True
    assert delivered[0]["business_disposition"] == disposition[0][
        "business_disposition"
    ]
    assert delivered[0]["execution_result"] == disposition[0]["execution_result"]
    assert run.final_state["result_delivery"] == "delivered"


def test_trace_tamper_and_wrong_replay_prestate_are_rejected() -> None:
    run = run_lineage_conformance()
    tampered = copy.deepcopy(run.records)
    first_delta = next(
        row for row in tampered if row["record_type"] == "state_delta"
    )
    first_delta["payload"]["after"] = "invented_state"
    assert "RECORD_HASH_MISMATCH" in validate_trace(tampered)

    wrong_initial = dict(run.initial_state)
    wrong_initial["request_stage"] = "already_issued"
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
            / "scenarios/panic_1907/lineage-conformance-v0.1/receipt.json"
        ).read_text(encoding="utf-8")
    )
    trace = receipt["trace"]

    assert receipt["verdict"] == "PASS_BOUNDED_LINEAGE_CONFORMANCE"
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
    assert trace["replay_state_sha256"] == canonical_sha256(run.replayed_state)
    assert trace["trace_errors"] == run.trace_errors() == []
    assert trace["deterministic_repeat_equal"] is True
