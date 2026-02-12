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

Module Structure:
- base.py: Abstract base classes, type definitions, enums (no implementation)
- general.py: Concrete implementations with Ray integration
"""

# Abstract base classes and type definitions (base.py)
from masim.simulator.base import (
    # Status enums
    SimulatorStatus,
    RoundPhase,
    # Execution clock
    ExecutionClock,
    # Configuration
    RayConfig,
    SimulationConfig,
    # Abstract simulator
    BaseSimulator,
)

# Concrete implementations (general.py)
from masim.simulator.general import (
    # Ray utilities
    ensure_ray,
    get_actor_name,
    load_class,
    # Concrete simulator
    GeneralSimulator,
)

__all__ = [
    # From base.py
    "SimulatorStatus",
    "RoundPhase",
    "ExecutionClock",
    "RayConfig",
    "SimulationConfig",
    "BaseSimulator",
    # From general.py
    "ensure_ray",
    "get_actor_name",
    "load_class",
    "GeneralSimulator",
]
