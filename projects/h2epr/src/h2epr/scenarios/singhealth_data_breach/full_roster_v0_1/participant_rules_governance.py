"""Security-governance and IHiS executive participant Rules."""

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


_SECTOR_LEAD = (
    "cyber_security_governance_director_and_healthcare_sector_lead"
)
_SECTOR_OBSERVATIONS = {
    "delivered_incident_account": (
        "none",
        "verification_needed",
        "category_assessment_needed",
        "briefing_needed",
        "reportable_concern",
    ),
    "cii_scope_indicator": (
        "none",
        "unclear",
        "potential_cii",
        "material_cii",
    ),
    "classification_verification_update": (
        "none",
        "disputed",
        "category_revision",
        "executive_review",
        "material_report_trigger",
        "corrected",
    ),
    "reporting_framework_context": (
        "unknown",
        "available",
        "report_required",
        "category_update_required",
        "briefing_condition",
        "leadership_notice_needed",
        "verification_needed",
    ),
    "executive_briefing_state": (
        "none",
        "scheduled",
        "completed",
        "cancelled",
    ),
    "ihis_executive_direction": (
        "none",
        "review",
        "report",
        "notify",
    ),
    "acting_capacity_context": (
        "unknown",
        "ihis_csg_sector_lead",
        "moh_ciso",
        "ambiguous",
    ),
    "report_lifecycle_notice": (
        *LIFECYCLE_NOTICE_DOMAIN,
        "correction_required",
    ),
}
_SECTOR_STATE = {
    "current_sector_assessment": (
        "unassessed",
        "unclear",
        "possible_deliberate_event",
        "potentially_reportable",
        "category_1_indicated",
    ),
    "open_classification_questions": OPEN_ITEM_DOMAIN,
    "last_classification_basis": (
        "none",
        "provisional",
        "revised",
        "material",
    ),
    "active_verification_intents": ACTIVE_REFERENCE_DOMAIN,
    "active_classification_intents": ACTIVE_REFERENCE_DOMAIN,
    "active_reporting_intents": ACTIVE_REFERENCE_DOMAIN,
}


def sector_lead_policy() -> RuleParticipantPolicy:
    """Build the CSG Director and Healthcare Sector Lead policy."""

    return policy(
        _SECTOR_LEAD,
        (
            decision(
                _SECTOR_LEAD,
                "DC-SL-1",
                observation_domains=_pick(
                    _SECTOR_OBSERVATIONS,
                    "delivered_incident_account",
                    "cii_scope_indicator",
                    "classification_verification_update",
                    "reporting_framework_context",
                    "executive_briefing_state",
                ),
                state_domains=_pick(
                    _SECTOR_STATE,
                    "current_sector_assessment",
                    "open_classification_questions",
                    "active_verification_intents",
                    "active_classification_intents",
                    "active_reporting_intents",
                ),
                branches=(
                    branch(
                        _SECTOR_LEAD,
                        "request_classification_verification",
                        when_observations={
                            "delivered_incident_account": "verification_needed"
                        },
                        state_updates={
                            "open_classification_questions": "pending",
                            "active_verification_intents": "pending",
                        },
                    ),
                    branch(
                        _SECTOR_LEAD,
                        "propose_incident_category",
                        when_observations={
                            "delivered_incident_account": (
                                "category_assessment_needed"
                            )
                        },
                        state_updates={
                            "current_sector_assessment": (
                                "possible_deliberate_event"
                            ),
                            "active_classification_intents": "pending",
                        },
                    ),
                    branch(
                        _SECTOR_LEAD,
                        "request_executive_briefing",
                        when_observations={
                            "delivered_incident_account": "briefing_needed"
                        },
                    ),
                    branch(
                        _SECTOR_LEAD,
                        "report_cii_incident_to_csa",
                        when_observations={
                            "delivered_incident_account": "reportable_concern"
                        },
                        state_updates={
                            "current_sector_assessment": "potentially_reportable",
                            "active_reporting_intents": "pending",
                        },
                    ),
                ),
                lifecycle_names=(
                    "information_product",
                    "investigation_or_verification_request",
                    "meeting_or_consultation",
                    "incident_assessment_and_category",
                    "report_and_notification",
                    "participant_intent",
                ),
            ),
            decision(
                _SECTOR_LEAD,
                "DC-SL-2",
                observation_domains=_pick(
                    _SECTOR_OBSERVATIONS,
                    "cii_scope_indicator",
                    "classification_verification_update",
                    "executive_briefing_state",
                    "ihis_executive_direction",
                ),
                state_domains=_pick(
                    _SECTOR_STATE,
                    "current_sector_assessment",
                    "open_classification_questions",
                    "last_classification_basis",
                    "active_classification_intents",
                ),
                branches=(
                    branch(
                        _SECTOR_LEAD,
                        "request_classification_verification",
                        when_observations={
                            "classification_verification_update": "disputed"
                        },
                        state_updates={
                            "open_classification_questions": "pending"
                        },
                        branch_name="resolve_disputed_revision",
                    ),
                    branch(
                        _SECTOR_LEAD,
                        "propose_incident_category",
                        when_observations={
                            "classification_verification_update": (
                                "category_revision"
                            )
                        },
                        state_updates={
                            "last_classification_basis": "revised",
                            "active_classification_intents": "pending",
                        },
                        branch_name="revise_category",
                    ),
                    branch(
                        _SECTOR_LEAD,
                        "request_executive_briefing",
                        when_observations={
                            "classification_verification_update": (
                                "executive_review"
                            )
                        },
                        branch_name="brief_revised_evidence",
                    ),
                    branch(
                        _SECTOR_LEAD,
                        "report_cii_incident_to_csa",
                        when_observations={
                            "classification_verification_update": (
                                "material_report_trigger"
                            )
                        },
                        state_updates={
                            "current_sector_assessment": "category_1_indicated"
                        },
                        branch_name="report_material_revision",
                    ),
                ),
                lifecycle_names=(
                    "information_product",
                    "investigation_or_verification_request",
                    "incident_assessment_and_category",
                    "meeting_or_consultation",
                    "report_and_notification",
                ),
            ),
            decision(
                _SECTOR_LEAD,
                "DC-SL-3",
                observation_domains=_pick(
                    _SECTOR_OBSERVATIONS,
                    "cii_scope_indicator",
                    "classification_verification_update",
                    "reporting_framework_context",
                    "executive_briefing_state",
                    "ihis_executive_direction",
                    "acting_capacity_context",
                    "report_lifecycle_notice",
                ),
                state_domains=_pick(
                    _SECTOR_STATE,
                    "current_sector_assessment",
                    "open_classification_questions",
                    "last_classification_basis",
                    "active_classification_intents",
                    "active_reporting_intents",
                ),
                branches=(
                    branch(
                        _SECTOR_LEAD,
                        "report_cii_incident_to_csa",
                        when_observations={
                            "reporting_framework_context": "report_required",
                            "acting_capacity_context": "ihis_csg_sector_lead",
                        },
                        state_updates={
                            "active_reporting_intents": "pending"
                        },
                    ),
                    branch(
                        _SECTOR_LEAD,
                        "propose_incident_category",
                        when_observations={
                            "reporting_framework_context": (
                                "category_update_required"
                            ),
                            "acting_capacity_context": "ihis_csg_sector_lead",
                        },
                        state_updates={
                            "active_classification_intents": "pending"
                        },
                    ),
                    branch(
                        _SECTOR_LEAD,
                        "request_executive_briefing",
                        when_observations={
                            "reporting_framework_context": "briefing_condition",
                            "acting_capacity_context": "ihis_csg_sector_lead",
                        },
                    ),
                    branch(
                        _SECTOR_LEAD,
                        "notify_authorized_healthcare_leadership",
                        when_observations={
                            "reporting_framework_context": (
                                "leadership_notice_needed"
                            ),
                            "acting_capacity_context": "ihis_csg_sector_lead",
                        },
                        state_updates={"active_reporting_intents": "pending"},
                    ),
                    branch(
                        _SECTOR_LEAD,
                        "request_classification_verification",
                        when_observations={
                            "reporting_framework_context": "verification_needed",
                            "acting_capacity_context": "ihis_csg_sector_lead",
                        },
                        state_updates={
                            "open_classification_questions": "pending"
                        },
                    ),
                ),
                lifecycle_names=(
                    "investigation_or_verification_request",
                    "meeting_or_consultation",
                    "incident_assessment_and_category",
                    "report_and_notification",
                    "participant_intent",
                ),
            ),
            decision(
                _SECTOR_LEAD,
                "DC-SL-4",
                observation_domains=_pick(
                    _SECTOR_OBSERVATIONS,
                    "reporting_framework_context",
                    "ihis_executive_direction",
                    "acting_capacity_context",
                    "report_lifecycle_notice",
                ),
                state_domains=_pick(
                    _SECTOR_STATE,
                    "open_classification_questions",
                    "last_classification_basis",
                    "active_reporting_intents",
                ),
                branches=(
                    branch(
                        _SECTOR_LEAD,
                        "request_report_status",
                        when_observations={
                            "report_lifecycle_notice": "expired",
                            "acting_capacity_context": "ihis_csg_sector_lead",
                        },
                        state_updates={"active_reporting_intents": "adverse"},
                    ),
                    branch(
                        _SECTOR_LEAD,
                        "report_cii_incident_to_csa",
                        when_observations={
                            "report_lifecycle_notice": "failed",
                            "acting_capacity_context": "ihis_csg_sector_lead",
                        },
                        state_updates={"active_reporting_intents": "adverse"},
                        branch_name="retry_failed_report",
                    ),
                    branch(
                        _SECTOR_LEAD,
                        "notify_authorized_healthcare_leadership",
                        when_observations={
                            "report_lifecycle_notice": "correction_required",
                            "acting_capacity_context": "ihis_csg_sector_lead",
                        },
                        state_updates={"active_reporting_intents": "adverse"},
                        branch_name="route_report_correction",
                    ),
                ),
                lifecycle_names=(
                    "report_and_notification",
                    "participant_intent",
                ),
            ),
        ),
    )


_IHIS_CEO = "ihis_chief_executive_officer"
_CEO_OBSERVATIONS = {
    "delivered_executive_incident_brief": (
        "none",
        "briefing_needed",
        "evidence_needed",
        "assignment_needed",
        "executive_update_needed",
        "material",
    ),
    "supporting_evidence_summary": (
        "none",
        "missing",
        "material",
        "contradictory",
        "corrected",
    ),
    "sector_lead_assessment": (
        "none",
        "pending",
        "reporting_ready",
        "adverse",
    ),
    "gcio_update": ("none", "clarification_needed", "material", "corrected"),
    "investigation_capacity_status": (
        "unknown",
        "available",
        "assignment_needed",
        "progress_due",
        "constrained",
    ),
    "acting_capacity_context": (
        "unknown",
        "ihis_ceo",
        "moh_cio",
        "ambiguous",
    ),
    "intent_lifecycle_notice": LIFECYCLE_NOTICE_DOMAIN,
}
_CEO_STATE = {
    "current_executive_assessment": (
        "unassessed",
        "unclear",
        "security_event_possible",
        "external_reporting_warranted",
    ),
    "open_evidence_questions": OPEN_ITEM_DOMAIN,
    "last_investigation_assignment": (
        "none",
        "proposed",
        "acknowledged",
        "adverse",
    ),
    "active_direction_intents": ACTIVE_REFERENCE_DOMAIN,
    "active_reporting_intents": ACTIVE_REFERENCE_DOMAIN,
}


def ihis_chief_executive_officer_policy() -> RuleParticipantPolicy:
    """Build the IHiS CEO participant policy."""

    return policy(
        _IHIS_CEO,
        (
            decision(
                _IHIS_CEO,
                "DC-ICEO-1",
                observation_domains=_pick(
                    _CEO_OBSERVATIONS,
                    "delivered_executive_incident_brief",
                    "supporting_evidence_summary",
                    "sector_lead_assessment",
                    "gcio_update",
                    "acting_capacity_context",
                    "intent_lifecycle_notice",
                ),
                state_domains=_pick(
                    _CEO_STATE,
                    "current_executive_assessment",
                    "open_evidence_questions",
                    "active_direction_intents",
                    "active_reporting_intents",
                ),
                branches=(
                    branch(
                        _IHIS_CEO,
                        "request_executive_incident_briefing",
                        when_observations={
                            "delivered_executive_incident_brief": (
                                "briefing_needed"
                            ),
                            "acting_capacity_context": "ihis_ceo",
                        },
                        state_updates={"active_direction_intents": "pending"},
                    ),
                    branch(
                        _IHIS_CEO,
                        "request_supporting_evidence",
                        when_observations={
                            "delivered_executive_incident_brief": "evidence_needed",
                            "acting_capacity_context": "ihis_ceo",
                        },
                        state_updates={
                            "open_evidence_questions": "pending",
                            "active_direction_intents": "pending",
                        },
                    ),
                    branch(
                        _IHIS_CEO,
                        "assign_investigation_lead",
                        when_observations={
                            "delivered_executive_incident_brief": (
                                "assignment_needed"
                            ),
                            "acting_capacity_context": "ihis_ceo",
                        },
                        state_updates={"active_direction_intents": "pending"},
                    ),
                    branch(
                        _IHIS_CEO,
                        "issue_ihis_executive_update",
                        when_observations={
                            "delivered_executive_incident_brief": (
                                "executive_update_needed"
                            ),
                            "acting_capacity_context": "ihis_ceo",
                        },
                        state_updates={
                            "current_executive_assessment": (
                                "security_event_possible"
                            ),
                            "active_reporting_intents": "pending",
                        },
                    ),
                ),
                lifecycle_names=(
                    "information_product",
                    "meeting_or_consultation",
                    "investigation_or_verification_request",
                    "investigation_assignment",
                    "report_and_notification",
                    "participant_intent",
                ),
            ),
            decision(
                _IHIS_CEO,
                "DC-ICEO-2",
                observation_domains=_pick(
                    _CEO_OBSERVATIONS,
                    "delivered_executive_incident_brief",
                    "supporting_evidence_summary",
                    "sector_lead_assessment",
                    "gcio_update",
                    "acting_capacity_context",
                    "intent_lifecycle_notice",
                ),
                state_domains=_pick(
                    _CEO_STATE,
                    "current_executive_assessment",
                    "open_evidence_questions",
                    "active_reporting_intents",
                ),
                branches=(
                    branch(
                        _IHIS_CEO,
                        "request_supporting_evidence",
                        when_observations={
                            "supporting_evidence_summary": "missing",
                            "acting_capacity_context": "ihis_ceo",
                        },
                        state_updates={"open_evidence_questions": "pending"},
                        branch_name="close_reporting_evidence_gap",
                    ),
                    branch(
                        _IHIS_CEO,
                        "direct_sector_lead_reporting",
                        when_observations={
                            "supporting_evidence_summary": "material",
                            "acting_capacity_context": "ihis_ceo",
                        },
                        state_updates={
                            "current_executive_assessment": (
                                "external_reporting_warranted"
                            ),
                            "active_reporting_intents": "pending",
                        },
                    ),
                    branch(
                        _IHIS_CEO,
                        "issue_ihis_executive_update",
                        when_observations={
                            "supporting_evidence_summary": "contradictory",
                            "acting_capacity_context": "ihis_ceo",
                        },
                        state_updates={"active_reporting_intents": "pending"},
                        branch_name="route_evidence_correction",
                    ),
                ),
                lifecycle_names=(
                    "information_product",
                    "investigation_or_verification_request",
                    "incident_assessment_and_category",
                    "report_and_notification",
                    "participant_intent",
                ),
            ),
            decision(
                _IHIS_CEO,
                "DC-ICEO-3",
                observation_domains=_pick(
                    _CEO_OBSERVATIONS,
                    "delivered_executive_incident_brief",
                    "supporting_evidence_summary",
                    "gcio_update",
                    "investigation_capacity_status",
                    "acting_capacity_context",
                    "intent_lifecycle_notice",
                ),
                state_domains=_pick(
                    _CEO_STATE,
                    "open_evidence_questions",
                    "last_investigation_assignment",
                    "active_direction_intents",
                ),
                branches=(
                    branch(
                        _IHIS_CEO,
                        "assign_investigation_lead",
                        when_observations={
                            "investigation_capacity_status": "assignment_needed",
                            "acting_capacity_context": "ihis_ceo",
                        },
                        state_updates={
                            "last_investigation_assignment": "proposed",
                            "active_direction_intents": "pending",
                        },
                        branch_name="assign_named_investigation",
                    ),
                    branch(
                        _IHIS_CEO,
                        "request_supporting_evidence",
                        when_observations={
                            "supporting_evidence_summary": "missing",
                            "acting_capacity_context": "ihis_ceo",
                        },
                        state_updates={"open_evidence_questions": "pending"},
                        branch_name="request_assignment_evidence",
                    ),
                    branch(
                        _IHIS_CEO,
                        "issue_ihis_executive_update",
                        when_observations={
                            "investigation_capacity_status": "progress_due",
                            "acting_capacity_context": "ihis_ceo",
                        },
                        state_updates={"active_direction_intents": "pending"},
                        branch_name="maintain_executive_oversight",
                    ),
                ),
                lifecycle_names=(
                    "investigation_assignment",
                    "investigation_or_verification_request",
                    "information_product",
                    "participant_intent",
                ),
            ),
        ),
    )


__all__ = ["ihis_chief_executive_officer_policy", "sector_lead_policy"]
