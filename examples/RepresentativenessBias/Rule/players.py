"""RepresentativenessBias Rule-Based Simulation

Representativeness heuristic causes traders to judge probability by similarity to prototypes rather than base rates

Theoretical Foundation:
- Kahneman & Tversky (1972): Subjective probability - A judgment of representativeness
- Grether (1980): Bayes rule as a descriptive model
- Barberis, Shleifer & Vishny (1998): A model of investor sentiment

Key Dynamics:
- PatternMatcher: Matches current price patterns to historical prototypes, ignoring base rates
- CategoryOvergeneralizer: Overgeneralizes from small samples, treating stocks as belonging to dramatic categories
- BayesianUpdater: Correctly updates beliefs using Bayes rule, weighing base rates and new evidence
- ContrarianStatistical: Trades against pattern-matching mispricing by exploiting base rate deviations
- NoiseTrader: Random uninformed trader providing baseline liquidity

Parameters from config (see configs/RepresentativenessBias/Rule/players.yml):
"""

import logging
import random
from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("RepresentativenessBias")


def _info_payload(message: Any) -> Any:
    if hasattr(message, "payload"):
        payload = message.payload
        if isinstance(payload, dict) and "order" in payload:
            return payload["order"]
        if isinstance(payload, dict) and "market_data" in payload:
            return payload["market_data"]
        return payload
    if isinstance(message, dict):
        if "payload" in message:
            payload = message["payload"]
            if isinstance(payload, dict) and "order" in payload:
                return payload["order"]
            if isinstance(payload, dict) and "market_data" in payload:
                return payload["market_data"]
            return payload
        if "order" in message:
            return message["order"]
        if "market_data" in message:
            return message["market_data"]
        return message
    return message


def _with_order_message(
    identity: str, agent_type: str, decision: Dict[str, Any], price: float
) -> Dict[str, Any]:
    order = {
        "type": "order",
        "from": identity,
        "action": decision["action"],
        "bid_price": price,
        "quantity": decision["quantity"],
        "agent_type": agent_type,
        "reasoning": decision["reasoning"],
    }
    return {
        **decision,
        "outbound_messages": [{"payload": order, "content_type": "order"}],
    }


class Market(GeneralPlayer):
    """
    Market agent for RepresentativenessBias simulation.

    Price Formation Model:
        P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon
    """

    async def perceive(self, observation, prev_result=None) -> None:
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
        for msg in observation.inbounds:
            payload = _info_payload(msg)
            if isinstance(payload, dict) and payload["type"] == "order":
                orders.append(
                    {
                        "agent_id": payload["from"],
                        "action": payload["action"],
                        "quantity": payload["quantity"],
                        "agent_type": payload["agent_type"],
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
        return {"price": new_price, "volume": volume, "net_demand": net_demand}

    def _update_state(self, market_result: dict) -> None:
        self.state.custom_state["price"] = market_result["price"]
        self.state.custom_state["price_history"].append(market_result["price"])
        self.state.custom_state["volume_history"].append(market_result["volume"])

    def _log_market_state(self) -> None:
        logger.debug(
            "Round %d: price=%.2f",
            self.state.custom_state["round"],
            self.state.custom_state["price"],
        )

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        if fundamental <= 0:
            raise ValueError("fundamental must be positive")
        deviation = (price - fundamental) / fundamental
        market_update = {
            "type": "market_update",
            "price": price,
            "fundamental": fundamental,
            "deviation": deviation,
            "round": self.state.custom_state["round"],
        }
        return {
            **market_update,
            "outbound_messages": [
                {"payload": market_update, "content_type": "market_update"}
            ],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        market_update = {
            "type": "market_update",
            "price": decision_payload["price"],
            "fundamental": decision_payload["fundamental"],
            "deviation": decision_payload["deviation"],
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


class PatternMatcher(GeneralPlayer):
    """
    Matches current price patterns to historical prototypes, ignoring base rates.

    Theory: simulation-bases.md §4.1 — PatternMatcher
    Theoretical basis: representativeness heuristic; salient prototypes
    dominate base-rate reasoning.
    See simulation-bases.md §4.1 for mathematical model.
    """

    async def perceive(self, observation, prev_result=None) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]

        for msg in observation.inbounds:
            payload = _info_payload(msg)
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        decision = self._make_decision(price, fundamental, deviation)
        return _with_order_message(self.identity, self.__class__.__name__, decision, price)

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        # Matches current price patterns to historical prototypes, ignoring base rates
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        _pattern_sensitivity = extras["pattern_sensitivity"]
        _base_rate_ignore = extras["base_rate_ignore"]

        if abs(deviation) > 0.02:
            qty = min(800, int(abs(deviation) * 5000))
            if deviation > 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {
                        "action": "buy",
                        "quantity": buy_qty,
                        "reasoning": "Prototype match implies bullish continuation.",
                    }
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {
                        "action": "sell",
                        "quantity": sell_qty,
                        "reasoning": "Prototype match implies bearish continuation.",
                    }
        return {"action": "hold", "quantity": 0, "reasoning": "No salient pattern threshold crossed."}

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "bid_price": self.state.custom_state["price"],
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
            "reasoning": decision_payload["reasoning"],
        }

        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class CategoryOvergeneralizer(GeneralPlayer):
    """
    Overgeneralizes from small samples into dramatic stock categories.

    Theory: simulation-bases.md §4.2 — CategoryOvergeneralizer
    Theoretical basis: base-rate neglect and small-sample extrapolation.
    See simulation-bases.md §4.2 for mathematical model.
    """

    async def perceive(self, observation, prev_result=None) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]

        for msg in observation.inbounds:
            payload = _info_payload(msg)
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        decision = self._make_decision(price, fundamental, deviation)
        return _with_order_message(self.identity, self.__class__.__name__, decision, price)

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        # Overgeneralizes from small samples, treating stocks as belonging to dramatic categories
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        _category_weight = extras["category_weight"]
        _sample_bias = extras["sample_bias"]

        if abs(deviation) > 0.02:
            qty = min(800, int(abs(deviation) * 5000))
            if deviation > 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {
                        "action": "buy",
                        "quantity": buy_qty,
                        "reasoning": "Small-sample category assignment is bullish.",
                    }
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {
                        "action": "sell",
                        "quantity": sell_qty,
                        "reasoning": "Small-sample category assignment is bearish.",
                    }
        return {"action": "hold", "quantity": 0, "reasoning": "Category evidence is below threshold."}

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "bid_price": self.state.custom_state["price"],
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
            "reasoning": decision_payload["reasoning"],
        }

        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class BayesianUpdater(GeneralPlayer):
    """
    Correctly updates beliefs using base rates and new evidence.

    Theory: simulation-bases.md §4.3 — BayesianUpdater
    Theoretical basis: Bayesian rationality as a stabilizing benchmark.
    See simulation-bases.md §4.3 for mathematical model.
    """

    async def perceive(self, observation, prev_result=None) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]

        for msg in observation.inbounds:
            payload = _info_payload(msg)
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        decision = self._make_decision(price, fundamental, deviation)
        return _with_order_message(self.identity, self.__class__.__name__, decision, price)

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        # Correctly updates beliefs using Bayes rule, weighing base rates and new evidence
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        _base_rate_weight = extras["base_rate_weight"]
        _evidence_weight = extras["evidence_weight"]

        if abs(deviation) > 0.05:
            qty = min(500, int(abs(deviation) * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {
                        "action": "buy",
                        "quantity": buy_qty,
                        "reasoning": "Bayesian update identifies undervaluation.",
                    }
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {
                        "action": "sell",
                        "quantity": sell_qty,
                        "reasoning": "Bayesian update identifies overvaluation.",
                    }
        return {"action": "hold", "quantity": 0, "reasoning": "Evidence does not overcome the base rate."}

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "bid_price": self.state.custom_state["price"],
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
            "reasoning": decision_payload["reasoning"],
        }

        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class ContrarianStatistical(GeneralPlayer):
    """
    Trades against pattern-matching mispricing and base-rate deviations.

    Theory: simulation-bases.md §4.4 — ContrarianStatistical
    Theoretical basis: statistical arbitrage against biased beliefs.
    See simulation-bases.md §4.4 for mathematical model.
    """

    async def perceive(self, observation, prev_result=None) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]

        for msg in observation.inbounds:
            payload = _info_payload(msg)
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        decision = self._make_decision(price, fundamental, deviation)
        return _with_order_message(self.identity, self.__class__.__name__, decision, price)

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        # Trades against pattern-matching mispricing by exploiting base rate deviations
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        _contrarian_threshold = extras["contrarian_threshold"]
        _position_size = extras["position_size"]

        if abs(deviation) > 0.05:
            qty = min(500, int(abs(deviation) * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {
                        "action": "buy",
                        "quantity": buy_qty,
                        "reasoning": "Contrarian signal identifies underpricing.",
                    }
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {
                        "action": "sell",
                        "quantity": sell_qty,
                        "reasoning": "Contrarian signal identifies overpricing.",
                    }
        return {"action": "hold", "quantity": 0, "reasoning": "Mispricing is below contrarian threshold."}

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "bid_price": self.state.custom_state["price"],
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
            "reasoning": decision_payload["reasoning"],
        }

        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class NoiseTrader(GeneralPlayer):
    """
    Random uninformed trader providing baseline liquidity.

    Theory: simulation-bases.md §4.5 — NoiseTrader
    Theoretical basis: noise-trader models of uninformed order flow.
    See simulation-bases.md §4.5 for mathematical model.
    """

    async def perceive(self, observation, prev_result=None) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]

        for msg in observation.inbounds:
            payload = _info_payload(msg)
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        decision = self._make_decision(price, fundamental, deviation)
        return _with_order_message(self.identity, self.__class__.__name__, decision, price)

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        # Random uninformed trader providing baseline liquidity
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        _trade_probability = extras["trade_probability"]

        if random.random() < _trade_probability:
            qty = random.randint(100, 500)
            action = "buy" if random.random() > 0.5 else "sell"
            if action == "buy":
                qty = min(qty, int(cash / price) if price > 0 else 0)
            else:
                qty = min(qty, max(position, 0))
            if qty > 0:
                return {
                    "action": action,
                    "quantity": qty,
                    "reasoning": "Random liquidity trade from configured probability.",
                }
        return {"action": "hold", "quantity": 0, "reasoning": "Random draw produced no trade."}

    async def act(self, decision_payload: dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "bid_price": self.state.custom_state["price"],
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
            "reasoning": decision_payload["reasoning"],
        }

        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


__all__ = [
    "Market",
    "PatternMatcher",
    "CategoryOvergeneralizer",
    "BayesianUpdater",
    "ContrarianStatistical",
    "NoiseTrader",
]
