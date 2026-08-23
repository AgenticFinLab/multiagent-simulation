"""Exact, fail-closed carrier projection for the bounded KT--NBC--NYCH lineage.

The accepted Scenario Configuration remains non-executable.  This module loads
one separately versioned E6 binding, checks every upstream identity, and
projects only four selected semantic intents into Contracts V1 carriers.
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

from h2epr.agents import RosterMappingProfile, load_roster_mapping_profile
from h2epr.artifacts.provenance import runtime_field
from h2epr.bundles.canonical import sha256_value
from h2epr.configuration import (
    ScenarioConfigurationAdmission,
    load_scenario_configuration,
)


BINDING_FORMAT = "h2epr.bounded-lineage-binding.v0_1"
RELEASE_FORMAT = "h2epr.bounded-lineage-binding-release.v0_1"
BINDING_ID = "h2epr.0288.kt-nbc-nych.binding.v0_1"
EVENT_ID = "H2EPR-0288"
FIXTURE_SOURCE_REF = "fixture.h2epr.0288.kt_nbc_nych.positive.v0_1"

_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_STABLE_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,127}$")
_PARAMETER_TYPES = frozenset(
    {
        "enum",
        "integer",
        "nullable_time_interval",
        "sha256",
        "stable_id",
        "stable_id_array",
    }
)
_CARRIERS = frozenset(
    {"parameters", "resource_offer_or_request", "expiry_time"}
)
_EXPECTED_ACTION_KEYS = (
    "kt.submit_support_request",
    "nbc.forward_request_with_provenance",
    "nych.record_and_classify_request",
    "nych.issue_typed_decline",
)
_EXPECTED_POLICY_IMPLEMENTATIONS = {
    "POL-FACILITY-01": "h2epr.policy.0288.facility.dated_activation.v0_1",
    "POL-INFO-01": "h2epr.policy.0288.info.delivery.v0_1",
    "POL-LIFECYCLE-01": "h2epr.policy.0288.lifecycle.event_revisit.v0_1",
    "POL-RESULT-01": "h2epr.policy.0288.result.layered.v0_1",
    "POL-REVIEW-01": "h2epr.policy.0288.review.typed_completeness.v0_1",
    "POL-TIME-01": "h2epr.policy.0288.time.partial_order.v0_1",
}
_EXPECTED_IMPLEMENTATION_PATHS = {
    "carrier_loader": "scenarios/panic_1907/lineage_v0_1/binding.py",
    "environment_policies": "scenarios/panic_1907/lineage_v0_1/environment.py",
    "participant_policies": "scenarios/panic_1907/lineage_v0_1/policies.py",
    "public_api": "scenarios/panic_1907/lineage_v0_1/__init__.py",
}


class LineageBindingError(ValueError):
    """The bounded binding, an upstream identity, or a projection is invalid."""


class _DuplicateKey(ValueError):
    pass


def _fail(code: str, detail: str = "") -> None:
    suffix = f":{detail}" if detail else ""
    raise LineageBindingError(f"{code}{suffix}")


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
        text = path.read_text(encoding="utf-8")
        value = json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        _fail("LINEAGE_JSON_INVALID", label)
        raise AssertionError from exc
    if not isinstance(value, dict):
        _fail("LINEAGE_JSON_OBJECT_REQUIRED", label)
    return value


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = ",".join(sorted(expected - actual))
        extra = ",".join(sorted(actual - expected))
        _fail(
            "LINEAGE_FIELDS_MISMATCH",
            f"{label}:missing={missing}:extra={extra}",
        )


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        _fail("LINEAGE_STRING_INVALID", label)
    return value


def _stable_id(value: Any, label: str) -> str:
    result = _string(value, label)
    if _STABLE_ID.fullmatch(result) is None:
        _fail("LINEAGE_STABLE_ID_INVALID", label)
    return result


def _sha256(value: Any, label: str) -> str:
    result = _string(value, label)
    if _SHA256.fullmatch(result) is None:
        _fail("LINEAGE_SHA256_INVALID", label)
    return result


def _boolean(value: Any, label: str) -> bool:
    if type(value) is not bool:
        _fail("LINEAGE_BOOLEAN_INVALID", label)
    return value


def _integer(value: Any, label: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        _fail("LINEAGE_INTEGER_INVALID", label)
    return value


def _object(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail("LINEAGE_OBJECT_REQUIRED", label)
    return value


def _array(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        _fail("LINEAGE_ARRAY_REQUIRED", label)
    return value


def _unique_ids(
    value: Any,
    label: str,
    *,
    allow_empty: bool = False,
    sorted_required: bool = False,
) -> tuple[str, ...]:
    items = _array(value, label)
    if not items and not allow_empty:
        _fail("LINEAGE_ARRAY_EMPTY", label)
    result = tuple(_stable_id(item, label) for item in items)
    if len(result) != len(set(result)):
        _fail("LINEAGE_ARRAY_DUPLICATE", label)
    if sorted_required and result != tuple(sorted(result)):
        _fail("LINEAGE_ARRAY_UNSORTED", label)
    return result


def _inside(root: Path, relative_value: Any, label: str) -> Path:
    relative = Path(_string(relative_value, label))
    if relative.is_absolute() or ".." in relative.parts:
        _fail("LINEAGE_PATH_UNSAFE", label)
    result = (root / relative).resolve()
    if not result.is_relative_to(root):
        _fail("LINEAGE_PATH_OUTSIDE_PROJECT", label)
    if not result.is_file():
        _fail("LINEAGE_PATH_MISSING", label)
    return result


def _find_project_root(path: Path, supplied: str | Path | None) -> Path:
    if supplied is not None:
        root = Path(supplied).resolve()
    else:
        roots = [
            parent
            for parent in path.resolve().parents
            if parent.joinpath("src/h2epr").is_dir()
            and parent.joinpath("contracts/v1").is_dir()
        ]
        if not roots:
            _fail("LINEAGE_PROJECT_ROOT_NOT_FOUND")
        root = roots[0]
    if not root.joinpath("src/h2epr").is_dir():
        _fail("LINEAGE_PROJECT_ROOT_INVALID", root.as_posix())
    return root


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _time_interval(value: Any, label: str, *, nullable: bool = False) -> Any:
    if value is None and nullable:
        return None
    item = _object(value, label)
    _exact_keys(
        item,
        {"lower", "upper", "precision", "timezone", "uncertainty"},
        label,
    )
    lower = _string(item["lower"], f"{label}.lower")
    upper = _string(item["upper"], f"{label}.upper")
    try:
        lower_time = datetime.fromisoformat(lower)
        upper_time = datetime.fromisoformat(upper)
    except ValueError:
        _fail("LINEAGE_TIME_INVALID", label)
    if lower_time.tzinfo is None or upper_time.tzinfo is None or lower_time > upper_time:
        _fail("LINEAGE_TIME_INVALID", label)
    _stable_id(item["precision"], f"{label}.precision")
    _string(item["timezone"], f"{label}.timezone")
    _string(item["uncertainty"], f"{label}.uncertainty")
    return copy.deepcopy(dict(item))


def _runtime_values(fields: Sequence[Mapping[str, Any]], label: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for index, field in enumerate(fields):
        if not isinstance(field, Mapping) or set(field) != {"field_name", "runtime_value"}:
            _fail("LINEAGE_RUNTIME_FIELD_INVALID", f"{label}.{index}")
        name = _stable_id(field["field_name"], f"{label}.{index}.field_name")
        runtime_value = _object(field["runtime_value"], f"{label}.{index}.runtime_value")
        if "value" not in runtime_value or name in result:
            _fail("LINEAGE_RUNTIME_FIELD_INVALID", f"{label}.{index}")
        result[name] = runtime_value["value"]
    return result


@dataclass(frozen=True)
class ParameterContract:
    name: str
    value_type: str
    carrier: str
    values: tuple[str, ...]

    def validate(self, value: Any) -> Any:
        label = f"parameter.{self.name}"
        if self.value_type == "stable_id":
            return _stable_id(value, label)
        if self.value_type == "sha256":
            return _sha256(value, label)
        if self.value_type == "integer":
            return _integer(value, label)
        if self.value_type == "enum":
            result = _stable_id(value, label)
            if result not in self.values:
                _fail("LINEAGE_PARAMETER_OUTSIDE_DOMAIN", self.name)
            return result
        if self.value_type == "stable_id_array":
            return list(_unique_ids(value, label, sorted_required=True))
        if self.value_type == "nullable_time_interval":
            return _time_interval(value, label, nullable=True)
        raise AssertionError(self.value_type)


@dataclass(frozen=True)
class ObservationContract:
    actor_id: str
    capability_id: str
    reader_observation_id: str
    field_name: str
    value_type: str
    values: tuple[str, ...]

    def validate(self, value: Any) -> Any:
        label = f"observation.{self.actor_id}.{self.reader_observation_id}"
        if self.value_type == "stable_id":
            return _stable_id(value, label)
        if self.value_type == "stable_id_array":
            return list(_unique_ids(value, label, sorted_required=True))
        if self.value_type == "enum":
            result = _stable_id(value, label)
            if result not in self.values:
                _fail("LINEAGE_OBSERVATION_OUTSIDE_DOMAIN", label)
            return result
        raise AssertionError(self.value_type)


@dataclass(frozen=True)
class RouteContract:
    route_id: str
    source_actor_id: str
    target_actor_id: str
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
    action_type: str
    action_schema_version: str
    commitment_ids: tuple[str, ...]
    observation_ids: tuple[str, ...]
    authority_ref_ids: tuple[str, ...]
    target_actor_ids: tuple[str, ...]
    lifecycle_family: str
    adjudication_family: str
    object_id_parameter: str
    object_version_parameter: str
    parameters: tuple[ParameterContract, ...]
    message_route_id: str | None
    forbidden_self_results: tuple[str, ...]

    @property
    def parameter_by_name(self) -> Mapping[str, ParameterContract]:
        return MappingProxyType({item.name: item for item in self.parameters})


@dataclass(frozen=True)
class PolicyBinding:
    policy_id: str
    version: str
    selection: str
    implementation_id: str
    status: str


@dataclass(frozen=True)
class LineageBinding:
    release_id: str
    release_manifest_sha256: str
    binding_id: str
    binding_sha256: str
    implementation_sha256s: Mapping[str, str]
    version: str
    configuration: ScenarioConfigurationAdmission
    roster_profile: RosterMappingProfile
    admission_receipt_sha256: str
    actor_ids: tuple[str, ...]
    capability_ids: tuple[str, ...]
    actors: Mapping[str, Mapping[str, Any]]
    relationship_refs: tuple[str, ...]
    policy_bindings: Mapping[str, PolicyBinding]
    unbound_policy_ids: tuple[str, ...]
    routes: Mapping[str, RouteContract]
    observations: Mapping[tuple[str, str], ObservationContract]
    actions: Mapping[str, ActionContract]
    decision_bindings: tuple[Mapping[str, Any], ...]
    document: Mapping[str, Any]

    def action_definition(self, action_key: str) -> dict[str, Any]:
        contract = self._action(action_key)
        representations = self.roster_profile.capabilities[
            contract.capability_id
        ].representation_classes
        return {
            "action_type": contract.action_type,
            "version": contract.action_schema_version,
            "allowed_representation_classes": list(representations),
            "parameter_names": sorted(item.name for item in contract.parameters),
            "state_changing": True,
            "review_state": "reviewed",
        }

    def route_definition(self, route_id: str) -> dict[str, Any]:
        try:
            return self.routes[route_id].as_v1_definition()
        except KeyError as exc:
            _fail("LINEAGE_ROUTE_UNKNOWN", route_id)
            raise AssertionError from exc

    def project_observation(
        self,
        action_key: str,
        *,
        observation_id: str,
        values: Mapping[str, Any],
    ) -> dict[str, Any]:
        contract = self._action(action_key)
        _stable_id(observation_id, "observation_id")
        if set(values) != set(contract.observation_ids):
            _fail("LINEAGE_OBSERVATION_INVENTORY_MISMATCH", action_key)
        fields = []
        for reader_id in sorted(values):
            try:
                observation = self.observations[(contract.actor_id, reader_id)]
            except KeyError as exc:
                _fail(
                    "LINEAGE_OBSERVATION_CONTRACT_MISSING",
                    f"{contract.actor_id}:{reader_id}",
                )
                raise AssertionError from exc
            value = observation.validate(values[reader_id])
            fields.append(
                runtime_field(
                    observation.field_name,
                    value,
                    source_kind="synthetic",
                    source_ref_id=FIXTURE_SOURCE_REF,
                    claim_ref_ids=("fixture.synthetic.conformance_only",),
                    derivation_class="assumed",
                    availability_at_t0="not_applicable",
                    visibility="runtime_private",
                    visibility_scope_ids=(contract.actor_id,),
                    consumers=(contract.actor_id, "world.reducer"),
                )
            )
        return {"observation_id": observation_id, "fields": fields}

    def read_observation(
        self, action_key: str, payload: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """Validate and decode exactly the observation fields for one action."""

        contract = self._action(action_key)
        _exact_keys(payload, {"observation_id", "fields"}, "observation_payload")
        _stable_id(payload["observation_id"], "observation_payload.observation_id")
        by_field = _runtime_values(payload["fields"], "observation_payload.fields")
        expected = {
            self.observations[(contract.actor_id, reader_id)].field_name: reader_id
            for reader_id in contract.observation_ids
        }
        if set(by_field) != set(expected):
            _fail("LINEAGE_OBSERVATION_CARRIER_MISMATCH", action_key)
        decoded: dict[str, Any] = {}
        for field_name, reader_id in expected.items():
            observation = self.observations[(contract.actor_id, reader_id)]
            decoded[reader_id] = observation.validate(by_field[field_name])
        return MappingProxyType(decoded)

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
        _stable_id(intent_id, "intent_id")
        _stable_id(run_id, "run_id")
        _integer(logical_tick, "logical_tick")
        _stable_id(decision_ref, "decision_ref")
        observation_ids = tuple(
            _stable_id(item, "observation_ref") for item in observation_refs
        )
        if not observation_ids or len(observation_ids) != len(set(observation_ids)):
            _fail("LINEAGE_OBSERVATION_REFS_INVALID", action_key)
        contracts = contract.parameter_by_name
        if set(semantic_parameters) != set(contracts):
            _fail("LINEAGE_PARAMETER_INVENTORY_MISMATCH", action_key)
        validated = {
            name: contracts[name].validate(value)
            for name, value in semantic_parameters.items()
        }
        earliest = (
            None
            if earliest_effect_time is None
            else _time_interval(earliest_effect_time, "earliest_effect_time")
        )
        parameter_fields = self._carrier_fields(
            contract, validated, "parameters"
        )
        resource_fields = self._carrier_fields(
            contract, validated, "resource_offer_or_request"
        )
        expiry_names = [
            item.name for item in contract.parameters if item.carrier == "expiry_time"
        ]
        if len(expiry_names) != 1:
            _fail("LINEAGE_EXPIRY_CONTRACT_INVALID", action_key)
        expiry = validated[expiry_names[0]]
        object_id = validated[contract.object_id_parameter]
        object_version = validated[contract.object_version_parameter]
        idempotency_key = self._action_idempotency_key(
            contract,
            object_id=object_id,
            object_version=object_version,
            semantic_parameters=validated,
        )
        action = {
            "intent_id": intent_id,
            "run_id": run_id,
            "logical_tick": logical_tick,
            "actor_id": contract.actor_id,
            "action_type": contract.action_type,
            "action_schema_version": contract.action_schema_version,
            "target_entity_ids": list(contract.target_actor_ids),
            "parameters": parameter_fields,
            "claimed_authority_refs": list(contract.authority_ref_ids),
            "resource_offer_or_request": resource_fields,
            "earliest_effect_time": earliest,
            "expiry_time": expiry,
            "observation_refs": list(observation_ids),
            "decision_ref": decision_ref,
            "idempotency_key": idempotency_key,
            "visibility": "restricted",
        }
        self.validate_action(action_key, action)
        return action

    def validate_action(self, action_key: str, action: Mapping[str, Any]) -> None:
        contract = self._action(action_key)
        expected_keys = {
            "intent_id",
            "run_id",
            "logical_tick",
            "actor_id",
            "action_type",
            "action_schema_version",
            "target_entity_ids",
            "parameters",
            "claimed_authority_refs",
            "resource_offer_or_request",
            "earliest_effect_time",
            "expiry_time",
            "observation_refs",
            "decision_ref",
            "idempotency_key",
            "visibility",
        }
        _exact_keys(action, expected_keys, f"action.{action_key}")
        if (
            action["actor_id"] != contract.actor_id
            or action["action_type"] != contract.action_type
            or action["action_schema_version"] != contract.action_schema_version
        ):
            _fail("LINEAGE_ACTION_IDENTITY_MISMATCH", action_key)
        if tuple(action["target_entity_ids"]) != contract.target_actor_ids:
            _fail("LINEAGE_ACTION_TARGET_MISMATCH", action_key)
        if tuple(action["claimed_authority_refs"]) != contract.authority_ref_ids:
            _fail("LINEAGE_ACTION_AUTHORITY_MISMATCH", action_key)
        parameters = _runtime_values(action["parameters"], f"action.{action_key}.parameters")
        resources = _runtime_values(
            action["resource_offer_or_request"],
            f"action.{action_key}.resources",
        )
        expected_parameters = {
            item.name for item in contract.parameters if item.carrier == "parameters"
        }
        expected_resources = {
            item.name
            for item in contract.parameters
            if item.carrier == "resource_offer_or_request"
        }
        if set(parameters) != expected_parameters or set(resources) != expected_resources:
            _fail("LINEAGE_ACTION_CARRIER_MISMATCH", action_key)
        expiry_contract = next(
            item for item in contract.parameters if item.carrier == "expiry_time"
        )
        expiry_contract.validate(action["expiry_time"])
        combined = {**parameters, **resources, expiry_contract.name: action["expiry_time"]}
        validated = {
            name: contract.parameter_by_name[name].validate(value)
            for name, value in combined.items()
        }
        expected_key = self._action_idempotency_key(
            contract,
            object_id=validated[contract.object_id_parameter],
            object_version=validated[contract.object_version_parameter],
            semantic_parameters=validated,
        )
        if action["idempotency_key"] != expected_key:
            _fail("LINEAGE_ACTION_IDEMPOTENCY_MISMATCH", action_key)

    def project_message(
        self,
        action_key: str,
        action: Mapping[str, Any],
        *,
        message_intent_id: str,
        earliest_delivery_time: Mapping[str, Any],
        correlation_ids: Sequence[str],
    ) -> dict[str, Any]:
        contract = self._action(action_key)
        if contract.message_route_id is None:
            _fail("LINEAGE_ACTION_HAS_NO_MESSAGE", action_key)
        self.validate_action(action_key, action)
        route = self.routes[contract.message_route_id]
        _stable_id(message_intent_id, "message_intent_id")
        correlations = tuple(
            _stable_id(item, "correlation_id") for item in correlation_ids
        )
        if not correlations or len(correlations) != len(set(correlations)):
            _fail("LINEAGE_CORRELATION_IDS_INVALID", action_key)
        if action["intent_id"] not in correlations:
            _fail("LINEAGE_ACTION_CORRELATION_MISSING", action_key)
        earliest = _time_interval(earliest_delivery_time, "earliest_delivery_time")
        structured = copy.deepcopy(
            list(action["parameters"]) + list(action["resource_offer_or_request"])
        )
        message = {
            "message_intent_id": message_intent_id,
            "run_id": action["run_id"],
            "logical_tick": action["logical_tick"],
            "sender_id": contract.actor_id,
            "recipient_ids": list(contract.target_actor_ids),
            "performative": route.performative,
            "content_schema_version": (
                f"h2epr.message.0288.kt_nbc_nych."
                f"{contract.reader_intent_id}.v0_1"
            ),
            "structured_content": structured,
            "channel": route.channel_id,
            "confidentiality": route.confidentiality,
            "created_at": copy.deepcopy(action["earliest_effect_time"]),
            "earliest_delivery_time": earliest,
            "expiry_time": copy.deepcopy(action["expiry_time"]),
            "decision_ref": action["decision_ref"],
            "idempotency_key": "idem.message."
            + sha256_value(
                {
                    "action_idempotency_key": action["idempotency_key"],
                    "route_id": route.route_id,
                    "binding_id": self.binding_id,
                }
            )[:48],
            "correlation_ids": list(correlations),
        }
        self.validate_message(action_key, action, message)
        return message

    def validate_message(
        self,
        action_key: str,
        action: Mapping[str, Any],
        message: Mapping[str, Any],
    ) -> None:
        contract = self._action(action_key)
        if contract.message_route_id is None:
            _fail("LINEAGE_ACTION_HAS_NO_MESSAGE", action_key)
        route = self.routes[contract.message_route_id]
        expected_keys = {
            "message_intent_id",
            "run_id",
            "logical_tick",
            "sender_id",
            "recipient_ids",
            "performative",
            "content_schema_version",
            "structured_content",
            "channel",
            "confidentiality",
            "created_at",
            "earliest_delivery_time",
            "expiry_time",
            "decision_ref",
            "idempotency_key",
            "correlation_ids",
        }
        _exact_keys(message, expected_keys, f"message.{action_key}")
        if (
            message["run_id"] != action["run_id"]
            or message["logical_tick"] != action["logical_tick"]
            or message["sender_id"] != route.source_actor_id
            or tuple(message["recipient_ids"]) != (route.target_actor_id,)
            or message["performative"] != route.performative
            or message["channel"] != route.channel_id
            or message["confidentiality"] != route.confidentiality
            or message["decision_ref"] != action["decision_ref"]
            or message["expiry_time"] != action["expiry_time"]
        ):
            _fail("LINEAGE_MESSAGE_ENVELOPE_MISMATCH", action_key)
        action_content = _runtime_values(
            list(action["parameters"]) + list(action["resource_offer_or_request"]),
            f"action.{action_key}.message_projection",
        )
        message_content = _runtime_values(
            message["structured_content"], f"message.{action_key}.content"
        )
        if message_content != action_content:
            _fail("LINEAGE_MESSAGE_CONTENT_MISMATCH", action_key)
        if action["intent_id"] not in message["correlation_ids"]:
            _fail("LINEAGE_ACTION_CORRELATION_MISSING", action_key)
        expected_key = "idem.message." + sha256_value(
            {
                "action_idempotency_key": action["idempotency_key"],
                "route_id": route.route_id,
                "binding_id": self.binding_id,
            }
        )[:48]
        if message["idempotency_key"] != expected_key:
            _fail("LINEAGE_MESSAGE_IDEMPOTENCY_MISMATCH", action_key)

    def semantic_values(self, action: Mapping[str, Any]) -> dict[str, Any]:
        result = _runtime_values(action["parameters"], "action.parameters")
        result.update(
            _runtime_values(action["resource_offer_or_request"], "action.resources")
        )
        result["expiry_time"] = copy.deepcopy(action["expiry_time"])
        return result

    def _action(self, action_key: str) -> ActionContract:
        try:
            return self.actions[action_key]
        except KeyError as exc:
            _fail("LINEAGE_ACTION_UNKNOWN", action_key)
            raise AssertionError from exc

    def _carrier_fields(
        self,
        contract: ActionContract,
        values: Mapping[str, Any],
        carrier: str,
    ) -> list[dict[str, Any]]:
        return [
            runtime_field(
                item.name,
                copy.deepcopy(values[item.name]),
                source_kind="synthetic",
                source_ref_id=FIXTURE_SOURCE_REF,
                claim_ref_ids=("fixture.synthetic.conformance_only",),
                derivation_class="assumed",
                availability_at_t0="not_applicable",
                visibility="runtime_private",
                visibility_scope_ids=(contract.actor_id,),
                consumers=(contract.actor_id, "world.reducer"),
            )
            for item in sorted(contract.parameters, key=lambda entry: entry.name)
            if item.carrier == carrier
        ]

    def _action_idempotency_key(
        self,
        contract: ActionContract,
        *,
        object_id: str,
        object_version: int,
        semantic_parameters: Mapping[str, Any],
    ) -> str:
        return "idem.action." + sha256_value(
            {
                "binding_id": self.binding_id,
                "action_key": contract.action_key,
                "actor_id": contract.actor_id,
                "object_id": object_id,
                "object_version": object_version,
                "target_actor_ids": list(contract.target_actor_ids),
                "authority_ref_ids": list(contract.authority_ref_ids),
                "semantic_parameters": dict(semantic_parameters),
            }
        )[:48]


def _parse_route(value: Any, label: str) -> RouteContract:
    item = _object(value, label)
    _exact_keys(
        item,
        {
            "route_id",
            "source_actor_id",
            "target_actor_id",
            "channel_id",
            "performative",
            "confidentiality",
            "latency_ticks",
        },
        label,
    )
    confidentiality = _string(item["confidentiality"], f"{label}.confidentiality")
    if confidentiality not in {"public", "private", "restricted"}:
        _fail("LINEAGE_ROUTE_CONFIDENTIALITY_INVALID", label)
    return RouteContract(
        route_id=_stable_id(item["route_id"], f"{label}.route_id"),
        source_actor_id=_stable_id(
            item["source_actor_id"], f"{label}.source_actor_id"
        ),
        target_actor_id=_stable_id(
            item["target_actor_id"], f"{label}.target_actor_id"
        ),
        channel_id=_stable_id(item["channel_id"], f"{label}.channel_id"),
        performative=_stable_id(item["performative"], f"{label}.performative"),
        confidentiality=confidentiality,
        latency_ticks=_integer(item["latency_ticks"], f"{label}.latency_ticks"),
    )


def _parse_parameter(value: Any, label: str) -> ParameterContract:
    item = _object(value, label)
    _exact_keys(item, {"name", "value_type", "carrier", "values"}, label)
    value_type = _string(item["value_type"], f"{label}.value_type")
    carrier = _string(item["carrier"], f"{label}.carrier")
    if value_type not in _PARAMETER_TYPES or carrier not in _CARRIERS:
        _fail("LINEAGE_PARAMETER_CONTRACT_INVALID", label)
    values = _unique_ids(
        item["values"], f"{label}.values", allow_empty=True
    )
    if (value_type == "enum") != bool(values):
        _fail("LINEAGE_PARAMETER_ENUM_DOMAIN_INVALID", label)
    if carrier == "expiry_time" and value_type != "nullable_time_interval":
        _fail("LINEAGE_EXPIRY_CONTRACT_INVALID", label)
    if value_type == "nullable_time_interval" and carrier != "expiry_time":
        _fail("LINEAGE_EXPIRY_CONTRACT_INVALID", label)
    return ParameterContract(
        name=_stable_id(item["name"], f"{label}.name"),
        value_type=value_type,
        carrier=carrier,
        values=values,
    )


def _parse_action(
    value: Any,
    label: str,
    *,
    profile: RosterMappingProfile,
    actor_capabilities: Mapping[str, str],
    routes: Mapping[str, RouteContract],
    observations: Mapping[tuple[str, str], ObservationContract],
) -> ActionContract:
    item = _object(value, label)
    _exact_keys(
        item,
        {
            "action_key",
            "actor_id",
            "capability_id",
            "reader_intent_id",
            "action_type",
            "action_schema_version",
            "commitment_ids",
            "observation_ids",
            "authority_ref_ids",
            "target_actor_ids",
            "lifecycle_family",
            "adjudication_family",
            "object_id_parameter",
            "object_version_parameter",
            "parameters",
            "message_route_id",
            "forbidden_self_results",
        },
        label,
    )
    actor_id = _stable_id(item["actor_id"], f"{label}.actor_id")
    capability_id = _stable_id(item["capability_id"], f"{label}.capability_id")
    reader_intent_id = _stable_id(
        item["reader_intent_id"], f"{label}.reader_intent_id"
    )
    if actor_id not in actor_capabilities:
        _fail("LINEAGE_ACTION_ACTOR_OUTSIDE_SCOPE", label)
    if actor_capabilities[actor_id] != capability_id:
        _fail("LINEAGE_ACTION_CAPABILITY_MISMATCH", label)
    placement = profile.intent(capability_id, reader_intent_id)
    if (
        item["action_type"] != placement.action_type
        or item["action_schema_version"] != placement.action_schema_version
    ):
        _fail("LINEAGE_ACTION_MAPPING_MISMATCH", label)
    product = profile.capabilities[capability_id]
    commitments = _unique_ids(item["commitment_ids"], f"{label}.commitment_ids")
    if not set(commitments).issubset(product.commitment_ids):
        _fail("LINEAGE_ACTION_COMMITMENT_MISMATCH", label)
    observation_ids = _unique_ids(
        item["observation_ids"], f"{label}.observation_ids"
    )
    if any((actor_id, obs) not in observations for obs in observation_ids):
        _fail("LINEAGE_ACTION_OBSERVATION_MISMATCH", label)
    authority_refs = _unique_ids(
        item["authority_ref_ids"], f"{label}.authority_ref_ids"
    )
    targets = _unique_ids(
        item["target_actor_ids"],
        f"{label}.target_actor_ids",
        allow_empty=True,
    )
    if any(target not in actor_capabilities for target in targets):
        _fail("LINEAGE_ACTION_TARGET_OUTSIDE_SCOPE", label)
    parameters = tuple(
        _parse_parameter(raw, f"{label}.parameters.{index}")
        for index, raw in enumerate(_array(item["parameters"], f"{label}.parameters"))
    )
    parameter_names = tuple(entry.name for entry in parameters)
    if len(parameter_names) != len(set(parameter_names)):
        _fail("LINEAGE_PARAMETER_CONTRACT_DUPLICATE", label)
    if sum(entry.carrier == "expiry_time" for entry in parameters) != 1:
        _fail("LINEAGE_EXPIRY_CONTRACT_INVALID", label)
    object_id_parameter = _stable_id(
        item["object_id_parameter"], f"{label}.object_id_parameter"
    )
    object_version_parameter = _stable_id(
        item["object_version_parameter"], f"{label}.object_version_parameter"
    )
    by_name = {entry.name: entry for entry in parameters}
    if (
        object_id_parameter not in by_name
        or by_name[object_id_parameter].value_type != "stable_id"
        or object_version_parameter not in by_name
        or by_name[object_version_parameter].value_type != "integer"
    ):
        _fail("LINEAGE_OBJECT_IDENTITY_CONTRACT_INVALID", label)
    route_value = item["message_route_id"]
    if route_value is None:
        message_route_id = None
        if targets:
            _fail("LINEAGE_MESSAGE_ROUTE_MISSING", label)
    else:
        message_route_id = _stable_id(route_value, f"{label}.message_route_id")
        if message_route_id not in routes:
            _fail("LINEAGE_MESSAGE_ROUTE_UNKNOWN", label)
        route = routes[message_route_id]
        if route.source_actor_id != actor_id or targets != (route.target_actor_id,):
            _fail("LINEAGE_MESSAGE_ROUTE_TARGET_MISMATCH", label)
    return ActionContract(
        action_key=_stable_id(item["action_key"], f"{label}.action_key"),
        actor_id=actor_id,
        capability_id=capability_id,
        reader_intent_id=reader_intent_id,
        action_type=placement.action_type,
        action_schema_version=placement.action_schema_version,
        commitment_ids=commitments,
        observation_ids=observation_ids,
        authority_ref_ids=authority_refs,
        target_actor_ids=targets,
        lifecycle_family=_stable_id(
            item["lifecycle_family"], f"{label}.lifecycle_family"
        ),
        adjudication_family=_stable_id(
            item["adjudication_family"], f"{label}.adjudication_family"
        ),
        object_id_parameter=object_id_parameter,
        object_version_parameter=object_version_parameter,
        parameters=parameters,
        message_route_id=message_route_id,
        forbidden_self_results=_unique_ids(
            item["forbidden_self_results"], f"{label}.forbidden_self_results"
        ),
    )


def _validate_receipt(
    path: Path,
    *,
    expected_file_sha256: str,
    expected_receipt_sha256: str,
) -> Mapping[str, Any]:
    if _sha256_file(path) != expected_file_sha256:
        _fail("LINEAGE_ADMISSION_RECEIPT_FILE_HASH_MISMATCH")
    receipt = _read_json(path, "admission_receipt")
    if receipt.get("receipt_sha256") != expected_receipt_sha256:
        _fail("LINEAGE_ADMISSION_RECEIPT_IDENTITY_MISMATCH")
    preimage = copy.deepcopy(receipt)
    preimage.pop("receipt_sha256", None)
    if sha256_value(preimage) != expected_receipt_sha256:
        _fail("LINEAGE_ADMISSION_RECEIPT_SELF_HASH_MISMATCH")
    if receipt.get("verdict") != "PASS_BOUNDED_CONFIGURATION_ADMISSION":
        _fail("LINEAGE_ADMISSION_RECEIPT_NOT_PASSING")
    return receipt


def _parse_binding(
    document: Mapping[str, Any],
    *,
    admission: ScenarioConfigurationAdmission,
    profile: RosterMappingProfile,
    receipt: Mapping[str, Any],
    release_id: str,
    release_manifest_sha256: str,
    binding_sha256: str,
    implementation_sha256s: Mapping[str, str],
) -> LineageBinding:
    _exact_keys(
        document,
        {
            "schema",
            "binding_id",
            "version",
            "status",
            "event_id",
            "configuration",
            "scope",
            "actors",
            "relationship_refs",
            "policy_bindings",
            "routes",
            "observation_contracts",
            "actions",
            "decision_bindings",
        },
        "binding",
    )
    if (
        document["schema"] != BINDING_FORMAT
        or document["binding_id"] != BINDING_ID
        or document["event_id"] != EVENT_ID
        or document["status"] != "bounded_conformance_binding"
    ):
        _fail("LINEAGE_BINDING_IDENTITY_MISMATCH")
    version = _string(document["version"], "binding.version")

    config = _object(document["configuration"], "binding.configuration")
    _exact_keys(
        config,
        {
            "configuration_id",
            "source_sha256",
            "canonical_sha256",
            "admission_receipt_sha256",
            "mapping_profile_id",
            "mapping_profile_sha256",
        },
        "binding.configuration",
    )
    expected_config = {
        "configuration_id": admission.configuration_id,
        "source_sha256": admission.source_sha256,
        "canonical_sha256": admission.canonical_sha256,
        "admission_receipt_sha256": receipt["receipt_sha256"],
        "mapping_profile_id": admission.mapping_profile_id,
        "mapping_profile_sha256": admission.mapping_profile_sha256,
    }
    if dict(config) != expected_config:
        _fail("LINEAGE_CONFIGURATION_BINDING_MISMATCH")

    scope = _object(document["scope"], "binding.scope")
    _exact_keys(
        scope,
        {
            "purpose",
            "actor_ids",
            "capability_ids",
            "bound_policy_ids",
            "unbound_policy_ids",
            "excluded_actor_count",
            "full_configuration_execution_enabled",
            "simulation_enabled",
            "historical_validity_claim",
            "scientific_validity_claim",
            "positive_fixture_exposure",
        },
        "binding.scope",
    )
    if scope["purpose"] != "exact_carrier_and_positive_binding_conformance":
        _fail("LINEAGE_PURPOSE_MISMATCH")
    actor_ids = _unique_ids(scope["actor_ids"], "binding.scope.actor_ids")
    capability_ids = _unique_ids(
        scope["capability_ids"], "binding.scope.capability_ids"
    )
    bound_policy_ids = _unique_ids(
        scope["bound_policy_ids"],
        "binding.scope.bound_policy_ids",
        sorted_required=True,
    )
    unbound_policy_ids = _unique_ids(
        scope["unbound_policy_ids"],
        "binding.scope.unbound_policy_ids",
        sorted_required=True,
    )
    all_config_policies = frozenset(admission.document["policy_selections"])
    if (
        set(bound_policy_ids) != set(_EXPECTED_POLICY_IMPLEMENTATIONS)
        or set(bound_policy_ids).intersection(unbound_policy_ids)
        or set(bound_policy_ids).union(unbound_policy_ids) != all_config_policies
    ):
        _fail("LINEAGE_POLICY_SCOPE_MISMATCH")
    if _integer(scope["excluded_actor_count"], "scope.excluded_actor_count") != 13:
        _fail("LINEAGE_ACTOR_SCOPE_MISMATCH")
    for name in (
        "full_configuration_execution_enabled",
        "simulation_enabled",
        "historical_validity_claim",
        "scientific_validity_claim",
    ):
        if _boolean(scope[name], f"scope.{name}"):
            _fail("LINEAGE_SCOPE_ESCALATION_FORBIDDEN", name)
    if scope["positive_fixture_exposure"] != "full_draft_exposed_conformance_only":
        _fail("LINEAGE_EXPOSURE_LABEL_MISMATCH")

    config_actors = {
        row["actor_id"]: row for row in admission.document["named_actors"]
    }
    actor_rows: dict[str, Mapping[str, Any]] = {}
    for index, raw in enumerate(_array(document["actors"], "binding.actors")):
        label = f"binding.actors.{index}"
        row = _object(raw, label)
        _exact_keys(
            row,
            {
                "actor_id",
                "entity_id",
                "participant_artifact_id",
                "capability_id",
                "authority_graph_id",
                "resource_owner_id",
                "definition_sha256",
            },
            label,
        )
        actor_id = _stable_id(row["actor_id"], f"{label}.actor_id")
        if actor_id in actor_rows or actor_id not in actor_ids:
            _fail("LINEAGE_ACTOR_BINDING_INVALID", actor_id)
        if actor_id not in config_actors:
            _fail("LINEAGE_ACTOR_NOT_IN_CONFIGURATION", actor_id)
        config_actor = config_actors[actor_id]
        for field in (
            "entity_id",
            "participant_artifact_id",
            "authority_graph_id",
            "resource_owner_id",
        ):
            if row[field] != config_actor[field]:
                _fail("LINEAGE_ACTOR_CONFIGURATION_MISMATCH", f"{actor_id}:{field}")
        capability_id = _stable_id(row["capability_id"], f"{label}.capability_id")
        if tuple(config_actor["capability_ids"]) != (capability_id,):
            _fail("LINEAGE_ACTOR_CAPABILITY_MISMATCH", actor_id)
        product = profile.capabilities[capability_id]
        if (
            product.content_sha256 != row["definition_sha256"]
            or "autonomous_participant_agent" not in product.representation_classes
        ):
            _fail("LINEAGE_ACTOR_MAPPING_MISMATCH", actor_id)
        actor_rows[actor_id] = _freeze(dict(row))
    if set(actor_rows) != set(actor_ids) or {
        row["capability_id"] for row in actor_rows.values()
    } != set(capability_ids):
        _fail("LINEAGE_ACTOR_SCOPE_MISMATCH")

    relationship_refs = _unique_ids(
        document["relationship_refs"],
        "binding.relationship_refs",
        sorted_required=True,
    )
    configured_relationships = {
        row["record_id"]
        for row in admission.document["initial_records"]["relationships"]
    }
    if not set(relationship_refs).issubset(configured_relationships):
        _fail("LINEAGE_RELATIONSHIP_REF_MISMATCH")

    policies: dict[str, PolicyBinding] = {}
    for index, raw in enumerate(
        _array(document["policy_bindings"], "binding.policy_bindings")
    ):
        label = f"binding.policy_bindings.{index}"
        row = _object(raw, label)
        _exact_keys(
            row,
            {"policy_id", "version", "selection", "implementation_id", "status"},
            label,
        )
        policy_id = _stable_id(row["policy_id"], f"{label}.policy_id")
        if policy_id in policies or policy_id not in bound_policy_ids:
            _fail("LINEAGE_POLICY_BINDING_INVALID", policy_id)
        selected = admission.document["policy_selections"][policy_id]
        if (
            row["version"] != selected["version"]
            or row["selection"] != selected["selection"]
            or row["implementation_id"]
            != _EXPECTED_POLICY_IMPLEMENTATIONS[policy_id]
            or row["status"] != "bound_for_bounded_lineage_only"
        ):
            _fail("LINEAGE_POLICY_BINDING_MISMATCH", policy_id)
        policies[policy_id] = PolicyBinding(
            policy_id=policy_id,
            version=_string(row["version"], f"{label}.version"),
            selection=_stable_id(row["selection"], f"{label}.selection"),
            implementation_id=_stable_id(
                row["implementation_id"], f"{label}.implementation_id"
            ),
            status=row["status"],
        )
    if set(policies) != set(bound_policy_ids):
        _fail("LINEAGE_POLICY_BINDING_INCOMPLETE")

    routes: dict[str, RouteContract] = {}
    for index, raw in enumerate(_array(document["routes"], "binding.routes")):
        route = _parse_route(raw, f"binding.routes.{index}")
        if route.route_id in routes:
            _fail("LINEAGE_ROUTE_DUPLICATE", route.route_id)
        if route.source_actor_id not in actor_rows or route.target_actor_id not in actor_rows:
            _fail("LINEAGE_ROUTE_ACTOR_OUTSIDE_SCOPE", route.route_id)
        routes[route.route_id] = route

    observations: dict[tuple[str, str], ObservationContract] = {}
    for index, raw in enumerate(
        _array(document["observation_contracts"], "binding.observation_contracts")
    ):
        label = f"binding.observation_contracts.{index}"
        row = _object(raw, label)
        _exact_keys(
            row,
            {
                "actor_id",
                "capability_id",
                "reader_observation_id",
                "value_type",
                "values",
            },
            label,
        )
        actor_id = _stable_id(row["actor_id"], f"{label}.actor_id")
        capability_id = _stable_id(row["capability_id"], f"{label}.capability_id")
        reader_id = _stable_id(
            row["reader_observation_id"], f"{label}.reader_observation_id"
        )
        key = (actor_id, reader_id)
        if key in observations or actor_id not in actor_rows:
            _fail("LINEAGE_OBSERVATION_CONTRACT_INVALID", label)
        if actor_rows[actor_id]["capability_id"] != capability_id:
            _fail("LINEAGE_OBSERVATION_CAPABILITY_MISMATCH", label)
        try:
            placement = profile.observations[(capability_id, reader_id)]
        except KeyError as exc:
            _fail("LINEAGE_OBSERVATION_MAPPING_MISSING", label)
            raise AssertionError from exc
        value_type = _string(row["value_type"], f"{label}.value_type")
        if value_type not in {"enum", "stable_id", "stable_id_array"}:
            _fail("LINEAGE_OBSERVATION_TYPE_INVALID", label)
        values = _unique_ids(row["values"], f"{label}.values", allow_empty=True)
        if (value_type == "enum") != bool(values):
            _fail("LINEAGE_OBSERVATION_ENUM_DOMAIN_INVALID", label)
        observations[key] = ObservationContract(
            actor_id=actor_id,
            capability_id=capability_id,
            reader_observation_id=reader_id,
            field_name=placement.field_name,
            value_type=value_type,
            values=values,
        )

    actions: dict[str, ActionContract] = {}
    for index, raw in enumerate(_array(document["actions"], "binding.actions")):
        action = _parse_action(
            raw,
            f"binding.actions.{index}",
            profile=profile,
            actor_capabilities={
                actor_id: row["capability_id"]
                for actor_id, row in actor_rows.items()
            },
            routes=routes,
            observations=observations,
        )
        if action.action_key in actions:
            _fail("LINEAGE_ACTION_DUPLICATE", action.action_key)
        actions[action.action_key] = action
    if tuple(actions) != _EXPECTED_ACTION_KEYS:
        _fail("LINEAGE_ACTION_SCOPE_MISMATCH")

    decisions: list[Mapping[str, Any]] = []
    decision_actors: set[str] = set()
    covered_actions: set[str] = set()
    for index, raw in enumerate(
        _array(document["decision_bindings"], "binding.decision_bindings")
    ):
        label = f"binding.decision_bindings.{index}"
        row = _object(raw, label)
        _exact_keys(
            row,
            {"decision_policy_id", "actor_id", "action_keys", "status"},
            label,
        )
        actor_id = _stable_id(row["actor_id"], f"{label}.actor_id")
        action_keys = _unique_ids(row["action_keys"], f"{label}.action_keys")
        if (
            actor_id in decision_actors
            or actor_id not in actor_rows
            or row["status"] != "positive_branch_only"
            or any(key not in actions or actions[key].actor_id != actor_id for key in action_keys)
        ):
            _fail("LINEAGE_DECISION_BINDING_INVALID", label)
        _stable_id(row["decision_policy_id"], f"{label}.decision_policy_id")
        decision_actors.add(actor_id)
        covered_actions.update(action_keys)
        decisions.append(_freeze(dict(row)))
    if decision_actors != set(actor_ids) or covered_actions != set(actions):
        _fail("LINEAGE_DECISION_BINDING_INCOMPLETE")

    return LineageBinding(
        release_id=release_id,
        release_manifest_sha256=release_manifest_sha256,
        binding_id=BINDING_ID,
        binding_sha256=binding_sha256,
        implementation_sha256s=MappingProxyType(dict(implementation_sha256s)),
        version=version,
        configuration=admission,
        roster_profile=profile,
        admission_receipt_sha256=receipt["receipt_sha256"],
        actor_ids=actor_ids,
        capability_ids=capability_ids,
        actors=MappingProxyType(actor_rows),
        relationship_refs=relationship_refs,
        policy_bindings=MappingProxyType(policies),
        unbound_policy_ids=unbound_policy_ids,
        routes=MappingProxyType(routes),
        observations=MappingProxyType(observations),
        actions=MappingProxyType(actions),
        decision_bindings=tuple(decisions),
        document=_freeze(copy.deepcopy(dict(document))),
    )


def load_lineage_binding(
    manifest_path: str | Path,
    *,
    expected_manifest_sha256: str,
    project_root: str | Path | None = None,
) -> LineageBinding:
    """Load the exact E6 binding only when its external manifest anchor matches."""

    expected_hash = _sha256(expected_manifest_sha256, "expected_manifest_sha256")
    supplied = Path(manifest_path)
    root = _find_project_root(supplied, project_root)
    path = supplied.resolve() if supplied.is_absolute() else (root / supplied).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        _fail("LINEAGE_MANIFEST_PATH_INVALID")
    raw_hash = _sha256_file(path)
    if raw_hash != expected_hash:
        _fail("LINEAGE_MANIFEST_HASH_MISMATCH")
    manifest = _read_json(path, "binding_manifest")
    _exact_keys(
        manifest,
        {
            "schema",
            "release_id",
            "version",
            "status",
            "event_id",
            "manifest_sha256",
            "binding",
            "implementation_surfaces",
            "upstream",
            "authorization",
        },
        "binding_manifest",
    )
    if (
        manifest["schema"] != RELEASE_FORMAT
        or manifest["event_id"] != EVENT_ID
        or manifest["status"] != "bounded_conformance_release"
    ):
        _fail("LINEAGE_MANIFEST_IDENTITY_MISMATCH")
    preimage = copy.deepcopy(manifest)
    self_hash = preimage.pop("manifest_sha256", None)
    if self_hash != sha256_value(preimage):
        _fail("LINEAGE_MANIFEST_SELF_HASH_MISMATCH")

    binding_ref = _object(manifest["binding"], "manifest.binding")
    _exact_keys(binding_ref, {"path", "sha256"}, "manifest.binding")
    binding_path = _inside(root, binding_ref["path"], "manifest.binding.path")
    binding_sha256 = _sha256(binding_ref["sha256"], "manifest.binding.sha256")
    if _sha256_file(binding_path) != binding_sha256:
        _fail("LINEAGE_BINDING_HASH_MISMATCH")

    implementation_sha256s: dict[str, str] = {}
    implementation_paths: dict[str, str] = {}
    for index, raw in enumerate(
        _array(
            manifest["implementation_surfaces"],
            "manifest.implementation_surfaces",
        )
    ):
        label = f"manifest.implementation_surfaces.{index}"
        row = _object(raw, label)
        _exact_keys(row, {"kind", "path", "sha256"}, label)
        kind = _stable_id(row["kind"], f"{label}.kind")
        if kind in implementation_sha256s:
            _fail("LINEAGE_IMPLEMENTATION_SURFACE_DUPLICATE", kind)
        surface_path = _inside(root, row["path"], f"{label}.path")
        surface_hash = _sha256(row["sha256"], f"{label}.sha256")
        if _sha256_file(surface_path) != surface_hash:
            _fail("LINEAGE_IMPLEMENTATION_SURFACE_HASH_MISMATCH", kind)
        implementation_paths[kind] = surface_path.relative_to(root).as_posix()
        implementation_sha256s[kind] = surface_hash
    if implementation_paths != _EXPECTED_IMPLEMENTATION_PATHS:
        _fail("LINEAGE_IMPLEMENTATION_SURFACE_SCOPE_MISMATCH")

    upstream = _object(manifest["upstream"], "manifest.upstream")
    _exact_keys(
        upstream,
        {
            "configuration_path",
            "configuration_release_manifest_path",
            "configuration_source_sha256",
            "configuration_release_manifest_sha256",
            "configuration_canonical_sha256",
            "admission_receipt_path",
            "admission_receipt_file_sha256",
            "admission_receipt_sha256",
            "mapping_profile_path",
            "mapping_profile_sha256",
        },
        "manifest.upstream",
    )
    configuration_path = _inside(
        root, upstream["configuration_path"], "manifest.upstream.configuration_path"
    )
    configuration_manifest_path = _inside(
        root,
        upstream["configuration_release_manifest_path"],
        "manifest.upstream.configuration_release_manifest_path",
    )
    admission = load_scenario_configuration(
        configuration_path,
        expected_source_sha256=_sha256(
            upstream["configuration_source_sha256"],
            "manifest.upstream.configuration_source_sha256",
        ),
        expected_release_manifest_sha256=_sha256(
            upstream["configuration_release_manifest_sha256"],
            "manifest.upstream.configuration_release_manifest_sha256",
        ),
        project_root=root,
        release_manifest_path=configuration_manifest_path,
    )
    if admission.canonical_sha256 != upstream["configuration_canonical_sha256"]:
        _fail("LINEAGE_CONFIGURATION_CANONICAL_HASH_MISMATCH")
    receipt_path = _inside(
        root,
        upstream["admission_receipt_path"],
        "manifest.upstream.admission_receipt_path",
    )
    receipt = _validate_receipt(
        receipt_path,
        expected_file_sha256=_sha256(
            upstream["admission_receipt_file_sha256"],
            "manifest.upstream.admission_receipt_file_sha256",
        ),
        expected_receipt_sha256=_sha256(
            upstream["admission_receipt_sha256"],
            "manifest.upstream.admission_receipt_sha256",
        ),
    )
    profile_path = _inside(
        root, upstream["mapping_profile_path"], "manifest.upstream.mapping_profile_path"
    )
    profile_hash = _sha256(
        upstream["mapping_profile_sha256"],
        "manifest.upstream.mapping_profile_sha256",
    )
    if _sha256_file(profile_path) != profile_hash:
        _fail("LINEAGE_MAPPING_PROFILE_HASH_MISMATCH")
    profile = load_roster_mapping_profile(profile_path, project_root=root)
    if profile.profile_sha256 != profile_hash or admission.mapping_profile_sha256 != profile_hash:
        _fail("LINEAGE_MAPPING_PROFILE_IDENTITY_MISMATCH")

    authorization = _object(manifest["authorization"], "manifest.authorization")
    _exact_keys(
        authorization,
        {
            "bounded_projection_authorized",
            "bounded_policy_binding_authorized",
            "full_roster_runtime_authorized",
            "simulation_authorized",
            "evaluation_authorized",
            "historical_validity_claim_authorized",
        },
        "manifest.authorization",
    )
    if (
        _boolean(
            authorization["bounded_projection_authorized"],
            "authorization.bounded_projection_authorized",
        )
        is not True
        or _boolean(
            authorization["bounded_policy_binding_authorized"],
            "authorization.bounded_policy_binding_authorized",
        )
        is not True
    ):
        _fail("LINEAGE_E6_AUTHORIZATION_MISSING")
    for key in (
        "full_roster_runtime_authorized",
        "simulation_authorized",
        "evaluation_authorized",
        "historical_validity_claim_authorized",
    ):
        if _boolean(authorization[key], f"authorization.{key}"):
            _fail("LINEAGE_AUTHORIZATION_SCOPE_ESCALATION", key)

    document = _read_json(binding_path, "binding")
    return _parse_binding(
        document,
        admission=admission,
        profile=profile,
        receipt=receipt,
        release_id=_stable_id(manifest["release_id"], "manifest.release_id"),
        release_manifest_sha256=raw_hash,
        binding_sha256=binding_sha256,
        implementation_sha256s=implementation_sha256s,
    )


__all__ = [
    "BINDING_FORMAT",
    "BINDING_ID",
    "EVENT_ID",
    "FIXTURE_SOURCE_REF",
    "LineageBinding",
    "LineageBindingError",
    "PolicyBinding",
    "load_lineage_binding",
]
