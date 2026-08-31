"""Fail-closed carrier projection for the bounded Note7 remedy lineage.

The accepted Scenario Configuration remains non-executable. This module pins
that release and projects only seven accepted participant intents across the
Samsung--regional--outlet--consumer slice. It adds no participant behavior and
does not start a simulator.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from h2epr.artifacts.provenance import runtime_field
from h2epr.bundles.canonical import sha256_value
from h2epr.configuration import ScenarioConfigurationAdmission, load_scenario_configuration


BINDING_FORMAT = "h2epr.bounded-lineage-binding.v0_1"
RELEASE_FORMAT = "h2epr.bounded-lineage-binding-release.v0_1"
BINDING_ID = "h2epr.0481.samsung-regional-outlet-consumer.binding.v0_1"
EVENT_ID = "H2EPR-0481"
FIXTURE_SOURCE_REF = "fixture.h2epr.0481.remedy_lineage.positive.v0_1"

_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_STABLE_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,191}$")
_VALUE_TYPES = frozenset(
    {"enum", "integer", "nullable_time_interval", "sha256", "stable_id", "stable_id_array"}
)
_EXPECTED_ACTORS = (
    "actor.0481.interface.samsung-crisis",
    "actor.0481.unit.samsung-regional-singapore",
    "actor.0481.unit.outlet-singapore-channel",
    "actor.0481.unit.consumer-primary",
)
_EXPECTED_CAPABILITIES = (
    "samsung_crisis_decision_interface",
    "samsung_regional_implementation_units",
    "carrier_and_retail_remedy_outlets",
    "note7_owners_and_prospective_consumers",
)
_EXPECTED_ACTIONS = (
    "samsung.issue_product_flow_direction",
    "samsung.announce_replacement_program",
    "regional.coordinate_local_partner_response",
    "regional.propose_local_remedy",
    "outlet.set_local_product_posture",
    "consumer.request_exchange_or_refund",
    "outlet.respond_to_remedy_request",
)
_EXPECTED_POLICIES = {
    "POL-0481-AUTH-01": "h2epr.policy.0481.auth.capacity_scope.v0_1",
    "POL-0481-INFO-01": "h2epr.policy.0481.info.source_delivery.v0_1",
    "POL-0481-LIFECYCLE-01": "h2epr.policy.0481.lifecycle.typed_idempotency.v0_1",
    "POL-0481-PRODUCT-01": "h2epr.policy.0481.product.posture_result.v0_1",
    "POL-0481-REMEDY-01": "h2epr.policy.0481.remedy.offer_request_response.v0_1",
    "POL-0481-ROUTE-01": "h2epr.policy.0481.route.exact_delivery.v0_1",
    "POL-0481-TIME-01": "h2epr.policy.0481.time.partial_order.v0_1",
}
_EXPECTED_UNBOUND = ("POL-0481-HAZARD-01", "POL-0481-PUBLIC-ACTION-01")
_EXPECTED_IMPLEMENTATION_PATHS = {
    "scenario_package": "src/h2epr/scenarios/samsung_note7_battery_recall/__init__.py",
    "carrier_loader": "src/h2epr/scenarios/samsung_note7_battery_recall/lineage_v0_1/binding.py",
    "environment_policies": "src/h2epr/scenarios/samsung_note7_battery_recall/lineage_v0_1/environment.py",
    "participant_policies": "src/h2epr/scenarios/samsung_note7_battery_recall/lineage_v0_1/policies.py",
    "public_api": "src/h2epr/scenarios/samsung_note7_battery_recall/lineage_v0_1/__init__.py",
}
_EXPECTED_SCOPE_KEYS = {
    "lineage_id",
    "purpose",
    "actor_ids",
    "capability_ids",
    "source_route_ids",
    "semantic_intent_sequence",
    "bound_policy_ids",
    "unbound_policy_ids",
    "excluded_actor_count",
    "excluded_intent_count",
    "logical_tick_start",
    "logical_tick_end",
    "full_configuration_execution_enabled",
    "simulation_enabled",
    "historical_validity_claim",
    "scientific_validity_claim",
    "positive_fixture_exposure",
}
_EXPECTED_DERIVED_INVENTORY = {
    "semantic_products": 8,
    "decision_and_population_commitments": 22,
    "observation_placements": 40,
    "private_state_placements": 28,
    "intent_placements": 37,
    "selected_observation_placements": 20,
    "selected_private_state_placements": 15,
    "selected_decision_placements": 12,
    "selected_intent_placements": 20,
    "bound_intent_placements": 7,
}
_ACTOR_KEYS = {
    "actor_id",
    "entity_id",
    "assembly_kind",
    "unit_id",
    "participant_product_id",
    "capability_id",
    "selected_capacity_id",
    "host_institution_id",
    "assignment_id",
    "authority_record_id",
    "authority_graph_id",
    "resource_owner_id",
    "access_scope_ids",
    "definition_sha256",
    "representation_class",
}
_ACTION_KEYS = {
    "action_key",
    "actor_id",
    "capability_id",
    "reader_intent_id",
    "commitment_ids",
    "observation_ids",
    "authority_ref_ids",
    "target_entity_ids",
    "lifecycle_family",
    "object_id_parameter",
    "object_version_parameter",
    "message_route_id",
    "forbidden_self_results",
    "parameters",
}
_FUTURE_TOKEN = re.compile(r"(?:^|[._:/-])2017(?:$|[._:/-])", re.IGNORECASE)


class Note7LineageBindingError(ValueError):
    """The Note7 binding, upstream identity, or carrier projection failed."""


class _DuplicateKey(ValueError):
    pass


def _fail(code: str, detail: str = "") -> None:
    raise Note7LineageBindingError(code + (f":{detail}" if detail else ""))


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey(key)
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(value)


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        _fail("NOTE7_LINEAGE_JSON_INVALID", label)
        raise AssertionError from exc
    if not isinstance(value, dict):
        _fail("NOTE7_LINEAGE_JSON_OBJECT_REQUIRED", label)
    return value


def _exact(value: Mapping[str, Any], keys: set[str], label: str) -> None:
    if set(value) != keys:
        _fail("NOTE7_LINEAGE_FIELDS_MISMATCH", label)


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        _fail("NOTE7_LINEAGE_STRING_INVALID", label)
    return value


def _stable(value: Any, label: str) -> str:
    result = _string(value, label)
    if _STABLE_ID.fullmatch(result) is None:
        _fail("NOTE7_LINEAGE_STABLE_ID_INVALID", label)
    return result


def _reject_future_reference(value: Any, label: str) -> None:
    """Keep the bounded 2016 carrier surface isolated from future evidence."""

    if isinstance(value, str):
        if _FUTURE_TOKEN.search(value) or value.lower().startswith("2017-"):
            _fail("NOTE7_LINEAGE_FUTURE_REFERENCE_FORBIDDEN", label)
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_future_reference(key, label)
            _reject_future_reference(item, label)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _reject_future_reference(item, label)


def _digest(value: Any, label: str) -> str:
    result = _string(value, label)
    if _SHA256.fullmatch(result) is None:
        _fail("NOTE7_LINEAGE_SHA256_INVALID", label)
    return result


def _integer(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _fail("NOTE7_LINEAGE_INTEGER_INVALID", label)
    return value


def _boolean(value: Any, label: str) -> bool:
    if type(value) is not bool:
        _fail("NOTE7_LINEAGE_BOOLEAN_INVALID", label)
    return value


def _object(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail("NOTE7_LINEAGE_OBJECT_REQUIRED", label)
    return value


def _array(value: Any, label: str) -> Sequence[Any]:
    if not isinstance(value, (list, tuple)):
        _fail("NOTE7_LINEAGE_ARRAY_REQUIRED", label)
    return value


def _ids(value: Any, label: str, *, empty: bool = False, sorted_: bool = False) -> tuple[str, ...]:
    result = tuple(_stable(item, label) for item in _array(value, label))
    if (not result and not empty) or len(result) != len(set(result)):
        _fail("NOTE7_LINEAGE_ID_ARRAY_INVALID", label)
    if sorted_ and result != tuple(sorted(result)):
        _fail("NOTE7_LINEAGE_ID_ARRAY_UNSORTED", label)
    return result


def _inside(root: Path, value: Any, label: str) -> Path:
    relative = Path(_string(value, label))
    if relative.is_absolute() or ".." in relative.parts:
        _fail("NOTE7_LINEAGE_PATH_UNSAFE", label)
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        _fail("NOTE7_LINEAGE_PATH_INVALID", label)
    return path


def _project_root(path: Path, supplied: str | Path | None) -> Path:
    if supplied is not None:
        root = Path(supplied).resolve()
    else:
        roots = [
            parent
            for parent in path.resolve().parents
            if parent.joinpath("src/h2epr").is_dir() and parent.joinpath("contracts/v1").is_dir()
        ]
        if not roots:
            _fail("NOTE7_LINEAGE_PROJECT_ROOT_NOT_FOUND")
        root = roots[0]
    if not root.joinpath("src/h2epr").is_dir():
        _fail("NOTE7_LINEAGE_PROJECT_ROOT_INVALID")
    return root


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    return value


def _time(value: Any, label: str, *, nullable: bool = False) -> Any:
    if value is None and nullable:
        return None
    row = _object(value, label)
    _exact(row, {"lower", "upper", "precision", "timezone", "uncertainty"}, label)
    try:
        lower = datetime.fromisoformat(_string(row["lower"], label))
        upper = datetime.fromisoformat(_string(row["upper"], label))
    except ValueError:
        _fail("NOTE7_LINEAGE_TIME_INVALID", label)
    if lower.tzinfo is None or upper.tzinfo is None or lower > upper:
        _fail("NOTE7_LINEAGE_TIME_INVALID", label)
    return copy.deepcopy(dict(row))


def _runtime_values(fields: Sequence[Mapping[str, Any]], label: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for index, field in enumerate(fields):
        if not isinstance(field, Mapping) or set(field) != {"field_name", "runtime_value"}:
            _fail("NOTE7_LINEAGE_RUNTIME_FIELD_INVALID", f"{label}.{index}")
        name = _stable(field["field_name"], label)
        runtime = _object(field["runtime_value"], label)
        if "value" not in runtime or name in result:
            _fail("NOTE7_LINEAGE_RUNTIME_FIELD_INVALID", f"{label}.{index}")
        result[name] = runtime["value"]
    return result


def _inventory(text: str, heading: str) -> Mapping[str, tuple[str, ...]]:
    start = text.find(heading)
    if start < 0:
        _fail("NOTE7_LINEAGE_INVENTORY_GRAMMAR_MISMATCH", heading)
    next_heading = text.find("\n## ", start + len(heading))
    section = text[start : len(text) if next_heading < 0 else next_heading]
    result: dict[str, tuple[str, ...]] = {}
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        capability = re.fullmatch(r"`([^`]+)`", cells[0]) if len(cells) == 2 else None
        if capability:
            values = tuple(re.findall(r"`([^`]+)`", cells[1]))
            if not values or len(values) != len(set(values)):
                _fail("NOTE7_LINEAGE_INVENTORY_GRAMMAR_MISMATCH", heading)
            result[capability.group(1)] = values
    if len(result) != 8:
        _fail("NOTE7_LINEAGE_INVENTORY_GRAMMAR_MISMATCH", heading)
    return MappingProxyType(result)


@dataclass(frozen=True)
class ParameterContract:
    name: str
    value_type: str
    carrier: str
    values: tuple[str, ...]

    def validate(self, value: Any) -> Any:
        _reject_future_reference(value, self.name)
        if self.value_type == "stable_id":
            return _stable(value, self.name)
        if self.value_type == "integer":
            return _integer(value, self.name)
        if self.value_type == "sha256":
            return _digest(value, self.name)
        if self.value_type == "stable_id_array":
            return list(_ids(value, self.name, sorted_=True))
        if self.value_type == "nullable_time_interval":
            return _time(value, self.name, nullable=True)
        if self.value_type == "enum":
            result = _stable(value, self.name)
            if result not in self.values:
                _fail("NOTE7_LINEAGE_VALUE_OUTSIDE_DOMAIN", self.name)
            return result
        raise AssertionError(self.value_type)


@dataclass(frozen=True)
class RouteContract:
    route_id: str
    source_opening_route_id: str
    source_actor_id: str
    target_actor_id: str
    required_source_capacity_id: str
    channel_id: str
    performative: str
    confidentiality: str
    latency_ticks: int

    def as_v1_definition(self) -> dict[str, Any]:
        return {
            "route_id": self.route_id,
            "source_id": self.source_actor_id,
            "target_id": self.target_actor_id,
            "performative": self.performative,
            "channel": self.channel_id,
            "confidentiality": self.confidentiality,
            "latency_ticks": self.latency_ticks,
            "expiry_policy": "deliver_if_due_before_expiry",
            "review_state": "reviewed",
        }


@dataclass(frozen=True)
class ActionContract:
    action_key: str
    actor_id: str
    capability_id: str
    reader_intent_id: str
    commitment_ids: tuple[str, ...]
    observation_ids: tuple[str, ...]
    authority_ref_ids: tuple[str, ...]
    target_entity_ids: tuple[str, ...]
    lifecycle_family: str
    object_id_parameter: str
    object_version_parameter: str
    parameters: tuple[ParameterContract, ...]
    message_route_id: str | None
    forbidden_self_results: tuple[str, ...]

    @property
    def action_type(self) -> str:
        return f"h2epr.action.0481.{self.capability_id}.{self.reader_intent_id}"

    @property
    def action_schema_version(self) -> str:
        return f"h2epr.intent.0481.{self.capability_id}.{self.reader_intent_id}.v0_1"

    @property
    def parameter_by_name(self) -> Mapping[str, ParameterContract]:
        return MappingProxyType({row.name: row for row in self.parameters})


@dataclass(frozen=True)
class Note7LineageBinding:
    release_id: str
    release_manifest_sha256: str
    binding_sha256: str
    implementation_sha256s: Mapping[str, str]
    configuration: ScenarioConfigurationAdmission
    admission_receipt_sha256: str
    actor_ids: tuple[str, ...]
    actors: Mapping[str, Mapping[str, Any]]
    policies: Mapping[str, str]
    unbound_policy_ids: tuple[str, ...]
    routes: Mapping[str, RouteContract]
    observation_ids: Mapping[str, tuple[str, ...]]
    actions: Mapping[str, ActionContract]
    document: Mapping[str, Any]

    def action_definition(self, action_key: str) -> dict[str, Any]:
        action = self._action(action_key)
        return {
            "action_type": action.action_type,
            "version": action.action_schema_version,
            "allowed_representation_classes": [self.actors[action.actor_id]["representation_class"]],
            "parameter_names": sorted(row.name for row in action.parameters),
            "state_changing": True,
            "review_state": "reviewed",
        }

    def route_definition(self, route_id: str) -> dict[str, Any]:
        try:
            return self.routes[route_id].as_v1_definition()
        except KeyError as exc:
            _fail("NOTE7_LINEAGE_ROUTE_UNKNOWN", route_id)
            raise AssertionError from exc

    def project_observation(self, action_key: str, *, observation_id: str, values: Mapping[str, Any]) -> dict[str, Any]:
        action = self._action(action_key)
        _reject_future_reference(values, f"observation.{action_key}")
        if set(values) != set(action.observation_ids):
            _fail("NOTE7_LINEAGE_OBSERVATION_INVENTORY_MISMATCH", action_key)
        fields = [
            runtime_field(
                f"obs.{action.capability_id}.{name}",
                _stable(values[name], f"observation.{name}"),
                source_kind="synthetic",
                source_ref_id=FIXTURE_SOURCE_REF,
                claim_ref_ids=("fixture.synthetic.conformance_only",),
                derivation_class="assumed",
                availability_at_t0="not_applicable",
                visibility="runtime_private",
                visibility_scope_ids=(action.actor_id,),
                consumers=(action.actor_id, "world.reducer"),
            )
            for name in sorted(values)
        ]
        return {"observation_id": _stable(observation_id, "observation_id"), "fields": fields}

    def read_observation(self, action_key: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        action = self._action(action_key)
        _exact(payload, {"observation_id", "fields"}, "observation")
        values = _runtime_values(payload["fields"], "observation.fields")
        expected = {f"obs.{action.capability_id}.{name}": name for name in action.observation_ids}
        if set(values) != set(expected):
            _fail("NOTE7_LINEAGE_OBSERVATION_CARRIER_MISMATCH", action_key)
        _reject_future_reference(values, f"observation.{action_key}")
        return MappingProxyType({reader: _stable(values[field], reader) for field, reader in expected.items()})

    def project_action(
        self,
        action_key: str,
        *,
        intent_id: str,
        run_id: str,
        logical_tick: int,
        decision_ref: str,
        observation_refs: Sequence[str],
        semantic_parameters: Mapping[str, Any],
        earliest_effect_time: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        contract = self._action(action_key)
        if set(semantic_parameters) != set(contract.parameter_by_name):
            _fail("NOTE7_LINEAGE_PARAMETER_INVENTORY_MISMATCH", action_key)
        values = {name: contract.parameter_by_name[name].validate(value) for name, value in semantic_parameters.items()}
        expiry = values[next(row.name for row in contract.parameters if row.carrier == "expiry_time")]
        fields = [
            runtime_field(
                row.name,
                copy.deepcopy(values[row.name]),
                source_kind="synthetic",
                source_ref_id=FIXTURE_SOURCE_REF,
                claim_ref_ids=("fixture.synthetic.conformance_only",),
                derivation_class="assumed",
                availability_at_t0="not_applicable",
                visibility="runtime_private",
                visibility_scope_ids=(contract.actor_id,),
                consumers=(contract.actor_id, "world.reducer"),
            )
            for row in sorted(contract.parameters, key=lambda item: item.name)
            if row.carrier == "parameters"
        ]
        payload = {
            "intent_id": _stable(intent_id, "intent_id"),
            "run_id": _stable(run_id, "run_id"),
            "logical_tick": _integer(logical_tick, "logical_tick"),
            "actor_id": contract.actor_id,
            "action_type": contract.action_type,
            "action_schema_version": contract.action_schema_version,
            "target_entity_ids": list(contract.target_entity_ids),
            "parameters": fields,
            "claimed_authority_refs": list(contract.authority_ref_ids),
            "resource_offer_or_request": [],
            "earliest_effect_time": None if earliest_effect_time is None else _time(earliest_effect_time, "earliest_effect_time"),
            "expiry_time": expiry,
            "observation_refs": list(_ids(observation_refs, "observation_refs")),
            "decision_ref": _stable(decision_ref, "decision_ref"),
            "idempotency_key": "idem.action." + sha256_value({"binding_id": BINDING_ID, "action_key": action_key, "actor_id": contract.actor_id, "object_id": values[contract.object_id_parameter], "object_version": values[contract.object_version_parameter], "parameters": values})[:48],
            "visibility": "restricted",
        }
        self.validate_action(action_key, payload)
        return payload

    def validate_action(self, action_key: str, payload: Mapping[str, Any]) -> None:
        contract = self._action(action_key)
        _exact(payload, {"intent_id", "run_id", "logical_tick", "actor_id", "action_type", "action_schema_version", "target_entity_ids", "parameters", "claimed_authority_refs", "resource_offer_or_request", "earliest_effect_time", "expiry_time", "observation_refs", "decision_ref", "idempotency_key", "visibility"}, f"action.{action_key}")
        if (
            payload["actor_id"] != contract.actor_id
            or payload["action_type"] != contract.action_type
            or payload["action_schema_version"] != contract.action_schema_version
            or tuple(payload["target_entity_ids"]) != contract.target_entity_ids
            or tuple(payload["claimed_authority_refs"]) != contract.authority_ref_ids
            or payload["resource_offer_or_request"] != []
            or payload["visibility"] != "restricted"
        ):
            _fail("NOTE7_LINEAGE_ACTION_ENVELOPE_MISMATCH", action_key)
        values = _runtime_values(payload["parameters"], f"action.{action_key}.parameters")
        expected = {row.name for row in contract.parameters if row.carrier == "parameters"}
        if set(values) != expected:
            _fail("NOTE7_LINEAGE_ACTION_CARRIER_MISMATCH", action_key)
        expiry = next(row for row in contract.parameters if row.carrier == "expiry_time")
        values[expiry.name] = expiry.validate(payload["expiry_time"])
        values = {name: contract.parameter_by_name[name].validate(value) for name, value in values.items()}
        _reject_future_reference(payload["earliest_effect_time"], f"action.{action_key}.earliest_effect_time")
        actor = self.actors[contract.actor_id]
        if values.get("capacity_id") != actor["selected_capacity_id"]:
            _fail("NOTE7_LINEAGE_ACTION_CAPACITY_MISMATCH", action_key)
        if contract.message_route_id:
            route = self.routes[contract.message_route_id]
            if values.get("sender_id") != contract.actor_id or values.get("recipient_id") != route.target_actor_id or values.get("route_id") != route.route_id:
                _fail("NOTE7_LINEAGE_ACTION_ROUTE_ENVELOPE_MISMATCH", action_key)
        if set(contract.forbidden_self_results).intersection(values):
            _fail("NOTE7_LINEAGE_RESULT_CONFLATION", action_key)
        expected_key = "idem.action." + sha256_value({"binding_id": BINDING_ID, "action_key": action_key, "actor_id": contract.actor_id, "object_id": values[contract.object_id_parameter], "object_version": values[contract.object_version_parameter], "parameters": values})[:48]
        if payload["idempotency_key"] != expected_key:
            _fail("NOTE7_LINEAGE_ACTION_IDEMPOTENCY_MISMATCH", action_key)

    def semantic_values(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        values = _runtime_values(payload["parameters"], "action.parameters")
        values["expiry_time"] = copy.deepcopy(payload["expiry_time"])
        return values

    def project_message(self, action_key: str, action: Mapping[str, Any], *, message_intent_id: str, earliest_delivery_time: Mapping[str, Any], correlation_ids: Sequence[str]) -> dict[str, Any]:
        contract = self._action(action_key)
        self.validate_action(action_key, action)
        if contract.message_route_id is None:
            _fail("NOTE7_LINEAGE_ACTION_HAS_NO_MESSAGE_ROUTE", action_key)
        route = self.routes[contract.message_route_id]
        correlations = _ids(correlation_ids, "correlation_ids")
        if action["intent_id"] not in correlations:
            _fail("NOTE7_LINEAGE_ACTION_CORRELATION_MISSING", action_key)
        payload = {
            "message_intent_id": _stable(message_intent_id, "message_intent_id"),
            "run_id": action["run_id"],
            "logical_tick": action["logical_tick"],
            "sender_id": route.source_actor_id,
            "recipient_ids": [route.target_actor_id],
            "performative": route.performative,
            "content_schema_version": f"h2epr.message.0481.{contract.capability_id}.{contract.reader_intent_id}.v0_1",
            "structured_content": copy.deepcopy(list(action["parameters"])),
            "channel": route.channel_id,
            "confidentiality": route.confidentiality,
            "created_at": copy.deepcopy(action["earliest_effect_time"]),
            "earliest_delivery_time": _time(earliest_delivery_time, "earliest_delivery_time"),
            "expiry_time": copy.deepcopy(action["expiry_time"]),
            "decision_ref": action["decision_ref"],
            "idempotency_key": "idem.message." + sha256_value({"action_idempotency_key": action["idempotency_key"], "route_id": route.route_id, "binding_id": BINDING_ID})[:48],
            "correlation_ids": list(correlations),
        }
        self.validate_message(action_key, action, payload)
        return payload

    def validate_message(self, action_key: str, action: Mapping[str, Any], message: Mapping[str, Any]) -> None:
        contract = self._action(action_key)
        self.validate_action(action_key, action)
        if contract.message_route_id is None:
            _fail("NOTE7_LINEAGE_ACTION_HAS_NO_MESSAGE_ROUTE", action_key)
        route = self.routes[contract.message_route_id]
        expected_schema = f"h2epr.message.0481.{contract.capability_id}.{contract.reader_intent_id}.v0_1"
        expected_key = "idem.message." + sha256_value(
            {
                "action_idempotency_key": action["idempotency_key"],
                "route_id": route.route_id,
                "binding_id": BINDING_ID,
            }
        )[:48]
        _exact(message, {"message_intent_id", "run_id", "logical_tick", "sender_id", "recipient_ids", "performative", "content_schema_version", "structured_content", "channel", "confidentiality", "created_at", "earliest_delivery_time", "expiry_time", "decision_ref", "idempotency_key", "correlation_ids"}, f"message.{action_key}")
        if (
            message["run_id"] != action["run_id"]
            or message["logical_tick"] != action["logical_tick"]
            or message["sender_id"] != route.source_actor_id
            or tuple(message["recipient_ids"]) != (route.target_actor_id,)
            or message["performative"] != route.performative
            or message["content_schema_version"] != expected_schema
            or message["channel"] != route.channel_id
            or message["confidentiality"] != route.confidentiality
            or message["decision_ref"] != action["decision_ref"]
            or message["created_at"] != action["earliest_effect_time"]
            or message["expiry_time"] != action["expiry_time"]
            or message["idempotency_key"] != expected_key
            or action["intent_id"] not in _ids(message["correlation_ids"], "message.correlation_ids")
            or _runtime_values(message["structured_content"], "message.content") != _runtime_values(action["parameters"], "action.content")
        ):
            _fail("NOTE7_LINEAGE_MESSAGE_ENVELOPE_MISMATCH", action_key)
        _time(message["earliest_delivery_time"], "message.earliest_delivery_time")
        _reject_future_reference(message, f"message.{action_key}")

    def _action(self, action_key: str) -> ActionContract:
        try:
            return self.actions[action_key]
        except KeyError as exc:
            _fail("NOTE7_LINEAGE_ACTION_UNKNOWN", action_key)
            raise AssertionError from exc


def _parameter(value: Any, label: str) -> ParameterContract:
    row = _object(value, label)
    _exact(row, {"name", "value_type", "carrier", "values"}, label)
    value_type = _string(row["value_type"], label)
    carrier = _string(row["carrier"], label)
    values = _ids(row["values"], label, empty=True)
    if value_type not in _VALUE_TYPES or carrier not in {"parameters", "expiry_time"} or (value_type == "enum") != bool(values) or (carrier == "expiry_time") != (value_type == "nullable_time_interval"):
        _fail("NOTE7_LINEAGE_PARAMETER_CONTRACT_INVALID", label)
    return ParameterContract(_stable(row["name"], label), value_type, carrier, values)


def _receipt(path: Path, file_hash: str, receipt_hash: str) -> Mapping[str, Any]:
    if _sha256_file(path) != file_hash:
        _fail("NOTE7_LINEAGE_ADMISSION_RECEIPT_FILE_HASH_MISMATCH")
    receipt = _read_json(path, "admission_receipt")
    preimage = copy.deepcopy(receipt)
    actual = preimage.pop("receipt_sha256", None)
    if actual != receipt_hash or sha256_value(preimage) != receipt_hash or receipt.get("verdict") != "PASS_BOUNDED_CONFIGURATION_ADMISSION":
        _fail("NOTE7_LINEAGE_ADMISSION_RECEIPT_IDENTITY_MISMATCH")
    return receipt


def load_note7_lineage_binding(manifest_path: str | Path, *, expected_manifest_sha256: str, project_root: str | Path | None = None) -> Note7LineageBinding:
    """Load exactly one externally anchored Note7 bounded binding release."""

    supplied = Path(manifest_path)
    root = _project_root(supplied, project_root)
    path = supplied.resolve() if supplied.is_absolute() else (root / supplied).resolve()
    if not path.is_relative_to(root) or not path.is_file() or _sha256_file(path) != _digest(expected_manifest_sha256, "expected_manifest_sha256"):
        _fail("NOTE7_LINEAGE_MANIFEST_HASH_MISMATCH")
    manifest = _read_json(path, "manifest")
    _exact(manifest, {"schema", "release_id", "version", "status", "event_id", "manifest_sha256", "binding", "selected_products", "implementation_surfaces", "upstream", "authorization"}, "manifest")
    preimage = copy.deepcopy(manifest)
    self_hash = preimage.pop("manifest_sha256", None)
    if (
        manifest["schema"] != RELEASE_FORMAT
        or manifest["release_id"] != "H2EPR-0481-SAMSUNG-REGIONAL-OUTLET-CONSUMER-BINDING-v0.1"
        or manifest["version"] != "0.1.0"
        or manifest["event_id"] != EVENT_ID
        or manifest["status"] != "bounded_conformance_release"
        or self_hash != sha256_value(preimage)
    ):
        _fail("NOTE7_LINEAGE_MANIFEST_IDENTITY_MISMATCH")

    binding_ref = _object(manifest["binding"], "manifest.binding")
    _exact(binding_ref, {"path", "sha256"}, "manifest.binding")
    binding_path = _inside(root, binding_ref["path"], "manifest.binding.path")
    binding_hash = _digest(binding_ref["sha256"], "manifest.binding.sha256")
    if _sha256_file(binding_path) != binding_hash:
        _fail("NOTE7_LINEAGE_BINDING_HASH_MISMATCH")

    implementation_hashes: dict[str, str] = {}
    implementation_paths: dict[str, str] = {}
    for index, raw in enumerate(_array(manifest["implementation_surfaces"], "implementation_surfaces")):
        row = _object(raw, f"implementation.{index}")
        _exact(row, {"kind", "path", "sha256"}, f"implementation.{index}")
        kind = _stable(row["kind"], f"implementation.{index}.kind")
        surface = _inside(root, row["path"], f"implementation.{index}.path")
        digest = _digest(row["sha256"], f"implementation.{index}.sha256")
        if kind in implementation_hashes or _sha256_file(surface) != digest:
            _fail("NOTE7_LINEAGE_IMPLEMENTATION_SURFACE_MISMATCH", kind)
        implementation_paths[kind] = surface.relative_to(root).as_posix()
        implementation_hashes[kind] = digest
    if implementation_paths != _EXPECTED_IMPLEMENTATION_PATHS:
        _fail("NOTE7_LINEAGE_IMPLEMENTATION_SCOPE_MISMATCH")

    upstream = _object(manifest["upstream"], "upstream")
    required_upstream = {"configuration_path", "configuration_release_manifest_path", "configuration_source_sha256", "configuration_release_manifest_sha256", "configuration_canonical_sha256", "admission_receipt_path", "admission_receipt_file_sha256", "admission_receipt_sha256", "roster_release_manifest_path", "roster_release_manifest_sha256", "consolidated_mapping_manifest_path", "consolidated_mapping_manifest_sha256", "semantic_inventory_path", "semantic_inventory_sha256"}
    _exact(upstream, required_upstream, "upstream")
    admission = load_scenario_configuration(
        _inside(root, upstream["configuration_path"], "configuration_path"),
        project_root=root,
        release_manifest_path=_inside(root, upstream["configuration_release_manifest_path"], "configuration_manifest"),
        expected_source_sha256=_digest(upstream["configuration_source_sha256"], "configuration_source_sha256"),
        expected_release_manifest_sha256=_digest(upstream["configuration_release_manifest_sha256"], "configuration_manifest_sha256"),
    )
    if admission.canonical_sha256 != upstream["configuration_canonical_sha256"]:
        _fail("NOTE7_LINEAGE_CONFIGURATION_CANONICAL_MISMATCH")
    receipt = _receipt(
        _inside(root, upstream["admission_receipt_path"], "admission_receipt_path"),
        _digest(upstream["admission_receipt_file_sha256"], "admission_receipt_file_sha256"),
        _digest(upstream["admission_receipt_sha256"], "admission_receipt_sha256"),
    )
    for path_key, hash_key in (("roster_release_manifest_path", "roster_release_manifest_sha256"), ("consolidated_mapping_manifest_path", "consolidated_mapping_manifest_sha256"), ("semantic_inventory_path", "semantic_inventory_sha256")):
        if _sha256_file(_inside(root, upstream[path_key], path_key)) != _digest(upstream[hash_key], hash_key):
            _fail("NOTE7_LINEAGE_UPSTREAM_HASH_MISMATCH", path_key)
    mapping = _read_json(_inside(root, upstream["consolidated_mapping_manifest_path"], "mapping_manifest"), "mapping_manifest")
    if mapping.get("release_id") != "H2EPR-0481-CONSOLIDATED-MAPPING-v0.1" or mapping.get("coverage") != {"decision_and_population_commitments": 22, "observation_placements": 40, "private_state_placements": 28, "intent_placements": 37, "lifecycle_families": 12, "cross_object_rules": 24}:
        _fail("NOTE7_LINEAGE_MAPPING_IDENTITY_MISMATCH")
    inventory_text = _inside(root, upstream["semantic_inventory_path"], "semantic_inventory").read_text(encoding="utf-8")
    observations = _inventory(inventory_text, "### 3.1 Released observations by capability")
    intents = _inventory(inventory_text, "### 5.1 Released intents by capability")

    selected_products: dict[str, Mapping[str, Any]] = {}
    for raw in _array(manifest["selected_products"], "selected_products"):
        row = _object(raw, "selected_product")
        _exact(row, {"product_id", "capability_id", "path", "sha256"}, "selected_product")
        product_path = _inside(root, row["path"], "selected_product.path")
        capability_id = _stable(row["capability_id"], "selected_product.capability_id")
        digest = _digest(row["sha256"], "selected_product.sha256")
        if (
            _sha256_file(product_path) != digest
            or capability_id in selected_products
            or _stable(row["product_id"], "selected_product.product_id") == ""
        ):
            _fail("NOTE7_LINEAGE_SELECTED_PRODUCT_MISMATCH")
        selected_products[capability_id] = _freeze(dict(row))
    if tuple(selected_products) != _EXPECTED_CAPABILITIES:
        _fail("NOTE7_LINEAGE_SELECTED_PRODUCT_SCOPE_MISMATCH")

    document = _read_json(binding_path, "binding")
    _exact(document, {"schema", "binding_id", "version", "status", "event_id", "configuration", "scope", "derived_inventory", "actors", "policy_bindings", "routes", "observation_contracts", "actions", "decision_bindings"}, "binding")
    if (
        document["schema"] != BINDING_FORMAT
        or document["binding_id"] != BINDING_ID
        or document["version"] != "0.1.0"
        or document["event_id"] != EVENT_ID
        or document["status"] != "bounded_conformance_binding"
    ):
        _fail("NOTE7_LINEAGE_BINDING_IDENTITY_MISMATCH")
    config = _object(document["configuration"], "binding.configuration")
    expected_config = {"configuration_id": admission.configuration_id, "source_sha256": admission.source_sha256, "canonical_sha256": admission.canonical_sha256, "admission_receipt_sha256": receipt["receipt_sha256"], "mapping_profile_id": admission.mapping_profile_id, "mapping_profile_sha256": admission.mapping_profile_sha256}
    if dict(config) != expected_config:
        _fail("NOTE7_LINEAGE_CONFIGURATION_BINDING_MISMATCH")
    scope = _object(document["scope"], "scope")
    _exact(scope, _EXPECTED_SCOPE_KEYS, "scope")
    actor_ids = _ids(scope["actor_ids"], "scope.actor_ids")
    capability_ids = _ids(scope["capability_ids"], "scope.capability_ids")
    bound = _ids(scope["bound_policy_ids"], "scope.bound_policy_ids", sorted_=True)
    unbound = _ids(scope["unbound_policy_ids"], "scope.unbound_policy_ids", sorted_=True)
    if (
        actor_ids != _EXPECTED_ACTORS
        or capability_ids != _EXPECTED_CAPABILITIES
        or set(bound) != set(_EXPECTED_POLICIES)
        or unbound != _EXPECTED_UNBOUND
        or tuple(admission.document["bounded_lineage"]["participant_ids"]) != actor_ids
        or tuple(admission.document["bounded_lineage"]["semantic_intent_sequence"])
        != tuple(scope["semantic_intent_sequence"])
        or _ids(scope["source_route_ids"], "scope.source_route_ids", sorted_=True)
        != (
            "opening.0481.route.outlet-consumer",
            "opening.0481.route.regional-outlet",
            "opening.0481.route.samsung-regional",
        )
        or _stable(scope["lineage_id"], "scope.lineage_id")
        != "lineage.0481.samsung-regional-outlet-consumer.v0_1"
        or scope["purpose"] != "exact_carrier_and_positive_binding_conformance"
        or _integer(scope["excluded_actor_count"], "scope.excluded_actor_count") != 4
        or _integer(scope["excluded_intent_count"], "scope.excluded_intent_count") != 30
        or _integer(scope["logical_tick_start"], "scope.logical_tick_start") != 0
        or _integer(scope["logical_tick_end"], "scope.logical_tick_end") != 14
        or scope["positive_fixture_exposure"]
        != "full_outcome_exposed_synthetic_conformance_only"
    ):
        _fail("NOTE7_LINEAGE_SCOPE_MISMATCH")
    for key in ("full_configuration_execution_enabled", "simulation_enabled", "historical_validity_claim", "scientific_validity_claim"):
        if _boolean(scope[key], f"scope.{key}"):
            _fail("NOTE7_LINEAGE_SCOPE_ESCALATION", key)
    if dict(_object(document["derived_inventory"], "derived_inventory")) != _EXPECTED_DERIVED_INVENTORY:
        _fail("NOTE7_LINEAGE_DERIVED_INVENTORY_MISMATCH")

    configured_named = {row["actor_id"]: row for row in admission.document["named_actors"]}
    configured_population = {row["actor_id"]: row for row in admission.document["population_actors"]}
    configured_units = {row["actor_id"]: row for row in admission.document["population_units"]}
    actors: dict[str, Mapping[str, Any]] = {}
    for raw in _array(document["actors"], "actors"):
        row = dict(_object(raw, "actor"))
        _exact(row, _ACTOR_KEYS, "actor")
        actor_id = row.get("actor_id")
        source = configured_named.get(actor_id) or configured_population.get(actor_id)
        if source is None or actor_id in actors or row["capability_id"] != source["capability_id"]:
            _fail("NOTE7_LINEAGE_ACTOR_MISMATCH", str(actor_id))
        if actor_id in configured_named:
            product_id = source["participant_product_id"]
            expected_capacity = "capacity.0481.samsung.product-safety"
            expected_authority = "opening.0481.authority.samsung"
        else:
            product_id = configured_units[actor_id]["population_product_id"]
            expected_capacity = source["capacity_id"]
            expected_authority = source["assignment_id"]
        product = selected_products[row["capability_id"]]
        expected_representation = (
            "autonomous_participant_agent"
            if actor_id in configured_named
            else "aggregate_population_agent"
        )
        if (
            row["participant_product_id"] != product_id
            or _digest(row["definition_sha256"], "actor.definition_sha256") != product["sha256"]
            or row["selected_capacity_id"] != expected_capacity
            or row["authority_record_id"] != expected_authority
            or row["representation_class"] != expected_representation
            or not _ids(row["access_scope_ids"], "actor.access_scope_ids")
        ):
            _fail("NOTE7_LINEAGE_ACTOR_MISMATCH", actor_id)
        actors[actor_id] = _freeze(row)
    if tuple(actors) != actor_ids:
        _fail("NOTE7_LINEAGE_ACTOR_SCOPE_MISMATCH")

    policy_selections = {row["policy_id"]: row for row in admission.document["policy_selections"]}
    policies: dict[str, str] = {}
    for raw in _array(document["policy_bindings"], "policy_bindings"):
        row = _object(raw, "policy_binding")
        _exact(
            row,
            {"policy_id", "semantic_version", "selection", "implementation_id", "status"},
            "policy_binding",
        )
        policy_id = row["policy_id"]
        if policy_id in policies or row.get("implementation_id") != _EXPECTED_POLICIES.get(policy_id) or row.get("selection") != policy_selections[policy_id]["selection"] or row.get("semantic_version") != "0.1.0" or row.get("status") != "bound_for_bounded_lineage_only":
            _fail("NOTE7_LINEAGE_POLICY_BINDING_MISMATCH", str(policy_id))
        policies[policy_id] = row["implementation_id"]
    if set(policies) != set(bound):
        _fail("NOTE7_LINEAGE_POLICY_BINDING_INCOMPLETE")

    opening_routes = {row["id"]: row for row in admission.document["initial_records"] if row["family"] == "institutional_route"}
    routes: dict[str, RouteContract] = {}
    for raw in _array(document["routes"], "routes"):
        row = _object(raw, "route")
        _exact(
            row,
            {
                "route_id",
                "source_opening_route_id",
                "source_actor_id",
                "target_actor_id",
                "required_source_capacity_id",
                "channel_id",
                "performative",
                "confidentiality",
                "latency_ticks",
            },
            "route",
        )
        route = RouteContract(
            _stable(row["route_id"], "route.route_id"),
            _stable(row["source_opening_route_id"], "route.source_opening_route_id"),
            _stable(row["source_actor_id"], "route.source_actor_id"),
            _stable(row["target_actor_id"], "route.target_actor_id"),
            _stable(row["required_source_capacity_id"], "route.required_source_capacity_id"),
            _stable(row["channel_id"], "route.channel_id"),
            _stable(row["performative"], "route.performative"),
            _stable(row["confidentiality"], "route.confidentiality"),
            _integer(row["latency_ticks"], "route.latency_ticks"),
        )
        source = actors.get(route.source_actor_id)
        opening = opening_routes.get(route.source_opening_route_id)
        endpoints = set(opening["endpoints"]["side_a"] + opening["endpoints"]["side_b"]) if opening else set()
        if route.route_id in routes or source is None or route.target_actor_id not in actors or route.required_source_capacity_id != source["selected_capacity_id"] or {route.source_actor_id, route.target_actor_id} - endpoints or route.latency_ticks != 1:
            _fail("NOTE7_LINEAGE_ROUTE_MISMATCH", route.route_id)
        routes[route.route_id] = route

    observation_contracts: dict[str, tuple[str, ...]] = {}
    for raw in _array(document["observation_contracts"], "observation_contracts"):
        row = _object(raw, "observation_contract")
        _exact(row, {"capability_id", "reader_observation_ids"}, "observation_contract")
        capability = row["capability_id"]
        ids = _ids(row["reader_observation_ids"], "reader_observation_ids")
        if capability in observation_contracts or ids != observations[capability]:
            _fail("NOTE7_LINEAGE_OBSERVATION_CONTRACT_MISMATCH", capability)
        observation_contracts[capability] = ids
    if tuple(observation_contracts) != capability_ids:
        _fail("NOTE7_LINEAGE_OBSERVATION_SCOPE_MISMATCH")

    actions: dict[str, ActionContract] = {}
    for raw in _array(document["actions"], "actions"):
        row = _object(raw, "action")
        _exact(row, _ACTION_KEYS, "action")
        parameters = tuple(_parameter(item, "action.parameter") for item in row["parameters"])
        names = [item.name for item in parameters]
        message_route = row["message_route_id"]
        contract = ActionContract(row["action_key"], row["actor_id"], row["capability_id"], row["reader_intent_id"], _ids(row["commitment_ids"], "commitments"), _ids(row["observation_ids"], "observations"), _ids(row["authority_ref_ids"], "authority"), _ids(row["target_entity_ids"], "targets"), row["lifecycle_family"], row["object_id_parameter"], row["object_version_parameter"], parameters, None if message_route is None else _stable(message_route, "message_route"), _ids(row["forbidden_self_results"], "forbidden"))
        if contract.action_key in actions or contract.actor_id not in actors or actors[contract.actor_id]["capability_id"] != contract.capability_id or contract.reader_intent_id not in intents[contract.capability_id] or not set(contract.observation_ids) <= set(observation_contracts[contract.capability_id]) or len(names) != len(set(names)) or sum(item.carrier == "expiry_time" for item in parameters) != 1 or contract.object_id_parameter not in names or contract.object_version_parameter not in names or (contract.message_route_id is not None and contract.message_route_id not in routes):
            _fail("NOTE7_LINEAGE_ACTION_CONTRACT_MISMATCH", contract.action_key)
        actions[contract.action_key] = contract
    if tuple(actions) != _EXPECTED_ACTIONS or tuple(f"{row.capability_id}.{row.reader_intent_id}" for row in actions.values()) != tuple(scope["semantic_intent_sequence"]):
        _fail("NOTE7_LINEAGE_ACTION_SCOPE_MISMATCH")

    decisions = _array(document["decision_bindings"], "decision_bindings")
    for row in decisions:
        _exact(
            _object(row, "decision_binding"),
            {"decision_policy_id", "actor_id", "action_keys", "status"},
            "decision_binding",
        )
    if (
        len(decisions) != 4
        or {row["actor_id"] for row in decisions} != set(actor_ids)
        or {key for row in decisions for key in row["action_keys"]} != set(actions)
        or any(row["status"] != "positive_branch_only" for row in decisions)
        or any(not _stable(row["decision_policy_id"], "decision_policy_id") for row in decisions)
    ):
        _fail("NOTE7_LINEAGE_DECISION_BINDING_MISMATCH")
    authorization = _object(manifest["authorization"], "authorization")
    _exact(
        authorization,
        {
            "owner_decisions",
            "owner_decision_path",
            "owner_decision_sha256",
            "bounded_projection_authorized",
            "bounded_policy_binding_authorized",
            "full_roster_runtime_authorized",
            "simulation_authorized",
            "evaluation_authorized",
            "historical_validity_claim_authorized",
        },
        "authorization",
    )
    owner_path = _inside(root, authorization["owner_decision_path"], "authorization.owner_decision_path")
    if (
        _ids(authorization["owner_decisions"], "authorization.owner_decisions")
        != ("OD-0481-BND-01", "OD-0481-BND-02", "OD-0481-BND-03", "OD-0481-BND-04")
        or _sha256_file(owner_path)
        != _digest(authorization["owner_decision_sha256"], "authorization.owner_decision_sha256")
        or authorization["bounded_projection_authorized"] is not True
        or authorization["bounded_policy_binding_authorized"] is not True
        or any(
            authorization[key] is not False
            for key in (
                "full_roster_runtime_authorized",
                "simulation_authorized",
                "evaluation_authorized",
                "historical_validity_claim_authorized",
            )
        )
    ):
        _fail("NOTE7_LINEAGE_AUTHORIZATION_MISMATCH")

    return Note7LineageBinding(
        release_id=manifest["release_id"],
        release_manifest_sha256=_sha256_file(path),
        binding_sha256=binding_hash,
        implementation_sha256s=MappingProxyType(implementation_hashes),
        configuration=admission,
        admission_receipt_sha256=receipt["receipt_sha256"],
        actor_ids=actor_ids,
        actors=MappingProxyType(actors),
        policies=MappingProxyType(policies),
        unbound_policy_ids=unbound,
        routes=MappingProxyType(routes),
        observation_ids=MappingProxyType(observation_contracts),
        actions=MappingProxyType(actions),
        document=_freeze(document),
    )


__all__ = [
    "BINDING_FORMAT",
    "BINDING_ID",
    "EVENT_ID",
    "FIXTURE_SOURCE_REF",
    "Note7LineageBinding",
    "Note7LineageBindingError",
    "load_note7_lineage_binding",
]
