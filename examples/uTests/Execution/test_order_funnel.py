"""Acceptance tests for the Execution part (the order funnel).

Every order passes ``clip → validate → emit``: ``require_positive_bid_price``
rejects non-positive BUY/SELL and allows HOLD, ``clip_order_to_liquidity``
shrinks sizes and marks ``clipped``/``clipped_from``, and ``InvestorOrder`` is
frozen and carries its provenance fields.
"""

from __future__ import annotations

import asyncio
import dataclasses
import unittest

from examples.uTests._helpers import (
    TempDirTestCase,
    make_player_config,
    make_rule_agent,
)

from masim.agents._base import CanonicalRulePlayer
from masim.format.finalize import (
    clip_order_to_liquidity,
    emit_order_envelope,
    finalize_rule_order,
    require_positive_bid_price,
)
from masim.format.order import (
    BUY,
    HOLD,
    SELL,
    InvestorOrder,
    signed_order_quantity,
    validate_order,
)
from masim.format.state import StandardMarketState


def _market_state(price: float = 10.0, cash: float = 1000.0, position: float = 0.0):
    """Build a StandardMarketState from the canonical broadcast payload."""
    return StandardMarketState.from_market_data(
        {"price": price, "prev_price": price, "round": 1},
        cash=cash,
        position=position,
    )


class _FillRecorder(CanonicalRulePlayer):
    """Probe archetype that records every ``on_fill`` invocation."""

    STRATEGY = "probe"

    def __init__(self, config):
        super().__init__(config)
        self.fills = []

    def decide_order(self, state):  # pragma: no cover - not exercised here
        return InvestorOrder.hold(price=state.price)

    def on_fill(self, action: str, quantity: float, bid_price: float) -> None:
        self.fills.append((action, quantity, bid_price))


class TestPositiveBidPriceGuard(unittest.TestCase):
    """The single fail-loud price check every emit site must call."""

    def test_positive_prices_pass_through_as_floats(self) -> None:
        self.assertEqual(require_positive_bid_price(1.5, BUY), 1.5)
        self.assertEqual(require_positive_bid_price("2.5", SELL), 2.5)
        self.assertEqual(require_positive_bid_price(7, BUY), 7.0)

    def test_non_positive_prices_are_rejected_for_buy_and_sell(self) -> None:
        for action in (BUY, SELL):
            for price in (0, 0.0, -1, -0.5):
                with self.subTest(action=action, price=price):
                    with self.assertRaises(ValueError):
                        require_positive_bid_price(price, action)

    def test_hold_accepts_zero_and_positive_but_not_negative(self) -> None:
        self.assertEqual(require_positive_bid_price(0, HOLD), 0.0)
        self.assertEqual(require_positive_bid_price(4.25, HOLD), 4.25)
        with self.assertRaises(ValueError):
            require_positive_bid_price(-0.01, HOLD)

    def test_non_numeric_and_unknown_actions_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            require_positive_bid_price("not-a-number", BUY)
        with self.assertRaises(ValueError):
            require_positive_bid_price(1.0, "rebalance")

    def test_action_matching_is_case_insensitive(self) -> None:
        self.assertEqual(require_positive_bid_price(3.0, "BUY"), 3.0)
        self.assertEqual(require_positive_bid_price(0.0, "Hold"), 0.0)


class TestClipToLiquidity(unittest.TestCase):
    """Clipping never invents size and never hides a shrunk decision."""

    def test_buy_is_shrunk_to_available_cash_and_marked_clipped(self) -> None:
        order = InvestorOrder.buy(quantity=50, price=10.0, investor="i", strategy="s")
        clipped = clip_order_to_liquidity(
            order, cash=100.0, position=0.0, bid_price=10.0
        )
        self.assertEqual(clipped.action, BUY)
        self.assertEqual(clipped.quantity, 10.0)
        self.assertTrue(clipped.clipped)
        self.assertEqual(clipped.clipped_from, BUY)
        self.assertEqual(clipped.clipped_intended_quantity, 50.0)
        self.assertEqual(clipped.clipped_reason, "insufficient_cash")

    def test_sell_is_shrunk_to_available_inventory_and_marked_clipped(self) -> None:
        order = InvestorOrder.sell(quantity=10, price=3.0, investor="i", strategy="s")
        clipped = clip_order_to_liquidity(
            order, cash=0.0, position=3.0, bid_price=3.0
        )
        self.assertEqual(clipped.action, SELL)
        self.assertEqual(clipped.quantity, 3.0)
        self.assertTrue(clipped.clipped)
        self.assertEqual(clipped.clipped_from, SELL)
        self.assertEqual(clipped.clipped_reason, "insufficient_position")

    def test_a_fully_clipped_order_becomes_a_marked_hold(self) -> None:
        order = InvestorOrder.buy(quantity=5, price=10.0, investor="i", strategy="s")
        clipped = clip_order_to_liquidity(
            order, cash=0.0, position=0.0, bid_price=10.0
        )
        self.assertEqual(clipped.action, HOLD)
        self.assertEqual(clipped.quantity, 0.0)
        self.assertTrue(clipped.clipped)
        self.assertEqual(clipped.clipped_from, BUY)
        self.assertEqual(clipped.clipped_intended_quantity, 5.0)
        # A clipped-to-zero order is still valid on the wire.
        validate_order(clipped.to_dict())

    def test_an_affordable_order_is_returned_unclipped(self) -> None:
        order = InvestorOrder.buy(quantity=3, price=10.0, investor="i", strategy="s")
        clipped = clip_order_to_liquidity(
            order, cash=1000.0, position=0.0, bid_price=10.0
        )
        self.assertEqual(clipped.quantity, 3.0)
        self.assertFalse(clipped.clipped)

    def test_hold_orders_are_never_flagged_as_clipped(self) -> None:
        order = InvestorOrder.hold(price=7.0, investor="i", strategy="s")
        clipped = clip_order_to_liquidity(
            order, cash=0.0, position=0.0, bid_price=9.0
        )
        self.assertEqual(clipped.action, HOLD)
        self.assertEqual(clipped.bid_price, 9.0)
        self.assertFalse(clipped.clipped)

    def test_clipping_returns_a_new_frozen_instance(self) -> None:
        order = InvestorOrder.buy(quantity=50, price=10.0, investor="i", strategy="s")
        clipped = clip_order_to_liquidity(
            order, cash=100.0, position=0.0, bid_price=10.0
        )
        self.assertIsNot(clipped, order)
        self.assertEqual(order.quantity, 50.0)


class TestInvestorOrderContract(unittest.TestCase):
    """``InvestorOrder`` is the frozen, format-locked decision record."""

    def test_orders_are_frozen(self) -> None:
        order = InvestorOrder.buy(quantity=1, price=2.0, investor="i", strategy="s")
        with self.assertRaises(dataclasses.FrozenInstanceError):
            order.quantity = 5

    def test_factories_reject_a_non_positive_reference_price(self) -> None:
        for factory in (InvestorOrder.buy, InvestorOrder.sell):
            with self.subTest(factory=factory.__name__):
                with self.assertRaises(ValueError):
                    factory(quantity=1, price=0.0)
        # HOLD only carries an audit reference, so zero is legitimate.
        self.assertEqual(InvestorOrder.hold(price=0.0).bid_price, 0.0)

    def test_to_dict_emits_the_required_schema_plus_provenance(self) -> None:
        order = InvestorOrder.buy(
            quantity=2, price=5.0, investor="investor_1", strategy="value-investor"
        )
        payload = order.to_dict()
        self.assertEqual(
            payload,
            {
                "action": "buy",
                "quantity": 2.0,
                "bid_price": 5.0,
                "investor": "investor_1",
                "strategy": "value-investor",
            },
        )
        validate_order(payload)

    def test_bookkeeping_flags_only_appear_when_set(self) -> None:
        order = InvestorOrder.buy(quantity=1, price=1.0, investor="i", strategy="s")
        flagged = dataclasses.replace(
            order,
            clipped=True,
            clipped_from=BUY,
            clipped_intended_quantity=9.0,
            clipped_reason="insufficient_cash",
        )
        payload = flagged.to_dict()
        self.assertTrue(payload["_clipped"])
        self.assertEqual(payload["_clipped_from"], BUY)
        self.assertEqual(payload["_clipped_intended_quantity"], 9.0)
        self.assertNotIn("_clipped", order.to_dict())

    def test_from_dict_round_trips_the_provenance_fields(self) -> None:
        original = dataclasses.replace(
            InvestorOrder.hold(price=3.0, investor="i", strategy="s"),
            skipped=True,
            skipped_reason="no_market_data",
            clipped=True,
            clipped_from=SELL,
            clipped_intended_quantity=4.0,
            clipped_reason="insufficient_position",
        )
        restored = InvestorOrder.from_dict(original.to_dict())
        self.assertTrue(restored.skipped)
        self.assertEqual(restored.skipped_reason, "no_market_data")
        self.assertTrue(restored.clipped)
        self.assertEqual(restored.clipped_from, SELL)
        self.assertEqual(restored.clipped_intended_quantity, 4.0)
        self.assertEqual(restored.clipped_reason, "insufficient_position")

    def test_from_dict_rejects_a_non_positive_buy_price(self) -> None:
        with self.assertRaises(ValueError):
            InvestorOrder.from_dict(
                {"action": BUY, "quantity": 1, "bid_price": 0, "investor": "i"}
            )

    def test_validate_order_rejects_schema_violations(self) -> None:
        with self.assertRaises(ValueError):
            validate_order({"action": "buy", "quantity": 1})
        with self.assertRaises(ValueError):
            validate_order(
                {"action": "sideways", "quantity": 1, "investor": "i", "strategy": "s"}
            )

    def test_signed_order_quantity_encodes_direction(self) -> None:
        self.assertEqual(signed_order_quantity({"action": BUY, "quantity": 3}), 3.0)
        self.assertEqual(signed_order_quantity({"action": SELL, "quantity": 3}), -3.0)
        self.assertEqual(signed_order_quantity({"action": HOLD, "quantity": 0}), 0.0)


class TestRuleFinaliser(unittest.TestCase):
    """``finalize_rule_order`` is the single Rule-path finalisation site."""

    def test_hold_orders_get_the_state_price_as_an_audit_reference(self) -> None:
        state = _market_state(price=10.0, cash=100.0, position=0.0)
        order = InvestorOrder.hold(price=0.0, investor="i", strategy="s")
        finalised = finalize_rule_order(
            order, state=state, investor="i", strategy="s"
        )
        self.assertEqual(finalised.action, HOLD)
        self.assertEqual(finalised.bid_price, 10.0)

    def test_non_positive_buy_orders_fail_loudly_instead_of_falling_back(
        self,
    ) -> None:
        state = _market_state()
        order = InvestorOrder.hold(price=0.0, investor="i", strategy="s")
        broken = dataclasses.replace(order, action=BUY, quantity=1.0, bid_price=0.0)
        with self.assertRaises(ValueError):
            finalize_rule_order(broken, state=state, investor="i", strategy="s")

    def test_buy_orders_are_clipped_against_cash(self) -> None:
        state = _market_state(price=10.0, cash=25.0, position=0.0)
        order = InvestorOrder.buy(quantity=10, price=10.0, investor="i", strategy="s")
        finalised = finalize_rule_order(
            order, state=state, investor="i", strategy="s"
        )
        self.assertEqual(finalised.quantity, 2.5)
        self.assertTrue(finalised.clipped)
        validate_order(finalised.to_dict())


class TestEmitEnvelope(unittest.TestCase):
    """``emit_order_envelope`` is the only wire-dict builder."""

    def test_envelope_carries_the_order_and_one_outbound_message(self) -> None:
        order = InvestorOrder.buy(
            quantity=1, price=10.0, investor="i", strategy="s", reasoning="r"
        )
        envelope = emit_order_envelope(order)
        self.assertEqual(envelope["action"], BUY)
        self.assertEqual(len(envelope["outbound_messages"]), 1)
        message = envelope["outbound_messages"][0]
        self.assertEqual(message["content_type"], "investor_bid")
        self.assertEqual(message["payload"]["quantity"], 1.0)

    def test_analysis_is_stripped_from_the_outbound_copy(self) -> None:
        order = InvestorOrder.from_llm_decision(
            {
                "action": BUY,
                "quantity": 1,
                "bid_price": 10.0,
                "analysis": "internal chain of thought",
                "reasoning": "public rationale",
            },
            investor="i",
            strategy="s",
        )
        envelope = emit_order_envelope(order)
        self.assertIn("analysis", envelope)
        self.assertNotIn("analysis", envelope["outbound_messages"][0]["payload"])
        self.assertEqual(
            envelope["outbound_messages"][0]["payload"]["reasoning"],
            "public rationale",
        )

    def test_agent_state_is_injected_into_both_copies(self) -> None:
        order = InvestorOrder.buy(quantity=1, price=10.0, investor="i", strategy="s")
        envelope = emit_order_envelope(
            order,
            agent_state={"cash": 5.0, "position": 1.0, "agent_type": "s"},
        )
        self.assertEqual(envelope["cash"], 5.0)
        payload = envelope["outbound_messages"][0]["payload"]
        self.assertEqual(payload["cash"], 5.0)
        self.assertEqual(payload["position"], 1.0)
        self.assertEqual(payload["agent_type"], "s")


class TestCanonicalActSemantics(unittest.TestCase):
    """The canonical ``act()`` books the fill immediately, at the bid price."""

    def test_canonical_act_books_the_fill_immediately_at_the_bid_price(self) -> None:
        """TODO(contract): the agent self-fills at its own ``bid_price``.

        ``_apply_fill_and_emit_action`` (masim/agents/_base.py:327) sets
        ``fill_price = bid_price`` and mutates cash/position inside ``act`` —
        there is no execution/settlement seam yet, so a market that would clear
        at a different price cannot influence the booking.  The platform is
        about to introduce that seam (the market decides the fill price); this
        test documents today's behaviour so the change is deliberate.
        """
        agent = make_rule_agent(identity="probe", cash=1000.0, position=0.0)
        action = asyncio.run(
            agent.act({"action": BUY, "quantity": 10, "bid_price": 2.5})
        )
        self.assertEqual(action.action_type, "investor_bid")
        self.assertEqual(action.payload["bid_price"], 2.5)
        self.assertEqual(agent.state.custom_state["cash"], 975.0)
        self.assertEqual(agent.state.custom_state["position"], 10.0)

    def test_canonical_act_books_a_sell_at_the_bid_price(self) -> None:
        agent = make_rule_agent(identity="probe", cash=0.0, position=10.0)
        asyncio.run(agent.act({"action": SELL, "quantity": 4, "bid_price": 3.0}))
        self.assertEqual(agent.state.custom_state["cash"], 12.0)
        self.assertEqual(agent.state.custom_state["position"], 6.0)

    def test_hold_orders_leave_cash_and_position_untouched(self) -> None:
        agent = make_rule_agent(identity="probe", cash=50.0, position=3.0)
        asyncio.run(agent.act({"action": HOLD, "quantity": 0, "bid_price": 0.0}))
        self.assertEqual(agent.state.custom_state["cash"], 50.0)
        self.assertEqual(agent.state.custom_state["position"], 3.0)

    def test_a_non_positive_buy_price_is_refused_at_the_fill_site(self) -> None:
        agent = make_rule_agent(identity="probe", cash=100.0, position=0.0)
        with self.assertRaises(ValueError):
            asyncio.run(agent.act({"action": BUY, "quantity": 1, "bid_price": 0.0}))
        # Nothing was booked on the rejected order.
        self.assertEqual(agent.state.custom_state["cash"], 100.0)

    def test_act_requires_action_quantity_and_bid_price(self) -> None:
        agent = make_rule_agent(identity="probe")
        for payload in (
            {"quantity": 1, "bid_price": 1.0},
            {"action": BUY, "bid_price": 1.0},
            {"action": BUY, "quantity": 1},
        ):
            with self.subTest(payload=sorted(payload)):
                with self.assertRaises(KeyError):
                    asyncio.run(agent.act(payload))

    def test_on_fill_runs_exactly_once_with_the_validated_values(self) -> None:
        agent = _FillRecorder(make_player_config("probe"))
        agent.state.custom_state["cash"] = 1000.0
        agent.state.custom_state["position"] = 0.0
        asyncio.run(agent.act({"action": BUY, "quantity": 2, "bid_price": 4.0}))
        self.assertEqual(agent.fills, [(BUY, 2.0, 4.0)])
        # The hook runs after the cash/position mutation, never before.
        self.assertEqual(agent.state.custom_state["cash"], 992.0)


class TestEnvelopeIsPipelineReady(TempDirTestCase):
    """The emitted envelope is consumed by ``prepare_pending_info`` unchanged."""

    def test_outbound_messages_become_pending_info_units(self) -> None:
        from masim.player.base import Info
        from masim.player.general import GeneralPlayer

        player = GeneralPlayer(make_player_config("probe"))
        order = InvestorOrder.buy(quantity=1, price=2.0, investor="probe", strategy="s")
        payload = emit_order_envelope(order)
        for raw in payload["outbound_messages"]:
            player.pending_info.append(Info(**raw))
        self.assertEqual(len(player.pending_info), 1)
        self.assertEqual(player.pending_info[0].content_type, "investor_bid")
        self.assertEqual(player.pending_info[0].payload["action"], BUY)
