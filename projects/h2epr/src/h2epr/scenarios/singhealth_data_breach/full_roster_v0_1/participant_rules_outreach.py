"""SingHealth governance and patient-outreach planning participant Rules."""

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


_DEPUTY_GCEO = "singhealth_deputy_group_chief_executive_officer"
_DEPUTY_OBSERVATIONS = {
    "delivered_gcio_incident_update": (
        "none",
        "clarification_needed",
        "gceo_attention",
        "moh_route_needed",
        "material",
    ),
    "singhealth_gceo_direction": (
        "none",
        "report",
        "prepare",
        "revise",
    ),
    "investigation_scope_update": (
        "none",
        "clarification_needed",
        "audience_revision",
        "plan_revision",
        "material",
    ),
    "data_integrity_update": (
        "none",
        "missing",
        "ready",
        "contradictory",
        "corrected",
    ),
    "interagency_consultation_record": (
        "none",
        "pending",
        "advice",
        "objection",
        "agreement",
    ),
    "outreach_readiness_status": (
        "none",
        "scope_gap",
        "preparation_needed",
        "audience_needed",
        "plan_needed",
        "status_due",
        "ready",
        "impediment",
    ),
    "intent_lifecycle_notice": LIFECYCLE_NOTICE_DOMAIN,
}
_DEPUTY_STATE = {
    "current_supervisory_assessment": (
        "unassessed",
        "unclear",
        "senior_reporting_required",
        "outreach_preparation_required",
    ),
    "open_information_needs": OPEN_ITEM_DOMAIN,
    "last_scope_update": ("none", "provisional", "revised"),
    "active_reporting_intents": ACTIVE_REFERENCE_DOMAIN,
    "active_outreach_intents": ACTIVE_REFERENCE_DOMAIN,
}


def singhealth_deputy_gceo_policy() -> RuleParticipantPolicy:
    """Build the Deputy GCEO reporting and outreach-preparation policy."""

    return policy(
        _DEPUTY_GCEO,
        (
            decision(
                _DEPUTY_GCEO,
                "DC-DGCEO-1",
                observation_domains=_pick(
                    _DEPUTY_OBSERVATIONS,
                    "delivered_gcio_incident_update",
                    "singhealth_gceo_direction",
                    "interagency_consultation_record",
                    "intent_lifecycle_notice",
                ),
                state_domains=_pick(
                    _DEPUTY_STATE,
                    "current_supervisory_assessment",
                    "open_information_needs",
                    "active_reporting_intents",
                ),
                branches=(
                    branch(
                        _DEPUTY_GCEO,
                        "request_incident_clarification",
                        when_observations={
                            "delivered_gcio_incident_update": (
                                "clarification_needed"
                            )
                        },
                        state_updates={
                            "open_information_needs": "pending",
                            "active_reporting_intents": "pending",
                        },
                    ),
                    branch(
                        _DEPUTY_GCEO,
                        "notify_singhealth_gceo",
                        when_observations={
                            "delivered_gcio_incident_update": "gceo_attention"
                        },
                        state_updates={
                            "current_supervisory_assessment": (
                                "senior_reporting_required"
                            ),
                            "active_reporting_intents": "pending",
                        },
                    ),
                    branch(
                        _DEPUTY_GCEO,
                        "request_moh_reporting",
                        when_observations={
                            "delivered_gcio_incident_update": "moh_route_needed"
                        },
                        state_updates={"active_reporting_intents": "pending"},
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
                _DEPUTY_GCEO,
                "DC-DGCEO-2",
                observation_domains=_pick(
                    _DEPUTY_OBSERVATIONS,
                    "delivered_gcio_incident_update",
                    "singhealth_gceo_direction",
                    "investigation_scope_update",
                    "data_integrity_update",
                    "interagency_consultation_record",
                    "outreach_readiness_status",
                    "intent_lifecycle_notice",
                ),
                state_domains=_pick(
                    _DEPUTY_STATE,
                    "current_supervisory_assessment",
                    "open_information_needs",
                    "active_outreach_intents",
                ),
                branches=(
                    branch(
                        _DEPUTY_GCEO,
                        "request_incident_clarification",
                        when_observations={
                            "outreach_readiness_status": "scope_gap"
                        },
                        state_updates={"open_information_needs": "pending"},
                        branch_name="clarify_outreach_scope",
                    ),
                    branch(
                        _DEPUTY_GCEO,
                        "mobilize_outreach_preparation",
                        when_observations={
                            "outreach_readiness_status": "preparation_needed"
                        },
                        state_updates={
                            "current_supervisory_assessment": (
                                "outreach_preparation_required"
                            ),
                            "active_outreach_intents": "pending",
                        },
                    ),
                    branch(
                        _DEPUTY_GCEO,
                        "propose_notification_audience",
                        when_observations={
                            "outreach_readiness_status": "audience_needed"
                        },
                        state_updates={"active_outreach_intents": "pending"},
                    ),
                    branch(
                        _DEPUTY_GCEO,
                        "propose_notification_plan",
                        when_observations={
                            "outreach_readiness_status": "plan_needed"
                        },
                        state_updates={"active_outreach_intents": "pending"},
                    ),
                    branch(
                        _DEPUTY_GCEO,
                        "provide_outreach_status",
                        when_observations={
                            "outreach_readiness_status": "status_due"
                        },
                        state_updates={"active_outreach_intents": "pending"},
                    ),
                ),
                lifecycle_names=(
                    "information_product",
                    "investigation_or_verification_request",
                    "meeting_or_consultation",
                    "outreach_plan",
                    "report_and_notification",
                    "participant_intent",
                ),
            ),
            decision(
                _DEPUTY_GCEO,
                "DC-DGCEO-3",
                observation_domains=_pick(
                    _DEPUTY_OBSERVATIONS,
                    "singhealth_gceo_direction",
                    "investigation_scope_update",
                    "data_integrity_update",
                    "interagency_consultation_record",
                    "outreach_readiness_status",
                    "intent_lifecycle_notice",
                ),
                state_domains=_pick(
                    _DEPUTY_STATE,
                    "open_information_needs",
                    "last_scope_update",
                    "active_outreach_intents",
                ),
                branches=(
                    branch(
                        _DEPUTY_GCEO,
                        "request_incident_clarification",
                        when_observations={
                            "investigation_scope_update": "clarification_needed"
                        },
                        state_updates={"open_information_needs": "pending"},
                        branch_name="clarify_scope_revision",
                    ),
                    branch(
                        _DEPUTY_GCEO,
                        "propose_notification_audience",
                        when_observations={
                            "investigation_scope_update": "audience_revision"
                        },
                        state_updates={
                            "last_scope_update": "revised",
                            "active_outreach_intents": "pending",
                        },
                        branch_name="revise_audience",
                    ),
                    branch(
                        _DEPUTY_GCEO,
                        "propose_notification_plan",
                        when_observations={
                            "investigation_scope_update": "plan_revision"
                        },
                        state_updates={
                            "last_scope_update": "revised",
                            "active_outreach_intents": "pending",
                        },
                        branch_name="revise_plan",
                    ),
                    branch(
                        _DEPUTY_GCEO,
                        "provide_outreach_status",
                        when_observations={
                            "outreach_readiness_status": "impediment"
                        },
                        state_updates={"active_outreach_intents": "adverse"},
                        branch_name="report_outreach_impediment",
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


_GCEO = "singhealth_group_chief_executive_officer"
_GCEO_OBSERVATIONS = {
    "delivered_incident_update": (
        "none",
        "detail_needed",
        "reporting_required",
        "patient_relevance",
    ),
    "unauthorized_access_indicator": (
        "none",
        "possible",
        "material",
    ),
    "deputy_gceo_outreach_proposal": (
        "none",
        "detail_needed",
        "plan_needed",
        "consultation_needed",
        "audience_advice_needed",
        "channel_ready",
    ),
    "interagency_consultation_record": (
        "none",
        "pending",
        "objection",
        "agreement",
        "revision",
    ),
    "notification_readiness_summary": (
        "none",
        "plan_revision_needed",
        "consultation_needed",
        "audience_revision_needed",
        "channel_recommendation_ready",
        "impediment",
    ),
    "intent_lifecycle_notice": LIFECYCLE_NOTICE_DOMAIN,
}
_GCEO_STATE = {
    "current_gceo_assessment": (
        "unassessed",
        "unclear",
        "institutional_reporting_required",
        "patient_communication_required",
    ),
    "open_governance_questions": OPEN_ITEM_DOMAIN,
    "last_consultation_record": ("none", "pending", "received", "revised"),
    "active_reporting_directions": ACTIVE_REFERENCE_DOMAIN,
    "active_notification_directions": ACTIVE_REFERENCE_DOMAIN,
}


def singhealth_group_gceo_policy() -> RuleParticipantPolicy:
    """Build the GCEO reporting and communication-supervision policy."""

    return policy(
        _GCEO,
        (
            decision(
                _GCEO,
                "DC-GCEO-1",
                observation_domains=_pick(
                    _GCEO_OBSERVATIONS,
                    "delivered_incident_update",
                    "unauthorized_access_indicator",
                    "interagency_consultation_record",
                    "intent_lifecycle_notice",
                ),
                state_domains=_pick(
                    _GCEO_STATE,
                    "current_gceo_assessment",
                    "open_governance_questions",
                    "active_reporting_directions",
                ),
                branches=(
                    branch(
                        _GCEO,
                        "request_incident_detail",
                        when_observations={
                            "delivered_incident_update": "detail_needed"
                        },
                        state_updates={
                            "open_governance_questions": "pending",
                            "active_reporting_directions": "pending",
                        },
                    ),
                    branch(
                        _GCEO,
                        "direct_moh_reporting",
                        when_observations={
                            "delivered_incident_update": "reporting_required"
                        },
                        state_updates={
                            "current_gceo_assessment": (
                                "institutional_reporting_required"
                            ),
                            "active_reporting_directions": "pending",
                        },
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
                _GCEO,
                "DC-GCEO-2",
                observation_domains=_pick(
                    _GCEO_OBSERVATIONS,
                    "delivered_incident_update",
                    "unauthorized_access_indicator",
                    "deputy_gceo_outreach_proposal",
                    "interagency_consultation_record",
                    "notification_readiness_summary",
                    "intent_lifecycle_notice",
                ),
                state_domains=_pick(
                    _GCEO_STATE,
                    "current_gceo_assessment",
                    "open_governance_questions",
                    "active_notification_directions",
                ),
                branches=(
                    branch(
                        _GCEO,
                        "request_incident_detail",
                        when_observations={
                            "deputy_gceo_outreach_proposal": "detail_needed"
                        },
                        state_updates={"open_governance_questions": "pending"},
                        branch_name="clarify_outreach_basis",
                    ),
                    branch(
                        _GCEO,
                        "request_outreach_plan",
                        when_observations={
                            "deputy_gceo_outreach_proposal": "plan_needed"
                        },
                        state_updates={
                            "active_notification_directions": "pending"
                        },
                    ),
                    branch(
                        _GCEO,
                        "consult_on_outreach_plan",
                        when_observations={
                            "deputy_gceo_outreach_proposal": (
                                "consultation_needed"
                            )
                        },
                        state_updates={
                            "active_notification_directions": "pending"
                        },
                    ),
                    branch(
                        _GCEO,
                        "advise_notification_audience",
                        when_observations={
                            "deputy_gceo_outreach_proposal": (
                                "audience_advice_needed"
                            )
                        },
                        state_updates={
                            "current_gceo_assessment": (
                                "patient_communication_required"
                            ),
                            "active_notification_directions": "pending",
                        },
                    ),
                ),
                lifecycle_names=(
                    "information_product",
                    "investigation_or_verification_request",
                    "meeting_or_consultation",
                    "outreach_plan",
                    "report_and_notification",
                    "participant_intent",
                ),
            ),
            decision(
                _GCEO,
                "DC-GCEO-3",
                observation_domains=_pick(
                    _GCEO_OBSERVATIONS,
                    "deputy_gceo_outreach_proposal",
                    "interagency_consultation_record",
                    "notification_readiness_summary",
                    "intent_lifecycle_notice",
                ),
                state_domains=_pick(
                    _GCEO_STATE,
                    "current_gceo_assessment",
                    "open_governance_questions",
                    "last_consultation_record",
                    "active_notification_directions",
                ),
                branches=(
                    branch(
                        _GCEO,
                        "request_outreach_plan",
                        when_observations={
                            "notification_readiness_summary": (
                                "plan_revision_needed"
                            )
                        },
                        state_updates={
                            "active_notification_directions": "pending"
                        },
                        branch_name="request_channel_plan_revision",
                    ),
                    branch(
                        _GCEO,
                        "consult_on_outreach_plan",
                        when_observations={
                            "notification_readiness_summary": (
                                "consultation_needed"
                            )
                        },
                        state_updates={
                            "last_consultation_record": "pending",
                            "active_notification_directions": "pending",
                        },
                        branch_name="consult_channel_choice",
                    ),
                    branch(
                        _GCEO,
                        "advise_notification_audience",
                        when_observations={
                            "notification_readiness_summary": (
                                "audience_revision_needed"
                            )
                        },
                        state_updates={
                            "active_notification_directions": "pending"
                        },
                        branch_name="revise_channel_audience",
                    ),
                    branch(
                        _GCEO,
                        "recommend_primary_notification_channel",
                        when_observations={
                            "notification_readiness_summary": (
                                "channel_recommendation_ready"
                            )
                        },
                        state_updates={
                            "current_gceo_assessment": (
                                "patient_communication_required"
                            ),
                            "active_notification_directions": "pending",
                        },
                    ),
                ),
                lifecycle_names=(
                    "meeting_or_consultation",
                    "outreach_plan",
                    "report_and_notification",
                    "participant_intent",
                ),
            ),
        ),
    )


__all__ = ["singhealth_deputy_gceo_policy", "singhealth_group_gceo_policy"]
