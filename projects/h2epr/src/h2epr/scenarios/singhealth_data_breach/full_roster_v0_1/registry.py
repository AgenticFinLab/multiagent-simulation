"""Static SingHealth participant-policy implementation registry."""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from h2epr.execution import RuleParticipantPolicy

from .participant_rules_coordination import (
    operational_and_scm_management_policy,
    singhealth_group_chief_information_officer_policy,
)
from .participant_rules_detection import (
    cluster_information_security_officer_policy,
    security_incident_response_manager_policy,
    technical_administration_policy,
)
from .participant_rules_governance import (
    ihis_chief_executive_officer_policy,
    sector_lead_policy,
)
from .participant_rules_outreach import (
    singhealth_deputy_gceo_policy,
    singhealth_group_gceo_policy,
)
from .semantic_inventory import DECISION_INTENT_INVENTORIES


_POLICIES = (
    technical_administration_policy(),
    security_incident_response_manager_policy(),
    cluster_information_security_officer_policy(),
    operational_and_scm_management_policy(),
    singhealth_group_chief_information_officer_policy(),
    sector_lead_policy(),
    ihis_chief_executive_officer_policy(),
    singhealth_deputy_gceo_policy(),
    singhealth_group_gceo_policy(),
)

_PARTICIPANT_POLICIES: Mapping[str, RuleParticipantPolicy] = MappingProxyType(
    {item.implementation_id: item for item in _POLICIES}
)
_PARTICIPANT_POLICIES_BY_CAPABILITY: Mapping[str, RuleParticipantPolicy] = (
    MappingProxyType({item.capability_id: item for item in _POLICIES})
)

if (
    len(_PARTICIPANT_POLICIES) != len(_POLICIES)
    or len(_PARTICIPANT_POLICIES_BY_CAPABILITY) != len(_POLICIES)
):
    raise ValueError("singhealth_participant_policy_registry_duplicate")

if set(_PARTICIPANT_POLICIES_BY_CAPABILITY) != set(
    DECISION_INTENT_INVENTORIES
):
    raise ValueError("singhealth_decision_intent_capability_coverage")
for capability_id, implementation in _PARTICIPANT_POLICIES_BY_CAPABILITY.items():
    expected_by_name = DECISION_INTENT_INVENTORIES[capability_id]
    observed_by_name = {
        commitment_id.rsplit(".", 1)[-1]: {
            intent_id.rsplit(".", 1)[-1]
            for intent_id in decision.intent_ids
        }
        for commitment_id, decision in implementation.decisions.items()
    }
    if set(observed_by_name) != set(expected_by_name) or any(
        observed_by_name[name] != set(expected_by_name[name])
        for name in expected_by_name
    ):
        raise ValueError(
            f"singhealth_decision_intent_coverage:{capability_id}"
        )


def participant_policies() -> Mapping[str, RuleParticipantPolicy]:
    """Return all reviewed participant implementations by implementation ID."""

    return _PARTICIPANT_POLICIES


def participant_policies_by_capability() -> Mapping[str, RuleParticipantPolicy]:
    """Return all reviewed participant implementations by capability ID."""

    return _PARTICIPANT_POLICIES_BY_CAPABILITY


def participant_policy(implementation_id: str) -> RuleParticipantPolicy:
    """Resolve one participant implementation without dynamic imports."""

    try:
        return _PARTICIPANT_POLICIES[implementation_id]
    except KeyError as exc:
        raise KeyError(f"unknown_participant_policy:{implementation_id}") from exc


__all__ = [
    "participant_policies",
    "participant_policies_by_capability",
    "participant_policy",
]
