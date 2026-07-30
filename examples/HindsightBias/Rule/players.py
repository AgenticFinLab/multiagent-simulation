"""HindsightBias Rule-Based Simulation

Hindsight bias causes traders to overestimate how predictable past events were,
distorting future risk assessment.

Theoretical Foundation:
- Fischhoff (1975): Hindsight is not equal to foresight
- Fischhoff & Beyth (1975): I knew it would happen
- Roese & Vohs (2012): Hindsight bias

Key Dynamics:
- HindsightOverconfident: Believes past outcomes were obvious, leading to excessive confidence
- OutcomeLearner: Learns only from outcomes not process, misattributes skill to luck
- ProcessEvaluator: Evaluates decisions by process quality, resists hindsight distortion
- ContrarianSkeptic: Skeptic of post-hoc narratives, trades against hindsight-driven consensus
- NoiseTrader: Random uninformed trader providing baseline liquidity
"""

import logging
import random

from masim.player.base import Action
from masim.player.general import GeneralPlayer

logger = logging.getLogger("HindsightBias")


def _build_order(player: GeneralPlayer, decision_payload: dict, reasoning: str) -> dict:
    """Apply a filled decision to local portfolio state and build canonical order."""
    action = decision_payload["action"]
    quantity = decision_payload["quantity"]
    price = player.state.custom_state["price"]

    if action == "buy" and quantity > 0:
        player.state.custom_state["cash"] -= quantity * price
        player.state.custom_state["position"] += quantity
    elif action == "sell" and quantity > 0:
        player.state.custom_state["cash"] += quantity * price
        player.state.custom_state["position"] -= quantity

    return {
        "type": "order",
        "from": player.identity,
        "action": action,
        "bid_price": price,
        "quantity": quantity,
        "reasoning": reasoning,
        "agent_type": player.__class__.__name__,
        "strategy": player.__class__.__name__,
    }


class Market(GeneralPlayer):
    """
    Market agent for HindsightBias simulation.

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
        self.state.custom_state["prev_price"] = self.state.custom_state["price"]
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
            payload = msg.payload if hasattr(msg, "payload") else msg
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

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = (price - fundamental) / fundamental if fundamental > 0 else 0
        prev_price = self.state.custom_state.get("prev_price", price)
        market_update = {
            "type": "market_update",
            "price": price,
            "prev_price": prev_price,
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

    async def act(self, decision_payload: dict) -> Action:
        price = decision_payload["price"]
        fundamental = decision_payload["fundamental"]
        deviation = decision_payload["deviation"]
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


class HindsightOverconfident(GeneralPlayer):
    """
    Theory: simulation-bases.md §4.1 — HindsightOverconfident

    Theoretical basis: Knew-it-all-along effect (Fischhoff, 1975).
    Believes past outcomes were obvious, leading to excessive confidence in predictions.
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
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        return self._make_decision(price, fundamental, deviation)

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        # Believes past outcomes were obvious, leading to excessive confidence in predictions
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        hindsight_inflation = extras["hindsight_inflation"]
        prediction_overweight = extras["prediction_overweight"]
        activation_threshold = extras["activation_threshold"]
        quantity_scale = extras["quantity_scale"]
        max_order = extras["max_order"]

        if abs(deviation) > activation_threshold:
            qty = min(
                max_order,
                int(
                    abs(deviation)
                    * quantity_scale
                    * hindsight_inflation
                    * prediction_overweight
                ),
            )
            if deviation > 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload: dict) -> Action:
        order = _build_order(
            self, decision_payload, "hindsight-overconfidence threshold rule"
        )

        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class OutcomeLearner(GeneralPlayer):
    """
    Theory: simulation-bases.md §4.2 — OutcomeLearner

    Theoretical basis: Outcome bias (Fischhoff & Beyth, 1975).
    Learns only from outcomes not process, misattributes skill to luck.
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
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        return self._make_decision(price, fundamental, deviation)

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        # Learns only from outcomes not process, misattributes skill to luck and vice versa
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        success_attribution = extras["success_attribution"]
        failure_discount = extras["failure_discount"]
        activation_threshold = extras["activation_threshold"]
        quantity_scale = extras["quantity_scale"]
        max_order = extras["max_order"]

        if abs(deviation) > activation_threshold:
            attribution_scale = (
                success_attribution if deviation > 0 else failure_discount
            )
            qty = min(
                max_order, int(abs(deviation) * quantity_scale * attribution_scale)
            )
            if deviation > 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload: dict) -> Action:
        order = _build_order(self, decision_payload, "outcome-learning threshold rule")

        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class ProcessEvaluator(GeneralPlayer):
    """
    Theory: simulation-bases.md §4.3 — ProcessEvaluator

    Theoretical basis: Process-oriented rationality (Roese & Vohs, 2012).
    Evaluates decisions by process quality, resists hindsight distortion.
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
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        return self._make_decision(price, fundamental, deviation)

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        # Evaluates decisions by process quality not outcomes, resists hindsight distortion
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        process_weight = extras["process_weight"]
        outcome_weight = extras["outcome_weight"]
        activation_threshold = extras["activation_threshold"]
        quantity_scale = extras["quantity_scale"]
        max_order = extras["max_order"]

        if abs(deviation) > activation_threshold:
            qty = min(
                max_order,
                int(abs(deviation) * quantity_scale * process_weight * outcome_weight),
            )
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload: dict) -> Action:
        order = _build_order(
            self, decision_payload, "process-evaluation contrarian rule"
        )

        return Action(
            action_type="order",
            payload={
                "order": order,
                "outbound_messages": [{"payload": order, "content_type": "order"}],
            },
            source_id=self.identity,
        )


class ContrarianSkeptic(GeneralPlayer):
    """
    Theory: simulation-bases.md §4.4 — ContrarianSkeptic

    Theoretical basis: Narrative skepticism (Roese & Vohs, 2012).
    Skeptic of post-hoc narratives, trades against hindsight-driven consensus.
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
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        return self._make_decision(price, fundamental, deviation)

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        # Skeptic of post-hoc narratives, trades against hindsight-driven consensus
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        skepticism_level = extras["skepticism_level"]
        activation_threshold = extras["activation_threshold"]
        quantity_scale = extras["quantity_scale"]
        max_order = extras["max_order"]

        if abs(deviation) > activation_threshold:
            qty = min(
                max_order, int(abs(deviation) * quantity_scale * skepticism_level)
            )
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload: dict) -> Action:
        order = _build_order(
            self, decision_payload, "contrarian-skeptic threshold rule"
        )

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
    Theory: simulation-bases.md §4.5 — NoiseTrader

    Theoretical basis: Noise trader model (Black, 1986).
    Random uninformed trader providing baseline liquidity.
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
            payload = msg.payload if hasattr(msg, "payload") else msg
            if isinstance(payload, dict) and payload["type"] == "market_update":
                self.state.custom_state["price"] = payload["price"]
                self.state.custom_state["fundamental"] = payload["fundamental"]
                self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        return self._make_decision(price, fundamental, deviation)

    def _make_decision(
        self, price: float, fundamental: float, deviation: float
    ) -> dict:
        # Random uninformed trader providing baseline liquidity
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        trade_probability = extras["trade_probability"]
        min_order = extras["min_order"]
        max_order = extras["max_order"]

        if random.random() < trade_probability:
            qty = random.randint(min_order, max_order)
            action = "buy" if random.random() > 0.5 else "sell"
            if action == "buy":
                qty = min(qty, int(cash / price) if price > 0 else 0)
            else:
                qty = min(qty, max(position, 0))
            if qty > 0:
                return {"action": action, "quantity": qty}
        return {"action": "hold", "quantity": 0}

    async def act(self, decision_payload: dict) -> Action:
        order = _build_order(self, decision_payload, "noise-trader random liquidity rule")

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
    "HindsightOverconfident",
    "OutcomeLearner",
    "ProcessEvaluator",
    "ContrarianSkeptic",
    "NoiseTrader",
]
