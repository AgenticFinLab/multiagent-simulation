"""Detection, technical response, and security-accountability Rules."""

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


_TECHNICAL = "technical_administration_and_line_security_staff"
_TECHNICAL_OBSERVATIONS = {
    "local_technical_signal": (
        "none",
        "unclear",
        "peer_context_needed",
        "security_review_needed",
        "immediate_local_risk",
        "material_connection",
    ),
    "delivered_peer_finding": (
        "none",
        "unverified_connection",
        "verified_connection",
        "security_review_needed",
        "immediate_local_risk",
    ),
    "local_control_state": ("unknown", "available", "constrained", "adverse"),
    "security_response_request": (
        "none",
        "investigate",
        "coordinate",
        "control",
    ),
    "action_result_notice": (
        *LIFECYCLE_NOTICE_DOMAIN,
        "recurrent",
    ),
}
_TECHNICAL_STATE = {
    "local_assessment": (
        "unexamined",
        "routine_possible",
        "suspicious",
        "security_review_needed",
    ),
    "open_questions": OPEN_ITEM_DOMAIN,
    "last_shared_finding": ("none", "issued", "acknowledged"),
    "active_intent_references": ACTIVE_REFERENCE_DOMAIN,
}


def technical_administration_policy() -> RuleParticipantPolicy:
    """Build the responsibility-unit technical policy."""

    return policy(
        _TECHNICAL,
        (
            decision(
                _TECHNICAL,
                "SITUATION-A",
                observation_domains=_pick(
                    _TECHNICAL_OBSERVATIONS,
                    "local_technical_signal",
                    "local_control_state",
                    "security_response_request",
                ),
                state_domains=_pick(
                    _TECHNICAL_STATE,
                    "local_assessment",
                    "open_questions",
                    "last_shared_finding",
                    "active_intent_references",
                ),
                branches=(
                    branch(
                        _TECHNICAL,
                        "investigate_local_signal",
                        when_observations={"local_technical_signal": "unclear"},
                        state_updates={
                            "local_assessment": "routine_possible",
                            "active_intent_references": "pending",
                        },
                    ),
                    branch(
                        _TECHNICAL,
                        "request_peer_context",
                        when_observations={
                            "local_technical_signal": "peer_context_needed"
                        },
                        state_updates={
                            "open_questions": "open",
                            "active_intent_references": "pending",
                        },
                    ),
                    branch(
                        _TECHNICAL,
                        "share_technical_finding",
                        when_observations={
                            "local_technical_signal": "material_connection"
                        },
                        state_updates={
                            "last_shared_finding": "issued",
                            "active_intent_references": "pending",
                        },
                        branch_name="share_material_signal",
                    ),
                    branch(
                        _TECHNICAL,
                        "request_security_review",
                        when_observations={
                            "local_technical_signal": "security_review_needed"
                        },
                        state_updates={
                            "local_assessment": "security_review_needed",
                            "active_intent_references": "pending",
                        },
                    ),
                    branch(
                        _TECHNICAL,
                        "apply_local_control",
                        when_observations={
                            "local_technical_signal": "immediate_local_risk",
                            "local_control_state": "available",
                        },
                        state_updates={
                            "local_assessment": "suspicious",
                            "active_intent_references": "pending",
                        },
                    ),
                ),
                lifecycle_names=(
                    "participant_intent",
                    "investigation_or_verification_request",
                    "local_control_request",
                    "attack_and_technical_effect",
                ),
            ),
            decision(
                _TECHNICAL,
                "SITUATION-B",
                observation_domains=_pick(
                    _TECHNICAL_OBSERVATIONS,
                    "local_technical_signal",
                    "delivered_peer_finding",
                    "local_control_state",
                ),
                state_domains=_pick(
                    _TECHNICAL_STATE,
                    "local_assessment",
                    "last_shared_finding",
                    "active_intent_references",
                ),
                branches=(
                    branch(
                        _TECHNICAL,
                        "investigate_local_signal",
                        when_observations={
                            "delivered_peer_finding": "unverified_connection"
                        },
                        state_updates={
                            "local_assessment": "suspicious",
                            "active_intent_references": "pending",
                        },
                        branch_name="verify_connection",
                    ),
                    branch(
                        _TECHNICAL,
                        "share_technical_finding",
                        when_observations={
                            "delivered_peer_finding": "verified_connection"
                        },
                        state_updates={
                            "last_shared_finding": "issued",
                            "active_intent_references": "pending",
                        },
                    ),
                    branch(
                        _TECHNICAL,
                        "request_security_review",
                        when_observations={
                            "delivered_peer_finding": "security_review_needed"
                        },
                        state_updates={
                            "local_assessment": "security_review_needed",
                            "active_intent_references": "pending",
                        },
                        branch_name="review_connection",
                    ),
                    branch(
                        _TECHNICAL,
                        "apply_local_control",
                        when_observations={
                            "delivered_peer_finding": "immediate_local_risk",
                            "local_control_state": "available",
                        },
                        state_updates={"active_intent_references": "pending"},
                        branch_name="control_connection",
                    ),
                ),
                lifecycle_names=(
                    "information_product",
                    "investigation_or_verification_request",
                    "local_control_request",
                    "participant_intent",
                ),
            ),
            decision(
                _TECHNICAL,
                "SITUATION-C",
                observation_domains=_pick(
                    _TECHNICAL_OBSERVATIONS,
                    "delivered_peer_finding",
                    "local_control_state",
                    "security_response_request",
                    "action_result_notice",
                ),
                state_domains=_pick(
                    _TECHNICAL_STATE,
                    "open_questions",
                    "last_shared_finding",
                    "active_intent_references",
                ),
                branches=(
                    branch(
                        _TECHNICAL,
                        "investigate_local_signal",
                        when_observations={"action_result_notice": "partial"},
                        state_updates={
                            "open_questions": "open",
                            "active_intent_references": "adverse",
                        },
                        branch_name="inspect_partial_result",
                    ),
                    branch(
                        _TECHNICAL,
                        "apply_local_control",
                        when_observations={"action_result_notice": "failed"},
                        when_state={"active_intent_references": "adverse"},
                        state_updates={"active_intent_references": "adverse"},
                        branch_name="revise_failed_control",
                    ),
                    branch(
                        _TECHNICAL,
                        "request_security_review",
                        when_observations={"action_result_notice": "expired"},
                        state_updates={
                            "open_questions": "adverse",
                            "active_intent_references": "adverse",
                        },
                        branch_name="escalate_expired_work",
                    ),
                    branch(
                        _TECHNICAL,
                        "request_peer_context",
                        when_observations={"action_result_notice": "recurrent"},
                        state_updates={
                            "open_questions": "open",
                            "active_intent_references": "adverse",
                        },
                        branch_name="corroborate_recurrence",
                    ),
                ),
                lifecycle_names=(
                    "participant_intent",
                    "investigation_or_verification_request",
                    "local_control_request",
                    "attack_and_technical_effect",
                ),
            ),
        ),
    )


_SIRM = "security_incident_response_manager"
_SIRM_OBSERVATIONS = {
    "delivered_security_signal": (
        "none",
        "unclear",
        "multi_unit",
        "immediate_control_risk",
        "reporting_concern",
    ),
    "technical_investigation_update": (
        "none",
        "incomplete",
        "material",
        "cross_system",
        "corrected",
    ),
    "delivered_response_request": (
        "none",
        "coordination_requested",
        "activation_requested",
        "status_requested",
        "assistance_needed",
    ),
    "incident_scope_indicator": (
        "none",
        "unclear",
        "cross_system",
        "cii_possible",
        "reporting_trigger",
    ),
    "response_capacity_status": (
        "unknown",
        "available",
        "constrained",
        "coverage_gap",
    ),
    "control_result_notice": (
        "none",
        "pending",
        "effective",
        "partial",
        "failed",
        "recurrent",
    ),
    "reporting_framework_context": (
        "unknown",
        "available",
        "reporting_trigger",
        "disputed",
    ),
    "escalation_feedback": (
        "none",
        "pending",
        "acknowledged",
        "failed",
        "expired",
        "direction",
    ),
}
_SIRM_STATE = {
    "current_incident_assessment": (
        "unassessed",
        "routine_possible",
        "suspicious",
        "probable_incident",
        "reporting_trigger_met",
    ),
    "open_information_requests": OPEN_ITEM_DOMAIN,
    "active_coordination_intents": ACTIVE_REFERENCE_DOMAIN,
    "last_escalation_intent": (
        "none",
        "pending",
        "acknowledged",
        "adverse",
    ),
    "coverage_assessment": (
        "unknown",
        "covered",
        "constrained",
        "uncovered",
    ),
}


def security_incident_response_manager_policy() -> RuleParticipantPolicy:
    """Build the SIRM participant policy."""

    return policy(
        _SIRM,
        (
            decision(
                _SIRM,
                "DC-SIRM-1",
                observation_domains=_pick(
                    _SIRM_OBSERVATIONS,
                    "delivered_security_signal",
                    "technical_investigation_update",
                    "incident_scope_indicator",
                    "control_result_notice",
                ),
                state_domains=_pick(
                    _SIRM_STATE,
                    "current_incident_assessment",
                    "open_information_requests",
                ),
                branches=(
                    branch(
                        _SIRM,
                        "request_security_investigation",
                        when_observations={"delivered_security_signal": "unclear"},
                        state_updates={
                            "current_incident_assessment": "routine_possible",
                            "open_information_requests": "pending",
                        },
                    ),
                    branch(
                        _SIRM,
                        "coordinate_incident_response",
                        when_observations={
                            "delivered_security_signal": "multi_unit"
                        },
                        state_updates={
                            "current_incident_assessment": "suspicious"
                        },
                    ),
                    branch(
                        _SIRM,
                        "direct_local_containment",
                        when_observations={
                            "delivered_security_signal": "immediate_control_risk"
                        },
                        state_updates={
                            "current_incident_assessment": "probable_incident"
                        },
                    ),
                    branch(
                        _SIRM,
                        "escalate_suspected_incident",
                        when_observations={
                            "delivered_security_signal": "reporting_concern"
                        },
                        state_updates={
                            "current_incident_assessment": "reporting_trigger_met"
                        },
                    ),
                ),
                lifecycle_names=(
                    "information_product",
                    "investigation_or_verification_request",
                    "local_control_request",
                    "incident_assessment_and_category",
                    "attack_and_technical_effect",
                ),
            ),
            decision(
                _SIRM,
                "DC-SIRM-2",
                observation_domains=_pick(
                    _SIRM_OBSERVATIONS,
                    "technical_investigation_update",
                    "delivered_response_request",
                    "response_capacity_status",
                    "control_result_notice",
                    "escalation_feedback",
                ),
                state_domains=_pick(
                    _SIRM_STATE,
                    "current_incident_assessment",
                    "active_coordination_intents",
                ),
                branches=(
                    branch(
                        _SIRM,
                        "coordinate_incident_response",
                        when_observations={
                            "delivered_response_request": "coordination_requested"
                        },
                        state_updates={"active_coordination_intents": "pending"},
                    ),
                    branch(
                        _SIRM,
                        "activate_incident_response_team",
                        when_observations={
                            "delivered_response_request": "activation_requested"
                        },
                        state_updates={"active_coordination_intents": "pending"},
                    ),
                    branch(
                        _SIRM,
                        "provide_incident_response_status",
                        when_observations={
                            "delivered_response_request": "status_requested"
                        },
                    ),
                    branch(
                        _SIRM,
                        "direct_local_containment",
                        when_observations={"control_result_notice": "partial"},
                        state_updates={"active_coordination_intents": "adverse"},
                        branch_name="revise_partial_control",
                    ),
                    branch(
                        _SIRM,
                        "request_external_assistance",
                        when_observations={
                            "response_capacity_status": "constrained"
                        },
                        state_updates={"active_coordination_intents": "pending"},
                    ),
                    branch(
                        _SIRM,
                        "request_security_investigation",
                        when_observations={
                            "technical_investigation_update": "incomplete"
                        },
                        state_updates={"active_coordination_intents": "pending"},
                        branch_name="close_investigation_gap",
                    ),
                ),
                lifecycle_names=(
                    "participant_intent",
                    "investigation_or_verification_request",
                    "local_control_request",
                    "response_team_activation",
                    "meeting_or_consultation",
                ),
            ),
            decision(
                _SIRM,
                "DC-SIRM-3",
                observation_domains=_pick(
                    _SIRM_OBSERVATIONS,
                    "delivered_security_signal",
                    "technical_investigation_update",
                    "delivered_response_request",
                    "incident_scope_indicator",
                    "control_result_notice",
                    "reporting_framework_context",
                ),
                state_domains=_pick(
                    _SIRM_STATE,
                    "current_incident_assessment",
                    "open_information_requests",
                    "last_escalation_intent",
                ),
                branches=(
                    branch(
                        _SIRM,
                        "escalate_suspected_incident",
                        when_observations={
                            "reporting_framework_context": "reporting_trigger"
                        },
                        state_updates={
                            "current_incident_assessment": "reporting_trigger_met",
                            "last_escalation_intent": "pending",
                        },
                    ),
                    branch(
                        _SIRM,
                        "request_security_investigation",
                        when_observations={
                            "technical_investigation_update": "incomplete"
                        },
                        state_updates={"open_information_requests": "pending"},
                        branch_name="verify_before_escalation",
                    ),
                    branch(
                        _SIRM,
                        "request_external_assistance",
                        when_observations={
                            "delivered_response_request": "assistance_needed"
                        },
                    ),
                    branch(
                        _SIRM,
                        "coordinate_incident_response",
                        when_observations={
                            "incident_scope_indicator": "cross_system"
                        },
                        state_updates={
                            "current_incident_assessment": "probable_incident"
                        },
                        branch_name="coordinate_cross_system_scope",
                    ),
                ),
                lifecycle_names=(
                    "participant_intent",
                    "investigation_or_verification_request",
                    "incident_assessment_and_category",
                    "report_and_notification",
                ),
            ),
            decision(
                _SIRM,
                "DC-SIRM-4",
                observation_domains=_pick(
                    _SIRM_OBSERVATIONS,
                    "delivered_response_request",
                    "response_capacity_status",
                    "reporting_framework_context",
                ),
                state_domains=_pick(
                    _SIRM_STATE,
                    "active_coordination_intents",
                    "coverage_assessment",
                ),
                branches=(
                    branch(
                        _SIRM,
                        "delegate_sirm_coverage",
                        when_observations={
                            "response_capacity_status": "coverage_gap"
                        },
                        state_updates={
                            "coverage_assessment": "uncovered",
                            "active_coordination_intents": "pending",
                        },
                    ),
                    branch(
                        _SIRM,
                        "coordinate_incident_response",
                        when_state={"active_coordination_intents": "adverse"},
                        state_updates={"active_coordination_intents": "pending"},
                        branch_name="reassign_open_work",
                    ),
                    branch(
                        _SIRM,
                        "request_external_assistance",
                        when_observations={
                            "response_capacity_status": "constrained"
                        },
                        state_updates={"coverage_assessment": "constrained"},
                        branch_name="seek_coverage_resources",
                    ),
                ),
                lifecycle_names=(
                    "participant_intent",
                    "investigation_assignment",
                    "meeting_or_consultation",
                ),
            ),
        ),
    )


_CISO = "cluster_information_security_officer"
_CISO_OBSERVATIONS = {
    "delivered_incident_signal": (
        "none",
        "clarification_needed",
        "response_unknown",
        "coordination_gap",
        "reporting_concern",
    ),
    "sirm_response_update": (
        "none",
        "pending",
        "adequate",
        "partial",
        "failed",
    ),
    "cii_scope_indicator": (
        "none",
        "unclear",
        "potential_cii",
        "material_cii",
    ),
    "technical_finding_summary": (
        "none",
        "unclear",
        "material",
        "corrected",
    ),
    "response_team_status": (
        "none",
        "unknown",
        "active",
        "activation_needed",
        "coordination_gap",
        "reporting_inputs_needed",
        "material_gap",
    ),
    "reporting_framework_context": (
        "unknown",
        "available",
        "reporting_concern",
    ),
    "coordination_meeting_record": (
        "none",
        "presented",
        "action_gap",
        "corrected",
    ),
    "office_availability_status": (
        "unknown",
        "available",
        "constrained",
        "unavailable",
    ),
    "intent_lifecycle_notice": LIFECYCLE_NOTICE_DOMAIN,
}
_CISO_STATE = {
    "current_iso_assessment": (
        "unassessed",
        "unclear",
        "potential_incident",
        "reporting_concern",
    ),
    "open_clarifications": OPEN_ITEM_DOMAIN,
    "last_response_status": ("none", "pending", "adequate", "adverse"),
    "active_coordination_intents": ACTIVE_REFERENCE_DOMAIN,
    "active_reporting_intents": ACTIVE_REFERENCE_DOMAIN,
}


def cluster_information_security_officer_policy() -> RuleParticipantPolicy:
    """Build the Cluster ISO participant policy."""

    return policy(
        _CISO,
        (
            decision(
                _CISO,
                "DC-CISO-1",
                observation_domains=_pick(
                    _CISO_OBSERVATIONS,
                    "delivered_incident_signal",
                    "sirm_response_update",
                    "cii_scope_indicator",
                    "technical_finding_summary",
                    "coordination_meeting_record",
                    "intent_lifecycle_notice",
                ),
                state_domains=_pick(
                    _CISO_STATE,
                    "current_iso_assessment",
                    "open_clarifications",
                    "active_coordination_intents",
                    "active_reporting_intents",
                ),
                branches=(
                    branch(
                        _CISO,
                        "request_incident_clarification",
                        when_observations={
                            "delivered_incident_signal": "clarification_needed"
                        },
                        state_updates={"open_clarifications": "pending"},
                    ),
                    branch(
                        _CISO,
                        "request_response_status",
                        when_observations={
                            "delivered_incident_signal": "response_unknown"
                        },
                        state_updates={"active_coordination_intents": "pending"},
                    ),
                    branch(
                        _CISO,
                        "issue_security_coordination_direction",
                        when_observations={
                            "delivered_incident_signal": "coordination_gap"
                        },
                        state_updates={"active_coordination_intents": "pending"},
                    ),
                    branch(
                        _CISO,
                        "escalate_potential_cii_incident",
                        when_observations={
                            "delivered_incident_signal": "reporting_concern"
                        },
                        state_updates={
                            "current_iso_assessment": "reporting_concern",
                            "active_reporting_intents": "pending",
                        },
                    ),
                ),
                lifecycle_names=(
                    "participant_intent",
                    "information_product",
                    "investigation_or_verification_request",
                    "incident_assessment_and_category",
                ),
            ),
            decision(
                _CISO,
                "DC-CISO-2",
                observation_domains=_pick(
                    _CISO_OBSERVATIONS,
                    "sirm_response_update",
                    "technical_finding_summary",
                    "response_team_status",
                    "reporting_framework_context",
                    "coordination_meeting_record",
                    "office_availability_status",
                    "intent_lifecycle_notice",
                ),
                state_domains=_pick(
                    _CISO_STATE,
                    "current_iso_assessment",
                    "open_clarifications",
                    "last_response_status",
                    "active_coordination_intents",
                ),
                branches=(
                    branch(
                        _CISO,
                        "request_sirt_activation",
                        when_observations={
                            "response_team_status": "activation_needed"
                        },
                        state_updates={"active_coordination_intents": "pending"},
                    ),
                    branch(
                        _CISO,
                        "issue_security_coordination_direction",
                        when_observations={
                            "response_team_status": "coordination_gap"
                        },
                        state_updates={"active_coordination_intents": "pending"},
                        branch_name="close_coordination_gap",
                    ),
                    branch(
                        _CISO,
                        "coordinate_incident_reporting",
                        when_observations={
                            "response_team_status": "reporting_inputs_needed"
                        },
                        state_updates={"active_coordination_intents": "pending"},
                    ),
                    branch(
                        _CISO,
                        "request_response_status",
                        when_observations={"response_team_status": "unknown"},
                        state_updates={"active_coordination_intents": "pending"},
                        branch_name="resolve_unknown_response",
                    ),
                    branch(
                        _CISO,
                        "escalate_potential_cii_incident",
                        when_observations={
                            "response_team_status": "material_gap"
                        },
                        state_updates={
                            "current_iso_assessment": "potential_incident"
                        },
                        branch_name="escalate_response_gap",
                    ),
                ),
                lifecycle_names=(
                    "participant_intent",
                    "response_team_activation",
                    "meeting_or_consultation",
                    "report_and_notification",
                ),
            ),
            decision(
                _CISO,
                "DC-CISO-3",
                observation_domains=_pick(
                    _CISO_OBSERVATIONS,
                    "delivered_incident_signal",
                    "sirm_response_update",
                    "cii_scope_indicator",
                    "technical_finding_summary",
                    "reporting_framework_context",
                    "coordination_meeting_record",
                    "office_availability_status",
                    "intent_lifecycle_notice",
                ),
                state_domains=_pick(
                    _CISO_STATE,
                    "current_iso_assessment",
                    "open_clarifications",
                    "active_reporting_intents",
                ),
                branches=(
                    branch(
                        _CISO,
                        "escalate_potential_cii_incident",
                        when_observations={
                            "cii_scope_indicator": "material_cii"
                        },
                        state_updates={
                            "current_iso_assessment": "reporting_concern",
                            "active_reporting_intents": "pending",
                        },
                    ),
                    branch(
                        _CISO,
                        "coordinate_incident_reporting",
                        when_observations={
                            "reporting_framework_context": "reporting_concern"
                        },
                        state_updates={"active_reporting_intents": "pending"},
                    ),
                    branch(
                        _CISO,
                        "request_incident_clarification",
                        when_observations={"cii_scope_indicator": "unclear"},
                        state_updates={"open_clarifications": "pending"},
                        branch_name="clarify_cii_scope",
                    ),
                    branch(
                        _CISO,
                        "request_sirt_activation",
                        when_observations={
                            "office_availability_status": "constrained"
                        },
                        branch_name="request_explicit_response_action",
                    ),
                ),
                lifecycle_names=(
                    "participant_intent",
                    "investigation_or_verification_request",
                    "response_team_activation",
                    "incident_assessment_and_category",
                    "report_and_notification",
                ),
            ),
        ),
    )


__all__ = [
    "cluster_information_security_officer_policy",
    "security_incident_response_manager_policy",
    "technical_administration_policy",
]
