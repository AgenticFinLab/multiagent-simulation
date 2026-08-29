"""Static implementation objects available to the Panic policy loader."""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from .participant import RuleParticipantPolicy
from .participant_rules_core import CORE_PARTICIPANT_POLICIES


_PARTICIPANT_POLICIES: Mapping[str, RuleParticipantPolicy] = MappingProxyType(
    {item.implementation_id: item for item in CORE_PARTICIPANT_POLICIES}
)


def participant_policies() -> Mapping[str, RuleParticipantPolicy]:
    """Return the immutable registry of implemented participant policies."""

    return _PARTICIPANT_POLICIES


def participant_policy(implementation_id: str) -> RuleParticipantPolicy:
    """Resolve one implementation identity without dynamic imports."""

    try:
        return _PARTICIPANT_POLICIES[implementation_id]
    except KeyError as exc:
        raise KeyError(f"unknown_participant_policy:{implementation_id}") from exc


def implementation_versions() -> Mapping[str, str]:
    """Return the closed registry without importing code from document fields."""

    return MappingProxyType(
        {
            implementation_id: implementation.implementation_version
            for implementation_id, implementation in _PARTICIPANT_POLICIES.items()
        }
    )


__all__ = [
    "implementation_versions",
    "participant_policies",
    "participant_policy",
]
