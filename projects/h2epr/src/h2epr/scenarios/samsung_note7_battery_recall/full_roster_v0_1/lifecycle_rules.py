"""Authoritative reducer-owned state graphs for the twelve Note7 lifecycles."""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping, Sequence

from h2epr.execution import LifecycleRule, chain_states

from .participant_rules import LIFECYCLE_CAPABILITIES


def _rule(
    family: str,
    *,
    states: Sequence[str],
    initials: Sequence[str],
    terminals: Sequence[str],
    transitions: Sequence[tuple[str, str]],
) -> LifecycleRule:
    return LifecycleRule(
        lifecycle_id=f"lifecycle.0481.{family}",
        implementation_id=f"h2epr.lifecycle.0481.{family}",
        implementation_version="0.1.0",
        owner_layer="reducer",
        participant_capability_ids=LIFECYCLE_CAPABILITIES[family],
        state_ids=tuple(states),
        initial_state_ids=tuple(initials),
        terminal_state_ids=tuple(terminals),
        transitions=tuple(transitions),
    )


PARTICIPANT_INTENT = _rule(
    "participant_intent",
    states=("issued", "admitted", "rejected", "pending", "acknowledged", "partial", "completed", "failed", "expired", "cancelled", "superseded"),
    initials=("issued",),
    terminals=("rejected", "completed", "failed", "expired", "cancelled", "superseded"),
    transitions=(
        ("issued", "admitted"), ("issued", "rejected"), ("issued", "expired"),
        ("admitted", "pending"), ("admitted", "acknowledged"), ("admitted", "partial"),
        ("admitted", "completed"), ("admitted", "failed"), ("admitted", "expired"),
        ("admitted", "cancelled"), ("admitted", "superseded"),
        ("pending", "acknowledged"), ("pending", "partial"), ("pending", "completed"),
        ("pending", "failed"), ("pending", "expired"), ("pending", "cancelled"),
        ("pending", "superseded"), ("acknowledged", "partial"),
        ("acknowledged", "completed"), ("acknowledged", "failed"),
        ("acknowledged", "superseded"), ("partial", "completed"),
        ("partial", "failed"), ("partial", "expired"), ("partial", "superseded"),
    ),
)

INFORMATION_PRODUCT_AND_MESSAGE = _rule(
    "information_product_and_message",
    states=("produced", "routed", "delivered", "corrected", "superseded", "stale", "failed"),
    initials=("produced",),
    terminals=("delivered", "superseded", "stale", "failed"),
    transitions=(
        ("produced", "routed"), ("produced", "corrected"), ("produced", "superseded"),
        ("produced", "stale"), ("produced", "failed"), ("routed", "delivered"),
        ("routed", "corrected"), ("routed", "superseded"), ("routed", "stale"),
        ("routed", "failed"), ("corrected", "routed"), ("corrected", "superseded"),
    ),
)

INVESTIGATION_AND_INFORMATION_REQUEST = _rule(
    "investigation_and_information_request",
    states=("requested", "admitted", "assigned", "active", "partial", "completed", "failed", "declined", "expired"),
    initials=("requested",),
    terminals=("completed", "failed", "declined", "expired"),
    transitions=(
        *chain_states("requested", "admitted", "assigned", "active"),
        ("requested", "declined"), ("requested", "expired"),
        ("admitted", "declined"), ("admitted", "expired"),
        ("assigned", "declined"), ("assigned", "expired"),
        ("active", "partial"), ("active", "completed"), ("active", "failed"),
        ("active", "expired"), ("partial", "active"), ("partial", "completed"),
        ("partial", "failed"), ("partial", "expired"),
    ),
)

INCIDENT_REPORT_AND_INTAKE = _rule(
    "incident_report_and_intake",
    states=("alleged", "submitted", "delivered", "admitted", "aggregated", "corrected", "closed"),
    initials=("alleged",),
    terminals=("closed",),
    transitions=(
        *chain_states("alleged", "submitted", "delivered", "admitted", "aggregated", "closed"),
        ("submitted", "corrected"), ("delivered", "corrected"),
        ("admitted", "corrected"), ("aggregated", "corrected"),
        ("corrected", "submitted"), ("corrected", "closed"),
    ),
)

PRODUCT_FLOW_POSTURE = _rule(
    "product_flow_posture",
    states=("proposed", "admitted", "active", "partial", "completed", "failed", "reversed", "superseded"),
    initials=("proposed",),
    terminals=("completed", "failed", "reversed", "superseded"),
    transitions=(
        ("proposed", "admitted"), ("proposed", "failed"), ("proposed", "superseded"),
        ("admitted", "active"), ("admitted", "partial"), ("admitted", "failed"),
        ("admitted", "reversed"), ("admitted", "superseded"),
        ("active", "partial"), ("active", "completed"), ("active", "failed"),
        ("active", "reversed"), ("active", "superseded"),
        ("partial", "active"), ("partial", "completed"), ("partial", "failed"),
        ("partial", "reversed"), ("partial", "superseded"),
    ),
)

PRODUCTION_POSTURE = _rule(
    "production_posture",
    states=("proposed", "admitted", "active", "suspended", "halted", "resumed", "failed", "superseded"),
    initials=("proposed",),
    terminals=("halted", "failed", "superseded"),
    transitions=(
        ("proposed", "admitted"), ("proposed", "failed"), ("proposed", "superseded"),
        ("admitted", "active"), ("admitted", "suspended"), ("admitted", "halted"),
        ("admitted", "failed"), ("admitted", "superseded"),
        ("active", "suspended"), ("active", "halted"), ("active", "failed"),
        ("active", "superseded"), ("suspended", "resumed"),
        ("suspended", "halted"), ("suspended", "failed"), ("suspended", "superseded"),
        ("resumed", "active"), ("resumed", "halted"), ("resumed", "failed"),
    ),
)

INVENTORY_AND_PARTNER_ACTION = _rule(
    "inventory_and_partner_action",
    states=("requested", "acknowledged", "allocated", "moved", "unavailable", "refused", "completed"),
    initials=("requested",),
    terminals=("unavailable", "refused", "completed"),
    transitions=(
        ("requested", "acknowledged"), ("requested", "unavailable"),
        ("requested", "refused"), ("acknowledged", "allocated"),
        ("acknowledged", "unavailable"), ("acknowledged", "refused"),
        ("allocated", "moved"), ("allocated", "unavailable"),
        ("moved", "completed"), ("moved", "unavailable"),
    ),
)

REMEDY_OFFER_AND_FULFILLMENT = _rule(
    "remedy_offer_and_fulfillment",
    states=("proposed", "reviewed", "available", "selected", "accepted", "handed_off", "refunded", "exchanged", "failed"),
    initials=("proposed",),
    terminals=("refunded", "exchanged", "failed"),
    transitions=(
        ("proposed", "reviewed"), ("proposed", "failed"),
        ("reviewed", "available"), ("reviewed", "failed"),
        ("available", "selected"), ("available", "failed"),
        ("selected", "accepted"), ("selected", "failed"),
        ("accepted", "handed_off"), ("accepted", "refunded"),
        ("accepted", "exchanged"), ("accepted", "failed"),
        ("handed_off", "refunded"), ("handed_off", "exchanged"),
        ("handed_off", "failed"),
    ),
)

RECALL_AUTHORITY_ACTION = _rule(
    "recall_authority_action",
    states=("proposed", "issued", "effective", "expanded", "corrected", "superseded", "closed"),
    initials=("proposed",),
    terminals=("superseded", "closed"),
    transitions=(
        ("proposed", "issued"), ("issued", "effective"), ("issued", "corrected"),
        ("issued", "superseded"), ("effective", "expanded"),
        ("effective", "corrected"), ("effective", "superseded"),
        ("effective", "closed"), ("expanded", "corrected"),
        ("expanded", "superseded"), ("expanded", "closed"),
        ("corrected", "issued"), ("corrected", "effective"),
    ),
)

WARNING_OR_EMERGENCY_ORDER_ACTION = _rule(
    "warning_or_emergency_order_action",
    states=("proposed", "qualified", "issued", "published", "effective", "delivered", "superseded", "expired"),
    initials=("proposed",),
    terminals=("delivered", "superseded", "expired"),
    transitions=(
        ("proposed", "qualified"), ("proposed", "issued"), ("proposed", "expired"),
        ("qualified", "issued"), ("qualified", "superseded"), ("qualified", "expired"),
        ("issued", "published"), ("issued", "superseded"), ("issued", "expired"),
        ("published", "effective"), ("published", "delivered"),
        ("published", "superseded"), ("published", "expired"),
        ("effective", "delivered"), ("effective", "superseded"), ("effective", "expired"),
    ),
)

DEVICE_USE_AND_PURCHASE_POSTURE = _rule(
    "device_use_and_purchase_posture",
    states=("proposed", "admitted", "transferred", "used", "ceased", "retained", "failed", "superseded"),
    initials=("proposed",),
    terminals=("ceased", "retained", "failed", "superseded"),
    transitions=(
        ("proposed", "admitted"), ("proposed", "failed"), ("proposed", "superseded"),
        ("admitted", "transferred"), ("admitted", "used"), ("admitted", "ceased"),
        ("admitted", "retained"), ("admitted", "failed"), ("admitted", "superseded"),
        ("transferred", "used"), ("transferred", "ceased"), ("transferred", "retained"),
        ("used", "ceased"), ("used", "retained"), ("used", "failed"),
    ),
)

TRANSPORT_ENCOUNTER_AND_HANDLING = _rule(
    "transport_encounter_and_handling",
    states=("encountered", "identified", "admitted", "denied", "unloaded", "isolated", "returned", "escalated", "closed"),
    initials=("encountered",),
    terminals=("closed",),
    transitions=(
        ("encountered", "identified"), ("encountered", "escalated"),
        ("identified", "admitted"), ("identified", "denied"),
        ("identified", "unloaded"), ("identified", "isolated"),
        ("identified", "returned"), ("identified", "escalated"),
        ("admitted", "closed"), ("denied", "closed"), ("unloaded", "closed"),
        ("isolated", "returned"), ("isolated", "closed"),
        ("returned", "closed"), ("escalated", "identified"), ("escalated", "closed"),
    ),
)


LIFECYCLE_RULES = (
    PARTICIPANT_INTENT,
    INFORMATION_PRODUCT_AND_MESSAGE,
    INVESTIGATION_AND_INFORMATION_REQUEST,
    INCIDENT_REPORT_AND_INTAKE,
    PRODUCT_FLOW_POSTURE,
    PRODUCTION_POSTURE,
    INVENTORY_AND_PARTNER_ACTION,
    REMEDY_OFFER_AND_FULFILLMENT,
    RECALL_AUTHORITY_ACTION,
    WARNING_OR_EMERGENCY_ORDER_ACTION,
    DEVICE_USE_AND_PURCHASE_POSTURE,
    TRANSPORT_ENCOUNTER_AND_HANDLING,
)
LIFECYCLE_RULES_BY_ID: Mapping[str, LifecycleRule] = MappingProxyType(
    {item.lifecycle_id: item for item in LIFECYCLE_RULES}
)
if len(LIFECYCLE_RULES_BY_ID) != 12:
    raise ValueError("note7_lifecycle_registry_invalid")


__all__ = ["LIFECYCLE_RULES", "LIFECYCLE_RULES_BY_ID"]
