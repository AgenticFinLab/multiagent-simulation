import random
import logging
from masim.player.base import Action

"""GFC2008 Rule-Based Simulation

2007-2009 financial crisis - Housing bubble burst triggered global recession

Theoretical Foundation:
- Gorton (2010): Securitized banking and the run on repo
- Brunnermeier (2009): Deciphering the liquidity and credit crunch
- Acharya & Richardson (2009): Restoring financial stability

Key Dynamics:
- MBSOriginator: Creates mortgage-backed securities with lax screening
- RatingAgency: Overrates securities due to issuer-pays model
- LeveragedInvestor: Uses high leverage, forced to sell in downturn
- DistressedBuyer: Buys assets at deep discount during panic
- Regulator: Monitors systemic risk and may intervene

Parameters from config (see configs/GFC2008/Rule/players.yml):
"""

from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

logger = logging.getLogger("GFC2008")


class Market(GeneralPlayer):
    """
    Market agent for GFC2008 simulation.
    
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
                orders.append({
                    "agent_id": msg.get("from"),
                    "action": msg.get("action"),
                    "quantity": msg.get("quantity"),
                    "agent_type": msg.get("agent_type"),
                })
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
            payload={"market_data": market_update, "outbound_messages": [{"payload": market_update, "content_type": "market_update"}]},
            source_id=self.identity,
        )


    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Originate-to-distribute: creates securities with lax screening."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        origination_rate = extras["origination_rate"]
        
        sell_qty = int(abs(position) * origination_rate)
        if sell_qty > 0 and position > 0:
            return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Rating agency: overrates securities due to conflict of interest."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        overrating_bias = extras["overrating_bias"]
        
        perceived_fundamental = fundamental * (1 + overrating_bias)
        if price < perceived_fundamental * 0.95:
            buy_qty = min(300, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Leveraged investor: fire sales when margin called."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        leverage = extras["leverage"]
        margin_trigger = extras["margin_call_trigger"]
        
        if deviation < -margin_trigger:
            fire_sale_qty = int(abs(position) * 0.5)
            if position > 0 and fire_sale_qty > 0:
                return {"action": "sell", "quantity": min(fire_sale_qty, position)}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Distressed buyer: buys at deep discount during panic."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        discount_threshold = extras["discount_threshold"]
        
        if deviation < -discount_threshold:
            buy_qty = min(1000, int(cash * 0.3 / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Regulator: intervenes during systemic stress."""
        extras = self.config.extras
        intervention_threshold = extras["intervention_threshold"]
        rescue_prob = extras["rescue_probability"]
        
        if deviation < -intervention_threshold and random.random() < rescue_prob:
            return {"action": "buy", "quantity": 3000}
        return {"action": "hold", "quantity": 0}


__all__ = ["Market", "MBSOriginator", "RatingAgency", "LeveragedInvestor", "DistressedBuyer", "Regulator"]
