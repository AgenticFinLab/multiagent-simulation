from __future__ import annotations

from h2epr.runtime.policy import POLICY_ID, RulePolicyV1


OWNERS = ("jp_morgan", "knickerbocker_trust", "member_banks_cohort", "nych", "other_trusts_cohort")


def _state(liquid=5000, pressure=5000, readiness=5000):
    actors = {}
    for actor in ("depositors_cohort", *OWNERS, "nyse"):
        actors[actor] = {"liquid_resource_bp": None, "withdrawal_pressure_bp": None, "coordination_readiness_bp": None, "operational_status": "open"}
    for actor in OWNERS:
        actors[actor].update(liquid_resource_bp=liquid, withdrawal_pressure_bp=pressure, coordination_readiness_bp=readiness)
    return {"actors": actors, "withdrawal_demand_bp": 5000}


def _observation(actor, state, messages=(), prior=None):
    return {"logical_tick": 1, "prestate_version": 0, "prestate_sha256": "a" * 64, "public_state": state, "private_state": state["actors"][actor], "delivered_messages": messages, "prior_generated_state": prior or {}}


def test_depositor_emits_bounded_withdrawal() -> None:
    policy = RulePolicyV1("depositors_cohort", ("withdraw_resource", "no_op"), "run", 0)
    action, messages = policy.decide(_observation("depositors_cohort", _state()))
    assert action.action_type == "withdraw_resource"
    assert action.parameters["amount_bp"] == 500
    assert messages == ()


def test_needy_owner_requests_support_with_linked_single_recipient_message() -> None:
    state = _state(liquid=4000)
    policy = RulePolicyV1("knickerbocker_trust", ("request_support", "change_operational_status", "no_op"), "run", 0)
    action, messages = policy.decide(_observation("knickerbocker_trust", state))
    assert action.action_type == "request_support"
    assert len(messages) == 1
    assert messages[0].source_action_intent_id == action.intent_id
    assert messages[0].payload["request_intent_id"] == action.intent_id


def test_provider_offer_uses_capacity_and_request_lineage() -> None:
    state = _state(liquid=5000)
    request = {"message_intent_id": "m1", "message_kind": "support_request", "sender_id": "knickerbocker_trust", "payload": {"requested_amount_bp": 1000, "request_intent_id": "request.1"}}
    policy = RulePolicyV1("jp_morgan", ("offer_or_provide_resource", "deny_request", "no_op"), "run", 0)
    action, messages = policy.decide(_observation("jp_morgan", state, (request,)))
    assert action.action_type == "offer_or_provide_resource"
    assert action.parameters == {"recipient_id": "knickerbocker_trust", "amount_bp": 1000, "request_intent_id": "request.1"}
    assert messages[0].message_kind == "support_offer"


def test_close_precedes_restrict_and_request() -> None:
    state = _state(liquid=0, pressure=7000)
    policy = RulePolicyV1("knickerbocker_trust", ("request_support", "change_operational_status", "no_op"), "run", 0)
    action, _ = policy.decide(_observation("knickerbocker_trust", state, prior={"latest_support_failed": True}))
    assert action.action_type == "change_operational_status"
    assert action.parameters["target_status"] == "closed"
    assert action.policy_id == POLICY_ID


def test_explicit_no_op_when_no_permitted_rule_matches() -> None:
    state = _state(liquid=7000, pressure=1000)
    policy = RulePolicyV1("nyse", ("request_support", "change_operational_status", "no_op"), "run", 0)
    assert policy.decide(_observation("nyse", state))[0].action_type == "no_op"
