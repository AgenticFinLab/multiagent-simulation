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
- base.py:    Abstract base classes, type definitions, enums, plus the
              abstract ``BaseSimulationRunner`` that pairs 1:1 with each
              concrete simulator (shared preflight + lifecycle).
- general.py: Concrete Ray-backed ``GeneralSimulator`` **and** its paired
              ``GeneralSimulationRunner`` + module-level ``run()`` CLI
              convenience function (used by every ``examples/*/run_*.py``
              shim). New simulator variants are expected to follow the
              same *simulator + runner + run()* co-location pattern.
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
    # Abstract simulator + runner + shared helpers
    BaseSimulator,
    BaseSimulationRunner,
    extract_knowledge_config,
    detect_variant,
)

# Concrete implementations (general.py) — engine, runner, and CLI entry
from masim.simulator.general import (
    # Ray utilities
    ensure_ray,
    get_actor_name,
    load_class,
    # Concrete simulator + runner + CLI convenience
    GeneralSimulator,
    GeneralSimulationRunner,
    run,
)

__all__ = [
    # From base.py
    "SimulatorStatus",
    "RoundPhase",
    "ExecutionClock",
    "SimulationConfig",
    "BaseSimulator",
    "BaseSimulationRunner",
    "extract_knowledge_config",
    "detect_variant",
    # From general.py
    "ensure_ray",
    "get_actor_name",
    "load_class",
    "GeneralSimulator",
    "GeneralSimulationRunner",
    "run",
]
