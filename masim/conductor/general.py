"""
General Conductor Implementation for MASim Framework.

This module provides ready-to-use Conductor implementations that extend BaseConductor.
Use GeneralConductor as:
    1. A starting point for quick prototyping
    2. A reference implementation showing how to extend BaseConductor
    3. A base class for domain-specific conductors

Conductor Contract:
- notify(): Send round state to Players (Conductor → Players)
- analyze(responses): Process responses from Players
- coordinate(): Produce CoordinationDecision

For abstract definitions and documentation, see base.py.
"""

from typing import Any, Dict, List, Optional

from masim.player.base import Action
from masim.conductor.base import (
    BaseConductor,
    ConductorConfig,
    CoordinationDecision,
    CycleResult,
    DecisionScope,
)


# =============================================================================
#                         GENERAL CONDUCTOR
# =============================================================================


class GeneralConductor(BaseConductor):
    """
    Ready-to-use Conductor implementation with sensible defaults.

    GeneralConductor provides a minimal but complete implementation of the
    notify → analyze → coordinate cycle. It can be:

    1. Used directly for testing and prototyping
    2. Extended for domain-specific coordination

    Default Behavior:
    -----------------
    - notify(): Broadcasts same data to all players
    - analyze(): Receives responses directly, computes basic statistics
    - coordinate(): Returns a global "continue" decision

    Extension Guide:
    ----------------
    Override any or all of the four methods:

        class MyMarketConductor(GeneralConductor):
            async def analyze(self, responses: List[Action]) -> Dict[str, Any]:
                # Custom analysis logic
                buy_volume = sum(a.payload["qty"]
                                 for a in responses if a.action_type == "buy")
                return {"buy_volume": buy_volume, "response_count": len(responses)}

            async def coordinate(self, analysis: Dict) -> CoordinationDecision:
                if analysis["buy_volume"] > 1000:
                    return CoordinationDecision(
                        decision_type="throttle",
                        scope=DecisionScope.GLOBAL,
                        parameters={"rate_limit": 0.5},
                        source_id=self.identity
                    )
                return await super().coordinate(analysis)

    Example Usage:
    --------------
        config = ConductorConfig(identity="conductor_001")
        conductor = GeneralConductor(config)
        await conductor.initialize()

        # Buffer some responses (builds response_pool)
        conductor.on_response_received(action1)
        conductor.on_response_received(action2)

        # Run coordination cycle
        result = await conductor.cycle()
        # result.decision.decision_type == "continue"
    """

    def notify(
        self,
        round_num: int,
        player_ids: List[str],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Notify players of round state (Conductor → Players).

        Default implementation broadcasts the same data to all players.
        Override this method to implement custom notification
        (e.g., private information, asymmetric notifications)

        Args:
            round_num: Current simulation round
            player_ids: List of player IDs to notify

        Returns:
            Dict of player_id -> notification_dict
        """
        # Get broadcast data from coordinator state
        if "broadcast_data" in self.state.custom_state:
            data = self.state.custom_state["broadcast_data"]
        else:
            data = {"round": round_num}

        notifications = {}
        for player_id in player_ids:
            notifications[player_id] = {
                "data": data,
                "source_id": self.identity,
                "target_id": player_id,
                "round": round_num,
                "num_steps": 1,
                "metadata": {},
            }
        return notifications

    async def analyze(self, responses: List[Action]) -> Dict[str, Any]:
        """
        Analyze responses and system state.

        Default implementation computes basic statistics:
        - response_count: Number of responses received
        - action_types: Distribution of action types
        - player_count: Number of registered players

        Args:
            responses: List of responses (Actions) from Players

        Returns:
            Analysis result dictionary
        """
        # Count action types
        type_counts: Dict[str, int] = {}
        for action in responses:
            action_type = action.action_type
            if action_type in type_counts:
                type_counts[action_type] += 1
            else:
                type_counts[action_type] = 1

        return {
            "response_count": len(responses),
            "action_types": type_counts,
            "player_count": len(self.state.player_registry),
        }

    async def coordinate(self, analysis_result: Dict[str, Any]) -> CoordinationDecision:
        """
        Generate a CoordinationDecision based on analysis.

        Default implementation returns a "continue" decision indicating
        normal operation should proceed.

        Args:
            analysis_result: Output from analyze()

        Returns:
            CoordinationDecision for the system
        """
        return CoordinationDecision(
            decision_type="continue",
            scope=DecisionScope.GLOBAL,
            parameters={
                "response_count": analysis_result["response_count"],
                "timestamp": self.state.cycle_count,
            },
            source_id=self.identity,
        )

    def prepare_broadcast(self, cycle_result: CycleResult) -> Dict[str, Any]:
        """
        Prepare the broadcast message from cycle result.

        Default implementation sends the decision as a dict.
        Override to customize what Players receive.

        Args:
            cycle_result: The complete CycleResult from cycle()

        Returns:
            Dict to be sent to each Player
        """
        return cycle_result.decision.to_dict() if cycle_result.decision else {}


# =============================================================================
#                      SPECIALIZED CONDUCTORS
# =============================================================================


class PassThroughConductor(GeneralConductor):
    """
    A Conductor that passes through without coordination.

    Useful for scenarios where players should operate autonomously
    without central coordination.
    """

    async def coordinate(self, analysis_result: Dict[str, Any]) -> CoordinationDecision:
        """Always return a no-op coordination decision."""
        return CoordinationDecision(
            decision_type="passthrough",
            scope=DecisionScope.GLOBAL,
            parameters={"mode": "autonomous"},
            source_id=self.identity,
        )


class ThrottlingConductor(GeneralConductor):
    """
    A Conductor that applies throttling based on activity levels.

    Configurable thresholds for action rate limiting.
    Requires 'high_threshold' and 'low_threshold' in config.extras.
    """

    def __init__(self, config: ConductorConfig):
        super().__init__(config)
        self._high_threshold = config.extras["high_threshold"]
        self._low_threshold = config.extras["low_threshold"]

    async def coordinate(self, analysis_result: Dict[str, Any]) -> CoordinationDecision:
        """Apply throttling based on response count."""
        response_count = analysis_result["response_count"]

        if response_count > self._high_threshold:
            return CoordinationDecision(
                decision_type="throttle",
                scope=DecisionScope.GLOBAL,
                parameters={
                    "rate_multiplier": 0.5,
                    "reason": "high_activity",
                    "response_count": response_count,
                },
                source_id=self.identity,
            )
        elif response_count < self._low_threshold:
            return CoordinationDecision(
                decision_type="accelerate",
                scope=DecisionScope.GLOBAL,
                parameters={
                    "rate_multiplier": 1.5,
                    "reason": "low_activity",
                    "response_count": response_count,
                },
                source_id=self.identity,
            )

        return await super().coordinate(analysis_result)


class BroadcastConductor(GeneralConductor):
    """
    A Conductor that broadcasts coordination decisions to all players.

    Useful for scenarios requiring synchronized player behavior.
    """

    async def coordinate(self, analysis_result: Dict[str, Any]) -> CoordinationDecision:
        """Create a broadcast decision with analysis summary."""
        return CoordinationDecision(
            decision_type="broadcast",
            scope=DecisionScope.GLOBAL,
            parameters={
                "message": "system_update",
                "analysis_summary": analysis_result,
            },
            source_id=self.identity,
        )
