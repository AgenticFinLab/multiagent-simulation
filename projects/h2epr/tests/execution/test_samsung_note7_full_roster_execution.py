from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path

import pytest

from h2epr.execution import (
    FORMAL_RUN_DOCUMENTS,
    LifecycleRecord,
    ParticipantDecisionContext,
)
from h2epr.scenarios.samsung_note7_battery_recall.full_roster_v0_1 import (
    build_note7_policy_catalog,
    build_note7_policy_realization_document,
    build_note7_runtime_bundle_document,
    load_note7_executable_package,
    load_note7_policy_realization,
)
from h2epr.scenarios.samsung_note7_battery_recall.full_roster_v0_1.lifecycle_rules import (
    LIFECYCLE_RULES,
)
from h2epr.scenarios.samsung_note7_battery_recall.full_roster_v0_1.registry import (
    implementation_versions,
    participant_policies_by_capability,
)
from h2epr.scenarios.samsung_note7_battery_recall.full_roster_v0_1.run_release import (
    EXPECTED_COVERAGE,
    load_note7_run_release,
)
from h2epr.scenarios.samsung_note7_battery_recall.full_roster_v0_1.runtime_components import (
    Note7Environment,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
POLICY_ROOT = (
    PROJECT_ROOT
    / "execution/samsung_note7_battery_recall/policy-realization-v0.1"
)
EXECUTABLE_ROOT = (
    PROJECT_ROOT
    / "execution/samsung_note7_battery_recall/full-roster-rule-v0.1"
)
RUN_ROOT = (
    PROJECT_ROOT
    / "execution/samsung_note7_battery_recall/run-and-graph-v0.1"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _checksum_rows(root: Path) -> dict[str, str]:
    return {
        name: digest
        for digest, name in (
            line.split("  ", 1)
            for line in (root / "SHA256SUMS")
            .read_text(encoding="utf-8")
            .splitlines()
        )
    }


def test_policy_catalog_and_machine_realization_close_exact_surface() -> None:
    catalog = build_note7_policy_catalog(project_root=PROJECT_ROOT)
    assert dict(catalog.coverage) == {
        "semantic_products": 8,
        "product_decision_commitments": 22,
        "product_observation_placements": 40,
        "product_private_state_placements": 28,
        "product_intent_placements": 37,
        "actor_instances": 8,
        "actor_capability_bindings": 8,
        "population_units": 4,
        "exogenous_inputs": 6,
        "structural_selections": 6,
        "decision_commitments": 22,
        "observation_placements": 40,
        "private_state_placements": 28,
        "configuration_parameter_bindings": 0,
        "intent_placements": 37,
        "lifecycle_families": 12,
        "selected_policies": 9,
    }
    released = json.loads(
        (POLICY_ROOT / "policy-realization.json").read_text(encoding="utf-8")
    )
    assert released == build_note7_policy_realization_document(
        project_root=PROJECT_ROOT
    )
    admission = load_note7_policy_realization(
        POLICY_ROOT / "policy-realization.json",
        project_root=PROJECT_ROOT,
        expected_source_sha256=_sha256(
            POLICY_ROOT / "policy-realization.json"
        ),
    )
    assert admission.accepted is True
    assert admission.semantic_complete is True
    assert admission.implementation_complete is True
    assert len(implementation_versions()) == 29


def test_every_participant_branch_and_no_intent_path_is_reachable() -> None:
    policies = participant_policies_by_capability()
    assert len(policies) == 8
    assert sum(len(policy.decisions) for policy in policies.values()) == 22
    assert sum(len(policy.intent_ids) for policy in policies.values()) == 37
    for capability_id, policy in policies.items():
        for decision in policy.decisions.values():
            baseline = dict(decision.baseline_facts)
            context = ParticipantDecisionContext(
                actor_id=f"actor.test.{capability_id}",
                capability_id=capability_id,
                commitment_id=decision.commitment_id,
                observations={
                    key: baseline[key] for key in decision.observation_ids
                },
                private_state={
                    key: baseline[key] for key in decision.private_state_ids
                },
                configuration_parameters={},
            )
            assert policy.decide(context).intent_id is None
            for branch in decision.branches:
                facts = dict(baseline)
                for field_id, values in branch.when_all:
                    facts[field_id] = values[0]
                branch_context = ParticipantDecisionContext(
                    actor_id=context.actor_id,
                    capability_id=capability_id,
                    commitment_id=decision.commitment_id,
                    observations={
                        key: facts[key] for key in decision.observation_ids
                    },
                    private_state={
                        key: facts[key] for key in decision.private_state_ids
                    },
                    configuration_parameters={},
                )
                result = policy.decide(branch_context)
                assert result.branch_id == branch.branch_id
                assert result.intent_id == branch.intent_id


def test_lifecycle_registry_is_exact_reachable_and_deterministic() -> None:
    catalog = build_note7_policy_catalog(project_root=PROJECT_ROOT)
    participants_by_lifecycle: dict[str, set[str]] = defaultdict(set)
    for capability_id, participant in participant_policies_by_capability().items():
        for decision in participant.decisions.values():
            for lifecycle_id in decision.lifecycle_ids:
                participants_by_lifecycle[lifecycle_id].add(capability_id)
    assert {rule.lifecycle_id for rule in LIFECYCLE_RULES} == set(
        catalog.lifecycle_ids
    )
    for rule in LIFECYCLE_RULES:
        assert set(rule.participant_capability_ids) == participants_by_lifecycle[
            rule.lifecycle_id
        ]
        reached = set(rule.initial_state_ids)
        while True:
            expanded = reached | {
                target
                for source, target in rule.transitions
                if source in reached
            }
            if expanded == reached:
                break
            reached = expanded
        assert reached == set(rule.state_ids)
        for index, (source, target) in enumerate(rule.transitions):
            record = LifecycleRecord(
                object_id=f"object.{index}",
                lifecycle_id=rule.lifecycle_id,
                owner_actor_id="actor.owner",
                state_id=source,
                version=3,
                terminal=source in rule.terminal_state_ids,
                causal_parent_ids=("event.open",),
            )
            first = rule.transition(
                record,
                target_state_id=target,
                cause_id="event.transition",
            )
            second = rule.transition(
                record,
                target_state_id=target,
                cause_id="event.transition",
            )
            assert first == second
            assert first.applied is True
            assert first.after.version == 4


def test_runtime_bundle_and_executable_admission_close() -> None:
    released_bundle = json.loads(
        (EXECUTABLE_ROOT / "runtime-bundle.json").read_text(encoding="utf-8")
    )
    assert released_bundle == build_note7_runtime_bundle_document(
        project_root=PROJECT_ROOT
    )
    package = EXECUTABLE_ROOT / "executable-package.json"
    admission = load_note7_executable_package(
        package,
        project_root=PROJECT_ROOT,
        expected_source_sha256=_sha256(package),
    )
    assert admission.accepted is True
    assert admission.execution_eligible is True
    assert dict(admission.coverage) == {
        "actor_instances": 8,
        "actor_carriers": 8,
        "actor_capability_bindings": 8,
        "action_bindings": 37,
        "decision_observation_rules": 22,
        "communication_routes": 24,
        "configured_route_records": 8,
        "lifecycle_families": 12,
        "runtime_components": 9,
    }
    bundle = admission.runtime_bundle_document
    assert len(bundle["clock"]["logical_ticks"]) == 50
    assert all(
        route["configured_route_record_id"] is not None
        for route in bundle["communication_routes"]
        if route["purpose"] != "environment_result"
    )
    assert {
        row["primary_lifecycle_id"]
        for row in bundle["observation_rules"]
    } == {row["lifecycle_id"] for row in bundle["lifecycle_registry"]}
    assert {
        row["policy_id"] for row in Note7Environment(bundle).scenario_policy_checks()
    } == {
        row["policy_id"]
        for row in bundle["policy_registry"]["scenario_policies"]
    }


def test_compact_run_release_is_strictly_admitted() -> None:
    manifest = RUN_ROOT / "manifest.json"
    admission = load_note7_run_release(
        manifest,
        project_root=PROJECT_ROOT,
        expected_manifest_source_sha256=_sha256(manifest),
    )
    assert admission.accepted is True
    assert admission.deterministic_pair is True
    assert admission.replay_closed is True
    assert admission.graph_closed is True
    assert tuple(admission.formal_documents) == FORMAL_RUN_DOCUMENTS
    receipt = admission.formal_documents["execution-receipt.json"]
    assert {
        name: receipt["coverage"][name] for name in EXPECTED_COVERAGE
    } == dict(EXPECTED_COVERAGE)
    assert receipt["coverage"]["record_counts"] == {
        "action_disposition": 22,
        "action_intent": 22,
        "carry_forward": 22,
        "completion": 1,
        "exogenous_input_release": 6,
        "message_disposition": 74,
        "message_intent": 37,
        "observation": 400,
        "participant_decision": 22,
        "run_seal": 1,
        "scenario_policy_application": 117,
        "state_delta": 52,
        "tick_commit": 50,
        "tick_open": 50,
        "tick_seal": 50,
    }
    graph = admission.formal_documents["generated-epg-receipt.json"]
    assert graph["generated_epg"]["node_count"] == 374
    assert graph["generated_epg"]["edge_count"] == 302


@pytest.mark.parametrize("root", [POLICY_ROOT, EXECUTABLE_ROOT, RUN_ROOT])
def test_release_checksum_inventory_closes(root: Path) -> None:
    rows = _checksum_rows(root)
    assert all(_sha256(root / name) == digest for name, digest in rows.items())
