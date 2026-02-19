"""Demo Package - Topology-Driven Message Passing

Components:
- SimpleCoordinator: Hub that broadcasts to players and collects responses
- SimplePlayer: Player that receives, processes, and responds
"""

from .players import SimpleCoordinator, SimplePlayer

__all__ = [
    "SimpleCoordinator",
    "SimplePlayer",
]
