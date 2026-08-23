from __future__ import annotations

import copy
import json
from dataclasses import replace
from pathlib import Path

import pytest

from h2epr.agents import load_executable_mapping, runtime_field_values
from masim.integrations.event_process import validate_trace

from h2epr.scenarios.panic_1907 import run_behavior_feedback_matrix
from h2epr.scenarios.panic_1907.first_slice import FirstSliceRunner, run_first_slice
from h2epr.scenarios.panic_1907.model import StateChange
from h2epr.scenarios.panic_1907.policies import KT_ID, NYCH_ID, decide_knickerbocker
from support.schema_registry import definition_errors


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BINDING_PATH = PROJECT_ROOT / "agents/bindings/panic_1907/binding.json"


def _sealed_records(runner: FirstSliceRunner):
    runner.trace.seal_tick(0, runner.state.state)
    runner.trace.seal_run(runner.state.state, (), ())
    assert validate_trace(runner.trace.records) == []
    return runner.trace.records


def test_cycle4_behavior_feedback_matrix_is_complete_and_deterministic() -> None:
    first = run_behavior_feedback_matrix(BINDING_PATH)
    second = run_behavior_feedback_matrix(BINDING_PATH)

    assert first == second
    assert len(first) == 22
    assert len({row.case_id for row in first}) == 22
    assert sum(row.actor_id == "knickerbocker_trust" for row in first) == 10
    assert sum(row.actor_id == "new_york_clearing_house" for row in first) == 12
    assert all(row.passed for row in first)
    assert sum(row.binding_valid for row in first) == 20
    rejected = [row for row in first if row.expected_rejection is not None]
    assert len(rejected) == 2
    assert all(not row.binding_valid and row.diagnostic for row in rejected)
    assert {row.case_id for row in rejected} == {
        "FB-NYCH-RESULT-WITHOUT-PROPOSAL",
        "FB-NYCH-UNREACHABLE-PROPOSAL",
    }
    assert {row.case_id for row in first} >= {
        "CC-10",
        "FB-NYCH-NO-DUE-FOLLOW-UP",
    }
    assert {row.actual_semantic_id for row in first} >= {
        None,
        "communicate_case_status",
        "issue_typed_decline",
        "open_or_continue_review",
        "prepare_information_package",
        "prepare_operational_contingency",
        "provide_requested_information",
        "record_and_classify_request",
        "request_case_information",
        "request_channel_confirmation",
        "seek_institutional_authorization",
        "seek_procedural_authority",
        "submit_support_request",
        "verify_internal_condition",
    }


def test_out_of_domain_observation_is_hashed_and_traced_without_delivery() -> None:
    mapping = load_executable_mapping(BINDING_PATH)
    runner = FirstSliceRunner(mapping, BINDING_PATH)
    runner._append_initial_identity()
    values = runner._observation_values(KT_ID)
    metadata = runner._observation_metadata(KT_ID, 0)
    forbidden_value = "illiquid_value_uncertain"
    values["asset_liquidity_assessment"] = forbidden_value

    assert runner._record_observation_attempt(KT_ID, 0, values, metadata) is None
    records = _sealed_records(runner)
    violations = [
        row for row in records if row["record_type"] == "invariant_violation"
    ]
    assert len(violations) == 1
    payload = violations[0]["payload"]
    assert definition_errors("SystemEventPayload", payload) == []
    fields = runtime_field_values(payload["fields"], "invariant_violation")
    assert fields["actor_id"] == KT_ID
    assert fields["failure_layer"] == "layer.observation_semantic_conformance"
    assert fields["failed_field_ids"] == ["asset_liquidity_assessment"]
    assert len(fields["attempted_payload_sha256"]) == 64
    assert not any(row["record_type"] == "observation_delivered" for row in records)
    assert forbidden_value not in json.dumps(records, sort_keys=True)


def test_schema_valid_unauthorized_intent_is_rejected_without_effect_or_message() -> None:
    mapping = load_executable_mapping(BINDING_PATH)
    runner = FirstSliceRunner(mapping, BINDING_PATH)
    runner._append_initial_identity()
    values = runner._observation_values(KT_ID)
    metadata = runner._observation_metadata(KT_ID, 0)
    observation = runner._record_observation_attempt(KT_ID, 0, values, metadata)
    assert observation is not None
    plan = decide_knickerbocker(
        values,
        metadata,
        runner._participant_state(KT_ID),
    )
    unauthorized = replace(
        plan,
        authority_refs=("authority.kt.unresolved.001",),
    )
    before = copy.deepcopy(runner.state.state)

    runner._check_plan_envelope(KT_ID, unauthorized)
    runner._execute_plan(KT_ID, 0, observation, unauthorized)
    records = _sealed_records(runner)

    dispositions = [
        row["payload"]
        for row in records
        if row["record_type"] == "action_disposition_recorded"
    ]
    assert len(dispositions) == 1
    disposition = dispositions[0]
    assert definition_errors("ActionDisposition", disposition) == []
    assert disposition["status"] == "rejected"
    assert disposition["reason_codes"] == [
        "reason.claimed_authority_not_effective"
    ]
    assert disposition["state_before_version"] == disposition["state_after_version"]
    assert disposition["delta_ids"] == []
    assert disposition["explicit_no_effect"] is True
    assert disposition["rejected_parameters"]
    assert runner.state.state == before
    assert not any(
        row["record_type"]
        in {
            "message_intent_created",
            "communication_disposition_recorded",
            "message_sent",
            "state_transition_applied",
        }
        for row in records
    )


@pytest.mark.parametrize(
    ("authority_ref", "parameter_overrides", "logical_tick", "reason_code"),
    [
        (
            "authority.nych.intake.001",
            {},
            0,
            "reason.claimed_authority_actor_mismatch",
        ),
        (
            "authority.kt.operational_preparation.001",
            {},
            0,
            "reason.claimed_authority_capability_mismatch",
        ),
        (
            "authority.kt.support_request.001",
            {"route_id": "route.not_authorized"},
            0,
            "reason.claimed_authority_parameter_scope_mismatch",
        ),
        (
            "authority.kt.support_request.001",
            {"recipient_id": "recipient.not_authorized"},
            0,
            "reason.claimed_authority_target_scope_mismatch",
        ),
        (
            "authority.kt.support_request.001",
            {},
            8,
            "reason.claimed_authority_outside_effective_interval",
        ),
    ],
)
def test_authority_resolution_fails_closed_by_actor_capability_scope_and_time(
    authority_ref: str,
    parameter_overrides: dict[str, object],
    logical_tick: int,
    reason_code: str,
) -> None:
    mapping = load_executable_mapping(BINDING_PATH)
    runner = FirstSliceRunner(mapping, BINDING_PATH)
    runner._append_initial_identity()
    values = runner._observation_values(KT_ID)
    metadata = runner._observation_metadata(KT_ID, logical_tick)
    observation = runner._record_observation_attempt(
        KT_ID, logical_tick, values, metadata
    )
    assert observation is not None
    plan = decide_knickerbocker(
        values,
        metadata,
        runner._participant_state(KT_ID),
    )
    modified = replace(
        plan,
        parameters={**plan.parameters, **parameter_overrides},
        authority_refs=(authority_ref,),
    )
    before = copy.deepcopy(runner.state.state)

    runner._execute_plan(KT_ID, logical_tick, observation, modified)

    dispositions = [
        row["payload"]
        for row in runner.trace.records
        if row["record_type"] == "action_disposition_recorded"
    ]
    assert len(dispositions) == 1
    assert dispositions[0]["status"] == "rejected"
    assert dispositions[0]["reason_codes"] == [reason_code]
    assert dispositions[0]["explicit_no_effect"] is True
    assert runner.state.state == before
    assert not any(
        row["record_type"] in {"message_intent_created", "state_transition_applied"}
        for row in runner.trace.records
    )


def test_nych_request_authorization_evidence_changes_only_after_delivery() -> None:
    mapping = load_executable_mapping(BINDING_PATH)
    runner = FirstSliceRunner(mapping, BINDING_PATH)
    before = runner._observation_values(NYCH_ID)
    assert before["request_authorization_evidence"] == "absent"
    assert runner._observation_metadata(NYCH_ID, 0)[
        "request_authorization_evidence"
    ]["authoritative_record_ref"] == "evidence.request.kt.support.001"

    runner.state.apply(
        (
            StateChange(
                "authorizations",
                "kt_corporate",
                "status",
                "authorized",
                "denied",
                "authority.kt.support_request.001",
            ),
        ),
        disposition_id="test.kt.internal_authority_change",
        causal_parent_ids=("test.kt.internal_authority_change",),
    )
    assert runner._observation_values(NYCH_ID)[
        "request_authorization_evidence"
    ] == "absent"

    result = run_first_slice(BINDING_PATH)
    assert result.final_state["facts"]["request_authorization_evidence"][
        "value"
    ] == "sufficient"


def test_empty_target_grant_is_not_a_target_wildcard() -> None:
    mapping = load_executable_mapping(BINDING_PATH)
    runner = FirstSliceRunner(mapping, BINDING_PATH)
    action = {
        "action_type": "h2epr.action.open_or_continue_review",
        "actor_id": NYCH_ID,
        "claimed_authority_refs": ["authority.nych.case_process.001"],
        "parameters": [
            {
                "field_name": "scope_id",
                "runtime_value": {
                    "value": "scope.nych.facility_classification"
                },
            }
        ],
        "resource_offer_or_request": [],
        "target_entity_ids": ["target.not_authorized"],
    }

    assert runner._authority_rejection_reason(
        action,
        logical_tick=0,
    ) == "reason.claimed_authority_target_scope_mismatch"
