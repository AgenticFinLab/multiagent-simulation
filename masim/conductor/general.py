"""
General Conductor Implementation for MASim Framework.

This module provides ready-to-use Conductor implementations that extend BaseConductor.
Use GeneralConductor as:
    1. A starting point for quick prototyping
    2. A reference implementation showing how to extend BaseConductor
    3. A base class for domain-specific conductors

Conductor Contract:
- notify(): Send round state to Players (Conductor → Players)
- collect_census(): Gather actions from Players (Players → Conductor)
- analyze(): Process the collected census
- coordinate(): Produce CoordinationDecision

For abstract definitions and documentation, see base.py.
"""

from typing import Any, Dict, List, Optional

from masim.player.base import Action
from masim.conductor.base import (
    BaseConductor,
    ConductorConfig,
    CoordinationDecision,
    DecisionScope,
)


# =============================================================================
#                         GENERAL CONDUCTOR
# =============================================================================


class GeneralConductor(BaseConductor):
    """
    Ready-to-use Conductor implementation with sensible defaults.

    GeneralConductor provides a minimal but complete implementation of the
    notify → collect_census → analyze → coordinate cycle. It can be:

    1. Used directly for testing and prototyping
    2. Extended for domain-specific coordination

    Default Behavior:
    -----------------
    - notify(): Broadcasts same data to all players
    - collect_census(): Stores census in custom_state["census"]
    - analyze(): Counts actions and computes basic statistics
    - coordinate(): Returns a global "continue" decision

    Extension Guide:
    ----------------
    Override any or all of the four methods:

        class MyMarketConductor(GeneralConductor):
            async def analyze(self) -> Dict[str, Any]:
                census = self._state.custom_state["census"]
                # Custom analysis logic
                buy_volume = sum(a.payload["qty"]
                                 for a in census if a.action_type == "buy")
                return {"buy_volume": buy_volume, "census_size": len(census)}

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

        # Buffer some actions (builds census)
        conductor.on_action_received(action1)
        conductor.on_action_received(action2)

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
        if "broadcast_data" in self._state.custom_state:
            data = self._state.custom_state["broadcast_data"]
        else:
            data = {"round": round_num}

        notifications = {}
        for player_id in player_ids:
            notifications[player_id] = {
                "data": data,
                "source_id": self.identity,
                "target_id": player_id,
                "step": round_num,
                "num_steps": 1,
                "metadata": {},
            }
        return notifications

    async def collect_census(self, actions: List[Action]) -> None:
        """
        Collect census from player actions (Players → Conductor).

        Default implementation stores census for analysis.

        Args:
            actions: List of Actions collected from Players (the census)
        """
        # Store census for analysis
        self._state.custom_state["census"] = actions

    async def analyze(self) -> Dict[str, Any]:
        """
        Analyze the collected census and system state.

        Default implementation computes basic statistics:
        - census_size: Number of actions in the census
        - action_types: Distribution of action types
        - player_count: Number of registered players

        Returns:
            Analysis result dictionary
        """
        if "census" not in self._state.custom_state:
            census = []
        else:
            census = self._state.custom_state["census"]

        # Count action types
        type_counts: Dict[str, int] = {}
        for action in census:
            action_type = action.action_type
            if action_type in type_counts:
                type_counts[action_type] += 1
            else:
                type_counts[action_type] = 1

        return {
            "census_size": len(census),
            "action_types": type_counts,
            "player_count": len(self._state.player_registry),
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
                "census_size": analysis_result["census_size"],
                "timestamp": self._state.cycle_count,
            },
            source_id=self.identity,
        )


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
        """Apply throttling based on census size."""
        census_size = analysis_result["census_size"]

        if census_size > self._high_threshold:
            return CoordinationDecision(
                decision_type="throttle",
                scope=DecisionScope.GLOBAL,
                parameters={
                    "rate_multiplier": 0.5,
                    "reason": "high_activity",
                    "census_size": census_size,
                },
                source_id=self.identity,
            )
        elif census_size < self._low_threshold:
            return CoordinationDecision(
                decision_type="accelerate",
                scope=DecisionScope.GLOBAL,
                parameters={
                    "rate_multiplier": 1.5,
                    "reason": "low_activity",
                    "census_size": census_size,
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
