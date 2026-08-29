"""Deterministic participant Rule interface for Panic full-roster execution."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Sequence


class ParticipantPolicyError(ValueError):
    """A participant context or static Rule specification is invalid."""


@dataclass(frozen=True)
class IntentBranch:
    """One explicit, ordered intent branch and its required facts."""

    branch_id: str
    intent_id: str
    when_all: tuple[tuple[str, tuple[str, ...]], ...]
    private_state_updates: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class DecisionSpec:
    """Executable realization of one released Decision Commitment."""

    commitment_id: str
    observation_ids: tuple[str, ...]
    private_state_ids: tuple[str, ...]
    configuration_parameter_ids: tuple[str, ...]
    intent_ids: tuple[str, ...]
    lifecycle_ids: tuple[str, ...]
    no_intent_reason_codes: tuple[str, ...]
    revisit_trigger_ids: tuple[str, ...]
    fact_domains: Mapping[str, tuple[str, ...]]
    baseline_facts: Mapping[str, str]
    branches: tuple[IntentBranch, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "fact_domains",
            MappingProxyType(
                {key: tuple(values) for key, values in self.fact_domains.items()}
            ),
        )
        object.__setattr__(
            self,
            "baseline_facts",
            MappingProxyType(dict(self.baseline_facts)),
        )


@dataclass(frozen=True)
class ParticipantDecisionContext:
    """Frozen participant-visible input to one commitment evaluation."""

    actor_id: str
    capability_id: str
    commitment_id: str
    observations: Mapping[str, str]
    private_state: Mapping[str, str]
    configuration_parameters: Mapping[str, str]

    def __post_init__(self) -> None:
        object.__setattr__(self, "observations", MappingProxyType(dict(self.observations)))
        object.__setattr__(self, "private_state", MappingProxyType(dict(self.private_state)))
        object.__setattr__(
            self,
            "configuration_parameters",
            MappingProxyType(dict(self.configuration_parameters)),
        )


@dataclass(frozen=True)
class ParticipantDecision:
    """One deterministic decision; it does not mutate authoritative state."""

    actor_id: str
    capability_id: str
    commitment_id: str
    branch_id: str | None
    intent_id: str | None
    no_intent_reason_code: str | None
    revisit_trigger_ids: tuple[str, ...]
    consumed_observation_ids: tuple[str, ...]
    persistent_state_ids: tuple[str, ...]
    consumed_configuration_parameter_ids: tuple[str, ...]
    lifecycle_ids: tuple[str, ...]
    proposed_private_state_updates: Mapping[str, str]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "proposed_private_state_updates",
            MappingProxyType(dict(self.proposed_private_state_updates)),
        )


def _duplicates(values: Sequence[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        else:
            seen.add(value)
    return duplicates


def _matches(branch: IntentBranch, facts: Mapping[str, str]) -> bool:
    return all(facts.get(field_id) in allowed for field_id, allowed in branch.when_all)


class RuleParticipantPolicy:
    """Ordered, fail-closed Rule behavior for one released capability."""

    def __init__(
        self,
        *,
        implementation_id: str,
        implementation_version: str,
        capability_id: str,
        configuration_parameter_ids: Sequence[str] = (),
        decisions: Sequence[DecisionSpec],
    ) -> None:
        self.implementation_id = implementation_id
        self.implementation_version = implementation_version
        self.capability_id = capability_id
        self.configuration_parameter_ids = tuple(configuration_parameter_ids)
        decision_rows = tuple(decisions)
        self._decisions = MappingProxyType(
            {decision.commitment_id: decision for decision in decision_rows}
        )
        if (
            not self.implementation_id
            or not self.implementation_version
            or not self.capability_id
            or not decision_rows
        ):
            raise ParticipantPolicyError("participant_policy_identity_incomplete")
        if len(self._decisions) != len(decision_rows):
            raise ParticipantPolicyError(
                f"duplicate_commitment:{self.implementation_id}"
            )
        self._validate()

    @property
    def decisions(self) -> Mapping[str, DecisionSpec]:
        return self._decisions

    @property
    def commitment_ids(self) -> tuple[str, ...]:
        return tuple(self._decisions)

    @property
    def observation_ids(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    item
                    for decision in self._decisions.values()
                    for item in decision.observation_ids
                }
            )
        )

    @property
    def private_state_ids(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    item
                    for decision in self._decisions.values()
                    for item in decision.private_state_ids
                }
            )
        )

    @property
    def intent_ids(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    item
                    for decision in self._decisions.values()
                    for item in decision.intent_ids
                }
            )
        )

    @property
    def lifecycle_ids(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    item
                    for decision in self._decisions.values()
                    for item in decision.lifecycle_ids
                }
            )
        )

    def _validate(self) -> None:
        if _duplicates(self.configuration_parameter_ids):
            raise ParticipantPolicyError(
                f"duplicate_configuration_parameter:{self.implementation_id}"
            )
        for decision in self._decisions.values():
            if set(decision.configuration_parameter_ids) != set(
                self.configuration_parameter_ids
            ):
                raise ParticipantPolicyError(
                    f"configuration_parameter_coverage:{decision.commitment_id}"
                )
            fact_ids = (
                *decision.observation_ids,
                *decision.private_state_ids,
                *decision.configuration_parameter_ids,
            )
            if _duplicates(fact_ids):
                raise ParticipantPolicyError(
                    f"duplicate_fact:{decision.commitment_id}"
                )
            if set(decision.baseline_facts) != set(fact_ids):
                raise ParticipantPolicyError(
                    f"baseline_fact_coverage:{decision.commitment_id}"
                )
            if set(decision.fact_domains) != set(fact_ids) or any(
                not values or len(values) != len(set(values))
                for values in decision.fact_domains.values()
            ):
                raise ParticipantPolicyError(
                    f"fact_domain_coverage:{decision.commitment_id}"
                )
            if any(
                decision.baseline_facts[field_id]
                not in decision.fact_domains[field_id]
                for field_id in fact_ids
            ):
                raise ParticipantPolicyError(
                    f"baseline_fact_outside_domain:{decision.commitment_id}"
                )
            if (
                not decision.intent_ids
                or _duplicates(decision.intent_ids)
                or not decision.no_intent_reason_codes
                or not decision.revisit_trigger_ids
                or not set(decision.revisit_trigger_ids)
                <= set(decision.observation_ids)
            ):
                raise ParticipantPolicyError(
                    f"decision_boundary_incomplete:{decision.commitment_id}"
                )
            branch_ids = tuple(branch.branch_id for branch in decision.branches)
            if _duplicates(branch_ids):
                raise ParticipantPolicyError(
                    f"duplicate_branch:{decision.commitment_id}"
                )
            if {branch.intent_id for branch in decision.branches} != set(
                decision.intent_ids
            ):
                raise ParticipantPolicyError(
                    f"intent_branch_coverage:{decision.commitment_id}"
                )
            for branch in decision.branches:
                conditions = tuple(field_id for field_id, _ in branch.when_all)
                updates = tuple(field_id for field_id, _ in branch.private_state_updates)
                if (
                    not branch.when_all
                    or _duplicates(conditions)
                    or _duplicates(updates)
                    or not set(conditions) <= set(fact_ids)
                    or not set(updates) <= set(decision.private_state_ids)
                    or any(not values for _, values in branch.when_all)
                    or any(
                        len(values) != len(set(values))
                        for _, values in branch.when_all
                    )
                    or any(
                        not set(values) <= set(decision.fact_domains[field_id])
                        for field_id, values in branch.when_all
                    )
                    or any(
                        value not in decision.fact_domains[field_id]
                        for field_id, value in branch.private_state_updates
                    )
                ):
                    raise ParticipantPolicyError(
                        f"branch_invalid:{decision.commitment_id}:{branch.branch_id}"
                    )
                witness = dict(decision.baseline_facts)
                witness.update(
                    {field_id: values[0] for field_id, values in branch.when_all}
                )
                selected = next(
                    (
                        candidate
                        for candidate in decision.branches
                        if _matches(candidate, witness)
                    ),
                    None,
                )
                if selected is not branch:
                    raise ParticipantPolicyError(
                        f"branch_unreachable:{decision.commitment_id}:{branch.branch_id}"
                    )
            if any(_matches(branch, decision.baseline_facts) for branch in decision.branches):
                raise ParticipantPolicyError(
                    f"no_intent_unreachable:{decision.commitment_id}"
                )

    def witness_context(
        self,
        *,
        actor_id: str,
        commitment_id: str,
        branch_id: str | None,
        configuration_parameters: Mapping[str, str] | None = None,
    ) -> ParticipantDecisionContext:
        """Build a deterministic branch witness for conformance tests."""

        try:
            decision = self._decisions[commitment_id]
        except KeyError as exc:
            raise ParticipantPolicyError(
                f"unknown_commitment:{commitment_id}"
            ) from exc
        facts = dict(decision.baseline_facts)
        if branch_id is not None:
            try:
                branch = next(
                    item for item in decision.branches if item.branch_id == branch_id
                )
            except StopIteration as exc:
                raise ParticipantPolicyError(
                    f"unknown_branch:{commitment_id}:{branch_id}"
                ) from exc
            facts.update(
                {field_id: values[0] for field_id, values in branch.when_all}
            )
        configured = {
            key: facts[key] for key in decision.configuration_parameter_ids
        }
        configured.update(configuration_parameters or {})
        return ParticipantDecisionContext(
            actor_id=actor_id,
            capability_id=self.capability_id,
            commitment_id=commitment_id,
            observations=MappingProxyType(
                {key: facts[key] for key in decision.observation_ids}
            ),
            private_state=MappingProxyType(
                {key: facts[key] for key in decision.private_state_ids}
            ),
            configuration_parameters=MappingProxyType(configured),
        )

    def decide(self, context: ParticipantDecisionContext) -> ParticipantDecision:
        """Evaluate one commitment without reading undeclared fields."""

        if context.capability_id != self.capability_id:
            raise ParticipantPolicyError(
                f"capability_mismatch:{context.capability_id}"
            )
        try:
            decision = self._decisions[context.commitment_id]
        except KeyError as exc:
            raise ParticipantPolicyError(
                f"unknown_commitment:{context.commitment_id}"
            ) from exc
        if set(context.observations) != set(decision.observation_ids):
            raise ParticipantPolicyError(
                f"observation_scope_mismatch:{context.commitment_id}"
            )
        if set(context.private_state) != set(decision.private_state_ids):
            raise ParticipantPolicyError(
                f"private_state_scope_mismatch:{context.commitment_id}"
            )
        if set(context.configuration_parameters) != set(
            decision.configuration_parameter_ids
        ):
            raise ParticipantPolicyError(
                f"configuration_parameter_scope_mismatch:{context.commitment_id}"
            )
        facts = {
            **context.observations,
            **context.private_state,
            **context.configuration_parameters,
        }
        if any(
            facts[field_id] not in decision.fact_domains[field_id]
            for field_id in facts
        ):
            raise ParticipantPolicyError(
                f"fact_value_outside_domain:{context.commitment_id}"
            )
        branch = next(
            (item for item in decision.branches if _matches(item, facts)),
            None,
        )
        if branch is None:
            return ParticipantDecision(
                actor_id=context.actor_id,
                capability_id=context.capability_id,
                commitment_id=context.commitment_id,
                branch_id=None,
                intent_id=None,
                no_intent_reason_code=decision.no_intent_reason_codes[0],
                revisit_trigger_ids=decision.revisit_trigger_ids,
                consumed_observation_ids=decision.observation_ids,
                persistent_state_ids=decision.private_state_ids,
                consumed_configuration_parameter_ids=(
                    decision.configuration_parameter_ids
                ),
                lifecycle_ids=decision.lifecycle_ids,
                proposed_private_state_updates=MappingProxyType({}),
            )
        return ParticipantDecision(
            actor_id=context.actor_id,
            capability_id=context.capability_id,
            commitment_id=context.commitment_id,
            branch_id=branch.branch_id,
            intent_id=branch.intent_id,
            no_intent_reason_code=None,
            revisit_trigger_ids=(),
            consumed_observation_ids=decision.observation_ids,
            persistent_state_ids=decision.private_state_ids,
            consumed_configuration_parameter_ids=decision.configuration_parameter_ids,
            lifecycle_ids=decision.lifecycle_ids,
            proposed_private_state_updates=MappingProxyType(
                dict(branch.private_state_updates)
            ),
        )


__all__ = [
    "DecisionSpec",
    "IntentBranch",
    "ParticipantDecision",
    "ParticipantDecisionContext",
    "ParticipantPolicyError",
    "RuleParticipantPolicy",
]
