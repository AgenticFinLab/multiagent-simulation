"""Unit tests for the execution / settlement seam.

Contract under test
-------------------
``_apply_fill_and_emit_action`` must route every order through the agent's
:class:`~masim.platform.execution.base.FillModel` and book the resulting
:class:`~masim.platform.execution.base.Fill` through
:class:`~masim.player.portfolio.Portfolio`. The default model reproduces the
historical agent-side self-fill exactly, so existing runs are unchanged; a
scenario can replace the policy through ``extras.fill_model`` and the *same*
order then settles differently.

No Ray / lmbase required.
"""

import unittest
from types import SimpleNamespace

from masim.agents._base import _apply_fill_and_emit_action
from masim.execution.self_fill import MarketPriceFillModel, SelfFillModel
from masim.platform.execution.base import Fill, FillModel, MarketView, OrderIntent
from masim.player.portfolio import Portfolio


def make_agent(extras=None, cash=1000.0, position=0.0, price=10.0):
    """Minimal agent double carrying exactly what the fill helper needs."""
    agent = SimpleNamespace(
        identity="probe_agent",
        STRATEGY="probe",
        config=SimpleNamespace(extras=dict(extras or {})),
        state=SimpleNamespace(
            custom_state={
                "cash": cash,
                "position": position,
                "market_data": {"price": price, "prev_price": price},
                "round": 3,
            }
        ),
    )
    agent.fills_seen = []
    agent.on_fill = lambda action, quantity, price_: agent.fills_seen.append(
        (action, quantity, price_)
    )
    return agent


class TestPortfolio(unittest.TestCase):
    """The book has exactly one mutation path."""

    def test_buy_and_sell_move_cash_and_position_exactly_once(self) -> None:
        book = Portfolio({"cash": 1000.0, "position": 0.0})
        book.apply_fill(
            Fill(investor="a", action="buy", fill_quantity=10.0, fill_price=2.5)
        )
        self.assertEqual(book.cash, 975.0)
        self.assertEqual(book.position, 10.0)

        book.apply_fill(
            Fill(investor="a", action="sell", fill_quantity=4.0, fill_price=3.0)
        )
        self.assertEqual(book.cash, 987.0)
        self.assertEqual(book.position, 6.0)

    def test_zero_hold_and_rejected_fills_are_no_ops(self) -> None:
        for fill in (
            Fill(investor="a", action="buy", fill_quantity=0.0, fill_price=2.5),
            Fill(investor="a", action="hold", fill_quantity=5.0, fill_price=2.5),
            Fill(
                investor="a",
                action="buy",
                fill_quantity=5.0,
                fill_price=2.5,
                rejected=True,
                reject_reason="no_liquidity",
            ),
        ):
            book = Portfolio({"cash": 1000.0, "position": 0.0})
            book.apply_fill(fill)
            self.assertEqual(book.snapshot(), {"cash": 1000.0, "position": 0.0})

    def test_non_positive_price_for_a_real_fill_is_rejected(self) -> None:
        book = Portfolio({"cash": 1000.0, "position": 0.0})
        with self.assertRaises(ValueError):
            book.apply_fill(
                Fill(investor="a", action="buy", fill_quantity=1.0, fill_price=0.0)
            )

    def test_equity_marks_the_position(self) -> None:
        book = Portfolio({"cash": 100.0, "position": 4.0})
        self.assertEqual(book.equity(), 100.0)
        self.assertEqual(book.equity(mark_price=25.0), 200.0)


class TestFillModels(unittest.TestCase):
    """Both shipped policies satisfy the FillModel contract."""

    def test_models_are_fill_models_and_identify_themselves(self) -> None:
        self.assertIsInstance(SelfFillModel(), FillModel)
        self.assertIsInstance(MarketPriceFillModel(), FillModel)
        self.assertEqual(SelfFillModel().model_id, "self_fill")
        self.assertEqual(MarketPriceFillModel().model_id, "market_price")

    def test_one_fill_per_intent_in_order(self) -> None:
        intents = [
            OrderIntent("a", "s", "buy", 1.0, 10.0, 1),
            OrderIntent("b", "s", "hold", 0.0, 10.0, 1),
        ]
        fills = SelfFillModel().execute(intents, MarketView(round_num=1, price=10.0))
        self.assertEqual(len(fills), 2)
        self.assertEqual([f.investor for f in fills], ["a", "b"])

    def test_self_fill_uses_the_quoted_price(self) -> None:
        fill = SelfFillModel().execute(
            [OrderIntent("a", "s", "buy", 10.0, 12.0, 1)],
            MarketView(round_num=1, price=10.0),
        )[0]
        self.assertEqual(fill.fill_price, 12.0)
        self.assertEqual(fill.fill_quantity, 10.0)

    def test_market_price_fill_uses_the_market_and_applies_slippage(self) -> None:
        model = MarketPriceFillModel(slippage_bps=50.0)  # 0.5%
        buy = model.execute(
            [OrderIntent("a", "s", "buy", 10.0, 12.0, 1)],
            MarketView(round_num=1, price=100.0),
        )[0]
        sell = model.execute(
            [OrderIntent("a", "s", "sell", 10.0, 88.0, 1)],
            MarketView(round_num=1, price=100.0),
        )[0]
        self.assertAlmostEqual(buy.fill_price, 100.5, places=6)
        self.assertAlmostEqual(sell.fill_price, 99.5, places=6)

    def test_market_price_fill_without_a_price_is_rejected_not_silently_mispriced(
        self,
    ) -> None:
        fill = MarketPriceFillModel().execute(
            [OrderIntent("a", "s", "buy", 10.0, 12.0, 1)],
            MarketView(round_num=1, price=None),
        )[0]
        self.assertTrue(fill.rejected)
        self.assertEqual(fill.fill_quantity, 0.0)
        self.assertEqual(fill.reject_reason, "no_market_price")

    def test_participation_cap_limits_the_filled_quantity(self) -> None:
        model = MarketPriceFillModel(participation_cap=0.25)
        fill = model.execute(
            [OrderIntent("a", "s", "buy", 100.0, 10.0, 1)],
            MarketView(round_num=1, price=10.0, extras={"available": 40.0}),
        )[0]
        self.assertEqual(fill.fill_quantity, 10.0)
        self.assertEqual(fill.requested_quantity, 100.0)


class TestApplyFillAndEmitAction(unittest.TestCase):
    """The canonical fill path routes through the seam."""

    PAYLOAD = {"action": "buy", "quantity": 10.0, "bid_price": 12.0}

    def test_default_model_reproduces_the_historical_self_fill(self) -> None:
        agent = make_agent()
        action = _apply_fill_and_emit_action(agent, dict(self.PAYLOAD), class_name="T")
        self.assertEqual(agent.state.custom_state["cash"], 880.0)
        self.assertEqual(agent.state.custom_state["position"], 10.0)
        self.assertEqual(action.action_type, "investor_bid")
        self.assertEqual(agent.fills_seen, [("buy", 10.0, 12.0)])

    def test_extras_fill_model_changes_settlement_for_the_same_order(self) -> None:
        agent = make_agent(
            {"fill_model": "masim.execution.self_fill:MarketPriceFillModel"}
        )
        _apply_fill_and_emit_action(agent, dict(self.PAYLOAD), class_name="T")
        # Market price is 10.0, not the 12.0 the agent quoted.
        self.assertEqual(agent.fills_seen, [("buy", 10.0, 10.0)])
        self.assertEqual(agent.state.custom_state["cash"], 900.0)

    def test_extras_fill_model_accepts_an_instance(self) -> None:
        agent = make_agent({"fill_model": MarketPriceFillModel(slippage_bps=100.0)})
        _apply_fill_and_emit_action(agent, dict(self.PAYLOAD), class_name="T")
        self.assertAlmostEqual(agent.fills_seen[0][2], 10.1, places=6)

    def test_unknown_fill_model_reference_fails_loudly(self) -> None:
        agent = make_agent({"fill_model": "masim.execution.self_fill:NoSuchModel"})
        with self.assertRaises(Exception):
            _apply_fill_and_emit_action(agent, dict(self.PAYLOAD), class_name="T")

    def test_hold_does_not_move_the_book_and_reports_zero_quantity(self) -> None:
        agent = make_agent()
        _apply_fill_and_emit_action(
            agent,
            {"action": "hold", "quantity": 0.0, "bid_price": 0.0},
            class_name="T",
        )
        self.assertEqual(agent.state.custom_state["cash"], 1000.0)
        self.assertEqual(agent.state.custom_state["position"], 0.0)
        self.assertEqual(agent.fills_seen, [("hold", 0.0, 0.0)])

    def test_missing_payload_field_raises_before_any_fill(self) -> None:
        agent = make_agent()
        with self.assertRaises(KeyError):
            _apply_fill_and_emit_action(
                agent, {"action": "buy", "quantity": 1.0}, class_name="T"
            )
        self.assertEqual(agent.fills_seen, [])

    def test_zero_price_buy_is_rejected_by_the_platform(self) -> None:
        agent = make_agent()
        with self.assertRaises(ValueError):
            _apply_fill_and_emit_action(
                agent,
                {"action": "buy", "quantity": 1.0, "bid_price": 0.0},
                class_name="T",
            )
        self.assertEqual(agent.state.custom_state["cash"], 1000.0)


if __name__ == "__main__":
    unittest.main()
