"""Shared implementation of the configuration-driven Rule backend."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from h2epr.benchmark.package import EventPackage
from h2epr.canonical import canonical_sha256
from h2epr.masim_kernel import ActionIntent, MessageIntent
from h2epr.runtime._environment_core import condition_matches
from h2epr.runtime.information import matching_receipts

from .interface import DecisionResult


class _RuleBackendCoreError(ValueError):
    """A Rule decision or observation violates the declared contract."""


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_ROOT = PROJECT_ROOT / "schemas"


def _identifier(*parts: object) -> str:
    return hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).hexdigest()[:32]


def _validate(value: Mapping[str, Any], schema_name: str, label: str) -> None:
    schema = json.loads((SCHEMA_ROOT / schema_name).read_text(encoding="utf-8"))
    try:
        jsonschema.Draft202012Validator(schema).validate(value)
    except jsonschema.ValidationError as exc:
        raise _RuleBackendCoreError(f"{label}_schema_invalid:{exc.json_path}") from exc


class _DeclarativeRuleBackendBase:
    backend_name = "rule"
    implementation_id = "h2epr.backend.rule.declarative.v4"

    def __init__(
        self,
        package: EventPackage,
        *,
        run_id: str,
        run_seed: int,
    ) -> None:
        self.package = package
        self.run_id = run_id
        self.run_seed = run_seed
        settings = package.backend_configuration["settings"]
        self.policy_id = settings["policy_id"]
        self.default_action = settings["default_action"]
        self.rules_by_actor: dict[str, list[dict[str, Any]]] = {}
        for row in settings["decision_rules"]:
            self.rules_by_actor.setdefault(row["actor_id"], []).append(copy.deepcopy(row))
        for rows in self.rules_by_actor.values():
            rows.sort(key=lambda row: (row["priority"], row["rule_id"]))
        self.tick_by_coordinate = {
            row["coordinate_id"]: row["logical_tick"]
            for row in package.scenario["timeline"]
        }
        self._attempts: dict[str, tuple[int, str]] = {}
        self.route_by_pair = {
            (row["source_id"], row["target_id"]): copy.deepcopy(row)
            for row in package.scenario["communication_routes"]
        }
        self._decision_projections: dict[tuple[int, str], dict[str, Any]] = {}

    async def setup(self) -> None:
        return None

    async def shutdown(self) -> None:
        return None

    def _guard_matches(
        self, guard: Mapping[str, Any], observation: Mapping[str, Any]
    ) -> bool:
        contract = observation["contract"]
        if guard["kind"] == "state":
            try:
                fields = {
                    **contract["public_state"]["entities"].get(guard["entity_id"], {}),
                    **contract["private_state"]["entities"].get(guard["entity_id"], {}),
                }
                value = fields[guard["field_name"]]
            except KeyError as exc:
                raise _RuleBackendCoreError(
                    f"rule_guard_state_missing:{guard['entity_id']}:{guard['field_name']}"
                ) from exc
            return condition_matches(value, guard["operator"], guard["value"])
        if guard["kind"] in {"message_received", "message_known"}:
            messages = (
                contract["delivered_messages"]
                if guard["kind"] == "message_received"
                else contract["memory"]["received_messages"]
            )
            return bool(matching_receipts(guard, messages, contract["logical_tick"]))
        raise _RuleBackendCoreError(f"rule_guard_kind_unknown:{guard['kind']}")

    @staticmethod
    def _information_identity(contract: Mapping[str, Any]) -> str:
        """Only visible information can reopen a denied attempt.

        A tick, global state-version bump, generated ID, or the denial itself
        is not new information about feasibility. Own results are inspected
        separately to prevent repeat submission after acceptance.
        """
        return canonical_sha256({
            "public": contract["public_state"]["entities"],
            "private": contract["private_state"]["entities"],
            "received_messages": contract["memory"]["received_messages"],
            "pending_lifecycles": contract["pending_lifecycles"],
        })

    def _eligible(self, row: Mapping[str, Any], observation: Mapping[str, Any]) -> bool:
        contract = observation["contract"]
        if "coordinate_id" in row:
            return row["coordinate_id"] == observation["runtime"]["coordinate"]["coordinate_id"]
        activation = row["activation"]
        start = self.tick_by_coordinate[activation["start_coordinate_id"]]
        end = self.tick_by_coordinate[activation["end_coordinate_id"]]
        if not start <= contract["logical_tick"] <= end:
            return False
        attempt = self._attempts.get(row["rule_id"])
        if attempt is None:
            return True
        tick, information = attempt
        result = next((item for item in contract["memory"]["own_actions"]
                       if item["logical_tick"] == tick), None)
        if result is None:
            raise _RuleBackendCoreError("rule_prior_action_result_missing")
        if result["status"] == "accepted":
            return False
        return information != self._information_identity(contract)

    def _choose_rule(
        self, actor_id: str, observation: Mapping[str, Any]
    ) -> dict[str, Any] | None:
        matches = [
            row
            for row in self.rules_by_actor.get(actor_id, [])
            if self._eligible(row, observation)
            and all(self._guard_matches(guard, observation) for guard in row["guards"])
        ]
        return copy.deepcopy(matches[0]) if matches else None

    def _decide_one(
        self, actor_id: str, observation: Mapping[str, Any]
    ) -> DecisionResult:
        contract = observation["contract"]
        runtime = observation["runtime"]
        _validate(contract, "participant-observation.schema.json", f"observation:{actor_id}")
        if contract["actor_id"] != actor_id:
            raise _RuleBackendCoreError(f"observation_actor_mismatch:{actor_id}")
        rule = self._choose_rule(actor_id, observation)
        if rule is None:
            action_type = self.default_action
            parameters = {
                "target_id": actor_id,
                "reason_code": "no_declared_rule_matched",
            }
            message_specs: list[dict[str, Any]] = []
            reason = "No applicable, uncompleted Rule row matched the available information."
            rule_id = "default.no_op"
            guard_count = 0
        else:
            action_type = rule["action"]["action_type"]
            parameters = copy.deepcopy(rule["action"]["parameters"])
            message_specs = copy.deepcopy(rule["messages"])
            reason = rule["reason"]
            rule_id = rule["rule_id"]
            guard_count = len(rule["guards"])
        if action_type not in contract["permitted_action_types"]:
            raise _RuleBackendCoreError(
                f"rule_action_not_permitted:{actor_id}:{action_type}"
            )
        logical_tick = contract["logical_tick"]
        # The readable actor prefix keeps MASim's deterministic identifier sort
        # semantically stable when the opaque run-derived suffix is perturbed.
        intent_id = (
            f"intent.{actor_id}."
            f"{_identifier(self.run_id, logical_tick, actor_id, action_type, rule_id)}"
        )
        action = ActionIntent(
            intent_id=intent_id,
            run_id=self.run_id,
            actor_id=actor_id,
            logical_tick=logical_tick,
            prestate_version=runtime["prestate_version"],
            prestate_sha256=runtime["prestate_sha256"],
            action_type=action_type,
            parameters=parameters,
            policy_id=self.policy_id,
        )
        messages: list[MessageIntent] = []
        for index, message in enumerate(message_specs):
            recipient = message["recipient_id"]
            route = self.route_by_pair.get((actor_id, recipient))
            if route is None:
                raise _RuleBackendCoreError(
                    f"rule_message_route_missing:{actor_id}:{recipient}"
                )
            messages.append(
                MessageIntent(
                    message_intent_id=(
                        f"message-intent.{actor_id}.{recipient}.{index}."
                        + _identifier(
                            intent_id,
                            recipient,
                            message["message_type"],
                            index,
                        )
                    ),
                    run_id=self.run_id,
                    source_action_intent_id=intent_id,
                    sender_id=actor_id,
                    recipient_id=recipient,
                    route_id=route["route_id"],
                    logical_tick=logical_tick,
                    latency_ticks=route["latency_ticks"],
                    message_kind=message["message_type"],
                    payload=copy.deepcopy(message["payload"]),
                )
            )
        projection = {
            "schema_version": "h2epr.participant-decision.v2",
            "actor_id": actor_id,
            "logical_tick": logical_tick,
            "backend": "rule",
            "action": {
                "action_type": action_type,
                "parameters": copy.deepcopy(parameters),
            },
            "messages": [
                {
                    "recipient_id": message.recipient_id,
                    "message_type": message.message_kind,
                    "payload": copy.deepcopy(dict(message.payload)),
                }
                for message in messages
            ],
            "decision_record": {
                "policy_id": self.policy_id,
                "rule_id": rule_id,
                "reason": reason,
                "reason_kind": "configured_policy_rationale",
                "matched_guards": copy.deepcopy(rule["guards"]) if rule else [],
                "observation_sha256": canonical_sha256(contract),
                "guard_count": guard_count,
                "deterministic": True,
            },
        }
        _validate(projection, "participant-decision.schema.json", f"decision:{actor_id}")
        self._decision_projections[(logical_tick, actor_id)] = projection
        if rule is not None and "activation" in rule:
            self._attempts[rule_id] = (logical_tick, self._information_identity(contract))
        return action, tuple(messages)

    async def decide(
        self, observations: Mapping[str, Mapping[str, object]]
    ) -> dict[str, DecisionResult]:
        if sorted(observations) != list(self.package.scenario["active_actor_ids"]):
            raise _RuleBackendCoreError("observation_actor_universe_mismatch")
        return {
            actor_id: self._decide_one(actor_id, observation)
            for actor_id, observation in sorted(observations.items())
        }

    def decision_projection(self, logical_tick: int, actor_id: str) -> dict[str, Any]:
        try:
            return copy.deepcopy(self._decision_projections[(logical_tick, actor_id)])
        except KeyError as exc:
            raise _RuleBackendCoreError(
                f"decision_projection_missing:{logical_tick}:{actor_id}"
            ) from exc
