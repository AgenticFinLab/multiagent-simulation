"""Executable binding for event-bound Markdown Agent Definitions.

The Markdown remains the pilot's behavioral authority.  The JSON binding is a
derived mapping that is rejected if its content hash, Decision Commitment,
semantic value contract, or commitment mapping drifts. This module deliberately
contains no historical policy and no environment state mutation.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
import re
from types import MappingProxyType
from typing import Any, Callable, Iterator, Mapping


BINDING_SCHEMA_VERSION = "h2epr.agent-definition-binding.v0_2"
_COMMITMENT_HEADING = re.compile(r"^### `(?P<commitment>DC-[A-Z]+-[0-9]+)`", re.MULTILINE)
_VALUE_TYPES = frozenset({"null", "string"})


class BindingValidationError(ValueError):
    """A derived binding no longer matches its canonical Markdown asset."""


class AgentConformanceError(ValueError):
    """An observation or decision escapes the bound Definition envelope."""


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stable_id(prefix: str, value: Mapping[str, Any]) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"{prefix}.{hashlib.sha256(payload).hexdigest()[:32]}"


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise BindingValidationError(f"invalid_{name}")
    return value


def _ordered_unique_strings(value: Any, name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise BindingValidationError(f"invalid_{name}")
    items = tuple(_string(item, name) for item in value)
    if len(items) != len(set(items)):
        raise BindingValidationError(f"duplicate_{name}")
    if items != tuple(sorted(items)):
        raise BindingValidationError(f"unsorted_{name}")
    return items


def _project_file(project_root: Path, relative_path: Any, name: str) -> Path:
    value = _string(relative_path, name)
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise BindingValidationError(f"unsafe_{name}")
    path = project_root / candidate
    if not path.is_file():
        raise BindingValidationError(f"missing_{name}:{value}")
    return path


@dataclass(frozen=True)
class ValueContract:
    """Small internal value contract used by the derived binding."""

    types: tuple[str, ...]
    enum: tuple[Any, ...] | None = None
    min_length: int | None = None


def _matches_value_type(value: Any, value_type: str) -> bool:
    if value_type == "null":
        return value is None
    if value_type == "string":
        return isinstance(value, str)
    raise AssertionError(f"unsupported_value_type:{value_type}")


def _parse_value_contract(value: Any, name: str) -> ValueContract:
    if not isinstance(value, dict):
        raise BindingValidationError(f"invalid_{name}")
    allowed_keys = {"enum", "min_length", "type"}
    extra_keys = set(value) - allowed_keys
    if extra_keys:
        raise BindingValidationError(
            f"unknown_{name}_fields:" + ",".join(sorted(extra_keys))
        )

    raw_types = value.get("type")
    if isinstance(raw_types, str):
        types = (raw_types,)
    elif isinstance(raw_types, list) and raw_types:
        types = tuple(raw_types)
    else:
        raise BindingValidationError(f"invalid_{name}_type")
    if (
        any(not isinstance(item, str) or item not in _VALUE_TYPES for item in types)
        or len(types) != len(set(types))
        or types != tuple(sorted(types))
    ):
        raise BindingValidationError(f"invalid_{name}_type")

    enum: tuple[Any, ...] | None = None
    if "enum" in value:
        raw_enum = value["enum"]
        if not isinstance(raw_enum, list) or not raw_enum:
            raise BindingValidationError(f"invalid_{name}_enum")
        if any(not isinstance(item, (str, type(None))) for item in raw_enum):
            raise BindingValidationError(f"invalid_{name}_enum")
        if len(raw_enum) != len(set(raw_enum)):
            raise BindingValidationError(f"duplicate_{name}_enum")
        if any(
            not any(_matches_value_type(item, value_type) for value_type in types)
            for item in raw_enum
        ):
            raise BindingValidationError(f"invalid_{name}_enum_type")
        enum = tuple(raw_enum)

    min_length = value.get("min_length")
    if min_length is not None:
        if (
            isinstance(min_length, bool)
            or not isinstance(min_length, int)
            or min_length < 0
            or "string" not in types
        ):
            raise BindingValidationError(f"invalid_{name}_min_length")

    return ValueContract(
        types=types,
        enum=enum,
        min_length=min_length,
    )


def _validate_runtime_value(value: Any, contract: ValueContract, context: str) -> None:
    if not any(_matches_value_type(value, value_type) for value_type in contract.types):
        raise AgentConformanceError(f"{context}_type_invalid")
    if contract.enum is not None and value not in contract.enum:
        raise AgentConformanceError(f"{context}_outside_enum")
    if isinstance(value, str) and contract.min_length is not None:
        if len(value) < contract.min_length:
            raise AgentConformanceError(f"{context}_below_min_length")


class _ObservedMapping(Mapping[str, Any]):
    """Read-only mapping that records fields actually consumed by a policy."""

    def __init__(self, values: Mapping[str, Any]) -> None:
        self._values = dict(values)
        self._accessed: set[str] = set()

    def __getitem__(self, key: str) -> Any:
        self._accessed.add(key)
        return self._values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    @property
    def accessed(self) -> frozenset[str]:
        return frozenset(self._accessed)


@dataclass(frozen=True)
class DefinitionBinding:
    definition_id: str
    version: str
    participant_id: str
    definition_path: str
    content_sha256: str
    decision_commitment_ids: tuple[str, ...]
    allowed_observations: frozenset[str]
    observation_contracts: Mapping[str, ValueContract]
    commitment_observations: Mapping[str, frozenset[str]]
    allowed_intents: frozenset[str]
    commitment_intents: Mapping[str, frozenset[str]]
    intent_contracts: Mapping[str, Mapping[str, ValueContract]]


def load_binding_catalog(
    binding_path: str | Path,
    *,
    project_root: str | Path | None = None,
) -> dict[str, DefinitionBinding]:
    """Load and cross-check a binding catalog against canonical files."""

    path = Path(binding_path).resolve()
    if not path.is_file():
        raise BindingValidationError("binding_catalog_missing")
    if project_root is not None:
        root = Path(project_root).resolve()
    else:
        candidates = [
            parent
            for parent in path.parents
            if parent.joinpath("src/h2epr").is_dir()
            and parent.joinpath("contracts/v1").is_dir()
        ]
        if not candidates:
            raise BindingValidationError("h2epr_project_root_not_found")
        root = candidates[0]
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BindingValidationError("binding_catalog_invalid_json") from exc
    if not isinstance(document, dict):
        raise BindingValidationError("binding_catalog_must_be_object")
    if document.get("binding_schema_version") != BINDING_SCHEMA_VERSION:
        raise BindingValidationError("binding_schema_version_mismatch")
    if document.get("authority") != "derived_mapping_only":
        raise BindingValidationError("binding_authority_mismatch")

    for stem in ("evidence", "micro_situation"):
        asset = _project_file(root, document.get(f"{stem}_path"), f"{stem}_path")
        expected = _string(document.get(f"{stem}_sha256"), f"{stem}_sha256")
        if _sha256_file(asset) != expected:
            raise BindingValidationError(f"{stem}_sha256_mismatch")

    rows = document.get("definitions")
    if not isinstance(rows, list) or not rows:
        raise BindingValidationError("definitions_missing")
    result: dict[str, DefinitionBinding] = {}
    definition_ids: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise BindingValidationError("definition_binding_must_be_object")
        definition_id = _string(row.get("definition_id"), "definition_id")
        version = _string(row.get("version"), "version")
        participant_id = _string(row.get("participant_id"), "participant_id")
        if participant_id in result or definition_id in definition_ids:
            raise BindingValidationError("duplicate_definition_identity")
        definition_ids.add(definition_id)
        definition_path = _string(row.get("definition_path"), "definition_path")
        markdown_path = _project_file(root, definition_path, "definition_path")
        content_sha256 = _string(row.get("content_sha256"), "content_sha256")
        if _sha256_file(markdown_path) != content_sha256:
            raise BindingValidationError(f"definition_sha256_mismatch:{participant_id}")
        text = markdown_path.read_text(encoding="utf-8")
        if f"> Definition ID: `{definition_id}`" not in text:
            raise BindingValidationError(f"definition_id_marker_mismatch:{participant_id}")
        if f"> Version: `{version}`" not in text:
            raise BindingValidationError(f"definition_version_marker_mismatch:{participant_id}")
        commitments = _ordered_unique_strings(
            row.get("decision_commitment_ids"), "decision_commitment_ids"
        )
        headings = tuple(_COMMITMENT_HEADING.findall(text))
        if headings != commitments:
            raise BindingValidationError(f"commitment_inventory_mismatch:{participant_id}")
        allowed_observations = frozenset(
            _ordered_unique_strings(row.get("allowed_observations"), "allowed_observations")
        )
        raw_observation_contracts = row.get("observation_contracts")
        if not isinstance(raw_observation_contracts, dict):
            raise BindingValidationError("observation_contracts_must_be_object")
        if set(raw_observation_contracts) != allowed_observations:
            raise BindingValidationError(
                f"observation_contract_inventory_mismatch:{participant_id}"
            )
        observation_contracts = {
            field_name: _parse_value_contract(
                raw_observation_contracts[field_name],
                f"observation_contract:{participant_id}:{field_name}",
            )
            for field_name in sorted(raw_observation_contracts)
        }

        raw_commitment_observations = row.get("commitment_observations")
        if not isinstance(raw_commitment_observations, dict):
            raise BindingValidationError("commitment_observations_must_be_object")
        if set(raw_commitment_observations) != set(commitments):
            raise BindingValidationError(
                f"commitment_observation_inventory_mismatch:{participant_id}"
            )
        commitment_observations: dict[str, frozenset[str]] = {}
        for commitment_id in commitments:
            mapped = frozenset(
                _ordered_unique_strings(
                    raw_commitment_observations[commitment_id],
                    "commitment_observations",
                )
            )
            if not mapped <= allowed_observations:
                raise BindingValidationError(
                    f"commitment_observation_outside_envelope:{participant_id}:{commitment_id}"
                )
            commitment_observations[commitment_id] = mapped
        if frozenset().union(*commitment_observations.values()) != allowed_observations:
            raise BindingValidationError(f"unmapped_allowed_observation:{participant_id}")

        allowed_intents = frozenset(
            _ordered_unique_strings(row.get("allowed_intents"), "allowed_intents")
        )
        raw_commitment_intents = row.get("commitment_intents")
        if not isinstance(raw_commitment_intents, dict):
            raise BindingValidationError("commitment_intents_must_be_object")
        if set(raw_commitment_intents) != set(commitments):
            raise BindingValidationError(
                f"commitment_intent_inventory_mismatch:{participant_id}"
            )
        commitment_intents: dict[str, frozenset[str]] = {}
        for commitment_id in commitments:
            mapped = frozenset(
                _ordered_unique_strings(
                    raw_commitment_intents[commitment_id],
                    "commitment_intents",
                )
            )
            if not mapped <= allowed_intents:
                raise BindingValidationError(
                    f"commitment_intent_outside_envelope:{participant_id}:{commitment_id}"
                )
            commitment_intents[commitment_id] = mapped
        if frozenset().union(*commitment_intents.values()) != allowed_intents:
            raise BindingValidationError(f"unmapped_allowed_intent:{participant_id}")

        raw_intent_contracts = row.get("intent_contracts")
        if not isinstance(raw_intent_contracts, dict):
            raise BindingValidationError("intent_contracts_must_be_object")
        if set(raw_intent_contracts) != allowed_intents:
            raise BindingValidationError(
                f"intent_contract_inventory_mismatch:{participant_id}"
            )
        intent_contracts: dict[str, Mapping[str, ValueContract]] = {}
        for intent_type in sorted(raw_intent_contracts):
            raw_parameters = raw_intent_contracts[intent_type]
            if not isinstance(raw_parameters, dict):
                raise BindingValidationError(
                    f"intent_contract_must_be_object:{participant_id}:{intent_type}"
                )
            parameter_contracts: dict[str, ValueContract] = {}
            for parameter_name in sorted(raw_parameters):
                _string(parameter_name, "intent_parameter_name")
                parameter_contracts[parameter_name] = _parse_value_contract(
                    raw_parameters[parameter_name],
                    f"intent_contract:{participant_id}:{intent_type}:{parameter_name}",
                )
            intent_contracts[intent_type] = MappingProxyType(parameter_contracts)
        result[participant_id] = DefinitionBinding(
            definition_id=definition_id,
            version=version,
            participant_id=participant_id,
            definition_path=definition_path,
            content_sha256=content_sha256,
            decision_commitment_ids=commitments,
            allowed_observations=allowed_observations,
            observation_contracts=MappingProxyType(observation_contracts),
            commitment_observations=MappingProxyType(commitment_observations),
            allowed_intents=allowed_intents,
            commitment_intents=MappingProxyType(commitment_intents),
            intent_contracts=MappingProxyType(intent_contracts),
        )
    return result


@dataclass(frozen=True)
class AgentObservation:
    observation_id: str
    actor_id: str
    logical_tick: int
    values: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not self.observation_id or not self.actor_id:
            raise ValueError("observation_identity_missing")
        if isinstance(self.logical_tick, bool) or self.logical_tick < 0:
            raise ValueError("observation_tick_invalid")
        if not isinstance(self.values, Mapping):
            raise TypeError("observation_values_must_be_mapping")
        if any(not isinstance(key, str) or not key for key in self.values):
            raise ValueError("observation_field_invalid")
        object.__setattr__(self, "values", dict(self.values))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DecisionDraft:
    commitment_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    intent_type: str | None = None
    parameters: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SemanticIntent:
    intent_id: str
    decision_id: str
    actor_id: str
    logical_tick: int
    intent_type: str
    parameters: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DecisionRecord:
    decision_id: str
    observation_id: str
    actor_id: str
    logical_tick: int
    definition_id: str
    definition_version: str
    definition_sha256: str
    commitment_ids: tuple[str, ...]
    used_observation_fields: tuple[str, ...]
    reason_codes: tuple[str, ...]
    intent_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DecisionOutcome:
    decision: DecisionRecord
    intent: SemanticIntent | None


Policy = Callable[[Mapping[str, Any]], DecisionDraft]


class DefinitionDrivenAgent:
    """Enforce a Definition binding around a small deterministic policy."""

    def __init__(self, binding: DefinitionBinding, policy: Policy) -> None:
        self.binding = binding
        self._policy = policy

    def decide(self, observation: AgentObservation) -> DecisionOutcome:
        if observation.actor_id != self.binding.participant_id:
            raise AgentConformanceError("observation_actor_mismatch")
        extra = set(observation.values) - self.binding.allowed_observations
        if extra:
            raise AgentConformanceError(
                "undeclared_observation_fields:" + ",".join(sorted(extra))
            )
        missing = self.binding.allowed_observations - set(observation.values)
        if missing:
            raise AgentConformanceError(
                "missing_observation_fields:" + ",".join(sorted(missing))
            )
        for field_name, value in observation.values.items():
            _validate_runtime_value(
                value,
                self.binding.observation_contracts[field_name],
                f"observation_value:{field_name}",
            )
        observed = _ObservedMapping(observation.values)
        draft = self._policy(observed)
        if not isinstance(draft, DecisionDraft):
            raise AgentConformanceError("policy_return_type_invalid")
        if not draft.commitment_ids or len(draft.commitment_ids) != len(
            set(draft.commitment_ids)
        ):
            raise AgentConformanceError("decision_commitment_ids_invalid")
        unknown_commitments = set(draft.commitment_ids) - set(
            self.binding.decision_commitment_ids
        )
        if unknown_commitments:
            raise AgentConformanceError(
                "unbound_decision_commitments:" + ",".join(sorted(unknown_commitments))
            )
        permitted_observations = frozenset().union(
            *(self.binding.commitment_observations[item] for item in draft.commitment_ids)
        )
        unexpected_access = observed.accessed - permitted_observations
        if unexpected_access:
            raise AgentConformanceError(
                "observation_not_permitted_by_commitments:"
                + ",".join(sorted(unexpected_access))
            )
        if not draft.reason_codes or len(draft.reason_codes) != len(set(draft.reason_codes)):
            raise AgentConformanceError("decision_reason_codes_invalid")
        if not isinstance(draft.parameters, Mapping):
            raise AgentConformanceError("decision_parameters_must_be_mapping")
        parameters = dict(draft.parameters)
        if draft.intent_type is None:
            if parameters:
                raise AgentConformanceError("zero_intent_decision_has_parameters")
        elif draft.intent_type not in self.binding.allowed_intents:
            raise AgentConformanceError(f"intent_outside_definition:{draft.intent_type}")
        elif draft.intent_type not in frozenset().union(
            *(self.binding.commitment_intents[item] for item in draft.commitment_ids)
        ):
            raise AgentConformanceError(
                f"intent_not_permitted_by_commitments:{draft.intent_type}"
            )
        else:
            parameter_contracts = self.binding.intent_contracts[draft.intent_type]
            missing_parameters = set(parameter_contracts) - set(parameters)
            if missing_parameters:
                raise AgentConformanceError(
                    "intent_parameters_missing:" + ",".join(sorted(missing_parameters))
                )
            extra_parameters = set(parameters) - set(parameter_contracts)
            if extra_parameters:
                raise AgentConformanceError(
                    "intent_parameters_undeclared:" + ",".join(sorted(extra_parameters))
                )
            for parameter_name, value in parameters.items():
                _validate_runtime_value(
                    value,
                    parameter_contracts[parameter_name],
                    f"intent_parameter:{draft.intent_type}:{parameter_name}",
                )

        decision_preimage = {
            "actor_id": observation.actor_id,
            "commitment_ids": list(draft.commitment_ids),
            "definition_sha256": self.binding.content_sha256,
            "intent_type": draft.intent_type,
            "logical_tick": observation.logical_tick,
            "observation_id": observation.observation_id,
            "parameters": parameters,
            "reason_codes": list(draft.reason_codes),
        }
        decision_id = _stable_id("decision", decision_preimage)
        intent = None
        if draft.intent_type is not None:
            intent_id = _stable_id(
                "intent",
                {
                    "decision_id": decision_id,
                    "intent_type": draft.intent_type,
                    "parameters": parameters,
                },
            )
            intent = SemanticIntent(
                intent_id=intent_id,
                decision_id=decision_id,
                actor_id=observation.actor_id,
                logical_tick=observation.logical_tick,
                intent_type=draft.intent_type,
                parameters=parameters,
            )
        decision = DecisionRecord(
            decision_id=decision_id,
            observation_id=observation.observation_id,
            actor_id=observation.actor_id,
            logical_tick=observation.logical_tick,
            definition_id=self.binding.definition_id,
            definition_version=self.binding.version,
            definition_sha256=self.binding.content_sha256,
            commitment_ids=draft.commitment_ids,
            used_observation_fields=tuple(sorted(observed.accessed)),
            reason_codes=draft.reason_codes,
            intent_ids=(() if intent is None else (intent.intent_id,)),
        )
        return DecisionOutcome(decision=decision, intent=intent)
