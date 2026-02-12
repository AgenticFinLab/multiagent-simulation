"""MASim Persona Layer - Infrastructure Coordination Facade

The Persona Layer is the "outer shell" of Player/Conductor entities,
handling all infrastructure interactions so the core entity can focus
purely on domain logic (algorithms, reasoning, decision-making).

Three-Layer Architecture:
    ┌─────────────────────────────────────────────────────┐
    │  Player / Conductor (What)                          │
    │  • Pure domain logic: perceive → decide → act       │
    │  • No infrastructure code                           │
    └───────────────┬─────────────────────────────────────┘
                    │ entity.persona.xxx()
                    ▼
    ┌─────────────────────────────────────────────────────┐
    │  Persona Layer (When) ← THIS MODULE                 │
    │  • Infrastructure timing & coordination             │
    │  • Proxy aggregation (Facade pattern)               │
    └───────────────┬─────────────────────────────────────┘
                    │ proxy.xxx()
                    ▼
    ┌─────────────────────────────────────────────────────┐
    │  Proxy Layer (How)                                  │
    │  • Communication, Storage, Resource, Observability  │
    └─────────────────────────────────────────────────────┘

Base Classes (base.py):
    - BasePersona: Abstract base for infrastructure coordination
    - PersonaConfig: Configuration options

General Implementations (general.py):
    - PlayerPersona: Player-specific persona
    - ConductorPersona: Conductor-specific persona
"""

from masim.persona.base import (
    BasePersona,
    PersonaConfig,
)

from masim.persona.general import (
    PlayerPersona,
    ConductorPersona,
)

__all__ = [
    # Base types
    "BasePersona",
    "PersonaConfig",
    # General implementations
    "PlayerPersona",
    "ConductorPersona",
]
