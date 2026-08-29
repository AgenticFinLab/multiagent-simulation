"""Panic Rule policies for Knickerbocker, NBC, and the clearing house."""

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


KT = "knickerbocker_trust"
KT_OBSERVATIONS: Mapping[str, Domain] = {
    "internal_liquidity_assessment": ("adequate", "strained", "critical", "unknown"),
    "withdrawal_pressure": ("ordinary", "elevated", "severe", "unknown"),
    "asset_liquidity_assessment": (
        "readily_available",
        "conditionally_liquid",
        "illiquid",
        "disputed",
        "unknown",
    ),
    "collateral_package_status": (
        "available",
        "not_prepared",
        "preparing",
        "submitted",
        "disputed",
        "unknown",
    ),
    "corporate_authorization": (
        "authorized",
        "not_requested",
        "pending",
        "denied",
        "unknown",
    ),
    "clearing_channel_status": (
        "active",
        "termination_notice_delivered",
        "ending_at_time",
        "inactive",
        "disputed",
        "unknown",
    ),
    "support_request_status": (
        "none",
        "prepared",
        "sent",
        "delivered",
        "awaiting_information",
        "under_review",
        "refused",
        "expired",
        "withdrawn",
        "partial",
        "failed",
        "executed",
        "unknown",
    ),
    "received_information_request": ("none", "delivered", "disputed"),
    "delivered_disposition": (
        "none",
        "pending",
        "need_information",
        "referred",
        "refused",
        "prohibited",
        "delayed",
        "partial",
        "failed",
        "executed",
    ),
}
KT_STATE: Mapping[str, Domain] = {
    "last_verified_condition_time": ("absent", "current", "verification_pending"),
    "operational_posture": (
        "ordinary",
        "contingency_prepared",
        "communication_due",
    ),
    "request_strategy_posture": (
        "no_active_request",
        "preparing",
        "submitted",
        "awaiting_response",
        "revising",
    ),
    "last_consumed_authoritative_references": ("none", "consumed"),
}


KNICKERBOCKER_TRUST_POLICY = policy(
    KT,
    (
        decision(
            KT,
            "DC-KT-01",
            observation_domains=_only(
                KT_OBSERVATIONS,
                (
                    "internal_liquidity_assessment",
                    "withdrawal_pressure",
                    "corporate_authorization",
                ),
            ),
            state_domains=KT_STATE,
            branches=(
                branch(
                    KT,
                    "verify_internal_condition",
                    when_all={_o(KT, "internal_liquidity_assessment"): "unknown"},
                    state_updates={
                        _s(KT, "last_verified_condition_time"): "verification_pending"
                    },
                ),
                branch(
                    KT,
                    "seek_institutional_authorization",
                    when_all={_o(KT, "corporate_authorization"): "pending"},
                    state_updates={_s(KT, "request_strategy_posture"): "preparing"},
                ),
                branch(
                    KT,
                    "prepare_information_package",
                    when_all={_o(KT, "internal_liquidity_assessment"): "strained"},
                    state_updates={_s(KT, "request_strategy_posture"): "preparing"},
                ),
                branch(
                    KT,
                    "prepare_operational_contingency",
                    when_all={_o(KT, "withdrawal_pressure"): "severe"},
                    state_updates={
                        _s(KT, "operational_posture"): "contingency_prepared"
                    },
                ),
            ),
            lifecycle_names=(
                "information_and_examination",
                "governance_and_authority",
                "proposal_and_plan",
                "withdrawal_service_and_payment",
            ),
        ),
        decision(
            KT,
            "DC-KT-02",
            observation_domains=_only(
                KT_OBSERVATIONS,
                (
                    "internal_liquidity_assessment",
                    "asset_liquidity_assessment",
                    "collateral_package_status",
                    "corporate_authorization",
                    "clearing_channel_status",
                    "support_request_status",
                ),
            ),
            state_domains=KT_STATE,
            branches=(
                branch(
                    KT,
                    "submit_support_request",
                    when_all={
                        _o(KT, "internal_liquidity_assessment"): "critical",
                        _o(KT, "collateral_package_status"): "available",
                        _o(KT, "corporate_authorization"): "authorized",
                        _o(KT, "support_request_status"): "none",
                    },
                    state_updates={_s(KT, "request_strategy_posture"): "submitted"},
                ),
                branch(
                    KT,
                    "request_channel_confirmation",
                    when_all={_o(KT, "clearing_channel_status"): "unknown"},
                    state_updates={_s(KT, "request_strategy_posture"): "preparing"},
                ),
                branch(
                    KT,
                    "prepare_information_package",
                    when_all={_o(KT, "collateral_package_status"): "not_prepared"},
                    state_updates={_s(KT, "request_strategy_posture"): "preparing"},
                ),
                branch(
                    KT,
                    "seek_institutional_authorization",
                    when_all={_o(KT, "corporate_authorization"): "pending"},
                    state_updates={_s(KT, "request_strategy_posture"): "preparing"},
                ),
            ),
            lifecycle_names=(
                "support_and_request_case",
                "governance_and_authority",
                "information_and_examination",
                "credit_and_clearing_relationship",
            ),
        ),
        decision(
            KT,
            "DC-KT-03",
            observation_domains=_only(
                KT_OBSERVATIONS,
                (
                    "collateral_package_status",
                    "corporate_authorization",
                    "support_request_status",
                    "received_information_request",
                    "delivered_disposition",
                ),
            ),
            state_domains=KT_STATE,
            branches=(
                branch(
                    KT,
                    "provide_requested_information",
                    when_all={_o(KT, "received_information_request"): "delivered"},
                    state_updates={
                        _s(KT, "last_consumed_authoritative_references"): "consumed"
                    },
                ),
                branch(
                    KT,
                    "request_status_clarification",
                    when_all={_o(KT, "support_request_status"): "under_review"},
                    state_updates={
                        _s(KT, "request_strategy_posture"): "awaiting_response"
                    },
                ),
                branch(
                    KT,
                    "revise_or_withdraw_request",
                    when_all={_o(KT, "delivered_disposition"): "refused"},
                    state_updates={_s(KT, "request_strategy_posture"): "revising"},
                ),
                branch(
                    KT,
                    "prepare_operational_contingency",
                    when_all={_o(KT, "delivered_disposition"): "failed"},
                    state_updates={
                        _s(KT, "operational_posture"): "contingency_prepared"
                    },
                ),
            ),
            lifecycle_names=(
                "information_and_examination",
                "support_and_request_case",
                "institutional_communication",
            ),
        ),
        decision(
            KT,
            "DC-KT-04",
            observation_domains=_only(
                KT_OBSERVATIONS,
                (
                    "withdrawal_pressure",
                    "asset_liquidity_assessment",
                    "corporate_authorization",
                    "clearing_channel_status",
                    "support_request_status",
                    "delivered_disposition",
                ),
            ),
            state_domains=KT_STATE,
            branches=(
                branch(
                    KT,
                    "request_result_clarification",
                    when_all={_o(KT, "delivered_disposition"): "delayed"},
                    state_updates={
                        _s(KT, "request_strategy_posture"): "awaiting_response"
                    },
                ),
                branch(
                    KT,
                    "issue_institutional_communication",
                    when_all={_o(KT, "delivered_disposition"): "refused"},
                    state_updates={_s(KT, "operational_posture"): "communication_due"},
                ),
                branch(
                    KT,
                    "prepare_operational_contingency",
                    when_all={_o(KT, "withdrawal_pressure"): "severe"},
                    state_updates={
                        _s(KT, "operational_posture"): "contingency_prepared"
                    },
                ),
                branch(
                    KT,
                    "request_channel_confirmation",
                    when_all={_o(KT, "clearing_channel_status"): "unknown"},
                    state_updates={_s(KT, "request_strategy_posture"): "preparing"},
                ),
            ),
            lifecycle_names=(
                "institutional_communication",
                "support_and_request_case",
                "credit_and_clearing_relationship",
                "withdrawal_service_and_payment",
            ),
        ),
    ),
)


NYCH = "new_york_clearing_house"
NYCH_OBSERVATIONS: Mapping[str, Domain] = {
    "delivered_request": ("absent", "complete", "incomplete", "disputed"),
    "relationship_status": (
        "active",
        "inactive",
        "notice_pending",
        "disputed",
        "unknown",
    ),
    "route_classification": (
        "unresolved",
        "member_facility",
        "nonmember_clearing_matter",
        "other_identified_route",
    ),
    "facility_eligibility": (
        "eligible",
        "ineligible",
        "not_applicable",
        "disputed",
        "unknown",
    ),
    "request_authorization_evidence": (
        "absent",
        "sufficient",
        "incomplete",
        "disputed",
        "unknown",
    ),
    "financial_information_status": (
        "not_received",
        "incomplete",
        "stale",
        "adequate_for_scope",
        "disputed",
        "unknown",
    ),
    "review_state": (
        "not_open",
        "collecting_information",
        "examining",
        "awaiting_forum",
        "decision_ready",
        "complete",
        "closed",
    ),
    "authority_state": (
        "no_competent_authority_identified",
        "committee_scope",
        "membership_scope_required",
        "authorized",
        "denied",
        "disputed",
        "unknown",
    ),
    "resource_proposal_status": (
        "none",
        "information_needed",
        "collateral_review",
        "member_consultation",
        "conditionally_authorized",
        "scheduled",
        "partial",
        "failed",
        "executed",
        "withdrawn",
    ),
    "case_disposition_status": (
        "none",
        "pending",
        "information_needed",
        "referred",
        "facility_declined",
        "other_scoped_decline",
        "conditioned_proposal",
        "closed",
    ),
    "case_communication_status": (
        "not_issued",
        "issued",
        "transport_pending",
        "delivered",
        "expired",
        "failed",
        "unknown",
    ),
    "delivered_case_result": (
        "none",
        "delayed",
        "partial",
        "failed",
        "executed",
        "withdrawn",
    ),
}
NYCH_STATE: Mapping[str, Domain] = {
    "procedural_assessment_posture": (
        "unclassified",
        "classified",
        "reviewing",
        "awaiting_authority",
        "disposition_ready",
        "closed",
    ),
    "last_consumed_record_versions": ("none", "consumed"),
}


NEW_YORK_CLEARING_HOUSE_POLICY = policy(
    NYCH,
    (
        decision(
            NYCH,
            "DC-NYCH-01",
            observation_domains=_only(
                NYCH_OBSERVATIONS,
                (
                    "delivered_request",
                    "relationship_status",
                    "route_classification",
                    "facility_eligibility",
                    "request_authorization_evidence",
                ),
            ),
            state_domains=NYCH_STATE,
            branches=(
                branch(
                    NYCH,
                    "record_and_classify_request",
                    when_all={
                        _o(NYCH, "delivered_request"): "complete",
                        _o(NYCH, "route_classification"): "member_facility",
                    },
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "classified"
                    },
                ),
                branch(
                    NYCH,
                    "request_case_information",
                    when_all={_o(NYCH, "delivered_request"): "incomplete"},
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "reviewing"
                    },
                ),
                branch(
                    NYCH,
                    "seek_procedural_authority",
                    when_all={
                        _o(NYCH, "request_authorization_evidence"): "incomplete"
                    },
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "awaiting_authority"
                    },
                ),
                branch(
                    NYCH,
                    "refer_request",
                    when_all={
                        _o(NYCH, "route_classification"): "other_identified_route"
                    },
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "classified"
                    },
                ),
                branch(
                    NYCH,
                    "communicate_case_status",
                    when_all={_o(NYCH, "relationship_status"): "disputed"},
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "reviewing"
                    },
                ),
            ),
            lifecycle_names=(
                "support_and_request_case",
                "governance_and_authority",
                "institutional_communication",
            ),
        ),
        decision(
            NYCH,
            "DC-NYCH-02",
            observation_domains=_only(
                NYCH_OBSERVATIONS,
                (
                    "delivered_request",
                    "route_classification",
                    "request_authorization_evidence",
                    "financial_information_status",
                    "review_state",
                    "authority_state",
                ),
            ),
            state_domains=NYCH_STATE,
            branches=(
                branch(
                    NYCH,
                    "request_case_information",
                    when_all={
                        _o(NYCH, "financial_information_status"): "incomplete"
                    },
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "reviewing"
                    },
                ),
                branch(
                    NYCH,
                    "open_or_continue_review",
                    when_all={
                        _o(NYCH, "financial_information_status"): "adequate_for_scope",
                        _o(NYCH, "review_state"): "not_open",
                    },
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "reviewing"
                    },
                ),
                branch(
                    NYCH,
                    "seek_procedural_authority",
                    when_all={_o(NYCH, "authority_state"): "unknown"},
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "awaiting_authority"
                    },
                ),
                branch(
                    NYCH,
                    "communicate_case_status",
                    when_all={_o(NYCH, "review_state"): "examining"},
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "reviewing"
                    },
                ),
                branch(
                    NYCH,
                    "refer_request",
                    when_all={
                        _o(NYCH, "route_classification"): "other_identified_route"
                    },
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "classified"
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
            NYCH,
            "DC-NYCH-03",
            observation_domains=_only(
                NYCH_OBSERVATIONS,
                (
                    "relationship_status",
                    "route_classification",
                    "facility_eligibility",
                    "review_state",
                    "authority_state",
                ),
            ),
            state_domains=NYCH_STATE,
            branches=(
                branch(
                    NYCH,
                    "issue_typed_decline",
                    when_all={_o(NYCH, "facility_eligibility"): "ineligible"},
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "disposition_ready"
                    },
                ),
                branch(
                    NYCH,
                    "seek_procedural_authority",
                    when_all={_o(NYCH, "authority_state"): "unknown"},
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "awaiting_authority"
                    },
                ),
                branch(
                    NYCH,
                    "refer_request",
                    when_all={
                        _o(NYCH, "route_classification"): "other_identified_route"
                    },
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "classified"
                    },
                ),
                branch(
                    NYCH,
                    "communicate_case_status",
                    when_all={_o(NYCH, "relationship_status"): "disputed"},
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "reviewing"
                    },
                ),
            ),
            lifecycle_names=(
                "support_and_request_case",
                "governance_and_authority",
                "institutional_communication",
            ),
        ),
        decision(
            NYCH,
            "DC-NYCH-04",
            observation_domains=_only(
                NYCH_OBSERVATIONS,
                (
                    "delivered_request",
                    "route_classification",
                    "request_authorization_evidence",
                    "financial_information_status",
                    "review_state",
                    "authority_state",
                    "resource_proposal_status",
                ),
            ),
            state_domains=NYCH_STATE,
            branches=(
                branch(
                    NYCH,
                    "request_case_information",
                    when_all={
                        _o(NYCH, "financial_information_status"): "incomplete"
                    },
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "reviewing"
                    },
                ),
                branch(
                    NYCH,
                    "seek_member_or_association_authorization",
                    when_all={
                        _o(NYCH, "authority_state"): "membership_scope_required"
                    },
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "awaiting_authority"
                    },
                ),
                branch(
                    NYCH,
                    "propose_conditioned_measure",
                    when_all={
                        _o(NYCH, "authority_state"): "authorized",
                        _o(NYCH, "financial_information_status"): "adequate_for_scope",
                    },
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "disposition_ready"
                    },
                ),
                branch(
                    NYCH,
                    "communicate_case_status",
                    when_all={
                        _o(NYCH, "resource_proposal_status"): "member_consultation"
                    },
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "reviewing"
                    },
                ),
            ),
            lifecycle_names=(
                "proposal_and_plan",
                "resource_commitment_and_execution",
                "governance_and_authority",
                "institutional_communication",
            ),
        ),
        decision(
            NYCH,
            "DC-NYCH-05",
            observation_domains=_only(
                NYCH_OBSERVATIONS,
                (
                    "delivered_request",
                    "route_classification",
                    "resource_proposal_status",
                    "case_disposition_status",
                    "case_communication_status",
                    "delivered_case_result",
                ),
            ),
            state_domains=NYCH_STATE,
            branches=(
                branch(
                    NYCH,
                    "communicate_case_status",
                    when_all={_o(NYCH, "case_disposition_status"): "pending"},
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "disposition_ready"
                    },
                ),
                branch(
                    NYCH,
                    "issue_typed_decline",
                    when_all={
                        _o(NYCH, "case_disposition_status"): "facility_declined"
                    },
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "disposition_ready"
                    },
                ),
                branch(
                    NYCH,
                    "refer_request",
                    when_all={_o(NYCH, "case_disposition_status"): "referred"},
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "classified"
                    },
                ),
                branch(
                    NYCH,
                    "request_case_information",
                    when_all={
                        _o(NYCH, "case_disposition_status"): "information_needed"
                    },
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "reviewing"
                    },
                ),
                branch(
                    NYCH,
                    "close_or_reopen_review",
                    when_all={
                        _o(NYCH, "delivered_case_result"): (
                            "executed",
                            "failed",
                            "withdrawn",
                        )
                    },
                    state_updates={
                        _s(NYCH, "procedural_assessment_posture"): "closed",
                        _s(NYCH, "last_consumed_record_versions"): "consumed",
                    },
                ),
            ),
            lifecycle_names=(
                "support_and_request_case",
                "proposal_and_plan",
                "institutional_communication",
                "resource_commitment_and_execution",
            ),
        ),
    ),
)


NBC = "national_bank_of_commerce"
NBC_OBSERVATIONS: Mapping[str, Domain] = {
    "clearing_relationship_status": (
        "active",
        "notice_pending",
        "ending_at_time",
        "inactive",
        "disputed",
        "unknown",
    ),
    "clearing_exposure_record": ("current", "stale", "missing", "disputed"),
    "credit_exposure_record": (
        "current",
        "capacity_available",
        "bounded",
        "stale",
        "missing",
        "disputed",
    ),
    "participant_review_notice": ("none", "due", "disputed", "unknown"),
    "counterparty_condition_information": (
        "current",
        "incomplete",
        "stale",
        "missing",
        "disputed",
    ),
    "counterparty_request": ("absent", "complete", "incomplete", "disputed"),
    "nbc_corporate_authority": (
        "authorized",
        "not_requested",
        "pending",
        "denied",
        "disputed",
        "unknown",
    ),
    "nych_clearing_direction": (
        "none_delivered",
        "direction_delivered",
        "clarification_pending",
        "disputed",
        "unknown",
    ),
    "nych_request_disposition": (
        "none",
        "pending",
        "information_needed",
        "referred",
        "scoped_decline",
        "conditioned_proposal",
        "delayed",
        "partial",
        "failed",
        "executed",
        "unknown",
    ),
    "incremental_recovery_assessment": (
        "protected",
        "no_post_possession_lien",
        "uncertain",
        "disputed",
        "unknown",
    ),
    "message_and_notice_status": (
        "delivered",
        "prepared",
        "issued",
        "transport_pending",
        "expired",
        "failed",
        "unknown",
    ),
    "delivered_credit_or_relationship_result": (
        "none",
        "no_change",
        "conditioned",
        "partial",
        "failed",
        "effective",
        "reversed",
        "disputed",
    ),
}
NBC_STATE: Mapping[str, Domain] = {
    "exposure_review_posture": ("unreviewed", "reviewing", "verified", "bounded"),
    "intermediation_posture": (
        "unclassified",
        "forwarding",
        "sponsorship_ready",
        "declined",
    ),
    "communication_posture": (
        "idle",
        "position_due",
        "result_clarification_due",
        "exposure_verification_due",
        "counterparty_information_due",
        "authority_due",
        "credit_posture_due",
        "credit_limit_due",
        "intermediation_clarification_due",
        "forwarding_due",
        "sponsorship_due",
        "intermediation_decline_due",
        "direction_clarification_due",
        "continuation_due",
        "relationship_condition_due",
        "termination_notice_due",
    ),
    "last_consumed_record_versions": ("none", "consumed"),
}


def _nbc_follow_up(intent_name: str, posture: str):
    return branch(
        NBC,
        intent_name,
        when_all={_s(NBC, "communication_posture"): posture},
        state_updates={
            _s(NBC, "communication_posture"): "idle",
            _s(NBC, "last_consumed_record_versions"): "consumed",
        },
    )


NATIONAL_BANK_OF_COMMERCE_POLICY = policy(
    NBC,
    (
        decision(
            NBC,
            "DC-NBC-01",
            observation_domains=_only(
                NBC_OBSERVATIONS,
                (
                    "clearing_relationship_status",
                    "clearing_exposure_record",
                    "credit_exposure_record",
                    "participant_review_notice",
                    "counterparty_condition_information",
                    "nbc_corporate_authority",
                    "incremental_recovery_assessment",
                    "delivered_credit_or_relationship_result",
                ),
            ),
            state_domains=NBC_STATE,
            branches=(
                branch(
                    NBC,
                    "verify_nbc_exposure",
                    when_all={
                        _o(NBC, "participant_review_notice"): "due",
                        _o(NBC, "credit_exposure_record"): "stale",
                    },
                    state_updates={
                        _s(NBC, "exposure_review_posture"): "reviewing"
                    },
                ),
                branch(
                    NBC,
                    "request_counterparty_information",
                    when_all={
                        _o(NBC, "counterparty_condition_information"): "missing"
                    },
                    state_updates={
                        _s(NBC, "exposure_review_posture"): "reviewing"
                    },
                ),
                branch(
                    NBC,
                    "seek_nbc_authority",
                    when_all={_o(NBC, "nbc_corporate_authority"): "pending"},
                    state_updates={
                        _s(NBC, "exposure_review_posture"): "reviewing"
                    },
                ),
                branch(
                    NBC,
                    "propose_credit_posture",
                    when_all={
                        _o(NBC, "credit_exposure_record"): "capacity_available",
                        _o(NBC, "nbc_corporate_authority"): "authorized",
                    },
                    state_updates={
                        _s(NBC, "exposure_review_posture"): "verified"
                    },
                ),
                branch(
                    NBC,
                    "limit_or_decline_additional_credit",
                    when_all={
                        _o(
                            NBC, "incremental_recovery_assessment"
                        ): "no_post_possession_lien"
                    },
                    state_updates={_s(NBC, "exposure_review_posture"): "bounded"},
                ),
                branch(
                    NBC,
                    "request_delivery_or_result_clarification",
                    when_all={
                        _o(
                            NBC, "delivered_credit_or_relationship_result"
                        ): "disputed"
                    },
                    state_updates={
                        _s(NBC, "communication_posture"): "result_clarification_due"
                    },
                ),
            ),
            lifecycle_names=(
                "credit_and_clearing_relationship",
                "information_and_examination",
                "governance_and_authority",
                "institutional_communication",
            ),
        ),
        decision(
            NBC,
            "DC-NBC-02",
            observation_domains=_only(
                NBC_OBSERVATIONS,
                (
                    "clearing_relationship_status",
                    "counterparty_condition_information",
                    "counterparty_request",
                    "nbc_corporate_authority",
                    "nych_request_disposition",
                    "message_and_notice_status",
                ),
            ),
            state_domains=NBC_STATE,
            branches=(
                branch(
                    NBC,
                    "seek_intermediation_clarification",
                    when_all={_o(NBC, "counterparty_request"): "incomplete"},
                    state_updates={
                        _s(NBC, "intermediation_posture"): "unclassified"
                    },
                ),
                branch(
                    NBC,
                    "forward_request_with_provenance",
                    when_all={
                        _o(NBC, "counterparty_request"): "complete",
                        _s(NBC, "intermediation_posture"): "forwarding",
                    },
                    state_updates={
                        _s(NBC, "communication_posture"): "forwarding_due"
                    },
                ),
                branch(
                    NBC,
                    "sponsor_or_represent_request",
                    when_all={
                        _o(NBC, "counterparty_request"): "complete",
                        _s(NBC, "intermediation_posture"): "sponsorship_ready",
                    },
                    state_updates={
                        _s(NBC, "communication_posture"): "sponsorship_due"
                    },
                ),
                branch(
                    NBC,
                    "decline_intermediation",
                    when_all={_o(NBC, "nbc_corporate_authority"): "denied"},
                    state_updates={
                        _s(NBC, "intermediation_posture"): "declined"
                    },
                ),
                branch(
                    NBC,
                    "request_nych_direction_clarification",
                    when_all={_o(NBC, "nych_request_disposition"): "unknown"},
                    state_updates={
                        _s(NBC, "communication_posture"): "direction_clarification_due"
                    },
                ),
            ),
            lifecycle_names=(
                "support_and_request_case",
                "institutional_communication",
                "governance_and_authority",
            ),
        ),
        decision(
            NBC,
            "DC-NBC-03",
            observation_domains=_only(
                NBC_OBSERVATIONS,
                (
                    "clearing_relationship_status",
                    "clearing_exposure_record",
                    "credit_exposure_record",
                    "participant_review_notice",
                    "counterparty_condition_information",
                    "nbc_corporate_authority",
                    "nych_clearing_direction",
                    "incremental_recovery_assessment",
                    "message_and_notice_status",
                    "delivered_credit_or_relationship_result",
                ),
            ),
            state_domains=NBC_STATE,
            branches=(
                branch(
                    NBC,
                    "confirm_clearing_continuation",
                    when_all={
                        _o(NBC, "participant_review_notice"): "due",
                        _s(NBC, "exposure_review_posture"): "verified",
                    },
                    state_updates={
                        _s(NBC, "communication_posture"): "continuation_due"
                    },
                ),
                branch(
                    NBC,
                    "propose_relationship_condition",
                    when_all={_o(NBC, "credit_exposure_record"): "bounded"},
                    state_updates={
                        _s(NBC, "communication_posture"): "relationship_condition_due"
                    },
                ),
                branch(
                    NBC,
                    "verify_nbc_exposure",
                    when_all={_o(NBC, "clearing_exposure_record"): "stale"},
                    state_updates={
                        _s(NBC, "exposure_review_posture"): "reviewing"
                    },
                ),
                branch(
                    NBC,
                    "request_counterparty_information",
                    when_all={
                        _o(NBC, "counterparty_condition_information"): "missing"
                    },
                    state_updates={
                        _s(NBC, "exposure_review_posture"): "reviewing"
                    },
                ),
                branch(
                    NBC,
                    "seek_nbc_authority",
                    when_all={_o(NBC, "nbc_corporate_authority"): "pending"},
                    state_updates={
                        _s(NBC, "exposure_review_posture"): "reviewing"
                    },
                ),
                branch(
                    NBC,
                    "request_nych_direction_clarification",
                    when_all={_o(NBC, "nych_clearing_direction"): "disputed"},
                    state_updates={
                        _s(NBC, "communication_posture"): "direction_clarification_due"
                    },
                ),
                branch(
                    NBC,
                    "issue_clearing_termination_notice",
                    when_all={
                        _o(NBC, "nych_clearing_direction"): "direction_delivered",
                        _o(NBC, "nbc_corporate_authority"): "authorized",
                    },
                    state_updates={
                        _s(NBC, "communication_posture"): "termination_notice_due"
                    },
                ),
            ),
            lifecycle_names=(
                "credit_and_clearing_relationship",
                "governance_and_authority",
                "information_and_examination",
                "institutional_communication",
            ),
        ),
        decision(
            NBC,
            "DC-NBC-04",
            observation_domains=NBC_OBSERVATIONS,
            state_domains=NBC_STATE,
            branches=(
                _nbc_follow_up("communicate_nbc_position", "position_due"),
                _nbc_follow_up(
                    "request_delivery_or_result_clarification",
                    "result_clarification_due",
                ),
                _nbc_follow_up("verify_nbc_exposure", "exposure_verification_due"),
                _nbc_follow_up("request_counterparty_information", "counterparty_information_due"),
                _nbc_follow_up("seek_nbc_authority", "authority_due"),
                _nbc_follow_up("propose_credit_posture", "credit_posture_due"),
                _nbc_follow_up("limit_or_decline_additional_credit", "credit_limit_due"),
                _nbc_follow_up(
                    "seek_intermediation_clarification",
                    "intermediation_clarification_due",
                ),
                _nbc_follow_up("forward_request_with_provenance", "forwarding_due"),
                _nbc_follow_up("sponsor_or_represent_request", "sponsorship_due"),
                _nbc_follow_up("decline_intermediation", "intermediation_decline_due"),
                _nbc_follow_up(
                    "request_nych_direction_clarification",
                    "direction_clarification_due",
                ),
                _nbc_follow_up("confirm_clearing_continuation", "continuation_due"),
                _nbc_follow_up("propose_relationship_condition", "relationship_condition_due"),
                _nbc_follow_up("issue_clearing_termination_notice", "termination_notice_due"),
            ),
            lifecycle_names=(
                "credit_and_clearing_relationship",
                "support_and_request_case",
                "institutional_communication",
                "governance_and_authority",
                "information_and_examination",
            ),
            revisit_observation_names=(
                "message_and_notice_status",
                "nych_request_disposition",
                "delivered_credit_or_relationship_result",
            ),
        ),
    ),
)


CORE_PARTICIPANT_POLICIES: tuple[RuleParticipantPolicy, ...] = (
    KNICKERBOCKER_TRUST_POLICY,
    NATIONAL_BANK_OF_COMMERCE_POLICY,
    NEW_YORK_CLEARING_HOUSE_POLICY,
)


__all__ = [
    "CORE_PARTICIPANT_POLICIES",
    "KNICKERBOCKER_TRUST_POLICY",
    "NATIONAL_BANK_OF_COMMERCE_POLICY",
    "NEW_YORK_CLEARING_HOUSE_POLICY",
]
