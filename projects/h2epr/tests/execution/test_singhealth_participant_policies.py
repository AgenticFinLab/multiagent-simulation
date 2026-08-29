from __future__ import annotations

from pathlib import Path

import pytest

from h2epr.execution import ParticipantDecisionContext, ParticipantPolicyError
from h2epr.scenarios.singhealth_data_breach.full_roster_v0_1 import (
    build_singhealth_policy_catalog,
    participant_policies,
    participant_policies_by_capability,
    participant_policy,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_registry_closes_all_nine_released_capabilities() -> None:
    policies = participant_policies_by_capability()

    assert len(policies) == 9
    assert len(participant_policies()) == 9
    assert sum(len(item.decisions) for item in policies.values()) == 29
    assert sum(
        len(decision.branches)
        for item in policies.values()
        for decision in item.decisions.values()
    ) == 111
    assert tuple(policies) == (
        "technical_administration_and_line_security_staff",
        "security_incident_response_manager",
        "cluster_information_security_officer",
        "ihis_operational_and_scm_management",
        "singhealth_group_chief_information_officer",
        "cyber_security_governance_director_and_healthcare_sector_lead",
        "ihis_chief_executive_officer",
        "singhealth_deputy_group_chief_executive_officer",
        "singhealth_group_chief_executive_officer",
    )


def test_policy_surfaces_equal_the_hash_pinned_execution_catalog() -> None:
    catalog = build_singhealth_policy_catalog(project_root=PROJECT_ROOT)
    policies = participant_policies_by_capability()
    placement_by_capability = {
        placement.capability_id: placement
        for placement in catalog.placements.values()
    }

    assert set(policies) == set(placement_by_capability)
    for capability_id, implementation in policies.items():
        placement = placement_by_capability[capability_id]
        assert set(implementation.commitment_ids) == set(
            placement.commitment_ids
        )
        assert set(implementation.observation_ids) == set(
            placement.observation_ids
        )
        assert set(implementation.private_state_ids) == set(
            placement.private_state_ids
        )
        assert set(implementation.intent_ids) == set(placement.intent_ids)
        assert implementation.configuration_parameter_ids == ()


def test_every_declared_branch_and_no_intent_path_has_a_witness() -> None:
    for implementation in participant_policies().values():
        for decision in implementation.decisions.values():
            baseline = implementation.witness_context(
                actor_id=f"actor.witness.{implementation.capability_id}",
                commitment_id=decision.commitment_id,
                branch_id=None,
            )
            baseline_result = implementation.decide(baseline)
            assert baseline_result.intent_id is None
            assert baseline_result.branch_id is None
            assert baseline_result.no_intent_reason_code == (
                "no_new_material_or_acknowledged_equivalent"
            )
            assert baseline_result.revisit_trigger_ids

            for branch in decision.branches:
                witness = implementation.witness_context(
                    actor_id=f"actor.witness.{implementation.capability_id}",
                    commitment_id=decision.commitment_id,
                    branch_id=branch.branch_id,
                )
                result = implementation.decide(witness)
                assert result.branch_id == branch.branch_id
                assert result.intent_id == branch.intent_id
                assert result.no_intent_reason_code is None
                assert result.revisit_trigger_ids == ()
                assert result.proposed_private_state_updates == dict(
                    branch.private_state_updates
                )
                assert (
                    witness.observations != baseline.observations
                    or witness.private_state != baseline.private_state
                )


def test_each_configured_actor_resolves_to_exactly_one_static_policy() -> None:
    catalog = build_singhealth_policy_catalog(project_root=PROJECT_ROOT)
    policies = participant_policies_by_capability()

    resolved = [policies[item.capability_id] for item in catalog.placements.values()]
    assert len(resolved) == 13
    assert len({item.implementation_id for item in resolved}) == 9
    assert sum(
        item.capability_id
        == "technical_administration_and_line_security_staff"
        for item in resolved
    ) == 3
    assert sum(
        item.capability_id == "ihis_operational_and_scm_management"
        for item in resolved
    ) == 3


def test_unknown_implementation_and_out_of_domain_fact_fail_closed() -> None:
    with pytest.raises(KeyError, match="unknown_participant_policy"):
        participant_policy("h2epr.policy.0616.participant.unknown")

    implementation = next(iter(participant_policies().values()))
    commitment_id = implementation.commitment_ids[0]
    context = implementation.witness_context(
        actor_id="actor.witness.invalid",
        commitment_id=commitment_id,
        branch_id=None,
    )
    observation_id = next(iter(context.observations))
    invalid = ParticipantDecisionContext(
        actor_id=context.actor_id,
        capability_id=context.capability_id,
        commitment_id=context.commitment_id,
        observations={**context.observations, observation_id: "invented_value"},
        private_state=context.private_state,
        configuration_parameters=context.configuration_parameters,
    )
    with pytest.raises(
        ParticipantPolicyError,
        match="fact_value_outside_domain",
    ):
        implementation.decide(invalid)


def test_access_and_concurrent_capacity_gates_fail_closed() -> None:
    policies = participant_policies_by_capability()

    technical = policies["technical_administration_and_line_security_staff"]
    technical_context = technical.witness_context(
        actor_id="actor.witness.technical",
        commitment_id=(
            "h2epr.commitment.0616."
            "technical_administration_and_line_security_staff.SITUATION-A"
        ),
        branch_id=(
            "branch.technical_administration_and_line_security_staff."
            "apply_local_control"
        ),
    )
    technical_without_access = ParticipantDecisionContext(
        actor_id=technical_context.actor_id,
        capability_id=technical_context.capability_id,
        commitment_id=technical_context.commitment_id,
        observations={
            **technical_context.observations,
            (
                "obs.technical_administration_and_line_security_staff."
                "local_control_state"
            ): "unknown",
        },
        private_state=technical_context.private_state,
        configuration_parameters=technical_context.configuration_parameters,
    )
    assert technical.decide(technical_without_access).intent_id is None

    gated_cases = (
        (
            policies[
                "cyber_security_governance_director_and_healthcare_sector_lead"
            ],
            (
                "h2epr.commitment.0616."
                "cyber_security_governance_director_and_healthcare_sector_lead."
                "DC-SL-3"
            ),
            (
                "branch."
                "cyber_security_governance_director_and_healthcare_sector_lead."
                "report_cii_incident_to_csa"
            ),
            (
                "obs."
                "cyber_security_governance_director_and_healthcare_sector_lead."
                "acting_capacity_context"
            ),
            "ambiguous",
        ),
        (
            policies["ihis_chief_executive_officer"],
            "h2epr.commitment.0616.ihis_chief_executive_officer.DC-ICEO-1",
            (
                "branch.ihis_chief_executive_officer."
                "request_executive_incident_briefing"
            ),
            "obs.ihis_chief_executive_officer.acting_capacity_context",
            "moh_cio",
        ),
    )
    for implementation, commitment_id, branch_id, observation_id, value in (
        gated_cases
    ):
        context = implementation.witness_context(
            actor_id="actor.witness.capacity",
            commitment_id=commitment_id,
            branch_id=branch_id,
        )
        wrong_capacity = ParticipantDecisionContext(
            actor_id=context.actor_id,
            capability_id=context.capability_id,
            commitment_id=context.commitment_id,
            observations={**context.observations, observation_id: value},
            private_state=context.private_state,
            configuration_parameters=context.configuration_parameters,
        )
        assert implementation.decide(wrong_capacity).intent_id is None


def test_registry_and_policy_views_are_immutable() -> None:
    registry = participant_policies()
    implementation = next(iter(registry.values()))

    with pytest.raises(TypeError):
        registry["forged"] = implementation
    with pytest.raises(TypeError):
        implementation.decisions["forged"] = next(
            iter(implementation.decisions.values())
        )


def test_singhealth_rules_consume_only_the_shared_participant_interface() -> None:
    package = (
        PROJECT_ROOT
        / "src/h2epr/scenarios/singhealth_data_breach/full_roster_v0_1"
    )
    specification = (package / "specification.py").read_text(encoding="utf-8")
    rule_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(package.glob("participant_rules_*.py"))
    )

    assert "from h2epr.execution import" in specification
    assert "panic_1907" not in specification
    assert "panic_1907" not in rule_sources
