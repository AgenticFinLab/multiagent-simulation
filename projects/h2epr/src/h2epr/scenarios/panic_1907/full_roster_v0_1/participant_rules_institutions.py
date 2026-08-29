"""Panic Rule policies for the remaining named institutional participants."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from .participant import RuleParticipantPolicy
from .specification import branch, decision, observation_id, policy, state_id


Domain = tuple[str, ...]


def _only(source: Mapping[str, Domain], names: Sequence[str]) -> dict[str, Domain]:
    return {name: source[name] for name in names}


def _o(capability: str, name: str) -> str:
    return observation_id(capability, name)


def _s(capability: str, name: str) -> str:
    return state_id(capability, name)


MORGAN = "j_pierpont_morgan"
MORGAN_OBSERVATIONS: Mapping[str, Domain] = {
    "delivered_coordination_matter": (
        "absent",
        "complete",
        "incomplete",
        "disputed",
        "withdrawn",
    ),
    "case_information_status": (
        "absent",
        "incomplete",
        "disputed",
        "adequate_for_scope",
        "superseded",
    ),
    "independent_report_status": (
        "not_requested",
        "pending",
        "delivered",
        "disputed",
        "withdrawn",
    ),
    "represented_authority": (
        "absent",
        "personal",
        "firm_delegated",
        "joint",
        "disputed",
        "unknown",
    ),
    "participant_roster_and_roles": (
        "absent",
        "complete",
        "incomplete",
        "disputed",
    ),
    "proposal_record": (
        "none",
        "draft",
        "circulating",
        "revising",
        "ready_for_assembly",
        "withdrawn",
        "closed",
    ),
    "delivered_commitment_reply": (
        "none",
        "pending",
        "conditioned",
        "committed",
        "declined",
        "expired",
        "disputed",
    ),
    "delivered_coordination_result": (
        "none",
        "delayed",
        "partial",
        "failed",
        "executed",
        "withdrawn",
    ),
    "dated_relationship_record": ("none", "current", "stale", "disputed"),
}
MORGAN_STATE: Mapping[str, Domain] = {
    "coordination_posture": (
        "unclassified",
        "reviewing",
        "convening",
        "soliciting",
        "assembling",
        "communicating",
        "closed",
    ),
    "last_consumed_record_versions": ("none", "consumed"),
}


J_PIERPONT_MORGAN_POLICY = policy(
    MORGAN,
    (
        decision(
            MORGAN,
            "DC-MG-01",
            observation_domains=_only(
                MORGAN_OBSERVATIONS,
                (
                    "delivered_coordination_matter",
                    "case_information_status",
                    "represented_authority",
                ),
            ),
            state_domains=MORGAN_STATE,
            branches=(
                branch(
                    MORGAN,
                    "classify_coordination_matter",
                    when_all={
                        _o(MORGAN, "delivered_coordination_matter"): "complete"
                    },
                    state_updates={
                        _s(MORGAN, "coordination_posture"): "reviewing"
                    },
                ),
                branch(
                    MORGAN,
                    "request_case_information",
                    when_all={_o(MORGAN, "case_information_status"): "incomplete"},
                    state_updates={
                        _s(MORGAN, "coordination_posture"): "reviewing"
                    },
                ),
                branch(
                    MORGAN,
                    "decline_or_close_coordination_role",
                    when_all={
                        _o(MORGAN, "delivered_coordination_matter"): (
                            "disputed",
                            "withdrawn",
                        )
                    },
                    state_updates={_s(MORGAN, "coordination_posture"): "closed"},
                ),
            ),
            lifecycle_names=(
                "support_and_request_case",
                "information_and_examination",
                "institutional_communication",
            ),
        ),
        decision(
            MORGAN,
            "DC-MG-02",
            observation_domains=_only(
                MORGAN_OBSERVATIONS,
                (
                    "case_information_status",
                    "independent_report_status",
                    "represented_authority",
                    "dated_relationship_record",
                ),
            ),
            state_domains=MORGAN_STATE,
            branches=(
                branch(
                    MORGAN,
                    "request_case_information",
                    when_all={_o(MORGAN, "case_information_status"): "incomplete"},
                    state_updates={
                        _s(MORGAN, "coordination_posture"): "reviewing"
                    },
                ),
                branch(
                    MORGAN,
                    "request_independent_examination",
                    when_all={
                        _o(MORGAN, "independent_report_status"): "not_requested",
                        _o(MORGAN, "case_information_status"): "disputed",
                    },
                    state_updates={
                        _s(MORGAN, "coordination_posture"): "reviewing"
                    },
                ),
                branch(
                    MORGAN,
                    "form_or_revise_coordination_proposal",
                    when_all={
                        _o(MORGAN, "case_information_status"): "adequate_for_scope",
                        _o(MORGAN, "independent_report_status"): "delivered",
                    },
                    state_updates={
                        _s(MORGAN, "coordination_posture"): "convening"
                    },
                ),
            ),
            lifecycle_names=(
                "information_and_examination",
                "proposal_and_plan",
                "governance_and_authority",
            ),
        ),
        decision(
            MORGAN,
            "DC-MG-03",
            observation_domains=_only(
                MORGAN_OBSERVATIONS,
                (
                    "independent_report_status",
                    "represented_authority",
                    "participant_roster_and_roles",
                    "proposal_record",
                    "dated_relationship_record",
                ),
            ),
            state_domains=MORGAN_STATE,
            branches=(
                branch(
                    MORGAN,
                    "convene_coordination_session",
                    when_all={
                        _o(MORGAN, "participant_roster_and_roles"): "complete",
                        _o(MORGAN, "proposal_record"): "draft",
                    },
                    state_updates={
                        _s(MORGAN, "coordination_posture"): "convening"
                    },
                ),
                branch(
                    MORGAN,
                    "form_or_revise_coordination_proposal",
                    when_all={
                        _o(MORGAN, "participant_roster_and_roles"): "incomplete"
                    },
                    state_updates={
                        _s(MORGAN, "coordination_posture"): "reviewing"
                    },
                ),
                branch(
                    MORGAN,
                    "communicate_coordination_position",
                    when_all={_o(MORGAN, "proposal_record"): "circulating"},
                    state_updates={
                        _s(MORGAN, "coordination_posture"): "communicating"
                    },
                ),
            ),
            lifecycle_names=(
                "proposal_and_plan",
                "institutional_communication",
                "governance_and_authority",
            ),
        ),
        decision(
            MORGAN,
            "DC-MG-04",
            observation_domains=_only(
                MORGAN_OBSERVATIONS,
                (
                    "represented_authority",
                    "participant_roster_and_roles",
                    "proposal_record",
                    "delivered_commitment_reply",
                ),
            ),
            state_domains=MORGAN_STATE,
            branches=(
                branch(
                    MORGAN,
                    "solicit_independent_commitment",
                    when_all={
                        _o(MORGAN, "proposal_record"): "circulating",
                        _o(MORGAN, "delivered_commitment_reply"): "none",
                    },
                    state_updates={
                        _s(MORGAN, "coordination_posture"): "soliciting"
                    },
                ),
            ),
            lifecycle_names=(
                "solicitation_and_independent_reply",
                "proposal_and_plan",
            ),
        ),
        decision(
            MORGAN,
            "DC-MG-05",
            observation_domains=_only(
                MORGAN_OBSERVATIONS,
                (
                    "represented_authority",
                    "participant_roster_and_roles",
                    "proposal_record",
                    "delivered_commitment_reply",
                ),
            ),
            state_domains=MORGAN_STATE,
            branches=(
                branch(
                    MORGAN,
                    "assemble_coordination_plan",
                    when_all={
                        _o(MORGAN, "proposal_record"): "ready_for_assembly",
                        _o(MORGAN, "delivered_commitment_reply"): "committed",
                    },
                    state_updates={
                        _s(MORGAN, "coordination_posture"): "assembling"
                    },
                ),
                branch(
                    MORGAN,
                    "form_or_revise_coordination_proposal",
                    when_all={
                        _o(MORGAN, "delivered_commitment_reply"): (
                            "conditioned",
                            "declined",
                        )
                    },
                    state_updates={
                        _s(MORGAN, "coordination_posture"): "reviewing"
                    },
                ),
                branch(
                    MORGAN,
                    "request_commitment_or_result_clarification",
                    when_all={
                        _o(MORGAN, "delivered_commitment_reply"): (
                            "expired",
                            "disputed",
                        )
                    },
                    state_updates={
                        _s(MORGAN, "coordination_posture"): "soliciting"
                    },
                ),
            ),
            lifecycle_names=(
                "proposal_and_plan",
                "solicitation_and_independent_reply",
                "resource_commitment_and_execution",
            ),
        ),
        decision(
            MORGAN,
            "DC-MG-06",
            observation_domains=_only(
                MORGAN_OBSERVATIONS,
                (
                    "represented_authority",
                    "proposal_record",
                    "delivered_commitment_reply",
                    "delivered_coordination_result",
                ),
            ),
            state_domains=MORGAN_STATE,
            branches=(
                branch(
                    MORGAN,
                    "communicate_coordination_position",
                    when_all={
                        _o(MORGAN, "delivered_coordination_result"): "executed"
                    },
                    state_updates={
                        _s(MORGAN, "coordination_posture"): "communicating",
                        _s(MORGAN, "last_consumed_record_versions"): "consumed",
                    },
                ),
                branch(
                    MORGAN,
                    "form_or_revise_coordination_proposal",
                    when_all={
                        _o(MORGAN, "delivered_coordination_result"): (
                            "partial",
                            "failed",
                        )
                    },
                    state_updates={
                        _s(MORGAN, "coordination_posture"): "reviewing",
                        _s(MORGAN, "last_consumed_record_versions"): "consumed",
                    },
                ),
                branch(
                    MORGAN,
                    "request_commitment_or_result_clarification",
                    when_all={
                        _o(MORGAN, "delivered_coordination_result"): "delayed"
                    },
                    state_updates={
                        _s(MORGAN, "coordination_posture"): "soliciting"
                    },
                ),
                branch(
                    MORGAN,
                    "decline_or_close_coordination_role",
                    when_all={
                        _o(MORGAN, "delivered_coordination_result"): "withdrawn"
                    },
                    state_updates={
                        _s(MORGAN, "coordination_posture"): "closed",
                        _s(MORGAN, "last_consumed_record_versions"): "consumed",
                    },
                ),
            ),
            lifecycle_names=(
                "proposal_and_plan",
                "resource_commitment_and_execution",
                "institutional_communication",
            ),
        ),
    ),
)


TCA = "trust_company_of_america"
TCA_OBSERVATIONS: Mapping[str, Domain] = {
    "participant_condition_notice": (
        "routine",
        "changed",
        "material_review_due",
        "disputed",
        "unknown",
    ),
    "company_condition_information": (
        "current",
        "stale",
        "incomplete",
        "disputed",
        "unknown",
    ),
    "governance_authority": (
        "authorized",
        "pending",
        "denied",
        "disputed",
        "absent",
        "unknown",
    ),
    "examination_request_or_result": (
        "none",
        "requested",
        "pending",
        "report_delivered",
        "disputed",
        "withdrawn",
    ),
    "support_route_state": (
        "submitted",
        "not_open",
        "draft",
        "pending",
        "information_needed",
        "conditioned",
        "declined",
        "withdrawn",
        "closed",
    ),
    "collateral_control_information": (
        "controlled",
        "incomplete",
        "uncontrolled",
        "disputed",
        "unknown",
    ),
    "service_condition": (
        "ordinary",
        "elevated",
        "strained",
        "disrupted",
        "unknown",
    ),
    "communication_matter": (
        "absent",
        "draft",
        "authorized",
        "stale",
        "disputed",
    ),
    "delivered_case_result": (
        "none",
        "delayed",
        "partial",
        "failed",
        "executed",
        "withdrawn",
        "disputed",
    ),
}
TCA_STATE: Mapping[str, Domain] = {
    "institutional_response_posture": (
        "ordinary",
        "verifying",
        "examination_pending",
        "support_preparing",
        "support_pending",
        "contingency",
        "communication_due",
        "close_due",
        "verify_due",
        "examination_consent_due",
        "information_provision_due",
        "information_terms_due",
        "support_update_due",
        "collateral_proposal_due",
        "support_close_due",
        "operational_proposal_due",
        "operational_authorization_due",
        "statement_authorization_due",
        "statement_issue_due",
        "statement_narrowing_due",
        "statement_correction_due",
    ),
    "last_consumed_record_versions": ("none", "consumed"),
}


def _tca_follow_up(intent_name: str, posture: str):
    return branch(
        TCA,
        intent_name,
        when_all={_s(TCA, "institutional_response_posture"): posture},
        state_updates={
            _s(TCA, "institutional_response_posture"): "ordinary",
            _s(TCA, "last_consumed_record_versions"): "consumed",
        },
    )


TCA_RESULT_FOLLOW_UPS = (
    ("verify_institutional_condition", "verify_due"),
    ("consent_to_scoped_examination", "examination_consent_due"),
    ("provide_scoped_case_information", "information_provision_due"),
    ("request_information_or_terms", "information_terms_due"),
    ("open_or_update_support_request", "support_update_due"),
    ("propose_collateral_package", "collateral_proposal_due"),
    ("withdraw_or_close_support_route", "support_close_due"),
    ("propose_operational_capacity_change", "operational_proposal_due"),
    ("authorize_operational_posture", "operational_authorization_due"),
    ("authorize_condition_statement", "statement_authorization_due"),
    ("issue_authorized_condition_statement", "statement_issue_due"),
    ("narrow_or_withhold_condition_statement", "statement_narrowing_due"),
    ("authorize_correction_or_update", "statement_correction_due"),
    ("close_or_pause_institutional_matter", "close_due"),
)


TRUST_COMPANY_OF_AMERICA_POLICY = policy(
    TCA,
    (
        decision(
            TCA,
            "DC-TCA-01",
            observation_domains=_only(
                TCA_OBSERVATIONS,
                (
                    "participant_condition_notice",
                    "company_condition_information",
                    "governance_authority",
                    "support_route_state",
                    "service_condition",
                    "communication_matter",
                ),
            ),
            state_domains=TCA_STATE,
            branches=(
                branch(
                    TCA,
                    "verify_institutional_condition",
                    when_all={_o(TCA, "company_condition_information"): "stale"},
                    state_updates={
                        _s(TCA, "institutional_response_posture"): "verifying"
                    },
                ),
                branch(
                    TCA,
                    "request_information_or_terms",
                    when_all={_o(TCA, "participant_condition_notice"): "unknown"},
                    state_updates={
                        _s(TCA, "institutional_response_posture"): "verifying"
                    },
                ),
                branch(
                    TCA,
                    "open_or_update_support_request",
                    when_all={
                        _o(TCA, "participant_condition_notice"): "material_review_due",
                        _o(TCA, "support_route_state"): "not_open",
                    },
                    state_updates={
                        _s(TCA, "institutional_response_posture"): "support_preparing"
                    },
                ),
                branch(
                    TCA,
                    "propose_operational_capacity_change",
                    when_all={_o(TCA, "service_condition"): "strained"},
                    state_updates={
                        _s(TCA, "institutional_response_posture"): "contingency"
                    },
                ),
                branch(
                    TCA,
                    "authorize_operational_posture",
                    when_all={
                        _o(TCA, "service_condition"): "elevated",
                        _o(TCA, "governance_authority"): "authorized",
                    },
                    state_updates={
                        _s(TCA, "institutional_response_posture"): "contingency"
                    },
                ),
                branch(
                    TCA,
                    "authorize_condition_statement",
                    when_all={
                        _o(TCA, "communication_matter"): "draft",
                        _o(TCA, "company_condition_information"): "current",
                    },
                    state_updates={
                        _s(TCA, "institutional_response_posture"): "communication_due"
                    },
                ),
                branch(
                    TCA,
                    "narrow_or_withhold_condition_statement",
                    when_all={
                        _o(TCA, "company_condition_information"): "disputed"
                    },
                    state_updates={
                        _s(TCA, "institutional_response_posture"): "communication_due"
                    },
                ),
            ),
            lifecycle_names=(
                "information_and_examination",
                "support_and_request_case",
                "governance_and_authority",
                "institutional_communication",
            ),
        ),
        decision(
            TCA,
            "DC-TCA-02",
            observation_domains=_only(
                TCA_OBSERVATIONS,
                (
                    "company_condition_information",
                    "governance_authority",
                    "examination_request_or_result",
                ),
            ),
            state_domains=TCA_STATE,
            branches=(
                branch(
                    TCA,
                    "consent_to_scoped_examination",
                    when_all={
                        _o(TCA, "examination_request_or_result"): "requested",
                        _o(TCA, "governance_authority"): "authorized",
                    },
                    state_updates={
                        _s(
                            TCA, "institutional_response_posture"
                        ): "examination_pending"
                    },
                ),
                branch(
                    TCA,
                    "provide_scoped_case_information",
                    when_all={
                        _o(TCA, "examination_request_or_result"): "pending",
                        _o(TCA, "company_condition_information"): "current",
                    },
                    state_updates={
                        _s(
                            TCA, "institutional_response_posture"
                        ): "examination_pending"
                    },
                ),
                branch(
                    TCA,
                    "request_information_or_terms",
                    when_all={
                        _o(TCA, "examination_request_or_result"): "disputed"
                    },
                    state_updates={
                        _s(TCA, "institutional_response_posture"): "verifying"
                    },
                ),
            ),
            lifecycle_names=(
                "information_and_examination",
                "governance_and_authority",
                "institutional_communication",
            ),
        ),
        decision(
            TCA,
            "DC-TCA-03",
            observation_domains=_only(
                TCA_OBSERVATIONS,
                (
                    "governance_authority",
                    "support_route_state",
                    "collateral_control_information",
                ),
            ),
            state_domains=TCA_STATE,
            branches=(
                branch(
                    TCA,
                    "open_or_update_support_request",
                    when_all={
                        _o(TCA, "support_route_state"): ("not_open", "draft")
                    },
                    state_updates={
                        _s(TCA, "institutional_response_posture"): "support_preparing"
                    },
                ),
                branch(
                    TCA,
                    "propose_collateral_package",
                    when_all={
                        _o(TCA, "support_route_state"): "information_needed",
                        _o(TCA, "collateral_control_information"): "controlled",
                    },
                    state_updates={
                        _s(TCA, "institutional_response_posture"): "support_preparing"
                    },
                ),
                branch(
                    TCA,
                    "request_information_or_terms",
                    when_all={_o(TCA, "support_route_state"): "conditioned"},
                    state_updates={
                        _s(TCA, "institutional_response_posture"): "support_pending"
                    },
                ),
                branch(
                    TCA,
                    "withdraw_or_close_support_route",
                    when_all={_o(TCA, "support_route_state"): "declined"},
                    state_updates={
                        _s(TCA, "institutional_response_posture"): "close_due"
                    },
                ),
            ),
            lifecycle_names=(
                "support_and_request_case",
                "collateral_and_facility_application",
                "governance_and_authority",
            ),
        ),
        decision(
            TCA,
            "DC-TCA-04",
            observation_domains=_only(
                TCA_OBSERVATIONS,
                (
                    "participant_condition_notice",
                    "company_condition_information",
                    "governance_authority",
                    "service_condition",
                ),
            ),
            state_domains=TCA_STATE,
            branches=(
                branch(
                    TCA,
                    "propose_operational_capacity_change",
                    when_all={_o(TCA, "service_condition"): "strained"},
                    state_updates={
                        _s(TCA, "institutional_response_posture"): "contingency"
                    },
                ),
                branch(
                    TCA,
                    "authorize_operational_posture",
                    when_all={
                        _o(TCA, "service_condition"): "elevated",
                        _o(TCA, "governance_authority"): "authorized",
                    },
                    state_updates={
                        _s(TCA, "institutional_response_posture"): "contingency"
                    },
                ),
                branch(
                    TCA,
                    "verify_institutional_condition",
                    when_all={_o(TCA, "company_condition_information"): "stale"},
                    state_updates={
                        _s(TCA, "institutional_response_posture"): "verifying"
                    },
                ),
            ),
            lifecycle_names=(
                "information_and_examination",
                "governance_and_authority",
                "withdrawal_service_and_payment",
            ),
        ),
        decision(
            TCA,
            "DC-TCA-05",
            observation_domains=_only(
                TCA_OBSERVATIONS,
                (
                    "participant_condition_notice",
                    "company_condition_information",
                    "governance_authority",
                    "communication_matter",
                ),
            ),
            state_domains=TCA_STATE,
            branches=(
                branch(
                    TCA,
                    "authorize_condition_statement",
                    when_all={
                        _o(TCA, "communication_matter"): "draft",
                        _o(TCA, "company_condition_information"): "current",
                        _o(TCA, "governance_authority"): "authorized",
                    },
                    state_updates={
                        _s(TCA, "institutional_response_posture"): "communication_due"
                    },
                ),
                branch(
                    TCA,
                    "issue_authorized_condition_statement",
                    when_all={
                        _o(TCA, "communication_matter"): "authorized",
                        _o(TCA, "participant_condition_notice"): "routine",
                    },
                    state_updates={
                        _s(TCA, "institutional_response_posture"): "communication_due"
                    },
                ),
                branch(
                    TCA,
                    "narrow_or_withhold_condition_statement",
                    when_all={
                        _o(TCA, "company_condition_information"): "disputed"
                    },
                    state_updates={
                        _s(TCA, "institutional_response_posture"): "communication_due"
                    },
                ),
                branch(
                    TCA,
                    "authorize_correction_or_update",
                    when_all={
                        _o(TCA, "participant_condition_notice"): "changed",
                        _o(TCA, "communication_matter"): "authorized",
                    },
                    state_updates={
                        _s(TCA, "institutional_response_posture"): "communication_due"
                    },
                ),
                branch(
                    TCA,
                    "verify_institutional_condition",
                    when_all={_o(TCA, "company_condition_information"): "unknown"},
                    state_updates={
                        _s(TCA, "institutional_response_posture"): "verifying"
                    },
                ),
            ),
            lifecycle_names=(
                "institutional_communication",
                "information_and_examination",
                "governance_and_authority",
            ),
        ),
        decision(
            TCA,
            "DC-TCA-06",
            observation_domains=TCA_OBSERVATIONS,
            state_domains=TCA_STATE,
            branches=tuple(_tca_follow_up(*item) for item in TCA_RESULT_FOLLOW_UPS),
            lifecycle_names=(
                "information_and_examination",
                "support_and_request_case",
                "collateral_and_facility_application",
                "withdrawal_service_and_payment",
                "institutional_communication",
                "resource_commitment_and_execution",
            ),
            revisit_observation_names=(
                "examination_request_or_result",
                "support_route_state",
                "delivered_case_result",
            ),
        ),
    ),
)


LINCOLN = "lincoln_trust_company"
LINCOLN_OBSERVATIONS: Mapping[str, Domain] = {
    "condition_statement_proposal": (
        "absent",
        "complete",
        "incomplete",
        "disputed",
    ),
    "lincoln_condition_information": (
        "current",
        "stale",
        "incomplete",
        "disputed",
        "unknown",
    ),
    "communication_decision_authority": (
        "absent",
        "competent_to_decide",
        "pending",
        "denied_scope",
        "disputed",
        "unknown",
    ),
    "statement_authorization_state": (
        "none",
        "pending",
        "authorized",
        "narrowed",
        "withheld",
        "superseded",
        "disputed",
    ),
    "message_lifecycle": (
        "none",
        "proposed",
        "issued",
        "transport_pending",
        "delivered",
        "expired",
        "failed",
    ),
    "material_information_update": ("none", "delivered", "disputed"),
}
LINCOLN_STATE: Mapping[str, Domain] = {
    "communication_posture": (
        "closed",
        "verifying",
        "awaiting_authority",
        "authorized",
        "withheld",
        "issued",
        "correction_due",
    ),
    "last_consumed_record_versions": ("none", "consumed"),
}


LINCOLN_TRUST_COMPANY_POLICY = policy(
    LINCOLN,
    (
        decision(
            LINCOLN,
            "DC-LTC-01",
            observation_domains=_only(
                LINCOLN_OBSERVATIONS,
                (
                    "condition_statement_proposal",
                    "lincoln_condition_information",
                    "communication_decision_authority",
                ),
            ),
            state_domains=LINCOLN_STATE,
            branches=(
                branch(
                    LINCOLN,
                    "request_condition_information",
                    when_all={
                        _o(LINCOLN, "condition_statement_proposal"): "incomplete"
                    },
                    state_updates={
                        _s(LINCOLN, "communication_posture"): "verifying"
                    },
                ),
                branch(
                    LINCOLN,
                    "authorize_condition_statement",
                    when_all={
                        _o(LINCOLN, "condition_statement_proposal"): "complete",
                        _o(LINCOLN, "lincoln_condition_information"): "current",
                        _o(
                            LINCOLN, "communication_decision_authority"
                        ): "competent_to_decide",
                    },
                    state_updates={
                        _s(LINCOLN, "communication_posture"): "authorized"
                    },
                ),
                branch(
                    LINCOLN,
                    "narrow_or_withhold_condition_statement",
                    when_all={
                        _o(LINCOLN, "lincoln_condition_information"): (
                            "stale",
                            "disputed",
                        )
                    },
                    state_updates={
                        _s(LINCOLN, "communication_posture"): "withheld"
                    },
                ),
            ),
            lifecycle_names=(
                "information_and_examination",
                "governance_and_authority",
                "institutional_communication",
            ),
        ),
        decision(
            LINCOLN,
            "DC-LTC-02",
            observation_domains=_only(
                LINCOLN_OBSERVATIONS,
                (
                    "lincoln_condition_information",
                    "statement_authorization_state",
                    "message_lifecycle",
                ),
            ),
            state_domains=LINCOLN_STATE,
            branches=(
                branch(
                    LINCOLN,
                    "issue_authorized_condition_statement",
                    when_all={
                        _o(LINCOLN, "statement_authorization_state"): "authorized",
                        _o(LINCOLN, "message_lifecycle"): "none",
                    },
                    state_updates={
                        _s(LINCOLN, "communication_posture"): "issued"
                    },
                ),
            ),
            lifecycle_names=("institutional_communication",),
        ),
        decision(
            LINCOLN,
            "DC-LTC-03",
            observation_domains=_only(
                LINCOLN_OBSERVATIONS,
                (
                    "lincoln_condition_information",
                    "statement_authorization_state",
                    "material_information_update",
                ),
            ),
            state_domains=LINCOLN_STATE,
            branches=(
                branch(
                    LINCOLN,
                    "authorize_correction_or_update",
                    when_all={
                        _o(LINCOLN, "material_information_update"): "delivered"
                    },
                    state_updates={
                        _s(LINCOLN, "communication_posture"): "correction_due",
                        _s(LINCOLN, "last_consumed_record_versions"): "consumed",
                    },
                ),
                branch(
                    LINCOLN,
                    "request_condition_information",
                    when_all={
                        _o(LINCOLN, "lincoln_condition_information"): "stale"
                    },
                    state_updates={
                        _s(LINCOLN, "communication_posture"): "verifying"
                    },
                ),
                branch(
                    LINCOLN,
                    "narrow_or_withhold_condition_statement",
                    when_all={
                        _o(LINCOLN, "statement_authorization_state"): "superseded"
                    },
                    state_updates={
                        _s(LINCOLN, "communication_posture"): "withheld"
                    },
                ),
            ),
            lifecycle_names=(
                "institutional_communication",
                "information_and_examination",
            ),
        ),
        decision(
            LINCOLN,
            "DC-LTC-04",
            observation_domains=_only(
                LINCOLN_OBSERVATIONS,
                ("statement_authorization_state", "message_lifecycle"),
            ),
            state_domains=LINCOLN_STATE,
            branches=(
                branch(
                    LINCOLN,
                    "request_message_delivery_clarification",
                    when_all={
                        _o(LINCOLN, "message_lifecycle"): ("expired", "failed")
                    },
                    state_updates={
                        _s(LINCOLN, "communication_posture"): "verifying"
                    },
                ),
                branch(
                    LINCOLN,
                    "close_communication_matter",
                    when_all={_o(LINCOLN, "message_lifecycle"): "delivered"},
                    state_updates={
                        _s(LINCOLN, "communication_posture"): "closed",
                        _s(LINCOLN, "last_consumed_record_versions"): "consumed",
                    },
                ),
            ),
            lifecycle_names=("institutional_communication",),
        ),
    ),
)


COMMITTEE = "trust_presidents_committee"
COMMITTEE_OBSERVATIONS: Mapping[str, Domain] = {
    "committee_mandate": (
        "absent",
        "authorized",
        "limited",
        "disputed",
        "unknown",
    ),
    "case_type_review_standard": ("absent", "pinned", "disputed"),
    "assistance_application": (
        "absent",
        "complete",
        "incomplete",
        "duplicate",
        "disputed",
    ),
    "case_information_package": (
        "absent",
        "incomplete",
        "adequate",
        "disputed",
    ),
    "examination_status_or_report": (
        "not_requested",
        "pending",
        "delivered",
        "disputed",
        "withdrawn",
    ),
    "reporting_opportunity": ("none", "open", "expired"),
    "delivered_continuity_assessment": (
        "absent",
        "supportive",
        "adverse",
        "uncertain",
        "disputed",
    ),
    "coordination_authority": (
        "absent",
        "authorized",
        "limited",
        "denied",
        "disputed",
        "unknown",
    ),
    "contributor_reply": (
        "none",
        "pending",
        "conditioned",
        "committed",
        "declined",
        "expired",
        "disputed",
    ),
    "process_disposition_or_result": (
        "none",
        "delayed",
        "partial",
        "failed",
        "executed",
        "expired",
        "disputed",
    ),
}
COMMITTEE_STATE: Mapping[str, Domain] = {
    "declared_information_inventory": (
        "absent",
        "incomplete",
        "sufficient",
        "qualified",
    ),
    "bounded_decision_posture": (
        "idle",
        "reviewing",
        "recommendation_ready",
        "reporting",
        "soliciting",
        "assembling",
        "awaiting",
        "closed",
    ),
}


TRUST_PRESIDENTS_COMMITTEE_POLICY = policy(
    COMMITTEE,
    (
        decision(
            COMMITTEE,
            "DC-TPC-01",
            observation_domains=_only(
                COMMITTEE_OBSERVATIONS,
                ("committee_mandate", "assistance_application"),
            ),
            state_domains=COMMITTEE_STATE,
            branches=(
                branch(
                    COMMITTEE,
                    "open_or_refer_assistance_case",
                    when_all={
                        _o(COMMITTEE, "committee_mandate"): "authorized",
                        _o(COMMITTEE, "assistance_application"): "complete",
                    },
                    state_updates={
                        _s(COMMITTEE, "bounded_decision_posture"): "reviewing"
                    },
                ),
                branch(
                    COMMITTEE,
                    "await_case_or_plan_result",
                    when_all={
                        _o(COMMITTEE, "assistance_application"): "duplicate"
                    },
                    state_updates={
                        _s(COMMITTEE, "bounded_decision_posture"): "awaiting"
                    },
                ),
            ),
            lifecycle_names=("support_and_request_case",),
        ),
        decision(
            COMMITTEE,
            "DC-TPC-02",
            observation_domains=_only(
                COMMITTEE_OBSERVATIONS,
                (
                    "committee_mandate",
                    "case_type_review_standard",
                    "assistance_application",
                    "case_information_package",
                    "examination_status_or_report",
                ),
            ),
            state_domains=COMMITTEE_STATE,
            branches=(
                branch(
                    COMMITTEE,
                    "request_case_information",
                    when_all={
                        _o(COMMITTEE, "case_information_package"): "incomplete"
                    },
                    state_updates={
                        _s(COMMITTEE, "bounded_decision_posture"): "reviewing",
                        _s(COMMITTEE, "declared_information_inventory"): "incomplete",
                    },
                ),
                branch(
                    COMMITTEE,
                    "request_scoped_examination",
                    when_all={
                        _o(COMMITTEE, "case_information_package"): "disputed",
                        _o(
                            COMMITTEE, "examination_status_or_report"
                        ): "not_requested",
                    },
                    state_updates={
                        _s(COMMITTEE, "bounded_decision_posture"): "reviewing"
                    },
                ),
                branch(
                    COMMITTEE,
                    "issue_case_recommendation",
                    when_all={
                        _o(COMMITTEE, "case_information_package"): "adequate",
                        _o(COMMITTEE, "case_type_review_standard"): "pinned",
                    },
                    state_updates={
                        _s(
                            COMMITTEE, "bounded_decision_posture"
                        ): "recommendation_ready",
                        _s(COMMITTEE, "declared_information_inventory"): "sufficient",
                    },
                ),
            ),
            lifecycle_names=(
                "information_and_examination",
                "support_and_request_case",
            ),
        ),
        decision(
            COMMITTEE,
            "DC-TPC-03",
            observation_domains=_only(
                COMMITTEE_OBSERVATIONS,
                (
                    "committee_mandate",
                    "case_type_review_standard",
                    "case_information_package",
                    "examination_status_or_report",
                    "reporting_opportunity",
                    "delivered_continuity_assessment",
                ),
            ),
            state_domains=COMMITTEE_STATE,
            branches=(
                branch(
                    COMMITTEE,
                    "issue_case_recommendation",
                    when_all={
                        _o(COMMITTEE, "reporting_opportunity"): "open",
                        _o(COMMITTEE, "case_information_package"): "adequate",
                        _o(COMMITTEE, "delivered_continuity_assessment"): (
                            "supportive",
                            "adverse",
                            "uncertain",
                        ),
                    },
                    state_updates={
                        _s(
                            COMMITTEE, "bounded_decision_posture"
                        ): "recommendation_ready"
                    },
                ),
            ),
            lifecycle_names=(
                "information_and_examination",
                "institutional_communication",
            ),
        ),
        decision(
            COMMITTEE,
            "DC-TPC-04",
            observation_domains=_only(
                COMMITTEE_OBSERVATIONS,
                ("committee_mandate", "reporting_opportunity"),
            ),
            state_domains=COMMITTEE_STATE,
            branches=(
                branch(
                    COMMITTEE,
                    "report_case_status",
                    when_all={
                        _o(COMMITTEE, "reporting_opportunity"): "open",
                        _s(
                            COMMITTEE, "bounded_decision_posture"
                        ): "recommendation_ready",
                    },
                    state_updates={
                        _s(COMMITTEE, "bounded_decision_posture"): "reporting"
                    },
                ),
            ),
            lifecycle_names=("institutional_communication",),
        ),
        decision(
            COMMITTEE,
            "DC-TPC-05",
            observation_domains=_only(
                COMMITTEE_OBSERVATIONS,
                (
                    "committee_mandate",
                    "coordination_authority",
                    "contributor_reply",
                ),
            ),
            state_domains=COMMITTEE_STATE,
            branches=(
                branch(
                    COMMITTEE,
                    "solicit_independent_contribution",
                    when_all={
                        _o(COMMITTEE, "coordination_authority"): "authorized",
                        _o(COMMITTEE, "contributor_reply"): "none",
                    },
                    state_updates={
                        _s(COMMITTEE, "bounded_decision_posture"): "soliciting"
                    },
                ),
                branch(
                    COMMITTEE,
                    "assemble_or_revise_support_plan",
                    when_all={_o(COMMITTEE, "contributor_reply"): "committed"},
                    state_updates={
                        _s(COMMITTEE, "bounded_decision_posture"): "assembling"
                    },
                ),
                branch(
                    COMMITTEE,
                    "await_case_or_plan_result",
                    when_all={_o(COMMITTEE, "contributor_reply"): "pending"},
                    state_updates={
                        _s(COMMITTEE, "bounded_decision_posture"): "awaiting"
                    },
                ),
            ),
            lifecycle_names=(
                "solicitation_and_independent_reply",
                "proposal_and_plan",
            ),
        ),
        decision(
            COMMITTEE,
            "DC-TPC-06",
            observation_domains=_only(
                COMMITTEE_OBSERVATIONS,
                (
                    "committee_mandate",
                    "contributor_reply",
                    "process_disposition_or_result",
                ),
            ),
            state_domains=COMMITTEE_STATE,
            branches=(
                branch(
                    COMMITTEE,
                    "assemble_or_revise_support_plan",
                    when_all={
                        _o(COMMITTEE, "process_disposition_or_result"): (
                            "partial",
                            "failed",
                        )
                    },
                    state_updates={
                        _s(COMMITTEE, "bounded_decision_posture"): "assembling"
                    },
                ),
                branch(
                    COMMITTEE,
                    "report_case_status",
                    when_all={
                        _o(COMMITTEE, "process_disposition_or_result"): "executed"
                    },
                    state_updates={
                        _s(COMMITTEE, "bounded_decision_posture"): "reporting"
                    },
                ),
                branch(
                    COMMITTEE,
                    "await_case_or_plan_result",
                    when_all={
                        _o(COMMITTEE, "process_disposition_or_result"): "delayed"
                    },
                    state_updates={
                        _s(COMMITTEE, "bounded_decision_posture"): "awaiting"
                    },
                ),
            ),
            lifecycle_names=(
                "resource_commitment_and_execution",
                "proposal_and_plan",
                "institutional_communication",
            ),
        ),
    ),
)


INSTITUTION_PARTICIPANT_POLICIES: tuple[RuleParticipantPolicy, ...] = (
    J_PIERPONT_MORGAN_POLICY,
    TRUST_COMPANY_OF_AMERICA_POLICY,
    LINCOLN_TRUST_COMPANY_POLICY,
    TRUST_PRESIDENTS_COMMITTEE_POLICY,
)


__all__ = [
    "INSTITUTION_PARTICIPANT_POLICIES",
    "J_PIERPONT_MORGAN_POLICY",
    "LINCOLN_TRUST_COMPANY_POLICY",
    "TRUST_COMPANY_OF_AMERICA_POLICY",
    "TRUST_PRESIDENTS_COMMITTEE_POLICY",
]
