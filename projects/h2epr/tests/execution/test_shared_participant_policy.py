from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from h2epr.execution import participant as shared
from h2epr.scenarios.panic_1907.full_roster_v0_1 import participant as panic


def _policy(module: Any) -> Any:
    observation = "obs.example.signal"
    state = "state.example.posture"
    parameter = "configuration.example.mode"
    inspect_intent = "h2epr.action.example.inspect"
    escalate_intent = "h2epr.action.example.escalate"
    decision = module.DecisionSpec(
        commitment_id="h2epr.commitment.example.review",
        observation_ids=(observation,),
        private_state_ids=(state,),
        configuration_parameter_ids=(parameter,),
        intent_ids=(inspect_intent, escalate_intent),
        lifecycle_ids=("lifecycle.example.request",),
        no_intent_reason_codes=("no_signal",),
        revisit_trigger_ids=(observation,),
        fact_domains={
            observation: ("quiet", "alert"),
            state: ("idle", "reviewing"),
            parameter: ("normal", "urgent"),
        },
        baseline_facts={
            observation: "quiet",
            state: "idle",
            parameter: "normal",
        },
        branches=(
            module.IntentBranch(
                branch_id="branch.example.inspect",
                intent_id=inspect_intent,
                when_all=((observation, ("alert",)), (parameter, ("normal",))),
                private_state_updates=((state, "reviewing"),),
            ),
            module.IntentBranch(
                branch_id="branch.example.escalate",
                intent_id=escalate_intent,
                when_all=((observation, ("alert",)), (parameter, ("urgent",))),
                private_state_updates=((state, "reviewing"),),
            ),
        ),
    )
    return module.RuleParticipantPolicy(
        implementation_id="h2epr.policy.example.participant",
        implementation_version="0.1.0",
        capability_id="example",
        configuration_parameter_ids=(parameter,),
        decisions=(decision,),
    )


def _decision_view(value: Any) -> dict[str, Any]:
    return {
        name: dict(item) if name == "proposed_private_state_updates" else item
        for name, item in vars(value).items()
    }


def test_shared_interface_preserves_the_accepted_panic_behavior_contract() -> None:
    shared_policy = _policy(shared)
    panic_policy = _policy(panic)

    for branch_id in (None, "branch.example.inspect", "branch.example.escalate"):
        shared_context = shared_policy.witness_context(
            actor_id="actor.example",
            commitment_id="h2epr.commitment.example.review",
            branch_id=branch_id,
        )
        panic_context = panic_policy.witness_context(
            actor_id="actor.example",
            commitment_id="h2epr.commitment.example.review",
            branch_id=branch_id,
        )
        assert _decision_view(shared_policy.decide(shared_context)) == (
            _decision_view(panic_policy.decide(panic_context))
        )

    assert shared_policy.commitment_ids == panic_policy.commitment_ids
    assert shared_policy.observation_ids == panic_policy.observation_ids
    assert shared_policy.private_state_ids == panic_policy.private_state_ids
    assert shared_policy.intent_ids == panic_policy.intent_ids
    assert shared_policy.lifecycle_ids == panic_policy.lifecycle_ids


def test_shared_policy_rejects_context_outside_the_declared_fact_surface() -> None:
    policy = _policy(shared)
    context = policy.witness_context(
        actor_id="actor.example",
        commitment_id="h2epr.commitment.example.review",
        branch_id=None,
    )
    invalid = shared.ParticipantDecisionContext(
        actor_id=context.actor_id,
        capability_id=context.capability_id,
        commitment_id=context.commitment_id,
        observations={**context.observations, "obs.example.hidden": "value"},
        private_state=context.private_state,
        configuration_parameters=context.configuration_parameters,
    )

    with pytest.raises(
        shared.ParticipantPolicyError,
        match="observation_scope_mismatch",
    ):
        policy.decide(invalid)


def test_shared_policy_rejects_an_unreachable_ordered_branch() -> None:
    observation = "obs.example.signal"
    state = "state.example.posture"
    first = shared.IntentBranch(
        branch_id="branch.example.first",
        intent_id="h2epr.action.example.first",
        when_all=((observation, ("alert",)),),
    )
    second = shared.IntentBranch(
        branch_id="branch.example.second",
        intent_id="h2epr.action.example.second",
        when_all=((observation, ("alert",)),),
    )
    decision = shared.DecisionSpec(
        commitment_id="h2epr.commitment.example.review",
        observation_ids=(observation,),
        private_state_ids=(state,),
        configuration_parameter_ids=(),
        intent_ids=(first.intent_id, second.intent_id),
        lifecycle_ids=("lifecycle.example.request",),
        no_intent_reason_codes=("no_signal",),
        revisit_trigger_ids=(observation,),
        fact_domains={observation: ("quiet", "alert"), state: ("idle",)},
        baseline_facts={observation: "quiet", state: "idle"},
        branches=(first, second),
    )

    with pytest.raises(
        shared.ParticipantPolicyError,
        match="branch_unreachable:.*branch.example.second",
    ):
        shared.RuleParticipantPolicy(
            implementation_id="h2epr.policy.example.participant",
            implementation_version="0.1.0",
            capability_id="example",
            decisions=(decision,),
        )


def test_shared_participant_source_is_event_neutral() -> None:
    source = Path(shared.__file__).read_text(encoding="utf-8")

    assert "h2epr.scenarios" not in source
    assert "panic_1907" not in source
    assert "singhealth_data_breach" not in source
