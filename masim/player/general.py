"""
General Player Implementation for MASim Framework.

This module provides ready-to-use Player implementations that extend BasePlayer.
Use GeneralPlayer as:
    1. A starting point for quick prototyping
    2. A reference implementation showing how to extend BasePlayer
    3. A base class for domain-specific players

For abstract definitions and documentation, see base.py.
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from masim.player.base import (
    BasePlayer,
    PlayerConfig,
    Action,
    Observation,
    PayloadType,
    StepResult,
)

if TYPE_CHECKING:
    pass


# =============================================================================
#                          GENERAL PLAYER
# =============================================================================


class GeneralPlayer(BasePlayer):
    """
    Ready-to-use Player implementation with sensible defaults.

    GeneralPlayer provides a minimal but complete implementation of the
    perceive → decide → act cycle. It can be:

    1. Used directly for testing and prototyping
    2. Extended for domain-specific behavior

    Default Behavior:
    -----------------
    - perceive(): Stores observation in custom_state["last_observation"]
    - decide(): Returns the observation data as-is
    - act(): Creates an Action with type "default" and the decision payload

    Extension Guide:
    ----------------
    Override any or all of the three methods:

        class MyPlayer(GeneralPlayer):
            async def decide(self) -> Dict[str, Any]:
                obs = self.state.get_custom("last_observation")
                # Custom decision logic
                return {"my_action": "do_something", "data": obs}

    Example Usage:
    --------------
        # Quick prototyping
        config = PlayerConfig(identity="player_001", name="Test Player")
        player = GeneralPlayer(config)
        await player.initialize()

        obs = Observation(
            local=LocalObservation(data={"price": 100.0}),
            conductor_notify={"phase": "trading"},
            round=1,
        )
        result = await player.step(obs)
        # result.action.action_type == "default"
        # result.action.payload == {"price": 100.0}
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional["StepResult"] = None,
    ) -> None:
        """
        Process incoming observation and update internal state.

        Default implementation stores the observation for later access
        in decide().

        Args:
            observation: The current observation from environment
            prev_result: Result from the previous step (for multi-step turns)
        """
        # Store observation for access in decide()
        self.state.set_custom("last_observation", observation.data)

        # Store previous action if available
        if prev_result and prev_result.action:
            self.state.set_custom("prev_action", prev_result.action)

    async def decide(self) -> PayloadType:
        """
        Make a decision based on current state.

        Default implementation returns the last observation data as-is.
        Override this method to implement custom decision logic.

        Returns:
            Decision payload (passed to act())
        """
        # Default: pass through observation data
        return self.state.get_custom("last_observation")

    async def act(self, decision_payload: PayloadType) -> Action:
        """
        Transform decision into an Action.

        Default implementation creates an Action with type "default"
        containing the decision payload.

        Args:
            decision_payload: Output from decide()

        Returns:
            Action object to be executed by environment
        """
        return Action(
            action_type="default",
            payload=(
                decision_payload
                if isinstance(decision_payload, dict)
                else {"data": decision_payload}
            ),
            source_id=self.identity,
        )


# =============================================================================
#                       SPECIALIZED PLAYERS
# =============================================================================


class EchoPlayer(GeneralPlayer):
    """
    A Player that echoes back observations with minimal processing.

    Useful for testing message flow and observing raw data.
    """

    async def act(self, decision_payload: PayloadType) -> Action:
        """Create an echo action with observation data."""
        return Action(
            action_type="echo",
            payload={"echoed_data": decision_payload},
            source_id=self.identity,
            metadata={"player_name": self.name},
        )


class NoOpPlayer(GeneralPlayer):
    """
    A Player that takes no action (returns empty actions).

    Useful for placeholder players or testing.
    """

    async def decide(self) -> PayloadType:
        """Always decide to do nothing."""
        return {"noop": True}

    async def act(self, decision_payload: PayloadType) -> Action:
        """Create a no-op action."""
        return Action(
            action_type="noop",
            payload={},
            source_id=self.identity,
        )


class ReactivePlayer(GeneralPlayer):
    """
    A Player that reacts based on observation triggers.

    Subclass and override should_react() and create_reaction() for
    domain-specific reactive behavior.

    Example:
        class PriceReactivePlayer(ReactivePlayer):
            def should_react(self, observation: Dict) -> bool:
                return observation["price"] > 100

            def create_reaction(self, observation: Dict) -> Dict:
                return {"action": "sell", "reason": "price_threshold"}
    """

    async def decide(self) -> PayloadType:
        """Decide based on reactive triggers."""
        obs = self.state.get_custom("last_observation")

        if self.should_react(obs):
            return self.create_reaction(obs)
        return self.create_default_response(obs)

    def should_react(self, observation: Dict[str, Any]) -> bool:
        """
        Determine if a reaction is needed.

        Override this method to define reaction triggers.

        Args:
            observation: Current observation data

        Returns:
            True if should react, False otherwise
        """
        # Default: never react
        return False

    def create_reaction(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a reaction payload when triggered.

        Override this method to define reaction behavior.

        Args:
            observation: Current observation data

        Returns:
            Reaction payload
        """
        return {"reaction": True, "triggered_by": observation}

    def create_default_response(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create default response when not reacting.

        Args:
            observation: Current observation data

        Returns:
            Default response payload
        """
        return {"reaction": False, "hold": True}
