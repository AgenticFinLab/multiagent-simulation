from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import pytest

from h2epr.agents import (
    IntentConformanceError,
    LifecycleConformanceError,
    MappingValidationError,
    load_executable_mapping,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BINDING_PATH = PROJECT_ROOT / "agents/bindings/panic_1907/binding.json"


def _mapping():
    return load_executable_mapping(BINDING_PATH)


def _support_request_parameters(**overrides):
    values = {
        "channel_id": "channel.nbc_mediated",
        "expiry_time": None,
        "qualitative_bound": "amount_unknown",
        "recipient_id": "new_york_clearing_house",
        "request_id": "request.kt.support.001",
        "resource_category_id": "resource.liquidity_support",
        "route_id": "route.nbc_mediated.nych",
        "withdrawal_condition_ids": ["condition.withdraw_if_channel_ends"],
    }
    values.update(overrides)
    return values


def _validate_support_request(parameters=None, **overrides):
    arguments = dict(
        actor_id="knickerbocker_trust",
        semantic_id="submit_support_request",
        commitment_ids=("DC-KT-02",),
        used_observations=(
            "asset_liquidity_assessment",
            "clearing_channel_status",
            "collateral_package_status",
            "corporate_authorization",
            "internal_liquidity_assessment",
            "support_request_status",
            "withdrawal_pressure",
        ),
        parameters=parameters or _support_request_parameters(),
        authority_refs=("authority.kt.support_request.001",),
        context={"package_material_exists": False},
    )
    arguments.update(overrides)
    return _mapping().validate_semantic_intent(**arguments)


def test_current_mapping_closes_reviewed_inventory() -> None:
    mapping = _mapping()
    assert mapping.mapping_profile_id == (
        "h2epr.agent-definition.mapping.0288.two-role.v0_2_1"
    )
    assert mapping.scenario_variant == "NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE"
    assert len(mapping.intents) == 21
    assert len(mapping.lifecycles.families) == 7
    assert set(mapping.participants) == {
        "knickerbocker_trust",
        "new_york_clearing_house",
    }
    assert len(mapping.participants["knickerbocker_trust"].intents) == 11
    assert len(mapping.participants["new_york_clearing_house"].intents) == 10


def test_machine_mapping_fails_after_reviewed_definition_drift(tmp_path: Path) -> None:
    copied_root = tmp_path / "h2epr"
    shutil.copytree(PROJECT_ROOT / "agents", copied_root / "agents")
    contract = PROJECT_ROOT / "contracts/v1/schemas/core/h2epr_core.schema.json"
    copied_contract = copied_root / "contracts/v1/schemas/core/h2epr_core.schema.json"
    copied_contract.parent.mkdir(parents=True)
    shutil.copy2(contract, copied_contract)
    definition = copied_root / "agents/defines/panic_1907/knickerbocker-trust.md"
    definition.write_text(
        definition.read_text(encoding="utf-8") + "\n<!-- drift -->\n",
        encoding="utf-8",
    )
    with pytest.raises(MappingValidationError, match="definition_sha256_mismatch"):
        load_executable_mapping(
            copied_root / "agents/bindings/panic_1907/binding.json",
            project_root=copied_root,
        )


def test_machine_registry_hash_is_bound_by_mapping(tmp_path: Path) -> None:
    copied_root = tmp_path / "h2epr"
    shutil.copytree(PROJECT_ROOT / "agents", copied_root / "agents")
    contract = PROJECT_ROOT / "contracts/v1/schemas/core/h2epr_core.schema.json"
    copied_contract = copied_root / "contracts/v1/schemas/core/h2epr_core.schema.json"
    copied_contract.parent.mkdir(parents=True)
    shutil.copy2(contract, copied_contract)
    registry = copied_root / "agents/bindings/panic_1907/intent-registry.json"
    value = json.loads(registry.read_text(encoding="utf-8"))
    value["actor_intent_counts"]["knickerbocker_trust"] = 12
    registry.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(
        MappingValidationError, match="machine_registry_sha256_mismatch:intent"
    ):
        load_executable_mapping(
            copied_root / "agents/bindings/panic_1907/binding.json",
            project_root=copied_root,
        )


def test_intent_cannot_introduce_hidden_participant_state(tmp_path: Path) -> None:
    copied_root = tmp_path / "h2epr"
    shutil.copytree(PROJECT_ROOT / "agents", copied_root / "agents")
    contract = PROJECT_ROOT / "contracts/v1/schemas/core/h2epr_core.schema.json"
    copied_contract = copied_root / "contracts/v1/schemas/core/h2epr_core.schema.json"
    copied_contract.parent.mkdir(parents=True)
    shutil.copy2(contract, copied_contract)

    registry = copied_root / "agents/bindings/panic_1907/intent-registry.json"
    registry_value = json.loads(registry.read_text(encoding="utf-8"))
    registry_value["intents"][0]["participant_state_inputs"] = [
        "hidden_backend_memory"
    ]
    registry.write_text(
        json.dumps(registry_value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    binding = copied_root / "agents/bindings/panic_1907/binding.json"
    binding_value = json.loads(binding.read_text(encoding="utf-8"))
    binding_value["machine_registries"]["intent"]["sha256"] = hashlib.sha256(
        registry.read_bytes()
    ).hexdigest()
    binding.write_text(
        json.dumps(binding_value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(
        MappingValidationError,
        match="intent_participant_state_outside_definition",
    ):
        load_executable_mapping(binding, project_root=copied_root)


def test_support_request_projects_each_semantic_value_once() -> None:
    projection = _validate_support_request()
    assert projection.target_entity_ids == ("new_york_clearing_house",)
    assert projection.claimed_authority_refs == (
        "authority.kt.support_request.001",
    )
    assert projection.expiry_time is None
    assert projection.resource_values == {
        "qualitative_bound": "amount_unknown",
        "resource_category_id": "resource.liquidity_support",
    }
    assert "recipient_id" not in projection.parameter_values
    assert "qualitative_bound" not in projection.parameter_values


def test_support_request_requires_exactly_one_quantity_representation() -> None:
    without_bound = _support_request_parameters()
    without_bound.pop("qualitative_bound")
    with pytest.raises(IntentConformanceError, match="conditional_exactly_one_group"):
        _validate_support_request(without_bound)

    conflicting = _support_request_parameters(
        requested_amount_value=100.0,
        requested_amount_unit="unit.usd",
    )
    with pytest.raises(IntentConformanceError, match="conditional_exactly_one_group"):
        _validate_support_request(conflicting)


def test_support_request_rejects_hidden_threshold_and_duplicate_ids() -> None:
    hidden = _support_request_parameters(hidden_pressure_threshold=0.7)
    with pytest.raises(
        IntentConformanceError,
        match="intent_parameters_undeclared:hidden_pressure_threshold",
    ):
        _validate_support_request(hidden)

    duplicate = _support_request_parameters(
        withdrawal_condition_ids=[
            "condition.withdraw_if_channel_ends",
            "condition.withdraw_if_channel_ends",
        ]
    )
    with pytest.raises(IntentConformanceError, match="invalid_stable_id_array"):
        _validate_support_request(duplicate)


def test_support_request_requires_scoped_authority() -> None:
    with pytest.raises(
        IntentConformanceError, match="claimed_authority_refs_missing"
    ):
        _validate_support_request(authority_refs=())


def test_policy_routing_observations_are_visible_and_participant_scoped() -> None:
    projection = _validate_support_request(
        used_observations=(
            "asset_liquidity_assessment",
            "clearing_channel_status",
            "collateral_package_status",
            "corporate_authorization",
            "delivered_disposition",
            "internal_liquidity_assessment",
            "support_request_status",
            "withdrawal_pressure",
        )
    )
    assert projection.definition.semantic_id == "submit_support_request"

    with pytest.raises(
        IntentConformanceError,
        match="observation_outside_participant_definition",
    ):
        _validate_support_request(
            used_observations=(
                "asset_liquidity_assessment",
                "clearing_channel_status",
                "collateral_package_status",
                "corporate_authorization",
                "hidden_world_balance",
                "internal_liquidity_assessment",
                "support_request_status",
                "withdrawal_pressure",
            )
        )


def test_intent_direct_observation_dependencies_must_be_consumed() -> None:
    with pytest.raises(
        IntentConformanceError,
        match="declared_intent_observation_not_used:withdrawal_pressure",
    ):
        _validate_support_request(
            used_observations=(
                "asset_liquidity_assessment",
                "clearing_channel_status",
                "collateral_package_status",
                "corporate_authorization",
                "internal_liquidity_assessment",
                "support_request_status",
            )
        )


def test_route_classification_requires_facility_only_for_facility_route() -> None:
    mapping = _mapping()
    base = {
        "case_id": "case.kt.001",
        "channel_id": "channel.nbc_mediated",
        "relationship_ref": "relationship.kt_nbc_nych.001",
        "represented_institution_id": "knickerbocker_trust",
        "route_class": "member_facility",
        "sender_id": "knickerbocker_trust",
        "source_request_id": "request.kt.support.001",
        "unresolved_field_ids": ["field.financial_information"],
    }
    kwargs = dict(
        actor_id="new_york_clearing_house",
        semantic_id="record_and_classify_request",
        commitment_ids=("DC-NYCH-01",),
        used_observations=(
            "delivered_request",
            "facility_eligibility",
            "relationship_status",
            "request_authorization_evidence",
            "route_classification",
        ),
        authority_refs=("authority.nych.intake.001",),
    )
    with pytest.raises(IntentConformanceError, match="facility_id"):
        mapping.validate_semantic_intent(parameters=base, **kwargs)

    valid = dict(base, facility_id="facility.nych.member_support")
    mapping.validate_semantic_intent(parameters=valid, **kwargs)

    wrong_scope = dict(valid, route_class="nonmember_clearing_matter")
    with pytest.raises(IntentConformanceError, match="conditional_parameter_forbidden"):
        mapping.validate_semantic_intent(parameters=wrong_scope, **kwargs)


@pytest.mark.parametrize(
    "semantic_id",
    ["seek_member_or_association_authorization", "propose_conditioned_measure"],
)
def test_alternative_route_intents_are_disabled_in_conservative_variant(
    semantic_id: str,
) -> None:
    with pytest.raises(IntentConformanceError, match="intent_disabled_by_scenario_variant"):
        _mapping().validate_semantic_intent(
            actor_id="new_york_clearing_house",
            semantic_id=semantic_id,
            commitment_ids=("DC-NYCH-04",),
            used_observations=("authority_state",),
            parameters={},
            authority_refs=("authority.nych.test",),
        )


def test_lifecycle_registry_accepts_only_named_transitions() -> None:
    lifecycles = _mapping().lifecycles
    lifecycles.assert_transition("support_request", "none", "prepared")
    lifecycles.assert_transition("support_request", "sent", "delivered")
    lifecycles.assert_transition("authorization", "pending", "authorized", track_id="corporate")
    with pytest.raises(LifecycleConformanceError, match="illegal_lifecycle_transition"):
        lifecycles.assert_transition("support_request", "none", "executed")
    with pytest.raises(LifecycleConformanceError, match="unknown_lifecycle_track"):
        lifecycles.assert_transition(
            "authorization", "pending", "authorized", track_id="unknown"
        )
