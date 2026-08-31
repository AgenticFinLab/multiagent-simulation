"""Deterministic participant Rule policies for all eight Note7 capabilities.

Each released Decision Commitment has an ordered, finite branch table. The
qualitative signal categories are declared implementation inputs rather than
historical labels or fitted probabilities. Baseline facts emit no intent.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from h2epr.execution import RuleParticipantPolicy

from .semantic_inventory import (
    CAPABILITY_INVENTORIES,
    DECISION_INTENT_INVENTORIES,
    TRIGGER_OBSERVATIONS,
)
from .specification import (
    ACTIVE_REFERENCE_DOMAIN,
    LIFECYCLE_NOTICE_DOMAIN,
    OPEN_ITEM_DOMAIN,
    branch,
    decision,
    policy,
)


_ASSESSMENT_DOMAIN = ("unknown", "open", "bounded", "reopened", "adverse")
_REFERENCE_DOMAIN = ("empty", "available", "pending", "adverse")
_OBSERVATION_DOMAIN = ("absent", "available", "changed", "adverse")


def _state_domain(name: str) -> tuple[str, ...]:
    if name.startswith("active_"):
        return ACTIVE_REFERENCE_DOMAIN
    if name.startswith("open_"):
        return OPEN_ITEM_DOMAIN
    if "assessment" in name:
        return _ASSESSMENT_DOMAIN
    if "reference" in name or name.startswith("observed_"):
        return _REFERENCE_DOMAIN
    raise ValueError(f"note7_private_state_domain_missing:{name}")


def _active_state(names: tuple[str, ...]) -> str | None:
    return next((name for name in names if name.startswith("active_")), None)


def lifecycle_names_for_intent(intent_name: str) -> tuple[str, ...]:
    names = ["participant_intent"]
    if intent_name == "submit_incident_report":
        names.append("incident_report_and_intake")
    elif intent_name in {
        "issue_product_flow_direction",
        "request_partner_stop",
        "set_local_product_posture",
    }:
        names.append("product_flow_posture")
    elif intent_name == "decide_production_posture":
        names.append("production_posture")
    elif intent_name == "request_inventory_action":
        names.append("inventory_and_partner_action")
    elif intent_name in {
        "announce_replacement_program",
        "propose_local_remedy",
        "respond_to_remedy_request",
        "request_exchange_or_refund",
    }:
        names.append("remedy_offer_and_fulfillment")
    elif intent_name in {"issue_recall_action", "expand_recall_action"}:
        names.append("recall_authority_action")
    elif intent_name in {
        "issue_transport_warning",
        "qualify_transport_warning",
        "qualify_emergency_order",
        "issue_emergency_order",
    }:
        names.append("warning_or_emergency_order_action")
    elif intent_name in {
        "choose_device_use_posture",
        "choose_purchase_posture",
    }:
        names.append("device_use_and_purchase_posture")
    elif intent_name in {
        "request_device_identification",
        "propose_carriage_denial_or_handling",
        "adopt_stricter_local_measure",
        "escalate_transport_ambiguity",
    }:
        names.append("transport_encounter_and_handling")
    elif intent_name.startswith("request_"):
        names.append("investigation_and_information_request")
    else:
        names.append("information_product_and_message")
    return tuple(names)


def _build_policy(capability_id: str) -> RuleParticipantPolicy:
    inventory = CAPABILITY_INVENTORIES[capability_id]
    decision_intents = DECISION_INTENT_INVENTORIES[capability_id]
    trigger_by_decision = TRIGGER_OBSERVATIONS[capability_id]
    state_domains = {
        name: _state_domain(name) for name in inventory.private_state_ids
    }
    active_state = _active_state(inventory.private_state_ids)
    decisions = []
    for commitment_name in inventory.released_decision_ids:
        intent_names = decision_intents[commitment_name]
        trigger = trigger_by_decision[commitment_name]
        candidates = tuple(f"candidate_{name}" for name in intent_names)
        observation_domains = {
            name: (
                tuple(dict.fromkeys((*LIFECYCLE_NOTICE_DOMAIN, *candidates)))
                if name == "intent_result_notice"
                else tuple(dict.fromkeys((*_OBSERVATION_DOMAIN, *candidates)))
                if name == trigger
                else LIFECYCLE_NOTICE_DOMAIN
                if name == "intent_result_notice"
                else _OBSERVATION_DOMAIN
            )
            for name in inventory.observation_ids
        }
        branches = []
        lifecycle_names: list[str] = []
        for intent_name in intent_names:
            for lifecycle_name in lifecycle_names_for_intent(intent_name):
                if lifecycle_name not in lifecycle_names:
                    lifecycle_names.append(lifecycle_name)
            branches.append(
                branch(
                    capability_id,
                    intent_name,
                    when_observations={trigger: f"candidate_{intent_name}"},
                    when_state=(
                        {
                            active_state: (
                                "empty",
                                "pending",
                                "acknowledged",
                                "adverse",
                            )
                        }
                        if active_state is not None
                        else None
                    ),
                    state_updates=(
                        {active_state: "pending"}
                        if active_state is not None
                        else None
                    ),
                    branch_name=f"{commitment_name}.{intent_name}",
                )
            )
        decisions.append(
            decision(
                capability_id,
                commitment_name,
                observation_domains=observation_domains,
                state_domains=state_domains,
                branches=branches,
                lifecycle_names=lifecycle_names,
                no_intent_reason_codes=(
                    "no_new_material_or_acknowledged_equivalent",
                    "required_information_or_authority_unavailable",
                ),
                revisit_observation_names=tuple(
                    dict.fromkeys((trigger, "intent_result_notice"))
                ),
            )
        )
    return policy(capability_id, decisions)


PARTICIPANT_POLICIES: Mapping[str, RuleParticipantPolicy] = MappingProxyType(
    {
        capability_id: _build_policy(capability_id)
        for capability_id in CAPABILITY_INVENTORIES
    }
)

LIFECYCLE_CAPABILITIES: Mapping[str, tuple[str, ...]] = MappingProxyType(
    {
        lifecycle_name: tuple(
            capability_id
            for capability_id, inventory in CAPABILITY_INVENTORIES.items()
            if any(
                lifecycle_name in lifecycle_names_for_intent(intent_name)
                for intent_name in inventory.intent_ids
            )
        )
        for lifecycle_name in {
            lifecycle_name
            for inventory in CAPABILITY_INVENTORIES.values()
            for intent_name in inventory.intent_ids
            for lifecycle_name in lifecycle_names_for_intent(intent_name)
        }
    }
)


def all_participant_policies() -> tuple[RuleParticipantPolicy, ...]:
    return tuple(PARTICIPANT_POLICIES.values())


__all__ = [
    "LIFECYCLE_CAPABILITIES",
    "PARTICIPANT_POLICIES",
    "all_participant_policies",
    "lifecycle_names_for_intent",
]
