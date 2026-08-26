"""Closed validation profile for explicit semantic Scenario Configurations."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from .errors import ConfigurationErrorCode
from .loader import (
    _ReleaseContext,
    _SEMANTIC_CONFIGURATION_INPUT_SPECS,
    _array,
    _duplicates,
    _object,
    _raise,
    _read_json,
    _resolved_file,
    _sha256,
    _sha256_file,
    _string,
    _value_type,
)


@dataclass(frozen=True)
class _SemanticReferenceProfile:
    event_id: str
    roster_release_id: str
    mapping_release_id: str
    mapping_profile_id: str
    products: Mapping[str, str]
    capabilities: frozenset[str]
    mapping_coverage: Mapping[str, int]


_SEMANTIC_VARIANT_MATERIALIZATION_FIELDS = {
    "attack_pressure": "attack_pressure_profile",
    "route_and_delivery": "route_delivery_profile",
    "responsibility_units": "active_population_actor_ids",
    "office_capacity": "office_capacity_profile",
    "technical_result": "technical_result_profile",
    "notification": "notification_profile",
}


def _load_semantic_reference_profile(
    root: Path,
    document: Mapping[str, Any],
    configuration_manifest: Mapping[str, Any],
    release: _ReleaseContext,
) -> _SemanticReferenceProfile:
    semantic = document["semantic_inputs"]
    roster_path = release.semantic_input_paths["roster_definition_release"]
    roster, _ = _read_json(roster_path, pointer="/semantic_references/roster")
    if (
        roster.get("schema") != "h2epr.roster-definition-release.v0_1"
        or roster.get("status") != "accepted_semantic_release"
        or roster.get("integrity_algorithm") != "sha256"
    ):
        _raise(
            ConfigurationErrorCode.MAPPING_PROFILE_INVALID,
            pointer="/semantic_references/roster",
            detail="accepted_roster_release_required",
        )
    roster_release_id = _string(
        roster.get("release_id"), pointer="/semantic_references/roster/release_id"
    )
    if (
        roster_release_id != semantic["roster_release_id"]
        or roster.get("event_id") != document["event_id"]
    ):
        _raise(
            ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
            pointer="/semantic_inputs/roster_release_id",
            detail="roster_release_identity_mismatch",
        )

    products: dict[str, str] = {}
    for collection, product_kind in (
        ("agent_definitions", "agent_definition"),
        ("population_models", "population_model"),
    ):
        rows = _array(
            roster.get(collection),
            pointer=f"/semantic_references/roster/{collection}",
        )
        for index, raw in enumerate(rows):
            pointer = f"/semantic_references/roster/{collection}/{index}"
            item = _object(raw, pointer=pointer)
            if set(item) != {"id", "version", "path", "sha256"}:
                _raise(
                    ConfigurationErrorCode.MAPPING_PROFILE_INVALID,
                    pointer=pointer,
                    detail="released_product_fields_mismatch",
                )
            product_id = _string(item.get("id"), pointer=f"{pointer}/id")
            if product_id in products:
                _raise(
                    ConfigurationErrorCode.MAPPING_PROFILE_INVALID,
                    pointer=f"{pointer}/id",
                    detail="duplicate_released_product",
                )
            product_path = _resolved_file(
                root,
                root,
                item.get("path"),
                pointer=f"{pointer}/path",
            )
            product_sha256 = _sha256(
                item.get("sha256"), pointer=f"{pointer}/sha256"
            )
            if _sha256_file(product_path) != product_sha256:
                _raise(
                    ConfigurationErrorCode.INTEGRITY_MISMATCH,
                    pointer=pointer,
                    detail="released_product_sha256_mismatch",
                )
            products[product_id] = product_kind

    mapping_path = release.semantic_input_paths["consolidated_mapping"]
    mapping, _ = _read_json(mapping_path, pointer="/semantic_references/mapping")
    if (
        mapping.get("schema") != "h2epr.consolidated-mapping-release.v0_1"
        or mapping.get("status") != "accepted_design_specification"
        or mapping.get("integrity_algorithm") != "sha256"
    ):
        _raise(
            ConfigurationErrorCode.MAPPING_PROFILE_INVALID,
            pointer="/semantic_references/mapping",
            detail="accepted_mapping_release_required",
        )
    mapping_release_id = _string(
        mapping.get("release_id"),
        pointer="/semantic_references/mapping/release_id",
    )
    if (
        mapping_release_id != semantic["consolidated_mapping_release_id"]
        or mapping.get("event_id") != document["event_id"]
    ):
        _raise(
            ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
            pointer="/semantic_inputs/consolidated_mapping_release_id",
            detail="mapping_release_identity_mismatch",
        )

    source_release = _object(
        mapping.get("source_release"),
        pointer="/semantic_references/mapping/source_release",
    )
    expected_agent_count = sum(
        kind == "agent_definition" for kind in products.values()
    )
    expected_population_count = sum(
        kind == "population_model" for kind in products.values()
    )
    expected_source = {
        "release_id": roster_release_id,
        "manifest_sha256": release.semantic_input_sha256s[
            "roster_definition_release"
        ],
        "semantic_products": len(products),
        "agent_definitions": expected_agent_count,
        "population_models": expected_population_count,
    }
    for name, expected in expected_source.items():
        if source_release.get(name) != expected:
            _raise(
                ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
                pointer=f"/semantic_references/mapping/source_release/{name}",
                detail="mapping_source_release_mismatch",
            )

    coverage_raw = _object(
        mapping.get("coverage"), pointer="/semantic_references/mapping/coverage"
    )
    expected_coverage_fields = {
        "decision_and_population_commitments",
        "observation_placements",
        "private_state_placements",
        "intent_placements",
        "lifecycle_families",
        "cross_object_rules",
    }
    if set(coverage_raw) != expected_coverage_fields:
        _raise(
            ConfigurationErrorCode.MAPPING_PROFILE_INVALID,
            pointer="/semantic_references/mapping/coverage",
            detail="mapping_coverage_fields_mismatch",
        )
    mapping_coverage: dict[str, int] = {}
    for name, value in coverage_raw.items():
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            _raise(
                ConfigurationErrorCode.MAPPING_PROFILE_INVALID,
                pointer=f"/semantic_references/mapping/coverage/{name}",
                detail="nonnegative_integer_required",
            )
        mapping_coverage[name] = value

    mapping_profile_items = [
        _object(raw, pointer=f"/semantic_references/mapping/artifacts/{index}")
        for index, raw in enumerate(
            _array(
                mapping.get("artifacts"),
                pointer="/semantic_references/mapping/artifacts",
            )
        )
        if isinstance(raw, dict) and raw.get("kind") == "mapping_specification"
    ]
    if len(mapping_profile_items) != 1:
        _raise(
            ConfigurationErrorCode.MAPPING_PROFILE_INVALID,
            pointer="/semantic_references/mapping/artifacts",
            detail="one_mapping_specification_required",
        )
    mapping_profile_item = mapping_profile_items[0]
    if mapping_profile_item.get("sha256") != release.semantic_input_sha256s[
        "mapping_profile"
    ]:
        _raise(
            ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
            pointer="/semantic_inputs/mapping_profile_sha256",
            detail="mapping_artifact_sha256_mismatch",
        )

    try:
        mapping_profile_text = release.mapping_profile_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        _raise(
            ConfigurationErrorCode.MAPPING_PROFILE_INVALID,
            pointer="/semantic_references/mapping_profile",
            detail="utf8_required",
        )
    mapping_lines = mapping_profile_text.splitlines()
    table_headers = [
        index
        for index, line in enumerate(mapping_lines)
        if line.strip() == "| Released capability | Required assembly pattern |"
    ]
    if len(table_headers) != 1:
        _raise(
            ConfigurationErrorCode.MAPPING_PROFILE_INVALID,
            pointer="/semantic_references/mapping_profile",
            detail="one_released_capability_table_required",
        )
    table_index = table_headers[0]
    if (
        table_index + 2 >= len(mapping_lines)
        or not mapping_lines[table_index + 1].startswith("|---")
    ):
        _raise(
            ConfigurationErrorCode.MAPPING_PROFILE_INVALID,
            pointer="/semantic_references/mapping_profile",
            detail="released_capability_table_header_invalid",
        )
    capabilities: set[str] = set()
    row_index = table_index + 2
    while row_index < len(mapping_lines) and mapping_lines[row_index].startswith("|"):
        cells = [
            cell.strip()
            for cell in mapping_lines[row_index].strip("|").split("|")
        ]
        if len(cells) != 2 or re.fullmatch(r"`[a-z][a-z0-9_]*`", cells[0]) is None:
            _raise(
                ConfigurationErrorCode.MAPPING_PROFILE_INVALID,
                pointer="/semantic_references/mapping_profile",
                detail=f"released_capability_row_invalid={row_index + 1}",
            )
        capability_id = cells[0][1:-1]
        if capability_id in capabilities or not cells[1]:
            _raise(
                ConfigurationErrorCode.MAPPING_PROFILE_INVALID,
                pointer="/semantic_references/mapping_profile",
                detail="released_capability_row_duplicate_or_empty",
            )
        capabilities.add(capability_id)
        row_index += 1
    if len(capabilities) != len(products):
        _raise(
            ConfigurationErrorCode.MAPPING_PROFILE_INVALID,
            pointer="/semantic_references/mapping_profile",
            detail="released_product_capability_count_mismatch",
        )

    manifest_semantic = _object(
        configuration_manifest.get("semantic_inputs"),
        pointer="/release_manifest/semantic_inputs",
    )
    mapping_profile_release = _object(
        manifest_semantic.get("mapping_profile"),
        pointer="/release_manifest/semantic_inputs/mapping_profile",
    )
    mapping_profile_id = _string(
        mapping_profile_release.get("id"),
        pointer="/release_manifest/semantic_inputs/mapping_profile/id",
    )
    if mapping_profile_id != semantic["mapping_profile_id"]:
        _raise(
            ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
            pointer="/semantic_inputs/mapping_profile_id",
            detail="mapping_profile_identity_mismatch",
        )
    return _SemanticReferenceProfile(
        event_id=document["event_id"],
        roster_release_id=roster_release_id,
        mapping_release_id=mapping_release_id,
        mapping_profile_id=mapping_profile_id,
        products=MappingProxyType(products),
        capabilities=frozenset(capabilities),
        mapping_coverage=MappingProxyType(mapping_coverage),
    )


def _validate_semantic_release_document_consistency(
    document: Mapping[str, Any],
    manifest: Mapping[str, Any],
    release: _ReleaseContext,
) -> None:
    clock = document["clock"]
    expected_metadata = {
        "id": document["configuration_id"],
        "version": document["version"],
        "purpose": document["purpose"],
        "timezone": clock["timezone"],
        "modeled_start": clock["modeled_start"],
        "participant_response_start": clock["participant_response_start"][
            "value"
        ],
        "acute_window": (
            f"{clock['acute_window']['start']}/{clock['acute_window']['end']}"
        ),
        "core_horizon": clock["core_horizon"]["value"],
        "notification_observation_horizon": clock[
            "notification_observation_horizon"
        ]["value"],
        "execution_eligible": document["execution_boundary"]["execution_eligible"],
        "historical_calibration": document["historical_calibration"],
        "historical_validation": document["historical_validation"],
        "known_outcome_fitting": document["known_outcome_fitting"],
    }
    metadata = _object(
        manifest.get("configuration"), pointer="/release_manifest/configuration"
    )
    for name, expected in expected_metadata.items():
        if metadata.get(name) != expected:
            _raise(
                ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
                pointer=f"/release_manifest/configuration/{name}",
                detail="configuration_metadata_mismatch",
            )
    if manifest.get("event_id") != document["event_id"]:
        _raise(
            ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
            pointer="/event_id",
            detail="release_event_id_mismatch",
        )
    if manifest.get("status") != document["status"]:
        _raise(
            ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
            pointer="/status",
            detail="release_status_mismatch",
        )

    semantic = document["semantic_inputs"]
    manifest_semantic = manifest["semantic_inputs"]
    identity_fields = {
        "scenario_definition_release_id": (
            "scenario_definition_release",
            "release_id",
        ),
        "scenario_definition_id": ("scenario_definition", "id"),
        "roster_release_id": ("roster_definition_release", "release_id"),
        "consolidated_mapping_release_id": (
            "consolidated_mapping",
            "release_id",
        ),
        "mapping_profile_id": ("mapping_profile", "id"),
    }
    for configuration_key, (input_name, manifest_key) in identity_fields.items():
        if semantic[configuration_key] != manifest_semantic[input_name].get(
            manifest_key
        ):
            _raise(
                ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
                pointer=f"/semantic_inputs/{configuration_key}",
                detail=f"release_input={input_name}",
            )
    for name, (_, _, configuration_key) in (
        _SEMANTIC_CONFIGURATION_INPUT_SPECS.items()
    ):
        if configuration_key is None:
            continue
        if semantic[configuration_key] != release.semantic_input_sha256s[name]:
            _raise(
                ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
                pointer=f"/semantic_inputs/{configuration_key}",
                detail=f"release_input={name}",
            )

    owner = _object(
        manifest.get("owner_decision"), pointer="/release_manifest/owner_decision"
    )
    if owner.get("resolved_items") != document["owner_decisions"]:
        _raise(
            ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
            pointer="/owner_decisions",
            detail="owner_decision_coverage_mismatch",
        )
    execution = _object(
        manifest.get("execution_boundary"),
        pointer="/release_manifest/execution_boundary",
    )
    expected_execution = {
        "execution_eligible": document["execution_boundary"]["execution_eligible"],
        "admission_status": "not_admitted",
        "unbound_policy_count": len(document["policy_selections"]),
        "authorization_conferred_by_release": "configuration_semantics_only",
        "required_before_execution": document["execution_boundary"][
            "required_before_execution"
        ],
    }
    for name, expected in expected_execution.items():
        if execution.get(name) != expected:
            _raise(
                ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
                pointer=f"/release_manifest/execution_boundary/{name}",
                detail="configuration_execution_boundary_mismatch",
            )


def _indexed_rows(
    rows: Sequence[Mapping[str, Any]],
    key: str,
    *,
    pointer: str,
) -> dict[str, Mapping[str, Any]]:
    values = [row[key] for row in rows]
    duplicates = _duplicates(values)
    if duplicates:
        _raise(
            ConfigurationErrorCode.ASSEMBLY_INVALID,
            pointer=pointer,
            detail=f"duplicate_{key}=" + ",".join(sorted(duplicates)),
        )
    return {row[key]: row for row in rows}


def _require_references(
    values: Sequence[str] | set[str],
    known: set[str],
    *,
    pointer: str,
    detail: str,
) -> None:
    missing = set(values) - known
    if missing:
        _raise(
            ConfigurationErrorCode.REFERENCE_UNRESOLVED,
            pointer=pointer,
            detail=f"{detail}=" + ",".join(sorted(missing)),
        )


def _validate_semantic_configuration(
    document: Mapping[str, Any],
    profile: _SemanticReferenceProfile,
    release_coverage: Mapping[str, int],
) -> tuple[Mapping[str, int], tuple[str, ...]]:
    if profile.event_id != document["event_id"]:
        _raise(
            ConfigurationErrorCode.SEMANTIC_INPUT_MISMATCH,
            pointer="/event_id",
            detail="semantic_reference_event_mismatch",
        )

    institutions = document["canonical_institutions"]
    institution_by_id = _indexed_rows(
        institutions, "id", pointer="/canonical_institutions"
    )
    institution_ids = set(institution_by_id)
    resource_owner_ids = [row["resource_owner_id"] for row in institutions]
    if _duplicates(resource_owner_ids):
        _raise(
            ConfigurationErrorCode.ASSEMBLY_INVALID,
            pointer="/canonical_institutions",
            detail="resource_owner_reused",
        )
    resource_owner_by_institution = {
        row["id"]: row["resource_owner_id"] for row in institutions
    }

    processes = document["scenario_processes"]
    process_ids = set(processes)
    if len(process_ids) != len(processes):
        _raise(
            ConfigurationErrorCode.ASSEMBLY_INVALID,
            pointer="/scenario_processes",
            detail="duplicate_process_id",
        )

    named = document["named_actors"]
    populations = document["population_actors"]
    actors = [*named, *populations]
    actor_by_id = _indexed_rows(actors, "actor_id", pointer="/actors")
    actor_ids = set(actor_by_id)
    for field in ("entity_id", "authority_graph_id"):
        duplicates = _duplicates([row[field] for row in actors])
        if duplicates:
            _raise(
                ConfigurationErrorCode.ASSEMBLY_INVALID,
                pointer=f"/actors/{field}",
                detail="duplicate=" + ",".join(sorted(duplicates)),
            )

    expected_agent_products = {
        product_id
        for product_id, kind in profile.products.items()
        if kind == "agent_definition"
    }
    expected_population_products = set(profile.products) - expected_agent_products
    named_product_ids = [row["participant_product_id"] for row in named]
    if set(named_product_ids) != expected_agent_products or _duplicates(
        named_product_ids
    ):
        _raise(
            ConfigurationErrorCode.ASSEMBLY_INVALID,
            pointer="/named_actors",
            detail="agent_product_coverage_mismatch",
        )
    named_capability_ids = [row["capability_id"] for row in named]
    if _duplicates(named_capability_ids):
        _raise(
            ConfigurationErrorCode.ASSEMBLY_INVALID,
            pointer="/named_actors",
            detail="named_capability_reused",
        )

    capacity_ids: set[str] = set()
    capability_by_actor: dict[str, str] = {}
    for index, actor in enumerate(named):
        pointer = f"/named_actors/{index}"
        primary = actor["primary_institution_id"]
        route_institutions = actor["additional_route_institution_ids"]
        _require_references(
            [primary, *route_institutions],
            institution_ids,
            pointer=pointer,
            detail="institution_unresolved",
        )
        if actor["resource_owner_id"] != resource_owner_by_institution[primary]:
            _raise(
                ConfigurationErrorCode.ASSEMBLY_INVALID,
                pointer=f"{pointer}/resource_owner_id",
                detail="primary_institution_resource_owner_mismatch",
            )
        overlap = capacity_ids & set(actor["capacity_ids"])
        if overlap:
            _raise(
                ConfigurationErrorCode.ASSEMBLY_INVALID,
                pointer=f"{pointer}/capacity_ids",
                detail="capacity_reused=" + ",".join(sorted(overlap)),
            )
        capacity_ids.update(actor["capacity_ids"])
        capability_by_actor[actor["actor_id"]] = actor["capability_id"]

    population_by_actor = _indexed_rows(
        populations, "actor_id", pointer="/population_actors"
    )
    unit_by_id = _indexed_rows(
        document["population_units"], "unit_id", pointer="/population_units"
    )
    units = list(unit_by_id.values())
    if set(row["unit_id"] for row in populations) != set(unit_by_id):
        _raise(
            ConfigurationErrorCode.ASSEMBLY_INVALID,
            pointer="/population_units",
            detail="population_actor_unit_coverage_mismatch",
        )
    population_product_capabilities: dict[str, set[str]] = {}
    assignments: set[str] = set()
    for index, unit in enumerate(units):
        pointer = f"/population_units/{index}"
        actor = population_by_actor.get(unit["actor_id"])
        if actor is None or actor["unit_id"] != unit["unit_id"]:
            _raise(
                ConfigurationErrorCode.REFERENCE_UNRESOLVED,
                pointer=f"{pointer}/actor_id",
                detail="population_actor_unresolved",
            )
        product_id = unit["population_product_id"]
        if profile.products.get(product_id) != "population_model":
            _raise(
                ConfigurationErrorCode.REFERENCE_UNRESOLVED,
                pointer=f"{pointer}/population_product_id",
                detail="population_product_unresolved",
            )
        population_product_capabilities.setdefault(product_id, set()).add(
            actor["capability_id"]
        )
        if (
            unit["capacity_id"] != actor["capacity_id"]
            or unit["assignment_id"] != actor["assignment_id"]
            or unit["host_institution_id"] != actor["host_institution_id"]
        ):
            _raise(
                ConfigurationErrorCode.ASSEMBLY_INVALID,
                pointer=pointer,
                detail="population_actor_unit_identity_mismatch",
            )
        host = unit["host_institution_id"]
        if host not in institution_ids:
            _raise(
                ConfigurationErrorCode.REFERENCE_UNRESOLVED,
                pointer=f"{pointer}/host_institution_id",
                detail="host_institution_unresolved",
            )
        if actor["resource_owner_id"] != resource_owner_by_institution[host]:
            _raise(
                ConfigurationErrorCode.ASSEMBLY_INVALID,
                pointer=f"/population_actors/{index}/resource_owner_id",
                detail="host_institution_resource_owner_mismatch",
            )
        if unit["availability_record_id"] != unit["assignment_id"]:
            _raise(
                ConfigurationErrorCode.ASSEMBLY_INVALID,
                pointer=f"{pointer}/availability_record_id",
                detail="assignment_availability_identity_mismatch",
            )
        if unit["assignment_id"] in assignments:
            _raise(
                ConfigurationErrorCode.ASSEMBLY_INVALID,
                pointer=f"{pointer}/assignment_id",
                detail="assignment_reused",
            )
        assignments.add(unit["assignment_id"])
        if unit["capacity_id"] in capacity_ids:
            _raise(
                ConfigurationErrorCode.ASSEMBLY_INVALID,
                pointer=f"{pointer}/capacity_id",
                detail="capacity_reused",
            )
        capacity_ids.add(unit["capacity_id"])
        capability_by_actor[unit["actor_id"]] = actor["capability_id"]
    if set(population_product_capabilities) != expected_population_products or any(
        len(capabilities) != 1
        for capabilities in population_product_capabilities.values()
    ):
        _raise(
            ConfigurationErrorCode.ASSEMBLY_INVALID,
            pointer="/population_units",
            detail="population_product_capability_coverage_mismatch",
        )
    population_capability_ids = {
        next(iter(capabilities))
        for capabilities in population_product_capabilities.values()
    }
    if population_capability_ids & set(named_capability_ids):
        _raise(
            ConfigurationErrorCode.ASSEMBLY_INVALID,
            pointer="/population_actors",
            detail="capability_product_kind_collision",
        )
    configured_capabilities = set(named_capability_ids) | population_capability_ids
    if configured_capabilities != profile.capabilities:
        _raise(
            ConfigurationErrorCode.COVERAGE_MISMATCH,
            pointer="/named_actors",
            detail="released_capability_coverage_mismatch",
        )

    assets = document["technical_assets"]
    asset_by_id = _indexed_rows(assets, "id", pointer="/technical_assets")
    asset_ids = set(asset_by_id)
    for index, asset in enumerate(assets):
        operating = asset["operating_institution_id"]
        owning = asset["owning_institution_id"]
        _require_references(
            [operating],
            institution_ids,
            pointer=f"/technical_assets/{index}/operating_institution_id",
            detail="institution_unresolved",
        )
        if owning is not None:
            _require_references(
                [owning],
                institution_ids,
                pointer=f"/technical_assets/{index}/owning_institution_id",
                detail="institution_unresolved",
            )
    for index, unit in enumerate(units):
        _require_references(
            unit["access_scope_ids"],
            asset_ids,
            pointer=f"/population_units/{index}/access_scope_ids",
            detail="asset_unresolved",
        )

    records = document["initial_records"]
    record_by_id = _indexed_rows(records, "id", pointer="/initial_records")
    record_ids = set(record_by_id)
    route_by_id = {
        row["id"]: row for row in records if row["family"] == "institutional_route"
    }
    authority_by_target: dict[str, Mapping[str, Any]] = {}
    assignment_by_target: dict[str, Mapping[str, Any]] = {}
    reference_ids = actor_ids | institution_ids | process_ids
    outer_start = datetime.fromisoformat(document["clock"]["modeled_start"]["value"])
    outer_end = datetime.fromisoformat(
        document["clock"]["notification_observation_horizon"]["value"]
    )
    for index, record in enumerate(records):
        pointer = f"/initial_records/{index}"
        if record["owner_id"] not in institution_ids | process_ids:
            _raise(
                ConfigurationErrorCode.REFERENCE_UNRESOLVED,
                pointer=f"{pointer}/owner_id",
                detail="record_owner_unresolved",
            )
        family = record["family"]
        if family == "authority_and_capacity":
            target = record["target_id"]
            actor = actor_by_id.get(target)
            if actor is None or target not in {row["actor_id"] for row in named}:
                _raise(
                    ConfigurationErrorCode.REFERENCE_UNRESOLVED,
                    pointer=f"{pointer}/target_id",
                    detail="named_actor_unresolved",
                )
            if target in authority_by_target:
                _raise(
                    ConfigurationErrorCode.ASSEMBLY_INVALID,
                    pointer=pointer,
                    detail="office_authority_record_reused",
                )
            authority_by_target[target] = record
            scopes = record["capacity_scopes"]
            scope_capacities = [row["capacity_id"] for row in scopes]
            scope_institutions = [row["institution_id"] for row in scopes]
            if (
                set(scope_capacities) != set(actor["capacity_ids"])
                or len(scope_capacities) != len(set(scope_capacities))
            ):
                _raise(
                    ConfigurationErrorCode.ASSEMBLY_INVALID,
                    pointer=f"{pointer}/capacity_scopes",
                    detail="office_capacity_scope_mismatch",
                )
            _require_references(
                scope_institutions,
                institution_ids,
                pointer=f"{pointer}/capacity_scopes",
                detail="institution_unresolved",
            )
            if record["owner_id"] != actor["primary_institution_id"]:
                _raise(
                    ConfigurationErrorCode.ASSEMBLY_INVALID,
                    pointer=f"{pointer}/owner_id",
                    detail="office_authority_owner_mismatch",
                )
        elif family == "unit_assignment":
            target = record["target_id"]
            unit = unit_by_id.get(target)
            if unit is None:
                _raise(
                    ConfigurationErrorCode.REFERENCE_UNRESOLVED,
                    pointer=f"{pointer}/target_id",
                    detail="population_unit_unresolved",
                )
            if target in assignment_by_target:
                _raise(
                    ConfigurationErrorCode.ASSEMBLY_INVALID,
                    pointer=pointer,
                    detail="unit_assignment_record_reused",
                )
            assignment_by_target[target] = record
            if (
                record["id"] != unit["assignment_id"]
                or record["capacity_id"] != unit["capacity_id"]
                or record["owner_id"] != unit["host_institution_id"]
                or set(record["access_scope_ids"]) != set(unit["access_scope_ids"])
            ):
                _raise(
                    ConfigurationErrorCode.ASSEMBLY_INVALID,
                    pointer=pointer,
                    detail="unit_assignment_record_mismatch",
                )
        elif family == "institutional_relationship":
            _require_references(
                record["parties"],
                institution_ids,
                pointer=f"{pointer}/parties",
                detail="institution_unresolved",
            )
        elif family == "institutional_route":
            endpoints = [
                *record["endpoints"]["side_a"],
                *record["endpoints"]["side_b"],
            ]
            _require_references(
                endpoints,
                reference_ids,
                pointer=f"{pointer}/endpoints",
                detail="route_endpoint_unresolved",
            )
            if len(endpoints) != len(set(endpoints)):
                _raise(
                    ConfigurationErrorCode.ASSEMBLY_INVALID,
                    pointer=f"{pointer}/endpoints",
                    detail="route_endpoint_reused",
                )
            if not record["addressing_rule"].startswith("one_exact_"):
                _raise(
                    ConfigurationErrorCode.ASSEMBLY_INVALID,
                    pointer=f"{pointer}/addressing_rule",
                    detail="exact_route_addressing_required",
                )
            required_capacity = record.get("required_sender_capacity_id")
            if required_capacity is not None:
                side_a_capacities = {
                    capacity
                    for endpoint in record["endpoints"]["side_a"]
                    for capacity in (
                        actor_by_id.get(endpoint, {}).get("capacity_ids")
                        or (actor_by_id.get(endpoint, {}).get("capacity_id"),)
                    )
                    if capacity is not None
                }
                if required_capacity not in side_a_capacities:
                    _raise(
                        ConfigurationErrorCode.ASSEMBLY_INVALID,
                        pointer=f"{pointer}/required_sender_capacity_id",
                        detail="sender_capacity_unresolved",
                    )
        elif family == "technical_asset_state":
            _require_references(
                [record["target_id"]],
                asset_ids,
                pointer=f"{pointer}/target_id",
                detail="technical_asset_unresolved",
            )
        elif family in {"business_object_state", "affected_cohort_state"}:
            _require_references(
                [record["target_id"]],
                process_ids,
                pointer=f"{pointer}/target_id",
                detail="scenario_process_unresolved",
            )
        if "effective_interval" in record:
            interval = record["effective_interval"]
            lower = datetime.fromisoformat(interval["start"])
            upper = datetime.fromisoformat(interval["end"])
            if lower > upper or lower < outer_start or upper > outer_end:
                _raise(
                    ConfigurationErrorCode.ASSEMBLY_INVALID,
                    pointer=f"{pointer}/effective_interval",
                    detail="outside_configuration_clock",
                )
    if set(authority_by_target) != {row["actor_id"] for row in named}:
        _raise(
            ConfigurationErrorCode.ASSEMBLY_INVALID,
            pointer="/initial_records",
            detail="office_authority_record_coverage_mismatch",
        )
    if set(assignment_by_target) != set(unit_by_id):
        _raise(
            ConfigurationErrorCode.ASSEMBLY_INVALID,
            pointer="/initial_records",
            detail="unit_assignment_record_coverage_mismatch",
        )

    clock = document["clock"]
    ordered_times = [
        datetime.fromisoformat(clock["modeled_start"]["value"]),
        datetime.fromisoformat(clock["participant_response_start"]["value"]),
        datetime.fromisoformat(clock["acute_window"]["start"]),
        datetime.fromisoformat(clock["acute_window"]["end"]),
        datetime.fromisoformat(clock["core_horizon"]["value"]),
        datetime.fromisoformat(clock["notification_observation_horizon"]["value"]),
    ]
    if ordered_times != sorted(ordered_times):
        _raise(
            ConfigurationErrorCode.ASSEMBLY_INVALID,
            pointer="/clock",
            detail="temporal_order_invalid",
        )

    overlays = document["sensitivity_overlays"]
    overlay_by_id = _indexed_rows(
        overlays, "overlay_id", pointer="/sensitivity_overlays"
    )
    overlay_ids = set(overlay_by_id)
    variants = document["structural_variants"]
    variant_by_id = _indexed_rows(
        variants, "id", pointer="/structural_variants"
    )
    if _duplicates([variant["family"] for variant in variants]):
        _raise(
            ConfigurationErrorCode.ASSEMBLY_INVALID,
            pointer="/structural_variants",
            detail="variant_family_reused",
        )
    variant_overlay_ids: set[str] = set()
    for index, variant in enumerate(variants):
        if variant["selection"] not in variant["allowed_domain"]:
            _raise(
                ConfigurationErrorCode.ASSEMBLY_INVALID,
                pointer=f"/structural_variants/{index}/selection",
                detail="selection_outside_allowed_domain",
            )
        materialization_field = _SEMANTIC_VARIANT_MATERIALIZATION_FIELDS.get(
            variant["family"]
        )
        if materialization_field is None:
            _raise(
                ConfigurationErrorCode.ASSEMBLY_INVALID,
                pointer=f"/structural_variants/{index}/family",
                detail="unsupported_variant_family",
            )
        variant_overlay_ids.add(variant["sensitivity_overlay_id"])
    if variant_overlay_ids != overlay_ids:
        _raise(
            ConfigurationErrorCode.OVERLAY_TARGET_INVALID,
            pointer="/structural_variants",
            detail="variant_overlay_coverage_mismatch",
        )

    materialization = document["variant_materialization"]
    for index, variant in enumerate(variants):
        materialization_field = _SEMANTIC_VARIANT_MATERIALIZATION_FIELDS[
            variant["family"]
        ]
        materialized = materialization[materialization_field]
        if (
            isinstance(materialized, Mapping)
            and materialized["selection"] != variant["selection"].lower()
        ):
            _raise(
                ConfigurationErrorCode.ASSEMBLY_INVALID,
                pointer=f"/structural_variants/{index}/selection",
                detail="variant_materialization_selection_mismatch",
            )
    for overlay_index, overlay in enumerate(overlays):
        pointer = f"/sensitivity_overlays/{overlay_index}"
        if overlay["coupled_operations_disclosed"] is not True:
            _raise(
                ConfigurationErrorCode.OVERLAY_TARGET_INVALID,
                pointer=f"{pointer}/coupled_operations_disclosed",
                detail="coupled_operations_must_be_disclosed",
            )
        operations = overlay["operations"]
        if len(operations) != 2:
            _raise(
                ConfigurationErrorCode.OVERLAY_TARGET_INVALID,
                pointer=f"{pointer}/operations",
                detail="paired_operations_required",
            )
        by_kind = {operation["target_kind"]: operation for operation in operations}
        if set(by_kind) != {"structural_variant", "variant_materialization"}:
            _raise(
                ConfigurationErrorCode.OVERLAY_TARGET_INVALID,
                pointer=f"{pointer}/operations",
                detail="paired_target_kinds_required",
            )
        structural = by_kind["structural_variant"]
        variant = variant_by_id.get(structural["target_id"])
        if (
            variant is None
            or variant["sensitivity_overlay_id"] != overlay["overlay_id"]
            or structural["field"] != "selection"
            or structural["replacement_value"] not in variant["allowed_domain"]
            or structural["replacement_value"] == variant["selection"]
        ):
            _raise(
                ConfigurationErrorCode.OVERLAY_TARGET_INVALID,
                pointer=f"{pointer}/operations",
                detail="structural_target_unresolved",
            )
        replacement = by_kind["variant_materialization"]
        expected_materialization_field = _SEMANTIC_VARIANT_MATERIALIZATION_FIELDS[
            variant["family"]
        ]
        if (
            replacement["target_id"] != "variant_materialization"
            or replacement["field"] != expected_materialization_field
        ):
            _raise(
                ConfigurationErrorCode.OVERLAY_TARGET_INVALID,
                pointer=f"{pointer}/operations",
                detail="materialization_target_mismatch",
            )
        target_value = materialization[replacement["field"]]
        if _value_type(target_value) is not _value_type(
            replacement["replacement_value"]
        ):
            _raise(
                ConfigurationErrorCode.OVERLAY_TARGET_INVALID,
                pointer=f"{pointer}/operations",
                detail="replacement_type_mismatch",
            )
        replacement_value = replacement["replacement_value"]
        if isinstance(replacement_value, Mapping):
            replacement_selection = replacement_value.get("selection")
            if (
                not isinstance(replacement_selection, str)
                or replacement_selection
                != structural["replacement_value"].lower()
            ):
                _raise(
                    ConfigurationErrorCode.OVERLAY_TARGET_INVALID,
                    pointer=f"{pointer}/operations",
                    detail="overlay_materialization_selection_mismatch",
                )
        if replacement["field"] == "active_population_actor_ids":
            if not all(isinstance(item, str) for item in replacement_value):
                _raise(
                    ConfigurationErrorCode.OVERLAY_TARGET_INVALID,
                    pointer=f"{pointer}/operations",
                    detail="population_actor_id_array_required",
                )
            _require_references(
                replacement_value,
                set(population_by_actor),
                pointer=f"{pointer}/operations",
                detail="population_actor_unresolved",
            )
    _require_references(
        materialization["active_population_actor_ids"],
        set(population_by_actor),
        pointer="/variant_materialization/active_population_actor_ids",
        detail="population_actor_unresolved",
    )
    _require_references(
        materialization["office_capacity_profile"]["unavailable_actor_ids"],
        {row["actor_id"] for row in named},
        pointer=(
            "/variant_materialization/office_capacity_profile/"
            "unavailable_actor_ids"
        ),
        detail="named_actor_unresolved",
    )

    exogenous = document["exogenous_inputs"]
    _indexed_rows(exogenous, "id", pointer="/exogenous_inputs")
    target_registries = {
        "scenario_process": process_ids,
        "technical_asset_set": asset_ids,
        "authority_record_set": {
            row["id"] for row in records if row["family"] == "authority_and_capacity"
        },
        "institutional_route_set": set(route_by_id),
    }
    for index, item in enumerate(exogenous):
        pointer = f"/exogenous_inputs/{index}"
        _require_references(
            item["target_ids"],
            target_registries[item["target_kind"]],
            pointer=f"{pointer}/target_ids",
            detail="typed_target_unresolved",
        )
        overlay_id = item["sensitivity_overlay_id"]
        if overlay_id is not None and overlay_id not in overlay_ids:
            _raise(
                ConfigurationErrorCode.REFERENCE_UNRESOLVED,
                pointer=f"{pointer}/sensitivity_overlay_id",
                detail="overlay_unresolved",
            )
        if item["outcome_forcing"] is not False:
            _raise(
                ConfigurationErrorCode.EXECUTION_BOUNDARY_INVALID,
                pointer=f"{pointer}/outcome_forcing",
                detail="non_outcome_forcing_input_required",
            )
        if "window_start" in item["activation"]:
            activation = datetime.fromisoformat(item["activation"]["window_start"])
            if activation < ordered_times[0] or activation > ordered_times[-1]:
                _raise(
                    ConfigurationErrorCode.ASSEMBLY_INVALID,
                    pointer=f"{pointer}/activation/window_start",
                    detail="outside_configuration_clock",
                )

    lineage = document["bounded_lineage"]
    _require_references(
        lineage["participant_ids"],
        actor_ids,
        pointer="/bounded_lineage/participant_ids",
        detail="actor_unresolved",
    )
    _require_references(
        lineage["route_ids"],
        set(route_by_id),
        pointer="/bounded_lineage/route_ids",
        detail="route_unresolved",
    )
    if len(lineage["route_ids"]) != len(lineage["participant_ids"]) - 1:
        _raise(
            ConfigurationErrorCode.ASSEMBLY_INVALID,
            pointer="/bounded_lineage/route_ids",
            detail="lineage_route_chain_length_mismatch",
        )
    for index, route_id in enumerate(lineage["route_ids"]):
        endpoints = {
            *route_by_id[route_id]["endpoints"]["side_a"],
            *route_by_id[route_id]["endpoints"]["side_b"],
        }
        pair = set(lineage["participant_ids"][index : index + 2])
        if not pair <= endpoints:
            _raise(
                ConfigurationErrorCode.ASSEMBLY_INVALID,
                pointer=f"/bounded_lineage/route_ids/{index}",
                detail="lineage_route_endpoint_mismatch",
            )
    lineage_capabilities = [
        capability_by_actor[actor_id] for actor_id in lineage["participant_ids"]
    ]
    capability_positions = {
        capability_id: index
        for index, capability_id in enumerate(lineage_capabilities)
    }
    intent_capabilities = [
        intent_id.split(".", 1)[0]
        for intent_id in lineage["semantic_intent_sequence"]
    ]
    if (
        not set(intent_capabilities) <= set(capability_positions)
        or set(intent_capabilities) != set(lineage_capabilities)
        or [capability_positions[item] for item in intent_capabilities]
        != sorted(capability_positions[item] for item in intent_capabilities)
    ):
        _raise(
            ConfigurationErrorCode.ASSEMBLY_INVALID,
            pointer="/bounded_lineage/semantic_intent_sequence",
            detail="lineage_capability_order_mismatch",
        )

    policies = document["policy_selections"]
    policy_by_id = _indexed_rows(
        policies, "policy_id", pointer="/policy_selections"
    )
    unbound = tuple(
        sorted(
            policy_id
            for policy_id, policy in policy_by_id.items()
            if policy["implementation_status"] == "unbound"
        )
    )
    if len(unbound) != len(policies) or any(
        policy["execution_consequence"] != "fail_closed" for policy in policies
    ):
        _raise(
            ConfigurationErrorCode.EXECUTION_BOUNDARY_INVALID,
            pointer="/policy_selections",
            detail="all_policy_implementations_must_be_unbound_fail_closed",
        )
    boundary = document["execution_boundary"]
    required_prerequisites = {
        "accepted_machine_schema_or_explicit_admission_profile",
        "exact_fail_closed_release_and_configuration_loader",
        "validated_event_qualified_carrier_projection",
        "versioned_implementation_for_every_enabled_policy",
        "bounded_lineage_binding",
        "runtime_bundle_and_trace_identity",
        "separate_execution_authorization",
    }
    if (
        boundary["execution_eligible"] is not False
        or boundary["unbound_policy_behavior"]
        != "reject_configuration_for_execution"
        or boundary["parsing_does_not_change_eligibility"] is not True
        or boundary["authorization_conferred_by_configuration"] != "none"
        or not required_prerequisites
        <= set(boundary["required_before_execution"])
        or any(
            document[name] is not False
            for name in (
                "historical_calibration",
                "historical_validation",
                "known_outcome_fitting",
            )
        )
        or lineage["implementation_included"] is not False
        or lineage["authorization_conferred_by_configuration"] != "none"
        or lineage["full_roster_implication"] != "none"
        or document["completion_policy"]["historical_outcome_required"] is not False
        or document["completion_policy"]["failed_closed"] != "INVARIANT_FAILURE"
    ):
        _raise(
            ConfigurationErrorCode.EXECUTION_BOUNDARY_INVALID,
            pointer="/execution_boundary",
            detail="non_executable_semantic_configuration_required",
        )

    expectations = document["validation_expectations"]
    mapping_fields = (
        "decision_and_population_commitments",
        "observation_placements",
        "private_state_placements",
        "intent_placements",
        "lifecycle_families",
    )
    for name in mapping_fields:
        if expectations[name] != profile.mapping_coverage[name]:
            _raise(
                ConfigurationErrorCode.COVERAGE_MISMATCH,
                pointer=f"/validation_expectations/{name}",
                detail=f"mapping_actual={profile.mapping_coverage[name]}",
            )
    actual_coverage = {
        "semantic_products": len(profile.products),
        **{name: profile.mapping_coverage[name] for name in mapping_fields},
        "named_actors": len(named),
        "population_actors": len(populations),
        "total_semantic_actor_instances": len(actors),
        "population_units": len(units),
        "technical_assets": len(assets),
        "canonical_institutions": len(institutions),
        "opening_records": len(records),
        "route_records": len(route_by_id),
        "structural_selections": len(variants),
        "exogenous_inputs": len(exogenous),
        "selected_policy_semantics": len(policies),
        "sensitivity_overlays": len(overlays),
    }
    for name, actual in actual_coverage.items():
        if expectations[name] != actual:
            _raise(
                ConfigurationErrorCode.COVERAGE_MISMATCH,
                pointer=f"/validation_expectations/{name}",
                detail=f"actual={actual}",
            )
    invariant_fields = (
        "one_actor_per_office_or_unit",
        "one_resource_owner_per_canonical_institution",
        "host_scope_required_for_population_units",
        "capacity_scope_required_for_office_authority",
        "exact_addressing_required_for_routes",
        "opening_record_basis_required",
        "intent_result_separation_required",
        "correction_preserves_prior_decision_basis",
        "unresolved_active_objects_carried_at_horizon",
        "deterministic_replay_required_before_execution",
    )
    for name in invariant_fields:
        if expectations[name] is not True:
            _raise(
                ConfigurationErrorCode.COVERAGE_MISMATCH,
                pointer=f"/validation_expectations/{name}",
                detail="required_true_invariant",
            )
    if expectations["execution_eligible"] is not False:
        _raise(
            ConfigurationErrorCode.COVERAGE_MISMATCH,
            pointer="/validation_expectations/execution_eligible",
            detail="required_false_invariant",
        )
    release_expected = {
        name: value
        for name, value in actual_coverage.items()
        if name != "canonical_institutions"
    }
    if dict(release_coverage) != release_expected:
        differing = sorted(
            name
            for name in set(release_coverage) | set(release_expected)
            if release_coverage.get(name) != release_expected.get(name)
        )
        _raise(
            ConfigurationErrorCode.COVERAGE_MISMATCH,
            pointer="/release_manifest/coverage",
            detail="coverage_mismatch=" + ",".join(differing),
        )
    return MappingProxyType(actual_coverage), unbound


__all__ = [
    "_load_semantic_reference_profile",
    "_validate_semantic_configuration",
    "_validate_semantic_release_document_consistency",
]
