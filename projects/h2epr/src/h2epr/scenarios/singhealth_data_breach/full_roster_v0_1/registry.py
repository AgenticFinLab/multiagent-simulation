"""Static SingHealth Policy Realization implementation registry."""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from h2epr.execution import LifecycleRule, RuleParticipantPolicy

from .lifecycle_rules import LIFECYCLE_RULES

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
from .scenario_rules import SCENARIO_POLICIES, ScenarioPolicy


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
_SCENARIO_POLICIES: Mapping[str, ScenarioPolicy] = MappingProxyType(
    {item.implementation_id: item for item in SCENARIO_POLICIES}
)
_LIFECYCLE_RULES: Mapping[str, LifecycleRule] = MappingProxyType(
    {item.implementation_id: item for item in LIFECYCLE_RULES}
)

if (
    len(_PARTICIPANT_POLICIES) != len(_POLICIES)
    or len(_PARTICIPANT_POLICIES_BY_CAPABILITY) != len(_POLICIES)
    or len(_SCENARIO_POLICIES) != len(SCENARIO_POLICIES)
    or len(_LIFECYCLE_RULES) != len(LIFECYCLE_RULES)
):
    raise ValueError("singhealth_implementation_registry_duplicate")

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

_CAPABILITIES_BY_LIFECYCLE: dict[str, set[str]] = {}
for capability_id, implementation in _PARTICIPANT_POLICIES_BY_CAPABILITY.items():
    for decision in implementation.decisions.values():
        for lifecycle_id in decision.lifecycle_ids:
            _CAPABILITIES_BY_LIFECYCLE.setdefault(lifecycle_id, set()).add(
                capability_id
            )
if set(_CAPABILITIES_BY_LIFECYCLE) != {
    rule.lifecycle_id for rule in LIFECYCLE_RULES
} or any(
    set(rule.participant_capability_ids)
    != _CAPABILITIES_BY_LIFECYCLE[rule.lifecycle_id]
    for rule in LIFECYCLE_RULES
):
    raise ValueError("singhealth_lifecycle_capability_coverage")


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


def scenario_policies() -> Mapping[str, ScenarioPolicy]:
    """Return all selected Scenario implementations by implementation ID."""

    return _SCENARIO_POLICIES


def scenario_policy(implementation_id: str) -> ScenarioPolicy:
    """Resolve one Scenario implementation without dynamic imports."""

    try:
        return _SCENARIO_POLICIES[implementation_id]
    except KeyError as exc:
        raise KeyError(f"unknown_scenario_policy:{implementation_id}") from exc


def lifecycle_rules() -> Mapping[str, LifecycleRule]:
    """Return all authoritative lifecycle implementations."""

    return _LIFECYCLE_RULES


def lifecycle_rule(implementation_id: str) -> LifecycleRule:
    """Resolve one lifecycle implementation without dynamic imports."""

    try:
        return _LIFECYCLE_RULES[implementation_id]
    except KeyError as exc:
        raise KeyError(f"unknown_lifecycle_rule:{implementation_id}") from exc


def implementation_versions() -> Mapping[str, str]:
    """Return the closed registry without importing from document fields."""

    implementations = (
        *_PARTICIPANT_POLICIES.values(),
        *_SCENARIO_POLICIES.values(),
        *_LIFECYCLE_RULES.values(),
    )
    versions = {
        implementation.implementation_id: implementation.implementation_version
        for implementation in implementations
    }
    if len(versions) != len(implementations):
        raise ValueError("singhealth_implementation_registry_cross_kind_duplicate")
    return MappingProxyType(versions)


__all__ = [
    "implementation_versions",
    "lifecycle_rule",
    "lifecycle_rules",
    "participant_policies",
    "participant_policies_by_capability",
    "participant_policy",
    "scenario_policies",
    "scenario_policy",
]
