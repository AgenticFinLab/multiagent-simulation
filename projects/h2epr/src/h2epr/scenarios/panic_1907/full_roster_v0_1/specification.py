"""Readable constructors for Panic participant Rule specifications."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from .participant import DecisionSpec, IntentBranch, RuleParticipantPolicy


EVENT_NAMESPACE = "0288"
IMPLEMENTATION_VERSION = "0.1.0"


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
    when_all: Mapping[str, str | Sequence[str]],
    state_updates: Mapping[str, str] | None = None,
    branch_name: str | None = None,
) -> IntentBranch:
    """Declare one ordered branch using already namespaced fact identifiers."""

    conditions = tuple(
        (
            field_id,
            (values,) if isinstance(values, str) else tuple(values),
        )
        for field_id, values in when_all.items()
    )
    return IntentBranch(
        branch_id=f"branch.{capability_id}.{branch_name or intent_name}",
        intent_id=intent_id(capability_id, intent_name),
        when_all=conditions,
        private_state_updates=tuple((state_updates or {}).items()),
    )


def decision(
    capability_id: str,
    commitment_name: str,
    *,
    observation_domains: Mapping[str, Sequence[str]],
    state_domains: Mapping[str, Sequence[str]],
    configuration_parameter_domains: Mapping[str, Sequence[str]] | None = None,
    branches: Sequence[IntentBranch],
    lifecycle_names: Sequence[str],
    no_intent_reason_codes: Sequence[str] = ("no_declared_activation_condition",),
    revisit_observation_names: Sequence[str] | None = None,
) -> DecisionSpec:
    """Close one commitment over explicit observations, state, and branches."""

    observation_domains_by_id = {
        observation_id(capability_id, name): tuple(values)
        for name, values in observation_domains.items()
    }
    state_domains_by_id = {
        state_id(capability_id, name): tuple(values)
        for name, values in state_domains.items()
    }
    parameter_domains_by_id = {
        name: tuple(values)
        for name, values in (configuration_parameter_domains or {}).items()
    }
    fact_domains = {
        **observation_domains_by_id,
        **state_domains_by_id,
        **parameter_domains_by_id,
    }
    baseline = {field_id: values[0] for field_id, values in fact_domains.items()}
    revisit_names = tuple(revisit_observation_names or observation_domains)
    return DecisionSpec(
        commitment_id=commitment_id(capability_id, commitment_name),
        observation_ids=tuple(observation_domains_by_id),
        private_state_ids=tuple(state_domains_by_id),
        configuration_parameter_ids=tuple(parameter_domains_by_id),
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
    *,
    configuration_parameter_ids: Sequence[str] = (),
) -> RuleParticipantPolicy:
    """Build one statically identified participant policy."""

    return RuleParticipantPolicy(
        implementation_id=f"h2epr.policy.{EVENT_NAMESPACE}.participant.{capability_id}",
        implementation_version=IMPLEMENTATION_VERSION,
        capability_id=capability_id,
        configuration_parameter_ids=configuration_parameter_ids,
        decisions=decisions,
    )


__all__ = [
    "EVENT_NAMESPACE",
    "IMPLEMENTATION_VERSION",
    "branch",
    "commitment_id",
    "decision",
    "intent_id",
    "lifecycle_id",
    "observation_id",
    "policy",
    "state_id",
]
