#!/usr/bin/env python3
"""Update _make_decision methods for all scenario players.py files.

This script replaces the placeholder _make_decision methods with
scenario-specific strategy logic based on each agent's theoretical model.
"""

import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
from generate_scenarios import SCENARIOS


STRATEGY_IMPLEMENTATIONS = {
    "LTCMCollapse": {
        "ConvergenceArbitrageur": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Convergence arbitrage: bets on spread narrowing.
        
        Based on LTCM strategy of convergence trades. When spread
        widens (price deviates from fundamental), increase position
        betting on convergence. Uses high leverage.
        """
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        entry_spread = extras.get("entry_spread", 0.02)
        leverage = extras.get("leverage", 25)
        max_position = extras.get("max_position", 50000)
        
        if abs(deviation) > entry_spread:
            leveraged_cash = cash * leverage
            if deviation < 0:
                buy_qty = min(int(leveraged_cash * abs(deviation) / price), max_position) if price > 0 else 0
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(int(leveraged_cash * deviation / price), max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
        "LeverageTrader": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Leverage cycle: forced to deleverage when losses mount.
        
        Based on Geanakoplos (2010) leverage cycle theory. Initially
        uses high leverage, but when losses exceed threshold, must
        rapidly deleverage, creating fire-sale pressure.
        """
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        leverage_ratio = extras.get("leverage_ratio", 20)
        margin_call = extras.get("margin_call_threshold", 0.1)
        
        portfolio_value = cash + position * price
        equity = portfolio_value - abs(position * price) / leverage_ratio
        
        if equity < abs(position * price) * margin_call:
            delever_qty = int(abs(position) * 0.3)
            if position > 0:
                delever_qty = min(delever_qty, position)
                return {"action": "sell", "quantity": delever_qty}
            elif position < 0:
                return {"action": "buy", "quantity": delever_qty}
        elif deviation < -0.03:
            buy_qty = min(int(cash * leverage_ratio * 0.01 / price), 5000) if price > 0 else 0
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}''',
        "RiskManager": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """VaR-based risk management: cuts positions when risk exceeds limit."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        var_limit = extras.get("var_limit", 0.02)
        
        if abs(deviation) > var_limit * 3:
            cut_qty = int(abs(position) * 0.5)
            if position > 0:
                return {"action": "sell", "quantity": min(cut_qty, position)}
            elif position < 0:
                return {"action": "buy", "quantity": cut_qty}
        return {"action": "hold", "quantity": 0}''',
        "LiquidityProvider": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Market making under stress: provides liquidity but withdraws when spreads widen."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        normal_spread = extras.get("normal_spread", 0.001)
        stress_spread = extras.get("stress_spread", 0.01)
        inventory_limit = extras.get("inventory_limit", 5000)
        
        if abs(deviation) > 0.05:
            return {"action": "hold", "quantity": 0}
        
        if abs(position) < inventory_limit:
            qty = min(500, inventory_limit - abs(position))
            if deviation > 0:
                return {"action": "sell", "quantity": qty}
            else:
                return {"action": "buy", "quantity": qty}
        return {"action": "hold", "quantity": 0}''',
        "CentralBank": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Lender of last resort: provides emergency liquidity during crisis.
        
        Based on Bagehot (1873) principles: lend freely at a penalty rate
        against good collateral to solvent institutions.
        """
        extras = self.config.extras
        intervention_threshold = extras.get("intervention_threshold", 0.10)
        rescue_prob = extras.get("rescue_probability", 0.8)
        
        import random
        if deviation < -intervention_threshold and random.random() < rescue_prob:
            return {"action": "buy", "quantity": 2000}
        return {"action": "hold", "quantity": 0}''',
    },
    "DotComBubble": {
        "NewEconomyEvangelist": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """New economy narrative: ignores traditional valuation, buys growth stories."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        narrative_strength = extras.get("narrative_strength", 0.8)
        val_multiplier = extras.get("valuation_multiplier", 3.0)
        
        perceived_value = fundamental * val_multiplier
        if price < perceived_value:
            buy_qty = min(int(cash * narrative_strength / price), 2000) if price > 0 else 0
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}''',
        "IPOFlipper": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """IPO flipping: buys new issues and sells quickly for profit."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        target_return = extras.get("target_return", 0.2)
        flip_days = extras.get("flip_days", 3)
        
        if position > 0 and deviation > target_return:
            return {"action": "sell", "quantity": position}
        elif deviation < -0.02:
            buy_qty = min(500, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}''',
        "MomentumFollower": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Momentum following: rides price trends."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        entry_threshold = extras.get("entry_threshold", 0.05)
        
        if deviation > entry_threshold:
            buy_qty = min(2000, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        elif deviation < -entry_threshold:
            sell_qty = min(2000, max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
        "SkepticalValueInvestor": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Value investing with high skepticism toward growth narratives."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        max_pe = extras.get("max_pe", 30)
        
        if deviation < -0.3:
            buy_qty = min(500, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        elif deviation > 1.0:
            sell_qty = min(500, max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
        "ShortSeller": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Short selling: bets against overvalued stocks with squeeze risk."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        short_threshold = extras.get("short_threshold", 2.0)
        squeeze_tolerance = extras.get("squeeze_tolerance", 0.3)
        
        if deviation > short_threshold:
            short_qty = min(2000, int(cash / price) if price > 0 else 0)
            if short_qty > 0:
                return {"action": "sell", "quantity": short_qty}
        elif deviation > 0 and position < 0:
            if deviation < squeeze_tolerance:
                cover_qty = min(abs(position), 500)
                return {"action": "buy", "quantity": cover_qty}
        return {"action": "hold", "quantity": 0}''',
    },
    "GFC2008": {
        "MBSOriginator": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Originate-to-distribute: creates securities with lax screening."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        origination_rate = extras.get("origination_rate", 0.8)
        
        sell_qty = int(abs(position) * origination_rate)
        if sell_qty > 0 and position > 0:
            return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
        "RatingAgency": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Rating agency: overrates securities due to conflict of interest."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        overrating_bias = extras.get("overrating_bias", 0.3)
        
        perceived_fundamental = fundamental * (1 + overrating_bias)
        if price < perceived_fundamental * 0.95:
            buy_qty = min(300, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}''',
        "LeveragedInvestor": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Leveraged investor: fire sales when margin called."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        leverage = extras.get("leverage", 30)
        margin_trigger = extras.get("margin_call_trigger", 0.05)
        
        if deviation < -margin_trigger:
            fire_sale_qty = int(abs(position) * 0.5)
            if position > 0 and fire_sale_qty > 0:
                return {"action": "sell", "quantity": min(fire_sale_qty, position)}
        return {"action": "hold", "quantity": 0}''',
        "DistressedBuyer": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Distressed buyer: buys at deep discount during panic."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        discount_threshold = extras.get("discount_threshold", 0.4)
        
        if deviation < -discount_threshold:
            buy_qty = min(1000, int(cash * 0.3 / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}''',
        "Regulator": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Regulator: intervenes during systemic stress."""
        extras = self.config.extras
        intervention_threshold = extras.get("intervention_threshold", 0.15)
        rescue_prob = extras.get("rescue_probability", 0.6)
        
        import random
        if deviation < -intervention_threshold and random.random() < rescue_prob:
            return {"action": "buy", "quantity": 3000}
        return {"action": "hold", "quantity": 0}''',
    },
    "OverconfidenceBias": {
        "OverconfidentTrader": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Overconfident: overestimates signal precision, trades too much."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        precision_over = extras.get("precision_overestimate", 2.0)
        
        signal = deviation * precision_over
        if abs(signal) > 0.01:
            qty = min(800, int(abs(signal) * 5000))
            if signal > 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
        "SelfAttributor": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Self-attribution bias: attributes success to skill, increases confidence."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        attribution_bias = extras.get("attribution_bias", 0.7)
        confidence_boost = extras.get("confidence_boost", 0.3)
        
        if position > 0 and deviation > 0:
            boosted_qty = min(1000, int(800 * (1 + confidence_boost)))
            buy_qty = min(boosted_qty, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        elif deviation < -0.02:
            sell_qty = min(600, max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
        "CalibratedTrader": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Calibrated: correctly estimates signal precision."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        signal_precision = extras.get("signal_precision", 0.6)
        trade_threshold = extras.get("trade_threshold", 0.02)
        
        if abs(deviation) > trade_threshold:
            qty = min(500, int(abs(deviation) * signal_precision * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
        "ContrarianInvestor": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Contrarian: trades against overconfident moves."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        contrarian_threshold = extras.get("contrarian_threshold", 0.05)
        
        if abs(deviation) > contrarian_threshold:
            qty = min(400, int(abs(deviation) * 2000))
            if deviation > 0:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
            else:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}''',
        "NoiseTrader": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Noise trader: random uninformed trading."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        prob = extras.get("trade_probability", 0.05)
        
        import random
        if random.random() < prob:
            qty = random.randint(100, 500)
            action = "buy" if random.random() > 0.5 else "sell"
            if action == "buy":
                qty = min(qty, int(cash / price) if price > 0 else 0)
            else:
                qty = min(qty, max(position, 0))
            if qty > 0:
                return {"action": action, "quantity": qty}
        return {"action": "hold", "quantity": 0}''',
    },
    "LossAversion": {
        "LossAverseInvestor": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Loss averse: values losses 2.25x more than gains (prospect theory).
        
        Sells winners too early (deviation > sell_gain_threshold) and
        holds losers too long (reluctant to realize losses).
        """
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        loss_lambda = extras.get("loss_aversion_lambda", 2.25)
        sell_gain = extras.get("sell_gain_threshold", 0.05)
        
        entry_price = self.state.custom_state.get("entry_price", fundamental)
        pnl_pct = (price - entry_price) / entry_price if entry_price > 0 else 0
        
        if pnl_pct > sell_gain:
            sell_qty = min(max(position, 0), int(position * 0.7))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        elif pnl_pct < -sell_gain * loss_lambda:
            sell_qty = min(max(position, 0), int(position * 0.2))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
        "BreakEvenTrader": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Break-even effect: takes excessive risk to get back to break-even."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        risk_increase = extras.get("risk_increase_factor", 2.0)
        
        entry_price = self.state.custom_state.get("entry_price", fundamental)
        pnl_pct = (price - entry_price) / entry_price if entry_price > 0 else 0
        
        if pnl_pct < -0.05:
            risky_qty = min(int(abs(pnl_pct) * risk_increase * 5000), int(cash / price) if price > 0 else 0)
            if risky_qty > 0:
                return {"action": "buy", "quantity": risky_qty}
        return {"action": "hold", "quantity": 0}''',
        "RationalTrader": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Rational: makes decisions based on expected utility."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        risk_aversion = extras.get("risk_aversion", 0.5)
        
        if abs(deviation) > 0.03:
            qty = min(500, int(abs(deviation) * risk_aversion * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
        "MomentumTrader": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Momentum following."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        entry_threshold = extras.get("entry_threshold", 0.02)
        
        if abs(deviation) > entry_threshold:
            qty = min(500, int(abs(deviation) * 3000))
            if deviation > 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
        "MarketMaker": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Market making: provides liquidity."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        inventory_limit = extras.get("inventory_limit", 2000)
        
        if abs(position) < inventory_limit:
            qty = 300
            if deviation > 0:
                return {"action": "sell", "quantity": min(qty, max(position, 0))}
            else:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}''',
    },
    "HerdingInformation": {
        "CascadeFollower": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Information cascade: ignores private signal when it contradicts observed actions."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        social_weight = extras.get("social_weight", 0.7)
        cascade_trigger = extras.get("cascade_trigger", 3)
        
        cascade_count = self.state.custom_state.get("cascade_count", 0)
        if abs(deviation) > 0.03:
            cascade_count += 1
        self.state.custom_state["cascade_count"] = cascade_count
        
        if cascade_count >= cascade_trigger:
            qty = min(800, int(abs(deviation) * social_weight * 5000))
            if deviation > 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
        "ReputationHerder": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Reputation herding: follows consensus to protect reputation."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        reputation_concern = extras.get("reputation_concern", 0.8)
        
        if abs(deviation) > 0.02:
            qty = min(600, int(abs(deviation) * reputation_concern * 4000))
            if deviation > 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
        "IndependentThinker": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Independent: processes signals correctly without social bias."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        signal_precision = extras.get("signal_precision", 0.7)
        
        if abs(deviation) > 0.03:
            qty = min(500, int(abs(deviation) * signal_precision * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
        "Contrarian": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Contrarian: goes against the crowd."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        contrarian_threshold = extras.get("contrarian_threshold", 0.7)
        
        if abs(deviation) > contrarian_threshold * 0.05:
            qty = min(400, int(abs(deviation) * 2000))
            if deviation > 0:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
            else:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}''',
        "NoiseTrader": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Noise trader: random uninformed trading."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        prob = extras.get("trade_probability", 0.05)
        
        import random
        if random.random() < prob:
            qty = random.randint(100, 500)
            action = "buy" if random.random() > 0.5 else "sell"
            if action == "buy":
                qty = min(qty, int(cash / price) if price > 0 else 0)
            else:
                qty = min(qty, max(position, 0))
            if qty > 0:
                return {"action": action, "quantity": qty}
        return {"action": "hold", "quantity": 0}''',
    },
}


# Generic strategies for scenarios not explicitly defined above
GENERIC_STRATEGIES = {
    "AnchoringEffect": {
        "AnchoredTrader": "anchoring",
        "HistoricalAnchor": "anchoring_historical",
        "RationalUpdater": "rational",
        "MomentumTrader": "momentum",
        "NoiseTrader": "noise",
    },
    "MentalAccounting": {
        "MentalAccountant": "mental_accounting",
        "HouseMoneyTrader": "house_money",
        "RationalPortfolioManager": "rational_portfolio",
        "SunkCostHolder": "sunk_cost",
        "NoiseTrader": "noise",
    },
    "GameStopShortSqueeze": {
        "RetailCoordinated": "retail_coordination",
        "ShortSellerHF": "short_squeeze",
        "MarketMakerGamma": "gamma_hedging",
        "InstitutionalValue": "value_extreme",
        "MomentumRetail": "fomo",
    },
    "SVBBankRun": {
        "Depositor": "depositor",
        "SocialMediaInfluencer": "social_amplifier",
        "BankManager": "bank_manager",
        "Regulator": "regulator_sv",
        "BondTrader": "bond_trader",
    },
    "LUNACollapse": {
        "StablecoinHolder": "stablecoin_holder",
        "Arbitrageur": "luna_arbitrage",
        "DeFiLender": "defi_liquidation",
        "AnchorDepositor": "anchor_depositor",
        "ValueBuyer": "value_buyer_luna",
    },
    "Volmageddon": {
        "ShortVolTrader": "short_vol",
        "VolETNManager": "vol_etn",
        "LongVolHedger": "long_vol_hedge",
        "VolArbitrageur": "vol_arb",
        "EquityTrader": "equity_basic",
    },
    "ArchegosCollapse": {
        "ConcentratedFund": "concentrated_fund",
        "PrimeBroker1": "prime_broker_fast",
        "PrimeBroker2": "prime_broker_slow",
        "BlockTradeBuyer": "block_buyer",
        "InformationTrader": "info_trader",
    },
}

STRATEGY_TEMPLATES = {
    "anchoring": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Anchoring: insufficiently adjusts from reference price."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        anchor_weight = extras.get("anchor_weight", 0.7)
        adjustment = extras.get("adjustment_factor", 0.3)
        
        anchor = self.state.custom_state.get("anchor_price", fundamental)
        adjusted_target = anchor + (fundamental - anchor) * adjustment
        perceived_deviation = (price - adjusted_target) / adjusted_target if adjusted_target > 0 else 0
        
        if abs(perceived_deviation) > 0.03:
            qty = min(500, int(abs(perceived_deviation) * 3000))
            if perceived_deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
    "anchoring_historical": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Historical anchoring: anchors to historical average price."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        anchor_weight = extras.get("anchor_weight", 0.5)
        
        anchor = self.state.custom_state.get("historical_avg", fundamental)
        perceived_deviation = (price - anchor) / anchor * (1 - anchor_weight) if anchor > 0 else 0
        
        if abs(perceived_deviation) > 0.03:
            qty = min(400, int(abs(perceived_deviation) * 2500))
            if perceived_deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
    "rational": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Rational: Bayesian updating without bias."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        
        if abs(deviation) > 0.02:
            qty = min(500, int(abs(deviation) * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
    "momentum": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Momentum: follows price trends."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        entry_threshold = extras.get("entry_threshold", 0.02)
        
        if abs(deviation) > entry_threshold:
            qty = min(500, int(abs(deviation) * 3000))
            if deviation > 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
    "noise": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Noise trader: random uninformed trading."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        prob = extras.get("trade_probability", 0.05)
        
        import random
        if random.random() < prob:
            qty = random.randint(100, 500)
            action = "buy" if random.random() > 0.5 else "sell"
            if action == "buy":
                qty = min(qty, int(cash / price) if price > 0 else 0)
            else:
                qty = min(qty, max(position, 0))
            if qty > 0:
                return {"action": action, "quantity": qty}
        return {"action": "hold", "quantity": 0}''',
    "mental_accounting": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Mental accounting: segregates portfolio into separate accounts."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        num_accounts = extras.get("num_accounts", 3)
        loss_lambda = extras.get("loss_aversion_per_account", 2.25)
        
        per_account_position = position / num_accounts if num_accounts > 0 else position
        per_account_cash = cash / num_accounts if num_accounts > 0 else cash
        
        entry_price = self.state.custom_state.get("entry_price", fundamental)
        pnl = (price - entry_price) / entry_price if entry_price > 0 else 0
        
        if pnl > 0.05:
            sell_qty = int(per_account_position * 0.7)
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        elif pnl < -0.05 * loss_lambda:
            sell_qty = int(per_account_position * 0.2)
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
    "house_money": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """House money effect: takes more risk with recent gains."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        gain_risk = extras.get("gain_risk_multiplier", 1.5)
        loss_risk = extras.get("loss_risk_multiplier", 0.5)
        
        entry_price = self.state.custom_state.get("entry_price", fundamental)
        pnl = (price - entry_price) / entry_price if entry_price > 0 else 0
        
        if pnl > 0:
            risk_factor = gain_risk
        else:
            risk_factor = loss_risk
        
        if abs(deviation) > 0.02:
            qty = min(int(500 * risk_factor), int(cash * risk_factor / price) if price > 0 else 0)
            if qty > 0:
                return {"action": "buy", "quantity": qty}
        return {"action": "hold", "quantity": 0}''',
    "rational_portfolio": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Rational portfolio: optimizes entire portfolio."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        risk_aversion = extras.get("risk_aversion", 0.5)
        
        if abs(deviation) > 0.02:
            qty = min(500, int(abs(deviation) * risk_aversion * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
    "sunk_cost": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Sunk cost: holds losing positions due to already invested capital."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        sunk_weight = extras.get("sunk_cost_weight", 0.6)
        
        entry_price = self.state.custom_state.get("entry_price", fundamental)
        pnl = (price - entry_price) / entry_price if entry_price > 0 else 0
        
        if pnl > 0.1:
            sell_qty = int(position * 0.5)
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
    "retail_coordination": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Retail coordination: buys and holds with diamond hands."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        buy_pressure = extras.get("buy_pressure", 0.8)
        
        if cash > price * 50:
            buy_qty = min(int(cash * buy_pressure / price), 500) if price > 0 else 0
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}''',
    "short_squeeze": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Short squeeze: forced to cover at higher prices."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        cover_threshold = extras.get("cover_threshold", 0.3)
        
        if position < 0 and deviation > cover_threshold:
            cover_qty = min(abs(position), int(abs(position) * 0.5))
            if cover_qty > 0:
                return {"action": "buy", "quantity": cover_qty}
        return {"action": "hold", "quantity": 0}''',
    "gamma_hedging": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Gamma hedging: delta-hedges options exposure."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        gamma = extras.get("gamma_exposure", 0.3)
        
        hedge_qty = int(abs(deviation) * gamma * 5000)
        if deviation > 0:
            buy_qty = min(hedge_qty, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}''',
    "value_extreme": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Institutional value: sells when extremely overvalued."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        sell_threshold = extras.get("sell_threshold", 3.0)
        
        if deviation > sell_threshold:
            sell_qty = min(1000, max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
    "fomo": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """FOMO trading: buys on fear of missing out."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        fomo_threshold = extras.get("fomo_threshold", 0.1)
        
        if deviation > fomo_threshold:
            buy_qty = min(50, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}''',
    "depositor": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Depositor: decides whether to withdraw based on bank health."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        withdrawal_threshold = extras.get("withdrawal_threshold", 0.1)
        social_influence = extras.get("social_influence", 0.6)
        
        if deviation < -withdrawal_threshold:
            sell_qty = min(1000, max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
    "social_amplifier": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Social media amplifier: amplifies panic signals."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        amplification = extras.get("amplification_factor", 3.0)
        
        if deviation < -0.05:
            sell_qty = min(int(abs(deviation) * amplification * 2000), max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
    "bank_manager": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Bank manager: manages asset-liability duration mismatch."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        duration_gap = extras.get("duration_gap", 6.0)
        
        if deviation < -0.05:
            buy_qty = min(500, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}''',
    "regulator_sv": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Regulator: may intervene with guarantees."""
        extras = self.config.extras
        intervention_threshold = extras.get("intervention_threshold", 0.3)
        guarantee_prob = extras.get("guarantee_probability", 0.7)
        
        import random
        if deviation < -intervention_threshold and random.random() < guarantee_prob:
            return {"action": "buy", "quantity": 2000}
        return {"action": "hold", "quantity": 0}''',
    "bond_trader": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Bond trader: trades based on interest rate expectations."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        
        if abs(deviation) > 0.03:
            qty = min(500, int(abs(deviation) * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}''',
    "stablecoin_holder": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Stablecoin holder: redeems when confidence drops."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        redemption_threshold = extras.get("redemption_threshold", 0.98)
        
        if deviation < -(1 - redemption_threshold):
            sell_qty = min(int(abs(position) * 0.5), max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
    "luna_arbitrage": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """LUNA arbitrage: amplifies death spiral via arbitrage."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        arb_threshold = extras.get("arb_threshold", 0.01)
        
        if abs(deviation) > arb_threshold:
            qty = min(5000, int(abs(deviation) * 100000))
            if deviation > 0:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
            else:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}''',
    "defi_liquidation": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """DeFi liquidation cascade: forced selling."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        liq_threshold = extras.get("liquidation_threshold", 0.8)
        
        if deviation < -(1 - liq_threshold):
            sell_qty = min(int(abs(position) * 0.6), max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
    "anchor_depositor": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Anchor depositor: exits yield protocol when confidence drops."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        yield_threshold = extras.get("yield_threshold", 0.15)
        
        if deviation < -0.05:
            sell_qty = min(int(position * 0.4), max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
    "value_buyer_luna": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Value buyer: attempts to buy at deep discount but gets overwhelmed."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        discount_threshold = extras.get("discount_threshold", 0.5)
        
        if deviation < -discount_threshold:
            buy_qty = min(1000, int(cash * 0.2 / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}''',
    "short_vol": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Short volatility: profits from contango, faces tail risk."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        stop_loss = extras.get("stop_loss", 0.5)
        
        if deviation > stop_loss:
            buy_qty = min(abs(position), int(abs(position) * 0.8))
            if buy_qty > 0 and position < 0:
                return {"action": "buy", "quantity": buy_qty}
        elif deviation < -0.02:
            sell_qty = min(1000, int(cash / price) if price > 0 else 0)
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
    "vol_etn": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Inverse VIX ETN: must buy VIX futures when VIX rises (positive feedback)."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        rebalance_threshold = extras.get("rebalance_threshold", 0.05)
        rebalance_size = extras.get("rebalance_size", 50000)
        
        if deviation > rebalance_threshold:
            buy_qty = min(int(deviation * rebalance_size), int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}''',
    "long_vol_hedge": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Long vol hedge: holds VIX for portfolio insurance."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        hedge_ratio = extras.get("hedge_ratio", 0.1)
        
        if deviation < -0.05:
            buy_qty = min(500, int(cash * hedge_ratio / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        elif deviation > 0.1:
            sell_qty = min(500, max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
    "vol_arb": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """VIX term structure arbitrage."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        entry_threshold = extras.get("entry_threshold", 0.02)
        
        if abs(deviation) > entry_threshold:
            qty = min(5000, int(abs(deviation) * 20000))
            if deviation > 0:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
            else:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}''',
    "equity_basic": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Basic equity trading."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        risk_limit = extras.get("risk_limit", 0.02)
        
        if abs(deviation) > risk_limit * 2:
            qty = min(1000, int(abs(deviation) * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
    "concentrated_fund": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Concentrated leveraged fund: holds large positions via swaps."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        leverage = extras.get("leverage", 5.0)
        concentration = extras.get("concentration", 0.3)
        
        leveraged_cash = cash * leverage
        if deviation < -0.05:
            return {"action": "hold", "quantity": 0}
        elif deviation > 0.02:
            buy_qty = min(int(leveraged_cash * concentration / price), 10000) if price > 0 else 0
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}''',
    "prime_broker_fast": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Prime broker: first to liquidate gains advantage."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        threshold = extras.get("threshold", 0.1)
        
        if deviation < -threshold:
            sell_qty = min(50000, max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
    "prime_broker_slow": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Prime broker: second to liquidate faces worse prices."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        threshold = extras.get("threshold", 0.1)
        
        if deviation < -threshold * 1.5:
            sell_qty = min(30000, max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
    "block_buyer": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Block trade buyer: buys large blocks at discount."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        discount_threshold = extras.get("discount_threshold", 0.1)
        
        if deviation < -discount_threshold:
            buy_qty = min(50000, int(cash * 0.3 / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}''',
    "info_trader": '''    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Information trader: detects liquidation and trades ahead."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        detection = extras.get("detection_ability", 0.5)
        
        if deviation < -0.05 and detection > 0.3:
            sell_qty = min(1000, max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}''',
}


def update_scenario_strategies(name: str, info: dict) -> bool:
    """Update _make_decision methods in a scenario's Rule/players.py."""
    filepath = f"{BASE_DIR}/examples/{name}/Rule/players.py"

    if not os.path.exists(filepath):
        print(f"  SKIP: {filepath} not found")
        return False

    with open(filepath, "r") as f:
        content = f.read()

    # Check if already implemented (not placeholder)
    if "# Strategy-specific logic should be implemented here" not in content:
        print(f"  SKIP: {name} already has strategy implementations")
        return False

    agents = info["agents"]
    updated = False

    # First check explicit implementations
    explicit = STRATEGY_IMPLEMENTATIONS.get(name, {})

    # Then check generic mappings
    generic = GENERIC_STRATEGIES.get(name, {})

    for agent_name in agents:
        # Find the _make_decision method for this agent
        pattern = rf'(class {agent_name}.*?def _make_decision\(self.*?\) -> dict:)\s*"""Implement {agent_name} strategy logic\.""".*?return {{"action": action, "quantity": quantity}}'

        replacement = None

        if agent_name in explicit:
            replacement = explicit[agent_name]
        elif agent_name in generic:
            template_name = generic[agent_name]
            if template_name in STRATEGY_TEMPLATES:
                replacement = STRATEGY_TEMPLATES[template_name]

        if replacement:
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            if new_content != content:
                content = new_content
                updated = True
            else:
                print(f"  WARN: Could not match pattern for {agent_name} in {name}")

    if updated:
        with open(filepath, "w") as f:
            f.write(content)
        print(f"  UPDATED: {name}")
    else:
        print(f"  NO CHANGE: {name}")

    return updated


def main():
    """Update all scenario strategies."""
    print("=" * 70)
    print("Strategy Logic Updater")
    print("=" * 70)

    updated_count = 0
    for name, info in SCENARIOS.items():
        print(f"\nProcessing: {name}")
        if update_scenario_strategies(name, info):
            updated_count += 1

    print("\n" + "=" * 70)
    print(f"Updated {updated_count}/{len(SCENARIOS)} scenarios")
    print("=" * 70)


if __name__ == "__main__":
    main()
