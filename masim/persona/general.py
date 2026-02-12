"""
General Persona Implementation for MASim Framework.

This module provides the concrete Persona implementations that wrap
Player and Conductor entities with infrastructure coordination.

For abstract definitions and documentation, see base.py.

Architecture:
    Simulator ─────► PlayerPersona (Ray Actor)
                          │
                          └──► BasePlayer (internal, hidden)

    Simulator ─────► ConductorPersona (Ray Actor)
                          │
                          └──► BaseConductor (internal, hidden)

Key Design Principles:
    1. ENCAPSULATION: Persona OWNS and hides Player/Conductor
    2. FACADE PATTERN: Persona aggregates all proxies + domain logic
    3. SINGLE INTERFACE: Simulator only sees Persona's operate()/cycle()
    4. INFRASTRUCTURE: All observability, storage, communication via Persona
"""

import time
from typing import Any, Dict, List, Optional, Type, TYPE_CHECKING

from masim.persona.base import BasePersona, PersonaConfig

if TYPE_CHECKING:
    from masim.player.base import (
        BasePlayer,
        PlayerConfig,
        Action,
        Observation,
        StepResult,
        TurnResult,
    )
    from masim.conductor.base import (
        BaseConductor,
        ConductorConfig,
        CoordinationDecision,
        CycleResult,
    )


# =============================================================================
#                        PLAYER PERSONA
# =============================================================================


class PlayerPersona(BasePersona):
    """
    Persona for Player entities - the primary interface Simulator uses.

    PlayerPersona OWNS and HIDES the BasePlayer instance. Simulator
    interacts only with PlayerPersona's public methods:
        - initialize(): Set up the Player
        - operate(observation, num_steps): Execute Player's turn
        - shutdown(): Clean up resources
        - get_state_snapshot(): Get state for monitoring

    The internal BasePlayer is completely hidden from Simulator.

    Execution Hierarchy:
        Simulator.round() ──► PlayerPersona.operate()
                                    │
                                    └──► Player.turn() (for loop of steps)
                                               │
                                               └──► Player.step() (perceive→decide→act)
    """

    def __init__(
        self,
        player_class: Type["BasePlayer"],
        player_config: "PlayerConfig",
        persona_config: Optional[PersonaConfig] = None,
    ):
        """
        Initialize PlayerPersona with a Player class and config.

        The Player instance is created internally and hidden from outside.

        Args:
            player_class: The BasePlayer subclass to instantiate
            player_config: Configuration for the Player
            persona_config: Configuration for the Persona
        """
        super().__init__(persona_config)

        # Store class and config for deferred creation
        self._player_class = player_class
        self._player_config = player_config

        # Internal Player instance (HIDDEN from Simulator)
        self._player: Optional["BasePlayer"] = None

        # Operate timing
        self._operate_start_time: Optional[float] = None

    # =========================================================================
    #                        IDENTITY
    # =========================================================================

    @property
    def identity(self) -> str:
        """Get the Player's identity."""
        return self._player_config.identity

    # =========================================================================
    #                        LIFECYCLE
    # =========================================================================

    async def initialize(self) -> None:
        """
        Initialize the Persona and its internal Player.

        Called by Simulator during setup phase.
        """
        if self._is_initialized:
            return

        # Create the internal Player instance
        self._player = self._player_class(self._player_config)

        # Initialize the Player
        await self._player.initialize()

        self._is_initialized = True

        # Log initialization
        if self._observability:
            await self._observability.log_event(
                "player_initialized", {"player_id": self.identity}
            )

    async def shutdown(self) -> None:
        """
        Shutdown the Persona and its internal Player.

        Called by Simulator during teardown phase.
        """
        if not self._player:
            return

        # Shutdown the Player
        await self._player.shutdown()

        # Log shutdown
        step_count = self._player._state.step_count if self._player else 0
        if self._observability:
            await self._observability.log_event(
                "player_shutdown",
                {"player_id": self.identity, "steps_completed": step_count},
            )

    # =========================================================================
    #                    MAIN INTERFACE (What Simulator Calls)
    # =========================================================================

    async def operate(
        self,
        observation: "Observation",
        num_steps: int = 1,
    ) -> "TurnResult":
        """
        Execute the Player's turn operation.

        This is the PRIMARY INTERFACE that Simulator calls.
        Internally delegates to the hidden Player.turn().

        In the hierarchical execution model:
        - Simulator: round (orchestrates all Personas)
        - PlayerPersona: operate (this method)  <-- Simulator calls this
        - Player: turn (for loop of steps)      <-- Hidden from Simulator
        - Player: step (perceive→decide→act)   <-- Hidden from Simulator

        Args:
            observation: The current observation from environment
            num_steps: Number of steps to execute in this turn (default: 1)

        Returns:
            TurnResult containing:
                - step_results: List of StepResult from each step
                - final_action: The last action produced
                - tick_turn_count: The turn number
                - tick_turn_duration_ms: Duration of the turn
                - tick_step_count: Number of steps executed
        """
        if not self._player:
            raise RuntimeError("PlayerPersona not initialized")

        # Start timing
        self._operate_start_time = time.perf_counter()
        if self._observability:
            await self._observability.start_timer("operate_duration")

        # Delegate to internal Player.turn() (HIDDEN from Simulator)
        turn_result = await self._player.turn(observation, num_steps)

        # Log completion
        if self._observability:
            duration = await self._observability.stop_timer("operate_duration")
            await self._observability.record_metric(
                "operate_completed",
                {
                    "player_id": self.identity,
                    "turn": turn_result.tick_turn_count,
                    "steps_executed": turn_result.tick_step_count,
                    "duration_ms": duration,
                    "final_action_type": (
                        turn_result.final_action.action_type
                        if turn_result.final_action
                        else None
                    ),
                },
            )

        # Auto-checkpoint if enabled
        if self._config.auto_checkpoint and self._storage:
            state = self._player.save_state()
            await self._storage.checkpoint(
                state=state,
                label=f"turn_{turn_result.tick_turn_count}",
            )

        return turn_result

    # =========================================================================
    #                    STATE ACCESS
    # =========================================================================

    def get_state_snapshot(self) -> Dict[str, Any]:
        """
        Get a snapshot of Player state for monitoring.

        Used by Simulator for debugging/monitoring, NOT for domain logic.
        """
        if not self._player:
            return {"player_id": self.identity, "initialized": False}

        state = self._player._state
        return {
            "player_id": self.identity,
            "initialized": True,
            "turn_count": state.turn_count,
            "step_count": state.step_count,
            "turn_metrics": state.get_turn_metrics(),
            "step_metrics": state.get_step_metrics(),
            "custom_state": state.custom_state,
        }

    def save_state(self) -> Dict[str, Any]:
        """Get persistable state from internal Player."""
        if not self._player:
            return {}
        return self._player.save_state()

    def load_state(self, state: Dict[str, Any]) -> None:
        """Restore state to internal Player."""
        if self._player:
            self._player.load_state(state)

    # =========================================================================
    #                    COORDINATION
    # =========================================================================

    async def receive_coordination(self, decision_dict: Dict[str, Any]) -> None:
        """
        Receive a CoordinationDecision from Conductor.

        Args:
            decision_dict: Serialized CoordinationDecision data
        """
        if self._player:
            self._player.get_state().set_custom("last_coordination", decision_dict)


# =============================================================================
#                       CONDUCTOR PERSONA
# =============================================================================


class ConductorPersona(BasePersona):
    """
    Persona for Conductor entities - the primary interface Simulator uses.

    ConductorPersona OWNS and HIDES the BaseConductor instance. Simulator
    interacts only with ConductorPersona's public methods:
        - initialize(): Set up the Conductor
        - notify(): Send round state to Players
        - cycle(): Execute one coordination cycle
        - shutdown(): Clean up resources
        - register_player()/unregister_player(): Manage Players
        - receive_actions(): Receive Actions from Players

    The internal BaseConductor is completely hidden from Simulator.

    Conductor Contract:
        notify() → Players act → receive_actions() → cycle()
        - notify(): Conductor → Players (outbound)
        - receive_actions(): Players → Conductor (inbound, builds census)
        - cycle(): collect_census → analyze → coordinate
    """

    def __init__(
        self,
        conductor_class: Type["BaseConductor"],
        conductor_config: "ConductorConfig",
        persona_config: Optional[PersonaConfig] = None,
    ):
        """
        Initialize ConductorPersona with a Conductor class and config.

        The Conductor instance is created internally and hidden from outside.

        Args:
            conductor_class: The BaseConductor subclass to instantiate
            conductor_config: Configuration for the Conductor
            persona_config: Configuration for the Persona
        """
        super().__init__(persona_config)

        # Store class and config for deferred creation
        self._conductor_class = conductor_class
        self._conductor_config = conductor_config

        # Internal Conductor instance (HIDDEN from Simulator)
        self._conductor: Optional["BaseConductor"] = None

        # Cycle timing
        self._cycle_start_time: Optional[float] = None

    # =========================================================================
    #                        IDENTITY
    # =========================================================================

    @property
    def identity(self) -> str:
        """Get the Conductor's identity."""
        return self._conductor_config.identity

    # =========================================================================
    #                        LIFECYCLE
    # =========================================================================

    async def initialize(self) -> None:
        """
        Initialize the Persona and its internal Conductor.

        Called by Simulator during setup phase.
        """
        if self._is_initialized:
            return

        # Create the internal Conductor instance
        self._conductor = self._conductor_class(self._conductor_config)

        # Initialize the Conductor
        await self._conductor.initialize()

        self._is_initialized = True

        # Log initialization
        if self._observability:
            await self._observability.log_event(
                "conductor_initialized",
                {
                    "conductor_id": self.identity,
                    "mode": self._conductor.coordination_mode,
                },
            )

    async def shutdown(self) -> None:
        """
        Shutdown the Persona and its internal Conductor.

        Called by Simulator during teardown phase.
        """
        if not self._conductor:
            return

        # Shutdown the Conductor
        await self._conductor.shutdown()

        # Log shutdown
        cycle_count = self._conductor._state.cycle_count if self._conductor else 0
        if self._observability:
            await self._observability.log_event(
                "conductor_shutdown",
                {"conductor_id": self.identity, "cycles_completed": cycle_count},
            )

    # =========================================================================
    #                    PLAYER MANAGEMENT
    # =========================================================================

    def register_player(self, player_id: str, metadata: Dict[str, Any] = None) -> None:
        """Register a Player with this Conductor."""
        if self._conductor:
            self._conductor.register_player(player_id, metadata)

    def unregister_player(self, player_id: str) -> None:
        """Unregister a Player from this Conductor."""
        if self._conductor:
            self._conductor.unregister_player(player_id)

    # =========================================================================
    #                    PLAYER NOTIFICATION (Conductor → Players)
    # =========================================================================

    def notify(
        self,
        round_num: int,
        player_ids: List[str],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Notify players of round state (Conductor → Players).

        Delegates to the internal Conductor's notify() method.

        Args:
            round_num: Current simulation round
            player_ids: List of player IDs to notify

        Returns:
            Dict of player_id -> notification_dict
        """
        if not self._conductor:
            raise RuntimeError("ConductorPersona not initialized")
        return self._conductor.notify(round_num, player_ids)

    # =========================================================================
    #                    CENSUS INTAKE (Players → Conductor)
    # =========================================================================

    def receive_action(self, action: "Action") -> None:
        """
        Receive a single Action from a Player (sync).

        Adds the action to the census for later processing.

        Args:
            action: The Action to add to census
        """
        if self._conductor:
            self._conductor.on_action_received(action)

    async def receive_actions(self, actions: List["Action"]) -> None:
        """
        Receive Actions from Players (builds the census).

        Args:
            actions: List of Action objects to add to census
        """
        if not self._conductor:
            return

        for action in actions:
            self._conductor.on_action_received(action)

            # Log action receipt
            if self._observability:
                await self._observability.record_metric(
                    "census_action_received",
                    {
                        "conductor_id": self.identity,
                        "action_id": action.action_id,
                        "source_id": action.source_id,
                    },
                )

    # =========================================================================
    #                    MAIN INTERFACE (What Simulator Calls)
    # =========================================================================

    async def cycle(self) -> "CycleResult":
        """
        Execute one coordination cycle.

        This is the PRIMARY INTERFACE that Simulator calls.
        Internally delegates to the hidden Conductor.cycle().

        In the hierarchical execution model:
        - Simulator: round (orchestrates all Personas)
        - ConductorPersona: cycle (this method)  <-- Simulator calls this
        - Conductor: cycle (internal, hidden)    <-- Hidden from Simulator

        The cycle processes the census (collected actions) and produces
        a CoordinationDecision.

        Returns:
            CycleResult containing:
                - decision: The CoordinationDecision generated
                - census_size: Number of actions in the census
                - tick_cycle_count: Cycle number
                - tick_cycle_duration_ms: Cycle duration
        """
        if not self._conductor:
            raise RuntimeError("ConductorPersona not initialized")

        # Start timing
        self._cycle_start_time = time.perf_counter()
        if self._observability:
            await self._observability.start_timer("cycle_duration")

        # Delegate to internal Conductor (HIDDEN from Simulator)
        cycle_result = await self._conductor.cycle()

        # Log completion
        if self._observability:
            duration = await self._observability.stop_timer("cycle_duration")
            await self._observability.record_metric(
                "cycle_completed",
                {
                    "conductor_id": self.identity,
                    "cycle": cycle_result.tick_cycle_count,
                    "decision_type": cycle_result.decision.decision_type,
                    "census_size": cycle_result.census_size,
                    "duration_ms": duration,
                },
            )

        # Auto-checkpoint if enabled
        if self._config.auto_checkpoint and self._storage:
            state = self._conductor.save_state()
            await self._storage.checkpoint(
                state=state,
                label=f"cycle_{cycle_result.tick_cycle_count}",
            )

        return cycle_result

    # =========================================================================
    #                    STATE ACCESS
    # =========================================================================

    def get_state_snapshot(self) -> Dict[str, Any]:
        """
        Get a snapshot of Conductor state for monitoring.

        Used by Simulator for debugging/monitoring, NOT for domain logic.
        """
        if not self._conductor:
            return {"conductor_id": self.identity, "initialized": False}

        return {
            "conductor_id": self.identity,
            "initialized": True,
            **self._conductor.get_state_snapshot(),
        }

    def save_state(self) -> Dict[str, Any]:
        """Get persistable state from internal Conductor."""
        if not self._conductor:
            return {}
        return self._conductor.save_state()

    def load_state(self, state: Dict[str, Any]) -> None:
        """Restore state to internal Conductor."""
        if self._conductor:
            self._conductor.load_state(state)

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics from internal Conductor."""
        if not self._conductor:
            return {}
        return self._conductor.get_system_metrics()
