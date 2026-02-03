"""
This module implements the GeneralMarket class, a concrete implementation of BaseMarket
that provides standard functionality for basic market mechanisms in simulations.
"""

from typing import Any, List
from datetime import datetime

from llmgt.utils import record
from llmgt.communication.base import I2MMessage, M2IMessage
from llmgt.market import base


class GeneralMarket(base.BaseMarket):
    """
    General implementation of BaseMarket providing standard functionality.

    The GeneralMarket is designed to be extended by specific market mechanism
    classes that implement the core decide() method with their particular
    clearing algorithms (e.g., Dutch auction, continuous double auction, etc.).
    """

    def get_history_entry(self, round_id: int) -> Any:
        """
        Get historical market clearing data for a specified round with intelligent caching.
        """
        # Search in memory first
        # This covers the most common case of accessing recent clearing history
        entry = next(
            (item for item in self.history_entry if item.get("round_id") == round_id),
            None,
        )
        if entry:
            return entry["data"]

        # If not found in memory, attempt to load from persistent disk storage
        # This handles access to older clearing data beyond the memory limit
        entry = record.load_record(
            self._storage_path,
            f"round_{round_id:06d}",
            file_format="json",
            from_block=True,
        )

        # Return the data portion of the loaded record, or None if not found
        return entry.get("data") if entry else None

    def build_initial_m2i_messages(self, round_id: int) -> List[M2IMessage]:
        """
        Build initial M2I messages for ALL participating investors.
        """
        if round_id == 1:
            # Initial state
            decision_content = {
                "current_price": self.market_config.get("initial_price", 100.0),
                "round_index": 0,
                "volatility": self.market_config.get("price_volatility", 0.15),
                "price_history": [self.market_config.get("initial_price", 100.0)],
            }
        else:
            # Get last decision from history
            last_entry = self.history_entry[-1]
            decision_content = last_entry["data"]["decision"]

        messages = []
        for investor_id in self.investor_ids:
            msg = M2IMessage(
                market_id=self.identity,
                investor_id=investor_id,
                decision_content=decision_content,
                rule="Market state",
            )
            messages.append(msg)

        return messages

    def ready_for_decision(self, messages: List[I2MMessage]) -> bool:
        """
        Determine readiness for market clearing based on investor message availability.
        """
        # Simple strategy: ready if we have any investor messages at all
        return len(messages) > 0

    def on_investors_messages(
        self,
        messages: List[I2MMessage],
    ) -> List[I2MMessage]:
        """
        Preprocess the messages from investors to enable a decision after-wards
        """
        # xxxx
        return messages

    def prior_decision(self, messages: List[I2MMessage]) -> Any:
        """
        Execute pre-clearing setup and validation.
        """
        return messages

    async def decide(self, messages: List[I2MMessage]) -> base.MarketDecision:
        """
        Simple market clearing implementation for framework validation.
        Returns basic clearing results without complex algorithms.
        """
        message_received_time = datetime.now().isoformat()

        decision_start_time = datetime.now().isoformat()

        # Extract prices from investor messages
        bids = []
        for msg in messages:
            if hasattr(msg, "decision_content") and isinstance(
                msg.decision_content, dict
            ):
                if "action" in msg.decision_content:
                    action = msg.decision_content["action"]
                    if isinstance(action, dict) and "price" in action:
                        bids.append(float(action["price"]))

        # Simple clearing: average price
        clearing_price = sum(bids) / len(bids) if bids else 100.0

        # Simple allocations: everyone gets 1 share
        allocations = {
            investor_id: {"shares": 1, "allocation_price": clearing_price}
            for investor_id in self.investor_ids
        }

        self._round_index += 1

        decision = base.MarketDecision(
            reason=f"Simple averaging of {len(bids)} bids for framework validation",
            clearing={"price": clearing_price, "volume": len(bids)},
            allocations=allocations,
            penalties={},
            market_alignment=1.0,
            round_index=self._round_index,
            message_received_time=message_received_time,
            decision_start_time=decision_start_time,
        )

        decision.ensure_valid()
        return decision

    def post_decision(
        self,
        messages: List[I2MMessage],
        decision: base.MarketDecision,
    ) -> base.MarketDecision:
        """
        Handle post-clearing processing and persistence.
        """

        return decision

    def build_m2i_message(
        self,
        messages: List[I2MMessage],
        decision: base.MarketDecision,
    ) -> M2IMessage:
        """
        Construct the message to send back to the investor system.
        """
        return M2IMessage(
            market_id=self.identity,
            investor_id=None,
            decision_content=decision,
            additions={},
        )
