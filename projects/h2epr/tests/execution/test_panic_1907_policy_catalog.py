from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from h2epr.scenarios.panic_1907.full_roster_v0_1 import (
    PanicPolicyCatalogError,
    build_panic_policy_catalog,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _copy_project(tmp_path: Path) -> Path:
    root = tmp_path / "h2epr"
    shutil.copytree(PROJECT_ROOT, root)
    return root


def test_panic_policy_catalog_closes_the_configured_placement_surface() -> None:
    catalog = build_panic_policy_catalog(project_root=PROJECT_ROOT)

    assert catalog.event_id == "H2EPR-0288"
    assert catalog.coverage == {
        "actor_instances": 16,
        "actor_capability_bindings": 17,
        "population_units": 10,
        "exogenous_inputs": 9,
        "structural_selections": 8,
        "decision_commitments": 88,
        "observation_placements": 158,
        "private_state_placements": 56,
        "configuration_parameter_bindings": 23,
        "intent_placements": 127,
        "lifecycle_families": 13,
        "selected_policies": 9,
    }
    assert tuple(catalog.placements) == tuple(sorted(catalog.placements))
    assert len(catalog.selected_policy_ids) == 9
    assert len(catalog.lifecycle_ids) == 13


def test_composed_member_bank_has_one_actor_and_two_capability_scopes() -> None:
    catalog = build_panic_policy_catalog(project_root=PROJECT_ROOT)
    resource = catalog.placements[
        "actor.member_bank_alpha::bank_resource_decision"
    ]
    lender = catalog.placements["actor.member_bank_alpha::call_money_lender"]

    assert resource.actor_id == lender.actor_id
    assert resource.entity_id == lender.entity_id
    assert resource.resource_owner_id == lender.resource_owner_id
    assert resource.participant_artifact_id == lender.participant_artifact_id
    assert resource.capability_id != lender.capability_id
    assert set(resource.observation_ids).isdisjoint(lender.observation_ids)
    assert set(resource.intent_ids).isdisjoint(lender.intent_ids)


def test_population_parameters_are_explicit_configuration_pointers() -> None:
    catalog = build_panic_policy_catalog(project_root=PROJECT_ROOT)
    placement = catalog.placements[
        "actor.depositor.knickerbocker.need::knickerbocker_depositor"
    ]

    assert placement.configuration_parameter_bindings == (
        ("response_profile", "/population_units/0/response_profile"),
        ("mixed_signal_rule", "/population_units/0/mixed_signal_rule"),
    )
    assert catalog.selected_policy_pointers["POL-TIME-01"] == (
        "/policy_selections/POL-TIME-01"
    )


def test_catalog_views_are_immutable() -> None:
    catalog = build_panic_policy_catalog(project_root=PROJECT_ROOT)

    with pytest.raises(TypeError):
        catalog.placements["forged"] = next(iter(catalog.placements.values()))
    with pytest.raises(TypeError):
        catalog.coverage["actor_instances"] = 99


def test_configuration_drift_is_rejected_before_catalog_construction(
    tmp_path: Path,
) -> None:
    root = _copy_project(tmp_path)
    path = (
        root
        / "configs/panic_1907/scenario-configuration-v0.1/"
        "scenario-configuration.json"
    )
    path.write_text(path.read_text(encoding="utf-8") + " ", encoding="utf-8")

    with pytest.raises(
        PanicPolicyCatalogError,
        match="PANIC_CATALOG_CONFIGURATION_REJECTED:CONFIG_INTEGRITY_MISMATCH",
    ):
        build_panic_policy_catalog(project_root=root)


def test_released_definition_drift_is_rejected_before_catalog_construction(
    tmp_path: Path,
) -> None:
    root = _copy_project(tmp_path)
    path = root / "agents/defines/panic_1907/knickerbocker-trust.md"
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    with pytest.raises(
        PanicPolicyCatalogError,
        match=(
            "PANIC_CATALOG_CONFIGURATION_REJECTED:"
            "CONFIG_MAPPING_PROFILE_INVALID"
        ),
    ):
        build_panic_policy_catalog(project_root=root)
