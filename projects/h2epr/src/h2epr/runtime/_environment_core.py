"""Shared primitives for the event-neutral declarative environment."""

from __future__ import annotations

import copy
import hashlib
from typing import Any, Mapping

from h2epr.masim_kernel import ActionDisposition, ActionIntent, StateDelta


class _DeclarativeEnvironmentCoreError(ValueError):
    """A declared handler, intent, state field, or replay delta is invalid."""


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise _DeclarativeEnvironmentCoreError(code)


def _identifier(*parts: object) -> str:
    return hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).hexdigest()[:32]


def condition_matches(value: Any, operator: str, expected: Any) -> bool:
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
    raise _DeclarativeEnvironmentCoreError(f"condition_operator_unknown:{operator}")


def _value_valid(value: Any, declaration: Mapping[str, Any]) -> bool:
    expected_type = declaration["value_type"]
    valid = {
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "array": isinstance(value, list),
    }[expected_type]
    if not valid:
        return False
    if "allowed_values" in declaration and value not in declaration["allowed_values"]:
        return False
    if "minimum" in declaration and value < declaration["minimum"]:
        return False
    if "maximum" in declaration and value > declaration["maximum"]:
        return False
    return True


class _DeclarativeEnvironmentBase:
    def __init__(self, scenario: Mapping[str, Any]) -> None:
        mechanism = scenario["mechanism"]
        self.handlers = {
            row["intent_id"]: copy.deepcopy(row)
            for row in mechanism["intent_handlers"]
        }
        self.fields = {
            (row["entity_id"], row["field_name"]): copy.deepcopy(row)
            for row in mechanism["state_fields"]
        }

    def _reject(
        self, intent: ActionIntent, logical_tick: int, reason: str
    ) -> ActionDisposition:
        return ActionDisposition(
            disposition_id=f"ad.{_identifier(intent.intent_id, logical_tick, reason)}",
            intent_id=intent.intent_id,
            logical_tick=logical_tick,
            status="rejected",
            reason_code=reason,
            state_delta_ids=(),
        )

    def _parameter_error(
        self, handler: Mapping[str, Any], parameters: Mapping[str, Any]
    ) -> str | None:
        domains = {row["parameter"]: row for row in handler["parameter_domains"]}
        if set(parameters) != set(domains):
            return "parameter_universe_mismatch"
        for parameter, declaration in domains.items():
            if not _value_valid(parameters[parameter], declaration):
                return f"parameter_domain_violation:{parameter}"
        return None

    def _precondition_error(
        self, handler: Mapping[str, Any], prestate: Mapping[str, Any]
    ) -> str | None:
        for condition in handler["preconditions"]:
            entity = prestate["entities"].get(condition["entity_id"])
            if not isinstance(entity, Mapping) or condition["field_name"] not in entity:
                return "precondition_field_missing"
            if not condition_matches(
                entity[condition["field_name"]],
                condition["operator"],
                condition["value"],
            ):
                return "precondition_not_met"
        return None

    def _planned_effects(
        self,
        handler: Mapping[str, Any],
        parameters: Mapping[str, Any],
        working_state: Mapping[str, Any],
    ) -> list[tuple[Mapping[str, Any], Any, Any]]:
        planned: list[tuple[Mapping[str, Any], Any, Any]] = []
        for effect in handler["effects"]:
            key = effect["entity_id"], effect["field_name"]
            _require(key in self.fields, f"effect_field_unknown:{key[0]}:{key[1]}")
            before = working_state["entities"][key[0]][key[1]]
            operand = (
                parameters[effect["value_from_parameter"]]
                if "value_from_parameter" in effect
                else copy.deepcopy(effect["value"])
            )
            if effect["operation"] == "set":
                after = operand
            elif effect["operation"] == "increment":
                _require(
                    isinstance(before, int)
                    and not isinstance(before, bool)
                    and isinstance(operand, int)
                    and not isinstance(operand, bool),
                    f"increment_operand_invalid:{key[0]}:{key[1]}",
                )
                after = before + operand
            elif effect["operation"] == "append_unique":
                _require(isinstance(before, list), f"append_target_invalid:{key[0]}:{key[1]}")
                after = copy.deepcopy(before)
                if operand not in after:
                    after.append(copy.deepcopy(operand))
            else:
                raise _DeclarativeEnvironmentCoreError(
                    f"effect_operation_unknown:{effect['operation']}"
                )
            _require(
                _value_valid(after, self.fields[key]),
                f"effect_result_domain_violation:{key[0]}:{key[1]}",
            )
            planned.append((effect, before, after))
        return planned

    def apply_batch(
        self,
        state: dict[str, Any],
        intents: tuple[ActionIntent, ...],
        run_seed: int,
        logical_tick: int,
    ) -> tuple[list[ActionDisposition], list[StateDelta]]:
        del run_seed
        prestate = copy.deepcopy(state)
        dispositions: list[ActionDisposition] = []
        deltas: list[StateDelta] = []
        writes: dict[tuple[str, str], tuple[str, Any]] = {}
        for intent in intents:
            handler = self.handlers.get(intent.action_type)
            if handler is None:
                dispositions.append(self._reject(intent, logical_tick, "intent_handler_missing"))
                continue
            if intent.actor_id not in handler["eligible_actors"]:
                dispositions.append(self._reject(intent, logical_tick, "actor_not_authorized"))
                continue
            parameters = dict(intent.parameters)
            parameter_error = self._parameter_error(handler, parameters)
            if parameter_error:
                dispositions.append(self._reject(intent, logical_tick, parameter_error))
                continue
            target = parameters[handler["target_parameter"]]
            if target not in handler["eligible_targets"]:
                dispositions.append(self._reject(intent, logical_tick, "target_not_eligible"))
                continue
            precondition_error = self._precondition_error(handler, prestate)
            if precondition_error:
                dispositions.append(self._reject(intent, logical_tick, precondition_error))
                continue
            planned = self._planned_effects(handler, parameters, state)
            conflict = False
            for effect, _, after in planned:
                key = effect["entity_id"], effect["field_name"]
                prior = writes.get(key)
                if prior is None:
                    continue
                if not (
                    prior[0] == effect["operation"] == "set"
                    and prior[1] == after
                ):
                    conflict = True
                    break
            if conflict:
                dispositions.append(
                    self._reject(intent, logical_tick, "concurrent_field_conflict")
                )
                continue
            intent_deltas: list[StateDelta] = []
            for index, (effect, before, after) in enumerate(planned):
                key = effect["entity_id"], effect["field_name"]
                writes.setdefault(key, (effect["operation"], copy.deepcopy(after)))
                current = state["entities"][key[0]][key[1]]
                if current == after:
                    continue
                delta = StateDelta(
                    delta_id=f"delta.{_identifier(intent.intent_id, key[0], key[1], index)}",
                    source_intent_id=intent.intent_id,
                    entity_id=key[0],
                    field_name=key[1],
                    before=copy.deepcopy(current),
                    after=copy.deepcopy(after),
                    delta_class=effect.get("delta_class", "declared_effect"),
                )
                state["entities"][key[0]][key[1]] = copy.deepcopy(after)
                intent_deltas.append(delta)
            deltas.extend(intent_deltas)
            reason = "admitted_applied" if intent_deltas else "admitted_no_effect"
            dispositions.append(
                ActionDisposition(
                    disposition_id=f"ad.{_identifier(intent.intent_id, logical_tick, reason)}",
                    intent_id=intent.intent_id,
                    logical_tick=logical_tick,
                    status="accepted",
                    reason_code=reason,
                    state_delta_ids=tuple(row.delta_id for row in intent_deltas),
                )
            )
        return dispositions, deltas
def _apply_delta(state: dict[str, Any], delta: Mapping[str, Any]) -> None:
    entity_id = delta["entity_id"]
    field_name = delta["field_name"]
    _require(entity_id in state.get("entities", {}), f"replay_entity_missing:{entity_id}")
    _require(field_name in state["entities"][entity_id], f"replay_field_missing:{entity_id}:{field_name}")
    _require(
        state["entities"][entity_id][field_name] == delta["before"],
        f"replay_before_mismatch:{entity_id}:{field_name}",
    )
    state["entities"][entity_id][field_name] = copy.deepcopy(delta["after"])
