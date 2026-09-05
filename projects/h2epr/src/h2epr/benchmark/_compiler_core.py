"""Compile one cross-event package from admitted declarative assets."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import jsonschema

from h2epr.canonical import canonical_sha256, file_sha256
from h2epr.semantic.assets import StandardAssetSet, load_release_json


class _SemanticPackageCompileCoreError(ValueError):
    """The admitted semantic parents do not close into one package."""


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_ROOT = PROJECT_ROOT / "schemas"


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise _SemanticPackageCompileCoreError(code)


def _validate(
    value: Mapping[str, Any], schema_name: str, label: str, *, version: int
) -> None:
    if version not in {2, 3, 4}:
        raise _SemanticPackageCompileCoreError(
            "schema_protocol_version_unknown"
        )
    schema = json.loads((SCHEMA_ROOT / schema_name).read_text(encoding="utf-8"))
    try:
        jsonschema.Draft202012Validator(schema).validate(value)
    except jsonschema.ValidationError as exc:
        raise _SemanticPackageCompileCoreError(
            f"{label}_schema_invalid:{exc.json_path}"
        ) from exc


def _self_hash(value: Mapping[str, Any], field: str, label: str) -> None:
    expected = canonical_sha256({key: item for key, item in value.items() if key != field})
    _require(value.get(field) == expected, f"{label}_self_hash_mismatch")


def _load_instance(
    release: Any,
    *,
    role: str,
    schema_name: str,
    hash_field: str,
    version: int,
) -> dict[str, Any]:
    value = load_release_json(release, role)
    _validate(value, schema_name, role, version=version)
    _self_hash(value, hash_field, role)
    return value


def _decode_json_pointer_token(token: str, label: str) -> str:
    result: list[str] = []
    index = 0
    while index < len(token):
        if token[index] != "~":
            result.append(token[index])
            index += 1
            continue
        _require(index + 1 < len(token), f"{label}_escape_invalid")
        escape = token[index + 1]
        _require(escape in {"0", "1"}, f"{label}_escape_invalid")
        result.append("~" if escape == "0" else "/")
        index += 2
    return "".join(result)


def _resolve_json_pointer(value: Any, pointer: str, label: str) -> Any:
    _require(pointer.startswith("/"), f"{label}_invalid")
    current = value
    for raw_token in pointer[1:].split("/"):
        token = _decode_json_pointer_token(raw_token, label)
        if isinstance(current, Mapping):
            _require(token in current, f"{label}_target_missing")
            current = current[token]
        elif isinstance(current, list):
            _require(token.isdigit(), f"{label}_array_index_invalid")
            index = int(token)
            _require(index < len(current), f"{label}_array_index_missing")
            current = current[index]
        else:
            raise _SemanticPackageCompileCoreError(f"{label}_traverses_scalar")
    return current


def _validate_configuration_value_provenance(
    configuration: Mapping[str, Any],
    label: str,
) -> None:
    """Require every declared provenance pointer to name one actual setting."""

    seen: set[str] = set()
    for index, row in enumerate(configuration["value_provenance"]):
        pointer = row["json_pointer"]
        pointer_label = f"{label}_value_provenance:{index}:{pointer}"
        _require(pointer not in seen, f"{pointer_label}_duplicate")
        seen.add(pointer)
        _require(
            pointer == "/settings" or pointer.startswith("/settings/"),
            f"{pointer_label}_outside_settings",
        )
        _resolve_json_pointer(configuration, pointer, pointer_label)


def _draft_value(value: Any, label: str) -> Any:
    _require(isinstance(value, Mapping) and "value" in value, f"{label}_invalid")
    return value["value"]


def _draft_roster(draft: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    by_id: dict[str, dict[str, Any]] = {}
    for stage in draft["stages"]:
        for episode in stage["episodes"]:
            for participant in episode["participants"]:
                participant_id = participant["participant_id"]
                row = by_id.setdefault(
                    participant_id,
                    {
                        "source_participant_id": participant_id,
                        "canonical_name": _draft_value(
                            participant["name"], f"name:{participant_id}"
                        ),
                        "observed_names": set(),
                        "observed_types": set(),
                        "observed_roles": set(),
                        "appearance_refs": [],
                    },
                )
                row["observed_names"].add(
                    _draft_value(participant["name"], f"name:{participant_id}")
                )
                row["observed_types"].add(
                    _draft_value(
                        participant["participant_type"], f"type:{participant_id}"
                    )
                )
                row["observed_roles"].add(
                    _draft_value(participant["base_role"], f"role:{participant_id}")
                )
                row["appearance_refs"].append(
                    f"draft_epg:{stage['stage_id']}/{episode['episode_id']}/{participant_id}"
                )
    result = []
    numeric_ids = []
    for participant_id, row in by_id.items():
        try:
            numeric_ids.append(int(participant_id.removeprefix("P_")))
        except ValueError as exc:
            raise _SemanticPackageCompileCoreError(
                f"draft_participant_numeric_suffix_invalid:{participant_id}"
            ) from exc
        result.append(
            {
                **{key: item for key, item in row.items() if key not in {"observed_names", "observed_types", "observed_roles"}},
                "observed_names": sorted(row["observed_names"]),
                "observed_types": sorted(row["observed_types"]),
                "observed_roles": sorted(row["observed_roles"]),
            }
        )
    gaps = [
        f"P_{index}"
        for index in range(min(numeric_ids), max(numeric_ids) + 1)
        if index not in set(numeric_ids)
    ]
    return result, gaps


def _document_stage_episode_ids(draft: Mapping[str, Any]) -> tuple[set[str], set[str]]:
    return (
        {stage["stage_id"] for stage in draft["stages"]},
        {
            episode["episode_id"]
            for stage in draft["stages"]
            for episode in stage["episodes"]
        },
    )


def _unique(rows: Sequence[Mapping[str, Any]], field: str, label: str) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        key = row[field]
        _require(key not in result, f"{label}_duplicate:{key}")
        result[key] = row
    return result


def _state_field_key(row: Mapping[str, Any]) -> tuple[str, str]:
    return row["entity_id"], row["field_name"]


def _condition_field(condition: Mapping[str, Any]) -> tuple[str, str]:
    return condition["entity_id"], condition["field_name"]


def _condition_matches(value: Any, operator: str, expected: Any) -> bool:
    if operator == "equals":
        return value == expected
    if operator == "not_equals":
        return value != expected
    if operator == "contains":
        return isinstance(value, (list, str)) and expected in value
    if operator == "gte":
        return isinstance(value, (int, float)) and not isinstance(value, bool) and value >= expected
    if operator == "lte":
        return isinstance(value, (int, float)) and not isinstance(value, bool) and value <= expected
    return False


def _validate_value_domain(value: Any, row: Mapping[str, Any], label: str) -> None:
    expected_type = row["value_type"]
    type_valid = {
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "array": isinstance(value, list),
    }[expected_type]
    _require(type_valid, f"{label}_type_mismatch")
    if "allowed_values" in row:
        _require(value in row["allowed_values"], f"{label}_outside_allowed_values")
    if "minimum" in row:
        _require(value >= row["minimum"], f"{label}_below_minimum")
    if "maximum" in row:
        _require(value <= row["maximum"], f"{label}_above_maximum")


def _derive_configuration_admission_receipt(
    *,
    configuration: Mapping[str, Any],
    roster: Mapping[str, Any],
    actor_map: Mapping[str, Any],
    participant_interface: Mapping[str, Any],
    scenario_interface: Mapping[str, Any],
    mechanism: Mapping[str, Any],
    draft: Mapping[str, Any],
) -> dict[str, Any]:
    """Derive the tracked receipt from independently recomputable evidence."""

    settings = configuration["settings"]
    checks = [
        ("configuration_schema", configuration["configuration_sha256"]),
        ("roster_identity", roster["roster_sha256"]),
        ("actor_map_identity", actor_map["actor_map_sha256"]),
        ("participant_interface_identity", participant_interface["interface_sha256"]),
        ("scenario_interface_identity", scenario_interface["scenario_interface_sha256"]),
        ("scenario_mechanism_identity", mechanism["mechanism_sha256"]),
        ("active_actor_closure", canonical_sha256(settings["active_actor_ids"])),
        ("timeline_closure", canonical_sha256(settings["timeline"])),
        ("initial_state_closure", canonical_sha256(settings["initial_state"])),
        ("route_closure", canonical_sha256(settings["communication_routes"])),
        (
            "draft_stage_episode_closure",
            canonical_sha256(
                [sorted(values) for values in _document_stage_episode_ids(draft)]
            ),
        ),
    ]
    receipt = {
        "schema_version": "h2epr.configuration-admission-receipt.v3",
        "receipt_id": f"{configuration['configuration_id']}.admission",
        "configuration_id": configuration["configuration_id"],
        "configuration_sha256": configuration["configuration_sha256"],
        "derived_by": "h2epr.configuration-admission.v3",
        "checks": [
            {
                "check_id": check_id,
                "passed": True,
                "evidence_sha256": canonical_sha256(
                    {"check_id": check_id, "evidence": evidence}
                ),
            }
            for check_id, evidence in checks
        ],
        "admitted": True,
        "receipt_sha256": "0" * 64,
    }
    receipt["receipt_sha256"] = canonical_sha256(
        {key: item for key, item in receipt.items() if key != "receipt_sha256"}
    )
    return receipt


def _derive_rule_configuration_admission_receipt(
    *,
    configuration: Mapping[str, Any],
    shared_configuration: Mapping[str, Any],
    participant_interface: Mapping[str, Any],
    mechanism: Mapping[str, Any],
) -> dict[str, Any]:
    """Derive admission evidence for one declarative Rule configuration."""

    checks = [
        ("configuration_schema", configuration["configuration_sha256"]),
        (
            "shared_configuration_identity",
            shared_configuration["configuration_sha256"],
        ),
        ("participant_interface_identity", participant_interface["interface_sha256"]),
        ("scenario_mechanism_identity", mechanism["mechanism_sha256"]),
        (
            "decision_rule_closure",
            canonical_sha256(configuration["settings"]["decision_rules"]),
        ),
    ]
    receipt = {
        "schema_version": "h2epr.configuration-admission-receipt.v3",
        "receipt_id": f"{configuration['configuration_id']}.admission",
        "configuration_id": configuration["configuration_id"],
        "configuration_sha256": configuration["configuration_sha256"],
        "derived_by": "h2epr.configuration-admission.v3",
        "checks": [
            {
                "check_id": check_id,
                "passed": True,
                "evidence_sha256": canonical_sha256(
                    {"check_id": check_id, "evidence": evidence}
                ),
            }
            for check_id, evidence in checks
        ],
        "admitted": True,
        "receipt_sha256": "0" * 64,
    }
    receipt["receipt_sha256"] = canonical_sha256(
        {key: item for key, item in receipt.items() if key != "receipt_sha256"}
    )
    return receipt


def _validate_semantic_parents(
    *,
    assets: StandardAssetSet,
    roster: Mapping[str, Any],
    actor_map: Mapping[str, Any],
    semantic_index: Mapping[str, Any],
) -> None:
    actor_rows = _unique(actor_map["runtime_actors"], "actor_id", "runtime_actor")
    parent_rows = _unique(semantic_index["parents"], "actor_id", "semantic_parent_actor")
    _require(set(actor_rows) == set(parent_rows), "semantic_parent_actor_universe_mismatch")
    roster_by_id = {
        row["source_participant_id"]: row for row in roster["participants"]
    }
    semantic_parent_ids: set[str] = set()
    for actor_id, parent in parent_rows.items():
        actor = actor_rows[actor_id]
        parent_id = parent["semantic_parent_id"]
        _require(parent_id not in semantic_parent_ids, f"semantic_parent_id_duplicate:{parent_id}")
        semantic_parent_ids.add(parent_id)
        _require(parent_id == actor["semantic_parent_id"], f"semantic_parent_id_mismatch:{actor_id}")
        _require(
            parent["representation_kind"] == actor["representation_kind"],
            f"semantic_parent_kind_mismatch:{actor_id}",
        )
        _require(
            sorted(parent["source_participant_ids"])
            == sorted(actor["source_participant_ids"]),
            f"semantic_parent_source_ids_mismatch:{actor_id}",
        )
        expected_refs = sorted(
            ref
            for participant_id in actor["source_participant_ids"]
            for ref in roster_by_id[participant_id]["appearance_refs"]
        )
        _require(
            sorted(parent["source_anchor_refs"]) == expected_refs,
            f"semantic_parent_anchor_mismatch:{actor_id}",
        )
        relative = Path(parent["relative_path"])
        _require(not relative.is_absolute() and ".." not in relative.parts, f"semantic_parent_path_unsafe:{actor_id}")
        path = assets.project_root / relative
        _require(path.is_file() and not path.is_symlink(), f"semantic_parent_missing:{actor_id}")
        _require(file_sha256(path) == parent["sha256"], f"semantic_parent_hash_mismatch:{actor_id}")
        text = path.read_text(encoding="utf-8")
        for ref in parent["source_anchor_refs"]:
            _require(ref in text, f"semantic_parent_anchor_not_cited:{actor_id}:{ref}")


def _validate_semantic_closure(
    assets: StandardAssetSet,
    values: Mapping[str, Mapping[str, Any]],
    *,
    expected_environment_implementation_id: str = (
        "h2epr.environment.declarative.v3"
    ),
    expected_annotation_implementation_id: str = (
        "h2epr.annotations.declarative.v3"
    ),
) -> None:
    roster = values["roster"]
    actor_map = values["actor_map"]
    interface = values["participant_interface"]
    scenario_interface = values["scenario_interface"]
    mechanism = values["scenario_mechanism"]
    configuration = values["shared_configuration"]
    receipt = values["configuration_admission"]

    expected_roster, expected_gaps = _draft_roster(assets.source_documents["draft_epg"])
    _require(roster["participants"] == expected_roster, "roster_draft_semantics_mismatch")
    _require(roster["source_id_gaps"] == expected_gaps, "roster_source_id_gap_mismatch")
    _require(roster["participant_count"] == len(expected_roster), "roster_participant_count_mismatch")
    _require(
        roster["occurrence_count"]
        == sum(len(row["appearance_refs"]) for row in expected_roster),
        "roster_occurrence_count_mismatch",
    )
    source_ids = [row["source_participant_id"] for row in expected_roster]
    mappings = actor_map["mappings"]
    mapped_ids = [row["source_participant_id"] for row in mappings]
    _require(len(mapped_ids) == len(set(mapped_ids)), "actor_map_source_duplicate")
    _require(mapped_ids == source_ids, "actor_map_source_order_or_closure_mismatch")
    actor_rows = _unique(actor_map["runtime_actors"], "actor_id", "runtime_actor")
    active_mappings = {
        row["target_id"]: row
        for row in mappings
        if row["disposition"] in {"named_agent", "population"}
    }
    _require(len(active_mappings) == len(actor_rows), "active_mapping_cardinality_mismatch")
    _require(set(active_mappings) == set(actor_rows), "active_mapping_actor_universe_mismatch")
    for actor_id, actor in actor_rows.items():
        mapping = active_mappings[actor_id]
        expected_kind = "agent" if mapping["disposition"] == "named_agent" else "population"
        _require(actor["representation_kind"] == expected_kind, f"actor_representation_kind_mismatch:{actor_id}")
        _require(
            sorted(actor["source_participant_ids"])
            == sorted(
                row["source_participant_id"]
                for row in mappings
                if row["target_id"] == actor_id
            ),
            f"actor_source_participant_closure_failure:{actor_id}",
        )
    _validate_semantic_parents(
        assets=assets,
        roster=roster,
        actor_map=actor_map,
        semantic_index=values["participant_semantic_index"],
    )

    active_ids = sorted(actor_rows)
    interface_rows = _unique(interface["actors"], "actor_id", "interface_actor")
    _require(sorted(interface_rows) == active_ids, "participant_interface_actor_universe_mismatch")
    _require(sorted(scenario_interface["actor_ids"]) == active_ids, "scenario_interface_actor_universe_mismatch")
    settings = configuration["settings"]
    _require(settings["active_actor_ids"] == active_ids, "configuration_actor_universe_mismatch")
    _require(settings["exposure_mode"] == assets.source_profile["exposure_mode"], "configuration_exposure_mode_mismatch")
    _require(settings["observation_contract"].get("schema_version") == "h2epr.participant-observation.v3",
             "configuration_observation_contract_mismatch")

    observations = _unique(
        values["observation_registry"]["observations"],
        "observation_id",
        "observation",
    )
    intents = _unique(values["intent_registry"]["intents"], "intent_id", "intent")
    lifecycles = _unique(
        values["lifecycle_registry"]["lifecycles"], "lifecycle_id", "lifecycle"
    )
    handlers = _unique(mechanism["intent_handlers"], "intent_id", "intent_handler")
    _require(set(intents) == set(handlers), "intent_handler_universe_mismatch")
    _require("no_op" in intents, "no_op_intent_missing")
    field_rows = _unique(
        [
            {**row, "field_key": f"{row['entity_id']}.{row['field_name']}"}
            for row in mechanism["state_fields"]
        ],
        "field_key",
        "state_field",
    )
    field_keys = {_state_field_key(row) for row in mechanism["state_fields"]}
    entity_ids = {entity for entity, _ in field_keys}
    target_universe = set(active_ids) | entity_ids
    for observation_id, observation in observations.items():
        _require(set(observation["consumers"]) <= set(active_ids), f"observation_consumer_unknown:{observation_id}")
    for actor_id, actor in interface_rows.items():
        _require(actor["semantic_parent_id"] == actor_rows[actor_id]["semantic_parent_id"], f"interface_semantic_parent_mismatch:{actor_id}")
        _require(set(actor["observation_ids"]) <= set(observations), f"actor_observation_unknown:{actor_id}")
        _require(set(actor["intent_ids"]) <= set(intents), f"actor_intent_unknown:{actor_id}")
        _require(set(actor["lifecycle_ids"]) <= set(lifecycles), f"actor_lifecycle_unknown:{actor_id}")
        _require("no_op" in actor["intent_ids"], f"actor_no_op_missing:{actor_id}")
    for intent_id, intent in intents.items():
        actors_from_interface = sorted(
            actor_id
            for actor_id, actor in interface_rows.items()
            if intent_id in actor["intent_ids"]
        )
        _require(intent["eligible_actors"] == actors_from_interface, f"intent_actor_closure_failure:{intent_id}")
        _require(set(intent["eligible_targets"]) <= target_universe, f"intent_target_unknown:{intent_id}")
        _require(intent["lifecycle_id"] in lifecycles, f"intent_lifecycle_unknown:{intent_id}")
        handler = handlers[intent_id]
        _require(handler["eligible_actors"] == intent["eligible_actors"], f"handler_actor_mismatch:{intent_id}")
        _require(handler["eligible_targets"] == intent["eligible_targets"], f"handler_target_mismatch:{intent_id}")
        for condition in handler["preconditions"]:
            _require(_condition_field(condition) in field_keys, f"handler_precondition_field_unknown:{intent_id}")
        for effect in handler["effects"]:
            _require(_state_field_key(effect) in field_keys, f"handler_effect_field_unknown:{intent_id}")

    scenario_fields = {
        row["field_id"] for row in scenario_interface["state_fields"]
    }
    expected_scenario_fields = {"state_version"} | {
        f"entities.{entity}.{field}" for entity, field in field_keys
    }
    _require(scenario_fields == expected_scenario_fields, "scenario_interface_state_field_mismatch")
    interface_fields = _unique(scenario_interface["state_fields"], "field_id", "scenario_field")
    for field in mechanism["state_fields"]:
        projection = interface_fields[f"entities.{field['entity_id']}.{field['field_name']}"]
        _require(projection["visibility"] == field["visibility"]
                 and projection["update_authority"] == field["update_authority"],
                 "scenario_interface_state_authority_mismatch")
        _require(field["visibility"] != "actor_private" or field["entity_id"] in active_ids,
                 "actor_private_state_owner_unknown")
    _require(scenario_interface["observation_registry_id"] == values["observation_registry"]["registry_id"], "scenario_observation_registry_mismatch")
    _require(scenario_interface["intent_registry_id"] == values["intent_registry"]["registry_id"], "scenario_intent_registry_mismatch")
    _require(scenario_interface["lifecycle_registry_id"] == values["lifecycle_registry"]["registry_id"], "scenario_lifecycle_registry_mismatch")
    _require(
        scenario_interface["environment_implementation_id"]
        == expected_environment_implementation_id,
        "scenario_environment_implementation_mismatch",
    )
    _require(
        scenario_interface["annotation_implementation_id"]
        == expected_annotation_implementation_id,
        "scenario_annotation_implementation_mismatch",
    )

    timeline = settings["timeline"]
    _require([row["logical_tick"] for row in timeline] == list(range(1, len(timeline) + 1)), "timeline_tick_sequence_invalid")
    coordinate_ids = [row["coordinate_id"] for row in timeline]
    _require(len(coordinate_ids) == len(set(coordinate_ids)), "timeline_coordinate_duplicate")
    stage_ids, episode_ids = _document_stage_episode_ids(assets.source_documents["draft_epg"])
    for row in timeline:
        _require(row["stage_id"] in stage_ids, f"timeline_stage_unknown:{row['coordinate_id']}")
        _require(row["episode_id"] in episode_ids, f"timeline_episode_unknown:{row['coordinate_id']}")
    initial = settings["initial_state"]
    _require(initial["state_version"] == 0, "initial_state_version_invalid")
    initial_fields = {
        (entity, field)
        for entity, fields in initial["entities"].items()
        for field in fields
    }
    _require(initial_fields == field_keys, "initial_state_field_universe_mismatch")
    state_row_by_key = {_state_field_key(row): row for row in mechanism["state_fields"]}
    for entity, fields in initial["entities"].items():
        _require(isinstance(fields, Mapping), f"initial_state_entity_shape_invalid:{entity}")
        for field, value in fields.items():
            _validate_value_domain(value, state_row_by_key[(entity, field)], f"initial_state:{entity}:{field}")

    routes = settings["communication_routes"]
    route_by_id = _unique(routes, "route_id", "route")
    route_pairs: set[tuple[str, str]] = set()
    for route_id, route in route_by_id.items():
        pair = route["source_id"], route["target_id"]
        _require(route["source_id"] in active_ids and route["target_id"] in active_ids, f"route_actor_unknown:{route_id}")
        _require(route["source_id"] != route["target_id"], f"route_self_forbidden:{route_id}")
        _require(pair not in route_pairs, f"route_pair_duplicate:{route_id}")
        route_pairs.add(pair)
    message_kinds = _unique(mechanism["message_kinds"], "message_kind", "message_kind")
    for kind, row in message_kinds.items():
        _require(set(row["eligible_senders"]) <= set(active_ids), f"message_sender_unknown:{kind}")
        _require(set(row["eligible_recipients"]) <= set(active_ids), f"message_recipient_unknown:{kind}")
    for annotation in mechanism["annotations"]:
        _require(set(annotation["participant_ids"]) <= set(active_ids), f"annotation_participant_unknown:{annotation['annotation_id']}")
        for condition in annotation["when_all"]:
            _require(_condition_field(condition) in field_keys, f"annotation_field_unknown:{annotation['annotation_id']}")
    for condition in mechanism["termination_invariants"]:
        _require(_condition_field(condition) in field_keys, "termination_invariant_field_unknown")
    expectations = mechanism.get("outcome_expectations", [])
    _unique(expectations, "expectation_id", "outcome_expectation")
    for condition in expectations:
        _require(_condition_field(condition) in field_keys, "outcome_expectation_field_unknown")

    derived = _derive_configuration_admission_receipt(
        configuration=configuration,
        roster=roster,
        actor_map=actor_map,
        participant_interface=interface,
        scenario_interface=scenario_interface,
        mechanism=mechanism,
        draft=assets.source_documents["draft_epg"],
    )
    _require(receipt == derived, "configuration_admission_receipt_not_independently_derived")


def _validate_rule_release(
    *,
    assets: StandardAssetSet,
    values: Mapping[str, Mapping[str, Any]],
    realization: Mapping[str, Any],
    backend_configuration: Mapping[str, Any],
    backend_configuration_admission: Mapping[str, Any],
    expected_implementation_id: str = "h2epr.backend.rule.declarative.v3",
) -> None:
    _validate_configuration_value_provenance(
        backend_configuration,
        "backend_configuration",
    )
    _require(
        realization["event_id"]
        == backend_configuration["event_id"]
        == assets.assembly["event_id"],
        "backend_release_event_identity_mismatch",
    )
    interface = values["participant_interface"]
    scenario = values["shared_configuration"]["settings"]
    mechanism = values["scenario_mechanism"]
    active_ids = scenario["active_actor_ids"]
    interface_by_actor = _unique(interface["actors"], "actor_id", "interface_actor")
    realization_by_actor = _unique(realization["actor_realizations"], "actor_id", "realization_actor")
    _require(sorted(realization_by_actor) == active_ids, "backend_realization_actor_universe_mismatch")
    for actor_id, row in realization_by_actor.items():
        parent = interface_by_actor[actor_id]
        _require(row["semantic_parent_id"] == parent["semantic_parent_id"], f"backend_realization_parent_mismatch:{actor_id}")
        _require(row["observation_ids"] == parent["observation_ids"], f"backend_realization_observation_mismatch:{actor_id}")
        _require(row["intent_ids"] == parent["intent_ids"], f"backend_realization_intent_mismatch:{actor_id}")
    expected_parents = {
        values["actor_map"]["actor_map_id"],
        interface["interface_id"],
        values["scenario_interface"]["scenario_interface_id"],
        values["scenario_mechanism"]["mechanism_id"],
        values["shared_configuration"]["configuration_id"],
        backend_configuration["configuration_id"],
    }
    _require(set(realization["semantic_parent_ids"]) == expected_parents, "backend_realization_parent_set_mismatch")
    _require(realization["backend"] == "rule", "backend_realization_backend_mismatch")
    _require(realization["decision_interface"] == "h2epr.participant-decision.v2", "backend_realization_decision_interface_mismatch")
    _require(
        realization["implementation_id"] == expected_implementation_id,
        "backend_realization_implementation_mismatch",
    )
    _require(realization["configuration_id"] == backend_configuration["configuration_id"], "backend_realization_configuration_mismatch")
    _require(backend_configuration["configuration_kind"] == "backend_rule", "backend_configuration_kind_mismatch")
    _require(
        set(backend_configuration["semantic_parent_ids"])
        == {values["shared_configuration"]["configuration_id"], interface["interface_id"]},
        "backend_configuration_parent_set_mismatch",
    )
    settings = backend_configuration["settings"]
    _require(settings["deterministic"] and settings["model_access"] == "denied" and settings["network_access"] == "denied", "rule_backend_boundary_mismatch")
    coordinate_ticks = {row["coordinate_id"]: row["logical_tick"] for row in scenario["timeline"]}
    message_kinds = _unique(mechanism["message_kinds"], "message_kind", "message_kind")
    route_pairs = {
        (row["source_id"], row["target_id"]): row
        for row in scenario["communication_routes"]
    }
    rule_ids: set[str] = set()
    rule_slots: set[tuple[str, int, int]] = set()
    used_intents: set[str] = set()
    for rule in settings["decision_rules"]:
        rule_id = rule["rule_id"]
        _require(rule_id not in rule_ids, f"rule_id_duplicate:{rule_id}")
        rule_ids.add(rule_id)
        actor_id = rule["actor_id"]
        _require(actor_id in active_ids, f"rule_actor_unknown:{rule_id}")
        if "coordinate_id" in rule:
            _require(rule["coordinate_id"] in coordinate_ticks, f"rule_coordinate_unknown:{rule_id}")
            ticks = [coordinate_ticks[rule["coordinate_id"]]]
        else:
            activation = rule["activation"]
            start_id, end_id = activation["start_coordinate_id"], activation["end_coordinate_id"]
            _require(start_id in coordinate_ticks and end_id in coordinate_ticks,
                     f"rule_activation_coordinate_unknown:{rule_id}")
            start, end = coordinate_ticks[start_id], coordinate_ticks[end_id]
            _require(start <= end, f"rule_activation_window_reversed:{rule_id}")
            ticks = range(start, end + 1)
        for tick in ticks:
            slot = actor_id, tick, rule["priority"]
            _require(slot not in rule_slots, f"rule_priority_slot_duplicate:{rule_id}")
            rule_slots.add(slot)
        action_type = rule["action"]["action_type"]
        _require(action_type in interface_by_actor[actor_id]["intent_ids"], f"rule_action_not_permitted:{rule_id}")
        used_intents.add(action_type)
        handler = next(row for row in mechanism["intent_handlers"] if row["intent_id"] == action_type)
        target = rule["action"]["parameters"].get(handler["target_parameter"])
        _require(target in handler["eligible_targets"], f"rule_action_target_invalid:{rule_id}")
        for guard in rule["guards"]:
            if guard["kind"] == "state":
                fields = {_state_field_key(row): row for row in mechanism["state_fields"]}
                _require(
                    _condition_field(guard) in fields,
                    f"rule_guard_field_unknown:{rule_id}",
                )
                field = fields[_condition_field(guard)]
                _require(field["visibility"] == "public" or (
                    field["visibility"] == "actor_private" and field["entity_id"] == actor_id
                ), f"rule_guard_state_visibility_forbidden:{rule_id}")
            else:
                _require(guard["message_kind"] in message_kinds, f"rule_guard_message_kind_unknown:{rule_id}")
                kind = message_kinds[guard["message_kind"]]
                _require(actor_id in kind["eligible_recipients"], f"rule_guard_recipient_ineligible:{rule_id}")
                if "sender_id" in guard:
                    _require(guard["sender_id"] in kind["eligible_senders"], f"rule_guard_sender_ineligible:{rule_id}")
        for message in rule["messages"]:
            kind = message["message_type"]
            recipient = message["recipient_id"]
            _require(kind in message_kinds, f"rule_message_kind_unknown:{rule_id}")
            declaration = message_kinds[kind]
            _require(actor_id in declaration["eligible_senders"], f"rule_message_sender_ineligible:{rule_id}")
            _require(recipient in declaration["eligible_recipients"], f"rule_message_recipient_ineligible:{rule_id}")
            _require((actor_id, recipient) in route_pairs, f"rule_message_route_missing:{rule_id}")
    declared_non_noop = {row["intent_id"] for row in mechanism["intent_handlers"]} - {"no_op"}
    _require(used_intents - {"no_op"} == declared_non_noop, "rule_intent_coverage_mismatch")

    derived_backend_receipt = _derive_rule_configuration_admission_receipt(
        configuration=backend_configuration,
        shared_configuration=values["shared_configuration"],
        participant_interface=interface,
        mechanism=mechanism,
    )
    _require(
        backend_configuration_admission == derived_backend_receipt,
        "backend_configuration_admission_receipt_not_independently_derived",
    )

    source_rows = realization["implementation_sources"]
    _require(len(source_rows) == len({row["relative_path"] for row in source_rows}), "implementation_source_duplicate")
    for row in source_rows:
        relative = Path(row["relative_path"])
        _require(not relative.is_absolute() and ".." not in relative.parts, "implementation_source_path_unsafe")
        path = assets.project_root / relative
        _require(path.is_file() and not path.is_symlink(), f"implementation_source_missing:{row['relative_path']}")
        _require(file_sha256(path) == row["sha256"], f"implementation_source_hash_mismatch:{row['relative_path']}")


def _compiled_participants(values: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    roster = values["roster"]
    actor_map = values["actor_map"]
    result = {
        "schema_version": "h2epr.compiled-participants.v2",
        "event_id": roster["event_id"],
        "roster_id": roster["roster_id"],
        "actor_map_id": actor_map["actor_map_id"],
        "participant_count": roster["participant_count"],
        "occurrence_count": roster["occurrence_count"],
        "source_id_gaps": copy.deepcopy(roster["source_id_gaps"]),
        "participants": copy.deepcopy(roster["participants"]),
        "mappings": copy.deepcopy(actor_map["mappings"]),
        "runtime_actors": copy.deepcopy(actor_map["runtime_actors"]),
    }
    _validate(result, "compiled-participants.schema.json", "compiled_participants", version=2)
    return result
