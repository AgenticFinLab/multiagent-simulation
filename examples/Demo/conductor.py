"""Demo Conductor - Simple Market Implementation

A simple market that:
1. Notifies investors with current market state
2. Collects price submissions from all investors (response_pool)
3. Calculates the average price
4. Broadcasts the average back to all investors

Conductor Contract:
- notify(): Send round state to Players (Conductor → Players)
- analyze(responses): Process responses from Players
- coordinate(): Produce CoordinationDecision
"""

import logging
from typing import Any, Dict, List

from masim.conductor.base import (
    BaseConductor,
    CoordinationDecision,
    CycleResult,
    DecisionScope,
)
from masim.player.base import Action

logger = logging.getLogger("Demo")


class SimpleMarket(BaseConductor):
    """
    A simple market that calculates average price from all investors.

    Each round:
    1. notify(): Broadcast current avg_price to investors
    2. analyze(responses): Calculate new average price from submissions
    3. coordinate(): Store new average for next round
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
        if "avg_price" in self.state.custom_state:
            avg_price = self.state.custom_state["avg_price"]
        else:
            avg_price = self.config.extras["initial_price"]

        notifications = {}
        for player_id in player_ids:
            notifications[player_id] = {
                "data": {"avg_price": avg_price},
                "source_id": self.identity,
                "target_id": player_id,
                "round": round_num,
                "num_steps": 1,
                "metadata": {},
            }
        return notifications

    async def analyze(self, responses: List[Action]) -> Dict[str, Any]:
        """Analyze responses: calculate average price from submissions."""
        prices = []
        for response in responses:
            if response.action_type == "submit_price":
                price = response.payload["price"]
                prices.append(price)
                logger.debug(
                    "        Received from %s: %.2f", response.source_id, price
                )

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
        self.state.custom_state["avg_price"] = avg_price

        return CoordinationDecision(
            decision_type="price_broadcast",
            scope=DecisionScope.GLOBAL,
            parameters={
                "avg_price": avg_price,
            },
            source_id=self.identity,
            metadata={
                "cycle": self.state.cycle_count + 1,
                "num_prices": analysis_result["num_prices"],
            },
        )

    def prepare_broadcast(self, cycle_result: CycleResult) -> Dict[str, Any]:
        """
        Prepare broadcast message for investors.

        Send avg_price in a simple dict for investors to process.
        """
        if cycle_result.decision:
            return {"avg_price": cycle_result.decision.parameters.get("avg_price")}
        return {}
