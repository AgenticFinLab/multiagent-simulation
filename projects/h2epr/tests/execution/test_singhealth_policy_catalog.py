from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from h2epr.scenarios.singhealth_data_breach.full_roster_v0_1 import (
    SingHealthPolicyCatalogError,
    build_singhealth_policy_catalog,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _copy_project(tmp_path: Path) -> Path:
    root = tmp_path / "h2epr"
    shutil.copytree(PROJECT_ROOT, root)
    return root


def test_singhealth_catalog_closes_product_and_actor_placement_surfaces() -> None:
    catalog = build_singhealth_policy_catalog(project_root=PROJECT_ROOT)

    assert catalog.event_id == "H2EPR-0616"
    assert catalog.coverage == {
        "semantic_products": 9,
        "product_decision_commitments": 29,
        "product_observation_placements": 62,
        "product_private_state_placements": 44,
        "product_intent_placements": 54,
        "actor_instances": 13,
        "actor_capability_bindings": 13,
        "population_units": 6,
        "exogenous_inputs": 6,
        "structural_selections": 6,
        "decision_commitments": 41,
        "observation_placements": 82,
        "private_state_placements": 60,
        "configuration_parameter_bindings": 0,
        "intent_placements": 74,
        "lifecycle_families": 11,
        "selected_policies": 9,
    }
    assert tuple(catalog.placements) == tuple(sorted(catalog.placements))
    assert len(catalog.selected_policy_ids) == 9
    assert len(catalog.lifecycle_ids) == 11


def test_population_units_are_separate_actors_over_one_released_capability() -> None:
    catalog = build_singhealth_policy_catalog(project_root=PROJECT_ROOT)
    technical = tuple(
        placement
        for placement in catalog.placements.values()
        if placement.capability_id
        == "technical_administration_and_line_security_staff"
    )

    assert len(technical) == 3
    assert len({item.actor_id for item in technical}) == 3
    assert len({item.entity_id for item in technical}) == 3
    assert {item.representation_class for item in technical} == {
        "aggregate_population_agent"
    }
    assert len({item.participant_product_id for item in technical}) == 1
    assert len({item.source_product_sha256 for item in technical}) == 1
    assert all(len(item.commitment_ids) == 3 for item in technical)


def test_reused_reader_labels_remain_capability_qualified() -> None:
    catalog = build_singhealth_policy_catalog(project_root=PROJECT_ROOT)
    ciso = catalog.placements[
        "actor.0616.office.cluster-iso::"
        "cluster_information_security_officer"
    ]
    deputy = catalog.placements[
        "actor.0616.office.singhealth-deputy-gceo::"
        "singhealth_deputy_group_chief_executive_officer"
    ]

    ciso_intent = next(
        item
        for item in ciso.intent_ids
        if item.endswith(".request_incident_clarification")
    )
    deputy_intent = next(
        item
        for item in deputy.intent_ids
        if item.endswith(".request_incident_clarification")
    )
    assert ciso_intent != deputy_intent
    assert ciso.commitment_ids == (
        "h2epr.commitment.0616.cluster_information_security_officer.DC-CISO-1",
        "h2epr.commitment.0616.cluster_information_security_officer.DC-CISO-2",
        "h2epr.commitment.0616.cluster_information_security_officer.DC-CISO-3",
    )


def test_policy_pointers_retain_the_released_list_positions() -> None:
    catalog = build_singhealth_policy_catalog(project_root=PROJECT_ROOT)

    assert catalog.selected_policy_pointers["POL-0616-TIME-01"] == (
        "/policy_selections/0"
    )
    assert catalog.selected_policy_pointers["POL-0616-AUTH-01"] == (
        "/policy_selections/5"
    )
    assert catalog.selected_policy_pointers["POL-0616-NOTIFY-01"] == (
        "/policy_selections/8"
    )


def test_catalog_views_are_immutable() -> None:
    catalog = build_singhealth_policy_catalog(project_root=PROJECT_ROOT)

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
        / "configs/singhealth_data_breach/scenario-configuration-v0.1/"
        "scenario-configuration.json"
    )
    path.write_text(path.read_text(encoding="utf-8") + " ", encoding="utf-8")

    with pytest.raises(
        SingHealthPolicyCatalogError,
        match=(
            "SINGHEALTH_CATALOG_CONFIGURATION_REJECTED:"
            "CONFIG_INTEGRITY_MISMATCH"
        ),
    ):
        build_singhealth_policy_catalog(project_root=root)


def test_released_definition_drift_is_rejected_before_catalog_construction(
    tmp_path: Path,
) -> None:
    root = _copy_project(tmp_path)
    path = (
        root
        / "agents/defines/singhealth_data_breach/"
        "security-incident-response-manager.md"
    )
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    with pytest.raises(
        SingHealthPolicyCatalogError,
        match=(
            "SINGHEALTH_CATALOG_CONFIGURATION_REJECTED:"
            "CONFIG_INTEGRITY_MISMATCH"
        ),
    ):
        build_singhealth_policy_catalog(project_root=root)


def test_semantic_inventory_drift_is_rejected_explicitly(tmp_path: Path) -> None:
    root = _copy_project(tmp_path)
    path = (
        root
        / "agents/bindings/singhealth_data_breach/consolidated/"
        "semantic-inventory.md"
    )
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    with pytest.raises(
        SingHealthPolicyCatalogError,
        match="SINGHEALTH_CATALOG_SEMANTIC_INVENTORY_INTEGRITY_MISMATCH",
    ):
        build_singhealth_policy_catalog(project_root=root)
