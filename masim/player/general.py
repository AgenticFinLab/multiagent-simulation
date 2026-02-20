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
    Action,
    Observation,
    LocalObservation,
    PayloadType,
    StepResult,
    TurnResult,
    Outbound,
)

if TYPE_CHECKING:
    from masim.communication.base import Message


# =============================================================================
#                          GENERAL PLAYER
# =============================================================================


class GeneralPlayer(BasePlayer):
    """
    Ready-to-use Player implementation with sensible defaults.

    GeneralPlayer provides a complete implementation of the Player lifecycle
    including initialization, step/turn execution, message handling, and
    state management. It can be:

    1. Used directly for testing and prototyping
    2. Extended for domain-specific behavior

    Default Behavior:
    -----------------
    - perceive(): Stores observation in custom_state["last_observation"]
    - decide(): Returns the observation data as-is
    - act(): Creates an Action with type "default" and the decision payload
    """

    # =========================================================================
    #          OBSERVABLEENTITY PROTOCOL IMPLEMENTATION
    # =========================================================================

    def save_state(self) -> Dict[str, Any]:
        """Return state that should be persisted by StorageProxy."""
        return {
            "turn_count": self.state.turn_count,
            "custom_state": self.state.custom_state.copy(),
        }

    def load_state(self, state: Dict[str, Any]) -> None:
        """Restore state from persisted data."""
        if "turn_count" in state:
            self.state.turn_count = state["turn_count"]
        elif "step_count" in state:
            self.state.turn_count = state["step_count"]
        else:
            raise KeyError("State must contain 'turn_count' or 'step_count'")
        self.state.custom_state = state["custom_state"].copy()

    # =========================================================================
    #                           LIFECYCLE
    # =========================================================================

    async def initialize(self) -> None:
        """Initialize the Player for simulation."""
        self.is_initialized = True

    async def shutdown(self) -> None:
        """Shutdown the Player after simulation."""
        self.is_running = False

    # =========================================================================
    #              CORE BEHAVIORAL CONTRACT (Override these)
    # =========================================================================

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional["StepResult"] = None,
    ) -> None:
        """Process incoming observation and update internal state."""
        self.state.custom_state["last_observation"] = observation.data
        if prev_result and prev_result.action:
            self.state.custom_state["prev_action"] = prev_result.action

    async def decide(self) -> PayloadType:
        """Make a decision based on current state."""
        return self.state.custom_state["last_observation"]

    async def act(self, decision_payload: PayloadType) -> Action:
        """Transform decision into an Action."""
        return Action(
            action_type="default",
            payload=(
                decision_payload
                if isinstance(decision_payload, dict)
                else {"data": decision_payload}
            ),
            source_id=self.identity,
        )

    # =========================================================================
    #                        MAIN EXECUTION
    # =========================================================================

    async def step(
        self,
        observation: Observation,
        prev_result: Optional["StepResult"] = None,
    ) -> "StepResult":
        """Execute one atomic step: perceive → decide → act."""
        self.state.step_tick_start()

        await self.perceive(observation, prev_result)
        decision_payload = await self.decide()
        action = await self.act(decision_payload)

        self.state.update_step(observation, action)
        self.state.step_tick_end()

        return StepResult(
            decision_payload=decision_payload,
            action=action,
            tick_step_count=self.state.step_count,
            tick_step_duration_ms=self.state.step_last_duration_ms,
        )

    def prepare_observation(self, round_num: int) -> Observation:
        """Prepare the Observation for this turn."""
        return Observation(
            local=LocalObservation(data={}),
            notification={},
            round=round_num,
        )

    async def turn(
        self,
        round_num: int,
        num_steps: int = 1,
    ) -> "TurnResult":
        """Execute a turn consisting of multiple steps."""
        observation = self.prepare_observation(round_num)
        self.state.turn_tick_start()

        step_results: List[StepResult] = []
        current_observation = observation
        prev_result: Optional[StepResult] = None

        for _ in range(num_steps):
            step_result = await self.step(current_observation, prev_result)
            step_results.append(step_result)
            prev_result = step_result
            current_observation = self._update_observation_for_next_step(
                current_observation, step_result
            )

        self.state.turn_count += 1
        self.state.turn_tick_end()

        # Prepare outbounds from step results (after turn completes)
        self.prepare_outbounds(step_results)

        return TurnResult(
            step_results=step_results,
            final_action=step_results[-1].action if step_results else None,
            tick_turn_count=self.state.turn_count,
            tick_turn_duration_ms=self.state.turn_last_duration_ms,
            tick_turn_total_duration_ms=self.state.turn_total_duration_ms,
            tick_step_count=len(step_results),
        )

    def _update_observation_for_next_step(
        self,
        current_observation: Observation,
        step_result: "StepResult",
    ) -> Observation:
        """Update observation for the next step."""
        return current_observation

    def prepare_outbounds(self, step_results: List["StepResult"]) -> None:
        """
        Extract outbound messages from step results.

        Called after turn() completes to separate message preparation
        from the core perceive → decide → act flow.

        Args:
            step_results: List of StepResult from the completed turn
        """
        for result in step_results:
            payload = result.decision_payload
            if isinstance(payload, dict) and "outbound_messages" in payload:
                raw_messages = payload.pop("outbound_messages", [])
                for msg in raw_messages:
                    if isinstance(msg, Outbound):
                        self.pending_outbounds.append(msg)
                    elif isinstance(msg, dict):
                        self.pending_outbounds.append(Outbound(**msg))

    # =========================================================================
    #                      TOPOLOGY ACCESS
    # =========================================================================

    def can_send_to(self, target_id: str) -> bool:
        """Check if this player can send to a specific target."""
        return target_id in self.topology_targets

    # =========================================================================
    #                      MESSAGE HANDLING
    # =========================================================================

    def on_message(self, message: "Message") -> None:
        """Receive a message from another player."""
        self.message_inbox.append(message)

    def get_pending_messages(self) -> List["Message"]:
        """Get and clear pending messages from inbox."""
        messages = self.message_inbox.copy()
        self.message_inbox.clear()
        return messages

    def has_received_expected_messages(self) -> bool:
        """
        Check if all expected messages have been received.

        Returns True if:
        - No expected senders configured (always ready), OR
        - All expected senders have sent at least one message
        """
        if not self.state.expected_senders:
            return True
        received_senders = {msg.sender_id for msg in self.message_inbox}
        return self.state.expected_senders.issubset(received_senders)

    def set_expected_senders(self, senders: List[str]) -> None:
        """
        Set which senders this player expects messages from.

        Called by Persona during topology setup based on sources.
        """
        self.state.expected_senders = set(senders)

    def clear_message_inbox(self) -> None:
        """Clear message inbox after processing."""
        self.message_inbox.clear()
        self.state.expected_senders.clear()

    # =========================================================================
    #                          UTILITY
    # =========================================================================

    def in_group(self, tag: str) -> bool:
        """Check if this Player belongs to a specific group."""
        return tag in self.group_tags

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Player(id={self.identity}, groups={self.group_tags})"


# =============================================================================
#                       SPECIALIZED PLAYERS
# =============================================================================


class EchoPlayer(GeneralPlayer):
    """A Player that echoes back observations with minimal processing."""

    async def act(self, decision_payload: PayloadType) -> Action:
        """Create an echo action with observation data."""
        return Action(
            action_type="echo",
            payload={"echoed_data": decision_payload},
            source_id=self.identity,
            metadata={"player_name": self.name},
        )


class NoOpPlayer(GeneralPlayer):
    """A Player that takes no action (returns empty actions)."""

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
    """A Player that reacts based on observation triggers."""

    async def decide(self) -> PayloadType:
        """Decide based on reactive triggers."""
        obs = self.state.custom_state["last_observation"]

        if self.should_react(obs):
            return self.create_reaction(obs)
        return self.create_default_response(obs)

    def should_react(self, observation: Dict[str, Any]) -> bool:
        """Determine if a reaction is needed."""
        return False

    def create_reaction(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Create a reaction payload when triggered."""
        return {"reaction": True, "triggered_by": observation}

    def create_default_response(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Create default response when not reacting."""
        return {"reaction": False, "hold": True}
