from __future__ import annotations

import copy
from collections import Counter
from pathlib import Path

import pytest

from h2epr.agents import (
    CarrierConformanceError,
    load_executable_mapping,
    runtime_field_values,
    validate_observation_payload,
)
from masim.integrations.event_process import validate_trace

from scenarios.panic_1907 import run_first_slice
from scenarios.panic_1907.policies import (
    KT_ID,
    NYCH_ID,
    decide_knickerbocker,
    decide_nych,
)
from support.schema_registry import definition_errors


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BINDING_PATH = PROJECT_ROOT / "agents/bindings/panic_1907/binding.json"


EXPECTED_ACTIONS = (
    "submit_support_request",
    "record_and_classify_request",
    "request_case_information",
    "provide_requested_information",
    "open_or_continue_review",
    "open_or_continue_review",
    "issue_typed_decline",
    "prepare_operational_contingency",
)


SCHEMA_BY_RECORD_TYPE = {
    "scenario_identity_bound": "SystemEventPayload",
    "decision_basis_bound": "SystemEventPayload",
    "institutional_process_event": "SystemEventPayload",
    "observation_delivered": "ObservationPayload",
    "decision_recorded": "DecisionRecord",
    "action_intent_created": "ActionIntent",
    "action_disposition_recorded": "ActionDisposition",
    "state_transition_applied": "StateDelta",
    "message_intent_created": "MessageIntent",
    "communication_disposition_recorded": "CommunicationDisposition",
    "message_sent": "MessageSent",
    "message_delivered": "MessageDelivered",
}


def _records(result, record_type: str):
    return [
        record for record in result.records if record["record_type"] == record_type
    ]


def _current_metadata(observations):
    return {
        name: {
            "authoritative_record_ref": f"record.test.{name}",
            "as_of": "1907-10-21T12:00:00-05:00",
            "freshness": "current",
            "availability": "delivered",
            "scope_id": "scope.test.participant",
        }
        for name in observations
    }


def test_first_slice_closes_request_to_feedback_without_simulation() -> None:
    result = run_first_slice(BINDING_PATH)

    assert result.action_semantic_ids == EXPECTED_ACTIONS
    assert result.final_state == result.replayed_state
    assert validate_trace(result.records) == []
    assert result.manifest["simulation_started"] is False
    assert result.manifest["historical_validity_claim"] is False
    assert result.run_seal["unresolved_intent_ids"] == []
    assert result.run_seal["unresolved_recipient_ids"] == []

    state = result.final_state
    assert state["scenario_identity"] == {
        "variant": "NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE",
        "alternative_route_ref": None,
        "alternative_forum_ref": None,
        "basis_ref": "model_choice.0288.nych_route_gap.conservative.v0_2_1",
        "immutable": True,
    }
    assert state["objects"]["support_request"]["status"] == "refused"
    assert state["objects"]["nych_case"]["status"] == "disposition_issued"
    assert state["objects"]["review"]["status"] == "decision_ready"
    assert state["objects"]["proposal"]["status"] == "none"
    assert state["objects"]["result"]["status"] == "none"
    assert state["facts"]["financial_information"]["value"] == (
        "adequate_for_scope"
    )
    assert state["facts"]["request_authorization_evidence"]["value"] == (
        "sufficient"
    )
    assert state["facts"]["case_disposition"]["value"] == "facility_declined"
    assert state["facts"]["case_disposition"]["reason_code"] == (
        "facility_ineligible"
    )
    assert state["facts"]["case_communication"]["value"] == "delivered"
    assert state["participant_state"]["knickerbocker_trust"][
        "operational_posture"
    ] == "contingency_prepared"


def test_first_slice_payloads_conform_to_existing_v1_contracts() -> None:
    result = run_first_slice(BINDING_PATH)
    for record in result.records:
        definition = SCHEMA_BY_RECORD_TYPE.get(record["record_type"])
        if definition is not None:
            assert definition_errors(definition, record["payload"]) == [], (
                record["record_type"],
                record["trace_id"],
            )


def test_observations_are_complete_actor_scoped_families() -> None:
    result = run_first_slice(BINDING_PATH)
    mapping = load_executable_mapping(BINDING_PATH)
    known_record_refs = {
        row["entity_id"]
        for container in (
            "objects",
            "authorizations",
            "facts",
            "participant_state",
            "communications",
        )
        for row in result.final_state[container].values()
    }

    for record in _records(result, "observation_delivered"):
        payload = record["payload"]
        rows = payload["fields"]
        actor_id = rows[0]["runtime_value"]["visibility_scope_ids"][0]
        semantic_names = mapping.participants[actor_id].observations
        values = runtime_field_values(rows, "observation")
        scoped_observations = {
            (KT_ID, "corporate_authorization"): "scope.kt.support_request",
            (NYCH_ID, "authority_state"): (
                "scope.nych.facility_classification"
            ),
            (NYCH_ID, "request_authorization_evidence"): (
                "scope.kt.support_request"
            ),
        }
        for name in semantic_names:
            assert name in values
            assert values[f"{name}_authoritative_record_ref"] in known_record_refs
            assert values[f"{name}_as_of"].startswith("1907-10-21T")
            assert values[f"{name}_freshness"] == "current"
            assert values[f"{name}_availability"] in {
                "delivered",
                "unavailable",
            }
            assert values[f"{name}_scope_id"] == scoped_observations.get(
                (actor_id, name), f"scope.observation.{actor_id}"
            )
        assert len(values) == len(semantic_names) * 6


def test_declared_participant_state_is_materialized_in_authoritative_state() -> None:
    result = run_first_slice(BINDING_PATH)
    mapping = load_executable_mapping(BINDING_PATH)
    for actor_id, participant in mapping.participants.items():
        actual = set(result.initial_state["participant_state"][actor_id]) - {
            "entity_id",
            "version",
        }
        assert actual == set(participant.participant_state)


def test_each_decision_records_the_fields_its_policy_actually_used() -> None:
    result = run_first_slice(BINDING_PATH)
    mapping = load_executable_mapping(BINDING_PATH)
    decisions = {
        record["payload"]["decision_id"]
        for record in _records(result, "decision_recorded")
    }
    bases = _records(result, "decision_basis_bound")
    assert len(bases) == len(decisions) == 8
    for record in bases:
        values = runtime_field_values(record["payload"]["fields"], "basis")
        assert values["decision_id"] in decisions
        actor_id = values["actor_id"]
        assert values["used_observation_fields"]
        assert set(values["used_observation_fields"]) <= set(
            mapping.participants[actor_id].observations
        )
        assert set(values["used_participant_state_fields"]) <= set(
            mapping.participants[actor_id].participant_state
        )


def test_observation_family_fails_closed_when_metadata_is_missing() -> None:
    result = run_first_slice(BINDING_PATH)
    mapping = load_executable_mapping(BINDING_PATH)
    observation = copy.deepcopy(_records(result, "observation_delivered")[0]["payload"])
    actor_id = "knickerbocker_trust"
    semantic_names = mapping.participants[actor_id].observations
    values = runtime_field_values(observation["fields"], "observation")
    semantic_values = {name: values[name] for name in semantic_names}
    observation["fields"] = [
        row
        for row in observation["fields"]
        if row["field_name"] != "withdrawal_pressure_as_of"
    ]
    with pytest.raises(CarrierConformanceError, match="observation_family_mismatch"):
        validate_observation_payload(
            mapping,
            observation,
            actor_id=actor_id,
            semantic_values=semantic_values,
        )


def test_delivery_dependent_observation_availability_is_not_invented() -> None:
    result = run_first_slice(BINDING_PATH)
    by_tick = {
        record["logical_tick"]: runtime_field_values(
            record["payload"]["fields"], "observation"
        )
        for record in _records(result, "observation_delivered")
    }
    assert by_tick[0]["received_information_request_availability"] == "unavailable"
    assert by_tick[0]["delivered_disposition_availability"] == "unavailable"
    assert by_tick[3]["received_information_request_availability"] == "delivered"
    assert by_tick[7]["delivered_disposition_availability"] == "delivered"
    for tick in (1, 2, 4, 5, 6):
        assert by_tick[tick]["delivered_case_result_availability"] == "unavailable"


def test_messages_follow_admitted_actions_and_all_reach_delivery() -> None:
    result = run_first_slice(BINDING_PATH)
    counts = Counter(record["record_type"] for record in result.records)
    assert counts["message_intent_created"] == 4
    assert counts["communication_disposition_recorded"] == 4
    assert counts["message_sent"] == 4
    assert counts["message_delivered"] == 4

    positions = {
        record["trace_id"]: index for index, record in enumerate(result.records)
    }
    actions = {
        record["payload"]["intent_id"]: record
        for record in _records(result, "action_intent_created")
    }
    dispositions = {
        record["payload"]["intent_id"]: record
        for record in _records(result, "action_disposition_recorded")
    }
    sent = {
        record["payload"]["message_intent_id"]: record
        for record in _records(result, "message_sent")
    }

    for message_record in _records(result, "message_intent_created"):
        message = message_record["payload"]
        action_id = next(
            correlation
            for correlation in message["correlation_ids"]
            if correlation in actions
        )
        assert dispositions[action_id]["payload"]["status"] == "accepted"
        assert result.records.index(dispositions[action_id]) < result.records.index(
            message_record
        )

    for delivered_record in _records(result, "message_delivered"):
        delivered = delivered_record["payload"]
        sent_record = sent[delivered["message_intent_id"]]
        assert delivered["message_sent_trace_ref"] == sent_record["trace_id"]
        assert positions[sent_record["trace_id"]] < positions[
            delivered_record["trace_id"]
        ]


def test_decline_is_delivered_before_knickerbocker_adapts() -> None:
    result = run_first_slice(BINDING_PATH)
    decline_delivery_index = next(
        index
        for index, record in enumerate(result.records)
        if record["record_type"] == "message_delivered"
        and record["logical_tick"] == 7
    )
    observation_index = next(
        index
        for index, record in enumerate(result.records)
        if record["record_type"] == "observation_delivered"
        and record["logical_tick"] == 7
    )
    contingency_index = next(
        index
        for index, record in enumerate(result.records)
        if record["record_type"] == "action_intent_created"
        and record["payload"]["action_type"].endswith(
            "prepare_operational_contingency"
        )
    )
    observation = result.records[observation_index]["payload"]
    assert runtime_field_values(observation["fields"], "observation")[
        "delivered_disposition"
    ] == ["refused", "facility_ineligible"]
    assert decline_delivery_index < observation_index < contingency_index


def test_first_slice_is_deterministic_and_replayable() -> None:
    first = run_first_slice(BINDING_PATH)
    second = run_first_slice(BINDING_PATH)
    assert first.records == second.records
    assert first.final_state == second.final_state
    assert first.run_seal == second.run_seal


def test_knickerbocker_policy_uses_qualitative_gates_and_suppresses_duplicates() -> None:
    observations = {
        "asset_liquidity_assessment": "unknown",
        "clearing_channel_status": "active",
        "collateral_package_status": "available",
        "corporate_authorization": "authorized",
        "delivered_disposition": ["none", None],
        "internal_liquidity_assessment": "critical",
        "received_information_request": None,
        "support_request_status": "none",
        "withdrawal_pressure": "severe",
    }
    participant_state = {
        "last_verified_condition_time": "time.focal_synthetic_input",
        "operational_posture": "ordinary",
        "request_strategy_posture": "no_active_request",
    }
    assert decide_knickerbocker(
        observations, _current_metadata(observations), participant_state
    ).semantic_id == "submit_support_request"

    observations["internal_liquidity_assessment"] = "unknown"
    verification_plan = decide_knickerbocker(
        observations, _current_metadata(observations), participant_state
    )
    assert verification_plan.semantic_id == "verify_internal_condition"
    assert verification_plan.used_participant_state == (
        "last_verified_condition_time",
    )

    observations["internal_liquidity_assessment"] = "critical"
    stale = _current_metadata(observations)
    stale["internal_liquidity_assessment"]["freshness"] = "stale"
    assert decide_knickerbocker(
        observations, stale, participant_state
    ).semantic_id == "verify_internal_condition"

    observations["support_request_status"] = "under_review"
    duplicate_plan = decide_knickerbocker(
        observations, _current_metadata(observations), participant_state
    )
    assert duplicate_plan.semantic_id is None
    assert duplicate_plan.reason_codes == (
        "reason.equivalent_request_unresolved",
        "reason.request_strategy_posture.no_active_request",
    )


def test_nych_conservative_policy_has_no_invented_alternative_route() -> None:
    observations = {
        "authority_state": "authorized",
        "case_communication_status": "not_issued",
        "case_disposition_status": ["none", None],
        "delivered_case_result": ["none", None],
        "delivered_request": "request.kt.support.001",
        "facility_eligibility": "ineligible",
        "financial_information_status": "adequate_for_scope",
        "relationship_status": "nonmember_clearing_relationship",
        "request_authorization_evidence": "sufficient",
        "resource_proposal_status": "none",
        "review_state": "decision_ready",
        "route_classification": "member_facility",
    }
    participant_state = {
        "last_consumed_record_versions": "none",
        "procedural_assessment_posture": "under_review",
    }
    plan = decide_nych(
        observations, _current_metadata(observations), participant_state
    )
    assert plan.semantic_id == "issue_typed_decline"
    assert "proposal_id" not in plan.parameters
    assert plan.authority_refs == ()


def test_nych_procedural_forum_must_come_from_authority_observation() -> None:
    observations = {
        "authority_state": "committee_scope",
        "case_communication_status": "not_issued",
        "case_disposition_status": ["none", None],
        "delivered_case_result": ["none", None],
        "delivered_request": "request.kt.support.001",
        "facility_eligibility": "ineligible",
        "financial_information_status": "adequate_for_scope",
        "relationship_status": "nonmember_clearing_relationship",
        "request_authorization_evidence": "sufficient",
        "resource_proposal_status": "none",
        "review_state": "not_open",
        "route_classification": "member_facility",
    }
    participant_state = {
        "last_consumed_record_versions": "none",
        "procedural_assessment_posture": "case_classified",
    }
    generic = _current_metadata(observations)
    blocked = decide_nych(observations, generic, participant_state)
    assert blocked.semantic_id is None
    assert "reason.no_competent_forum_identified" in blocked.reason_codes

    delivered = _current_metadata(observations)
    delivered["authority_state"]["scope_id"] = (
        "forum.nych.executive_committee"
    )
    selected = decide_nych(observations, delivered, participant_state)
    assert selected.semantic_id == "seek_procedural_authority"
    assert selected.parameters["proposed_forum_id"] == (
        "forum.nych.executive_committee"
    )
