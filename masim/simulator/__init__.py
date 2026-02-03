"""MASim Simulator Module.

Provides simulation orchestration with Ray-based distributed computing.

Architecture:
    Simulator ─────► PlayerPersona (Ray Actor) ──► BasePlayer (hidden)
    Simulator ─────► ConductorPersona (Ray Actor) ──► BaseConductor (hidden)

Simulator interacts ONLY with Personas - Player/Conductor are internal details.

Hierarchical Execution Model:
- Simulator: round (orchestrates all Personas)
- PlayerPersona: step (internally calls Player.step)
- ConductorPersona: cycle (internally calls Conductor.cycle)
"""

from masim.simulator.base import (
    # Status
    SimulatorStatus,
    RoundPhase,
    # Execution Clock
    ExecutionClock,
    # Configuration
    RayConfig,
    SimulationConfig,
    # Ray utilities
    ensure_ray,
    get_actor_name,
    load_class,
    # Simulator
    BaseSimulator,
)

__all__ = [
    "SimulatorStatus",
    "RoundPhase",
    "ExecutionClock",
    "RayConfig",
    "SimulationConfig",
    "ensure_ray",
    "get_actor_name",
    "load_class",
    "BaseSimulator",
]
