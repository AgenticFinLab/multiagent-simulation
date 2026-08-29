from __future__ import annotations

from h2epr.scenarios.panic_1907.full_roster_v0_1 import (
    build_panic_policy_catalog,
)
from h2epr.scenarios.panic_1907.full_roster_v0_1.participant_rules_institutions import (
    INSTITUTION_PARTICIPANT_POLICIES,
)
from h2epr.scenarios.panic_1907.full_roster_v0_1.registry import (
    implementation_versions,
    participant_policies,
)


TCA_INTENTS = {
    "verify_institutional_condition",
    "consent_to_scoped_examination",
    "provide_scoped_case_information",
    "request_information_or_terms",
    "open_or_update_support_request",
    "propose_collateral_package",
    "withdraw_or_close_support_route",
    "propose_operational_capacity_change",
    "authorize_operational_posture",
    "authorize_condition_statement",
    "issue_authorized_condition_statement",
    "narrow_or_withhold_condition_statement",
    "authorize_correction_or_update",
    "close_or_pause_institutional_matter",
}


EXPECTED_INTENTS = {
    "j_pierpont_morgan": {
        "DC-MG-01": {
            "classify_coordination_matter",
            "request_case_information",
            "decline_or_close_coordination_role",
        },
        "DC-MG-02": {
            "request_case_information",
            "request_independent_examination",
            "form_or_revise_coordination_proposal",
        },
        "DC-MG-03": {
            "convene_coordination_session",
            "form_or_revise_coordination_proposal",
            "communicate_coordination_position",
        },
        "DC-MG-04": {"solicit_independent_commitment"},
        "DC-MG-05": {
            "assemble_coordination_plan",
            "form_or_revise_coordination_proposal",
            "request_commitment_or_result_clarification",
        },
        "DC-MG-06": {
            "communicate_coordination_position",
            "form_or_revise_coordination_proposal",
            "request_commitment_or_result_clarification",
            "decline_or_close_coordination_role",
        },
    },
    "trust_company_of_america": {
        "DC-TCA-01": {
            "verify_institutional_condition",
            "request_information_or_terms",
            "open_or_update_support_request",
            "propose_operational_capacity_change",
            "authorize_operational_posture",
            "authorize_condition_statement",
            "narrow_or_withhold_condition_statement",
        },
        "DC-TCA-02": {
            "consent_to_scoped_examination",
            "provide_scoped_case_information",
            "request_information_or_terms",
        },
        "DC-TCA-03": {
            "open_or_update_support_request",
            "propose_collateral_package",
            "request_information_or_terms",
            "withdraw_or_close_support_route",
        },
        "DC-TCA-04": {
            "propose_operational_capacity_change",
            "authorize_operational_posture",
            "verify_institutional_condition",
        },
        "DC-TCA-05": {
            "authorize_condition_statement",
            "issue_authorized_condition_statement",
            "narrow_or_withhold_condition_statement",
            "authorize_correction_or_update",
            "verify_institutional_condition",
        },
        "DC-TCA-06": TCA_INTENTS,
    },
    "lincoln_trust_company": {
        "DC-LTC-01": {
            "request_condition_information",
            "authorize_condition_statement",
            "narrow_or_withhold_condition_statement",
        },
        "DC-LTC-02": {"issue_authorized_condition_statement"},
        "DC-LTC-03": {
            "authorize_correction_or_update",
            "request_condition_information",
            "narrow_or_withhold_condition_statement",
        },
        "DC-LTC-04": {
            "request_message_delivery_clarification",
            "close_communication_matter",
        },
    },
    "trust_presidents_committee": {
        "DC-TPC-01": {
            "open_or_refer_assistance_case",
            "await_case_or_plan_result",
        },
        "DC-TPC-02": {
            "request_case_information",
            "request_scoped_examination",
            "issue_case_recommendation",
        },
        "DC-TPC-03": {"issue_case_recommendation"},
        "DC-TPC-04": {"report_case_status"},
        "DC-TPC-05": {
            "solicit_independent_contribution",
            "assemble_or_revise_support_plan",
            "await_case_or_plan_result",
        },
        "DC-TPC-06": {
            "assemble_or_revise_support_plan",
            "report_case_status",
            "await_case_or_plan_result",
        },
    },
}


def _reader_id(value: str) -> str:
    return value.rsplit(".", 1)[-1]


def test_institution_policies_close_their_released_capability_inventories() -> None:
    catalog = build_panic_policy_catalog()

    for implementation in INSTITUTION_PARTICIPANT_POLICIES:
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


def test_institution_commitment_intent_surfaces_match_the_definitions() -> None:
    for implementation in INSTITUTION_PARTICIPANT_POLICIES:
        expected = EXPECTED_INTENTS[implementation.capability_id]
        assert {_reader_id(item) for item in implementation.commitment_ids} == set(
            expected
        )
        for commitment_id, specification in implementation.decisions.items():
            assert {_reader_id(item) for item in specification.intent_ids} == expected[
                _reader_id(commitment_id)
            ]


def test_every_institution_branch_and_no_intent_path_is_reachable() -> None:
    for implementation in INSTITUTION_PARTICIPANT_POLICIES:
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

            for declared_branch in specification.branches:
                context = implementation.witness_context(
                    actor_id="actor.test",
                    commitment_id=commitment_id,
                    branch_id=declared_branch.branch_id,
                )
                result = implementation.decide(context)
                assert result.intent_id == declared_branch.intent_id
                assert result.branch_id == declared_branch.branch_id


def test_institution_policies_are_statically_registered() -> None:
    registry = participant_policies()
    versions = implementation_versions()

    for implementation in INSTITUTION_PARTICIPANT_POLICIES:
        assert registry[implementation.implementation_id] is implementation
        assert versions[implementation.implementation_id] == "0.1.0"
