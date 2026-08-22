from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from h2epr.agents import (
    RosterMappingError,
    expected_roster_idempotency_key,
    load_roster_mapping_profile,
)
from h2epr.artifacts.provenance import runtime_field
from support.schema_registry import definition_errors


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = (
    PROJECT_ROOT
    / "agents/bindings/panic_1907/roster-v0.1/mapping-profile.json"
)
RELEASE_MANIFEST_PATH = (
    PROJECT_ROOT / "releases/panic_1907/roster-definition-v0.1/manifest.json"
)
ACCEPTED_MAPPING_MANIFEST_PATH = (
    PROJECT_ROOT / "agents/bindings/panic_1907/consolidated/manifest.json"
)


def _profile():
    return load_roster_mapping_profile(PROFILE_PATH)


def _copy_profile_inputs(tmp_path: Path) -> tuple[Path, Path]:
    copied_root = tmp_path / "h2epr"
    source_manifest = json.loads(RELEASE_MANIFEST_PATH.read_text(encoding="utf-8"))
    accepted_manifest = json.loads(
        ACCEPTED_MAPPING_MANIFEST_PATH.read_text(encoding="utf-8")
    )
    relative_paths = {
        PROFILE_PATH.relative_to(PROJECT_ROOT),
        RELEASE_MANIFEST_PATH.relative_to(PROJECT_ROOT),
        ACCEPTED_MAPPING_MANIFEST_PATH.relative_to(PROJECT_ROOT),
        Path(accepted_manifest["source_release"]["checksums_path"]),
        Path(accepted_manifest["owner_decision"]["path"]),
    }
    relative_paths.update(
        Path(item["path"])
        for key in ("agent_definitions", "population_models")
        for item in source_manifest[key]
    )
    relative_paths.update(
        ACCEPTED_MAPPING_MANIFEST_PATH.parent.relative_to(PROJECT_ROOT)
        / item["path"]
        for item in accepted_manifest["artifacts"]
    )
    for relative in sorted(relative_paths):
        source = PROJECT_ROOT / relative
        target = copied_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return copied_root, copied_root / PROFILE_PATH.relative_to(PROJECT_ROOT)


def _mutate_profile(tmp_path: Path, mutation) -> tuple[Path, Path]:
    copied_root, copied_profile = _copy_profile_inputs(tmp_path)
    value = json.loads(copied_profile.read_text(encoding="utf-8"))
    mutation(value)
    copied_profile.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return copied_root, copied_profile


def test_roster_loader_hash_checks_and_derives_complete_inventory() -> None:
    profile = _profile()

    assert profile.profile_id == "h2epr.roster-consolidated-mapping.v0_1"
    assert profile.source_release_id == "H2EPR-0288-ROSTER-DEFINITION-RELEASE-v0.1"
    assert profile.accepted_mapping_id == "H2EPR-0288-CONSOLIDATED-MAPPING-v0.1"
    assert len(profile.products) == 12
    assert len(profile.capabilities) == 12
    assert profile.commitment_count == 62
    assert profile.observation_count == 115
    assert profile.distinct_reader_observation_count == 103
    assert profile.intent_count == 107
    assert profile.distinct_reader_intent_count == 98
    assert len({item.field_name for item in profile.observations.values()}) == 115
    assert len({item.action_type for item in profile.intents.values()}) == 107


def test_reader_name_collisions_remain_capability_qualified() -> None:
    profile = _profile()
    placements = sorted(
        (
            item
            for item in profile.intents.values()
            if item.reader_intent_id == "request_case_information"
        ),
        key=lambda item: item.capability_id,
    )
    assert len(placements) == 3
    assert len({item.action_type for item in placements}) == 3
    assert {
        item.capability_id for item in placements
    } == {
        "j_pierpont_morgan",
        "new_york_clearing_house",
        "trust_presidents_committee",
    }


def test_all_derived_action_identity_surfaces_fit_the_v1_carrier() -> None:
    profile = _profile()
    for placement in profile.intents.values():
        capability = profile.capabilities[placement.capability_id]
        candidate = {
            "action_type": placement.action_type,
            "version": placement.action_schema_version,
            "allowed_representation_classes": list(
                capability.representation_classes
            ),
            "parameter_names": [],
            "state_changing": False,
            "review_state": "reviewed",
        }
        assert definition_errors("ActionDefinition", candidate) == []


def test_all_derived_observation_names_fit_the_v1_runtime_field_carrier() -> None:
    profile = _profile()
    for placement in profile.observations.values():
        field = runtime_field(
            placement.field_name,
            "synthetic_conformance_value",
            source_ref_id="fixture.roster_mapping.observation",
            claim_ref_ids=("fixture.synthetic.conformance_only",),
            visibility="runtime_private",
            visibility_scope_ids=("actor.synthetic.conformance",),
            consumers=("participant.runtime",),
        )
        payload = {
            "observation_id": (
                f"observation.0288.{placement.capability_id}."
                f"{placement.reader_observation_id}.001"
            ),
            "fields": [field],
        }
        assert definition_errors("ObservationPayload", payload) == []


def test_multi_capability_institution_has_one_actor_and_resource_owner() -> None:
    profile = _profile()
    actor = profile.actor("actor.member_bank_alpha")
    units = [
        unit
        for unit in profile.fixture.population_units.values()
        if unit.actor_id == actor.actor_id
    ]

    assert actor.capability_ids == (
        "bank_resource_decision",
        "call_money_lender",
    )
    assert len(actor.observation_field_names) == 22
    assert len(actor.action_types) == 16
    assert len({unit.resource_owner_id for unit in units}) == 1
    assert {unit.resource_owner_id for unit in units} == {actor.resource_owner_id}
    assert len({unit.private_state_owner_id for unit in units}) == 2


def test_host_scoped_depositor_keeps_private_scope_and_separate_owner() -> None:
    profile = _profile()
    case = profile.fixture.observation_cases[
        "observation_case.knickerbocker_depositor.access.001"
    ]
    unit = profile.fixture.population_units[
        "unit.depositor.knickerbocker.cohort_a"
    ]

    assert case.host_entity_id == "entity.knickerbocker_trust"
    assert unit.host_entity_id == case.host_entity_id
    assert case.visibility == "runtime_private"
    assert case.visibility_scope_ids == (unit.actor_id,)
    assert case.field_name == (
        "obs.knickerbocker_depositor.service_access_observation"
    )
    assert unit.resource_owner_id != case.host_entity_id


def test_broker_funding_lifecycle_replays_with_distinct_result_layers() -> None:
    profile = _profile()
    lifecycle = profile.fixture.funding_lifecycle
    action_events = [event for event in lifecycle.events if event.trigger == "action"]

    assert lifecycle.initial_state == "draft"
    assert lifecycle.initial_version == 0
    assert lifecycle.final_state == "closed"
    assert lifecycle.final_version == 12
    assert {event.capability_id for event in action_events} == {
        "call_money_broker_borrower",
        "call_money_lender",
    }
    for event in action_events:
        actor = profile.actor(event.actor_id)
        authority = profile.fixture.authority_records[event.authority_refs[0]]
        assert event.action_type in actor.action_types
        assert authority.actor_id == event.actor_id
        assert authority.capability_id == event.capability_id
        assert authority.reader_intent_id == event.reader_intent_id
        assert authority.target_actor_ids == event.target_actor_ids
        assert authority.resource_owner_id == event.resource_owner_id
        assert event.action_intent_id != event.action_disposition_id
        assert event.action_disposition_id != event.business_result_id
        assert event.action_intent_id != event.business_result_id
        assert event.idempotency_key == expected_roster_idempotency_key(
            profile.profile_id,
            lifecycle.object_id,
            event.before_version,
            event.actor_id,
            event.action_type,
            event.target_actor_ids,
            event.material_parameters,
        )


def test_profile_and_fixture_identity_are_deterministic() -> None:
    first = _profile()
    second = _profile()

    assert first.profile_sha256 == second.profile_sha256
    assert first.fixture.identity_sha256 == second.fixture.identity_sha256
    assert first.fixture.funding_lifecycle == second.fixture.funding_lifecycle


def test_fixture_identity_covers_observations_and_lifecycle(tmp_path: Path) -> None:
    baseline = _profile().fixture.identity_sha256

    def observation_mutation(value):
        value["conformance_fixture"]["observation_cases"][0][
            "freshness"
        ] = "recent_for_decision"

    observation_root, observation_profile = _mutate_profile(
        tmp_path / "observation", observation_mutation
    )
    observation_identity = load_roster_mapping_profile(
        observation_profile, project_root=observation_root
    ).fixture.identity_sha256

    def lifecycle_mutation(value):
        value["conformance_fixture"]["funding_lifecycle"]["events"][0][
            "material_parameters"
        ]["request_id"] = "funding_request.broker_alpha.002"

    lifecycle_root, lifecycle_profile = _mutate_profile(
        tmp_path / "lifecycle", lifecycle_mutation
    )
    lifecycle_identity = load_roster_mapping_profile(
        lifecycle_profile, project_root=lifecycle_root
    ).fixture.identity_sha256

    assert observation_identity != baseline
    assert lifecycle_identity != baseline
    assert observation_identity != lifecycle_identity


def test_source_product_byte_drift_fails_closed(tmp_path: Path) -> None:
    copied_root, copied_profile = _copy_profile_inputs(tmp_path)
    product = copied_root / "agents/defines/panic_1907/knickerbocker-trust.md"
    product.write_text(product.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    with pytest.raises(
        RosterMappingError, match="source_product_sha256_mismatch"
    ):
        load_roster_mapping_profile(copied_profile, project_root=copied_root)


def test_accepted_mapping_artifact_byte_drift_fails_closed(tmp_path: Path) -> None:
    copied_root, copied_profile = _copy_profile_inputs(tmp_path)
    artifact = (
        copied_root
        / "agents/bindings/panic_1907/consolidated/mapping-specification.md"
    )
    artifact.write_text(
        artifact.read_text(encoding="utf-8") + "\n", encoding="utf-8"
    )

    with pytest.raises(
        RosterMappingError,
        match="accepted_mapping_artifact_sha256_mismatch:mapping_specification",
    ):
        load_roster_mapping_profile(copied_profile, project_root=copied_root)


def test_declared_inventory_drift_fails_closed(tmp_path: Path) -> None:
    def mutation(value):
        capability = next(
            item
            for item in value["capabilities"]
            if item["capability_id"] == "national_bank_of_commerce"
        )
        capability["expected_intents"] = 14

    copied_root, copied_profile = _mutate_profile(tmp_path, mutation)
    with pytest.raises(RosterMappingError, match="capability_inventory_mismatch"):
        load_roster_mapping_profile(copied_profile, project_root=copied_root)


def test_duplicate_actor_for_one_entity_fails_closed(tmp_path: Path) -> None:
    def mutation(value):
        actors = value["conformance_fixture"]["actors"]
        actors[0]["entity_id"] = actors[-1]["entity_id"]

    copied_root, copied_profile = _mutate_profile(tmp_path, mutation)
    with pytest.raises(RosterMappingError, match="duplicate_actor_for_entity"):
        load_roster_mapping_profile(copied_profile, project_root=copied_root)


def test_population_resource_owner_drift_fails_closed(tmp_path: Path) -> None:
    def mutation(value):
        unit = next(
            item
            for item in value["conformance_fixture"]["population_units"]
            if item["unit_id"] == "unit.call_money_lender.member_bank_alpha"
        )
        unit["resource_owner_id"] = "entity.resource_shadow"

    copied_root, copied_profile = _mutate_profile(tmp_path, mutation)
    with pytest.raises(RosterMappingError, match="population_resource_owner_mismatch"):
        load_roster_mapping_profile(copied_profile, project_root=copied_root)


def test_private_observation_scope_drift_fails_closed(tmp_path: Path) -> None:
    def mutation(value):
        case = value["conformance_fixture"]["observation_cases"][0]
        case["visibility_scope_ids"] = ["actor.knickerbocker_trust"]

    copied_root, copied_profile = _mutate_profile(tmp_path, mutation)
    with pytest.raises(RosterMappingError, match="private_observation_scope_mismatch"):
        load_roster_mapping_profile(copied_profile, project_root=copied_root)


def test_authority_scope_drift_fails_closed(tmp_path: Path) -> None:
    def mutation(value):
        authority = next(
            item
            for item in value["conformance_fixture"]["authority_records"]
            if item["authority_ref"] == "authority.member_bank_alpha.lending.001"
        )
        authority["target_actor_ids"] = ["actor.knickerbocker_trust"]

    copied_root, copied_profile = _mutate_profile(tmp_path, mutation)
    with pytest.raises(RosterMappingError, match="lifecycle_authority_scope_mismatch"):
        load_roster_mapping_profile(copied_profile, project_root=copied_root)


def test_lifecycle_version_gap_fails_closed(tmp_path: Path) -> None:
    def mutation(value):
        event = value["conformance_fixture"]["funding_lifecycle"]["events"][5]
        event["after_version"] = 8

    copied_root, copied_profile = _mutate_profile(tmp_path, mutation)
    with pytest.raises(RosterMappingError, match="lifecycle_transition_invalid"):
        load_roster_mapping_profile(copied_profile, project_root=copied_root)
