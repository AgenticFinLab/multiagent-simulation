from __future__ import annotations

from dataclasses import replace

import pytest

from h2epr.scenarios.panic_1907.full_roster_v0_1 import (
    build_panic_policy_catalog,
)
from h2epr.scenarios.panic_1907.full_roster_v0_1.participant import (
    ParticipantPolicyError,
)
from h2epr.scenarios.panic_1907.full_roster_v0_1.participant_rules_populations import (
    KNICKERBOCKER_DEPOSITOR_POLICY,
    POPULATION_PARTICIPANT_POLICIES,
)
from h2epr.scenarios.panic_1907.full_roster_v0_1.registry import (
    implementation_versions,
    participant_policies,
)


DEPOSITOR_INTENTS = {
    "PC-KDP-01": {"request_withdrawal", "retain_for_interval"},
    "PC-KDP-02": {
        "request_withdrawal",
        "retain_for_interval",
        "await_request_result",
    },
    "PC-KDP-03": {
        "request_withdrawal",
        "retain_for_interval",
        "await_request_result",
    },
    "PC-KDP-04": {"await_request_result"},
    "PC-KDP-05": {
        "request_withdrawal",
        "retain_for_interval",
        "await_request_result",
    },
}

EXPECTED_INTENTS = {
    "knickerbocker_depositor": DEPOSITOR_INTENTS,
    "later_trust_depositor": {
        key.replace("KDP", "LDP"): value for key, value in DEPOSITOR_INTENTS.items()
    },
    "bank_resource_decision": {
        "PC-CBC-01": {
            "request_proposal_information",
            "refer_or_decline_proposal",
            "make_conditional_contribution_offer",
            "commit_owned_resource",
            "await_commitment_or_application_result",
        },
        "PC-CBC-02": {
            "request_proposal_information",
            "refer_or_decline_proposal",
            "make_conditional_contribution_offer",
            "commit_owned_resource",
        },
        "PC-CBC-03": {
            "refer_or_decline_proposal",
            "make_conditional_contribution_offer",
            "commit_owned_resource",
        },
        "PC-CBC-04": {
            "revise_or_cancel_commitment",
            "await_commitment_or_application_result",
        },
        "PC-CBC-05": {
            "apply_for_member_certificate",
            "submit_controlled_collateral",
        },
        "PC-CBC-06": {
            "revise_or_cancel_commitment",
            "await_commitment_or_application_result",
        },
    },
    "call_money_lender": {
        "PC-CML-01": {
            "request_call_loan_information",
            "continue_call_loan_for_interval",
            "propose_call_loan_term_change",
            "issue_call_or_reduction_notice",
            "await_call_loan_result",
        },
        "PC-CML-02": {
            "request_call_loan_information",
            "continue_call_loan_for_interval",
            "propose_call_loan_term_change",
            "issue_call_or_reduction_notice",
        },
        "PC-CML-03": {
            "request_call_loan_information",
            "make_conditional_call_loan_offer",
            "decline_call_loan_request",
            "await_call_loan_result",
        },
        "PC-CML-04": {
            "make_conditional_call_loan_offer",
            "decline_call_loan_request",
        },
        "PC-CML-05": {
            "revise_or_cancel_call_loan_offer",
            "await_call_loan_result",
        },
    },
    "call_money_broker_borrower": {
        "PC-CMB-01": {"request_call_or_term_clarification"},
        "PC-CMB-02": {
            "authorize_controlled_repayment",
            "request_call_loan_renewal_or_replacement",
            "request_authorized_position_reduction",
            "record_funding_inability",
            "await_funding_or_repayment_result",
        },
        "PC-CMB-03": {
            "request_call_loan_renewal_or_replacement",
            "submit_controlled_collateral_proposal",
            "await_funding_or_repayment_result",
        },
        "PC-CMB-04": {
            "submit_controlled_collateral_proposal",
            "accept_call_loan_offer",
            "request_call_loan_offer_revision",
            "decline_call_loan_offer",
            "record_funding_inability",
        },
        "PC-CMB-05": {
            "authorize_controlled_repayment",
            "request_authorized_position_reduction",
        },
        "PC-CMB-06": {
            "request_call_or_term_clarification",
            "request_call_loan_renewal_or_replacement",
            "submit_controlled_collateral_proposal",
            "accept_call_loan_offer",
            "request_call_loan_offer_revision",
            "decline_call_loan_offer",
            "authorize_controlled_repayment",
            "request_authorized_position_reduction",
            "record_funding_inability",
            "await_funding_or_repayment_result",
        },
    },
}


def _reader_id(value: str) -> str:
    return value.rsplit(".", 1)[-1]


def test_population_policies_close_their_released_capability_inventories() -> None:
    catalog = build_panic_policy_catalog()

    for implementation in POPULATION_PARTICIPANT_POLICIES:
        placement = next(
            item
            for item in catalog.placements.values()
            if item.capability_id == implementation.capability_id
        )
        assert set(implementation.commitment_ids) == set(placement.commitment_ids)
        assert set(implementation.observation_ids) == set(placement.observation_ids)
        assert set(implementation.private_state_ids) == set(placement.private_state_ids)
        assert set(implementation.intent_ids) == set(placement.intent_ids)
        assert set(implementation.configuration_parameter_ids) == {
            name for name, _ in placement.configuration_parameter_bindings
        }


def test_population_commitment_intent_surfaces_match_the_definitions() -> None:
    for implementation in POPULATION_PARTICIPANT_POLICIES:
        expected = EXPECTED_INTENTS[implementation.capability_id]
        assert {_reader_id(item) for item in implementation.commitment_ids} == set(
            expected
        )
        for commitment_id, specification in implementation.decisions.items():
            assert {_reader_id(item) for item in specification.intent_ids} == expected[
                _reader_id(commitment_id)
            ]


def test_every_population_branch_and_no_intent_path_is_reachable() -> None:
    for implementation in POPULATION_PARTICIPANT_POLICIES:
        for commitment_id, specification in implementation.decisions.items():
            baseline = implementation.witness_context(
                actor_id="actor.test",
                commitment_id=commitment_id,
                branch_id=None,
            )
            no_intent = implementation.decide(baseline)
            assert no_intent.intent_id is None
            assert no_intent.no_intent_reason_code is not None
            assert no_intent.revisit_trigger_ids
            assert set(no_intent.consumed_configuration_parameter_ids) == set(
                implementation.configuration_parameter_ids
            )

            for declared_branch in specification.branches:
                context = implementation.witness_context(
                    actor_id="actor.test",
                    commitment_id=commitment_id,
                    branch_id=declared_branch.branch_id,
                )
                first = implementation.decide(context)
                second = implementation.decide(context)
                assert first == second
                assert first.intent_id == declared_branch.intent_id
                assert first.branch_id == declared_branch.branch_id


def test_configuration_parameters_change_population_choices() -> None:
    implementation = KNICKERBOCKER_DEPOSITOR_POLICY
    commitment_id = next(
        item for item in implementation.commitment_ids if item.endswith("PC-KDP-02")
    )
    branch_id = next(
        item.branch_id
        for item in implementation.decisions[commitment_id].branches
        if item.branch_id.endswith("request_withdrawal")
    )
    signal_responsive = implementation.witness_context(
        actor_id="actor.test",
        commitment_id=commitment_id,
        branch_id=branch_id,
    )

    assert implementation.decide(signal_responsive).intent_id is not None
    need_only = replace(
        signal_responsive,
        configuration_parameters={
            **signal_responsive.configuration_parameters,
            "response_profile": "need_only",
        },
    )
    assert implementation.decide(need_only).intent_id is None


def test_population_configuration_domains_fail_closed() -> None:
    implementation = KNICKERBOCKER_DEPOSITOR_POLICY
    commitment_id = implementation.commitment_ids[0]
    context = implementation.witness_context(
        actor_id="actor.test",
        commitment_id=commitment_id,
        branch_id=None,
    )

    with pytest.raises(ParticipantPolicyError, match="fact_value_outside_domain"):
        implementation.decide(
            replace(
                context,
                configuration_parameters={
                    **context.configuration_parameters,
                    "response_profile": "outcome_fitted",
                },
            )
        )
    with pytest.raises(
        ParticipantPolicyError,
        match="configuration_parameter_scope_mismatch",
    ):
        implementation.decide(replace(context, configuration_parameters={}))


def test_all_twelve_participant_policies_are_statically_registered() -> None:
    registry = participant_policies()
    versions = implementation_versions()

    assert len(registry) == 12
    for implementation in POPULATION_PARTICIPANT_POLICIES:
        assert registry[implementation.implementation_id] is implementation
        assert versions[implementation.implementation_id] == "0.1.0"
