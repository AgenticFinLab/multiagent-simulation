"""DispositionEffect - Prospect Theory Trading Simulation Players

Phenomenon: Disposition Effect (Shefrin & Statman 1985)
    - Investors sell winners too early (realize gains prematurely)
    - Investors hold losers too long (reluctant to realize losses)

Theoretical Foundation:
    - Prospect Theory (Kahneman & Tversky 1979)
    - Loss Aversion: λ ≈ 2.25 (losses hurt 2.25x more than gains feel good)
    - Reference Point: Purchase price as psychological anchor
    - S-shaped value function: Concave for gains, convex for losses

Investor Types:
    - DispositionInvestor: Exhibits disposition effect (behavioral)
    - RationalInvestor: Expected utility maximizer (rational baseline)
    - TaxAwareInvestor: Considers tax implications (sells losers for tax loss)
    - IndexHolder: Passive buy-and-hold
    - InstitutionalInvestor: Professional, less prone to disposition

All parameters are configured via players.yml config file.
"""

import os
import random
import logging
from typing import Any, Dict, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("DispositionEffect")


# =============================================================================
# Market - Coordinator
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market with standard price dynamics.

    Parameters from config extras:
        - initial_price, fundamental_value
        - price_impact, mean_reversion, noise_std
        - news_probability, news_impact_range
        - custom_state_hot_limit, record_path
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["price"] = extras["initial_price"]
            custom_state_hot_limit = extras["custom_state_hot_limit"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
            )

        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                order = inb.payload
                orders.append(
                    {
                        "investor": inb.sender_id,
                        "price": order["bid_price"],
                        "quantity": order["quantity"],
                        "strategy": order["strategy"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        orders = self.state.custom_state["orders"]

        # Random news shock
        news_probability = extras["news_probability"]
        news_impact_range = extras["news_impact_range"]
        news_shock = 0.0
        if random.random() < news_probability:
            news_shock = random.uniform(-news_impact_range, news_impact_range)

        # Aggregate orders
        total_buy_qty = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell_qty = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        # Price dynamics
        price_impact_rate = extras["price_impact"]
        mean_reversion_rate = extras["mean_reversion"]
        fundamental_value = extras["fundamental_value"]
        noise_std = extras["noise_std"]
        minimum_price = extras["minimum_price"]

        price_impact = price_impact_rate * net_demand
        mean_reversion = mean_reversion_rate * (fundamental_value - current_price)
        noise = random.gauss(0, noise_std)

        new_price = max(
            minimum_price,
            current_price + price_impact + mean_reversion + noise + news_shock,
        )
        price_return = (new_price - current_price) / current_price

        # Update
        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)

        logger.debug(
            "\n%s\n[Market] Round %d\n  Price: %.2f → %.2f (%+.2f%%)%s\n  Net Demand: %+.2f, Volume: %.2f%s",
            "=" * 70,
            round_num,
            current_price,
            new_price,
            price_return * 100,
            f"\n  NEWS SHOCK: {news_shock:+.2f}" if news_shock != 0 else "",
            net_demand,
            total_volume,
            (
                ("\n  Orders (%d):\n" % len(orders))
                + "\n".join(
                    f"    {o['investor']:24s} [{o['strategy']:20s}]: Q={o['quantity']:+8.2f}"
                    for o in orders
                )
                if orders
                else ""
            ),
        )

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "volume": total_volume,
            "net_demand": net_demand,
            "news_shock": news_shock,
            "round": round_num,
        }

        return {
            "market_data": market_data,
            "outbound_messages": [
                {"payload": market_data, "content_type": "market_price"}
            ],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="market_broadcast",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# Base Investor with Reference Point Tracking
# =============================================================================


class BaseInvestor(GeneralPlayer):
    """
    Base class with purchase price (reference point) tracking.

    Parameters from config extras:
        - initial_cash, initial_position, initial_purchase_price, custom_state_hot_limit
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            initial_cash = extras["initial_cash"]
            initial_position = extras["initial_position"]
            initial_purchase_price = extras["initial_purchase_price"]

            self.state.custom_state["cash"] = initial_cash
            self.state.custom_state["position"] = initial_position
            self.state.custom_state["purchase_price"] = initial_purchase_price
            self.state.custom_state["total_cost"] = (
                initial_position * initial_purchase_price
            )

        market_data = None
        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                break
        self.state.custom_state["market_data"] = market_data

    def update_reference_point(
        self, quantity: float, price: float, move_reference: bool = True
    ):
        """Update position and cost basis after trade.

        Args:
            quantity: positive=buy, negative=sell
            price: execution price
            move_reference: if True, recalculate purchase_price (average cost).
                            Set False for DispositionInvestor buys to preserve
                            the original purchase price as behavioral anchor.
        """
        position = self.state.custom_state["position"]
        total_cost = self.state.custom_state["total_cost"]

        # Buy: add to position and optionally update reference price
        if quantity > 0:
            new_cost = quantity * price
            total_cost += new_cost
            position += quantity
            if move_reference and position > 0:
                self.state.custom_state["purchase_price"] = total_cost / position
        # Sell: remove shares at average cost; reference point stays at original anchor
        elif quantity < 0:
            if position > 0:
                cost_per_share = total_cost / position
                total_cost -= abs(quantity) * cost_per_share
            position += quantity
            # After selling, reference point stays at original anchor

        self.state.custom_state["position"] = position
        self.state.custom_state["total_cost"] = max(0, total_cost)

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )

    def _hold_order(self, round_num: int, strategy_name: str) -> Dict[str, Any]:
        """Emit the explicit no-signal action required before the first broadcast."""
        logger.debug(
            "[%s] R%d (%s): Q=   +0.00 [NO MARKET DATA]",
            self.config.identity,
            round_num,
            strategy_name,
        )
        return {
            "bid_price": 0.0,
            "quantity": 0.0,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": 0.0,
                        "quantity": 0.0,
                        "strategy": strategy_name,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


# =============================================================================
# DispositionInvestor - Exhibits Disposition Effect
# =============================================================================


class DispositionInvestor(BaseInvestor):
    """
    Disposition Effect Investor (Prospect Theory).

    Behavior:
        - Sells winners quickly (gain_threshold ~10%)
        - Holds losers stubbornly (loss_threshold ~30%)

    Parameters from config extras:
        - gain_threshold, loss_threshold, loss_aversion
        - sell_fraction_gain, sell_fraction_loss
        - reference_buy_band, cash_deployment_fraction, minimum_trade_quantity

    Theory: simulation-bases.md §4.1 — DispositionInvestor
    Theoretical basis: Kahneman & Tversky (1979) Prospect Theory; asymmetric gain/loss treatment with λ = 2.25.
    See simulation-bases.md §4.1 for mathematical model.
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        purchase_price = self.state.custom_state["purchase_price"]
        market_data = self.state.custom_state["market_data"]

        strategy_name = self.__class__.__name__

        if market_data is None:
            return self._hold_order(round_num, strategy_name)

        price = market_data["price"]
        if price <= 0 or purchase_price <= 0:
            raise ValueError("price and purchase_price must be positive")

        # Calculate gain/loss relative to reference point
        gain_loss = (price - purchase_price) / purchase_price

        gain_threshold = extras["gain_threshold"]
        loss_threshold = extras["loss_threshold"]
        sell_fraction_gain = extras["sell_fraction_gain"]
        sell_fraction_loss = extras["sell_fraction_loss"]
        loss_aversion = extras["loss_aversion"]

        max_position = extras["max_position"]
        buy_fraction = extras["buy_fraction"]
        reference_buy_band = extras["reference_buy_band"]
        cash_deployment_fraction = extras["cash_deployment_fraction"]
        minimum_trade_quantity = extras["minimum_trade_quantity"]
        if loss_aversion <= 1.0:
            raise ValueError("loss_aversion must be greater than 1")
        if sell_fraction_gain <= loss_aversion * sell_fraction_loss:
            raise ValueError(
                "sell fractions must preserve the configured loss-aversion asymmetry"
            )

        quantity = 0.0
        action = "HOLD"

        # Disposition effect logic
        if gain_loss >= gain_threshold and position > 0:
            # SELL WINNERS quickly (realize gains) — concave value function in gain domain
            quantity = -position * sell_fraction_gain
            action = "SELL_WINNER"
        elif gain_loss <= loss_threshold and position > 0:
            # Reluctantly sell losers — only at extreme loss (convex value function)
            quantity = -position * sell_fraction_loss
            action = "SELL_LOSER"
        elif abs(gain_loss) < reference_buy_band and position < max_position:
            # Buy only inside the configured reference-point band.
            # Odean: investors add to positions at perceived "fair value"
            # gain_threshold excluded — any rise toward threshold is sell territory
            target_qty = (max_position - position) * buy_fraction
            affordable = cash * cash_deployment_fraction / price
            quantity = min(target_qty, affordable)
            if quantity >= minimum_trade_quantity:
                action = "BUY"
            else:
                quantity = 0.0

        # Execute trade
        if quantity > 0:
            cost = quantity * price
            if cost <= cash:
                self.state.custom_state["cash"] -= cost
                # move_reference=False: preserve original purchase price as behavioral anchor
                self.update_reference_point(quantity, price, move_reference=False)
            else:
                quantity = 0
        elif quantity < 0:
            if abs(quantity) <= position:
                proceeds = abs(quantity) * price
                self.state.custom_state["cash"] += proceeds
                self.update_reference_point(quantity, price)
            else:
                quantity = 0

        logger.debug(
            "[%s] R%d (%s): Q=%+8.2f [%s] g/l=%+.1f%% | Cash=%10.2f, Pos=%+8.2f",
            self.config.identity,
            round_num,
            strategy_name,
            quantity,
            action,
            gain_loss * 100,
            self.state.custom_state["cash"],
            self.state.custom_state["position"],
        )
        return {
            "bid_price": price,
            "quantity": quantity,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }

# =============================================================================
# RationalInvestor - Expected Utility Maximizer
# =============================================================================


class RationalInvestor(BaseInvestor):
    """
    Rational Investor (Baseline).

    Makes decisions based on expected future returns,
    NOT affected by sunk costs or reference points.

    Parameters from config extras:
        - target_allocation, rebalance_threshold, rebalance_speed

    Theory: simulation-bases.md §4.2 — RationalInvestor
    Theoretical basis: Expected Utility Theory (von Neumann & Morgenstern, 1944); ignores purchase price.
    See simulation-bases.md §4.2 for mathematical model.
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        market_data = self.state.custom_state["market_data"]

        strategy_name = self.__class__.__name__

        if market_data is None:
            return self._hold_order(round_num, strategy_name)

        price = market_data["price"]
        if price <= 0:
            raise ValueError("market price must be positive")

        target_allocation = extras["target_allocation"]
        rebalance_threshold = extras["rebalance_threshold"]
        rebalance_speed = extras["rebalance_speed"]

        # Calculate current allocation
        equity_value = position * price
        total_value = cash + equity_value
        if total_value <= 0:
            raise ValueError("total portfolio value must be positive")
        current_alloc = equity_value / total_value

        deviation = current_alloc - target_allocation
        quantity = 0.0

        # Rebalance regardless of gain/loss
        if abs(deviation) > rebalance_threshold:
            target_equity = total_value * target_allocation
            target_position = target_equity / price
            quantity = (target_position - position) * rebalance_speed

        # Execute
        if quantity > 0:
            cost = quantity * price
            if cost <= cash:
                self.state.custom_state["cash"] -= cost
                self.update_reference_point(quantity, price)
            else:
                quantity = 0
        elif quantity < 0:
            if abs(quantity) <= position:
                proceeds = abs(quantity) * price
                self.state.custom_state["cash"] += proceeds
                self.update_reference_point(quantity, price)
            else:
                quantity = 0

        logger.debug(
            "[%s] R%d (%s): Q=%+8.2f alloc=%.1f%% | Cash=%10.2f, Pos=%+8.2f",
            self.config.identity,
            round_num,
            strategy_name,
            quantity,
            current_alloc * 100,
            self.state.custom_state["cash"],
            self.state.custom_state["position"],
        )

        return {
            "bid_price": price,
            "quantity": quantity,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }

# =============================================================================
# TaxAwareInvestor - Tax Loss Harvesting
# =============================================================================


class TaxAwareInvestor(BaseInvestor):
    """
    Tax-Aware Investor.

    Opposite of disposition effect for tax optimization:
    - Sells losers to harvest tax losses
    - Holds winners to defer capital gains tax

    Parameters from config extras:
        - tax_loss_threshold, capital_gains_hold, tax_harvest_fraction

    Theory: simulation-bases.md §4.3 — TaxAwareInvestor
    Theoretical basis: Constantinides (1983) tax-loss harvesting; anti-disposition via economic incentive.
    See simulation-bases.md §4.3 for mathematical model.
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        purchase_price = self.state.custom_state["purchase_price"]
        market_data = self.state.custom_state["market_data"]

        strategy_name = self.__class__.__name__

        if market_data is None:
            return self._hold_order(round_num, strategy_name)

        price = market_data["price"]
        if price <= 0 or purchase_price <= 0:
            raise ValueError("price and purchase_price must be positive")
        gain_loss = (price - purchase_price) / purchase_price

        tax_loss_threshold = extras["tax_loss_threshold"]
        capital_gains_hold = extras["capital_gains_hold"]
        tax_harvest_fraction = extras["tax_harvest_fraction"]

        quantity = 0.0
        action = "HOLD"

        if gain_loss <= tax_loss_threshold and position > 0:
            # Tax loss harvesting - SELL losers
            quantity = -position * tax_harvest_fraction
            action = "TAX_HARVEST"
        elif gain_loss >= capital_gains_hold:
            # Hold winners for tax deferral (opposite of disposition)
            action = "DEFER_GAINS"

        # Execute
        if quantity > 0:
            cost = quantity * price
            if cost <= cash:
                self.state.custom_state["cash"] -= cost
                self.update_reference_point(quantity, price)
            else:
                quantity = 0
        elif quantity < 0:
            if abs(quantity) <= position:
                proceeds = abs(quantity) * price
                self.state.custom_state["cash"] += proceeds
                self.update_reference_point(quantity, price)
            else:
                quantity = 0

        logger.debug(
            "[%s] R%d (%s): Q=%+8.2f [%s] g/l=%+.1f%% | Cash=%10.2f, Pos=%+8.2f",
            self.config.identity,
            round_num,
            strategy_name,
            quantity,
            action,
            gain_loss * 100,
            self.state.custom_state["cash"],
            self.state.custom_state["position"],
        )

        return {
            "bid_price": price,
            "quantity": quantity,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }

# =============================================================================
# IndexHolder - Passive Baseline
# =============================================================================


class IndexHolder(BaseInvestor):
    """Passive buy-and-hold investor (no active trading).

    Theory: simulation-bases.md §4.4 — IndexHolder
    Theoretical basis: Sharpe (1991) passive investing; zero disposition effect by design.
    See simulation-bases.md §4.4 for mathematical model.
    """

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        market_data = self.state.custom_state["market_data"]

        strategy_name = self.__class__.__name__

        if market_data is None:
            return self._hold_order(round_num, strategy_name)
        price = market_data["price"]
        if price <= 0:
            raise ValueError("market price must be positive")

        # Pure hold - no trading
        quantity = 0.0

        logger.debug(
            "[%s] R%d (%s): Q=%+8.2f [HOLD] | Cash=%10.2f, Pos=%+8.2f",
            self.config.identity,
            round_num,
            strategy_name,
            quantity,
            self.state.custom_state["cash"],
            self.state.custom_state["position"],
        )

        return {
            "bid_price": price,
            "quantity": quantity,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }


# =============================================================================
# InstitutionalInvestor - Professional (Less Disposition)
# =============================================================================


class InstitutionalInvestor(BaseInvestor):
    """
    Institutional Investor.

    Professional money managers show weaker disposition effect
    due to training, oversight, and fiduciary duty.

    Parameters from config extras:
        - gain_threshold, loss_threshold, sell_fraction

    Theory: simulation-bases.md §4.5 — InstitutionalInvestor
    Theoretical basis: Shapira & Venezia (2001) professional discipline; symmetric thresholds reduce disposition bias.
    See simulation-bases.md §4.5 for mathematical model.
    """

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        purchase_price = self.state.custom_state["purchase_price"]
        market_data = self.state.custom_state["market_data"]

        strategy_name = self.__class__.__name__

        if market_data is None:
            return self._hold_order(round_num, strategy_name)

        price = market_data["price"]
        if price <= 0 or purchase_price <= 0:
            raise ValueError("price and purchase_price must be positive")
        gain_loss = (price - purchase_price) / purchase_price

        gain_threshold = extras["gain_threshold"]
        loss_threshold = extras["loss_threshold"]
        sell_fraction = extras["sell_fraction"]

        quantity = 0.0
        action = "HOLD"

        # More rational thresholds
        if gain_loss >= gain_threshold and position > 0:
            quantity = -position * sell_fraction
            action = "TAKE_PROFIT"
        elif gain_loss <= loss_threshold and position > 0:
            quantity = -position * sell_fraction
            action = "CUT_LOSS"

        # Execute
        if quantity > 0:
            cost = quantity * price
            if cost <= cash:
                self.state.custom_state["cash"] -= cost
                self.update_reference_point(quantity, price)
            else:
                quantity = 0
        elif quantity < 0:
            if abs(quantity) <= position:
                proceeds = abs(quantity) * price
                self.state.custom_state["cash"] += proceeds
                self.update_reference_point(quantity, price)
            else:
                quantity = 0

        logger.debug(
            "[%s] R%d (%s): Q=%+8.2f [%s] g/l=%+.1f%% | Cash=%10.2f, Pos=%+8.2f",
            self.config.identity,
            round_num,
            strategy_name,
            quantity,
            action,
            gain_loss * 100,
            self.state.custom_state["cash"],
            self.state.custom_state["position"],
        )

        return {
            "bid_price": price,
            "quantity": quantity,
            "strategy": strategy_name,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }

__all__ = [
    "Market",
    "BaseInvestor",
    "DispositionInvestor",
    "RationalInvestor",
    "TaxAwareInvestor",
    "IndexHolder",
    "InstitutionalInvestor",
]
