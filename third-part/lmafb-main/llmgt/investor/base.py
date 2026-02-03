"""
Define the abstract BaseInvestor class along with configuration, decision, and status enums for building various market
mechanisms.
"""

from pathlib import Path
from collections import deque
from datetime import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List

from projinit.config import Config
from llmgt.utils.status import InvestorStatus
from llmgt.communication.base import M2IMessage, I2MMessage


@dataclass
class BaseInvestorConfig:
    """
    General implementation of BaseInvestor providing standard functionality.

    This class serves as a middle-layer implementation that provides common
    infrastructure and default behaviors for investor agents.
    It handles:
    - Historical data management (both memory and disk storage)
    - Basic message processing
    - Decision persistence
    - Standard message construction

    The GeneralInvestor is designed to be extended by specific investment
    strategy classes that implement the core decide() method with their
    particular decision-making algorithms.
    """

    identity: str
    extras: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InvestorDecision:
    """
    The decision content of the Investor.
    """

    # use 'action' to represent all investors' decisions not only to price (though now is),
    # but also given to the variables (supply_change, advertising_budget, etc.)
    action: Dict[str, Any]
    reason: str
    # When making final decisions, the market end can refer to the confidence of each investor.
    confidence: Optional[float] = None
    # Record which business/rule constraints were violated in this decision-making process to facilitate the design
    # of a penalty mechanism.
    violations: Dict[str, Any] = field(default_factory=dict)
    # Mark this as the nth round of decision-making (round number)
    round_index: Optional[int] = None

    message_received_time: Optional[str] = None
    decision_start_time: Optional[str] = None

    # Generate timestamps for decision objects. Know the decision time during debugging and replay.
    # Convenient for timing analysis (response delay, batch synchronization status).
    default_factory = lambda: datetime.now().isoformat()

    additions: Dict[str, Any] = field(default_factory=dict)

    def ensure_valid(self):
        """
        Perform minimal validity checks to ensure that the required fields in the decision structure exist.
        """
        if not self.action:
            raise ValueError("InvestorDecision.action must contain 'price' key")
        if 'price' in self.action:
            # Single market format: {'price': ...}
            pass
        else:
            # Multi-market format: {market_id: {'price': ...}, ...}
            pass


class BaseInvestor(ABC):
    """
    The abstract base class for all investors.

    This class serves as a middle-layer implementation that provides common
    infrastructure and default behaviors for investor agents.
    It handles:
    - Historical data management (both memory and disk storage)
    - Basic message processing
    - Decision persistence
    - Standard message construction
    """

    def __init__(self, config: BaseInvestorConfig, market_ids: List[str]):
        """
        Initialize base-investor.
        """
        # Simulation Identity
        # This is assigned from the ID sent by the simulator
        self.simulation_id = None
        # Identity and config of the investor
        self.identity = config.identity
        self.investor_config = config.extras

        # Markets that the investor belongs to
        self.market_ids = market_ids

        # Operation status of the investor
        self.receive_status = InvestorStatus.NO_RECEIVED
        self.running_status = InvestorStatus.RUNNING
        self.alert_status = InvestorStatus.NONE

        # Round information
        self._round_index: int = 0
        self.entry_limit = config.extras["entry_limit"]
        self.history_entry = deque(maxlen=self.entry_limit)
        self._storage_path = (
            Path(Config.logging.logging_path) / "investors" / self.identity
        )
        self._storage_path.mkdir(parents=True, exist_ok=True)

    def get_history_entry(self, entry_id: int) -> Any:
        """
        Get historical data for a specified round.
        """
        raise NotImplementedError

    @abstractmethod
    def ready_for_decision(self, messages: List[M2IMessage]) -> bool:
        """
        Determine readiness for decision-making based on message availability.

        As a general implementation uses a simple heuristic:
        if any messages are available, the investor is ready to make a decision.

        This works well for basic scenarios but can be overridden by subclasses
        that need more sophisticated readiness logic.
        """
        raise NotImplementedError

    @abstractmethod
    def on_markets_messages(
        self,
        messages: List[M2IMessage],
    ) -> List[M2IMessage]:
        """
        Process markets' messages before decision-making.

        This general implementation performs no transformation on the messages,
        simply passing them through unchanged.

        This is appropriate for basic investors that can work directly with raw market data.
        """
        raise NotImplementedError

    @abstractmethod
    def prior_decision(self, messages: List[M2IMessage]) -> Any:
        """
        Execute pre-decision setup and validation.

        This general implementation performs no additional processing,
        making it suitable for simple investors that don't require
        special setup before making decisions.
        """
        raise NotImplementedError

    @abstractmethod
    async def decide(self, messages: List[M2IMessage]) -> InvestorDecision:
        """
        Async decision step which allows concurrency and external APIs.

        This method is intentionally left abstract in GeneralInvestor because
        decision-making logic is highly specific to the investment strategy
        being implemented.

        Strategy implementations should analyze the provided messages and
        return a complete InvestorDecision object with:
        - action dictionary (must include 'price' key)
        - reasoning explanation
        - confidence level (optional)
        - any constraint violations
        """
        raise NotImplementedError

    @abstractmethod
    def post_decision(
        self,
        messages: List[M2IMessage],
        decision: InvestorDecision,
    ) -> InvestorDecision:
        """
        Process the decision after it has been made.

        This method manages the storage of decision history using a dual-storage
        approach for optimal performance and complete historical preservation:

        1. Persistent Storage: Saves complete decision record to disk as JSON
           - Ensures no data loss across system restarts
           - Enables long-term analysis and replay
           - Uses zero-padded filenames for proper chronological ordering

        2. Memory Cache: Maintains recent decisions in a circular buffer
           - Provides fast access to recent history
           - Automatically manages memory usage via maxlen
           - Supports quick lookups for decision context
        """
        raise NotImplementedError

    @abstractmethod
    def build_i2m_message(
        self,
        messages: List[M2IMessage],
        decision: InvestorDecision,
    ) -> List[I2MMessage]:
        """
        Create the single I2MMessage sent from the investor to the market.

        This method creates a standard I2MMessage that packages the investor's decision
        in the format expected by the market simulation system.

        The message includes:
        - investor_id: Identifies which investor made this decision
        - decision_content: The complete InvestorDecision object
        - additions: Empty dict for extensibility (can be used by subclasses)

        This standard format ensures compatibility with the market system
        while allowing for future extensions through the additions field.
        """
        raise NotImplementedError
