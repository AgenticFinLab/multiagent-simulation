"""
Define the abstract BaseMarket class along with configuration, decision, and status enums for building various market
mechanisms.
"""

from pathlib import Path
from datetime import datetime
from collections import deque
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field

from projinit.config import Config
from llmgt.utils.status import MarketStatus
from llmgt.communication.base import I2MMessage, M2IMessage


@dataclass
class BaseMarketConfig:
    """
    Basic config for the market.
    """

    identity: str
    extras: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MarketDecision:
    """
    The decision content of the Market.
    """

    reason: str
    # Market clearing results, i.e., core market outputs (prices, trading volumes, etc.) for this round
    clearing: Dict[str, Any] = field(default_factory=dict)
    # Allocation results for each investor (shares, quantity, etc.)
    allocations: Dict[str, Any] = field(default_factory=dict)
    # Penalties or price adjustments for specific investors (typically used to curb misconduct)
    penalties: Dict[str, Any] = field(default_factory=dict)
    # Market alignment score measuring the consistency between market decision and investor strategies
    # Range: [0.0, 1.0] where:
    # - 1.0: Perfect alignment - all investor strategies are consistent with market clearing price/mechanism
    # - 0.5: Moderate alignment - mixed consistency across investors
    # - 0.0: No alignment - investor strategies conflict significantly with market outcome
    # This metric helps evaluate market efficiency and participant behavior coherence
    market_alignment: float = 0.0
    # Mark this as the nth round of decision-making (round number)
    round_index: Optional[int] = None

    message_received_time: Optional[str] = None
    decision_start_time: Optional[str] = None

    # Generate timestamps for decision objects. Know the decision time during debugging and replay.
    start_time_stamp: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time_stamp: str = field(default_factory=lambda: datetime.now().isoformat())
    additions: Dict[str, Any] = field(default_factory=dict)

    def ensure_valid(self):
        """
        Perform minimal validity checks to ensure that the required fields in the decision structure exist.
        """
        if "price" not in self.clearing:
            raise ValueError("MarketDecision.clearing must contain 'price' key")


class BaseMarket(ABC):
    """
    The abstract base class for all market simulations.

    This class serves as a middle-layer implementation that provides common
    infrastructure and default behaviors for market mechanisms. It handles:
    - Historical clearing data management (both memory and disk storage)
    - Basic message processing from investors
    - Market decision persistence
    - Standard message construction to investors
    """

    def __init__(self, config: BaseMarketConfig, investor_ids: List[str]):
        """
        Initialize base-market.

        This class serves as a middle-layer implementation that provides common
        infrastructure and default behaviors for market mechanisms. It handles:
        - Historical clearing data management (both memory and disk storage)
        - Basic message processing from investors
        - Market decision persistence
        - Standard message construction to investors
        """
        # Simulation Identity
        # This is assigned from the ID sent by the simulator
        self.simulation_id = None

        # Identity and config of the market
        self.identity = config.identity
        self.market_config = config.extras

        # Investors that the market serves
        self.investor_ids = investor_ids

        # Operation status of the market
        self.receive_status = MarketStatus.NO_RECEIVED
        self.running_status = MarketStatus.RUNNING
        self.alert_status = MarketStatus.NONE

        # Time notification
        # The message received time of each investor
        # investor_id: time
        self.messages_received_time = {}
        self.decision_start_time = None
        self._round_index: int = 0
        self.entry_limit = config.extras["entry_limit"]
        self.history_entry = deque(maxlen=self.entry_limit)
        self._storage_path = (
            Path(Config.logging.logging_path) / "markets" / self.identity
        )
        self._storage_path.mkdir(parents=True, exist_ok=True)

    def get_history_entry(self, round_id: int) -> Any:
        """
        Get historical market clearing data for a specified round with intelligent caching.

        This method implements a two-tier storage system:
        1. First checks in-memory cache (deque) for recent entries
        2. Falls back to disk storage for older entries not in memory

        This approach optimizes for common access patterns where recent
        market history is accessed frequently for trend analysis and decision-making,
        while still providing access to the complete historical record when needed.
        """
        raise NotImplementedError

    def build_initial_m2i_messages(self, round_id: int) -> List[M2IMessage]:
        """
        Build the initial market message at the starting of the simulation for investors.
        """
        raise NotImplementedError

    @abstractmethod
    def ready_for_decision(self, messages: List[I2MMessage]) -> bool:
        """
        Determine readiness for market clearing based on investor message availability.

        This general implementation uses a simple heuristic: if any investor messages
        are available, the market is ready to clear.

        This works well for basic scenarios but can be overridden by subclasses that need more sophisticated
        readiness logic.
        """
        raise NotImplementedError

    @abstractmethod
    def on_investors_messages(
        self,
        messages: List[I2MMessage],
    ) -> List[I2MMessage]:
        """
        Preprocess the messages from investors to enable a decision after-wards.

        This general implementation performs no transformation on the messages,
        simply passing them through unchanged. This is appropriate for basic
        markets that can work directly with raw investor submissions.
        """
        raise NotImplementedError

    @abstractmethod
    def prior_decision(self, messages: List[I2MMessage]) -> Any:
        """
        Execute pre-clearing setup and validation.

        This general implementation performs no additional processing,
        making it suitable for simple markets that don't require
        special setup before clearing.
        """
        raise NotImplementedError

    @abstractmethod
    async def decide(self, messages: List[I2MMessage]) -> MarketDecision:
        """
        This method is intentionally left abstract in GeneralMarket because
        clearing logic is highly specific to the market mechanism being
        implemented.

        Mechanism implementations should analyze the provided investor messages and
        return a complete MarketDecision object with:
        - clearing dictionary (must include 'price' key)
        - allocations for each participating investor
        - penalties for rule violations (if any)
        - market alignment score
        - detailed reasoning explanation
        """
        raise NotImplementedError

    @abstractmethod
    def post_decision(
        self,
        messages: List[I2MMessage],
        decision: MarketDecision,
    ) -> MarketDecision:
        """
        Handle post-clearing processing and persistence.

        This method manages the storage of clearing history using a dual-storage
        approach for optimal performance and complete historical preservation:

        1. Persistent Storage: Saves complete clearing record to disk as JSON
           - Ensures no data loss across system restarts
           - Enables long-term market analysis and replay
           - Uses zero-padded filenames for proper chronological ordering

        2. Memory Cache: Maintains recent clearing decisions in a circular buffer
           - Provides fast access to recent market history
           - Automatically manages memory usage via maxlen
           - Supports quick lookups for trend analysis and decision context
        """
        raise NotImplementedError

    def build_m2i_message(
        self,
        messages: List[I2MMessage],
        decision: MarketDecision,
    ) -> M2IMessage:
        """
        Construct the message to send back to the investor system.

        This method creates a standard M2IMessage (Market-to-Investor message)
        that packages the market's clearing decision in the format expected by
        investors in the simulation system.
        """
        raise NotImplementedError
