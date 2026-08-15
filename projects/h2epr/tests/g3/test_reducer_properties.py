from __future__ import annotations

import copy

import pytest

from masim.integrations.event_process import ActionDisposition, ActionIntent, AuthoritativeReducer, StateDelta, canonical_sha256
from h2epr.runtime.runner import H2EPRWorldReducer, RESOURCE_OWNERS
from h2epr.world import pro_rata_floor_then_seeded_remainder, transfer_balances


def _intent(state: dict, intent_id: str = "i1") -> ActionIntent:
    return ActionIntent(intent_id, "run", "actor", 1, state["state_version"], canonical_sha256(state), "set", {"after": 4}, "policy")


def _apply(state, intents, seed, tick):
    intent = intents[0]
    before = state["value"]
    state["value"] = intent.parameters["after"]
    delta = StateDelta("delta.1", intent.intent_id, "__world__", "value", before, state["value"], "synthetic")
    return [ActionDisposition("ad.1", intent.intent_id, tick, "accepted", "ok", (delta.delta_id,))], [delta]


def test_authoritative_reducer_commits_exactly_one_version() -> None:
    initial = {"state_version": 0, "value": 3}
    result = AuthoritativeReducer(initial, _apply).reduce([_intent(initial)], logical_tick=1, run_seed=0)
    assert result.state == {"state_version": 1, "value": 4}
    assert result.prestate_sha256 == canonical_sha256(initial)


def test_reducer_rejects_wrong_prestate_without_commit() -> None:
    initial = {"state_version": 0, "value": 3}
    bad = ActionIntent("i1", "run", "actor", 1, 0, "b" * 64, "set", {"after": 4}, "policy")
    reducer = AuthoritativeReducer(initial, _apply)
    with pytest.raises(ValueError, match="prestate"):
        reducer.reduce([bad], logical_tick=1, run_seed=0)
    assert reducer.state == initial


def test_seeded_pro_rata_is_order_independent_and_conserved() -> None:
    first = pro_rata_floor_then_seeded_remainder(7, {"c": 5, "a": 5, "b": 5}, run_seed=2, logical_tick=9)
    second = pro_rata_floor_then_seeded_remainder(7, {"b": 5, "c": 5, "a": 5}, run_seed=2, logical_tick=9)
    assert first == second
    assert sum(first.values()) == 7


def test_zero_claim_allocation_and_transfer_conservation() -> None:
    assert pro_rata_floor_then_seeded_remainder(10, {"a": 0}, run_seed=0, logical_tick=0) == {"a": 0}
    assert transfer_balances({"a": 10, "b": 5}, [("a", "b", 3)]) == {"a": 7, "b": 8}


def _world_state(liquid_by_owner: dict[str, int]) -> dict:
    actors = {}
    for owner in RESOURCE_OWNERS:
        liquid = liquid_by_owner.get(owner, 5000)
        actors[owner] = {
            "liquid_resource_bp": liquid,
            "confidence_index_bp": 5000,
            "withdrawal_pressure_bp": 5000,
            "coordination_readiness_bp": 5000,
            "resource_stress_bp": 10000 - liquid,
            "operational_status": "open",
        }
    return {
        "state_version": 0,
        "actors": actors,
        "withdrawal_demand_bp": 5000,
        "exposures": [
            (source, target, 1000)
            for source in RESOURCE_OWNERS
            for target in RESOURCE_OWNERS
            if source != target
        ],
    }


def _support_batch(state: dict, offers: list[tuple[str, str, int, str]]) -> tuple[ActionIntent, ...]:
    offer_by_provider = {provider: (recipient, amount, intent_id) for provider, recipient, amount, intent_id in offers}
    prestate_sha256 = canonical_sha256(state)
    intents = []
    for owner in RESOURCE_OWNERS:
        if owner in offer_by_provider:
            recipient, amount, intent_id = offer_by_provider[owner]
            action_type = "offer_or_provide_resource"
            parameters = {"recipient_id": recipient, "amount_bp": amount}
        else:
            intent_id = f"intent.noop.{owner}"
            action_type = "no_op"
            parameters = {}
        intents.append(
            ActionIntent(
                intent_id,
                "run",
                owner,
                1,
                state["state_version"],
                prestate_sha256,
                action_type,
                parameters,
                "rule",
            )
        )
    return tuple(intents)


def _apply_support(
    state: dict,
    offers: list[tuple[str, str, int, str]],
    *,
    reverse: bool = False,
) -> tuple[dict, dict[str, int]]:
    action_spaces = {
        owner: ("no_op", "offer_or_provide_resource") for owner in RESOURCE_OWNERS
    }
    working = copy.deepcopy(state)
    intents = list(_support_batch(state, offers))
    if reverse:
        intents.reverse()
    _, deltas = H2EPRWorldReducer(action_spaces).apply_batch(
        working, tuple(intents), run_seed=7, logical_tick=1
    )
    accepted = {
        intent_id: sum(
            delta.before - delta.after
            for delta in deltas
            if delta.source_intent_id == intent_id
            and delta.delta_class == "support_transfer"
            and delta.entity_id == provider
        )
        for provider, _, _, intent_id in offers
    }
    return working, accepted


def test_support_transfer_caps_exact_recipient_headroom() -> None:
    state = _world_state({"jp_morgan": 8000, "knickerbocker_trust": 9000})
    after, accepted = _apply_support(
        state,
        [("jp_morgan", "knickerbocker_trust", 2000, "intent.support.1")],
    )
    assert accepted == {"intent.support.1": 1000}
    assert after["actors"]["jp_morgan"]["liquid_resource_bp"] == 7000
    assert after["actors"]["knickerbocker_trust"]["liquid_resource_bp"] == 10000


def test_support_transfer_zero_headroom_accepts_zero() -> None:
    state = _world_state({"jp_morgan": 8000, "knickerbocker_trust": 10000})
    after, accepted = _apply_support(
        state,
        [("jp_morgan", "knickerbocker_trust", 1000, "intent.support.1")],
    )
    assert accepted == {"intent.support.1": 0}
    assert after["actors"]["jp_morgan"]["liquid_resource_bp"] == 8000
    assert after["actors"]["knickerbocker_trust"]["liquid_resource_bp"] == 10000


def test_competing_support_offers_share_recipient_headroom_deterministically() -> None:
    state = _world_state(
        {"jp_morgan": 8000, "nych": 8000, "knickerbocker_trust": 9000}
    )
    after, accepted = _apply_support(
        state,
        [
            ("jp_morgan", "knickerbocker_trust", 1000, "intent.support.1"),
            ("nych", "knickerbocker_trust", 1000, "intent.support.2"),
        ],
    )
    assert accepted == {"intent.support.1": 500, "intent.support.2": 500}
    assert after["actors"]["knickerbocker_trust"]["liquid_resource_bp"] == 10000


def test_support_transfer_conserves_total_liquid_resource() -> None:
    state = _world_state({"jp_morgan": 8000, "knickerbocker_trust": 9500})
    before_total = sum(actor["liquid_resource_bp"] for actor in state["actors"].values())
    after, accepted = _apply_support(
        state,
        [("jp_morgan", "knickerbocker_trust", 1000, "intent.support.1")],
    )
    after_total = sum(actor["liquid_resource_bp"] for actor in after["actors"].values())
    assert accepted == {"intent.support.1": 500}
    assert after_total == before_total


def test_support_allocation_is_input_order_independent() -> None:
    state = _world_state(
        {"jp_morgan": 8000, "nych": 8000, "knickerbocker_trust": 8999}
    )
    offers = [
        ("jp_morgan", "knickerbocker_trust", 1000, "intent.support.1"),
        ("nych", "knickerbocker_trust", 1000, "intent.support.2"),
    ]
    canonical_state, canonical_amounts = _apply_support(state, offers)
    reversed_state, reversed_amounts = _apply_support(state, offers, reverse=True)
    assert canonical_amounts == reversed_amounts
    assert canonical_state == reversed_state
