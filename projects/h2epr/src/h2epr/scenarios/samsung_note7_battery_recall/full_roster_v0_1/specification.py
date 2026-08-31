"""Readable constructors for Note7 participant Rule specifications."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from h2epr.execution import (
    DecisionSpec,
    IntentBranch,
    RuleParticipantPolicy,
)


EVENT_NAMESPACE = "0481"
IMPLEMENTATION_VERSION = "0.1.0"

ACTIVE_REFERENCE_DOMAIN = (
    "empty",
    "pending",
    "acknowledged",
    "adverse",
)
OPEN_ITEM_DOMAIN = ("empty", "open", "pending", "adverse")
LIFECYCLE_NOTICE_DOMAIN = (
    "none",
    "pending",
    "acknowledged",
    "completed",
    "partial",
    "failed",
    "expired",
    "cancelled",
    "superseded",
)


def observation_id(capability_id: str, name: str) -> str:
    return f"obs.{capability_id}.{name}"


def state_id(capability_id: str, name: str) -> str:
    return f"state.{capability_id}.{name}"


def intent_id(capability_id: str, name: str) -> str:
    return f"h2epr.action.{EVENT_NAMESPACE}.{capability_id}.{name}"


def commitment_id(capability_id: str, name: str) -> str:
    return f"h2epr.commitment.{EVENT_NAMESPACE}.{capability_id}.{name}"


def lifecycle_id(name: str) -> str:
    return f"lifecycle.{EVENT_NAMESPACE}.{name}"


def branch(
    capability_id: str,
    intent_name: str,
    *,
    when_observations: Mapping[str, str | Sequence[str]] | None = None,
    when_state: Mapping[str, str | Sequence[str]] | None = None,
    state_updates: Mapping[str, str] | None = None,
    branch_name: str | None = None,
) -> IntentBranch:
    """Declare an ordered branch using reader-facing fact names."""

    def values(value: str | Sequence[str]) -> tuple[str, ...]:
        return (value,) if isinstance(value, str) else tuple(value)

    conditions = tuple(
        (
            observation_id(capability_id, name),
            values(allowed),
        )
        for name, allowed in (when_observations or {}).items()
    ) + tuple(
        (
            state_id(capability_id, name),
            values(allowed),
        )
        for name, allowed in (when_state or {}).items()
    )
    return IntentBranch(
        branch_id=f"branch.{capability_id}.{branch_name or intent_name}",
        intent_id=intent_id(capability_id, intent_name),
        when_all=conditions,
        private_state_updates=tuple(
            (state_id(capability_id, name), value)
            for name, value in (state_updates or {}).items()
        ),
    )


def decision(
    capability_id: str,
    commitment_name: str,
    *,
    observation_domains: Mapping[str, Sequence[str]],
    state_domains: Mapping[str, Sequence[str]],
    branches: Sequence[IntentBranch],
    lifecycle_names: Sequence[str],
    no_intent_reason_codes: Sequence[str] = (
        "no_new_material_or_acknowledged_equivalent",
    ),
    revisit_observation_names: Sequence[str] | None = None,
) -> DecisionSpec:
    """Close one commitment over explicit observations, state, and branches."""

    observations = {
        observation_id(capability_id, name): tuple(values)
        for name, values in observation_domains.items()
    }
    private_state = {
        state_id(capability_id, name): tuple(values)
        for name, values in state_domains.items()
    }
    fact_domains = {**observations, **private_state}
    baseline = {field_id: values[0] for field_id, values in fact_domains.items()}
    revisit_names = tuple(revisit_observation_names or observation_domains)
    return DecisionSpec(
        commitment_id=commitment_id(capability_id, commitment_name),
        observation_ids=tuple(observations),
        private_state_ids=tuple(private_state),
        configuration_parameter_ids=(),
        intent_ids=tuple(dict.fromkeys(item.intent_id for item in branches)),
        lifecycle_ids=tuple(lifecycle_id(name) for name in lifecycle_names),
        no_intent_reason_codes=tuple(no_intent_reason_codes),
        revisit_trigger_ids=tuple(
            observation_id(capability_id, name) for name in revisit_names
        ),
        fact_domains=fact_domains,
        baseline_facts=baseline,
        branches=tuple(branches),
    )


def policy(
    capability_id: str,
    decisions: Sequence[DecisionSpec],
) -> RuleParticipantPolicy:
    """Build one statically identified participant policy."""

    return RuleParticipantPolicy(
        implementation_id=(
            f"h2epr.policy.{EVENT_NAMESPACE}.participant.{capability_id}"
        ),
        implementation_version=IMPLEMENTATION_VERSION,
        capability_id=capability_id,
        decisions=decisions,
    )


__all__ = [
    "ACTIVE_REFERENCE_DOMAIN",
    "EVENT_NAMESPACE",
    "IMPLEMENTATION_VERSION",
    "LIFECYCLE_NOTICE_DOMAIN",
    "OPEN_ITEM_DOMAIN",
    "branch",
    "commitment_id",
    "decision",
    "intent_id",
    "lifecycle_id",
    "observation_id",
    "policy",
    "state_id",
]
