"""Operational coordination and cross-institution information-routing Rules."""

from __future__ import annotations

from h2epr.execution import RuleParticipantPolicy

from .specification import (
    ACTIVE_REFERENCE_DOMAIN,
    LIFECYCLE_NOTICE_DOMAIN,
    OPEN_ITEM_DOMAIN,
    branch,
    decision,
    policy,
)


def _pick(
    domains: dict[str, tuple[str, ...]], *names: str
) -> dict[str, tuple[str, ...]]:
    return {name: domains[name] for name in names}


_OPERATIONS = "ihis_operational_and_scm_management"
_OPERATIONS_OBSERVATIONS = {
    "delivered_role_local_account": (
        "none",
        "missing_account",
        "verification_needed",
        "fragmented_material",
        "cross_system_material",
    ),
    "coordination_meeting_record": (
        "none",
        "review_needed",
        "action_gap",
        "completed",
        "corrected",
    ),
    "verification_result_notice": (
        *LIFECYCLE_NOTICE_DOMAIN,
        "disputed",
    ),
    "management_route_context": ("unknown", "available", "unavailable"),
    "intent_lifecycle_notice": LIFECYCLE_NOTICE_DOMAIN,
}
_OPERATIONS_STATE = {
    "current_cross_team_assessment": (
        "unassembled",
        "fragmented",
        "correlated",
        "senior_attention_needed",
    ),
    "open_verification_items": OPEN_ITEM_DOMAIN,
    "last_consolidated_account": ("none", "assembled", "issued"),
    "active_management_intents": ACTIVE_REFERENCE_DOMAIN,
}


def operational_and_scm_management_policy() -> RuleParticipantPolicy:
    """Build the operational responsibility-unit policy."""

    return policy(
        _OPERATIONS,
        (
            decision(
                _OPERATIONS,
                "SITUATION-A",
                observation_domains=_pick(
                    _OPERATIONS_OBSERVATIONS,
                    "delivered_role_local_account",
                    "verification_result_notice",
                    "management_route_context",
                ),
                state_domains=_pick(
                    _OPERATIONS_STATE,
                    "current_cross_team_assessment",
                    "open_verification_items",
                    "active_management_intents",
                ),
                branches=(
                    branch(
                        _OPERATIONS,
                        "request_operational_account",
                        when_observations={
                            "delivered_role_local_account": "missing_account"
                        },
                        state_updates={
                            "open_verification_items": "pending",
                            "active_management_intents": "pending",
                        },
                    ),
                    branch(
                        _OPERATIONS,
                        "request_fact_verification",
                        when_observations={
                            "delivered_role_local_account": "verification_needed"
                        },
                        state_updates={
                            "open_verification_items": "pending",
                            "active_management_intents": "pending",
                        },
                    ),
                    branch(
                        _OPERATIONS,
                        "convene_cross_functional_review",
                        when_observations={
                            "delivered_role_local_account": "fragmented_material"
                        },
                        state_updates={
                            "current_cross_team_assessment": "fragmented",
                            "active_management_intents": "pending",
                        },
                    ),
                ),
                lifecycle_names=(
                    "participant_intent",
                    "information_product",
                    "investigation_or_verification_request",
                    "meeting_or_consultation",
                ),
            ),
            decision(
                _OPERATIONS,
                "SITUATION-B",
                observation_domains=_pick(
                    _OPERATIONS_OBSERVATIONS,
                    "delivered_role_local_account",
                    "coordination_meeting_record",
                    "verification_result_notice",
                    "management_route_context",
                ),
                state_domains=_pick(
                    _OPERATIONS_STATE,
                    "current_cross_team_assessment",
                    "last_consolidated_account",
                    "active_management_intents",
                ),
                branches=(
                    branch(
                        _OPERATIONS,
                        "escalate_operational_concern",
                        when_observations={
                            "delivered_role_local_account": "cross_system_material"
                        },
                        state_updates={
                            "current_cross_team_assessment": (
                                "senior_attention_needed"
                            ),
                            "last_consolidated_account": "issued",
                            "active_management_intents": "pending",
                        },
                    ),
                    branch(
                        _OPERATIONS,
                        "convene_cross_functional_review",
                        when_observations={
                            "coordination_meeting_record": "review_needed"
                        },
                        state_updates={"active_management_intents": "pending"},
                        branch_name="convene_connection_review",
                    ),
                ),
                lifecycle_names=(
                    "information_product",
                    "meeting_or_consultation",
                    "investigation_or_verification_request",
                    "investigation_assignment",
                    "participant_intent",
                ),
            ),
            decision(
                _OPERATIONS,
                "SITUATION-C",
                observation_domains=_pick(
                    _OPERATIONS_OBSERVATIONS,
                    "coordination_meeting_record",
                    "verification_result_notice",
                    "management_route_context",
                    "intent_lifecycle_notice",
                ),
                state_domains=_pick(
                    _OPERATIONS_STATE,
                    "open_verification_items",
                    "last_consolidated_account",
                    "active_management_intents",
                ),
                branches=(
                    branch(
                        _OPERATIONS,
                        "request_operational_account",
                        when_observations={"intent_lifecycle_notice": "failed"},
                        state_updates={
                            "open_verification_items": "adverse",
                            "active_management_intents": "adverse",
                        },
                        branch_name="retry_failed_account_request",
                    ),
                    branch(
                        _OPERATIONS,
                        "convene_cross_functional_review",
                        when_observations={"intent_lifecycle_notice": "expired"},
                        state_updates={"active_management_intents": "adverse"},
                        branch_name="reopen_expired_coordination",
                    ),
                    branch(
                        _OPERATIONS,
                        "assign_operational_follow_up",
                        when_observations={"intent_lifecycle_notice": "partial"},
                        state_updates={"active_management_intents": "adverse"},
                        branch_name="close_partial_follow_up",
                    ),
                    branch(
                        _OPERATIONS,
                        "request_fact_verification",
                        when_observations={
                            "verification_result_notice": "disputed"
                        },
                        state_updates={"open_verification_items": "pending"},
                        branch_name="recheck_adverse_result",
                    ),
                    branch(
                        _OPERATIONS,
                        "escalate_operational_concern",
                        when_observations={
                            "management_route_context": "unavailable"
                        },
                        state_updates={
                            "active_management_intents": "adverse",
                            "last_consolidated_account": "issued",
                        },
                        branch_name="escalate_route_gap",
                    ),
                ),
                lifecycle_names=(
                    "participant_intent",
                    "information_product",
                    "investigation_or_verification_request",
                    "meeting_or_consultation",
                    "investigation_assignment",
                ),
            ),
        ),
    )


_GCIO = "singhealth_group_chief_information_officer"
_GCIO_OBSERVATIONS = {
    "delivered_operational_account": (
        "none",
        "clarification_needed",
        "management_review_needed",
        "senior_attention_required",
        "singhealth_relevance",
    ),
    "technical_verification_update": (
        "none",
        "incomplete",
        "material",
        "corrected",
        "contradictory",
    ),
    "ihis_executive_direction": (
        "none",
        "review_requested",
        "reporting_requested",
        "update_requested",
    ),
    "sector_lead_update": (
        "none",
        "classification_question",
        "reporting_update",
        "action_requested",
    ),
    "singhealth_management_response": (
        "none",
        "notification_needed",
        "advice_needed",
        "clarification_needed",
        "ihis_escalation_needed",
        "acknowledged",
    ),
    "patient_impact_update": (
        "none",
        "material_update",
        "missing_provenance",
        "management_attention",
        "corrected",
    ),
    "intent_lifecycle_notice": LIFECYCLE_NOTICE_DOMAIN,
}
_GCIO_STATE = {
    "current_gcio_assessment": (
        "unassessed",
        "unclear",
        "suspicious",
        "senior_attention_required",
    ),
    "open_information_requests": OPEN_ITEM_DOMAIN,
    "last_routed_account": ("none", "ihis", "singhealth", "both"),
    "active_review_intents": ACTIVE_REFERENCE_DOMAIN,
    "active_reporting_intents": ACTIVE_REFERENCE_DOMAIN,
}


def singhealth_group_chief_information_officer_policy() -> RuleParticipantPolicy:
    """Build the GCIO cross-institution routing policy."""

    return policy(
        _GCIO,
        (
            decision(
                _GCIO,
                "DC-GCIO-1",
                observation_domains=_pick(
                    _GCIO_OBSERVATIONS,
                    "delivered_operational_account",
                    "technical_verification_update",
                    "ihis_executive_direction",
                    "sector_lead_update",
                    "intent_lifecycle_notice",
                ),
                state_domains=_pick(
                    _GCIO_STATE,
                    "current_gcio_assessment",
                    "open_information_requests",
                    "active_review_intents",
                    "active_reporting_intents",
                ),
                branches=(
                    branch(
                        _GCIO,
                        "request_operational_clarification",
                        when_observations={
                            "delivered_operational_account": "clarification_needed"
                        },
                        state_updates={
                            "open_information_requests": "pending",
                            "active_review_intents": "pending",
                        },
                    ),
                    branch(
                        _GCIO,
                        "convene_management_review",
                        when_observations={
                            "delivered_operational_account": (
                                "management_review_needed"
                            )
                        },
                        state_updates={"active_review_intents": "pending"},
                    ),
                    branch(
                        _GCIO,
                        "escalate_to_ihis_leadership",
                        when_observations={
                            "delivered_operational_account": (
                                "senior_attention_required"
                            )
                        },
                        state_updates={
                            "current_gcio_assessment": "senior_attention_required",
                            "active_reporting_intents": "pending",
                        },
                    ),
                ),
                lifecycle_names=(
                    "information_product",
                    "investigation_or_verification_request",
                    "meeting_or_consultation",
                    "report_and_notification",
                    "participant_intent",
                ),
            ),
            decision(
                _GCIO,
                "DC-GCIO-2",
                observation_domains=_pick(
                    _GCIO_OBSERVATIONS,
                    "delivered_operational_account",
                    "technical_verification_update",
                    "ihis_executive_direction",
                    "sector_lead_update",
                    "singhealth_management_response",
                    "intent_lifecycle_notice",
                ),
                state_domains=_pick(
                    _GCIO_STATE,
                    "current_gcio_assessment",
                    "last_routed_account",
                    "active_review_intents",
                    "active_reporting_intents",
                ),
                branches=(
                    branch(
                        _GCIO,
                        "notify_singhealth_management",
                        when_observations={
                            "singhealth_management_response": "notification_needed"
                        },
                        state_updates={
                            "last_routed_account": "singhealth",
                            "active_reporting_intents": "pending",
                        },
                    ),
                    branch(
                        _GCIO,
                        "request_singhealth_reporting_advice",
                        when_observations={
                            "singhealth_management_response": "advice_needed"
                        },
                        state_updates={"active_reporting_intents": "pending"},
                    ),
                    branch(
                        _GCIO,
                        "request_operational_clarification",
                        when_observations={
                            "singhealth_management_response": "clarification_needed"
                        },
                        state_updates={"active_review_intents": "pending"},
                        branch_name="clarify_dual_account",
                    ),
                    branch(
                        _GCIO,
                        "escalate_to_ihis_leadership",
                        when_observations={
                            "singhealth_management_response": (
                                "ihis_escalation_needed"
                            )
                        },
                        state_updates={
                            "last_routed_account": "both",
                            "active_reporting_intents": "pending",
                        },
                        branch_name="maintain_ihis_route",
                    ),
                ),
                lifecycle_names=(
                    "information_product",
                    "investigation_or_verification_request",
                    "report_and_notification",
                    "participant_intent",
                ),
            ),
            decision(
                _GCIO,
                "DC-GCIO-3",
                observation_domains=_pick(
                    _GCIO_OBSERVATIONS,
                    "technical_verification_update",
                    "singhealth_management_response",
                    "patient_impact_update",
                    "intent_lifecycle_notice",
                ),
                state_domains=_pick(
                    _GCIO_STATE,
                    "current_gcio_assessment",
                    "open_information_requests",
                    "last_routed_account",
                    "active_reporting_intents",
                ),
                branches=(
                    branch(
                        _GCIO,
                        "provide_patient_impact_update",
                        when_observations={
                            "patient_impact_update": "material_update"
                        },
                        state_updates={
                            "last_routed_account": "singhealth",
                            "active_reporting_intents": "pending",
                        },
                    ),
                    branch(
                        _GCIO,
                        "request_operational_clarification",
                        when_observations={
                            "patient_impact_update": "missing_provenance"
                        },
                        state_updates={"open_information_requests": "pending"},
                        branch_name="clarify_impact_provenance",
                    ),
                    branch(
                        _GCIO,
                        "notify_singhealth_management",
                        when_observations={
                            "patient_impact_update": "management_attention"
                        },
                        state_updates={"active_reporting_intents": "pending"},
                        branch_name="route_impact_concern",
                    ),
                ),
                lifecycle_names=(
                    "information_product",
                    "investigation_or_verification_request",
                    "outreach_plan",
                    "report_and_notification",
                    "participant_intent",
                ),
            ),
        ),
    )


__all__ = [
    "operational_and_scm_management_policy",
    "singhealth_group_chief_information_officer_policy",
]
