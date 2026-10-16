"""Acceptance tests for per-source market perception.

Contract
--------
An agent's ``custom_state["market_data"]`` is a **single slot** whose value is
the last market signal processed; that is correct for one market and is kept
unchanged as a last-wins alias. Because the macro tier needs several markets in
one run, every market signal is *also* recorded per source
(``custom_state["market_data_by_source"]``), so an archetype can ask for one
specific market without the platform guessing. ``Info.sender_id`` — populated on
receive — is the source identity.

Bounds: an inbound payload without a ``price`` is not a market signal and is
ignored; an unknown source yields the caller's default.

No Ray, no filesystem.
"""

from __future__ import annotations

import asyncio
import unittest

from examples.uTests._helpers import make_rule_agent
from masim.player.base import Info, LocalObservation, Observation


def observe(agent, *signals) -> None:
    """Feed ``(sender_id, price)`` pairs to the agent's (async) perceive path."""
    inbounds = []
    for sender_id, price in signals:
        inbounds.append(
            Info(
                payload={"price": price, "prev_price": price - 1.0},
                sender_id=sender_id,
            )
        )
    asyncio.run(
        agent.perceive(
            Observation(local=LocalObservation(data={}), inbounds=inbounds, round=1)
        )
    )


class TestPerSourceMarketData(unittest.TestCase):
    """Two markets in one run must stay distinguishable to a participant."""

    def test_signals_are_recorded_against_their_sender(self) -> None:
        agent = make_rule_agent()
        observe(agent, ("market", 100.0), ("market_b", 62.0))

        self.assertEqual(agent.market_data_for("market")["price"], 100.0)
        self.assertEqual(agent.market_data_for("market_b")["price"], 62.0)
        self.assertEqual(agent.market_sources(), ["market", "market_b"])

    def test_the_single_slot_stays_a_last_wins_alias(self) -> None:
        agent = make_rule_agent()
        observe(agent, ("market", 100.0), ("market_b", 62.0))

        # Existing archetypes read this slot, so its meaning must not change.
        self.assertEqual(agent.state.custom_state["market_data"]["price"], 62.0)

    def test_a_single_market_is_indistinguishable_from_before(self) -> None:
        agent = make_rule_agent()
        observe(agent, ("market", 100.0))

        self.assertEqual(agent.state.custom_state["market_data"]["price"], 100.0)
        self.assertEqual(agent.market_sources(), ["market"])
        self.assertEqual(agent.market_data_for("market")["price"], 100.0)

    def test_an_unknown_source_returns_the_default(self) -> None:
        agent = make_rule_agent()
        observe(agent, ("market", 100.0))

        self.assertIsNone(agent.market_data_for("market_b"))
        self.assertEqual(agent.market_data_for("market_b", default={}), {})

    def test_a_payload_without_a_price_is_not_a_market_signal(self) -> None:
        agent = make_rule_agent()
        asyncio.run(
            agent.perceive(
                Observation(
                    local=LocalObservation(data={}),
                    inbounds=[
                        Info(payload={"note": "no price here"}, sender_id="chat")
                    ],
                    round=1,
                )
            )
        )

        self.assertEqual(agent.market_sources(), [])
        self.assertIsNone(agent.state.custom_state.get("market_data"))

    def test_a_later_signal_from_the_same_source_replaces_the_earlier_one(self) -> None:
        agent = make_rule_agent()
        observe(agent, ("market", 100.0))
        agent.state.custom_state.setdefault("price_history", [])
        observe(agent, ("market", 101.0))

        self.assertEqual(agent.market_data_for("market")["price"], 101.0)
        self.assertEqual(agent.market_sources(), ["market"])

    def test_a_signal_without_a_sender_is_still_recorded(self) -> None:
        """Defensive: a missing sender_id must not lose the market signal."""
        agent = make_rule_agent()
        observe(agent, (None, 100.0))

        self.assertEqual(agent.market_data_for("unknown")["price"], 100.0)
        self.assertEqual(agent.state.custom_state["market_data"]["price"], 100.0)


if __name__ == "__main__":
    unittest.main()
