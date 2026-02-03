"""
This module defines the abstract BaseInvestor class along with configuration, decision, and status enums for building
market simulation agents.
"""

import asyncio
from typing import Any, List
from datetime import datetime

from llmgt.utils import record
from llmgt.communication.base import M2IMessage, I2MMessage
from llmgt.investor import base


class GeneralInvestor(base.BaseInvestor):
    """
    General implementation of BaseInvestor providing standard functionality.

    The GeneralInvestor is designed to be extended by specific investment
    strategy classes that implement the core decide() method with their
    particular decision-making algorithms.
    """

    def get_history_entry(self, round_id: int) -> Any:
        """
        Get historical data for a specified round.

        This method implements a two-tier storage system:
        1. First checks in-memory cache for recent entries.
        2. Falls back to disk storage for older entries not in memory.

        This approach optimizes for common access patterns where recent
        history is accessed frequently, while still providing access to
        the complete historical record when needed.
        """
        # Search in memory first
        entry = next(
            (item for item in self.history_entry if item.get("round_id") == round_id),
            None,
        )
        if entry:
            return entry["data"]

        # If not in memory, try to load from disk
        entry = record.load_record(
            self._storage_path,
            f"round_{round_id:06d}",
            file_format="json",
            from_block=True,
        )

        return entry.get("data") if entry else None

    def ready_for_decision(self, messages: List[M2IMessage]) -> bool:
        """
        Determine readiness for decision-making based on message availability.
        """
        return len(messages) > 0

    def on_markets_messages(
        self,
        messages: List[M2IMessage],
    ) -> List[M2IMessage]:
        """
        Process markets' messages before decision-making.
        """
        return messages

    def prior_decision(self, messages: List[M2IMessage]) -> Any:
        """
        Execute pre-decision setup and validation.
        """
        return messages

    async def decide(self, messages: List[M2IMessage]) -> base.InvestorDecision:
        """
        Simple decision implementation for framework validation.
        Returns a basic valid decision without complex logic.
        """
        # Record timing
        message_received_time = datetime.now().isoformat()

        strategy = self.investor_config.get("strategy", "balanced")
        if strategy == "conservative":
            sleep_time = 15
        elif strategy == "aggressive":
            sleep_time = 5
        else:
            sleep_time = 8

        await asyncio.sleep(sleep_time)

        decision_start_time = datetime.now().isoformat()

        # Build actions for each market
        actions = {}
        for message in messages:
            market_id = message.market_id
            decision_content = message.decision_content

            # Extract price based on message type
            if "current_price" in decision_content:
                # Round 1: Initial market state
                current_price = float(decision_content["current_price"])
            else:
                # Round 2+: Market decision with clearing price
                current_price = float(decision_content["clearing"]["price"])

            actions[market_id] = {"price": current_price}

        self._round_index += 1

        # Simple decision: just return current price
        decision = base.InvestorDecision(
            action=actions,
            reason="Simple price matching for framework validation",
            confidence=1.0,
            violations={},
            round_index=self._round_index,
            message_received_time=message_received_time,
            decision_start_time=decision_start_time,
        )

        decision.ensure_valid()
        return decision

    def post_decision(
        self,
        messages: List[M2IMessage],
        decision: base.InvestorDecision,
    ) -> base.InvestorDecision:
        """
        Handle post-decision processing and persistence.
        """

        return decision

    def build_i2m_message(
        self,
        messages: List[M2IMessage],
        decision: base.InvestorDecision,
    ) -> List[I2MMessage]:
        """
        Construct the message to send back to the market system.
        """
        messages = []
        for market_id, action in decision.action.items():
            # Create a new decision for this specific market
            market_decision = base.InvestorDecision(
                action=action,
                reason=decision.reason,
                confidence=decision.confidence,
                violations=decision.violations,
                round_index=decision.round_index,
                message_received_time=decision.message_received_time,
                decision_start_time=decision.decision_start_time,
                additions=decision.additions,
            )

            messages.append(
                I2MMessage(
                    investor_id=self.identity,
                    market_id=market_id,
                    decision_content=market_decision,
                    additions={},
                )
            )
        return messages
