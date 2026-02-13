"""Demo Conductor - Simple Market Implementation

A simple market that:
1. Notifies investors with current market state
2. Collects price submissions from all investors (response_pool)
3. Calculates the average price
4. Broadcasts the average back to all investors

Conductor Contract:
- notify(): Send round state to Players (Conductor → Players)
- collect_responses(): Gather responses from Players (Players → Conductor)
- analyze(): Process the collected response_pool
- coordinate(): Produce CoordinationDecision
"""

import logging
from typing import Any, Dict, List

from masim.conductor.base import (
    BaseConductor,
    CoordinationDecision,
    DecisionScope,
)
from masim.player.base import Action

logger = logging.getLogger("Demo")


class SimpleMarket(BaseConductor):
    """
    A simple market that calculates average price from all investors.

    Each round:
    1. notify(): Broadcast current avg_price to investors
    2. collect_responses(): Collect price submissions from investors
    3. analyze(): Calculate new average price
    4. coordinate(): Store new average for next round
    """

    def notify(
        self,
        round_num: int,
        player_ids: List[str],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Notify investors of current market state.

        Args:
            round_num: Current simulation round
            player_ids: List of player IDs

        Returns:
            Dict of player_id -> notification_dict
        """
        # Get current avg_price from state, or use initial price
        if "avg_price" in self._state.custom_state:
            avg_price = self._state.custom_state["avg_price"]
        else:
            avg_price = self.config.extras["initial_price"]

        notifications = {}
        for player_id in player_ids:
            notifications[player_id] = {
                "data": {"avg_price": avg_price},
                "source_id": self.identity,
                "target_id": player_id,
                "step": round_num,
                "num_steps": 1,
                "metadata": {},
            }
        return notifications

    async def collect_responses(self, responses: List[Action]) -> None:
        """Collect price submissions from investors (response_pool)."""
        prices = []
        for response in responses:
            if response.action_type == "submit_price":
                price = response.payload["price"]
                prices.append(price)
                logger.debug(
                    "        Received from %s: %.2f", response.source_id, price
                )

        # Store response_pool data for analysis
        self._state.custom_state["prices"] = prices
        self._state.custom_state["response_count"] = len(responses)

    async def analyze(self) -> Dict[str, Any]:
        """Analyze the response_pool: calculate average price."""
        if "prices" not in self._state.custom_state:
            prices = []
        else:
            prices = self._state.custom_state["prices"]

        if prices:
            avg_price = sum(prices) / len(prices)
        else:
            avg_price = self.config.extras["initial_price"]

        logger.info("    Market avg: %.2f (from %d prices)", avg_price, len(prices))

        return {
            "avg_price": avg_price,
            "num_prices": len(prices),
            "prices": prices,
        }

    async def coordinate(self, analysis_result: Dict[str, Any]) -> CoordinationDecision:
        """Broadcast average price to all investors."""
        avg_price = analysis_result["avg_price"]

        # Store avg_price for next round's observations
        self._state.custom_state["avg_price"] = avg_price

        return CoordinationDecision(
            decision_type="price_broadcast",
            scope=DecisionScope.GLOBAL,
            parameters={
                "avg_price": avg_price,
            },
            source_id=self.identity,
            metadata={
                "cycle": self._state.cycle_count + 1,
                "num_prices": analysis_result["num_prices"],
            },
        )
