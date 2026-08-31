"""Exact semantic inventory for the accepted H2EPR-0481 roster release.

The accepted mapping is a publication document, not a runtime data source.
This module records its closed capability-qualified surface for executable
authoring. Parent hashes remain authoritative and are verified by admission.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class CapabilityInventory:
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
        product_id,
        product_kind,
        decisions,
        observations,
        private_state,
        intents,
    )


CAPABILITY_INVENTORIES: Mapping[str, CapabilityInventory] = MappingProxyType(
    {
        "samsung_crisis_decision_interface": _capability(
            "h2epr.agent-definition.0481.samsung-note7-crisis-decision-interface",
            "agent_definition",
            ("DC-SAM-1", "DC-SAM-2", "DC-SAM-3"),
            (
                "delivered_incident_record",
                "investigation_update",
                "product_flow_snapshot",
                "authority_or_partner_record",
                "intent_result_notice",
            ),
            (
                "current_safety_assessment",
                "open_investigation_questions",
                "active_intent_references",
            ),
            (
                "request_safety_investigation",
                "issue_product_flow_direction",
                "announce_replacement_program",
                "request_partner_stop",
                "decide_production_posture",
                "publish_safety_message",
            ),
        ),
        "cpsc_recall_decision_interface": _capability(
            "h2epr.agent-definition.0481.cpsc-recall-decision-interface",
            "agent_definition",
            ("DC-CPSC-1", "DC-CPSC-2", "DC-CPSC-3"),
            (
                "delivered_firm_safety_report",
                "incident_summary",
                "remedy_proposal",
                "replacement_device_signal",
                "intent_result_notice",
            ),
            (
                "current_authority_assessment",
                "open_information_requests",
                "active_action_references",
            ),
            (
                "issue_consumer_warning",
                "request_incident_information",
                "request_remedy_information",
                "issue_recall_action",
                "expand_recall_action",
            ),
        ),
        "caac_warning_decision_interface": _capability(
            "h2epr.agent-definition.0481.caac-warning-decision-interface",
            "agent_definition",
            ("DC-CAAC-1", "DC-CAAC-2"),
            (
                "delivered_device_safety_record",
                "delivered_recall_record",
                "dangerous_goods_context",
                "operator_risk_record",
                "intent_result_notice",
            ),
            (
                "current_transport_assessment",
                "open_information_requests",
                "active_warning_references",
            ),
            (
                "request_transport_risk_information",
                "issue_transport_warning",
                "qualify_transport_warning",
            ),
        ),
        "us_dot_emergency_order_decision_interface": _capability(
            "h2epr.agent-definition.0481.us-dot-emergency-order-decision-interface",
            "agent_definition",
            ("DC-DOT-1", "DC-DOT-2"),
            (
                "delivered_safety_predicate",
                "delivered_recall_scope",
                "transport_feasibility_record",
                "authority_context",
                "intent_result_notice",
            ),
            (
                "current_hazard_assessment",
                "open_authority_questions",
                "active_order_references",
            ),
            (
                "request_hazard_information",
                "qualify_emergency_order",
                "issue_emergency_order",
            ),
        ),
        "samsung_regional_implementation_units": _capability(
            "h2epr.population-model.0481.samsung-regional-implementation-units",
            "population_model",
            ("situation_a", "situation_b", "situation_c"),
            (
                "delivered_central_direction",
                "local_authority_record",
                "partner_response",
                "local_inventory_observation",
                "intent_result_notice",
            ),
            (
                "local_resolution_assessment",
                "open_partner_questions",
                "active_offer_reference",
                "active_intent_references",
            ),
            (
                "request_regional_clarification",
                "coordinate_local_partner_response",
                "propose_local_remedy",
                "publish_local_safety_message",
            ),
        ),
        "carrier_and_retail_remedy_outlets": _capability(
            "h2epr.population-model.0481.carrier-and-retail-remedy-outlets",
            "population_model",
            ("situation_a", "situation_b", "situation_c"),
            (
                "delivered_product_direction",
                "delivered_authority_notice",
                "local_inventory_observation",
                "consumer_request",
                "intent_result_notice",
            ),
            (
                "local_action_assessment",
                "open_instruction_questions",
                "observed_inventory_reference",
                "active_intent_references",
            ),
            (
                "request_channel_clarification",
                "set_local_product_posture",
                "publish_outlet_notice",
                "request_inventory_action",
                "respond_to_remedy_request",
            ),
        ),
        "note7_owners_and_prospective_consumers": _capability(
            "h2epr.population-model.0481.note7-owners-and-prospective-consumers",
            "population_model",
            ("situation_a", "situation_b", "situation_c"),
            (
                "local_device_experience",
                "delivered_safety_message",
                "local_remedy_offer",
                "purchase_opportunity",
                "intent_result_notice",
            ),
            (
                "current_safety_assessment",
                "current_remedy_assessment",
                "associated_device_reference",
                "active_intent_references",
            ),
            (
                "choose_device_use_posture",
                "submit_incident_report",
                "request_safety_information",
                "choose_purchase_posture",
                "request_exchange_or_refund",
            ),
        ),
        "air_transport_operators": _capability(
            "h2epr.population-model.0481.air-transport-operators",
            "population_model",
            ("situation_a", "situation_b", "situation_c"),
            (
                "delivered_transport_record",
                "local_procedure_record",
                "device_encounter",
                "peer_or_authority_message",
                "intent_result_notice",
            ),
            (
                "current_rule_assessment",
                "open_scope_questions",
                "active_encounter_reference",
                "active_intent_references",
            ),
            (
                "request_transport_clarification",
                "publish_operator_notice",
                "request_device_identification",
                "propose_carriage_denial_or_handling",
                "adopt_stricter_local_measure",
                "escalate_transport_ambiguity",
            ),
        ),
    }
)


DECISION_INTENT_INVENTORIES: Mapping[str, Mapping[str, tuple[str, ...]]] = (
    MappingProxyType(
        {
            "samsung_crisis_decision_interface": MappingProxyType(
                {
                    "DC-SAM-1": (
                        "request_safety_investigation",
                        "publish_safety_message",
                    ),
                    "DC-SAM-2": (
                        "request_safety_investigation",
                        "issue_product_flow_direction",
                        "announce_replacement_program",
                        "publish_safety_message",
                    ),
                    "DC-SAM-3": (
                        "request_safety_investigation",
                        "issue_product_flow_direction",
                        "request_partner_stop",
                        "decide_production_posture",
                        "publish_safety_message",
                    ),
                }
            ),
            "cpsc_recall_decision_interface": MappingProxyType(
                {
                    "DC-CPSC-1": (
                        "issue_consumer_warning",
                        "request_incident_information",
                        "request_remedy_information",
                    ),
                    "DC-CPSC-2": (
                        "request_incident_information",
                        "request_remedy_information",
                        "issue_recall_action",
                    ),
                    "DC-CPSC-3": (
                        "request_incident_information",
                        "request_remedy_information",
                        "expand_recall_action",
                    ),
                }
            ),
            "caac_warning_decision_interface": MappingProxyType(
                {
                    "DC-CAAC-1": (
                        "request_transport_risk_information",
                        "issue_transport_warning",
                    ),
                    "DC-CAAC-2": (
                        "request_transport_risk_information",
                        "qualify_transport_warning",
                    ),
                }
            ),
            "us_dot_emergency_order_decision_interface": MappingProxyType(
                {
                    "DC-DOT-1": (
                        "request_hazard_information",
                        "qualify_emergency_order",
                    ),
                    "DC-DOT-2": (
                        "request_hazard_information",
                        "qualify_emergency_order",
                        "issue_emergency_order",
                    ),
                }
            ),
            "samsung_regional_implementation_units": MappingProxyType(
                {
                    "situation_a": (
                        "request_regional_clarification",
                        "coordinate_local_partner_response",
                        "publish_local_safety_message",
                    ),
                    "situation_b": (
                        "request_regional_clarification",
                        "propose_local_remedy",
                        "publish_local_safety_message",
                    ),
                    "situation_c": (
                        "request_regional_clarification",
                        "coordinate_local_partner_response",
                        "propose_local_remedy",
                        "publish_local_safety_message",
                    ),
                }
            ),
            "carrier_and_retail_remedy_outlets": MappingProxyType(
                {
                    "situation_a": (
                        "request_channel_clarification",
                        "set_local_product_posture",
                        "publish_outlet_notice",
                        "request_inventory_action",
                    ),
                    "situation_b": ("respond_to_remedy_request",),
                    "situation_c": (
                        "request_channel_clarification",
                        "set_local_product_posture",
                        "publish_outlet_notice",
                        "request_inventory_action",
                    ),
                }
            ),
            "note7_owners_and_prospective_consumers": MappingProxyType(
                {
                    "situation_a": (
                        "choose_device_use_posture",
                        "request_safety_information",
                        "choose_purchase_posture",
                    ),
                    "situation_b": (
                        "choose_device_use_posture",
                        "submit_incident_report",
                        "request_safety_information",
                        "request_exchange_or_refund",
                    ),
                    "situation_c": (
                        "choose_device_use_posture",
                        "request_safety_information",
                        "request_exchange_or_refund",
                    ),
                }
            ),
            "air_transport_operators": MappingProxyType(
                {
                    "situation_a": (
                        "request_transport_clarification",
                        "publish_operator_notice",
                        "adopt_stricter_local_measure",
                    ),
                    "situation_b": (
                        "request_device_identification",
                        "propose_carriage_denial_or_handling",
                        "escalate_transport_ambiguity",
                    ),
                    "situation_c": (
                        "request_transport_clarification",
                        "publish_operator_notice",
                        "adopt_stricter_local_measure",
                        "escalate_transport_ambiguity",
                    ),
                }
            ),
        }
    )
)


TRIGGER_OBSERVATIONS: Mapping[str, Mapping[str, str]] = MappingProxyType(
    {
        "samsung_crisis_decision_interface": MappingProxyType(
            {"DC-SAM-1": "delivered_incident_record", "DC-SAM-2": "investigation_update", "DC-SAM-3": "authority_or_partner_record"}
        ),
        "cpsc_recall_decision_interface": MappingProxyType(
            {"DC-CPSC-1": "delivered_firm_safety_report", "DC-CPSC-2": "remedy_proposal", "DC-CPSC-3": "replacement_device_signal"}
        ),
        "caac_warning_decision_interface": MappingProxyType(
            {"DC-CAAC-1": "delivered_device_safety_record", "DC-CAAC-2": "operator_risk_record"}
        ),
        "us_dot_emergency_order_decision_interface": MappingProxyType(
            {"DC-DOT-1": "delivered_safety_predicate", "DC-DOT-2": "authority_context"}
        ),
        "samsung_regional_implementation_units": MappingProxyType(
            {"situation_a": "delivered_central_direction", "situation_b": "local_inventory_observation", "situation_c": "intent_result_notice"}
        ),
        "carrier_and_retail_remedy_outlets": MappingProxyType(
            {"situation_a": "delivered_product_direction", "situation_b": "consumer_request", "situation_c": "intent_result_notice"}
        ),
        "note7_owners_and_prospective_consumers": MappingProxyType(
            {"situation_a": "purchase_opportunity", "situation_b": "delivered_safety_message", "situation_c": "local_remedy_offer"}
        ),
        "air_transport_operators": MappingProxyType(
            {"situation_a": "delivered_transport_record", "situation_b": "device_encounter", "situation_c": "intent_result_notice"}
        ),
    }
)


LIFECYCLE_FAMILIES = (
    "participant_intent",
    "information_product_and_message",
    "investigation_and_information_request",
    "incident_report_and_intake",
    "product_flow_posture",
    "production_posture",
    "inventory_and_partner_action",
    "remedy_offer_and_fulfillment",
    "recall_authority_action",
    "warning_or_emergency_order_action",
    "device_use_and_purchase_posture",
    "transport_encounter_and_handling",
)


__all__ = [
    "CAPABILITY_INVENTORIES",
    "DECISION_INTENT_INVENTORIES",
    "LIFECYCLE_FAMILIES",
    "TRIGGER_OBSERVATIONS",
    "CapabilityInventory",
]
