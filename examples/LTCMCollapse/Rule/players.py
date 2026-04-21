import random
import logging
from masim.player.base import Action

"""LTCMCollapse Rule-Based Simulation

August-September 1998 LTCM crisis - Russian default triggered liquidity crisis

Theoretical Foundation:
- Shleifer & Vishny (1997): Limits to arbitrage
- Long-Term Capital Management (1998): Convergence trades gone wrong
- Morris & Shin (2004): Liquidity black holes

Key Dynamics:
- ConvergenceArbitrageur: Bets on spread convergence between related securities
- LeverageTrader: Highly leveraged trader forced to deleverage in crisis
- RiskManager: Monitors portfolio risk and cuts positions when VaR breached
- LiquidityProvider: Provides liquidity but withdraws when spreads widen
- CentralBank: Provides emergency liquidity to prevent systemic collapse

Parameters from config (see configs/LTCMCollapse/Rule/players.yml):
"""

from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

logger = logging.getLogger("LTCMCollapse")


class Market(GeneralPlayer):
    """
    Market agent for LTCMCollapse simulation.
    
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
        """Convergence arbitrage: bets on spread narrowing.
        
        Based on LTCM strategy of convergence trades. When spread
        widens (price deviates from fundamental), increase position
        betting on convergence. Uses high leverage.
        """
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        entry_spread = extras["entry_spread"]
        leverage = extras["leverage"]
        max_position = extras["max_position"]
        
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
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Leverage cycle: forced to deleverage when losses mount.
        
        Based on Geanakoplos (2010) leverage cycle theory. Initially
        uses high leverage, but when losses exceed threshold, must
        rapidly deleverage, creating fire-sale pressure.
        """
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        leverage_ratio = extras["leverage_ratio"]
        margin_call = extras["margin_call_threshold"]
        
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
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """VaR-based risk management: cuts positions when risk exceeds limit."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        var_limit = extras["var_limit"]
        
        if abs(deviation) > var_limit * 3:
            cut_qty = int(abs(position) * 0.5)
            if position > 0:
                return {"action": "sell", "quantity": min(cut_qty, position)}
            elif position < 0:
                return {"action": "buy", "quantity": cut_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Market making under stress: provides liquidity but withdraws when spreads widen."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        normal_spread = extras["normal_spread"]
        stress_spread = extras["stress_spread"]
        inventory_limit = extras["inventory_limit"]
        
        if abs(deviation) > 0.05:
            return {"action": "hold", "quantity": 0}
        
        if abs(position) < inventory_limit:
            qty = min(500, inventory_limit - abs(position))
            if deviation > 0:
                return {"action": "sell", "quantity": qty}
            else:
                return {"action": "buy", "quantity": qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Lender of last resort: provides emergency liquidity during crisis.
        
        Based on Bagehot (1873) principles: lend freely at a penalty rate
        against good collateral to solvent institutions.
        """
        extras = self.config.extras
        intervention_threshold = extras["intervention_threshold"]
        rescue_prob = extras["rescue_probability"]
        
        if deviation < -intervention_threshold and random.random() < rescue_prob:
            return {"action": "buy", "quantity": 2000}
        return {"action": "hold", "quantity": 0}


__all__ = ["Market", "ConvergenceArbitrageur", "LeverageTrader", "RiskManager", "LiquidityProvider", "CentralBank"]
