"""World layer: shared environment state.

:class:`~masim.world.shared_state.VersionedSharedState` implements the
:class:`masim.platform.world.base.SharedState` contract with scopes and
versioned commits. It is the platform's answer to "where does world state
live?" — see the module docstring for what is implemented today (a driver-side,
scope-per-coordinator projection) and what a writable-by-agents world would
still need.
"""

from masim.world.shared_state import VersionedSharedState

__all__ = ["VersionedSharedState"]
