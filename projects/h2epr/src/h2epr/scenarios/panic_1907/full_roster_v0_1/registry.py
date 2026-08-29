"""Static implementation objects available to the Panic policy loader."""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from .lifecycle_rules import LIFECYCLE_RULES, LifecycleRule
from .participant import RuleParticipantPolicy
from .participant_rules_core import CORE_PARTICIPANT_POLICIES
from .participant_rules_institutions import INSTITUTION_PARTICIPANT_POLICIES
from .participant_rules_populations import POPULATION_PARTICIPANT_POLICIES
from .scenario_rules import SCENARIO_POLICIES, ScenarioPolicy


_PARTICIPANT_POLICIES: Mapping[str, RuleParticipantPolicy] = MappingProxyType(
    {
        item.implementation_id: item
        for item in (
            *CORE_PARTICIPANT_POLICIES,
            *INSTITUTION_PARTICIPANT_POLICIES,
            *POPULATION_PARTICIPANT_POLICIES,
        )
    }
)

_SCENARIO_POLICIES: Mapping[str, ScenarioPolicy] = MappingProxyType(
    {item.implementation_id: item for item in SCENARIO_POLICIES}
)

_LIFECYCLE_RULES: Mapping[str, LifecycleRule] = MappingProxyType(
    {item.implementation_id: item for item in LIFECYCLE_RULES}
)

if (
    len(_SCENARIO_POLICIES) != len(SCENARIO_POLICIES)
    or len(_LIFECYCLE_RULES) != len(LIFECYCLE_RULES)
):
    raise ValueError("panic_implementation_registry_duplicate")


def participant_policies() -> Mapping[str, RuleParticipantPolicy]:
    """Return the immutable registry of implemented participant policies."""

    return _PARTICIPANT_POLICIES


def participant_policy(implementation_id: str) -> RuleParticipantPolicy:
    """Resolve one implementation identity without dynamic imports."""

    try:
        return _PARTICIPANT_POLICIES[implementation_id]
    except KeyError as exc:
        raise KeyError(f"unknown_participant_policy:{implementation_id}") from exc


def scenario_policies() -> Mapping[str, ScenarioPolicy]:
    """Return the immutable registry of selected Scenario policies."""

    return _SCENARIO_POLICIES


def scenario_policy(implementation_id: str) -> ScenarioPolicy:
    """Resolve one Scenario implementation without dynamic imports."""

    try:
        return _SCENARIO_POLICIES[implementation_id]
    except KeyError as exc:
        raise KeyError(f"unknown_scenario_policy:{implementation_id}") from exc


def lifecycle_rules() -> Mapping[str, LifecycleRule]:
    """Return the immutable registry of authoritative lifecycle rules."""

    return _LIFECYCLE_RULES


def lifecycle_rule(implementation_id: str) -> LifecycleRule:
    """Resolve one lifecycle implementation without dynamic imports."""

    try:
        return _LIFECYCLE_RULES[implementation_id]
    except KeyError as exc:
        raise KeyError(f"unknown_lifecycle_rule:{implementation_id}") from exc


def implementation_versions() -> Mapping[str, str]:
    """Return the closed registry without importing code from document fields."""

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
        raise ValueError("panic_implementation_registry_cross_kind_duplicate")
    return MappingProxyType(versions)


__all__ = [
    "implementation_versions",
    "lifecycle_rule",
    "lifecycle_rules",
    "participant_policies",
    "participant_policy",
    "scenario_policies",
    "scenario_policy",
]
