from __future__ import annotations

import json
from pathlib import Path

import pytest

from h2epr.bundles.canonical import canonical_bytes
from h2epr.world import (
    PROFILES,
    build_normalized_world,
    clamp_basis_points,
    neighbor_stress,
    next_confidence,
    next_withdrawal_pressure,
    pro_rata_floor_then_seeded_remainder,
    resource_stress,
    transfer_balances,
    validate_world,
)


FIXTURE = Path(__file__).parents[1] / "fixtures/g2/v1/synthetic/normalized_world_golden.json"


def test_exact_profiles_and_equations() -> None:
    assert PROFILES == {
        "low_stress": {"liquid_resource_bp": 7000, "confidence_index_bp": 7000, "withdrawal_pressure_bp": 3000, "coordination_readiness_bp": 7000},
        "balanced": {"liquid_resource_bp": 5000, "confidence_index_bp": 5000, "withdrawal_pressure_bp": 5000, "coordination_readiness_bp": 5000},
        "high_stress": {"liquid_resource_bp": 3000, "confidence_index_bp": 3000, "withdrawal_pressure_bp": 7000, "coordination_readiness_bp": 3000},
    }
    assert clamp_basis_points(-1) == 0
    assert clamp_basis_points(10_001) == 10_000
    assert resource_stress(3000) == 7000
    assert neighbor_stress({"a": 2500, "b": 2500}, {"a": 7000, "b": 3000}) == 2500
    assert next_withdrawal_pressure(5000, 5000, 2500, 1000) == 6625
    assert next_confidence(5000, 1000, 2000, 2500) == 3875


def test_synthetic_world_golden_is_deterministic() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    kwargs = {key: fixture[key] for key in ("profile_id", "world_entity_ids", "resource_owner_ids", "operational_entity_ids", "depositor_entity_id")}
    first = build_normalized_world(**kwargs)
    second = build_normalized_world(**kwargs)
    assert canonical_bytes(first) == canonical_bytes(second)
    resources = first["resources"]
    summary = {
        "entity_count": len(first["entities"]),
        "resource_count": len(resources),
        "relation_count": len(first["relations"]),
        "liquid_total_bp": sum(item["quantity"]["value"] for item in resources if item["resource_type"] == "liquid_resource_bp"),
        "derived_stress_total_bp": sum(item["quantity"]["value"] for item in resources if item["resource_type"] == "resource_stress_bp"),
        "operational_statuses": [item["runtime_value"]["value"] for item in first["process_states"]],
    }
    assert summary == fixture["expected"]
    assert validate_world(first, owners=fixture["resource_owner_ids"]) == []


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_allocation_is_conserved_bounded_and_order_invariant(seed: int) -> None:
    claims_a = {"intent.a": 5, "intent.b": 4, "intent.c": 3}
    claims_b = dict(reversed(tuple(claims_a.items())))
    first = pro_rata_floor_then_seeded_remainder(7, claims_a, run_seed=seed, logical_tick=4)
    second = pro_rata_floor_then_seeded_remainder(7, claims_b, run_seed=seed, logical_tick=4)
    assert first == second
    assert sum(first.values()) == 7
    assert all(0 <= first[key] <= claims_a[key] for key in first)


def test_zero_claim_is_not_ranked_for_remainder_allocation() -> None:
    claims = {"intent.zero": 0, "intent.a": 1, "intent.b": 1}
    allocation = pro_rata_floor_then_seeded_remainder(
        1, claims, run_seed=0, logical_tick=0
    )
    assert set(allocation) == set(claims)
    assert allocation["intent.zero"] == 0
    assert sum(allocation.values()) == 1
    assert all(0 <= allocation[key] <= claims[key] for key in claims)


def test_transfer_conservation_and_malformed_world_rejections() -> None:
    assert transfer_balances({"a": 6000, "b": 4000}, [("a", "b", 1500)]) == {"a": 4500, "b": 5500}
    with pytest.raises(ValueError, match="insufficient"):
        transfer_balances({"a": 1, "b": 1}, [("a", "b", 2)])
    with pytest.raises(ValueError, match="out_of_range"):
        resource_stress(10_001)
    with pytest.raises(ValueError, match="neighbor_universe"):
        neighbor_stress({"a": 1}, {"b": 1})
