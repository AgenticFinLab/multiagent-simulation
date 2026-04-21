import random
import logging
from masim.player.base import Action

"""LUNACollapse Rule-Based Simulation

May 2022 Terra/LUNA crash - $40B wiped out in algorithmic stablecoin death spiral

Theoretical Foundation:
- Algorithmic stablecoin mechanism design (Klages-Mundt et al., 2020)
- Death spiral dynamics (Levy, 2022)
- DeFi contagion (Werner et al., 2022)

Key Dynamics:
- StablecoinHolder: Redeems UST for LUNA, creating selling pressure on LUNA
- Arbitrageur: Arbitrage between UST and LUNA amplifies death spiral
- DeFiLender: Forced liquidations create additional selling pressure
- AnchorDepositor: Withdraws from Anchor protocol when confidence drops
- ValueBuyer: Attempts to buy at deep discount but gets overwhelmed

Parameters from config (see configs/LUNACollapse/Rule/players.yml):
"""

from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

logger = logging.getLogger("LUNACollapse")


class Market(GeneralPlayer):
    """
    Market agent for LUNACollapse simulation.
    
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
        """Stablecoin holder: redeems when confidence drops."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        redemption_threshold = extras["redemption_threshold"]
        
        if deviation < -(1 - redemption_threshold):
            sell_qty = min(int(abs(position) * 0.5), max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """LUNA arbitrage: amplifies death spiral via arbitrage."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        arb_threshold = extras["arb_threshold"]
        
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
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """DeFi liquidation cascade: forced selling."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        liq_threshold = extras["liquidation_threshold"]
        
        if deviation < -(1 - liq_threshold):
            sell_qty = min(int(abs(position) * 0.6), max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Anchor depositor: exits yield protocol when confidence drops."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        yield_threshold = extras["yield_threshold"]
        
        if deviation < -0.05:
            sell_qty = min(int(position * 0.4), max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Value buyer: attempts to buy at deep discount but gets overwhelmed."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        discount_threshold = extras["discount_threshold"]
        
        if deviation < -discount_threshold:
            buy_qty = min(1000, int(cash * 0.2 / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}


__all__ = ["Market", "StablecoinHolder", "Arbitrageur", "DeFiLender", "AnchorDepositor", "ValueBuyer"]
