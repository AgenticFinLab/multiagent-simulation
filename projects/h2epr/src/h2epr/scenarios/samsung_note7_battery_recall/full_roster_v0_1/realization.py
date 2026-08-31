"""Deterministic construction of the Note7 Policy Realization."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from h2epr.execution import read_json_object

from .admission import expected_note7_semantic_parent
from .catalog import CONFIGURATION_PATH, build_note7_policy_catalog
from .registry import (
    lifecycle_rules,
    participant_policies_by_capability,
    scenario_policies,
)


_COVERAGE_KEYS = (
    "actor_instances",
    "actor_capability_bindings",
    "population_units",
    "exogenous_inputs",
    "structural_selections",
    "decision_commitments",
    "observation_placements",
    "private_state_placements",
    "configuration_parameter_bindings",
    "intent_placements",
    "lifecycle_families",
    "selected_policies",
)


def build_note7_policy_realization_document(
    *,
    project_root: str | Path | None = None,
    status: str = "accepted_policy_realization",
) -> dict[str, Any]:
    """Build the exact machine document from reviewed static Rules."""

    if status not in {"candidate", "accepted_policy_realization"}:
        raise ValueError("note7_policy_realization_status_invalid")
    root = _project_root(project_root)
    catalog = build_note7_policy_catalog(project_root=root)
    configuration, _ = read_json_object(
        root / CONFIGURATION_PATH,
        pointer="/semantic_parent/configuration_path",
    )
    participants = participant_policies_by_capability()

    participant_rows = []
    for placement in catalog.placements.values():
        implementation = participants[placement.capability_id]
        state_rows = []
        for state_id in implementation.private_state_ids:
            state_rows.append(
                {
                    "state_id": state_id,
                    "replay_path": "reducer_owned_actor_private_state",
                    "initialization": _state_initialization(state_id),
                    "update_trigger_ids": list(
                        _state_update_triggers(
                            implementation.decisions,
                            state_id,
                        )
                    ),
                }
            )
        decision_rows = [
            {
                "commitment_id": decision.commitment_id,
                "consumed_observation_ids": list(decision.observation_ids),
                "persistent_state_ids": list(decision.private_state_ids),
                "emittable_intent_ids": list(decision.intent_ids),
                "no_intent_reason_codes": list(
                    decision.no_intent_reason_codes
                ),
                "revisit_trigger_ids": list(decision.revisit_trigger_ids),
                "lifecycle_ids": list(decision.lifecycle_ids),
            }
            for decision in implementation.decisions.values()
        ]
        participant_rows.append(
            {
                "realization_key": placement.realization_key,
                "actor_id": placement.actor_id,
                "capability_id": placement.capability_id,
                "participant_product_id": placement.participant_product_id,
                "implementation_id": implementation.implementation_id,
                "implementation_version": implementation.implementation_version,
                "configuration_parameter_bindings": [
                    {
                        "parameter_id": parameter_id,
                        "source_pointer": source_pointer,
                    }
                    for parameter_id, source_pointer in (
                        placement.configuration_parameter_bindings
                    )
                ],
                "private_state_realizations": state_rows,
                "decision_realizations": decision_rows,
            }
        )

    configured = {
        str(row["policy_id"]): row
        for row in configuration["policy_selections"]
    }
    scenario_by_policy_id = {
        implementation.policy_id: implementation
        for implementation in scenario_policies().values()
    }
    scenario_rows = []
    for policy_id in catalog.selected_policy_ids:
        implementation = scenario_by_policy_id[policy_id]
        selected = configured[policy_id]
        scenario_rows.append(
            {
                "policy_id": policy_id,
                "semantic_version": selected["semantic_version"],
                "selection": implementation.selection,
                "implementation_id": implementation.implementation_id,
                "implementation_version": implementation.implementation_version,
                "owner_layer": implementation.owner_layer,
                "configuration_source_pointers": [
                    catalog.selected_policy_pointers[policy_id]
                ],
                "governed_semantic_ids": list(
                    implementation.governed_semantic_ids
                ),
                "rejection_reason_codes": list(
                    implementation.rejection_reason_codes
                ),
            }
        )

    lifecycle_by_id = {
        implementation.lifecycle_id: implementation
        for implementation in lifecycle_rules().values()
    }
    lifecycle_rows = []
    for lifecycle_id in catalog.lifecycle_ids:
        implementation = lifecycle_by_id[lifecycle_id]
        lifecycle_rows.append(
            {
                "lifecycle_id": lifecycle_id,
                "implementation_id": implementation.implementation_id,
                "implementation_version": implementation.implementation_version,
                "owner_layer": implementation.owner_layer,
                "participant_capability_ids": list(
                    implementation.participant_capability_ids
                ),
                "state_ids": list(implementation.state_ids),
                "terminal_state_ids": list(
                    implementation.terminal_state_ids
                ),
                "invalid_transition_behavior": (
                    implementation.invalid_transition_behavior
                ),
            }
        )

    coverage = {
        **{key: catalog.coverage[key] for key in _COVERAGE_KEYS},
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
        "realization_id": "h2epr.0481.policy-realization.v0_1",
        "version": "0.1.0",
        "status": status,
        "event_id": "H2EPR-0481",
        "purpose": "mechanism_coverage",
        "semantic_parent": dict(expected_note7_semantic_parent()),
        "participant_policy_realizations": participant_rows,
        "scenario_policy_realizations": scenario_rows,
        "lifecycle_realizations": lifecycle_rows,
        "coverage_expectations": coverage,
        "failure_policy": {
            "missing_implementation": "reject_before_run",
            "unknown_actor_or_capability": "reject_before_run",
            "unknown_observation_or_intent": "reject_before_run",
            "unresolved_configuration_parameter": "reject_before_run",
            "invalid_lifecycle_definition": "reject_before_run",
            "invalid_runtime_transition": (
                "typed_failure_without_state_change"
            ),
            "authority_or_resource_mismatch": (
                "fail_closed_without_state_change"
            ),
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
            "output_interpretation": (
                "simulation_generated_mechanism_coverage"
            ),
        },
    }


def _project_root(supplied: str | Path | None) -> Path:
    if supplied is not None:
        root = Path(supplied).resolve()
    else:
        root = next(
            (
                parent
                for parent in Path(__file__).resolve().parents
                if parent.joinpath("src/h2epr").is_dir()
                and parent.joinpath("configs").is_dir()
            ),
            Path(),
        )
    if not root.is_dir() or not root.joinpath("src/h2epr").is_dir():
        raise ValueError("note7_policy_realization_project_root_invalid")
    return root


def _state_initialization(state_id: str) -> str:
    reader_id = state_id.rsplit(".", 1)[-1]
    if reader_id == "coverage_assessment":
        return "authoritative_projection"
    return "empty"


def _state_update_triggers(
    decisions: Mapping[str, Any],
    state_id: str,
) -> tuple[str, ...]:
    direct = {
        branch.intent_id
        for decision in decisions.values()
        for branch in decision.branches
        if state_id in dict(branch.private_state_updates)
    }
    if direct:
        return tuple(sorted(direct))
    observed = {
        observation_id
        for decision in decisions.values()
        if state_id in decision.private_state_ids
        for observation_id in decision.revisit_trigger_ids
    }
    if not observed:
        raise ValueError(f"note7_state_update_trigger_missing:{state_id}")
    return tuple(sorted(observed))


__all__ = ["build_note7_policy_realization_document"]
