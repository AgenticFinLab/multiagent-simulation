import random
import logging
from masim.player.base import Action

"""BlackMonday1987 Rule-Based Simulation

October 19, 1987 stock market crash - Dow fell 22.6% in one day

Theoretical Foundation:
- Brady Commission (1988): Portfolio insurance as key amplifier
- Genotte & Leland (1990): Noise trading and portfolio insurance
- Jacklin et al. (1992): Information cascades during crash

Key Dynamics:
- PortfolioInsurer: Dynamic hedging strategy that sells as prices fall
- IndexArbitrageur: Exploits price gaps between index futures and stocks
- ProgramTrader: Automated trading that amplifies price moves
- ValueInvestor: Buys when price falls below intrinsic value
- NoiseTrader: Random uninformed trader

Parameters from config (see configs/BlackMonday1987/Rule/players.yml):
"""

from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

logger = logging.getLogger("BlackMonday1987")


class Market(GeneralPlayer):
    """
    Market agent for BlackMonday1987 simulation.

    Price Formation Model:
        P(t+1) = P(t) + λ × NetDemand + γ × (F - P(t)) + ε

    Where:
        - λ: Price impact coefficient
        - γ: Mean reversion strength
        - F: Fundamental value
        - ε: Random noise
    """

    async def perceive(
        self,
        observation,
        prev_result=None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            self._initialize_market_state()

        orders = self._extract_orders(observation)
        market_result = self._clear_market(orders)
        self._update_state(market_result)
        self._log_market_state()

    def _initialize_market_state(self) -> None:
        extras = self.config.extras
        self.state.custom_state["price"] = extras["initial_price"]
        self.state.custom_state["fundamental"] = extras["fundamental_value"]
        self.state.custom_state["price_history"] = []
        self.state.custom_state["volume_history"] = []

        self.state.custom_state["price_impact"] = extras["price_impact"]
        self.state.custom_state["mean_reversion"] = extras["mean_reversion"]
        self.state.custom_state["noise_std"] = extras["noise_std"]

    def _extract_orders(self, observation) -> list:
        orders = []
        for msg in observation.messages:
            if msg.get("type") == "order":
                orders.append(
                    {
                        "agent_id": msg.get("from"),
                        "action": msg.get("action"),
                        "quantity": msg.get("quantity"),
                        "agent_type": msg.get("agent_type"),
                    }
                )
        return orders

    def _clear_market(self, orders: list) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]

        buy_orders = [o for o in orders if o["action"] == "buy"]
        sell_orders = [o for o in orders if o["action"] == "sell"]
        total_buy = sum(o["quantity"] for o in buy_orders)
        total_sell = sum(o["quantity"] for o in sell_orders)
        net_demand = total_buy - total_sell

        price_impact = self.state.custom_state["price_impact"]
        mean_reversion = self.state.custom_state["mean_reversion"]
        noise_std = self.state.custom_state["noise_std"]

        price_change = price_impact * net_demand
        reversion = mean_reversion * (fundamental - price)
        noise = random.gauss(0, noise_std)

        new_price = price + price_change + reversion + noise
        new_price = max(new_price, 0.01)

        volume = min(total_buy, total_sell) + abs(net_demand) * 0.5

        return {
            "price": new_price,
            "volume": volume,
            "net_demand": net_demand,
        }

    def _update_state(self, market_result: dict) -> None:
        self.state.custom_state["price"] = market_result["price"]
        self.state.custom_state["price_history"].append(market_result["price"])
        self.state.custom_state["volume_history"].append(market_result["volume"])

    def _log_market_state(self) -> None:
        logger = logging.getLogger("{name}")
        logger.debug(
            "Round %%d: price=%%.2f",
            self.state.custom_state["round"],
            self.state.custom_state["price"],
        )

    async def step(self):
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = (price - fundamental) / fundamental if fundamental > 0 else 0

        market_update = {
            "type": "market_update",
            "price": price,
            "fundamental": fundamental,
            "deviation": deviation,
            "round": self.state.custom_state["round"],
        }

        return Action(
            action_type="market_broadcast",
            payload={
                "market_data": market_update,
                "outbound_messages": [
                    {"payload": market_update, "content_type": "market_update"}
                ],
            },
            source_id=self.identity,
        )


class PortfolioInsurer(GeneralPlayer):
    """
    Dynamic hedging strategy that sells as prices fall

    Theoretical Basis: Portfolio insurance (Leland & Rubinstein, 1980)
    Market Role: destabilizing

    Parameters from config:
        hedge_ratio=0.5, rebalance_threshold=0.02, initial_insurance=1000000
    """

    async def perceive(
        self,
        observation,
        prev_result=None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            self._initialize_investor_state()

        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self.state.custom_state["price"] = msg.get("price")
                self.state.custom_state["fundamental"] = msg.get("fundamental")
                self.state.custom_state["deviation"] = msg.get("deviation")

    def _initialize_investor_state(self) -> None:
        extras = self.config.extras
        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]
        self.state.custom_state["price_history"] = []

    async def step(self):
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]

        decision = self._make_decision(price, fundamental, deviation)

        order = {
            "type": "order",
            "action": decision["action"],
            "quantity": decision["quantity"],
            "agent_type": "destabilizing",
        }
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        """Portfolio insurance: dynamic hedging that sells as prices fall.

        Based on Leland & Rubinstein (1980) portfolio insurance model.
        When price drops, increase short position to maintain floor value.
        Hedge ratio determines sensitivity to price changes.
        """
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        hedge_ratio = extras["hedge_ratio"]
        rebalance_threshold = extras["rebalance_threshold"]

        if abs(deviation) > rebalance_threshold:
            if deviation < 0:
                sell_quantity = int(abs(deviation) * hedge_ratio * abs(position))
                sell_quantity = min(sell_quantity, max(position, 0))
                if sell_quantity > 0:
                    return {"action": "sell", "quantity": sell_quantity}
            else:
                buy_quantity = (
                    int(deviation * hedge_ratio * cash / price) if price > 0 else 0
                )
                buy_quantity = min(buy_quantity, 500)
                if buy_quantity > 0:
                    return {"action": "buy", "quantity": buy_quantity}

        return {"action": "hold", "quantity": 0}


class IndexArbitrageur(GeneralPlayer):
    """
    Exploits price gaps between index futures and stocks

    Theoretical Basis: Index arbitrage between futures and spot
    Market Role: destabilizing

    Parameters from config:
        arbitrage_threshold=0.005, position_size=500, speed=fast
    """

    async def perceive(
        self,
        observation,
        prev_result=None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            self._initialize_investor_state()

        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self.state.custom_state["price"] = msg.get("price")
                self.state.custom_state["fundamental"] = msg.get("fundamental")
                self.state.custom_state["deviation"] = msg.get("deviation")

    def _initialize_investor_state(self) -> None:
        extras = self.config.extras
        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]
        self.state.custom_state["price_history"] = []

    async def step(self):
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]

        decision = self._make_decision(price, fundamental, deviation)

        order = {
            "type": "order",
            "action": decision["action"],
            "quantity": decision["quantity"],
            "agent_type": "destabilizing",
        }
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        """Index arbitrage: exploits gaps between futures and spot prices.

        When spot price deviates from fair value (determined by
        futures pricing), arbitrageurs buy the underpriced and sell
        the overpriced, amplifying price moves in the same direction
        as the portfolio insurers' sell orders.
        """
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        arb_threshold = extras["arbitrage_threshold"]
        position_size = extras["position_size"]

        if abs(deviation) > arb_threshold:
            if deviation > 0:
                sell_qty = min(position_size, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
            else:
                buy_qty = min(position_size, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}

        return {"action": "hold", "quantity": 0}


class ProgramTrader(GeneralPlayer):
    """
    Automated trading that amplifies price moves

    Theoretical Basis: Program trading feedback (Brady Commission, 1988)
    Market Role: destabilizing

    Parameters from config:
        trigger_threshold=0.01, sell_size=1000, feedback_strength=0.3
    """

    async def perceive(
        self,
        observation,
        prev_result=None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            self._initialize_investor_state()

        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self.state.custom_state["price"] = msg.get("price")
                self.state.custom_state["fundamental"] = msg.get("fundamental")
                self.state.custom_state["deviation"] = msg.get("deviation")

    def _initialize_investor_state(self) -> None:
        extras = self.config.extras
        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]
        self.state.custom_state["price_history"] = []

    async def step(self):
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]

        decision = self._make_decision(price, fundamental, deviation)

        order = {
            "type": "order",
            "action": decision["action"],
            "quantity": decision["quantity"],
            "agent_type": "destabilizing",
        }
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        """Program trading: amplifies price moves via automated sell triggers.

        Based on Brady Commission (1988) finding that program trading
        created positive feedback loops on Black Monday. When price
        drops below threshold, triggers large automated sell orders.
        """
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        trigger_threshold = extras["trigger_threshold"]
        sell_size = extras["sell_size"]
        feedback_strength = extras["feedback_strength"]

        if deviation < -trigger_threshold:
            amplified_sell = int(
                sell_size * (1 + feedback_strength * abs(deviation) * 10)
            )
            sell_qty = min(amplified_sell, max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        elif deviation > trigger_threshold:
            buy_qty = min(sell_size, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}

        return {"action": "hold", "quantity": 0}


class ValueInvestor(GeneralPlayer):
    """
    Buys when price falls below intrinsic value

    Theoretical Basis: Value investing (Graham, 1949)
    Market Role: stabilizing

    Parameters from config:
        value_discount=0.15, order_size=800, patience=high
    """

    async def perceive(
        self,
        observation,
        prev_result=None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            self._initialize_investor_state()

        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self.state.custom_state["price"] = msg.get("price")
                self.state.custom_state["fundamental"] = msg.get("fundamental")
                self.state.custom_state["deviation"] = msg.get("deviation")

    def _initialize_investor_state(self) -> None:
        extras = self.config.extras
        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]
        self.state.custom_state["price_history"] = []

    async def step(self):
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]

        decision = self._make_decision(price, fundamental, deviation)

        order = {
            "type": "order",
            "action": decision["action"],
            "quantity": decision["quantity"],
            "agent_type": "stabilizing",
        }
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        """Value investing: buys when price falls below intrinsic value.

        Based on Graham (1949) - buys with margin of safety when
        market overreacts to the downside. Provides stabilizing force.
        """
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        value_discount = extras["value_discount"]
        order_size = extras["order_size"]

        if deviation < -value_discount:
            buy_qty = min(order_size, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        elif deviation > value_discount:
            sell_qty = min(order_size, max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}

        return {"action": "hold", "quantity": 0}


class NoiseTrader(GeneralPlayer):
    """
    Random uninformed trader

    Theoretical Basis: Black (1986)
    Market Role: neutral

    Parameters from config:
        trade_probability=0.05, min_order=100, max_order=500
    """

    async def perceive(
        self,
        observation,
        prev_result=None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            self._initialize_investor_state()

        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self.state.custom_state["price"] = msg.get("price")
                self.state.custom_state["fundamental"] = msg.get("fundamental")
                self.state.custom_state["deviation"] = msg.get("deviation")

    def _initialize_investor_state(self) -> None:
        extras = self.config.extras
        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]
        self.state.custom_state["price_history"] = []

    async def step(self):
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]

        decision = self._make_decision(price, fundamental, deviation)

        order = {
            "type": "order",
            "action": decision["action"],
            "quantity": decision["quantity"],
            "agent_type": "neutral",
        }
        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        """Noise trading: random buy/sell for background liquidity.

        Based on Black (1986) - noise makes markets possible.
        Trades randomly with configured probability.
        """
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        prob = extras["trade_probability"]
        min_order = extras["min_order"]
        max_order = extras["max_order"]

        if random.random() < prob:
            quantity = random.randint(min_order, max_order)
            action = "buy" if random.random() > 0.5 else "sell"
            if action == "buy":
                quantity = min(quantity, int(cash / price) if price > 0 else 0)
            else:
                quantity = min(quantity, max(position, 0))
            if quantity > 0:
                return {"action": action, "quantity": quantity}

        return {"action": "hold", "quantity": 0}


__all__ = [
    "Market",
    "PortfolioInsurer",
    "IndexArbitrageur",
    "ProgramTrader",
    "ValueInvestor",
    "NoiseTrader",
]
