"""AnchoringEffect Rule-Based Simulation — pilot rewiring.

This module used to inline every investor archetype. It is now the reference
example of the new canonical layer:

    * The ``Market`` coordinator remains inline (coordinators are still
      per-scenario until the market-coordinator canonical base lands).
    * The 9 investor archetypes are imported from :mod:`masim.agents`
      and re-exported under the historical PascalCase names used by
      ``configs/AnchoringEffect/Rule/players.yml``.

Naming contract:
    - Canonical class in ``masim.agents.<snake_stem>``: ``Rule<Camel>`` /
      ``LLM<Camel>``, both carrying ``STRATEGY = "<kebab-stem>"`` where
      ``<kebab-stem>`` is the ``examples/AGENT_POOL/finance/<stem>.md`` id.
    - Scenario-facing alias: PascalCase name expected by the existing
      ``players.yml`` (``class: "examples.AnchoringEffect.Rule.players:X"``).

Rewire scope:
    - Market                        (inline, unchanged)
    - AnchoredTrader                <- masim.agents.anchored_trader
    - HistoricalAnchor              <- masim.agents.historical_anchor
    - RationalUpdater               <- masim.agents.rational_updater
    - MomentumTrader                <- masim.agents.momentum_trader
    - NoiseTrader                   <- masim.agents.noise_trader
    - DispositionTrader             <- masim.agents.disposition_trader
    - ContrarianTrader              <- masim.agents.contrarian_trader
    - FundamentalAnalyst            <- masim.agents.fundamental_analyst
    - LiquidityProvider             <- masim.agents.liquidity_provider

All numeric parameters continue to flow from ``players.yml`` extras;
the canonical classes read the same extras keys that the inlined
predecessors did (verified during pilot migration).
"""

from __future__ import annotations

import logging
import os
import random
from typing import Any, Dict, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

# Canonical archetype implementations (Rule variants).
# Rule / LLM siblings live at masim.agents.<snake_stem>; the STRATEGY
# attribute on each class carries the kebab-case AGENT_POOL stem.
from masim.agents import (
    RuleAnchoredTrader as AnchoredTrader,
    RuleContrarianTrader as ContrarianTrader,
    RuleDispositionTrader as DispositionTrader,
    RuleFundamentalAnalyst as FundamentalAnalyst,
    RuleHistoricalAnchor as HistoricalAnchor,
    RuleLiquidityProvider as LiquidityProvider,
    RuleMomentumTrader as MomentumTrader,
    RuleNoiseTrader as NoiseTrader,
    RuleRationalUpdater as RationalUpdater,
)

logger = logging.getLogger("AnchoringEffect")


class Market(GeneralPlayer):
    """
    Central market coordinator for AnchoringEffect simulation.

    Implements simulation-bases.md §3.1 — Price Formation Model:
        P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon

    Variable mapping (simulation-bases.md §3.1 → code):
        lambda (price_impact):    extras["price_impact"]      = 0.01
        gamma (mean_reversion):   extras["mean_reversion"]    = 0.01
        F (fundamental value):    extras["fundamental_value"] = 100.0
        epsilon (noise):          random.gauss(0, noise_std)

    See also:
        - simulation-bases.md §3.2: price floor mechanism (max(new_price, 0.01))
        - simulation-bases.md §3.3: information broadcast design (market_data payload)

    NOTE: Coordinator remains inline pending a future canonical
    ``masim.agents.market.*`` base class (broadcaster lifecycle differs
    from the bidder base ``CanonicalRulePlayer``).
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
            hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["fundamental_value"]
            self.state.custom_state["price_impact"] = extras["price_impact"]
            self.state.custom_state["mean_reversion"] = extras["mean_reversion"]
            self.state.custom_state["noise_std"] = extras["noise_std"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(record_path, "market", "price"),
                entry_limit=hot_limit,
            )

        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                orders.append(inb.payload)

        current_price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        price_impact = self.state.custom_state["price_impact"]
        mean_reversion = self.state.custom_state["mean_reversion"]
        noise_std = self.state.custom_state["noise_std"]

        buy_qty = sum(o["quantity"] for o in orders if o["action"] == "buy")
        sell_qty = sum(o["quantity"] for o in orders if o["action"] == "sell")
        net_demand = buy_qty - sell_qty

        noise = random.gauss(0, noise_std)
        new_price = (
            current_price
            + price_impact * net_demand
            + mean_reversion * (fundamental - current_price)
            + noise
        )
        new_price = max(new_price, 0.01)

        deviation = (new_price - fundamental) / fundamental if fundamental > 0 else 0.0
        prev_price = current_price

        self.state.custom_state["price"] = new_price
        self.state.custom_state["prev_price"] = prev_price
        self.state.custom_state["deviation"] = deviation
        self.state.custom_state["price_history"].append(new_price)

        logger.debug(
            "Round %d: price=%.2f fundamental=%.2f deviation=%+.2f%%",
            round_num,
            new_price,
            fundamental,
            deviation * 100,
        )

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        prev_price = self.state.custom_state["prev_price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        round_num = self.state.custom_state["round"]

        market_data = {
            "price": price,
            "prev_price": prev_price,
            "fundamental": fundamental,
            "deviation": deviation,
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


__all__ = [
    "Market",
    "AnchoredTrader",
    "HistoricalAnchor",
    "RationalUpdater",
    "MomentumTrader",
    "NoiseTrader",
    "DispositionTrader",
    "ContrarianTrader",
    "FundamentalAnalyst",
    "LiquidityProvider",
]
