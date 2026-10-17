"""Unit tests for MASim reproducibility / contract / config-wiring upgrades.

Run with:  PYTHONPATH=. python3 -m unittest discover -s tests -v
No Ray / lmbase runtime is required — these are pure unit checks.
"""

import types
import unittest
from pathlib import Path

from masim.agents._base import _apply_fill_and_emit_action, validate_archetype_extras
from agent_library.finance.anchored_trader import RuleAnchoredTrader
from agent_library.finance.noise_trader import RuleNoiseTrader
from agent_library.market.stock_standard_price_impact import MarketStockStandardPriceImpact
from masim.format.finalize import finalize_rule_order, require_positive_bid_price
from masim.format.order import InvestorOrder
from masim.format.state import StandardMarketState
from masim.utils.rng import derive_rng


class FakeAgent:
    def __init__(self, cash=10000.0, position=0.0):
        self.identity = "test_agent"
        self.state = types.SimpleNamespace(
            custom_state={"cash": cash, "position": position}
        )


class TestRng(unittest.TestCase):
    def test_deterministic_same_salt(self):
        self.assertEqual(derive_rng(42, "a").random(), derive_rng(42, "a").random())

    def test_distinct_salt_differs(self):
        self.assertNotEqual(derive_rng(42, "a").random(), derive_rng(42, "b").random())

    def test_none_seed_is_nondeterministic(self):
        self.assertNotEqual(derive_rng(None, "a").random(), derive_rng(None, "a").random())


class TestContract(unittest.TestCase):
    def test_zero_price_buy_rejected(self):
        with self.assertRaises(ValueError):
            InvestorOrder.buy(quantity=1, price=0.0, investor="x", strategy="s")

    def test_require_positive_bid_price(self):
        with self.assertRaises(ValueError):
            require_positive_bid_price(0.0, "buy", context="t")

    def test_clip_to_liquidity(self):
        state = StandardMarketState(
            round=1, price=100.0, prev_price=99.0, fundamental=100.0,
            deviation=0.0, price_change=0.01, cash=100.0, position=0.0,
            portfolio_value=100.0,
        )
        order = InvestorOrder.buy(quantity=50, price=100.0, investor="x", strategy="s")
        fin = finalize_rule_order(order, state=state, investor="x", strategy="s")
        self.assertTrue(fin.clipped)
        self.assertEqual(fin.action, "buy")
        self.assertLessEqual(fin.quantity * 100.0, 100.0 + 1e-9)

    def test_missing_bid_price_raises_keyerror(self):
        agent = FakeAgent()
        with self.assertRaises(KeyError):
            _apply_fill_and_emit_action(agent, {"action": "buy", "quantity": 1}, class_name="T")

    def test_zero_price_raises_and_leaves_state_untouched(self):
        agent = FakeAgent(cash=1000.0, position=10.0)
        before = dict(agent.state.custom_state)
        with self.assertRaises(ValueError):
            _apply_fill_and_emit_action(
                agent, {"action": "buy", "quantity": 1, "bid_price": 0.0}, class_name="T"
            )
        self.assertEqual(agent.state.custom_state, before)

    def test_buy_mutates_once_and_on_fill_receives_validated_args(self):
        agent = FakeAgent(cash=1000.0, position=0.0)
        seen = []
        agent.on_fill = lambda action, quantity, bid_price: seen.append((action, quantity, bid_price))
        _apply_fill_and_emit_action(agent, {"action": "buy", "quantity": 2, "bid_price": 10.0}, class_name="T")
        self.assertEqual(agent.state.custom_state["cash"], 980.0)
        self.assertEqual(agent.state.custom_state["position"], 2.0)
        self.assertEqual(seen, [("buy", 2.0, 10.0)])


class TestExtrasValidation(unittest.TestCase):
    SPEC = {"alpha": {"type": "float", "range": (0.0, 1.0)}}

    def test_in_range_passes(self):
        validate_archetype_extras("x", {"alpha": 0.5}, self.SPEC)

    def test_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            validate_archetype_extras("x", {"alpha": 1.5}, self.SPEC)

    def test_non_numeric_raises(self):
        with self.assertRaises(ValueError):
            validate_archetype_extras("x", {"alpha": "high"}, self.SPEC)

    def test_missing_optional_is_ignored(self):
        validate_archetype_extras("x", {}, self.SPEC)

    def test_int_type_rejects_fractional(self):
        spec = {"lookback": {"type": "int", "range": (1, None)}}
        with self.assertRaises(ValueError):
            validate_archetype_extras("x", {"lookback": 2.5}, spec)

    def test_archetype_specs_are_valid(self):
        self.assertIn("alpha", RuleAnchoredTrader.PARAM_SPECS)
        self.assertIn("trade_probability", RuleNoiseTrader.PARAM_SPECS)
        self.assertIn("noise_std", MarketStockStandardPriceImpact.PARAM_SPECS)


def _make_market(seed):
    market = MarketStockStandardPriceImpact.__new__(MarketStockStandardPriceImpact)
    market.identity = "market"
    market.state = types.SimpleNamespace(
        custom_state={
            "price": 105.0,
            "prev_price": 105.0,
            "fundamental": 100.0,
            "price_impact": 0.01,
            "mean_reversion": 0.01,
            "noise_std": 0.5,
            "price_floor": 0.01,
            "deviation": 0.0,
            "price_history": [],
            "rng": derive_rng(seed, salt="market"),
        }
    )
    return market


class TestSeededMarket(unittest.TestCase):
    def test_same_seed_same_price_path(self):
        a = _make_market(42)
        b = _make_market(42)
        for _ in range(5):
            self.assertEqual(a.advance_market([], 1)["price"], b.advance_market([], 1)["price"])

    def test_same_seed_same_price_path_with_orders(self):
        a = _make_market(42)
        b = _make_market(42)
        orders = [
            {"action": "buy", "quantity": 10.0},
            {"action": "sell", "quantity": 4.0},
            {"action": "hold", "quantity": 0.0},
        ]
        pa = [a.advance_market(orders, r)["price"] for r in range(1, 6)]
        pb = [b.advance_market(orders, r)["price"] for r in range(1, 6)]
        self.assertEqual(pa, pb)

    def test_different_seed_differs(self):
        a = _make_market(42)
        b = _make_market(7)
        self.assertNotEqual(
            [a.advance_market([], 1)["price"] for _ in range(5)],
            [b.advance_market([], 1)["price"] for _ in range(5)],
        )


def _make_noise(seed):
    t = RuleNoiseTrader.__new__(RuleNoiseTrader)
    t.identity = "noise_1"
    t.state = types.SimpleNamespace(
        custom_state={
            "trade_probability": 1.0,
            "min_order": 10.0,
            "max_order": 20.0,
            "rng": derive_rng(seed, salt="noise_1"),
        }
    )
    return t


def _state():
    return StandardMarketState(
        round=1, price=100.0, prev_price=99.0, fundamental=100.0,
        deviation=0.0, price_change=0.01, cash=10000.0, position=0.0,
        portfolio_value=10000.0,
    )


class TestSeededNoiseTrader(unittest.TestCase):
    def test_same_seed_same_decision_stream(self):
        a = _make_noise(42)
        b = _make_noise(42)
        state = _state()
        for _ in range(10):
            self.assertEqual(a.decide_order(state).to_dict(), b.decide_order(state).to_dict())


class TestConfigWiring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from masim.utils.config import load_config
        root = Path(__file__).resolve().parents[1]
        cls.variants = {}
        for variant in ("Rule", "LLM", "RuleLLM", "Rag"):
            cls.variants[variant] = load_config(
                root / "configs" / "AnchoringEffect" / variant / "simulation.yml",
                env_interpolate=False,
            )

    def _extras_for(self, cfg, class_fragment):
        for player in cfg["players"].values():
            if class_fragment in player.get("class", ""):
                return player["config"].get("extras", {})
        self.fail(f"no player class matching {class_fragment!r}")

    def test_no_legacy_scenario_domain_keys(self):
        for variant, cfg in self.variants.items():
            for player in cfg["players"].values():
                extras = player["config"].get("extras", {})
                self.assertNotIn("adjustment_factor", extras, (variant, player))
                self.assertNotIn("entry_threshold", extras, (variant, player))

    def test_anchored_trader_uses_alpha(self):
        for variant, cfg in self.variants.items():
            self.assertIn("alpha", self._extras_for(cfg, "AnchoredTrader"), variant)

    def test_rule_momentum_and_contrarian_use_threshold(self):
        for variant in ("Rule", "RuleLLM", "Rag"):
            cfg = self.variants[variant]
            self.assertIn("threshold", self._extras_for(cfg, "MomentumTrader"), variant)
            self.assertIn("threshold", self._extras_for(cfg, "ContrarianTrader"), variant)


class TestPathDerivation(unittest.TestCase):
    def test_sibling_dirs_from_record_root(self):
        from masim.simulator.general import derive_persona_output_paths
        d = derive_persona_output_paths("EXPERIMENT/AnchoringEffect/Rule/records")
        self.assertEqual(d["storage"]["record_path"], "EXPERIMENT/AnchoringEffect/Rule/records")
        self.assertEqual(d["storage"]["checkpoint_dir"], "EXPERIMENT/AnchoringEffect/Rule/checkpoints")
        self.assertEqual(d["monitoring"]["record_path"], "EXPERIMENT/AnchoringEffect/Rule/monitoring")

    def test_bare_record_root(self):
        from masim.simulator.general import derive_persona_output_paths
        d = derive_persona_output_paths("records")
        self.assertEqual(d["storage"]["record_path"], "records")
        self.assertEqual(d["storage"]["checkpoint_dir"], "./checkpoints")
        self.assertEqual(d["monitoring"]["record_path"], "./monitoring")


class TestSettingSchema(unittest.TestCase):
    def test_seed_field_accepted(self):
        from masim.simulator.config_schema import validate_simulation_config
        from masim.utils.config import load_config
        root = Path(__file__).resolve().parents[1]
        cfg = load_config(root / "configs" / "AnchoringEffect" / "Rule" / "simulation.yml", env_interpolate=False)
        cfg["setting"]["seed"] = 7
        validate_simulation_config(cfg)  # must not raise

    def test_seed_must_be_int(self):
        from pydantic import ValidationError
        from masim.simulator.config_schema import validate_simulation_config
        from masim.utils.config import load_config
        root = Path(__file__).resolve().parents[1]
        cfg = load_config(root / "configs" / "AnchoringEffect" / "Rule" / "simulation.yml", env_interpolate=False)
        cfg["setting"]["seed"] = "not-an-int"
        with self.assertRaises(ValidationError):
            validate_simulation_config(cfg)


if __name__ == "__main__":
    unittest.main()
