"""Pure normalized-world calculations for the architecture canary.

This module owns no live state.  It creates declarative initial values and
provides deterministic functions that a separately authorized reducer may use
later.
"""

from __future__ import annotations

import hashlib
from typing import Iterable, Mapping

from h2epr.artifacts.provenance import runtime_field, runtime_value


MIN_BP = 0
MAX_BP = 10_000
PROFILES = {
    "low_stress": {
        "liquid_resource_bp": 7000,
        "confidence_index_bp": 7000,
        "withdrawal_pressure_bp": 3000,
        "coordination_readiness_bp": 7000,
    },
    "balanced": {
        "liquid_resource_bp": 5000,
        "confidence_index_bp": 5000,
        "withdrawal_pressure_bp": 5000,
        "coordination_readiness_bp": 5000,
    },
    "high_stress": {
        "liquid_resource_bp": 3000,
        "confidence_index_bp": 3000,
        "withdrawal_pressure_bp": 7000,
        "coordination_readiness_bp": 3000,
    },
}


def clamp_basis_points(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("basis_points_must_be_integer")
    return min(MAX_BP, max(MIN_BP, value))


def resource_stress(liquid_resource: int) -> int:
    if not MIN_BP <= liquid_resource <= MAX_BP:
        raise ValueError("liquid_resource_out_of_range")
    return MAX_BP - liquid_resource


def neighbor_stress(
    exposure_weights: Mapping[str, int],
    neighbor_resource_stress: Mapping[str, int],
) -> int:
    if set(exposure_weights) != set(neighbor_resource_stress):
        raise ValueError("neighbor_universe_mismatch")
    total = 0
    for neighbor_id in sorted(exposure_weights):
        weight = exposure_weights[neighbor_id]
        stress = neighbor_resource_stress[neighbor_id]
        if not MIN_BP <= weight <= MAX_BP or not MIN_BP <= stress <= MAX_BP:
            raise ValueError("neighbor_value_out_of_range")
        total += weight * stress
    return total // MAX_BP


def next_withdrawal_pressure(
    current_withdrawal_pressure: int,
    confidence: int,
    observed_neighbor_stress: int,
    accepted_support: int,
) -> int:
    return clamp_basis_points(
        current_withdrawal_pressure
        + (MAX_BP - confidence) // 4
        + observed_neighbor_stress // 4
        - accepted_support // 4
    )


def next_confidence(
    current_confidence: int,
    accepted_support: int,
    unmet_withdrawal: int,
    observed_neighbor_stress: int,
) -> int:
    return clamp_basis_points(
        current_confidence
        + accepted_support // 2
        - unmet_withdrawal // 2
        - observed_neighbor_stress // 4
    )


def _allocation_rank(run_seed: int, logical_tick: int, intent_id: str) -> str:
    preimage = f"{run_seed}|resource_allocation|{logical_tick}|{intent_id}"
    return hashlib.sha256(preimage.encode("utf-8")).hexdigest()


def pro_rata_floor_then_seeded_remainder(
    available: int,
    claims: Mapping[str, int],
    *,
    run_seed: int,
    logical_tick: int,
) -> dict[str, int]:
    """Allocate a conserved integer amount independent of mapping order."""
    if isinstance(available, bool) or not isinstance(available, int) or available < 0:
        raise ValueError("invalid_available_resource")
    if isinstance(run_seed, bool) or not isinstance(run_seed, int):
        raise TypeError("run_seed_must_be_integer")
    if isinstance(logical_tick, bool) or not isinstance(logical_tick, int) or logical_tick < 0:
        raise ValueError("logical_tick_invalid")
    normalized = dict(claims)
    if len(normalized) != len(claims):
        raise ValueError("duplicate_intent_id")
    if any(not isinstance(key, str) or not key for key in normalized):
        raise ValueError("intent_id_invalid")
    if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in normalized.values()):
        raise ValueError("claim_amount_invalid")
    total_claim = sum(normalized.values())
    allocation_target = min(available, total_claim)
    if total_claim == 0:
        return {key: 0 for key in sorted(normalized)}
    if total_claim <= available:
        return {key: normalized[key] for key in sorted(normalized)}

    allocation = {
        key: allocation_target * normalized[key] // total_claim
        for key in sorted(normalized)
    }
    remainder = allocation_target - sum(allocation.values())
    ranked = sorted(
        (
            key
            for key in normalized
            if allocation[key] < normalized[key]
        ),
        key=lambda key: (_allocation_rank(run_seed, logical_tick, key), key),
    )
    for key in ranked[:remainder]:
        allocation[key] += 1
    if sum(allocation.values()) != allocation_target:
        raise AssertionError("allocation_conservation_failure")
    if any(allocation[key] > normalized[key] for key in allocation):
        raise AssertionError("allocation_exceeds_claim")
    return allocation


def transfer_balances(
    balances: Mapping[str, int], transfers: Iterable[tuple[str, str, int]]
) -> dict[str, int]:
    """Apply accepted transfers while enforcing exact global conservation."""
    result = dict(balances)
    before = sum(result.values())
    for source_id, target_id, amount in transfers:
        if source_id not in result or target_id not in result:
            raise ValueError("transfer_endpoint_unknown")
        if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
            raise ValueError("transfer_amount_invalid")
        if result[source_id] < amount:
            raise ValueError("insufficient_transfer_resource")
        result[source_id] -= amount
        result[target_id] += amount
    if sum(result.values()) != before:
        raise AssertionError("transfer_not_conserved")
    return result


def _resource(
    owner_id: str,
    resource_type: str,
    quantity: int,
    *,
    conservation_rule: str,
    visibility: str = "owner_private",
) -> dict:
    return {
        "resource_id": f"{owner_id}.{resource_type}",
        "resource_type": resource_type,
        "owner_entity_id": owner_id,
        "unit": "basis_points",
        "lower_bound": MIN_BP,
        "upper_bound": MAX_BP,
        "quantity": runtime_value(
            quantity,
            claim_ref_ids=(f"profile.{resource_type}",),
            visibility=("runtime_private" if visibility == "owner_private" else "runtime_system_only"),
            visibility_scope_ids=((owner_id,) if visibility == "owner_private" else ()),
            consumers=(owner_id, "world.reducer"),
        ),
        "visibility": visibility,
        "conservation_rule": conservation_rule,
        "state_version": 0,
    }


def build_normalized_world(
    profile_id: str,
    *,
    world_entity_ids: Iterable[str],
    resource_owner_ids: Iterable[str],
    operational_entity_ids: Iterable[str],
    depositor_entity_id: str,
) -> dict:
    if profile_id not in PROFILES:
        raise ValueError("unknown_world_profile")
    profile = PROFILES[profile_id]
    entities = tuple(sorted(set(world_entity_ids)))
    owners = tuple(sorted(set(resource_owner_ids)))
    operational = tuple(sorted(set(operational_entity_ids)))
    if depositor_entity_id not in entities or not set(owners).issubset(entities):
        raise ValueError("world_entity_universe_mismatch")

    resources: list[dict] = []
    for owner_id in owners:
        liquid = profile["liquid_resource_bp"]
        resources.extend(
            [
                _resource(owner_id, "liquid_resource_bp", liquid, conservation_rule="conserved"),
                _resource(owner_id, "confidence_index_bp", profile["confidence_index_bp"], conservation_rule="nonconserved_index"),
                _resource(owner_id, "withdrawal_pressure_bp", profile["withdrawal_pressure_bp"], conservation_rule="nonconserved_index"),
                _resource(owner_id, "coordination_readiness_bp", profile["coordination_readiness_bp"], conservation_rule="nonconserved_index"),
                _resource(owner_id, "resource_stress_bp", resource_stress(liquid), conservation_rule="nonconserved_index", visibility="restricted"),
            ]
        )
    resources.append(
        _resource(
            depositor_entity_id,
            "withdrawal_demand_bp",
            profile["withdrawal_pressure_bp"],
            conservation_rule="nonconserved_index",
        )
    )

    relations = []
    for source_id in owners:
        for target_id in owners:
            if source_id == target_id:
                continue
            relations.append(
                runtime_field(
                    f"stress.exposure.{source_id}.{target_id}",
                    2500,
                    claim_ref_ids=("p006.artificial.equal.weight.graph",),
                    consumers=("world.reducer",),
                )
            )
    process_states = [
        runtime_field(
            f"operational.status.{entity_id}",
            "open",
            claim_ref_ids=("p006.initial.operational.status",),
            consumers=(entity_id, "world.reducer"),
        )
        for entity_id in operational
    ]
    world = {
        "state_version": 0,
        "entities": list(entities),
        "resources": resources,
        "relations": relations,
        "commitments": [],
        "risks": [
            runtime_field(
                "canary.profile",
                profile_id,
                claim_ref_ids=("p006.sensitivity.profile",),
                consumers=("world.reducer",),
            )
        ],
        "access_grants": [],
        "public_signals": [
            runtime_field(
                "system.stress.signal",
                profile_id,
                claim_ref_ids=("p006.public.signal.assumption",),
                visibility="runtime_public",
                consumers=("participant.runtime", "world.reducer"),
            )
        ],
        "process_states": process_states,
    }
    errors = validate_world(world, owners=owners)
    if errors:
        raise ValueError("invalid_normalized_world:" + ",".join(errors))
    return world


def validate_world(world: dict, *, owners: Iterable[str]) -> list[str]:
    errors: list[str] = []
    resource_ids: set[str] = set()
    by_owner_type: dict[tuple[str, str], int] = {}
    for resource in world.get("resources", []):
        resource_id = resource.get("resource_id")
        if resource_id in resource_ids:
            errors.append("DUPLICATE_RESOURCE_ID")
        resource_ids.add(resource_id)
        quantity = resource.get("quantity", {}).get("value")
        if isinstance(quantity, bool) or not isinstance(quantity, int) or not MIN_BP <= quantity <= MAX_BP:
            errors.append("RESOURCE_OUT_OF_RANGE")
        by_owner_type[(resource.get("owner_entity_id"), resource.get("resource_type"))] = quantity
    for owner_id in owners:
        liquid = by_owner_type.get((owner_id, "liquid_resource_bp"))
        stress = by_owner_type.get((owner_id, "resource_stress_bp"))
        if liquid is None or stress != MAX_BP - liquid:
            errors.append("DERIVED_STRESS_MISMATCH")
    return errors
