"""MASim Simulator Module.

Provides simulation orchestration with Ray-based distributed computing.

Architecture:
    Simulator ─────► PlayerPersona (Ray Actor) ──► BasePlayer (hidden)

All agents are Players. Coordinator functionality is implemented as a
Player with role='coordinator' in config.

Simulator interacts ONLY with Personas - Player internals are hidden.

Hierarchical Execution Model:
- Simulator: round (orchestrates all Personas)
- PlayerPersona: operate (internally calls Player.turn)
- Player: turn (for loop calling step)
- Player: step (perceive→decide→act)

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
    "SimulationConfig",
    "BaseSimulator",
    # From general.py
    "ensure_ray",
    "get_actor_name",
    "load_class",
    "GeneralSimulator",
]
