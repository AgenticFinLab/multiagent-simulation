"""Fixed, deterministic Rule policy used only by the architecture canary."""

from __future__ import annotations

import hashlib
from typing import Any, Mapping

from masim.integrations.event_process import ActionIntent, MessageIntent


POLICY_ID = "h2epr.0288.rule.runtime.policy.v1"
PROVIDERS = ("jp_morgan", "member_banks_cohort", "nych")
RESOURCE_OWNERS = (
    "jp_morgan",
    "knickerbocker_trust",
    "member_banks_cohort",
    "nych",
    "other_trusts_cohort",
)
PRECEDENCE = {
    "change_operational_status.closed": 0,
    "change_operational_status.restricted": 1,
    "offer_or_provide_resource": 2,
    "deny_request": 2,
    "request_support": 3,
    "coordinate_collective_action": 4,
    "withdraw_resource": 5,
    "no_op": 6,
}


def _rank(*parts: object) -> str:
    return hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).hexdigest()


def _intent_id(run_id: str, tick: int, actor_id: str, action_type: str) -> str:
    return f"intent.{_rank(run_id, tick, actor_id, action_type)[:32]}"


class RulePolicyV1:
    def __init__(self, actor_id: str, allowed_actions: tuple[str, ...], run_id: str, run_seed: int) -> None:
        self.actor_id = actor_id
        self.allowed_actions = set(allowed_actions)
        self.run_id = run_id
        self.run_seed = run_seed

    def decide(self, observation: Mapping[str, Any]) -> tuple[ActionIntent, tuple[MessageIntent, ...]]:
        tick = observation["logical_tick"]
        state = observation["public_state"]
        actors = state["actors"]
        own = actors[self.actor_id]
        delivered = sorted(observation["delivered_messages"], key=lambda item: item["message_intent_id"])
        unresolved = set(observation["prior_generated_state"].get("unresolved_request_actor_ids", []))
        candidates: list[tuple[str, dict[str, Any], list[tuple[str, str, dict[str, Any]]]]] = []

        if self.actor_id in RESOURCE_OWNERS and own["liquid_resource_bp"] == 0 and observation["prior_generated_state"].get("latest_support_failed", False):
            candidates.append(("change_operational_status", {"target_status": "closed"}, []))
        if self.actor_id in RESOURCE_OWNERS and own["liquid_resource_bp"] <= 2500 and own["operational_status"] not in {"restricted", "closed"}:
            candidates.append(("change_operational_status", {"target_status": "restricted"}, []))

        requests = [item for item in delivered if item["message_kind"] == "support_request"]
        if self.actor_id in PROVIDERS and requests:
            request = requests[0]
            amount = min(
                request["payload"]["requested_amount_bp"],
                1000,
                max(0, own["liquid_resource_bp"] - 3000),
            )
            if own["coordination_readiness_bp"] >= 4000 and amount > 0:
                action_type = "offer_or_provide_resource"
                params = {
                    "recipient_id": request["sender_id"],
                    "amount_bp": amount,
                    "request_intent_id": request["payload"]["request_intent_id"],
                }
                response_kind = "support_offer"
            else:
                action_type = "deny_request"
                params = {
                    "request_intent_id": request["payload"]["request_intent_id"],
                    "reason_code": "capacity_or_readiness_unmet",
                }
                response_kind = "support_denial"
            candidates.append((action_type, params, [(request["sender_id"], response_kind, {**params, "request_intent_id": request["payload"]["request_intent_id"]})]))

        needy = self.actor_id in RESOURCE_OWNERS and (own["liquid_resource_bp"] <= 4000 or own["withdrawal_pressure_bp"] >= 6000)
        if needy and self.actor_id not in unresolved and "request_support" in self.allowed_actions:
            eligible = [pid for pid in PROVIDERS if pid != self.actor_id and actors[pid]["operational_status"] != "closed"]
            if eligible:
                provider = min(
                    eligible,
                    key=lambda pid: (-actors[pid]["coordination_readiness_bp"], _rank(self.run_seed, "support_provider", tick, self.actor_id, pid)),
                )
                params = {"recipient_id": provider, "amount_bp": 1000}
                candidates.append(("request_support", params, [(provider, "support_request", {"requested_amount_bp": 1000})]))

        stressed = [pid for pid in RESOURCE_OWNERS if actors[pid]["liquid_resource_bp"] <= 2500 and actors[pid]["operational_status"] != "closed"]
        if self.actor_id == "nych" and len(stressed) >= 2 and not observation["prior_generated_state"].get("coordination_emitted", False):
            recipients = [pid for pid in PROVIDERS if pid != self.actor_id]
            candidates.append(("coordinate_collective_action", {"participant_ids": sorted(recipients), "coordination_kind": "liquidity_support"}, [(pid, "coordination", {"stressed_actor_ids": sorted(stressed)}) for pid in recipients]))

        if self.actor_id == "depositors_cohort" and state["withdrawal_demand_bp"] > 0:
            eligible = [pid for pid in RESOURCE_OWNERS if actors[pid]["operational_status"] in {"open", "restricted"} and actors[pid]["liquid_resource_bp"] > 0]
            if eligible:
                target = min(
                    eligible,
                    key=lambda pid: (-actors[pid]["withdrawal_pressure_bp"], _rank(self.run_seed, "withdrawal_target", tick, pid)),
                )
                candidates.append(("withdraw_resource", {"resource_owner_id": target, "amount_bp": min(500, state["withdrawal_demand_bp"])}, []))

        filtered = [item for item in candidates if item[0] in self.allowed_actions]
        if filtered:
            action_type, parameters, outbound = min(filtered, key=lambda item: (self._precedence(item[0], item[1]), item[0]))
        else:
            action_type, parameters, outbound = "no_op", {"reason_code": "no_higher_precedence_rule_matched"}, []
        intent_id = _intent_id(self.run_id, tick, self.actor_id, action_type)
        action = ActionIntent(
            intent_id,
            self.run_id,
            self.actor_id,
            tick,
            observation["prestate_version"],
            observation["prestate_sha256"],
            action_type,
            parameters,
            POLICY_ID,
        )
        messages = []
        for index, (recipient, kind, payload) in enumerate(sorted(outbound, key=lambda item: item[0])):
            full_payload = dict(payload)
            if kind == "support_request":
                full_payload["request_intent_id"] = intent_id
            message_id = f"message-intent.{_rank(intent_id, recipient, kind, index)[:32]}"
            messages.append(
                MessageIntent(
                    message_id,
                    self.run_id,
                    intent_id,
                    self.actor_id,
                    recipient,
                    f"route.{self.actor_id}.{recipient}",
                    tick,
                    1,
                    kind,
                    full_payload,
                )
            )
        return action, tuple(messages)

    @staticmethod
    def _precedence(action_type: str, parameters: Mapping[str, Any]) -> int:
        if action_type == "change_operational_status":
            return PRECEDENCE[f"{action_type}.{parameters['target_status']}"]
        return PRECEDENCE[action_type]
