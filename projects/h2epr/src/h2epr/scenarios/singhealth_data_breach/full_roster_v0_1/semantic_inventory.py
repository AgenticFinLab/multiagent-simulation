"""Exact semantic inventory for the accepted SingHealth roster release.

The accepted mapping is a publication document rather than a runtime data
file.  This module records its closed capability surface for executable
authoring.  Parent hashes remain the authority; no Markdown is parsed at run
time.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class CapabilityInventory:
    """One released product's capability-qualified semantic placements."""

    product_id: str
    product_kind: str
    released_decision_ids: tuple[str, ...]
    observation_ids: tuple[str, ...]
    private_state_ids: tuple[str, ...]
    intent_ids: tuple[str, ...]


def _capability(
    product_id: str,
    product_kind: str,
    decisions: tuple[str, ...],
    observations: tuple[str, ...],
    private_state: tuple[str, ...],
    intents: tuple[str, ...],
) -> CapabilityInventory:
    return CapabilityInventory(
        product_id=product_id,
        product_kind=product_kind,
        released_decision_ids=decisions,
        observation_ids=observations,
        private_state_ids=private_state,
        intent_ids=intents,
    )


CAPABILITY_INVENTORIES: Mapping[str, CapabilityInventory] = MappingProxyType(
    {
        "technical_administration_and_line_security_staff": _capability(
            "h2epr.population-model.0616.technical-administration-and-line-security-staff",
            "population_model",
            ("SITUATION-A", "SITUATION-B", "SITUATION-C"),
            (
                "local_technical_signal",
                "delivered_peer_finding",
                "local_control_state",
                "security_response_request",
                "action_result_notice",
            ),
            (
                "local_assessment",
                "open_questions",
                "last_shared_finding",
                "active_intent_references",
            ),
            (
                "investigate_local_signal",
                "request_peer_context",
                "share_technical_finding",
                "request_security_review",
                "apply_local_control",
            ),
        ),
        "security_incident_response_manager": _capability(
            "h2epr.agent-definition.0616.security-incident-response-manager",
            "agent_definition",
            ("DC-SIRM-1", "DC-SIRM-2", "DC-SIRM-3", "DC-SIRM-4"),
            (
                "delivered_security_signal",
                "technical_investigation_update",
                "delivered_response_request",
                "incident_scope_indicator",
                "response_capacity_status",
                "control_result_notice",
                "reporting_framework_context",
                "escalation_feedback",
            ),
            (
                "current_incident_assessment",
                "open_information_requests",
                "active_coordination_intents",
                "last_escalation_intent",
                "coverage_assessment",
            ),
            (
                "request_security_investigation",
                "coordinate_incident_response",
                "activate_incident_response_team",
                "provide_incident_response_status",
                "direct_local_containment",
                "request_external_assistance",
                "escalate_suspected_incident",
                "delegate_sirm_coverage",
            ),
        ),
        "cluster_information_security_officer": _capability(
            "h2epr.agent-definition.0616.cluster-information-security-officer",
            "agent_definition",
            ("DC-CISO-1", "DC-CISO-2", "DC-CISO-3"),
            (
                "delivered_incident_signal",
                "sirm_response_update",
                "cii_scope_indicator",
                "technical_finding_summary",
                "response_team_status",
                "reporting_framework_context",
                "coordination_meeting_record",
                "office_availability_status",
                "intent_lifecycle_notice",
            ),
            (
                "current_iso_assessment",
                "open_clarifications",
                "last_response_status",
                "active_coordination_intents",
                "active_reporting_intents",
            ),
            (
                "request_incident_clarification",
                "request_response_status",
                "issue_security_coordination_direction",
                "request_sirt_activation",
                "coordinate_incident_reporting",
                "escalate_potential_cii_incident",
            ),
        ),
        "ihis_operational_and_scm_management": _capability(
            "h2epr.population-model.0616.ihis-operational-and-scm-management",
            "population_model",
            ("SITUATION-A", "SITUATION-B", "SITUATION-C"),
            (
                "delivered_role_local_account",
                "coordination_meeting_record",
                "verification_result_notice",
                "management_route_context",
                "intent_lifecycle_notice",
            ),
            (
                "current_cross_team_assessment",
                "open_verification_items",
                "last_consolidated_account",
                "active_management_intents",
            ),
            (
                "request_operational_account",
                "convene_cross_functional_review",
                "request_fact_verification",
                "assign_operational_follow_up",
                "escalate_operational_concern",
            ),
        ),
        "singhealth_group_chief_information_officer": _capability(
            "h2epr.agent-definition.0616.singhealth-group-chief-information-officer",
            "agent_definition",
            ("DC-GCIO-1", "DC-GCIO-2", "DC-GCIO-3"),
            (
                "delivered_operational_account",
                "technical_verification_update",
                "ihis_executive_direction",
                "sector_lead_update",
                "singhealth_management_response",
                "patient_impact_update",
                "intent_lifecycle_notice",
            ),
            (
                "current_gcio_assessment",
                "open_information_requests",
                "last_routed_account",
                "active_review_intents",
                "active_reporting_intents",
            ),
            (
                "request_operational_clarification",
                "convene_management_review",
                "escalate_to_ihis_leadership",
                "notify_singhealth_management",
                "request_singhealth_reporting_advice",
                "provide_patient_impact_update",
            ),
        ),
        "cyber_security_governance_director_and_healthcare_sector_lead": _capability(
            "h2epr.agent-definition.0616.cyber-security-governance-director-and-healthcare-sector-lead",
            "agent_definition",
            ("DC-SL-1", "DC-SL-2", "DC-SL-3", "DC-SL-4"),
            (
                "delivered_incident_account",
                "cii_scope_indicator",
                "classification_verification_update",
                "reporting_framework_context",
                "executive_briefing_state",
                "ihis_executive_direction",
                "acting_capacity_context",
                "report_lifecycle_notice",
            ),
            (
                "current_sector_assessment",
                "open_classification_questions",
                "last_classification_basis",
                "active_verification_intents",
                "active_classification_intents",
                "active_reporting_intents",
            ),
            (
                "request_classification_verification",
                "propose_incident_category",
                "request_executive_briefing",
                "report_cii_incident_to_csa",
                "notify_authorized_healthcare_leadership",
                "request_report_status",
            ),
        ),
        "ihis_chief_executive_officer": _capability(
            "h2epr.agent-definition.0616.ihis-chief-executive-officer",
            "agent_definition",
            ("DC-ICEO-1", "DC-ICEO-2", "DC-ICEO-3"),
            (
                "delivered_executive_incident_brief",
                "supporting_evidence_summary",
                "sector_lead_assessment",
                "gcio_update",
                "investigation_capacity_status",
                "acting_capacity_context",
                "intent_lifecycle_notice",
            ),
            (
                "current_executive_assessment",
                "open_evidence_questions",
                "last_investigation_assignment",
                "active_direction_intents",
                "active_reporting_intents",
            ),
            (
                "request_executive_incident_briefing",
                "request_supporting_evidence",
                "direct_sector_lead_reporting",
                "assign_investigation_lead",
                "issue_ihis_executive_update",
            ),
        ),
        "singhealth_deputy_group_chief_executive_officer": _capability(
            "h2epr.agent-definition.0616.singhealth-deputy-group-chief-executive-officer",
            "agent_definition",
            ("DC-DGCEO-1", "DC-DGCEO-2", "DC-DGCEO-3"),
            (
                "delivered_gcio_incident_update",
                "singhealth_gceo_direction",
                "investigation_scope_update",
                "data_integrity_update",
                "interagency_consultation_record",
                "outreach_readiness_status",
                "intent_lifecycle_notice",
            ),
            (
                "current_supervisory_assessment",
                "open_information_needs",
                "last_scope_update",
                "active_reporting_intents",
                "active_outreach_intents",
            ),
            (
                "request_incident_clarification",
                "notify_singhealth_gceo",
                "request_moh_reporting",
                "mobilize_outreach_preparation",
                "propose_notification_audience",
                "propose_notification_plan",
                "provide_outreach_status",
            ),
        ),
        "singhealth_group_chief_executive_officer": _capability(
            "h2epr.agent-definition.0616.singhealth-group-chief-executive-officer",
            "agent_definition",
            ("DC-GCEO-1", "DC-GCEO-2", "DC-GCEO-3"),
            (
                "delivered_incident_update",
                "unauthorized_access_indicator",
                "deputy_gceo_outreach_proposal",
                "interagency_consultation_record",
                "notification_readiness_summary",
                "intent_lifecycle_notice",
            ),
            (
                "current_gceo_assessment",
                "open_governance_questions",
                "last_consultation_record",
                "active_reporting_directions",
                "active_notification_directions",
            ),
            (
                "request_incident_detail",
                "direct_moh_reporting",
                "request_outreach_plan",
                "consult_on_outreach_plan",
                "advise_notification_audience",
                "recommend_primary_notification_channel",
            ),
        ),
    }
)


LIFECYCLE_FAMILIES = (
    "participant_intent",
    "information_product",
    "investigation_or_verification_request",
    "local_control_request",
    "meeting_or_consultation",
    "response_team_activation",
    "incident_assessment_and_category",
    "report_and_notification",
    "investigation_assignment",
    "outreach_plan",
    "attack_and_technical_effect",
)


__all__ = [
    "CAPABILITY_INVENTORIES",
    "LIFECYCLE_FAMILIES",
    "CapabilityInventory",
]
