"""MASim Persona Layer - Infrastructure Coordination Facade

The Persona Layer is the "outer shell" of Player entities.
It handles infrastructure interactions so the core entity can focus
on domain logic.

Base Classes (base.py):
    - BasePersona: Abstract base for infrastructure coordination

General Implementations (general.py):
    - PlayerPersona: Player-specific persona
"""

from masim.persona.base import BasePersona
from masim.persona.general import PlayerPersona

__all__ = [
    "BasePersona",
    "PlayerPersona",
]
