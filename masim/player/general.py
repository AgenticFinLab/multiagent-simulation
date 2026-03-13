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
    Info,
)

if TYPE_CHECKING:
    pass


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
        """
        Return state that should be persisted by StorageProxy.

        NOTE: Returns direct reference to custom_state (no copy).
        StorageProxy serializes immediately, so copy is unnecessary.
        Avoiding .copy() prevents memory waste for large custom_state dicts.
        """
        return {
            "turn_count": self.state.turn_count,
            "custom_state": self.state.custom_state,
        }

    def load_state(self, state: Dict[str, Any]) -> None:
        """
        Restore state from persisted data.

        NOTE: Directly assigns custom_state (no copy).
        State comes from storage deserialization, already a new object.
        """
        if "turn_count" in state:
            self.state.turn_count = state["turn_count"]
        elif "step_count" in state:
            self.state.turn_count = state["step_count"]
        else:
            raise KeyError("State must contain 'turn_count' or 'step_count'")
        self.state.custom_state = state["custom_state"]

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
        """Prepare the Observation for this turn with local data + received Info units."""
        infos = self.get_received_infos()
        return Observation(
            local=self.get_local_observation(),
            inbounds=infos,
            round=round_num,
        )

    def get_local_observation(self) -> LocalObservation:
        """Get player's local observation data. Override in subclass."""
        return LocalObservation(data={})

    async def turn(
        self,
        round_num: int,
        **kwargs,
    ) -> "TurnResult":
        """Execute a turn consisting of multiple steps."""
        observation = self.prepare_observation(round_num)
        self.state.turn_tick_start()
        self.state.step_reset()  # Reset step metrics for new turn

        step_results: List[StepResult] = []
        current_observation = observation
        prev_result: Optional[StepResult] = None

        num_steps = self.config.steps_per_turn
        for _ in range(num_steps):
            step_result = await self.step(current_observation, prev_result)
            step_results.append(step_result)
            prev_result = step_result
            current_observation = self._update_observation_for_next_step(
                current_observation, step_result
            )

        self.state.turn_count += 1
        self.state.turn_tick_end()

        # Prepare pending Info from step results (after turn completes)
        self.prepare_pending_info(step_results)

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

    def prepare_pending_info(self, step_results: List["StepResult"]) -> None:
        """
        Extract Info units from step results and queue them for Simulator dispatch.

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
                    if isinstance(msg, Info):
                        self.pending_info.append(msg)
                    elif isinstance(msg, dict):
                        self.pending_info.append(Info(**msg))

    # =========================================================================
    #                      TOPOLOGY ACCESS
    # =========================================================================

    def can_send_to(self, target_id: str) -> bool:
        """Check if this player can send to a specific target."""
        return target_id in self.topology_targets

    # =========================================================================
    #                      RECEIVED INFO HANDLING
    # =========================================================================

    def receive_info(self, info: Info) -> None:
        """Receive an Info unit from Persona (incoming content from another player)."""
        self.received_infos.append(info)

    def get_received_infos(self) -> List[Info]:
        """Get and clear all received Info units (consumed once, in operate())."""
        infos = self.received_infos.copy()
        self.received_infos.clear()
        return infos

    def is_received_ready(
        self, round_num: int, received_senders: set, **kwargs
    ) -> bool:
        """
        Check if player has received enough inbounds to proceed.

        Logic:
        - Level 0 in Round 1: ready immediately (initiators don't wait)
        - If no expected_senders → ready immediately
        - Otherwise check if all expected senders have sent

        Args:
            round_num: Current round number
            received_senders: Set of sender IDs in proxy inbound queue
                              (injected by Persona from proxy.get_received_senders())
            **kwargs: Additional parameters (level, etc.)

        Returns:
            True if ready to proceed with decision
        """
        level = kwargs.get("level", 0)

        # Level 0 nodes in Round 1 are initiators - they don't wait for messages
        if round_num == 1 and level == 0:
            return True

        if not self.expected_senders:
            return True

        # Player owns the readiness decision; proxy provides received_senders data
        return self.expected_senders.issubset(received_senders)

    # =========================================================================
    #                          UTILITY
    # =========================================================================

    def in_group(self, tag: str) -> bool:
        """Check if this Player belongs to a specific group."""
        return tag in self.group_tags

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Player(id={self.identity}, groups={self.group_tags})"
