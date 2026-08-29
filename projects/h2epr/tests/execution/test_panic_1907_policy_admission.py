from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import shutil

import pytest

from h2epr.scenarios.panic_1907.full_roster_v0_1 import (
    PolicyRealizationAdmissionError,
    PolicyRealizationErrorCode,
    build_panic_policy_catalog,
    expected_panic_semantic_parent,
    load_panic_policy_realization,
)
from h2epr.scenarios.panic_1907.full_roster_v0_1.realization import (
    build_panic_policy_realization_document,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def project_copy(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("panic-policy-admission") / "h2epr"
    shutil.copytree(PROJECT_ROOT, root)
    return root


def _candidate(root: Path) -> dict:
    catalog = build_panic_policy_catalog(project_root=root)
    participants = []
    for placement in catalog.placements.values():
        commitments = placement.commitment_ids
        observations = placement.observation_ids
        states = placement.private_state_ids
        intents = placement.intent_ids
        decisions = []
        for index, commitment_id in enumerate(commitments):
            decisions.append(
                {
                    "commitment_id": commitment_id,
                    "consumed_observation_ids": list(
                        observations[index :: len(commitments)]
                    ),
                    "persistent_state_ids": list(
                        states[index :: len(commitments)]
                    ),
                    "emittable_intent_ids": list(
                        intents[index :: len(commitments)]
                    ),
                    "no_intent_reason_codes": ["declared_blocker"],
                    "revisit_trigger_ids": [
                        observations[index % len(observations)]
                    ],
                    "lifecycle_ids": [
                        catalog.lifecycle_ids[index % len(catalog.lifecycle_ids)]
                    ],
                }
            )
        participants.append(
            {
                "realization_key": placement.realization_key,
                "actor_id": placement.actor_id,
                "capability_id": placement.capability_id,
                "participant_product_id": placement.source_product_id,
                "implementation_id": (
                    "h2epr.policy.0288.participant."
                    f"{placement.capability_id}"
                ),
                "implementation_version": "0.1.0",
                "configuration_parameter_bindings": [
                    {"parameter_id": parameter, "source_pointer": pointer}
                    for parameter, pointer in (
                        placement.configuration_parameter_bindings
                    )
                ],
                "private_state_realizations": [
                    {
                        "state_id": state_id,
                        "replay_path": "reducer_owned_actor_private_state",
                        "initialization": "empty",
                        "update_trigger_ids": [observations[0]],
                    }
                    for state_id in states
                ],
                "decision_realizations": decisions,
            }
        )

    owner_layers = {
        "POL-TIME-01": "scheduler",
        "POL-INFO-01": "information",
        "POL-SERVICE-01": "environment",
        "POL-REVIEW-01": "environment",
        "POL-AMOUNT-01": "environment",
        "POL-FACILITY-01": "environment",
        "POL-VENUE-01": "environment",
        "POL-LIFECYCLE-01": "reducer",
        "POL-RESULT-01": "reducer",
    }
    configuration = json.loads(
        (root / expected_panic_semantic_parent()["configuration_path"])
        .read_text(encoding="utf-8")
    )
    scenario_policies = []
    for policy_id in catalog.selected_policy_ids:
        selection = configuration["policy_selections"][policy_id]
        scenario_policies.append(
            {
                "policy_id": policy_id,
                "semantic_version": selection["version"],
                "selection": selection["selection"],
                "implementation_id": (
                    "h2epr.policy.0288.scenario."
                    f"{policy_id.lower().replace('-', '_')}"
                ),
                "implementation_version": "0.1.0",
                "owner_layer": owner_layers[policy_id],
                "configuration_source_pointers": [
                    catalog.selected_policy_pointers[policy_id]
                ],
                "governed_semantic_ids": list(
                    catalog.policy_governed_semantic_ids[policy_id]
                ),
                "rejection_reason_codes": ["unsupported_input"],
            }
        )

    capabilities = sorted(
        {placement.capability_id for placement in catalog.placements.values()}
    )
    lifecycles = [
        {
            "lifecycle_id": lifecycle_id,
            "implementation_id": (
                "h2epr.lifecycle.0288."
                f"{lifecycle_id.removeprefix('lifecycle.0288.')}"
            ),
            "implementation_version": "0.1.0",
            "owner_layer": "reducer",
            "participant_capability_ids": [
                capabilities[index % len(capabilities)]
            ],
            "state_ids": ["none", "active", "closed"],
            "terminal_state_ids": ["closed"],
            "invalid_transition_behavior": "typed_failure_without_state_change",
        }
        for index, lifecycle_id in enumerate(catalog.lifecycle_ids)
    ]
    coverage = {
        **dict(catalog.coverage),
        "actor_capabilities_exact": True,
        "configuration_semantics_exact": True,
        "observations_and_private_state_exact": True,
        "commitments_and_intents_exact": True,
        "lifecycle_families_exact": True,
        "selected_policies_exact": True,
        "unsupported_semantics_rejected": True,
    }
    return {
        "format_identity": "h2epr.policy-realization.v0_1",
        "realization_id": "h2epr.0288.policy-realization.v0_1",
        "version": "0.1.0",
        "status": "candidate",
        "event_id": "H2EPR-0288",
        "purpose": "mechanism_coverage",
        "semantic_parent": dict(expected_panic_semantic_parent()),
        "participant_policy_realizations": participants,
        "scenario_policy_realizations": scenario_policies,
        "lifecycle_realizations": lifecycles,
        "coverage_expectations": coverage,
        "failure_policy": {
            "missing_implementation": "reject_before_run",
            "unknown_actor_or_capability": "reject_before_run",
            "unknown_observation_or_intent": "reject_before_run",
            "unresolved_configuration_parameter": "reject_before_run",
            "invalid_lifecycle_definition": "reject_before_run",
            "invalid_runtime_transition": "typed_failure_without_state_change",
            "authority_or_resource_mismatch": "fail_closed_without_state_change",
            "hidden_default": "forbidden",
            "participant_authored_result": "forbidden",
        },
        "claim_boundary": {
            "construction_exposure": "full_event_evidence",
            "historical_calibration": False,
            "historical_validation": False,
            "known_outcome_fitting": False,
            "held_out_evaluation": False,
            "scientific_validity_claim": False,
            "output_interpretation": "simulation_generated_mechanism_coverage",
        },
    }


def _write(root: Path, name: str, document: dict) -> tuple[Path, str]:
    directory = root / "execution/panic_1907/test-candidates"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.json"
    path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path, hashlib.sha256(path.read_bytes()).hexdigest()


def test_complete_candidate_is_implementation_closed_but_not_accepted(
    project_copy: Path,
) -> None:
    path, digest = _write(project_copy, "complete", _candidate(project_copy))

    admission = load_panic_policy_realization(
        path,
        project_root=project_copy,
        expected_source_sha256=digest,
    )

    assert admission.semantic_complete is True
    assert admission.implementation_complete is True
    assert admission.accepted is False
    assert admission.missing_implementation_ids == ()
    assert admission.coverage["actor_capability_bindings"] == 17
    with pytest.raises(TypeError):
        admission.document["status"] = "forged"


def test_accepted_status_rejects_an_unimplemented_realization(
    project_copy: Path,
) -> None:
    document = _candidate(project_copy)
    document["status"] = "accepted_policy_realization"
    document["scenario_policy_realizations"][0]["implementation_id"] = (
        "h2epr.policy.0288.scenario.unimplemented"
    )
    path, digest = _write(project_copy, "false-acceptance", document)

    with pytest.raises(PolicyRealizationAdmissionError) as raised:
        load_panic_policy_realization(
            path,
            project_root=project_copy,
            expected_source_sha256=digest,
        )
    assert raised.value.code is PolicyRealizationErrorCode.IMPLEMENTATION_MISSING


def test_accepted_status_admits_the_closed_implementation_registry(
    project_copy: Path,
) -> None:
    document = _candidate(project_copy)
    document["status"] = "accepted_policy_realization"
    path, digest = _write(project_copy, "accepted", document)

    admission = load_panic_policy_realization(
        path,
        project_root=project_copy,
        expected_source_sha256=digest,
    )

    assert admission.accepted is True
    assert admission.implementation_complete is True
    assert admission.missing_implementation_ids == ()


def test_static_implementations_build_the_accepted_realization(
    project_copy: Path,
) -> None:
    document = build_panic_policy_realization_document(
        project_root=project_copy,
    )
    path, digest = _write(project_copy, "built-accepted", document)

    admission = load_panic_policy_realization(
        path,
        project_root=project_copy,
        expected_source_sha256=digest,
    )

    assert admission.accepted is True
    assert len(document["participant_policy_realizations"]) == 17
    assert len(document["scenario_policy_realizations"]) == 9
    assert len(document["lifecycle_realizations"]) == 13


def test_missing_actor_capability_placement_fails_exact_coverage(
    project_copy: Path,
) -> None:
    document = _candidate(project_copy)
    document["participant_policy_realizations"].pop()
    path, digest = _write(project_copy, "missing-placement", document)

    with pytest.raises(PolicyRealizationAdmissionError) as raised:
        load_panic_policy_realization(
            path,
            project_root=project_copy,
            expected_source_sha256=digest,
        )
    assert raised.value.code is (
        PolicyRealizationErrorCode.PLACEMENT_COVERAGE_MISMATCH
    )


def test_cross_capability_intent_reference_fails_closed(
    project_copy: Path,
) -> None:
    document = _candidate(project_copy)
    first, second = document["participant_policy_realizations"][:2]
    foreign_intent = second["decision_realizations"][0]["emittable_intent_ids"][0]
    first["decision_realizations"][0]["emittable_intent_ids"] = [foreign_intent]
    path, digest = _write(project_copy, "cross-capability-intent", document)

    with pytest.raises(PolicyRealizationAdmissionError) as raised:
        load_panic_policy_realization(
            path,
            project_root=project_copy,
            expected_source_sha256=digest,
        )
    assert raised.value.code is (
        PolicyRealizationErrorCode.SEMANTIC_REFERENCE_INVALID
    )


def test_wrong_but_resolvable_parameter_pointer_is_rejected(
    project_copy: Path,
) -> None:
    document = _candidate(project_copy)
    participant = next(
        row
        for row in document["participant_policy_realizations"]
        if row["configuration_parameter_bindings"]
    )
    participant["configuration_parameter_bindings"][0]["source_pointer"] = (
        "/population_units/1/response_profile"
    )
    path, digest = _write(project_copy, "wrong-parameter-pointer", document)

    with pytest.raises(PolicyRealizationAdmissionError) as raised:
        load_panic_policy_realization(
            path,
            project_root=project_copy,
            expected_source_sha256=digest,
        )
    assert raised.value.code is (
        PolicyRealizationErrorCode.CONFIGURATION_POINTER_INVALID
    )


def test_parent_or_source_identity_drift_is_rejected(
    project_copy: Path,
) -> None:
    document = _candidate(project_copy)
    document["semantic_parent"]["configuration_canonical_sha256"] = "0" * 64
    path, digest = _write(project_copy, "wrong-parent", document)

    with pytest.raises(PolicyRealizationAdmissionError) as raised:
        load_panic_policy_realization(
            path,
            project_root=project_copy,
            expected_source_sha256=digest,
        )
    assert raised.value.code is PolicyRealizationErrorCode.PARENT_MISMATCH

    with pytest.raises(PolicyRealizationAdmissionError) as source_raised:
        load_panic_policy_realization(
            path,
            project_root=project_copy,
            expected_source_sha256="f" * 64,
        )
    assert source_raised.value.code is (
        PolicyRealizationErrorCode.INTEGRITY_MISMATCH
    )


def test_candidate_objects_are_detached_before_mutation(project_copy: Path) -> None:
    first = _candidate(project_copy)
    second = copy.deepcopy(first)
    second["version"] = "0.1.1"
    assert first["version"] == "0.1.0"
