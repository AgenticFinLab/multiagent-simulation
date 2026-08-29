from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_ROOT = PROJECT_ROOT / "execution/schemas"
POLICY_SCHEMA_PATH = SCHEMA_ROOT / "policy-realization-v0.1.schema.json"
PACKAGE_SCHEMA_PATH = SCHEMA_ROOT / "executable-scenario-package-v0.1.schema.json"


def _schemas() -> tuple[dict, dict]:
    policy = json.loads(POLICY_SCHEMA_PATH.read_text(encoding="utf-8"))
    package = json.loads(PACKAGE_SCHEMA_PATH.read_text(encoding="utf-8"))
    return policy, package


def _validator(schema: dict, policy_schema: dict) -> Draft202012Validator:
    registry = Registry().with_resources(
        (
            (policy_schema["$id"], Resource.from_contents(policy_schema)),
            (schema["$id"], Resource.from_contents(schema)),
        )
    )
    return Draft202012Validator(schema, registry=registry)


def _semantic_parent() -> dict:
    digest = "0" * 64
    return {
        "configuration_id": "h2epr.example.configuration.v0_1",
        "configuration_version": "0.1.0",
        "configuration_status": "accepted_non_executable_configuration",
        "configuration_path": "configs/example/scenario-configuration.json",
        "configuration_source_sha256": digest,
        "configuration_canonical_sha256": digest,
        "configuration_release_manifest_path": "configs/example/manifest.json",
        "configuration_release_manifest_sha256": digest,
        "configuration_admission_receipt_path": "configs/example/admission/receipt.json",
        "configuration_admission_receipt_sha256": digest,
        "roster_release_manifest_path": "releases/example/manifest.json",
        "roster_release_manifest_sha256": digest,
        "consolidated_mapping_manifest_path": "agents/bindings/example/manifest.json",
        "consolidated_mapping_manifest_sha256": digest,
        "mapping_profile_id": "h2epr.example.mapping.v0_1",
        "mapping_profile_path": "agents/bindings/example/mapping.json",
        "mapping_profile_sha256": digest,
        "scenario_release_manifest_path": "scenarios/example/manifest.json",
        "scenario_release_manifest_sha256": digest,
    }


def _coverage() -> dict:
    return {
        "actor_instances": 1,
        "actor_capability_bindings": 1,
        "population_units": 1,
        "exogenous_inputs": 1,
        "structural_selections": 1,
        "decision_commitments": 1,
        "observation_placements": 1,
        "private_state_placements": 1,
        "configuration_parameter_bindings": 1,
        "intent_placements": 1,
        "lifecycle_families": 1,
        "selected_policies": 1,
        "actor_capabilities_exact": True,
        "configuration_semantics_exact": True,
        "observations_and_private_state_exact": True,
        "commitments_and_intents_exact": True,
        "lifecycle_families_exact": True,
        "selected_policies_exact": True,
        "unsupported_semantics_rejected": True,
    }


def _claim_boundary() -> dict:
    return {
        "construction_exposure": "full_event_evidence",
        "historical_calibration": False,
        "historical_validation": False,
        "known_outcome_fitting": False,
        "held_out_evaluation": False,
        "scientific_validity_claim": False,
        "output_interpretation": "simulation_generated_mechanism_coverage",
    }


def _policy_realization() -> dict:
    return {
        "format_identity": "h2epr.policy-realization.v0_1",
        "realization_id": "h2epr.example.policy-realization.v0_1",
        "version": "0.1.0",
        "status": "accepted_policy_realization",
        "event_id": "H2EPR-EXAMPLE",
        "purpose": "mechanism_coverage",
        "semantic_parent": _semantic_parent(),
        "participant_policy_realizations": [
            {
                "realization_key": "realization.example.actor.capability",
                "actor_id": "actor.example",
                "capability_id": "capability.example",
                "participant_product_id": "h2epr.agent-definition.example",
                "implementation_id": "h2epr.policy.example.participant",
                "implementation_version": "0.1.0",
                "configuration_parameter_bindings": [
                    {
                        "parameter_id": "response_profile",
                        "source_pointer": "/population_units/0/response_profile",
                    }
                ],
                "private_state_realizations": [
                    {
                        "state_id": "state.example.pending",
                        "replay_path": "reducer_owned_actor_private_state",
                        "initialization": "empty",
                        "update_trigger_ids": ["observation.example.changed"],
                    }
                ],
                "decision_realizations": [
                    {
                        "commitment_id": "DC-EXAMPLE-01",
                        "consumed_observation_ids": ["observation.example"],
                        "persistent_state_ids": ["state.example.pending"],
                        "emittable_intent_ids": ["intent.example"],
                        "no_intent_reason_codes": ["condition_not_met"],
                        "revisit_trigger_ids": ["observation.example.changed"],
                        "lifecycle_ids": ["lifecycle.example"],
                    }
                ],
            }
        ],
        "scenario_policy_realizations": [
            {
                "policy_id": "POL-EXAMPLE-01",
                "semantic_version": "0.1.0",
                "selection": "explicit_example_selection",
                "implementation_id": "h2epr.policy.example.environment",
                "implementation_version": "0.1.0",
                "owner_layer": "environment",
                "configuration_source_pointers": ["/policies/0"],
                "governed_semantic_ids": ["lifecycle.example"],
                "rejection_reason_codes": ["unsupported_transition"],
            }
        ],
        "lifecycle_realizations": [
            {
                "lifecycle_id": "lifecycle.example",
                "implementation_id": "h2epr.lifecycle.example",
                "implementation_version": "0.1.0",
                "owner_layer": "reducer",
                "participant_capability_ids": ["capability.example"],
                "state_ids": ["pending", "succeeded", "failed"],
                "terminal_state_ids": ["succeeded", "failed"],
                "invalid_transition_behavior": (
                    "typed_failure_without_state_change"
                ),
            }
        ],
        "coverage_expectations": _coverage(),
        "failure_policy": {
            "missing_implementation": "reject_before_run",
            "unknown_actor_or_capability": "reject_before_run",
            "unknown_observation_or_intent": "reject_before_run",
            "unresolved_configuration_parameter": "reject_before_run",
            "invalid_lifecycle_definition": "reject_before_run",
            "invalid_runtime_transition": "typed_failure_without_state_change",
            "authority_or_resource_mismatch": (
                "fail_closed_without_state_change"
            ),
            "hidden_default": "forbidden",
            "participant_authored_result": "forbidden",
        },
        "claim_boundary": _claim_boundary(),
    }


def _component(identifier: str) -> dict:
    return {
        "implementation_id": identifier,
        "implementation_version": "0.1.0",
    }


def _executable_package() -> dict:
    digest = "1" * 64
    component_names = (
        "policy_registry",
        "scheduler",
        "observation_projector",
        "participant_executor",
        "message_transport",
        "environment",
        "reducer",
        "trace",
        "compiler",
    )
    return {
        "format_identity": "h2epr.executable-scenario-package.v0_1",
        "package_id": "h2epr.example.full-roster-rule.v0_1",
        "version": "0.1.0",
        "status": "accepted_executable_package",
        "execution_eligible": True,
        "event_id": "H2EPR-EXAMPLE",
        "purpose": "mechanism_coverage",
        "semantic_parent": _semantic_parent(),
        "policy_realization": {
            "realization_id": "h2epr.example.policy-realization.v0_1",
            "version": "0.1.0",
            "status": "accepted_policy_realization",
            "path": "execution/example/policy-realization.json",
            "sha256": digest,
        },
        "actor_bindings": [
            {
                "actor_id": "actor.example",
                "capability_ids": ["capability.example"],
                "participant_policy_realization_keys": [
                    "realization.example.actor.capability"
                ],
                "participant_artifact_id": "participant.example",
                "carrier_projection_id": "h2epr.carrier.example",
                "carrier_projection_version": "0.1.0",
                "representation_class": "autonomous_participant_agent",
            }
        ],
        "component_bindings": {
            name: _component(f"h2epr.component.example.{name}")
            for name in component_names
        },
        "masim_usage": {
            "mode": "read_only_public_interfaces",
            "package_version": "0.0.1",
            "public_interface_ids": ["masim.event_process.trace"],
            "phased_runner_used": True,
            "source_modification_allowed": False,
        },
        "runtime_bundle_contract": {
            "format_identity": "h2epr.rule-runtime-bundle.v0_1",
            "builder_implementation_id": "h2epr.runtime.bundle-builder",
            "builder_implementation_version": "0.1.0",
            "deterministic_materialization": True,
            "sections": {
                "actor_registry": True,
                "participant_artifacts": True,
                "carrier_projections": True,
                "initial_state": True,
                "action_registry": True,
                "policy_registry": True,
                "communication_routes": True,
                "observation_rules": True,
                "clock": True,
                "structural_selections": True,
                "exogenous_inputs": True,
                "lifecycle_registry": True,
                "completion_policy": True,
                "compiler_inputs": True,
                "component_registry": True,
            },
        },
        "run_plan": {
            "run_profile_id": "h2epr.example.run-profile.canonical",
            "run_seed": 7,
            "materialization_count": 2,
            "same_input_required": True,
            "same_seed_required": True,
            "independent_materialization_required": True,
            "resume_allowed": False,
            "targeted_perturbation_profile_ids": [],
        },
        "completion": {
            "normal_condition_ids": ["horizon_reached"],
            "unresolved_object_behavior": "carry_forward_with_reason",
            "failure_behavior": "fail_closed_without_output_claim",
        },
        "coverage_expectations": _coverage(),
        "output_contract": {
            "simulation_trace": True,
            "tick_seals": True,
            "run_seal": True,
            "replay_receipt": True,
            "generated_epg": True,
            "execution_receipt": True,
            "determinism_comparison": {
                "runtime_bundle_sha256_match": True,
                "simulation_trace_sha256_match": True,
                "tick_seals_sha256_match": True,
                "run_seal_sha256_match": True,
                "replay_receipt_sha256_match": True,
                "generated_epg_sha256_match": True,
                "replay_final_state_match": True,
                "generated_epg_trace_closure": True,
            },
            "large_artifact_custody": "gitignored_event_run_directory",
            "tracked_surface": (
                "code_inputs_manifest_receipt_checksums_tests_documentation"
            ),
        },
        "claim_boundary": _claim_boundary(),
    }


def test_execution_schemas_are_valid_and_accept_closed_examples() -> None:
    policy_schema, package_schema = _schemas()
    Draft202012Validator.check_schema(policy_schema)
    Draft202012Validator.check_schema(package_schema)

    assert list(_validator(policy_schema, policy_schema).iter_errors(
        _policy_realization()
    )) == []
    assert list(_validator(package_schema, policy_schema).iter_errors(
        _executable_package()
    )) == []


def test_policy_realization_rejects_unknown_fields_and_unresolved_decision() -> None:
    policy_schema, _ = _schemas()
    validator = _validator(policy_schema, policy_schema)

    unknown = _policy_realization()
    unknown["local_worktree"] = "forbidden"
    assert any(
        error.validator == "additionalProperties"
        for error in validator.iter_errors(unknown)
    )

    unresolved = _policy_realization()
    decision = unresolved["participant_policy_realizations"][0][
        "decision_realizations"
    ][0]
    decision["emittable_intent_ids"] = []
    decision["no_intent_reason_codes"] = []
    assert any(
        error.validator == "anyOf"
        for error in validator.iter_errors(unresolved)
    )


def test_policy_realization_requires_complete_coverage_dimensions() -> None:
    policy_schema, _ = _schemas()
    validator = _validator(policy_schema, policy_schema)

    for field in (
        "population_units",
        "exogenous_inputs",
        "structural_selections",
        "private_state_placements",
        "configuration_parameter_bindings",
        "lifecycle_families",
        "configuration_semantics_exact",
        "observations_and_private_state_exact",
        "lifecycle_families_exact",
    ):
        incomplete = _policy_realization()
        incomplete["coverage_expectations"].pop(field)
        errors = list(validator.iter_errors(incomplete))
        assert any(
            error.validator == "required" and field in error.message
            for error in errors
        )


def test_participant_policy_requires_explicit_configuration_bindings() -> None:
    policy_schema, _ = _schemas()
    validator = _validator(policy_schema, policy_schema)

    missing = _policy_realization()
    realization = missing["participant_policy_realizations"][0]
    realization.pop("configuration_parameter_bindings")
    assert any(
        error.validator == "required"
        and "configuration_parameter_bindings" in error.message
        for error in validator.iter_errors(missing)
    )

    unsafe = _policy_realization()
    binding = unsafe["participant_policy_realizations"][0][
        "configuration_parameter_bindings"
    ][0]
    binding["source_pointer"] = "../population_units/0"
    assert list(validator.iter_errors(unsafe))


def test_no_intent_branch_requires_a_revisit_trigger() -> None:
    policy_schema, _ = _schemas()
    validator = _validator(policy_schema, policy_schema)
    incomplete = _policy_realization()
    decision = incomplete["participant_policy_realizations"][0][
        "decision_realizations"
    ][0]
    decision["revisit_trigger_ids"] = []
    assert list(validator.iter_errors(incomplete))


def test_policy_realization_requires_state_lifecycle_and_policy_inputs() -> None:
    policy_schema, _ = _schemas()
    validator = _validator(policy_schema, policy_schema)

    missing_state = _policy_realization()
    missing_state["participant_policy_realizations"][0].pop(
        "private_state_realizations"
    )
    assert list(validator.iter_errors(missing_state))

    missing_lifecycles = _policy_realization()
    missing_lifecycles.pop("lifecycle_realizations")
    assert list(validator.iter_errors(missing_lifecycles))

    missing_policy_inputs = _policy_realization()
    missing_policy_inputs["scenario_policy_realizations"][0].pop(
        "configuration_source_pointers"
    )
    assert list(validator.iter_errors(missing_policy_inputs))


def test_runtime_bundle_requires_every_replay_and_compiler_section() -> None:
    policy_schema, package_schema = _schemas()
    validator = _validator(package_schema, policy_schema)

    for section in (
        "carrier_projections",
        "policy_registry",
        "clock",
        "structural_selections",
        "lifecycle_registry",
        "completion_policy",
        "compiler_inputs",
    ):
        incomplete = _executable_package()
        incomplete["runtime_bundle_contract"]["sections"].pop(section)
        assert any(
            error.validator == "required" and section in error.message
            for error in validator.iter_errors(incomplete)
        )


def test_execution_package_status_and_masim_boundary_fail_closed() -> None:
    policy_schema, package_schema = _schemas()
    validator = _validator(package_schema, policy_schema)

    candidate = _executable_package()
    candidate["status"] = "candidate"
    assert list(validator.iter_errors(candidate))
    candidate["execution_eligible"] = False
    assert list(validator.iter_errors(candidate)) == []

    modified_framework = _executable_package()
    modified_framework["masim_usage"]["source_modification_allowed"] = True
    assert list(validator.iter_errors(modified_framework))


def test_execution_package_requires_closed_repeat_comparison() -> None:
    policy_schema, package_schema = _schemas()
    validator = _validator(package_schema, policy_schema)

    single_materialization = _executable_package()
    single_materialization["run_plan"]["materialization_count"] = 1
    assert list(validator.iter_errors(single_materialization))

    missing_comparison = _executable_package()
    missing_comparison["output_contract"].pop("determinism_comparison")
    assert list(validator.iter_errors(missing_comparison))

    incomplete_comparison = _executable_package()
    incomplete_comparison["output_contract"]["determinism_comparison"].pop(
        "generated_epg_trace_closure"
    )
    assert list(validator.iter_errors(incomplete_comparison))


def test_execution_profiles_reject_unsafe_paths_and_duplicate_ids() -> None:
    policy_schema, package_schema = _schemas()
    policy_validator = _validator(policy_schema, policy_schema)
    package_validator = _validator(package_schema, policy_schema)

    for unsafe_path in (
        "../configuration.json",
        "https://example.test/configuration.json",
        "configs\\configuration.json",
    ):
        unsafe = _policy_realization()
        unsafe["semantic_parent"]["configuration_path"] = unsafe_path
        assert list(policy_validator.iter_errors(unsafe))

        unsafe_package = _executable_package()
        unsafe_package["policy_realization"]["path"] = unsafe_path
        assert list(package_validator.iter_errors(unsafe_package))

    duplicate = _executable_package()
    duplicate["actor_bindings"][0]["capability_ids"] *= 2
    assert any(
        error.validator == "uniqueItems"
        for error in package_validator.iter_errors(duplicate)
    )


def test_examples_are_detached_before_mutation() -> None:
    first = _executable_package()
    second = copy.deepcopy(first)
    second["run_plan"]["run_seed"] = 9
    assert first["run_plan"]["run_seed"] == 7
