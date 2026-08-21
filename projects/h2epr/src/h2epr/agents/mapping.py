"""Strict loaders and validators for executable Agent Definition mappings.

Markdown Definitions and their reviewed specifications remain authoritative.
The machine files loaded here are derived projections: a changed source hash,
inventory mismatch, undeclared parameter, or carrier conflict is rejected
instead of repaired by an adapter.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
import re
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence


MAPPING_SCHEMA_VERSION = "h2epr.agent-definition-mapping.v0_2_2"
INTENT_REGISTRY_SCHEMA_VERSION = "h2epr.intent-registry-machine.v0_2"
LIFECYCLE_REGISTRY_SCHEMA_VERSION = "h2epr.lifecycle-registry-machine.v0_2"
OBSERVATION_REGISTRY_SCHEMA_VERSION = "h2epr.observation-registry-machine.v0_1"

_STABLE_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,127}$")
_COMMITMENT_HEADING = re.compile(
    r"^#### `(?P<commitment>DC-[A-Z]+-[0-9]+)`[^\n]*$", re.MULTILINE
)
_PERMITTED_INTENTS = re.compile(
    r"\*\*Permitted intents\.\*\*(?P<body>.*?)(?:\n\n|\Z)", re.DOTALL
)
_SEMANTIC_ID = re.compile(r"^[a-z][a-z0-9_]*$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")

_PARAMETER_TYPES = frozenset(
    {
        "enum",
        "nullable_time_value",
        "number",
        "stable_id",
        "stable_id_array",
        "time_value",
    }
)
_CARRIERS = frozenset(
    {
        "claimed_authority_refs",
        "expiry_time",
        "parameters",
        "resource_offer_or_request",
        "target_entity_ids",
    }
)
_CONDITIONAL_RULES = frozenset(
    {
        "exactly_one_group",
        "required_when_context_true",
        "required_when_parameter_in",
    }
)
_OBSERVATION_VALUE_TYPES = frozenset(
    {"enum", "nullable_stable_id", "stable_id", "status_reason_pair"}
)


class MappingValidationError(ValueError):
    """A derived machine mapping is stale, incomplete, or contradictory."""


class IntentConformanceError(ValueError):
    """A semantic intent escapes its reviewed mapping envelope."""


class ObservationConformanceError(ValueError):
    """A runtime observation escapes its Definition-derived semantic domain."""


class LifecycleConformanceError(ValueError):
    """A requested business-state transition is not registered."""


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise MappingValidationError(f"invalid_{name}")
    return value


def _stable_id(value: Any, name: str) -> str:
    result = _string(value, name)
    if _STABLE_ID.fullmatch(result) is None:
        raise MappingValidationError(f"invalid_{name}")
    return result


def _sha256(value: Any, name: str) -> str:
    result = _string(value, name)
    if _SHA256.fullmatch(result) is None:
        raise MappingValidationError(f"invalid_{name}")
    return result


def _bool(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise MappingValidationError(f"invalid_{name}")
    return value


def _exact_keys(value: Mapping[str, Any], expected: set[str], name: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = ",".join(sorted(expected - actual))
        extra = ",".join(sorted(actual - expected))
        raise MappingValidationError(f"{name}_keys_mismatch:missing={missing}:extra={extra}")


def _ordered_unique_strings(
    value: Any,
    name: str,
    *,
    allow_empty: bool = False,
    sorted_required: bool = True,
) -> tuple[str, ...]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise MappingValidationError(f"invalid_{name}")
    result = tuple(_string(item, name) for item in value)
    if len(result) != len(set(result)):
        raise MappingValidationError(f"duplicate_{name}")
    if sorted_required and result != tuple(sorted(result)):
        raise MappingValidationError(f"unsorted_{name}")
    return result


def _project_file(root: Path, value: Any, name: str) -> Path:
    relative = Path(_string(value, name))
    if relative.is_absolute() or ".." in relative.parts:
        raise MappingValidationError(f"unsafe_{name}")
    path = root / relative
    if not path.is_file():
        raise MappingValidationError(f"missing_{name}:{relative.as_posix()}")
    return path


def _read_json(path: Path, name: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MappingValidationError(f"invalid_json:{name}") from exc
    if not isinstance(value, dict):
        raise MappingValidationError(f"json_object_required:{name}")
    return value


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
            raise MappingValidationError("h2epr_project_root_not_found")
        root = roots[0]
    return root


@dataclass(frozen=True)
class ParameterContract:
    """One semantic value and its single canonical V1 carrier."""

    value_type: str
    carrier: str
    values: tuple[str, ...] = ()


@dataclass(frozen=True)
class ObservationContract:
    """One Definition observation's accepted runtime value representation."""

    value_type: str
    values: tuple[str, ...] = ()

    def validate(self, value: Any, *, availability: str, context: str) -> None:
        if availability not in {"delivered", "unavailable", "unknown"}:
            raise ObservationConformanceError(
                f"observation_availability_invalid:{context}"
            )
        if self.value_type == "enum":
            if not isinstance(value, str) or value not in self.values:
                raise ObservationConformanceError(
                    f"observation_value_outside_enum:{context}"
                )
            if availability == "unavailable":
                if "unknown" not in self.values or value != "unknown":
                    raise ObservationConformanceError(
                        f"unavailable_observation_requires_unknown:{context}"
                    )
            return
        if self.value_type == "stable_id":
            if not isinstance(value, str) or _STABLE_ID.fullmatch(value) is None:
                raise ObservationConformanceError(
                    f"observation_value_invalid_stable_id:{context}"
                )
            if availability == "unavailable":
                raise ObservationConformanceError(
                    f"unavailable_observation_has_value:{context}"
                )
            return
        if self.value_type == "nullable_stable_id":
            if value is not None and (
                not isinstance(value, str) or _STABLE_ID.fullmatch(value) is None
            ):
                raise ObservationConformanceError(
                    f"observation_value_invalid_nullable_stable_id:{context}"
                )
            if availability == "unavailable" and value is not None:
                raise ObservationConformanceError(
                    f"unavailable_observation_has_value:{context}"
                )
            if availability == "delivered" and value is None:
                raise ObservationConformanceError(
                    f"delivered_observation_missing_value:{context}"
                )
            return
        if self.value_type == "status_reason_pair":
            if not isinstance(value, list) or len(value) != 2:
                raise ObservationConformanceError(
                    f"observation_status_reason_pair_invalid:{context}"
                )
            status, reason = value
            if not isinstance(status, str) or status not in self.values:
                raise ObservationConformanceError(
                    f"observation_status_outside_enum:{context}"
                )
            if status == "none":
                if reason is not None:
                    raise ObservationConformanceError(
                        f"neutral_observation_has_reason:{context}"
                    )
            elif not isinstance(reason, str) or _STABLE_ID.fullmatch(reason) is None:
                raise ObservationConformanceError(
                    f"nonneutral_observation_missing_reason:{context}"
                )
            if availability == "unavailable" and value != ["none", None]:
                raise ObservationConformanceError(
                    f"unavailable_observation_has_value:{context}"
                )
            return
        raise AssertionError(self.value_type)


@dataclass(frozen=True)
class ConditionalParameterRule:
    rule: str
    groups: tuple[Mapping[str, ParameterContract], ...] = ()
    parameter: str | None = None
    contract: ParameterContract | None = None
    context_key: str | None = None
    source_parameter: str | None = None
    values: tuple[str, ...] = ()


@dataclass(frozen=True)
class IntentDefinition:
    semantic_id: str
    actor_id: str
    commitment_ids: tuple[str, ...]
    observations: frozenset[str]
    participant_state_inputs: frozenset[str]
    authority_refs_required: int
    required_parameters: Mapping[str, ParameterContract]
    optional_parameters: Mapping[str, ParameterContract]
    conditional_rules: tuple[ConditionalParameterRule, ...]
    lifecycle_rule_id: str
    message_performative: str | None
    forbidden_self_results: tuple[str, ...]
    enabled_variants: frozenset[str]

    @property
    def declared_parameter_names(self) -> frozenset[str]:
        names = set(self.required_parameters) | set(self.optional_parameters)
        for rule in self.conditional_rules:
            if rule.parameter is not None:
                names.add(rule.parameter)
            for group in rule.groups:
                names.update(group)
        return frozenset(names)

    def parameter_contract(self, name: str) -> ParameterContract:
        if name in self.required_parameters:
            return self.required_parameters[name]
        if name in self.optional_parameters:
            return self.optional_parameters[name]
        for rule in self.conditional_rules:
            if rule.parameter == name and rule.contract is not None:
                return rule.contract
            for group in rule.groups:
                if name in group:
                    return group[name]
        raise KeyError(name)


@dataclass(frozen=True)
class ParticipantMapping:
    participant_id: str
    definition_id: str
    version: str
    definition_path: str
    content_sha256: str
    representation_class: str
    decision_commitments: Mapping[str, frozenset[str]]
    hard_obligation_ids: tuple[str, ...]
    behavioral_hypothesis_ids: tuple[str, ...]
    scenario_conditional_commitment_ids: tuple[str, ...]
    observations: frozenset[str]
    participant_state: tuple[str, ...]
    intents: frozenset[str]


@dataclass(frozen=True)
class LifecycleTrack:
    track_id: str
    states: frozenset[str]
    terminal_states: frozenset[str]
    transitions: frozenset[tuple[str, str]]


@dataclass(frozen=True)
class LifecycleFamily:
    family_id: str
    authority: str
    tracks: Mapping[str, LifecycleTrack]


@dataclass(frozen=True)
class LifecycleRegistry:
    registry_id: str
    version: str
    families: Mapping[str, LifecycleFamily]

    def assert_transition(
        self,
        family_id: str,
        before: str,
        after: str,
        *,
        track_id: str = "default",
    ) -> None:
        family = self.families.get(family_id)
        if family is None:
            raise LifecycleConformanceError(f"unknown_lifecycle_family:{family_id}")
        track = family.tracks.get(track_id)
        if track is None:
            raise LifecycleConformanceError(
                f"unknown_lifecycle_track:{family_id}:{track_id}"
            )
        if before not in track.states or after not in track.states:
            raise LifecycleConformanceError(
                f"unknown_lifecycle_state:{family_id}:{track_id}:{before}:{after}"
            )
        if (before, after) not in track.transitions:
            raise LifecycleConformanceError(
                f"illegal_lifecycle_transition:{family_id}:{track_id}:{before}:{after}"
            )


@dataclass(frozen=True)
class SemanticIntentProjection:
    definition: IntentDefinition
    semantic_parameters: Mapping[str, Any]
    parameter_values: Mapping[str, Any]
    target_entity_ids: tuple[str, ...]
    claimed_authority_refs: tuple[str, ...]
    resource_values: Mapping[str, Any]
    expiry_time: Any


@dataclass(frozen=True)
class ExecutableDefinitionMapping:
    mapping_profile_id: str
    status: str
    observation_registry_id: str
    observation_registry_version: str
    intent_registry_id: str
    intent_registry_version: str
    action_schema_version: str
    message_content_schema_version: str
    scenario_variant: str
    scenario_basis_ref: str
    causal_scope: Mapping[str, Any]
    participants: Mapping[str, ParticipantMapping]
    observation_contracts: Mapping[str, Mapping[str, ObservationContract]]
    intents: Mapping[str, IntentDefinition]
    lifecycles: LifecycleRegistry

    def validate_observation_values(
        self,
        *,
        actor_id: str,
        values: Mapping[str, Any],
        availability: Mapping[str, str],
    ) -> None:
        participant = self.participants.get(actor_id)
        contracts = self.observation_contracts.get(actor_id)
        if participant is None or contracts is None:
            raise ObservationConformanceError(f"observation_actor_unknown:{actor_id}")
        if set(values) != participant.observations or set(availability) != set(values):
            raise ObservationConformanceError(
                f"observation_contract_inventory_mismatch:{actor_id}"
            )
        for semantic_id, value in values.items():
            contract = contracts.get(semantic_id)
            if contract is None:
                raise ObservationConformanceError(
                    f"observation_contract_missing:{actor_id}:{semantic_id}"
                )
            contract.validate(
                value,
                availability=availability[semantic_id],
                context=f"{actor_id}:{semantic_id}",
            )
        self.validate_scenario_observation_coherence(
            actor_id=actor_id,
            values=values,
        )

    def validate_scenario_observation_coherence(
        self,
        *,
        actor_id: str,
        values: Mapping[str, Any],
    ) -> None:
        """Reject actor-local values that cannot coexist in the bound scenario.

        The per-field registry checks vocabulary.  This check preserves the
        separately bound structural interpretation and cross-object order.
        """

        if actor_id != "new_york_clearing_house":
            return
        disposition = values.get("case_disposition_status")
        result = values.get("delivered_case_result")
        proposal = values.get("resource_proposal_status")
        if not (
            isinstance(disposition, list)
            and len(disposition) == 2
            and isinstance(result, list)
            and len(result) == 2
            and isinstance(proposal, str)
        ):
            return  # individual contracts report malformed values first

        disposition_status = disposition[0]
        result_status = result[0]
        if values.get("delivered_request") is None and values.get(
            "request_authorization_evidence"
        ) not in {"absent", "unknown"}:
            raise ObservationConformanceError(
                "request_authorization_evidence_without_delivered_request:"
                "request_authorization_evidence"
            )
        if self.scenario_variant == "NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE":
            if disposition_status == "conditioned_proposal":
                raise ObservationConformanceError(
                    "conditioned_proposal_unreachable_in_conservative_variant:"
                    "case_disposition_status"
                )
            if proposal != "none":
                raise ObservationConformanceError(
                    "resource_proposal_unreachable_in_conservative_variant:"
                    "resource_proposal_status"
                )
            if result_status != "none":
                raise ObservationConformanceError(
                    "proposal_result_unreachable_in_conservative_variant:"
                    "delivered_case_result"
                )
            return

        if disposition_status == "conditioned_proposal" and proposal == "none":
            raise ObservationConformanceError(
                "conditioned_disposition_without_resource_proposal"
            )
        if result_status != "none" and proposal == "none":
            raise ObservationConformanceError(
                "delivered_result_without_prior_resource_proposal"
            )

    def validate_semantic_intent(
        self,
        *,
        actor_id: str,
        semantic_id: str,
        commitment_ids: Sequence[str],
        used_observations: Iterable[str],
        used_participant_state: Iterable[str] = (),
        parameters: Mapping[str, Any],
        authority_refs: Sequence[str] = (),
        context: Mapping[str, Any] | None = None,
    ) -> SemanticIntentProjection:
        participant = self.participants.get(actor_id)
        if participant is None:
            raise IntentConformanceError(f"unknown_actor:{actor_id}")
        definition = self.intents.get(semantic_id)
        if definition is None or semantic_id not in participant.intents:
            raise IntentConformanceError(f"intent_outside_definition:{semantic_id}")
        if definition.actor_id != actor_id:
            raise IntentConformanceError("intent_actor_mismatch")
        if definition.enabled_variants and self.scenario_variant not in definition.enabled_variants:
            raise IntentConformanceError(
                f"intent_disabled_by_scenario_variant:{semantic_id}:{self.scenario_variant}"
            )

        commitments = tuple(commitment_ids)
        if not commitments or len(commitments) != len(set(commitments)):
            raise IntentConformanceError("decision_commitment_ids_invalid")
        if not set(commitments) <= set(definition.commitment_ids):
            raise IntentConformanceError(
                f"intent_not_permitted_by_commitments:{semantic_id}"
            )
        for commitment_id in commitments:
            if semantic_id not in participant.decision_commitments[commitment_id]:
                raise IntentConformanceError(
                    f"binding_commitment_mismatch:{commitment_id}:{semantic_id}"
                )

        observations = tuple(used_observations)
        if not observations or len(observations) != len(set(observations)):
            raise IntentConformanceError("used_observations_invalid")
        observation_set = set(observations)
        missing_direct_observations = definition.observations - observation_set
        if missing_direct_observations:
            raise IntentConformanceError(
                "declared_intent_observation_not_used:"
                + ",".join(sorted(missing_direct_observations))
            )
        unknown_observations = observation_set - participant.observations
        if unknown_observations:
            raise IntentConformanceError(
                "observation_outside_participant_definition:"
                + ",".join(sorted(unknown_observations))
            )

        state_inputs = tuple(used_participant_state)
        if len(state_inputs) != len(set(state_inputs)):
            raise IntentConformanceError("used_participant_state_invalid")
        unknown_state = set(state_inputs) - definition.participant_state_inputs
        if unknown_state:
            raise IntentConformanceError(
                "participant_state_not_permitted_by_intent:"
                + ",".join(sorted(unknown_state))
            )

        if not isinstance(parameters, Mapping):
            raise IntentConformanceError("semantic_parameters_must_be_mapping")
        values = dict(parameters)
        context_values = dict(context or {})
        missing = set(definition.required_parameters) - set(values)
        if missing:
            raise IntentConformanceError(
                "intent_parameters_missing:" + ",".join(sorted(missing))
            )
        extra = set(values) - definition.declared_parameter_names
        if extra:
            raise IntentConformanceError(
                "intent_parameters_undeclared:" + ",".join(sorted(extra))
            )
        _validate_conditional_parameters(definition, values, context_values)
        for name, value in values.items():
            _validate_semantic_value(
                value,
                definition.parameter_contract(name),
                f"intent_parameter:{semantic_id}:{name}",
            )

        external_authority = tuple(authority_refs)
        if len(external_authority) != len(set(external_authority)):
            raise IntentConformanceError("duplicate_claimed_authority_ref")
        for ref in external_authority:
            _validate_stable_id_value(ref, "claimed_authority_ref")

        projected: dict[str, dict[str, Any]] = {
            "parameters": {},
            "resource_offer_or_request": {},
        }
        target_ids: list[str] = []
        projected_authority: list[str] = list(external_authority)
        expiry_time: Any = None
        expiry_present = False
        for name, value in values.items():
            contract = definition.parameter_contract(name)
            if contract.carrier == "parameters":
                projected["parameters"][name] = value
            elif contract.carrier == "resource_offer_or_request":
                projected["resource_offer_or_request"][name] = value
            elif contract.carrier == "target_entity_ids":
                target_ids.extend(value if isinstance(value, list) else [value])
            elif contract.carrier == "claimed_authority_refs":
                projected_authority.extend(value if isinstance(value, list) else [value])
            elif contract.carrier == "expiry_time":
                if expiry_present:
                    raise IntentConformanceError("multiple_expiry_time_values")
                expiry_time = value
                expiry_present = True
            else:  # pragma: no cover - rejected while loading
                raise AssertionError(contract.carrier)

        if len(target_ids) != len(set(target_ids)):
            raise IntentConformanceError("duplicate_target_entity_id")
        if len(projected_authority) != len(set(projected_authority)):
            raise IntentConformanceError("duplicate_claimed_authority_ref")
        if len(projected_authority) < definition.authority_refs_required:
            raise IntentConformanceError(
                f"claimed_authority_refs_missing:{semantic_id}"
            )

        return SemanticIntentProjection(
            definition=definition,
            semantic_parameters=MappingProxyType(values),
            parameter_values=MappingProxyType(projected["parameters"]),
            target_entity_ids=tuple(target_ids),
            claimed_authority_refs=tuple(projected_authority),
            resource_values=MappingProxyType(projected["resource_offer_or_request"]),
            expiry_time=expiry_time,
        )


def _parse_parameter_contract(value: Any, name: str) -> ParameterContract:
    if not isinstance(value, dict):
        raise MappingValidationError(f"invalid_parameter_contract:{name}")
    allowed = {"carrier", "type", "values"}
    if set(value) - allowed:
        raise MappingValidationError(f"unknown_parameter_contract_fields:{name}")
    value_type = _string(value.get("type"), f"parameter_type:{name}")
    carrier = _string(value.get("carrier"), f"parameter_carrier:{name}")
    if value_type not in _PARAMETER_TYPES:
        raise MappingValidationError(f"unsupported_parameter_type:{name}:{value_type}")
    if carrier not in _CARRIERS:
        raise MappingValidationError(f"unsupported_parameter_carrier:{name}:{carrier}")
    raw_values = value.get("values", [])
    values = _ordered_unique_strings(
        raw_values,
        f"parameter_values:{name}",
        allow_empty=True,
        sorted_required=False,
    )
    if (value_type == "enum") != bool(values):
        raise MappingValidationError(f"enum_values_mismatch:{name}")
    return ParameterContract(value_type=value_type, carrier=carrier, values=values)


def _parse_parameter_map(value: Any, name: str) -> Mapping[str, ParameterContract]:
    if not isinstance(value, dict):
        raise MappingValidationError(f"invalid_parameter_map:{name}")
    result: dict[str, ParameterContract] = {}
    for parameter_name, contract in value.items():
        if _SEMANTIC_ID.fullmatch(parameter_name) is None:
            raise MappingValidationError(f"invalid_parameter_name:{parameter_name}")
        result[parameter_name] = _parse_parameter_contract(
            contract, f"{name}:{parameter_name}"
        )
    return MappingProxyType(result)


def _parse_conditional_rules(value: Any, intent_id: str) -> tuple[ConditionalParameterRule, ...]:
    if not isinstance(value, list):
        raise MappingValidationError(f"conditional_rules_invalid:{intent_id}")
    result: list[ConditionalParameterRule] = []
    declared: set[str] = set()
    for index, row in enumerate(value):
        if not isinstance(row, dict):
            raise MappingValidationError(f"conditional_rule_invalid:{intent_id}:{index}")
        rule = _string(row.get("rule"), f"conditional_rule:{intent_id}:{index}")
        if rule not in _CONDITIONAL_RULES:
            raise MappingValidationError(f"conditional_rule_unknown:{intent_id}:{rule}")
        if rule == "exactly_one_group":
            _exact_keys(row, {"groups", "rule"}, f"conditional_rule:{intent_id}:{index}")
            raw_groups = row["groups"]
            if not isinstance(raw_groups, list) or len(raw_groups) < 2:
                raise MappingValidationError(f"conditional_groups_invalid:{intent_id}")
            groups = tuple(
                _parse_parameter_map(group, f"conditional_group:{intent_id}:{group_index}")
                for group_index, group in enumerate(raw_groups)
            )
            names = [name for group in groups for name in group]
            if len(names) != len(set(names)) or declared.intersection(names):
                raise MappingValidationError(f"conditional_parameter_duplicate:{intent_id}")
            declared.update(names)
            result.append(ConditionalParameterRule(rule=rule, groups=groups))
            continue

        expected = {
            "context_key", "contract", "parameter", "rule"
        } if rule == "required_when_context_true" else {
            "contract", "parameter", "rule", "source_parameter", "values"
        }
        _exact_keys(row, expected, f"conditional_rule:{intent_id}:{index}")
        parameter = _string(row["parameter"], f"conditional_parameter:{intent_id}")
        if parameter in declared or _SEMANTIC_ID.fullmatch(parameter) is None:
            raise MappingValidationError(f"conditional_parameter_duplicate:{intent_id}:{parameter}")
        declared.add(parameter)
        contract = _parse_parameter_contract(
            row["contract"], f"conditional_parameter:{intent_id}:{parameter}"
        )
        if rule == "required_when_context_true":
            result.append(
                ConditionalParameterRule(
                    rule=rule,
                    parameter=parameter,
                    contract=contract,
                    context_key=_string(row["context_key"], "context_key"),
                )
            )
        else:
            result.append(
                ConditionalParameterRule(
                    rule=rule,
                    parameter=parameter,
                    contract=contract,
                    source_parameter=_string(row["source_parameter"], "source_parameter"),
                    values=_ordered_unique_strings(
                        row["values"], "conditional_values", sorted_required=False
                    ),
                )
            )
    return tuple(result)


def _validate_conditional_parameters(
    definition: IntentDefinition,
    values: Mapping[str, Any],
    context: Mapping[str, Any],
) -> None:
    for rule in definition.conditional_rules:
        if rule.rule == "exactly_one_group":
            presence = [
                all(name in values for name in group)
                and not any(name not in values for name in group)
                for group in rule.groups
            ]
            partial = [
                group_index
                for group_index, group in enumerate(rule.groups)
                if any(name in values for name in group)
                and not all(name in values for name in group)
            ]
            if partial or sum(presence) != 1:
                raise IntentConformanceError(
                    f"conditional_exactly_one_group_failed:{definition.semantic_id}"
                )
        elif rule.rule == "required_when_context_true":
            enabled = context.get(rule.context_key or "", False)
            if not isinstance(enabled, bool):
                raise IntentConformanceError(
                    f"conditional_context_not_boolean:{rule.context_key}"
                )
            if enabled and rule.parameter not in values:
                raise IntentConformanceError(
                    f"conditional_parameter_missing:{rule.parameter}"
                )
        elif rule.rule == "required_when_parameter_in":
            enabled = values.get(rule.source_parameter or "") in rule.values
            present = rule.parameter in values
            if enabled and not present:
                raise IntentConformanceError(
                    f"conditional_parameter_missing:{rule.parameter}"
                )
            if not enabled and present:
                raise IntentConformanceError(
                    f"conditional_parameter_forbidden:{rule.parameter}"
                )
        else:  # pragma: no cover - rejected while loading
            raise AssertionError(rule.rule)


def _validate_stable_id_value(value: Any, context: str) -> None:
    if not isinstance(value, str) or _STABLE_ID.fullmatch(value) is None:
        raise IntentConformanceError(f"{context}_invalid_stable_id")


def _is_time_value(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value) and len(value) <= 128
    if not isinstance(value, Mapping):
        return False
    return set(value) == {"lower", "precision", "timezone", "uncertainty", "upper"}


def _validate_semantic_value(
    value: Any, contract: ParameterContract, context: str
) -> None:
    if contract.value_type == "stable_id":
        _validate_stable_id_value(value, context)
    elif contract.value_type == "stable_id_array":
        if not isinstance(value, list) or len(value) != len(set(value)):
            raise IntentConformanceError(f"{context}_invalid_stable_id_array")
        for item in value:
            _validate_stable_id_value(item, context)
    elif contract.value_type == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise IntentConformanceError(f"{context}_invalid_number")
    elif contract.value_type == "enum":
        if value not in contract.values:
            raise IntentConformanceError(f"{context}_outside_enum")
    elif contract.value_type == "time_value":
        if not _is_time_value(value):
            raise IntentConformanceError(f"{context}_invalid_time_value")
    elif contract.value_type == "nullable_time_value":
        if value is not None and not _is_time_value(value):
            raise IntentConformanceError(f"{context}_invalid_nullable_time_value")
    else:  # pragma: no cover - rejected while loading
        raise AssertionError(contract.value_type)


def _parse_intent_registry(
    document: Mapping[str, Any], root: Path, registry_path: Path
) -> tuple[str, str, str, str, Mapping[str, IntentDefinition]]:
    _exact_keys(
        document,
        {
            "action_schema_version",
            "actor_intent_counts",
            "authority",
            "intents",
            "message_content_schema_version",
            "registry_id",
            "schema_version",
            "source_path",
            "source_sha256",
            "version",
        },
        "intent_registry",
    )
    if document["schema_version"] != INTENT_REGISTRY_SCHEMA_VERSION:
        raise MappingValidationError("intent_registry_schema_version_mismatch")
    if document["authority"] != "derived_mapping_only":
        raise MappingValidationError("intent_registry_authority_mismatch")
    source = _project_file(root, document["source_path"], "intent_registry_source_path")
    if _sha256_file(source) != _sha256(document["source_sha256"], "intent_source_sha256"):
        raise MappingValidationError("intent_registry_source_sha256_mismatch")
    if _sha256_file(registry_path) == document["source_sha256"]:
        raise MappingValidationError("intent_registry_cannot_be_its_own_source")

    counts = document["actor_intent_counts"]
    if not isinstance(counts, dict) or not counts:
        raise MappingValidationError("actor_intent_counts_invalid")
    for actor, count in counts.items():
        _stable_id(actor, "actor_id")
        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            raise MappingValidationError("actor_intent_count_invalid")

    rows = document["intents"]
    if not isinstance(rows, list) or not rows:
        raise MappingValidationError("intent_registry_empty")
    result: dict[str, IntentDefinition] = {}
    actual_counts = {actor: 0 for actor in counts}
    required_keys = {
        "actor_id",
        "authority_refs_required",
        "commitment_ids",
        "forbidden_self_results",
        "lifecycle_rule_id",
        "message_performative",
        "observations",
        "parameters",
        "semantic_id",
    }
    for row in rows:
        if not isinstance(row, dict):
            raise MappingValidationError("intent_registry_row_invalid")
        allowed_keys = required_keys | {"enabled_variants", "participant_state_inputs"}
        if not required_keys <= set(row) or set(row) - allowed_keys:
            raise MappingValidationError("intent_registry_row_keys_mismatch")
        semantic_id = _string(row["semantic_id"], "semantic_id")
        if _SEMANTIC_ID.fullmatch(semantic_id) is None or semantic_id in result:
            raise MappingValidationError(f"semantic_intent_identity_invalid:{semantic_id}")
        actor_id = _stable_id(row["actor_id"], "actor_id")
        if actor_id not in counts:
            raise MappingValidationError(f"intent_actor_not_counted:{actor_id}")
        actual_counts[actor_id] += 1
        commitments = _ordered_unique_strings(
            row["commitment_ids"], "intent_commitment_ids"
        )
        observations = frozenset(
            _ordered_unique_strings(row["observations"], "intent_observations")
        )
        participant_state_inputs = frozenset(
            _ordered_unique_strings(
                row.get("participant_state_inputs", []),
                "intent_participant_state_inputs",
                allow_empty=True,
            )
        )
        authority_required = row["authority_refs_required"]
        if (
            isinstance(authority_required, bool)
            or not isinstance(authority_required, int)
            or authority_required < 0
        ):
            raise MappingValidationError("authority_refs_required_invalid")
        parameters = row["parameters"]
        if not isinstance(parameters, dict):
            raise MappingValidationError(f"intent_parameters_invalid:{semantic_id}")
        _exact_keys(parameters, {"conditional", "optional", "required"}, "intent_parameters")
        required_parameters = _parse_parameter_map(
            parameters["required"], f"required:{semantic_id}"
        )
        optional_parameters = _parse_parameter_map(
            parameters["optional"], f"optional:{semantic_id}"
        )
        if set(required_parameters).intersection(optional_parameters):
            raise MappingValidationError(f"parameter_required_optional_overlap:{semantic_id}")
        conditional = _parse_conditional_rules(parameters["conditional"], semantic_id)
        conditional_names = {
            name
            for rule in conditional
            for name in (
                ([rule.parameter] if rule.parameter else [])
                + [item for group in rule.groups for item in group]
            )
        }
        if conditional_names.intersection(required_parameters) or conditional_names.intersection(
            optional_parameters
        ):
            raise MappingValidationError(f"conditional_parameter_overlap:{semantic_id}")
        enabled = frozenset(
            _ordered_unique_strings(
                row.get("enabled_variants", []),
                "enabled_variants",
                allow_empty=True,
            )
        )
        message = row["message_performative"]
        if message is not None:
            message = _stable_id(message, "message_performative")
        forbidden = _ordered_unique_strings(
            row["forbidden_self_results"],
            "forbidden_self_results",
            sorted_required=False,
        )
        result[semantic_id] = IntentDefinition(
            semantic_id=semantic_id,
            actor_id=actor_id,
            commitment_ids=commitments,
            observations=observations,
            participant_state_inputs=participant_state_inputs,
            authority_refs_required=authority_required,
            required_parameters=required_parameters,
            optional_parameters=optional_parameters,
            conditional_rules=conditional,
            lifecycle_rule_id=_stable_id(row["lifecycle_rule_id"], "lifecycle_rule_id"),
            message_performative=message,
            forbidden_self_results=forbidden,
            enabled_variants=enabled,
        )
    if actual_counts != counts or sum(counts.values()) != len(result):
        raise MappingValidationError("actor_intent_counts_mismatch")
    return (
        _stable_id(document["registry_id"], "intent_registry_id"),
        _stable_id(document["version"], "intent_registry_version"),
        _stable_id(document["action_schema_version"], "action_schema_version"),
        _stable_id(
            document["message_content_schema_version"],
            "message_content_schema_version",
        ),
        MappingProxyType(result),
    )


def _parse_observation_registry(
    document: Mapping[str, Any],
    root: Path,
    registry_path: Path,
) -> tuple[str, str, Mapping[str, Mapping[str, ObservationContract]]]:
    _exact_keys(
        document,
        {
            "actor_observation_counts",
            "authority",
            "observations",
            "registry_id",
            "schema_version",
            "source_path",
            "source_sha256",
            "version",
        },
        "observation_registry",
    )
    if document["schema_version"] != OBSERVATION_REGISTRY_SCHEMA_VERSION:
        raise MappingValidationError("observation_registry_schema_version_mismatch")
    if document["authority"] != "derived_mapping_only":
        raise MappingValidationError("observation_registry_authority_mismatch")
    source = _project_file(
        root, document["source_path"], "observation_registry_source_path"
    )
    source_sha256 = _sha256(
        document["source_sha256"], "observation_registry_source_sha256"
    )
    if _sha256_file(source) != source_sha256:
        raise MappingValidationError("observation_registry_source_sha256_mismatch")
    if _sha256_file(registry_path) == source_sha256:
        raise MappingValidationError("observation_registry_cannot_be_its_own_source")
    source_text = source.read_text(encoding="utf-8")

    counts = document["actor_observation_counts"]
    if not isinstance(counts, dict) or not counts:
        raise MappingValidationError("actor_observation_counts_invalid")
    for actor_id, count in counts.items():
        _stable_id(actor_id, "observation_actor_id")
        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            raise MappingValidationError("actor_observation_count_invalid")

    rows = document["observations"]
    if not isinstance(rows, list) or not rows:
        raise MappingValidationError("observation_registry_empty")
    actual_counts = {actor_id: 0 for actor_id in counts}
    result: dict[str, dict[str, ObservationContract]] = {
        actor_id: {} for actor_id in counts
    }
    previous_identity: tuple[str, str] | None = None
    for row in rows:
        if not isinstance(row, dict):
            raise MappingValidationError("observation_registry_row_invalid")
        required = {"actor_id", "semantic_id", "value_type"}
        if not required <= set(row) or set(row) - (required | {"values"}):
            raise MappingValidationError("observation_registry_row_keys_mismatch")
        actor_id = _stable_id(row["actor_id"], "observation_actor_id")
        if actor_id not in counts:
            raise MappingValidationError(
                f"observation_actor_not_counted:{actor_id}"
            )
        semantic_id = _string(row["semantic_id"], "observation_semantic_id")
        if _SEMANTIC_ID.fullmatch(semantic_id) is None:
            raise MappingValidationError(
                f"observation_semantic_id_invalid:{semantic_id}"
            )
        identity = (actor_id, semantic_id)
        if previous_identity is not None and identity <= previous_identity:
            raise MappingValidationError("observation_registry_not_strictly_sorted")
        previous_identity = identity
        if semantic_id in result[actor_id]:
            raise MappingValidationError(
                f"duplicate_observation_contract:{actor_id}:{semantic_id}"
            )
        value_type = _string(row["value_type"], "observation_value_type")
        if value_type not in _OBSERVATION_VALUE_TYPES:
            raise MappingValidationError(
                f"unsupported_observation_value_type:{semantic_id}:{value_type}"
            )
        raw_values = row.get("values", [])
        values = _ordered_unique_strings(
            raw_values,
            f"observation_values:{actor_id}:{semantic_id}",
            allow_empty=True,
            sorted_required=False,
        )
        if (value_type in {"enum", "status_reason_pair"}) != bool(values):
            raise MappingValidationError(
                f"observation_values_mismatch:{actor_id}:{semantic_id}"
            )
        if value_type == "status_reason_pair" and "none" not in values:
            raise MappingValidationError(
                f"observation_neutral_status_missing:{actor_id}:{semantic_id}"
            )
        if f"`{semantic_id}`" not in source_text:
            raise MappingValidationError(
                f"observation_missing_from_source:{actor_id}:{semantic_id}"
            )
        for item in values:
            if f"`{item}`" not in source_text:
                raise MappingValidationError(
                    f"observation_value_missing_from_source:{actor_id}:{semantic_id}:{item}"
                )
        result[actor_id][semantic_id] = ObservationContract(
            value_type=value_type,
            values=values,
        )
        actual_counts[actor_id] += 1

    if actual_counts != counts:
        raise MappingValidationError("actor_observation_counts_mismatch")
    return (
        _stable_id(document["registry_id"], "observation_registry_id"),
        _stable_id(document["version"], "observation_registry_version"),
        MappingProxyType(
            {
                actor_id: MappingProxyType(contracts)
                for actor_id, contracts in result.items()
            }
        ),
    )


def _parse_track(value: Mapping[str, Any], name: str, *, track_id: str) -> LifecycleTrack:
    _exact_keys(value, {"states", "terminal_states", "transitions"}, name)
    states = frozenset(
        _ordered_unique_strings(
            value["states"], f"states:{name}", sorted_required=False
        )
    )
    terminal = frozenset(
        _ordered_unique_strings(
            value["terminal_states"],
            f"terminal_states:{name}",
            sorted_required=False,
        )
    )
    if not terminal <= states:
        raise MappingValidationError(f"terminal_state_outside_inventory:{name}")
    raw_transitions = value["transitions"]
    if not isinstance(raw_transitions, list) or not raw_transitions:
        raise MappingValidationError(f"transitions_invalid:{name}")
    transitions: list[tuple[str, str]] = []
    for pair in raw_transitions:
        if not isinstance(pair, list) or len(pair) != 2:
            raise MappingValidationError(f"transition_invalid:{name}")
        before, after = (_string(item, f"transition:{name}") for item in pair)
        if before not in states or after not in states:
            raise MappingValidationError(f"transition_state_unknown:{name}:{before}:{after}")
        transitions.append((before, after))
    if len(transitions) != len(set(transitions)):
        raise MappingValidationError(f"duplicate_transition:{name}")
    return LifecycleTrack(
        track_id=track_id,
        states=states,
        terminal_states=terminal,
        transitions=frozenset(transitions),
    )


def _parse_lifecycle_registry(
    document: Mapping[str, Any], root: Path
) -> LifecycleRegistry:
    _exact_keys(
        document,
        {
            "authority",
            "families",
            "family_count",
            "registry_id",
            "schema_version",
            "source_path",
            "source_sha256",
            "version",
        },
        "lifecycle_registry",
    )
    if document["schema_version"] != LIFECYCLE_REGISTRY_SCHEMA_VERSION:
        raise MappingValidationError("lifecycle_registry_schema_version_mismatch")
    if document["authority"] != "derived_mapping_only":
        raise MappingValidationError("lifecycle_registry_authority_mismatch")
    source = _project_file(root, document["source_path"], "lifecycle_source_path")
    if _sha256_file(source) != _sha256(document["source_sha256"], "lifecycle_source_sha256"):
        raise MappingValidationError("lifecycle_source_sha256_mismatch")
    raw_families = document["families"]
    count = document["family_count"]
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise MappingValidationError("lifecycle_family_count_invalid")
    if not isinstance(raw_families, list) or len(raw_families) != count:
        raise MappingValidationError("lifecycle_family_count_mismatch")
    families: dict[str, LifecycleFamily] = {}
    for row in raw_families:
        if not isinstance(row, dict):
            raise MappingValidationError("lifecycle_family_invalid")
        family_id = _stable_id(row.get("family_id"), "lifecycle_family_id")
        authority = _stable_id(row.get("authority"), "lifecycle_authority")
        if family_id in families:
            raise MappingValidationError(f"duplicate_lifecycle_family:{family_id}")
        if "tracks" in row:
            _exact_keys(row, {"authority", "family_id", "tracks"}, "lifecycle_family")
            raw_tracks = row["tracks"]
            if not isinstance(raw_tracks, list) or not raw_tracks:
                raise MappingValidationError(f"lifecycle_tracks_invalid:{family_id}")
            tracks: dict[str, LifecycleTrack] = {}
            for raw_track in raw_tracks:
                if not isinstance(raw_track, dict):
                    raise MappingValidationError(f"lifecycle_track_invalid:{family_id}")
                _exact_keys(
                    raw_track,
                    {"states", "terminal_states", "track_id", "transitions"},
                    "lifecycle_track",
                )
                track_id = _stable_id(raw_track["track_id"], "lifecycle_track_id")
                if track_id in tracks:
                    raise MappingValidationError(f"duplicate_lifecycle_track:{family_id}:{track_id}")
                track_value = {key: raw_track[key] for key in ("states", "terminal_states", "transitions")}
                tracks[track_id] = _parse_track(
                    track_value, f"{family_id}:{track_id}", track_id=track_id
                )
        else:
            _exact_keys(
                row,
                {"authority", "family_id", "states", "terminal_states", "transitions"},
                "lifecycle_family",
            )
            track_value = {key: row[key] for key in ("states", "terminal_states", "transitions")}
            tracks = {
                "default": _parse_track(
                    track_value, family_id, track_id="default"
                )
            }
        families[family_id] = LifecycleFamily(
            family_id=family_id,
            authority=authority,
            tracks=MappingProxyType(tracks),
        )
    return LifecycleRegistry(
        registry_id=_stable_id(document["registry_id"], "lifecycle_registry_id"),
        version=_stable_id(document["version"], "lifecycle_registry_version"),
        families=MappingProxyType(families),
    )


def _commitment_intents(markdown: str) -> dict[str, frozenset[str]]:
    matches = list(_COMMITMENT_HEADING.finditer(markdown))
    result: dict[str, frozenset[str]] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        section = markdown[match.end():end]
        permitted = _PERMITTED_INTENTS.search(section)
        if permitted is None:
            raise MappingValidationError(
                f"permitted_intents_missing:{match.group('commitment')}"
            )
        values = {
            value
            for value in re.findall(r"`([^`]+)`", permitted.group("body"))
            if _SEMANTIC_ID.fullmatch(value)
        }
        if not values:
            raise MappingValidationError(
                f"permitted_intents_empty:{match.group('commitment')}"
            )
        result[match.group("commitment")] = frozenset(values)
    return result


def _parse_participant(
    row: Mapping[str, Any],
    *,
    root: Path,
    intents: Mapping[str, IntentDefinition],
    conformance_text: str,
) -> ParticipantMapping:
    required = {
        "behavioral_hypothesis_ids",
        "content_sha256",
        "decision_commitments",
        "definition_id",
        "definition_path",
        "hard_obligation_ids",
        "intents",
        "observations",
        "participant_id",
        "participant_state",
        "representation_class",
        "version",
    }
    optional = {"scenario_conditional_commitment_ids"}
    if set(row) not in (required, required | optional):
        raise MappingValidationError("participant_mapping_keys_mismatch")
    participant_id = _stable_id(row["participant_id"], "participant_id")
    definition_id = _stable_id(row["definition_id"], "definition_id")
    version = _stable_id(row["version"], "definition_version")
    definition_path = _string(row["definition_path"], "definition_path")
    path = _project_file(root, definition_path, "definition_path")
    content_sha256 = _sha256(row["content_sha256"], "definition_sha256")
    if _sha256_file(path) != content_sha256:
        raise MappingValidationError(f"definition_sha256_mismatch:{participant_id}")
    markdown = path.read_text(encoding="utf-8")
    marker = f"`{definition_id}`, version `{version}`"
    if marker not in markdown:
        raise MappingValidationError(f"definition_identity_marker_mismatch:{participant_id}")

    raw_commitments = row["decision_commitments"]
    if not isinstance(raw_commitments, dict) or not raw_commitments:
        raise MappingValidationError(f"decision_commitments_invalid:{participant_id}")
    commitments = {
        commitment_id: frozenset(
            _ordered_unique_strings(
                intent_ids, f"commitment_intents:{participant_id}:{commitment_id}"
            )
        )
        for commitment_id, intent_ids in raw_commitments.items()
    }
    headings = tuple(_COMMITMENT_HEADING.findall(markdown))
    if set(headings) != set(commitments) or len(headings) != len(commitments):
        raise MappingValidationError(f"commitment_inventory_mismatch:{participant_id}")
    if _commitment_intents(markdown) != commitments:
        raise MappingValidationError(f"commitment_intent_text_mismatch:{participant_id}")

    participant_intents = frozenset(
        _ordered_unique_strings(row["intents"], f"participant_intents:{participant_id}")
    )
    registry_intents = {
        semantic_id
        for semantic_id, definition in intents.items()
        if definition.actor_id == participant_id
    }
    if participant_intents != registry_intents:
        raise MappingValidationError(f"participant_intent_registry_mismatch:{participant_id}")
    from_commitments = frozenset().union(*commitments.values())
    if from_commitments != participant_intents:
        raise MappingValidationError(f"participant_intent_commitment_mismatch:{participant_id}")
    registry_commitments = {
        commitment_id: {
            semantic_id
            for semantic_id, definition in intents.items()
            if definition.actor_id == participant_id
            and commitment_id in definition.commitment_ids
        }
        for commitment_id in commitments
    }
    if registry_commitments != {key: set(value) for key, value in commitments.items()}:
        raise MappingValidationError(f"registry_commitment_parity_mismatch:{participant_id}")

    observations = frozenset(
        _ordered_unique_strings(row["observations"], f"observations:{participant_id}")
    )
    registry_observations = frozenset().union(
        *(definition.observations for definition in intents.values() if definition.actor_id == participant_id)
    )
    if observations != registry_observations:
        raise MappingValidationError(f"observation_registry_mismatch:{participant_id}")
    for observation in observations:
        if f"`{observation}`" not in markdown:
            raise MappingValidationError(
                f"observation_not_found_in_definition:{participant_id}:{observation}"
            )

    participant_state = _ordered_unique_strings(
        row["participant_state"], f"participant_state:{participant_id}"
    )
    registry_state = frozenset().union(
        *(
            definition.participant_state_inputs
            for definition in intents.values()
            if definition.actor_id == participant_id
        )
    )
    undeclared_state = registry_state - set(participant_state)
    if undeclared_state:
        raise MappingValidationError(
            "intent_participant_state_outside_definition:"
            + participant_id
            + ":"
            + ",".join(sorted(undeclared_state))
        )
    hard_obligations = _ordered_unique_strings(
        row["hard_obligation_ids"], f"hard_obligation_ids:{participant_id}"
    )
    for obligation_id in hard_obligations:
        if f"`{obligation_id}`" not in conformance_text:
            raise MappingValidationError(
                f"hard_obligation_not_found:{participant_id}:{obligation_id}"
            )
    behavioral = _ordered_unique_strings(
        row["behavioral_hypothesis_ids"],
        f"behavioral_hypothesis_ids:{participant_id}",
    )
    conditional = _ordered_unique_strings(
        row.get("scenario_conditional_commitment_ids", []),
        f"scenario_conditional_commitment_ids:{participant_id}",
        allow_empty=True,
    )
    if not set(behavioral).isdisjoint(conditional):
        raise MappingValidationError(f"commitment_class_overlap:{participant_id}")
    if set(behavioral) | set(conditional) != set(commitments):
        raise MappingValidationError(f"commitment_class_incomplete:{participant_id}")

    return ParticipantMapping(
        participant_id=participant_id,
        definition_id=definition_id,
        version=version,
        definition_path=definition_path,
        content_sha256=content_sha256,
        representation_class=_stable_id(row["representation_class"], "representation_class"),
        decision_commitments=MappingProxyType(commitments),
        hard_obligation_ids=hard_obligations,
        behavioral_hypothesis_ids=behavioral,
        scenario_conditional_commitment_ids=conditional,
        observations=observations,
        participant_state=participant_state,
        intents=participant_intents,
    )


def _validate_definition_observation_domain_parity(
    *,
    root: Path,
    participants: Mapping[str, ParticipantMapping],
    contracts: Mapping[str, Mapping[str, ObservationContract]],
) -> None:
    """Bind each machine value domain to the matching actor Definition row."""

    for actor_id, participant in participants.items():
        markdown = (root / participant.definition_path).read_text(encoding="utf-8")
        lines = markdown.splitlines()
        for semantic_id, contract in contracts[actor_id].items():
            row_pattern = re.compile(
                rf"^\|\s*`{re.escape(semantic_id)}`\s*\|"
            )
            rows = [line for line in lines if row_pattern.search(line)]
            if len(rows) != 1:
                raise MappingValidationError(
                    "definition_observation_row_identity_mismatch:"
                    f"{actor_id}:{semantic_id}"
                )
            row = rows[0]
            for value in contract.values:
                value_pattern = re.compile(
                    rf"(?<![A-Za-z0-9_]){re.escape(value)}(?![A-Za-z0-9_])"
                )
                if value_pattern.search(row) is None:
                    raise MappingValidationError(
                        "definition_observation_value_domain_mismatch:"
                        f"{actor_id}:{semantic_id}:{value}"
                    )


def load_executable_mapping(
    binding_path: str | Path,
    *,
    project_root: str | Path | None = None,
) -> ExecutableDefinitionMapping:
    """Load a fully cross-checked machine projection of reviewed Definitions."""

    path = Path(binding_path).resolve()
    if not path.is_file():
        raise MappingValidationError("binding_file_missing")
    root = _find_project_root(path, project_root)
    document = _read_json(path, "binding")
    _exact_keys(
        document,
        {
            "authority",
            "binding_schema_version",
            "causal_scope",
            "contract_carrier",
            "machine_registries",
            "mapping_profile_id",
            "participants",
            "scenario_identity",
            "source_assets",
            "status",
        },
        "binding",
    )
    if document["binding_schema_version"] != MAPPING_SCHEMA_VERSION:
        raise MappingValidationError("binding_schema_version_mismatch")
    if document["authority"] != "derived_mapping_only":
        raise MappingValidationError("binding_authority_mismatch")

    source_assets = document["source_assets"]
    if not isinstance(source_assets, list) or not source_assets:
        raise MappingValidationError("source_assets_missing")
    seen_assets: set[str] = set()
    conformance_text: str | None = None
    for row in source_assets:
        if not isinstance(row, dict):
            raise MappingValidationError("source_asset_invalid")
        _exact_keys(row, {"asset_id", "path", "sha256"}, "source_asset")
        asset_id = _stable_id(row["asset_id"], "source_asset_id")
        if asset_id in seen_assets:
            raise MappingValidationError(f"duplicate_source_asset:{asset_id}")
        seen_assets.add(asset_id)
        asset_path = _project_file(root, row["path"], f"source_asset_path:{asset_id}")
        if _sha256_file(asset_path) != _sha256(row["sha256"], f"source_asset_sha256:{asset_id}"):
            raise MappingValidationError(f"source_asset_sha256_mismatch:{asset_id}")
        if asset_id == "cross_object_conformance":
            conformance_text = asset_path.read_text(encoding="utf-8")
    if conformance_text is None:
        raise MappingValidationError("cross_object_conformance_source_missing")

    machine = document["machine_registries"]
    if not isinstance(machine, dict):
        raise MappingValidationError("machine_registries_invalid")
    _exact_keys(
        machine, {"intent", "lifecycle", "observation"}, "machine_registries"
    )
    registry_documents: dict[str, tuple[Path, dict[str, Any]]] = {}
    for registry_name in ("intent", "lifecycle", "observation"):
        descriptor = machine[registry_name]
        if not isinstance(descriptor, dict):
            raise MappingValidationError(f"machine_registry_invalid:{registry_name}")
        _exact_keys(descriptor, {"path", "sha256"}, "machine_registry")
        registry_path = _project_file(root, descriptor["path"], f"{registry_name}_registry_path")
        if _sha256_file(registry_path) != _sha256(
            descriptor["sha256"], f"{registry_name}_registry_sha256"
        ):
            raise MappingValidationError(f"machine_registry_sha256_mismatch:{registry_name}")
        registry_documents[registry_name] = (
            registry_path,
            _read_json(registry_path, registry_name),
        )

    (
        registry_id,
        registry_version,
        action_version,
        message_version,
        intents,
    ) = _parse_intent_registry(
        registry_documents["intent"][1], root, registry_documents["intent"][0]
    )
    lifecycles = _parse_lifecycle_registry(registry_documents["lifecycle"][1], root)
    (
        observation_registry_id,
        observation_registry_version,
        observation_contracts,
    ) = _parse_observation_registry(
        registry_documents["observation"][1],
        root,
        registry_documents["observation"][0],
    )

    contract = document["contract_carrier"]
    if not isinstance(contract, dict):
        raise MappingValidationError("contract_carrier_invalid")
    _exact_keys(
        contract,
        {"path", "sha256", "successor_required", "verdict"},
        "contract_carrier",
    )
    contract_path = _project_file(root, contract["path"], "contract_carrier_path")
    if _sha256_file(contract_path) != _sha256(contract["sha256"], "contract_carrier_sha256"):
        raise MappingValidationError("contract_carrier_sha256_mismatch")
    if _bool(contract["successor_required"], "successor_required"):
        raise MappingValidationError("successor_contract_not_permitted_in_current_mapping")
    if contract["verdict"] != (
        "V1_COMPATIBLE_VIA_EXPLICIT_INTERNAL_MAPPING_AND_CROSS_OBJECT_VALIDATION"
    ):
        raise MappingValidationError("contract_carrier_verdict_mismatch")

    scenario = document["scenario_identity"]
    if not isinstance(scenario, dict):
        raise MappingValidationError("scenario_identity_invalid")
    _exact_keys(
        scenario,
        {
            "alternative_forum_ref",
            "alternative_route_ref",
            "basis_ref",
            "immutable",
            "variant",
            "visibility",
        },
        "scenario_identity",
    )
    variant = _stable_id(scenario["variant"], "scenario_variant")
    route_ref = scenario["alternative_route_ref"]
    forum_ref = scenario["alternative_forum_ref"]
    if variant == "NO_EVIDENCED_COMPETENT_ALTERNATIVE_ROUTE":
        if route_ref is not None or forum_ref is not None:
            raise MappingValidationError("conservative_variant_has_alternative_route")
    elif variant == "BOUNDED_ALTERNATIVE_ROUTE_DISCRETION":
        _stable_id(route_ref, "alternative_route_ref")
        _stable_id(forum_ref, "alternative_forum_ref")
    else:
        raise MappingValidationError(f"unknown_scenario_variant:{variant}")
    if scenario["visibility"] != "runtime_system_only" or not _bool(
        scenario["immutable"], "scenario_immutable"
    ):
        raise MappingValidationError("scenario_identity_not_immutable_system_only")
    basis_ref = _stable_id(scenario["basis_ref"], "scenario_basis_ref")

    raw_participants = document["participants"]
    if not isinstance(raw_participants, list) or not raw_participants:
        raise MappingValidationError("participants_missing")
    participants: dict[str, ParticipantMapping] = {}
    definition_ids: set[str] = set()
    for raw_participant in raw_participants:
        if not isinstance(raw_participant, dict):
            raise MappingValidationError("participant_mapping_invalid")
        participant = _parse_participant(
            raw_participant,
            root=root,
            intents=intents,
            conformance_text=conformance_text,
        )
        if participant.participant_id in participants or participant.definition_id in definition_ids:
            raise MappingValidationError("duplicate_participant_identity")
        participants[participant.participant_id] = participant
        definition_ids.add(participant.definition_id)
    if set(participants) != {definition.actor_id for definition in intents.values()}:
        raise MappingValidationError("participant_actor_inventory_mismatch")
    if set(observation_contracts) != set(participants):
        raise MappingValidationError("observation_contract_actor_inventory_mismatch")
    for actor_id, participant in participants.items():
        if set(observation_contracts[actor_id]) != participant.observations:
            raise MappingValidationError(
                f"observation_contract_inventory_mismatch:{actor_id}"
            )
    _validate_definition_observation_domain_parity(
        root=root,
        participants=participants,
        contracts=observation_contracts,
    )

    causal_scope = document["causal_scope"]
    if not isinstance(causal_scope, dict):
        raise MappingValidationError("causal_scope_invalid")
    _exact_keys(
        causal_scope,
        {
            "external_channel_actor",
            "external_channel_policy_endogenous",
            "historical_validity_claim",
            "scope_id",
        },
        "causal_scope",
    )
    if _bool(causal_scope["external_channel_policy_endogenous"], "external_channel_policy_endogenous"):
        raise MappingValidationError("external_channel_policy_must_remain_exogenous")
    if _bool(causal_scope["historical_validity_claim"], "historical_validity_claim"):
        raise MappingValidationError("historical_validity_claim_forbidden")
    _stable_id(causal_scope["external_channel_actor"], "external_channel_actor")
    _stable_id(causal_scope["scope_id"], "causal_scope_id")

    return ExecutableDefinitionMapping(
        mapping_profile_id=_stable_id(document["mapping_profile_id"], "mapping_profile_id"),
        status=_stable_id(document["status"], "binding_status"),
        observation_registry_id=observation_registry_id,
        observation_registry_version=observation_registry_version,
        intent_registry_id=registry_id,
        intent_registry_version=registry_version,
        action_schema_version=action_version,
        message_content_schema_version=message_version,
        scenario_variant=variant,
        scenario_basis_ref=basis_ref,
        causal_scope=MappingProxyType(dict(causal_scope)),
        participants=MappingProxyType(participants),
        observation_contracts=observation_contracts,
        intents=intents,
        lifecycles=lifecycles,
    )


__all__ = [
    "ConditionalParameterRule",
    "ExecutableDefinitionMapping",
    "IntentConformanceError",
    "IntentDefinition",
    "LifecycleConformanceError",
    "LifecycleFamily",
    "LifecycleRegistry",
    "LifecycleTrack",
    "MappingValidationError",
    "ObservationConformanceError",
    "ObservationContract",
    "ParameterContract",
    "ParticipantMapping",
    "SemanticIntentProjection",
    "load_executable_mapping",
]
