"""
MASim Persona Layer - Infrastructure Coordination Facade

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

Public API:
    - BasePersona: Abstract base for infrastructure coordination
    - PlayerPersona: Player-specific persona
    - ConductorPersona: Conductor-specific persona
    - PersonaConfig: Configuration options
"""

from masim.persona.base import (
    BasePersona,
    PlayerPersona,
    ConductorPersona,
    PersonaConfig,
)

__all__ = [
    "BasePersona",
    "PlayerPersona",
    "ConductorPersona",
    "PersonaConfig",
]
