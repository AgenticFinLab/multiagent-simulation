from __future__ import annotations

from dataclasses import replace

import pytest

from h2epr.scenarios.panic_1907.full_roster_v0_1 import (
    build_panic_policy_catalog,
)
from h2epr.scenarios.panic_1907.full_roster_v0_1.participant import (
    ParticipantPolicyError,
)
from h2epr.scenarios.panic_1907.full_roster_v0_1.participant_rules_core import (
    CORE_PARTICIPANT_POLICIES,
)
from h2epr.scenarios.panic_1907.full_roster_v0_1.registry import (
    implementation_versions,
    participant_policies,
    participant_policy,
)


EXPECTED_INTENTS = {
    "knickerbocker_trust": {
        "DC-KT-01": {
            "verify_internal_condition",
            "seek_institutional_authorization",
            "prepare_information_package",
            "prepare_operational_contingency",
        },
        "DC-KT-02": {
            "submit_support_request",
            "request_channel_confirmation",
            "prepare_information_package",
            "seek_institutional_authorization",
        },
        "DC-KT-03": {
            "provide_requested_information",
            "request_status_clarification",
            "revise_or_withdraw_request",
            "prepare_operational_contingency",
        },
        "DC-KT-04": {
            "request_result_clarification",
            "issue_institutional_communication",
            "prepare_operational_contingency",
            "request_channel_confirmation",
        },
    },
    "new_york_clearing_house": {
        "DC-NYCH-01": {
            "record_and_classify_request",
            "request_case_information",
            "seek_procedural_authority",
            "refer_request",
            "communicate_case_status",
        },
        "DC-NYCH-02": {
            "request_case_information",
            "open_or_continue_review",
            "seek_procedural_authority",
            "communicate_case_status",
            "refer_request",
        },
        "DC-NYCH-03": {
            "issue_typed_decline",
            "seek_procedural_authority",
            "refer_request",
            "communicate_case_status",
        },
        "DC-NYCH-04": {
            "request_case_information",
            "seek_member_or_association_authorization",
            "propose_conditioned_measure",
            "communicate_case_status",
        },
        "DC-NYCH-05": {
            "communicate_case_status",
            "issue_typed_decline",
            "refer_request",
            "request_case_information",
            "close_or_reopen_review",
        },
    },
    "national_bank_of_commerce": {
        "DC-NBC-01": {
            "verify_nbc_exposure",
            "request_counterparty_information",
            "seek_nbc_authority",
            "propose_credit_posture",
            "limit_or_decline_additional_credit",
            "request_delivery_or_result_clarification",
        },
        "DC-NBC-02": {
            "seek_intermediation_clarification",
            "forward_request_with_provenance",
            "sponsor_or_represent_request",
            "decline_intermediation",
            "request_nych_direction_clarification",
        },
        "DC-NBC-03": {
            "confirm_clearing_continuation",
            "propose_relationship_condition",
            "verify_nbc_exposure",
            "request_counterparty_information",
            "seek_nbc_authority",
            "request_nych_direction_clarification",
            "issue_clearing_termination_notice",
        },
        "DC-NBC-04": {
            "verify_nbc_exposure",
            "request_counterparty_information",
            "seek_nbc_authority",
            "propose_credit_posture",
            "limit_or_decline_additional_credit",
            "seek_intermediation_clarification",
            "forward_request_with_provenance",
            "sponsor_or_represent_request",
            "decline_intermediation",
            "request_nych_direction_clarification",
            "confirm_clearing_continuation",
            "propose_relationship_condition",
            "issue_clearing_termination_notice",
            "communicate_nbc_position",
            "request_delivery_or_result_clarification",
        },
    },
}


def _reader_id(value: str) -> str:
    return value.rsplit(".", 1)[-1]


def _commitment_reader_id(value: str) -> str:
    return value.rsplit(".", 1)[-1]


def test_core_registry_contains_real_policy_objects_only() -> None:
    registry = participant_policies()

    assert set(registry.values()) == set(CORE_PARTICIPANT_POLICIES)
    assert implementation_versions() == {
        policy.implementation_id: "0.1.0" for policy in CORE_PARTICIPANT_POLICIES
    }
    for implementation_id, implementation in registry.items():
        assert participant_policy(implementation_id) is implementation
    with pytest.raises(KeyError, match="unknown_participant_policy"):
        participant_policy("h2epr.policy.0288.participant.unknown")


def test_core_policies_close_the_released_capability_inventories() -> None:
    catalog = build_panic_policy_catalog()

    for implementation in CORE_PARTICIPANT_POLICIES:
        placement = next(
            item
            for item in catalog.placements.values()
            if item.capability_id == implementation.capability_id
        )
        assert set(implementation.commitment_ids) == set(placement.commitment_ids)
        assert set(implementation.observation_ids) == set(placement.observation_ids)
        assert set(implementation.private_state_ids) == set(placement.private_state_ids)
        assert set(implementation.intent_ids) == set(placement.intent_ids)
        assert implementation.configuration_parameter_ids == ()


def test_each_released_core_intent_has_a_reachable_branch() -> None:
    for implementation in CORE_PARTICIPANT_POLICIES:
        expected = EXPECTED_INTENTS[implementation.capability_id]
        assert {
            _commitment_reader_id(item) for item in implementation.commitment_ids
        } == set(expected)
        for commitment, specification in implementation.decisions.items():
            reader_commitment = _commitment_reader_id(commitment)
            assert {_reader_id(item) for item in specification.intent_ids} == expected[
                reader_commitment
            ]
            for branch_specification in specification.branches:
                context = implementation.witness_context(
                    actor_id="actor.test",
                    commitment_id=commitment,
                    branch_id=branch_specification.branch_id,
                )
                first = implementation.decide(context)
                second = implementation.decide(context)
                assert first == second
                assert first.branch_id == branch_specification.branch_id
                assert first.intent_id == branch_specification.intent_id
                assert first.no_intent_reason_code is None
                assert set(first.proposed_private_state_updates) <= set(
                    specification.private_state_ids
                )


def test_each_commitment_has_an_explicit_revisitable_no_intent_path() -> None:
    for implementation in CORE_PARTICIPANT_POLICIES:
        for commitment, specification in implementation.decisions.items():
            context = implementation.witness_context(
                actor_id="actor.test",
                commitment_id=commitment,
                branch_id=None,
            )

            result = implementation.decide(context)

            assert result.intent_id is None
            assert result.branch_id is None
            assert result.no_intent_reason_code in specification.no_intent_reason_codes
            assert result.revisit_trigger_ids == specification.revisit_trigger_ids
            assert result.proposed_private_state_updates == {}


def test_context_scope_and_fact_domains_fail_closed() -> None:
    implementation = CORE_PARTICIPANT_POLICIES[0]
    commitment = implementation.commitment_ids[0]
    context = implementation.witness_context(
        actor_id="actor.test",
        commitment_id=commitment,
        branch_id=None,
    )
    observation_id = next(iter(context.observations))
    outside_domain = dict(context.observations)
    outside_domain[observation_id] = "historical_outcome_known"

    with pytest.raises(ParticipantPolicyError, match="fact_value_outside_domain"):
        implementation.decide(replace(context, observations=outside_domain))
    with pytest.raises(ParticipantPolicyError, match="observation_scope_mismatch"):
        implementation.decide(replace(context, observations={}))
    with pytest.raises(ParticipantPolicyError, match="capability_mismatch"):
        implementation.decide(replace(context, capability_id="unknown"))


def test_policy_views_and_contexts_are_immutable() -> None:
    implementation = CORE_PARTICIPANT_POLICIES[0]
    commitment = implementation.commitment_ids[0]
    specification = implementation.decisions[commitment]
    context = implementation.witness_context(
        actor_id="actor.test",
        commitment_id=commitment,
        branch_id=None,
    )

    with pytest.raises(TypeError):
        implementation.decisions["forged"] = specification
    with pytest.raises(TypeError):
        specification.baseline_facts["forged"] = "value"
    with pytest.raises(TypeError):
        context.observations["forged"] = "value"
