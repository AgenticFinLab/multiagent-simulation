"""Demo Players - Simple Investor Implementation

A simple investor that:
1. Receives average price from market
2. Updates local price: local_price += avg_price * random_factor
3. Submits new price to market
"""

import random
from typing import Any, Dict, Optional

from masim.player.base import (
    BasePlayer,
    Action,
    Observation,
    StepResult,
)


class SimpleInvestor(BasePlayer):
    """
    A simple investor that adjusts price based on market average.

    Each round:
    1. Receive market average price (observation)
    2. Update local price: local += avg * random(-0.1, 0.1)
    3. Submit new local price (action)
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        """Receive market average price."""
        avg_price = observation.data["avg_price"]
        self._state.set_custom("market_avg", avg_price)
        self._state.set_custom("round", observation.step)

    async def decide(self) -> Dict[str, Any]:
        """Update local price based on market average."""
        # Get current local price (must be initialized first round)
        if self._state.has_custom("local_price"):
            local_price = self._state.get_custom("local_price")
        else:
            local_price = self.config.extras["initial_price"]

        # Get market average (must be set in perceive)
        market_avg = self._state.get_custom("market_avg")

        # Update: local_price += avg_price * random_factor
        random_factor = random.uniform(-0.1, 0.1)
        new_price = local_price + market_avg * random_factor

        # Store updated price
        self._state.set_custom("local_price", new_price)

        return {
            "price": new_price,
            "random_factor": random_factor,
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        """Submit price to market."""
        return Action(
            action_type="submit_price",
            payload={
                "price": decision_payload["price"],
            },
            source_id=self.identity,
            metadata={
                "round": self._state.get_custom("round"),
                "random_factor": decision_payload["random_factor"],
            },
        )
